from __future__ import annotations

from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Профиль", callback_data="nav:profile")
    builder.button(text="📝 Добавить симптомы", callback_data="nav:add_symptom")
    builder.button(text="📅 История симптомов", callback_data="nav:symptoms")
    builder.button(text="📄 PDF отчёт", callback_data="nav:pdf")
    builder.button(text="🚪 Выйти", callback_data="nav:logout")
    builder.adjust(2, 2, 1)
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


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✖ Отменить", callback_data="symptom:cancel")
    return builder.as_markup()
