from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from api_client.client import BackendAPIError, api_client
from handlers.menu import show_main_menu
from services.session_store import save_user_session


router = Router()


class LoginStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()


class RegistrationStates(StatesGroup):
    waiting_for_field = State()


REGISTRATION_FIELDS: list[dict[str, str]] = [
    {"key": "name", "prompt": "📝 Введите ваше имя:"},
    {"key": "email", "prompt": "📧 Введите email:"},
    {"key": "age", "prompt": "🔢 Сколько вам лет?"},
    {"key": "password", "prompt": "🔒 Придумайте пароль:"},
    {"key": "weight", "prompt": "⚖️ Вес, кг:"},
    {"key": "height", "prompt": "📏 Рост, см:"},
    {"key": "puls_is_normal", "prompt": "🫀 Пульс в норме?"},
    {"key": "systolic", "prompt": "🩺 Верхнее давление:"},
    {"key": "diastolic", "prompt": "🩺 Нижнее давление:"},
]


@router.callback_query(F.data == "auth:login")
async def login_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await callback.message.answer("📥 Введите email:")
    await state.set_state(LoginStates.waiting_for_email)


@router.message(LoginStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext) -> None:
    email = message.text.strip()
    if "@" not in email:
        await message.answer("❌ Некорректный email. Попробуйте ещё раз:")
        return

    await state.update_data(email=email)
    await message.answer("🔑 Теперь введите пароль:")
    await state.set_state(LoginStates.waiting_for_password)


@router.message(LoginStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext) -> None:
    password = message.text.strip()
    data = await state.get_data()
    email = data.get("email")

    if not email:
        await state.clear()
        await message.answer("Сессия ввода потеряна. Начните вход заново через /start.")
        return

    await message.answer("🔄 Проверяю данные...")

    try:
        auth = await api_client.login(email=email, password=password)
    except BackendAPIError as exc:
        await message.answer(f"❌ Ошибка входа: {exc}")
        return

    user = auth["user"]
    await save_user_session(
        telegram_id=message.from_user.id,
        token=auth["token"],
        email=str(user.get("email") or email),
        created_at=user.get("created_at"),
        app_user_id=int(user["id"]),
    )
    await state.clear()
    await show_main_menu(message, user)


@router.callback_query(F.data == "auth:register")
async def register_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    fields = REGISTRATION_FIELDS.copy()
    first = fields.pop(0)
    await state.update_data(remaining_fields=fields, answers={}, current_key=first["key"])
    await callback.message.answer(first["prompt"])
    await state.set_state(RegistrationStates.waiting_for_field)


@router.message(RegistrationStates.waiting_for_field)
async def register_field(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    current_key = data.get("current_key")
    remaining_fields = data.get("remaining_fields", [])
    answers = data.get("answers", {})
    value = message.text.strip()

    if not current_key:
        await state.clear()
        await message.answer("Сессия регистрации потеряна. Начните заново через /start.")
        return

    if current_key == "email" and "@" not in value:
        await message.answer("❌ Некорректный email. Попробуйте ещё раз:")
        return
    if current_key == "age" and not value.isdigit():
        await message.answer("❌ Возраст должен быть числом:")
        return
    if current_key in {"weight", "height", "puls_is_normal", "systolic", "diastolic"} and not value.isdigit():
        await message.answer("❌ Это поле должно быть числом:")
        return

    answers[current_key] = value

    if remaining_fields:
        next_field = remaining_fields.pop(0)
        await state.update_data(remaining_fields=remaining_fields, answers=answers, current_key=next_field["key"])
        await message.answer(next_field["prompt"])
        return

    payload = dict(answers)
    systolic = payload.pop("systolic")
    diastolic = payload.pop("diastolic")
    payload["pressure_is_normal"] = f"{systolic}/{diastolic}"
    payload["plan_type"] = "free"
    payload["age"] = int(payload["age"])

    await message.answer("🔄 Создаю аккаунт...")

    try:
        auth = await api_client.register(payload)
    except BackendAPIError as exc:
        await message.answer(f"❌ Ошибка регистрации: {exc}")
        await state.clear()
        return

    user = auth["user"]
    await save_user_session(
        telegram_id=message.from_user.id,
        token=auth["token"],
        email=str(user.get("email") or payload["email"]),
        created_at=user.get("created_at"),
        app_user_id=int(user["id"]),
    )
    await state.clear()
    await show_main_menu(message, user)
