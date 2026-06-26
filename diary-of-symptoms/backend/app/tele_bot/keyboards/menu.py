from __future__ import annotations

from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Профиль", callback_data="nav:profile")
    builder.button(text="🔔 Уведомления", callback_data="nav:notifications")
    builder.button(text="📝 Добавить симптомы", callback_data="nav:add_symptom")
    builder.button(text="📅 История симптомов", callback_data="nav:symptoms")
    builder.button(text="📄 PDF отчёт", callback_data="nav:pdf")
    builder.button(text="🚪 Выйти", callback_data="nav:logout")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🩺 Мои симптомы", callback_data="profile:symptoms")
    builder.button(text="💊 Мои лекарства", callback_data="profile:medications")
    builder.button(text="📊 Статистика", callback_data="profile:statistics")
    builder.button(text="⬅️ Назад", callback_data="profile:back")
    builder.adjust(2, 2)
    return builder.as_markup()


def symptoms_history_keyboard() -> InlineKeyboardMarkup:
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    builder = InlineKeyboardBuilder()
    builder.button(text="За 7 дней", callback_data=f"history:{week_ago.isoformat()}:{today.isoformat()}")
    builder.button(text="За месяц", callback_data=f"history:{month_ago.isoformat()}:{today.isoformat()}")
    builder.button(text="За все время", callback_data="history:all")
    builder.button(text="⬅️ Назад", callback_data="history:back")
    builder.adjust(1)
    return builder.as_markup()


def report_keyboard() -> InlineKeyboardMarkup:
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    builder = InlineKeyboardBuilder()
    builder.button(text="За 7 дней", callback_data=f"report:{week_ago.isoformat()}:{today.isoformat()}")
    builder.button(text="За месяц", callback_data=f"report:{month_ago.isoformat()}:{today.isoformat()}")
    builder.button(text="За все время", callback_data="report:all")
    builder.button(text="⬅️ Назад", callback_data="report:back")
    builder.adjust(1)
    return builder.as_markup()


def back_keyboard(callback_data: str = "menu:home") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=callback_data)
    return builder.as_markup()


def notification_channels_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Telegram", callback_data="notifications:channel:telegram")
    builder.button(text="Email", callback_data="notifications:channel:email")
    builder.button(text="⬅️ Назад", callback_data="nav:notifications")
    builder.adjust(2, 1)
    return builder.as_markup()


def notifications_keyboard(reminders: list[dict], active_id: int | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Создать", callback_data="notifications:create")

    if active_id is not None:
        active = next((item for item in reminders if int(item.get("id")) == active_id), None)
        if active is not None:
            toggle_label = "⏸ Выключить" if active.get("enable") else "▶️ Включить"
            builder.button(text=toggle_label, callback_data=f"notifications:toggle:{active_id}")
            builder.button(text="🗑 Удалить", callback_data=f"notifications:delete:{active_id}")

    for reminder in reminders[:10]:
        reminder_id = int(reminder.get("id"))
        title = str(reminder.get("title") or f"#{reminder_id}")[:24]
        prefix = "🟢" if reminder.get("enable") else "⚪️"
        builder.button(text=f"{prefix} {title}", callback_data=f"notifications:view:{reminder_id}")

    builder.button(text="⬅️ Назад", callback_data="notifications:back")
    builder.adjust(1, 2, *([1] * min(len(reminders), 10)), 1)
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✖ Отменить", callback_data="symptom:cancel")
    return builder.as_markup()
