from __future__ import annotations

import logging
import os
import re
from html import escape, unescape
from io import BytesIO
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from api_client.client import BackendAPIError, api_client
from keyboards.menu import cancel_keyboard
from keyboards.symptom import get_voice_confirmation_keyboard
from services.session_store import get_app_user_id, get_user_token
from services.symptoms_voic import extract_symptom_json_from_audio


router = Router()
logger = logging.getLogger(__name__)


class SymptomStates(StatesGroup):
    waiting_for_field = State()


class VoiceStates(StatesGroup):
    waiting_for_voice = State()
    waiting_for_confirmation = State()


SYMPTOM_FIELDS: list[dict[str, str]] = [
    {"key": "symptom", "prompt": "🤕 Главный симптом:"},
    {"key": "body_state", "prompt": "🧘 Общее состояние:"},
    {"key": "start_at", "prompt": "🕒 Когда началось? (ДД.ММ.ГГГГ ЧЧ:ММ или 'сейчас')"},
    {"key": "duration", "prompt": "⏳ Длительность:"},
    {"key": "sleep_hours", "prompt": "😴 Сон за сутки (часы):"},
    {"key": "severity", "prompt": "📊 Тяжесть от 0 до 10:"},
    {"key": "stress_level", "prompt": "🤯 Стресс от 0 до 10:"},
    {"key": "sleep_quality", "prompt": "💤 Качество сна от 0 до 10:"},
    {"key": "food_notes", "prompt": "🍏 Что ели/пили?"},
    {"key": "medications_taken", "prompt": "💊 Лекарства:"},
    {"key": "notes", "prompt": "📝 Дополнительные заметки:"},
]

VOICE_PROMPT = (
    "🎙️ <b>Запишите одно голосовое сообщение</b>\n\n"
    "Расскажите о симптоме, когда он начался, сколько длится, "
    "как сильно беспокоит по шкале от 0 до 10, сколько вы спали, "
    "уровень стресса, качество сна, еду, лекарства и дополнительные заметки.\n\n"
    "Если чего-то не знаете, просто пропустите."
)

REQUIRED_VOICE_FIELDS = (
    "symptom",
    "severity",
    "duration",
    "sleep_quality",
    "sleep_hours",
    "stress_level",
)


def _telegram_text(value: object) -> str:
    return escape(str(value or "не указано"))


def _format_ai_insights(value: object) -> str:
    text = str(value or "Анализ временно недоступен.")
    text = re.sub(r"</?(h[1-6]|p|ol|ul|li|br)\b[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", unescape(text)).strip()
    if len(text) > 3500:
        text = f"{text[:3500].rstrip()}\n\n..."
    return escape(text or "Анализ временно недоступен.")


