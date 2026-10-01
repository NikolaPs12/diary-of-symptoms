from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_voice_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Сохранить",
                    callback_data="confirm_voice",
                ),
                InlineKeyboardButton(
                    text="🔄 Записать заново",
                    callback_data="retry_voice",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="symptom:cancel",
                ),
            ],
        ]
    )
