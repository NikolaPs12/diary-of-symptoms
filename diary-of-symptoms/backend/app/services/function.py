import io
import os
import re
import textwrap
from html import escape, unescape
from pathlib import Path
import logging

from datetime import date, datetime
import sqlalchemy
from app.services.config import get_settings


try:
    from google import genai
except ImportError:  # pragma: no cover
    genai = None

try:
    from fpdf import FPDF
except ImportError:  # pragma: no cover
    FPDF = None


FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/google-droid-sans-fonts/DroidSans.ttf",
    "/usr/share/fonts/google-carlito-fonts/Carlito-Regular.ttf",
    "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf",
    "/usr/share/fonts/adwaita-sans-fonts/AdwaitaSans-Regular.ttf",
]


from textwrap import dedent

import markdown
import bleach

def build_ai_insight(symptom_entry) -> str:
    prompt = dedent(f"""
    Проанализируй состояние пациента.

    Данные:
    - Симптом: {symptom_entry.symptom}
    - Тяжесть: {symptom_entry.severity}/10
    - Длительность: {symptom_entry.duration}
    - Сон: {symptom_entry.sleep_hours} часов
    - Качество сна: {symptom_entry.sleep_quality}/10
    - Стресс: {symptom_entry.stress_level}/10
    - Общее состояние: {symptom_entry.body_state}
    - Заметки: {symptom_entry.notes}
    - Еда: {symptom_entry.food_notes}
    - Лекарства: {symptom_entry.medications_taken}

    Верни ответ **строго в Markdown**.

    Используй структуру:

    ## Анализ состояния

    ...

    ## Возможные триггеры

    - ...
    - ...

    ## Рекомендации

    1. ...
    2. ...

    Важно:
    - Верни только Markdown.
    - Не используй HTML.
    - Не используй блоки ```markdown```.
    - Ответ должен начинаться сразу с заголовка.
    """).strip()

    settings = get_settings()
    api_key = settings.api_ai_key or os.getenv("API_AI_KEY")

    if genai is None or not api_key:
        logging.warning("AI insight generation skipped: genai unavailable or API key missing")
        return _ai_insight_fallback(symptom_entry)

    try:
        client = genai.Client(api_key=api_key)
        response = None
        for model_name in ["gemini-2.5-flash-lite", "gemini-2.0-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                break
            except Exception as exc:
                logging.warning("AI model %s failed: %s", model_name, exc)
                response = None
        if response is None or not getattr(response, "text", None):
            raise RuntimeError("AI generation failed for all available models")

        # Markdown -> HTML
        html = markdown.markdown(
            response.text,
            extensions=["extra", "nl2br"]
        )

        # Очистка HTML
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS.union({
            "h1", "h2", "h3", "p", "ul", "ol", "li",
            "strong", "em", "hr", "blockquote"
        })

        safe_html = bleach.clean(
            html,
            tags=allowed_tags,
            strip=True
        )

        return safe_html

    except Exception as exc:
        logging.exception("Failed to build AI insight")
        return _ai_insight_fallback(symptom_entry)


def _ai_insight_fallback(symptom_entry) -> str:
    return (
        "<p>ИИ временно недоступен. Возможные триггеры: "
        f"стресс {symptom_entry.stress_level}/10, "
        f"качество сна {symptom_entry.sleep_quality}/10, "
        "и влияние еды или лекарств.</p>"
    )


def _normalize_text(value, empty_value: str = "Not specified") -> str:
    if value is None:
        return empty_value

    text = str(value)
    text = unescape(re.sub(r"<[^>]+>", " ", text))
    text = text.replace("**", "")
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or empty_value


def _ascii_safe_text(value, empty_value: str = "Not specified") -> str:
    return _normalize_text(value, empty_value).encode("latin-1", "replace").decode("latin-1")


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_lines(line: str, width: int = 92) -> list[str]:
    if line == "":
        return [""]
    return textwrap.wrap(_ascii_safe_text(line), width=width) or [""]


def _build_report_lines(symptoms_list, start_date: date | None, end_date: date | None) -> list[str]:
    if start_date and end_date:
        period = f"Period: {start_date.isoformat()} to {end_date.isoformat()}"
    elif start_date:
        period = f"Period: {start_date.isoformat()}"
    else:
        period = "Period: all data"

    lines = [
        "DIARY OF SYMPTOMS REPORT",
        period,
        f"Entries: {len(symptoms_list)}",
        "",
    ]

    for index, item in enumerate(symptoms_list, start=1):
        lines.extend(
            [
                f"Entry {index}",
                f"Date: {item.start_at.strftime('%Y-%m-%d %H:%M')}",
                f"Symptom: {_normalize_text(item.symptom)}",
                f"Severity: {item.severity}/10 | Duration: {_normalize_text(item.duration)}",
                f"Body state: {_normalize_text(item.body_state)}",
                f"Sleep: {item.sleep_hours}h | Quality: {item.sleep_quality}/10",
                f"Stress: {item.stress_level}/10",
                f"Food: {_normalize_text(item.food_notes)}",
                f"Medications: {_normalize_text(item.medications_taken)}",
                f"Notes: {_normalize_text(item.notes)}",
                f"AI insight: {_normalize_text(item.ai_insights)}",
                "",
            ]
        )

    return lines


def _find_pdf_font() -> str | None:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


def _generate_pdf_with_fpdf(report_lines: list[str]) -> io.BytesIO:
    if FPDF is None:
        raise RuntimeError("fpdf is not available")

    font_path = _find_pdf_font()
    if font_path is None:
        raise RuntimeError("No unicode-compatible font found for PDF export")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font("CodexSans", "", font_path)
    pdf.set_font("CodexSans", size=15)
    pdf.cell(0, 10, "Diary of Symptoms Report", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("CodexSans", size=11)
    effective_width = pdf.w - pdf.l_margin - pdf.r_margin

    for line in report_lines:
        if line == "":
            pdf.ln(4)
            continue
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(effective_width, 7, line, new_x="LMARGIN", new_y="NEXT")

    payload = pdf.output(dest="S")
    if isinstance(payload, str):
        payload = payload.encode("latin-1")
    else:
        payload = bytes(payload)

    output = io.BytesIO(payload)
    output.seek(0)
    return output


import io
from datetime import date
from weasyprint import HTML

def generate_symptoms_pdf(symptoms_list, start_date: date | None = None, end_date: date | None = None) -> io.BytesIO:
    period_str = f"{start_date or '...'} - {end_date or '...'}" if start_date or end_date else "За всё время"
    entry_count = len(symptoms_list)

    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '    <meta charset="utf-8">',
        "    <style>",
        "        @page { size: A4; margin: 20mm; }",
        "        body { font-family: 'DejaVu Sans', 'Helvetica', 'Arial', sans-serif; color: #333333; line-height: 1.45; font-size: 13px; }",
        "        .header { border-bottom: 2px solid #4F46E5; padding-bottom: 15px; margin-bottom: 24px; }",
        "        .header h1 { font-size: 24px; color: #1F2937; margin: 0 0 6px 0; text-transform: uppercase; letter-spacing: 1px; }",
        "        .header p { color: #6B7280; margin: 0; font-size: 14px; }",
        "        .summary { margin: 14px 0 22px; padding: 12px 14px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 6px; }",
        "        .card { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 15px; margin-bottom: 18px; page-break-inside: avoid; }",
        "        .card-header { font-size: 14px; font-weight: bold; color: #4F46E5; border-bottom: 1px solid #F3F4F6; padding-bottom: 8px; margin-bottom: 12px; }",
        "        .grid { display: flex; flex-wrap: wrap; margin-bottom: 10px; gap: 10px; }",
        "        .grid-item { flex: 1 1 30%; min-width: 30%; font-size: 13px; margin-bottom: 8px; }",
        "        .grid-item span { color: #6B7280; display: block; font-size: 11px; text-transform: uppercase; margin-bottom: 2px; }",
        "        .notes, .insight, .empty-state { background: #F9FAFB; padding: 10px; border-left: 3px solid #D1D5DB; font-size: 13px; margin-top: 10px; border-radius: 0 4px 4px 0; }",
        "        .insight { border-left-color: #4F46E5; }",
        "        .empty-state { border: 1px dashed #CBD5E1; border-left-width: 3px; padding: 18px; }",
        "    </style>",
        "</head>",
        "<body>",
        '    <div class="header">',
        "        <h1>Diary of Symptoms Report</h1>",
        f"        <p>Период отчёта: {escape(str(period_str))}</p>",
        "    </div>",
        f'    <div class="summary"><strong>Всего записей:</strong> {entry_count}</div>',
    ]

    if not symptoms_list:
        html_parts.extend(
            [
                '    <div class="empty-state">',
                "        По выбранному периоду записи симптомов не найдены.",
                "    </div>",
            ]
        )
    else:
        for item in symptoms_list:
            date_str = item.start_at.strftime("%d.%m.%Y в %H:%M") if item.start_at else "Не указано"
            symptom_name = _normalize_text(item.symptom, "Не указан")
            entry_kind = "Сводка состояния" if symptom_name.lower() == "daily check-in" else "Симптом"
            severity_val = f"{item.severity}/10"
            duration_val = _normalize_text(item.duration, "—")
            body_val = _normalize_text(item.body_state, "—")
            stress_val = f"{item.stress_level}/10"
            sleep_val = f"{item.sleep_hours}ч (Качество: {item.sleep_quality}/10)"
            meds_val = _normalize_text(item.medications_taken, "Нет")
            food_val = _normalize_text(item.food_notes, "Нет заметок")
            notes_val = _normalize_text(item.notes, "Нет описания")
            insight_val = _normalize_text(item.ai_insights, "AI-анализ отсутствует")

            html_parts.extend(
                [
                    '    <div class="card">',
                    f'        <div class="card-header">Запись от {escape(date_str)}</div>',
                    '        <div class="grid">',
                    f'            <div class="grid-item"><span>Тип записи</span><strong>{escape(entry_kind)}</strong></div>',
                    f'            <div class="grid-item"><span>Симптом / check-in</span><strong>{escape(symptom_name)}</strong></div>',
                    f'            <div class="grid-item"><span>Интенсивность</span><strong>{escape(severity_val)}</strong></div>',
                    f'            <div class="grid-item"><span>Длительность</span><strong>{escape(duration_val)}</strong></div>',
                    "        </div>",
                    '        <div class="grid">',
                    f'            <div class="grid-item"><span>Состояние тела</span>{escape(body_val)}</div>',
                    f'            <div class="grid-item"><span>Уровень стресса</span>{escape(stress_val)}</div>',
                    f'            <div class="grid-item"><span>Сон</span>{escape(sleep_val)}</div>',
                    "        </div>",
                    '        <div class="grid">',
                    f'            <div class="grid-item"><span>Медикаменты</span>{escape(meds_val)}</div>',
                    f'            <div class="grid-item"><span>Еда</span>{escape(food_val)}</div>',
                    "        </div>",
                    f'        <div class="notes"><strong>Заметки:</strong> {escape(notes_val)}</div>',
                    f'        <div class="insight"><strong>AI insight:</strong> {escape(insight_val)}</div>',
                    "    </div>",
                ]
            )

    html_parts.extend(["</body>", "</html>"])
    html_content = "\n".join(html_parts)

    try:
        pdf_bytes = HTML(string=html_content).write_pdf()
        output = io.BytesIO(pdf_bytes)
        output.seek(0)
        return output
    except Exception:
        report_lines = _build_report_lines(symptoms_list, start_date, end_date)
        return _generate_pdf_with_fpdf(report_lines)
