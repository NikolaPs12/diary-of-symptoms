from __future__ import annotations

from datetime import datetime
from html import escape
from statistics import mean


def _parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _fmt_number(value: float | int | None, suffix: str = "") -> str:
    if value is None:
        return "Нет данных"
    if isinstance(value, float):
        return f"{value:.1f}{suffix}"
    return f"{value}{suffix}"


def _short_text(value: str | None, limit: int = 260) -> str:
    if not value:
        return "Нет заметки"
    clean = value.strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def compute_health_stats(entries: list[dict]) -> dict[str, object]:
    if not entries:
        return {
            "entries_count": 0,
            "average_severity": None,
            "average_sleep": None,
            "average_stress": None,
            "latest_entry_at": None,
            "latest_ai_insight": None,
        }

    ordered = sorted(entries, key=lambda item: item.get("created_at") or item.get("start_at") or "")
    latest = ordered[-1]

    def safe_float(field: str) -> list[float]:
        values = []
        for item in entries:
            value = item.get(field)
            if value is not None:
                values.append(float(value))
        return values

    severity_values = safe_float("severity")
    sleep_values = safe_float("sleep_hours")
    stress_values = safe_float("stress_level")

    return {
        "entries_count": len(entries),
        "average_severity": mean(severity_values) if severity_values else None,
        "average_sleep": mean(sleep_values) if sleep_values else None,
        "average_stress": mean(stress_values) if stress_values else None,
        "latest_entry_at": latest.get("created_at") or latest.get("start_at"),
        "latest_ai_insight": latest.get("ai_insights") or None,
    }


def format_user_profile(user: dict, stats: dict[str, object], medications_count: int) -> str:
    name = escape(str(user.get("name") or "Не указано"))
    email = escape(str(user.get("email") or "Не указано"))
    plan_type = escape(str(user.get("plan_type") or "free"))
    age = escape(str(user.get("age") or "Не указано"))
    weight = escape(str(user.get("weight") or "Не указано"))
    height = escape(str(user.get("height") or "Не указано"))
    verified = "Да" if user.get("email_verified") else "Нет"

    latest = _parse_datetime(stats.get("latest_entry_at"))
    latest_text = latest.isoformat(sep=" ", timespec="minutes") if latest else "Нет записей"
    avg_severity = _fmt_number(stats.get("average_severity"), "/10")
    avg_sleep = _fmt_number(stats.get("average_sleep"), " ч")
    avg_stress = _fmt_number(stats.get("average_stress"), "/10")

    return (
        f"<b>Профиль</b>\n\n"
        f"<b>Пользователь</b>\n"
        f"• Имя: {name}\n"
        f"• Почта: {email}\n"
        f"• Возраст: {age}\n"
        f"• План: {plan_type}\n"
        f"• Подтверждена почта: {verified}\n\n"
        f"<b>Базовые данные</b>\n"
        f"• Вес: {weight}\n"
        f"• Рост: {height}\n"
        f"• Медкарточек: {medications_count}\n\n"
        f"<b>Сводка здоровья</b>\n"
        f"• Записей симптомов: {stats.get('entries_count', 0)}\n"
        f"• Средняя тяжесть: {avg_severity}\n"
        f"• Средний сон: {avg_sleep}\n"
        f"• Средний стресс: {avg_stress}\n"
        f"• Последняя активность: {escape(latest_text)}\n"
    )


def format_statistics(stats: dict[str, object]) -> str:
    return (
        f"<b>Статистика</b>\n\n"
        f"• Записей: {stats.get('entries_count', 0)}\n"
        f"• Средняя тяжесть: {_fmt_number(stats.get('average_severity'), '/10')}\n"
        f"• Средний сон: {_fmt_number(stats.get('average_sleep'), ' ч')}\n"
        f"• Средний стресс: {_fmt_number(stats.get('average_stress'), '/10')}\n"
    )


def format_latest_insight(insight: str | None) -> str:
    return (
        "<b>AI-заметка</b>\n\n"
        f"{escape(_short_text(insight, 420))}"
        if insight
        else "<b>AI-заметка</b>\n\nПока нет сгенерированного анализа для последней записи."
    )


def format_medication_card(medication: dict | None) -> str:
    if not medication:
        return "<b>Медикаменты</b>\n\nПока нет сохранённой медицинской карточки."

    regular = medication.get("regular_medications") or []
    regular_text = ", ".join(str(item) for item in regular) if regular else "Не указано"
    allergies = medication.get("allergies") or []
    allergy_text = ", ".join(str(item) for item in allergies) if allergies else "Нет"

    return (
        f"<b>Медикаменты</b>\n\n"
        f"• Название: {escape(str(medication.get('name') or 'Не указано'))}\n"
        f"• Дозировка: {escape(str(medication.get('dosage') or 'Не указано'))}\n"
        f"• Диагноз: {escape(str(medication.get('diagnosis') or 'Не указано'))}\n"
        f"• Регулярные: {escape(regular_text)}\n"
        f"• Аллергии: {escape(allergy_text)}\n"
        f"• Заметки: {escape(str(medication.get('notes') or 'Нет'))}\n"
    )


def format_symptoms_list(entries: list[dict], limit: int = 5) -> str:
    if not entries:
        return "<b>Последние симптомы</b>\n\nЗаписей пока нет."

    ordered = sorted(entries, key=lambda item: item.get("created_at") or item.get("start_at") or "", reverse=True)
    lines = ["<b>Последние симптомы</b>", ""]
    for index, entry in enumerate(ordered[:limit], start=1):
        created_at = _parse_datetime(entry.get("created_at") or entry.get("start_at"))
        when = created_at.isoformat(sep=" ", timespec="minutes") if created_at else "Неизвестно"
        lines.extend(
            [
                f"<b>{index}. {escape(str(entry.get('symptom') or 'Не указано'))}</b>",
                f"• Когда: {escape(when)}",
                f"• Тяжесть: {entry.get('severity', '—')}/10",
                f"• Сон: {entry.get('sleep_hours', '—')} ч",
                f"• Стресс: {entry.get('stress_level', '—')}/10",
                f"• AI: {escape(_short_text(entry.get('ai_insights'), 180))}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()
