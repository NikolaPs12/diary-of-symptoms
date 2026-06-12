from __future__ import annotations

from datetime import date

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery

from api_client.client import BackendAPIError, api_client
from handlers.menu import show_auth_entry
from keyboards.menu import report_keyboard
from services.messages import send_or_edit
from services.session_store import get_app_user_id, get_user_token


router = Router()


@router.callback_query(F.data == "nav:pdf")
async def report_menu(callback: CallbackQuery) -> None:
    await send_or_edit(
        callback,
        "<b>PDF отчёт</b>\n\nВыберите период или скачайте весь архив.",
        report_keyboard(),
    )


@router.callback_query(F.data.startswith("report:"))
async def generate_report(callback: CallbackQuery) -> None:
    action = callback.data.split(":", maxsplit=1)[1]
    if action == "back":
        from handlers.menu import show_main_menu

        app_user_id = await get_app_user_id(callback.from_user.id)
        token = await get_user_token(callback.from_user.id)
        if not app_user_id:
            await show_auth_entry(callback)
            return

        try:
            user = await api_client.get_user(app_user_id, token=token)
        except BackendAPIError:
            user = {"name": callback.from_user.full_name, "email": ""}
        await show_main_menu(callback, user)
        return

    app_user_id = await get_app_user_id(callback.from_user.id)
    token = await get_user_token(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return

    if action == "all":
        start_date = None
        end_date = None
    else:
        try:
            start_raw, end_raw = action.split(":", maxsplit=1)
            start_date = date.fromisoformat(start_raw)
            end_date = date.fromisoformat(end_raw)
        except ValueError:
            await send_or_edit(callback, "Не удалось распознать период отчёта.")
            return

    await callback.answer("Генерирую отчёт...")

    try:
        pdf_bytes, filename = await api_client.download_pdf_report(
            user_id=app_user_id,
            token=token,
            start_date=start_date,
            end_date=end_date,
        )
    except BackendAPIError as exc:
        await callback.message.answer(f"❌ Не удалось сформировать отчёт: {exc}")
        return

    await callback.message.answer_document(
        document=BufferedInputFile(file=pdf_bytes, filename=filename),
    )


@router.callback_query(F.data == "nav:symptoms")
async def symptoms_history(callback: CallbackQuery) -> None:
    await send_or_edit(
        callback,
        "<b>История симптомов</b>\n\nВыберите готовый период для PDF-отчёта.",
        report_keyboard(),
    )
