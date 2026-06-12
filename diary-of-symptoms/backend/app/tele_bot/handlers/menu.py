from __future__ import annotations

from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from api_client.client import api_client
from keyboards.auth import auth_start_keyboard
from keyboards.menu import main_menu_keyboard
from services.messages import send_or_edit
from services.session_store import clear_user_session, get_user_session


router = Router()


def _home_text(user: dict | None = None) -> str:
    if user and user.get("name"):
        name = escape(str(user.get("name")))
        email = escape(str(user.get("email") or ""))
        return (
            f"<b>Главное меню</b>\n\n"
            f"Привет, {name}.\n"
            f"{email}\n\n"
            f"Выберите раздел."
        )

    return "<b>Diary of Symptoms</b>\n\nВойдите или зарегистрируйтесь, чтобы продолжить."


async def show_auth_entry(target: Message | CallbackQuery) -> None:
    await send_or_edit(target, _home_text(None), auth_start_keyboard())


async def show_main_menu(target: Message | CallbackQuery, user: dict) -> None:
    await send_or_edit(target, _home_text(user), main_menu_keyboard())


async def _resolve_session(telegram_id: int) -> dict[str, object] | None:
    return await get_user_session(telegram_id)


async def _resolve_user(telegram_id: int) -> dict | None:
    session = await _resolve_session(telegram_id)
    if not session or not session.get("app_user_id"):
        return None

    try:
        return await api_client.get_user(int(session["app_user_id"]), token=str(session.get("auth_token") or ""))
    except Exception:
        return {"name": session.get("email"), "email": session.get("email")}


@router.message(Command("start"))
async def start_cmd(message: Message) -> None:
    user = await _resolve_user(message.from_user.id)
    if user:
        await show_main_menu(message, user)
        return

    await show_auth_entry(message)


@router.message(Command("menu"))
async def menu_cmd(message: Message) -> None:
    user = await _resolve_user(message.from_user.id)
    if user:
        await show_main_menu(message, user)
        return

    await show_auth_entry(message)


@router.callback_query(F.data == "menu:home")
async def menu_home(callback: CallbackQuery) -> None:
    user = await _resolve_user(callback.from_user.id)
    if user:
        await show_main_menu(callback, user)
        return

    await show_auth_entry(callback)


@router.callback_query(F.data == "nav:logout")
async def logout(callback: CallbackQuery) -> None:
    await clear_user_session(callback.from_user.id)
    await show_auth_entry(callback)
