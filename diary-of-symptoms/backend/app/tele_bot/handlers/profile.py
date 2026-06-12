from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from api_client.client import BackendAPIError, api_client
from handlers.menu import show_auth_entry, show_main_menu
from keyboards.menu import profile_keyboard
from services.formatters import (
    format_latest_insight,
    format_medication_card,
    format_statistics,
    format_symptoms_list,
    format_user_profile,
)
from services.messages import send_or_edit
from services.profile_service import load_profile_context
from services.session_store import get_app_user_id, get_user_token


router = Router()


async def _resolve_context(telegram_id: int) -> tuple[int | None, str | None]:
    return await get_app_user_id(telegram_id), await get_user_token(telegram_id)


@router.message(Command("profile"))
async def profile_cmd(message: Message) -> None:
    await open_profile(message)


@router.callback_query(F.data == "nav:profile")
async def profile_nav(callback: CallbackQuery) -> None:
    await open_profile(callback)


async def open_profile(target: Message | CallbackQuery) -> None:
    telegram_id = target.from_user.id
    app_user_id, token = await _resolve_context(telegram_id)
    if not app_user_id:
        await show_auth_entry(target)
        return

    try:
        context = await load_profile_context(api_client, app_user_id, token)
    except BackendAPIError as exc:
        await send_or_edit(target, f"❌ Не удалось загрузить профиль: {exc}")
        return

    text = (
        f"{format_user_profile(context.user, context.stats, len(context.medications))}\n"
        f"{format_latest_insight(context.stats.get('latest_ai_insight'))}"
    )
    await send_or_edit(target, text, profile_keyboard())


@router.callback_query(F.data == "profile:statistics")
async def profile_statistics(callback: CallbackQuery) -> None:
    app_user_id, token = await _resolve_context(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return

    try:
        context = await load_profile_context(api_client, app_user_id, token)
    except BackendAPIError as exc:
        await send_or_edit(callback, f"❌ Не удалось загрузить статистику: {exc}")
        return

    await send_or_edit(callback, format_statistics(context.stats), profile_keyboard())


@router.callback_query(F.data == "profile:symptoms")
async def profile_symptoms(callback: CallbackQuery) -> None:
    app_user_id, token = await _resolve_context(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return

    try:
        context = await load_profile_context(api_client, app_user_id, token)
    except BackendAPIError as exc:
        await send_or_edit(callback, f"❌ Не удалось загрузить симптомы: {exc}")
        return

    await send_or_edit(callback, format_symptoms_list(context.entries), profile_keyboard())


@router.callback_query(F.data == "profile:medications")
async def profile_medications(callback: CallbackQuery) -> None:
    app_user_id, token = await _resolve_context(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return

    try:
        context = await load_profile_context(api_client, app_user_id, token)
    except BackendAPIError as exc:
        await send_or_edit(callback, f"❌ Не удалось загрузить медикаменты: {exc}")
        return

    await send_or_edit(callback, format_medication_card(context.medications[0] if context.medications else None), profile_keyboard())


@router.callback_query(F.data == "profile:back")
async def profile_back(callback: CallbackQuery) -> None:
    app_user_id, token = await _resolve_context(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return

    try:
        user = await api_client.get_user(app_user_id, token=token)
    except BackendAPIError:
        user = {"name": callback.from_user.full_name, "email": ""}
    await show_main_menu(callback, user)
