from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from api_client.client import BackendAPIError, api_client
from keyboards.menu import cancel_keyboard
from services.session_store import get_app_user_id, get_user_token


router = Router()


class SymptomStates(StatesGroup):
    waiting_for_field = State()


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
        await message.answer(f"❌ Не удалось сохранить запись: {exc}")
        return

    ai_text = created.get("ai_insights") or "Анализ временно недоступен."
    await state.clear()
    await message.answer(f"<b>Запись сохранена</b>\n\n<b>AI:</b> {ai_text}")


@router.callback_query(F.data == "symptom:cancel")
async def cancel_symptom(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("Отменено")
    await state.clear()
    await callback.message.edit_text("Заполнение симптомов отменено.")
