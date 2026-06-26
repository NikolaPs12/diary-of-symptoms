from __future__ import annotations

from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from api_client.client import BackendAPIError, api_client
from handlers.menu import show_auth_entry, show_main_menu
from keyboards.menu import back_keyboard, notification_channels_keyboard, notifications_keyboard
from services.messages import send_or_edit
from services.session_store import get_app_user_id, get_user_token

router = Router()

WEEKDAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
WEEKDAY_LABELS = {
    "mon": "Пн",
    "tue": "Вт",
    "wed": "Ср",
    "thu": "Чт",
    "fri": "Пт",
    "sat": "Сб",
    "sun": "Вс",
}
DEFAULT_MESSAGE = "Не забудьте отметить симптомы в дневнике."


class ReminderStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_message = State()
    waiting_for_time = State()
    waiting_for_weekdays = State()


async def _resolve_context(telegram_id: int) -> tuple[int | None, str | None]:
    return await get_app_user_id(telegram_id), await get_user_token(telegram_id)


async def _load_reminders(telegram_id: int) -> tuple[int | None, str | None, list[dict]]:
    app_user_id, token = await _resolve_context(telegram_id)
    if not app_user_id:
        return None, None, []
    reminders = await api_client.list_reminders(app_user_id, token=token)
    return app_user_id, token, reminders


def _format_schedule(reminder: dict) -> str:
    send_time = reminder.get("send_time") or "--:--"
    weekdays = reminder.get("weekdays") or []
    weekdays_text = ", ".join(WEEKDAY_LABELS.get(day, day) for day in weekdays) if weekdays else "каждый день"
    return f"{send_time} · {weekdays_text}"


def _format_channel(reminder: dict) -> str:
    if reminder.get("send_email"):
        return "Email"
    return "Telegram"


def _render_notifications(reminders: list[dict]) -> str:
    if not reminders:
        return (
            "<b>Уведомления</b>\n\n"
            "Список пуст. Создайте уведомление и выберите канал доставки: Telegram или Email."
        )

    lines = ["<b>Уведомления</b>", "", "Выберите уведомление для управления:"]
    for reminder in reminders[:12]:
        status = "🟢" if reminder.get("enable") else "⚪️"
        title = escape(str(reminder.get("title") or "Без названия"))
        schedule = escape(_format_schedule(reminder))
        channel = escape(_format_channel(reminder))
        lines.append(f"{status} <b>{title}</b> — {channel}")
        lines.append(f"{schedule}")
        lines.append("")
    return "\n".join(lines).strip()


def _render_detail(reminder: dict) -> str:
    title = escape(str(reminder.get("title") or "Без названия"))
    message = escape(str(reminder.get("message") or ""))
    channel = escape(_format_channel(reminder))
    schedule = escape(_format_schedule(reminder))
    status = "включено" if reminder.get("enable") else "выключено"
    return (
        f"<b>{title}</b>\n\n"
        f"{message}\n\n"
        f"Канал: <b>{channel}</b>\n"
        f"Расписание: <b>{schedule}</b>\n"
        f"Статус: <b>{status}</b>"
    )


def _normalize_time(value: str) -> str:
    text = value.strip()
    parts = text.split(":")
    if len(parts) != 2:
        raise ValueError("Введите время в формате ЧЧ:ММ.")
    hour = int(parts[0])
    minute = int(parts[1])
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("Время должно быть в диапазоне 00:00–23:59.")
    return f"{hour:02d}:{minute:02d}"


