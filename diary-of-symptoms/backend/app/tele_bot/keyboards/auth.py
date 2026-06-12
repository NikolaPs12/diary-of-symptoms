from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def auth_start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔑 Войти", callback_data="auth:login")
    builder.button(text="📝 Регистрация", callback_data="auth:register")
    builder.adjust(1)
    return builder.as_markup()