@router.callback_query(F.data == "nav:add_symptom")
async def start_symptom_add(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    fields = SYMPTOM_FIELDS.copy()
    first = fields.pop(0)
    await state.update_data(remaining_fields=fields, answers={}, current_key=first["key"])
    await callback.message.answer(first["prompt"], reply_markup=cancel_keyboard())
    await state.set_state(SymptomStates.waiting_for_field)


@router.message(F.text == "/addsymptom")
async def start_symptom_add_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    fields = SYMPTOM_FIELDS.copy()
    first = fields.pop(0)
    await state.update_data(remaining_fields=fields, answers={}, current_key=first["key"])
    await message.answer(first["prompt"], reply_markup=cancel_keyboard())
    await state.set_state(SymptomStates.waiting_for_field)


@router.callback_query(F.data == "nav:add_symptom_voice")
async def start_symptom_add_voice(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await state.set_state(VoiceStates.waiting_for_voice)
    await callback.message.answer(VOICE_PROMPT, reply_markup=cancel_keyboard())


@router.message(F.text == "/addsymptomvoice")
async def start_symptom_add_voice_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(VoiceStates.waiting_for_voice)
    await message.answer(VOICE_PROMPT, reply_markup=cancel_keyboard())


@router.message(VoiceStates.waiting_for_voice, F.voice)
async def process_symptom_voice(message: Message, state: FSMContext) -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        await message.answer(
            "❌ Голосовое добавление не настроено: отсутствует GEMINI_API_KEY в .env.",
            reply_markup=cancel_keyboard(),
        )
        return

    status_message = await message.answer("🎙️ Обрабатываю голосовое...")

    try:
        audio_buffer = BytesIO()
        await message.bot.download(message.voice, destination=audio_buffer)
        audio_bytes = audio_buffer.getvalue()

        payload = await extract_symptom_json_from_audio(
            audio_bytes=audio_bytes,
            api_key=api_key,
            mime_type=message.voice.mime_type or "audio/ogg",
        )
    except Exception as exc:
        logger.exception("Failed to process voice symptom")
        await status_message.edit_text(
            f"❌ Не получилось обработать голосовое: {exc}\n\n"
            "Попробуйте записать сообщение ещё раз.",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(voice_payload=payload)
    await state.set_state(VoiceStates.waiting_for_confirmation)

    summary = "\n".join(
        f"<b>{field['prompt'].split(':', 1)[0]}</b> {_telegram_text(payload.get(field['key']))}"
        for field in SYMPTOM_FIELDS
    )

    await status_message.edit_text(
        f"✅ Я распознал запись:\n\n{summary}\n\nСохранить?",
        reply_markup=get_voice_confirmation_keyboard(),
    )


@router.message(VoiceStates.waiting_for_voice)
async def process_non_voice_in_voice_state(message: Message) -> None:
    await message.answer(
        "Отправьте именно голосовое сообщение.",
        reply_markup=cancel_keyboard(),
    )


@router.callback_query(VoiceStates.waiting_for_confirmation, F.data == "retry_voice")
async def retry_symptom_voice(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(voice_payload=None)
    await state.set_state(VoiceStates.waiting_for_voice)
    await callback.message.edit_text(VOICE_PROMPT, reply_markup=cancel_keyboard())


@router.callback_query(VoiceStates.waiting_for_confirmation, F.data == "confirm_voice")
async def confirm_symptom_voice(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    payload = data.get("voice_payload")

    if not isinstance(payload, dict):
        await state.clear()
        await callback.message.edit_text("Данные голосового сообщения потеряны. Начните заново.")
        return

    missing_fields = [field for field in REQUIRED_VOICE_FIELDS if payload.get(field) is None]
    if missing_fields:
        await callback.message.edit_text(
            "❌ В голосовом сообщении не хватает обязательных данных: "
            f"{', '.join(missing_fields)}.\n\n"
            "Запишите голосовое ещё раз и назовите эти значения.",
            reply_markup=get_voice_confirmation_keyboard(),
        )
        return

    app_user_id = await get_app_user_id(callback.from_user.id)
    token = await get_user_token(callback.from_user.id)
    if not app_user_id:
        await state.clear()
        await callback.message.edit_text("Сначала войдите заново через /start.")
        return

    payload["user_id"] = app_user_id
    await callback.message.edit_text("🔄 Сохраняю запись...")

    try:
        created = await api_client.create_symptom_entry(payload, token=token)
    except BackendAPIError as exc:
        await callback.message.edit_text(
            f"❌ Не удалось сохранить запись: {_telegram_text(exc)}",
            reply_markup=get_voice_confirmation_keyboard(),
        )
        return

    ai_text = _format_ai_insights(created.get("ai_insights"))
    await state.clear()
    await callback.message.edit_text(f"<b>Запись сохранена</b>\n\n<b>AI:</b> {ai_text}")


@router.message(SymptomStates.waiting_for_field)
async def process_symptom_field(message: Message, state: FSMContext) -> None:
    user_input = message.text.strip()
    data = await state.get_data()
    current_key = data.get("current_key")
    remaining_fields = data.get("remaining_fields", [])
    answers = data.get("answers", {})

    if not current_key:
        await state.clear()
        await message.answer("Сессия заполнения потеряна. Начните заново через /start.")
        return

    if current_key in {"severity", "sleep_quality", "stress_level"}:
        if not user_input.isdigit() or not (0 <= int(user_input) <= 10):
            await message.answer("❌ Введите целое число от 0 до 10.", reply_markup=cancel_keyboard())
            return
        user_input = int(user_input)
    elif current_key == "sleep_hours":
        try:
            user_input = float(user_input.replace(",", "."))
        except ValueError:
            await message.answer("❌ Введите число, например 7 или 7.5.", reply_markup=cancel_keyboard())
            return
    elif current_key == "start_at":
        if user_input.lower() in {"сейчас", "now", "today", "сегодня"}:
            user_input = datetime.now().isoformat()
        else:
            try:
                user_input = datetime.strptime(user_input, "%d.%m.%Y %H:%M").isoformat()
            except ValueError:
                await message.answer("❌ Формат: ДД.ММ.ГГГГ ЧЧ:ММ.", reply_markup=cancel_keyboard())
                return

    answers[current_key] = user_input

    if remaining_fields:
        next_field = remaining_fields.pop(0)
        await state.update_data(remaining_fields=remaining_fields, answers=answers, current_key=next_field["key"])
        await message.answer(next_field["prompt"], reply_markup=cancel_keyboard())
        return

    app_user_id = await get_app_user_id(message.from_user.id)
    token = await get_user_token(message.from_user.id)
    if not app_user_id:
        await state.clear()
        await message.answer("Сначала войдите заново через /start.")
        return

    answers["user_id"] = app_user_id
    await message.answer("🔄 Сохраняю запись...")

    try:
        created = await api_client.create_symptom_entry(answers, token=token)
    except BackendAPIError as exc:
        await state.clear()
        await message.answer(f"❌ Не удалось сохранить запись: {_telegram_text(exc)}")
        return

    ai_text = _format_ai_insights(created.get("ai_insights"))
    await state.clear()
    await message.answer(f"<b>Запись сохранена</b>\n\n<b>AI:</b> {ai_text}")


@router.callback_query(F.data == "symptom:cancel")
async def cancel_symptom(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("Отменено")
    await state.clear()
    await callback.message.edit_text("Заполнение симптомов отменено.")