def _normalize_weekdays(text: str) -> list[str]:
    raw = text.strip().lower()
    if not raw or raw in {"every", "daily", "каждый день", "ежедневно", "all"}:
        return []

    aliases = {
        "пн": "mon",
        "вт": "tue",
        "ср": "wed",
        "чт": "thu",
        "пт": "fri",
        "сб": "sat",
        "вс": "sun",
        "mon": "mon",
        "tue": "tue",
        "wed": "wed",
        "thu": "thu",
        "fri": "fri",
        "sat": "sat",
        "sun": "sun",
    }
    values = []
    for chunk in raw.replace(";", ",").split(","):
        key = aliases.get(chunk.strip())
        if not key:
            raise ValueError("Используйте дни через запятую: пн, вт, ср, чт, пт, сб, вс.")
        if key not in values:
            values.append(key)
    return sorted(values, key=WEEKDAY_ORDER.index)


@router.callback_query(F.data == "nav:notifications")
async def notifications_menu(callback: CallbackQuery) -> None:
    app_user_id, token, reminders = await _load_reminders(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return
    await send_or_edit(callback, _render_notifications(reminders), notifications_keyboard(reminders))


@router.callback_query(F.data == "notifications:back")
async def notifications_back(callback: CallbackQuery) -> None:
    app_user_id, token = await _resolve_context(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return
    try:
        user = await api_client.get_user(app_user_id, token=token)
    except BackendAPIError:
        user = {"name": callback.from_user.full_name, "email": ""}
    await show_main_menu(callback, user)


@router.callback_query(F.data == "notifications:create")
async def notifications_create(callback: CallbackQuery, state: FSMContext) -> None:
    app_user_id, _token = await _resolve_context(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return

    await state.clear()
    await state.update_data(reminder={"type": "custom", "enable": True})
    await callback.answer()
    await callback.message.answer("Введите название уведомления:", reply_markup=back_keyboard("notifications:back"))
    await state.set_state(ReminderStates.waiting_for_title)


@router.callback_query(F.data.startswith("notifications:view:"))
async def notifications_view(callback: CallbackQuery) -> None:
    reminder_id = int(callback.data.split(":")[-1])
    app_user_id, token = await _resolve_context(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return
    reminders = await api_client.list_reminders(app_user_id, token=token)
    reminder = next((item for item in reminders if int(item.get("id")) == reminder_id), None)
    if not reminder:
        await send_or_edit(callback, "Уведомление не найдено.", back_keyboard("nav:notifications"))
        return
    await send_or_edit(callback, _render_detail(reminder), notifications_keyboard(reminders, active_id=reminder_id))


@router.callback_query(F.data.startswith("notifications:toggle:"))
async def notifications_toggle(callback: CallbackQuery) -> None:
    reminder_id = int(callback.data.split(":")[-1])
    app_user_id, token, reminders = await _load_reminders(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return
    reminder = next((item for item in reminders if int(item.get("id")) == reminder_id), None)
    if not reminder:
        await send_or_edit(callback, "Уведомление не найдено.", back_keyboard("nav:notifications"))
        return

    try:
        updated = await api_client.toggle_reminder(reminder_id, not bool(reminder.get("enable")), user_id=app_user_id, token=token)
    except BackendAPIError as exc:
        await send_or_edit(callback, f"❌ Не удалось изменить уведомление: {escape(str(exc))}")
        return

    refreshed = await api_client.list_reminders(app_user_id, token=token)
    await send_or_edit(callback, _render_detail(updated), notifications_keyboard(refreshed, active_id=reminder_id))


@router.callback_query(F.data.startswith("notifications:delete:"))
async def notifications_delete(callback: CallbackQuery) -> None:
    reminder_id = int(callback.data.split(":")[-1])
    app_user_id, token = await _resolve_context(callback.from_user.id)
    if not app_user_id:
        await show_auth_entry(callback)
        return

    try:
        await api_client.delete_reminder(reminder_id, user_id=app_user_id, token=token)
        reminders = await api_client.list_reminders(app_user_id, token=token)
    except BackendAPIError as exc:
        await send_or_edit(callback, f"❌ Не удалось удалить уведомление: {escape(str(exc))}")
        return

    await send_or_edit(callback, _render_notifications(reminders), notifications_keyboard(reminders))


@router.callback_query(F.data == "notifications:channel:telegram")
async def notifications_channel_telegram(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    reminder = dict(data.get("reminder") or {})
    reminder.update({"send_telegram": True, "send_email": False, "telegram_chat_id": callback.from_user.id})
    await state.update_data(reminder=reminder)
    await callback.answer()
    await callback.message.answer(
        "Введите время отправки в формате ЧЧ:ММ, например 09:30.",
        reply_markup=back_keyboard("nav:notifications"),
    )
    await state.set_state(ReminderStates.waiting_for_time)


@router.callback_query(F.data == "notifications:channel:email")
async def notifications_channel_email(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    reminder = dict(data.get("reminder") or {})
    reminder.update({"send_telegram": False, "send_email": True, "telegram_chat_id": None})
    await state.update_data(reminder=reminder)
    await callback.answer()
    await callback.message.answer(
        "Введите время отправки в формате ЧЧ:ММ, например 09:30.",
        reply_markup=back_keyboard("nav:notifications"),
    )
    await state.set_state(ReminderStates.waiting_for_time)


@router.message(ReminderStates.waiting_for_title)
async def reminder_title(message: Message, state: FSMContext) -> None:
    title = message.text.strip()
    if not title:
        await message.answer("Название не должно быть пустым.")
        return
    data = await state.get_data()
    reminder = dict(data.get("reminder") or {})
    reminder["title"] = title
    await state.update_data(reminder=reminder)
    await message.answer(
        "Введите текст уведомления или отправьте '-' для шаблона по умолчанию.",
        reply_markup=back_keyboard("nav:notifications"),
    )
    await state.set_state(ReminderStates.waiting_for_message)


@router.message(ReminderStates.waiting_for_message)
async def reminder_message(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    data = await state.get_data()
    reminder = dict(data.get("reminder") or {})
    reminder["message"] = DEFAULT_MESSAGE if text == "-" else text
    await state.update_data(reminder=reminder)
    await message.answer("Выберите канал доставки.", reply_markup=notification_channels_keyboard())


@router.message(ReminderStates.waiting_for_time)
async def reminder_time(message: Message, state: FSMContext) -> None:
    try:
        send_time = _normalize_time(message.text)
    except ValueError as exc:
        await message.answer(f"❌ {exc}")
        return

    data = await state.get_data()
    reminder = dict(data.get("reminder") or {})
    reminder["send_time"] = send_time
    await state.update_data(reminder=reminder)
    await message.answer(
        "Введите дни недели через запятую (пн, ср, пт) или напишите 'каждый день'.",
        reply_markup=back_keyboard("nav:notifications"),
    )
    await state.set_state(ReminderStates.waiting_for_weekdays)


@router.message(ReminderStates.waiting_for_weekdays)
async def reminder_weekdays(message: Message, state: FSMContext) -> None:
    try:
        weekdays = _normalize_weekdays(message.text)
    except ValueError as exc:
        await message.answer(f"❌ {exc}")
        return

    data = await state.get_data()
    reminder = dict(data.get("reminder") or {})
    reminder["weekdays"] = weekdays

    app_user_id, token = await _resolve_context(message.from_user.id)
    if not app_user_id:
        await state.clear()
        await message.answer("Сначала войдите заново через /start.")
        return

    reminder["user_id"] = app_user_id

    try:
        created = await api_client.create_reminder(reminder, token=token)
        reminders = await api_client.list_reminders(app_user_id, token=token)
    except BackendAPIError as exc:
        await message.answer(f"❌ Не удалось создать уведомление: {escape(str(exc))}")
        return

    await state.clear()
    await message.answer(f"✅ Создано уведомление: <b>{escape(str(created.get('title') or 'Без названия'))}</b>")
    await message.answer(_render_notifications(reminders), reply_markup=notifications_keyboard(reminders, active_id=int(created.get("id"))))
