import io
import os
import re
import textwrap
from html import unescape
from pathlib import Path

from datetime import date, datetime
import sqlalchemy


try:
    from google import genai
except ImportError:  # pragma: no cover
    genai = None

try:
    from fpdf import FPDF
except ImportError:  # pragma: no cover
    FPDF = None


FONT_CANDIDATES = [
    "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/google-droid-sans-fonts/DroidSans.ttf",
    "/usr/share/fonts/google-carlito-fonts/Carlito-Regular.ttf",
    "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf",
    "/usr/share/fonts/adwaita-sans-fonts/AdwaitaSans-Regular.ttf",
]


def build_ai_insight(symptom_entry) -> str:
    prompt = (
        f"Проанализируй состояние. Симптом: {symptom_entry.symptom}, "
        f"тяжесть: {symptom_entry.severity}/10, длительность: {symptom_entry.duration}. "
        f"Сон: {symptom_entry.sleep_hours}ч (качество: {symptom_entry.sleep_quality}/10). "
        f"Стресс: {symptom_entry.stress_level}/10. Состояние: {symptom_entry.body_state}. "
        f"Заметки: {symptom_entry.notes}. Еда: {symptom_entry.food_notes}. "
        f"Лекарства: {symptom_entry.medications_taken}. "
        "Назови возможные триггеры и дай краткие рекомендации."
    )
    api_key = os.getenv("API_AI_KEY")

    if genai is None or not api_key:
        return (
            f"Possible triggers: stress {symptom_entry.stress_level}/10, "
            f"sleep quality {symptom_entry.sleep_quality}/10, and recent food or medication patterns."
        )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        return response.text
    except Exception:
        return (
            f"Possible triggers: stress {symptom_entry.stress_level}/10, "
            f"sleep quality {symptom_entry.sleep_quality}/10, and recent food or medication patterns."
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
    # 1. Формируем период для заголовка
    period_str = f"{start_date or '...'} - {end_date or '...'}" if start_date or end_date else "За всё время"

    # 2. Пишем красивую HTML-верстку со стилями
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm;
            }}
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                color: #333333;
                line-height: 1.4;
            }}
            .header {{
                border-bottom: 2px solid #4F46E5;
                padding-bottom: 15px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                font-size: 24px;
                color: #1F2937;
                margin: 0 0 5px 0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .header p {{
                color: #6B7280;
                margin: 0;
                font-size: 14px;
            }}
            .card {{
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                page-break-inside: avoid; /* Чтобы карточка не разрывалась между страницами */
            }}
            .card-header {{
                font-size: 14px;
                font-weight: bold;
                color: #4F46E5;
                border-bottom: 1px solid #F3F4F6;
                padding-bottom: 8px;
                margin-bottom: 12px;
            }}
            .grid {{
                display: flex;
                flex-wrap: wrap;
                margin-bottom: 10px;
            }}
            .grid-item {{
                flex: 1;
                min-width: 30%;
                font-size: 13px;
                margin-bottom: 8px;
            }}
            .grid-item span {{
                color: #6B7280;
                display: block;
                font-size: 11px;
                text-transform: uppercase;
            }}
            .notes {{
                background: #F9FAFB;
                padding: 10px;
                border-left: 3px solid #D1D5DB;
                font-size: 13px;
                margin-top: 10px;
                border-radius: 0 4px 4px 0;
            }}
        </style>
    </head>
    <body>

        <div class="header">
            <h1>Diary of Symptoms Report</h1>
            <p>Период отчёта: {period_str}</p>
        </div>
    </div>
    """

    # 3. Циклом добавляем карточки симптомов в HTML
    for item in symptoms_list:
        date_str = item.start_at.strftime("%d.%m.%Y в %H:%M")
        symptom_name = item.symptom if item.symptom else "Не указан"
        severity_val = f"{item.severity}/10"
        duration_val = item.duration if item.duration else "—"
        body_val = item.body_state if item.body_state else "—"
        stress_val = f"{item.stress_level}/10"
        sleep_val = f"{item.sleep_hours}ч (Качество: {item.sleep_quality}/10)"
        meds_val = item.medications_taken if item.medications_taken else "Нет"
        food_val = item.food_notes if item.food_notes else "Нет заметок"
        notes_val = item.notes if item.notes else "Нет описания"

        html_content += f"""
        <div class="card">
            <div class="card-header">Запись от {date_str}</div>
            
            <div class="grid">
                <div class="grid-item"><span>Симптом</span><strong>{symptom_name}</strong></div>
                <div class="grid-item"><span>Интенсивность</span><strong>{severity_val}</strong></div>
                <div class="grid-item"><span>Длительность</span><strong>{duration_val}</strong></div>
            </div>
            
            <div class="grid">
                <div class="grid-item"><span>Состояние тела</span>{body_val}</div>
                <div class="grid-item"><span>Уровень стресса</span>{stress_val}</div>
                <div class="grid-item"><span>Сон</span>{sleep_val}</div>
            </div>

            <div class="grid">
                <div class="grid-item"><span>Медикаменты</span>{meds_val}</div>
                <div class="grid-item"><span>Еда</span>{food_val}</div>
            </div>

            <div class="notes">
                <strong>Заметки:</strong> {notes_val}
            </div>
        </div>
        """

    # Закрываем теги HTML
    html_content += """
    </body>
    </html>
    """

    # 4. Самая магия: WeasyPrint компилирует HTML со стилями прямо в байты PDF
    pdf_bytes = HTML(string=html_content).write_pdf()
    
    return io.BytesIO(pdf_bytes)