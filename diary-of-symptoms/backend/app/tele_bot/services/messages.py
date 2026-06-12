from __future__ import annotations

from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message


async def send_or_edit(target: Message | CallbackQuery, text: str, reply_markup=None) -> None:
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        await target.answer()
        return

    await target.answer(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
