from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from api_requests.user import reg_user, API_URL
from db import save_user_session
from keyb.Symptoms import get_main_reply_keyboard

router = Router()

url_reg = f"{API_URL}/register"

class RegistrationStates(StatesGroup):
    waiting_for_field = State()  # Одно универсальное состояние для всех шагов

Registr_Fields = [
    {"key": "name", "prompt": "📝 Введите ваше имя пользователя:"},
    {"key": "email", "prompt": "📧 Введите ваш Email:"},
    {"key": "age", "prompt": "🔢 Сколько вам лет?"},
    {"key": "password", "prompt": "🔒 Придумайте надежный пароль:"},
    {"key": "weight", "prompt": "⚖️ Вес:"},
    {"key": "height", "prompt": "📏 Рост:"},
    {"key": "puls_is_normal", "prompt": "🫀 Пульс в норме?"},
    {"key": "systolic", "prompt": "🩺 Введите верхнее давление (например, 120):"},
    {"key": "diastolic", "prompt": "🩺 Теперь введите нижнее давление (например, 80):"}
]

@router.callback_query(F.data == "auth_register") # ИСПРАВЛЕНО: ловим кнопку регистрации, а не логина
async def registration_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    # ИСПРАВЛЕНО: делаем правильную копию списка без круглых скобок у Registr_Fields
    fields_copy = Registr_Fields.copy()
    
    # Сразу выдергиваем САМЫЙ ПЕРВЫЙ вопрос (Имя), чтобы задать его
    first_field = fields_copy.pop(0)

    # Сохраняем в FSM список, где имени уже НЕТ
    await state.set_data({
        "remaining_fields": fields_copy, 
        "answers": {},
        "current_key": first_field["key"] # Запоминаем, какой ключ мы СЕЙЧАС ждем от юзера
    })

    # Отправляем первый вопрос в чат
    await callback.message.answer(first_field["prompt"])
    await state.set_state(RegistrationStates.waiting_for_field)


@router.message(RegistrationStates.waiting_for_field)
async def reg_data(message: Message, state: FSMContext):
    data = await state.get_data()
    remaining_fields = data.get("remaining_fields")
    answers = data.get("answers")         # ИСПРАВЛЕНО: добавлена буква "s" (answers)
    current_key = data.get("current_key") # Узнаем, на какой вопрос отвечает пользователь

    user_input = message.text.strip()

    # --- Валидация данных ---
    if current_key == "email" and "@" not in user_input:
        await message.answer("❌ Некорректный email. Попробуйте еще раз:")
        return # Останавливаемся, стейт и списки не меняем
        
    if current_key == "age" and not user_input.isdigit():
        await message.answer("❌ Возраст должен быть числом. Введите заново:")
        return

    if current_key in {"weight", "height", "puls_is_normal", "systolic", "diastolic"} and not user_input.isdigit():
        await message.answer("❌ Это поле должно быть числом. Введите заново:")
        return

    # Записываем валидный ответ в наш мешок ответов
    answers[current_key] = user_input
    
    # --- Проверяем, есть ли следующий вопрос ---
    if remaining_fields:
        # Достаем следующий вопрос и УДАЛЯЕМ его из списка оставшихся
        next_field = remaining_fields.pop(0)
        
        # Обновляем состояние памяти
        await state.update_data(
            remaining_fields=remaining_fields, 
            answers=answers,
            current_key=next_field["key"] # Теперь ждем этот ключ
        )
        
        # Задаем следующий вопрос
        await message.answer(next_field["prompt"])
    
    # --- Если вопросов больше нет — отправляем на сервер ---
# --- Если вопросов больше нет — отправляем на сервер ---
    else:
        processing_msg = await message.answer("🔄 Все данные собраны. Регистрирую вас на сервере...")

        # 1. Создаем глубокую копию, чтобы не испортить оригинальный answers
        api_payload = answers.copy()
        
        # 2. Формируем давление из копии и удаляем старые ключи ТОЛЬКО из копии
        systolic = api_payload.pop('systolic')
        diastolic = api_payload.pop('diastolic')
        api_payload["pressure_is_normal"] = f"{systolic}/{diastolic}"
        api_payload["plan_type"] = "free"
        
        # 3. Передаем безопасный словарь в твою функцию запроса к FastAPI
        result = await reg_user(url_reg, api_payload) 
        
        await processing_msg.delete() # Удаляем промежуточный текст
        
        if result.get("status") == "success":
            token = result.get("token")
            
            # Вытаскиваем данные из вложенного словаря 'user'
            user_data = result.get("user", {})
            
            app_user_id = user_data.get("id")
            create_at = user_data.get("created_at")  # Достали без проблем!
            email = user_data.get("email")

            await save_user_session(
                telegram_id=message.from_user.id, 
                token=token, 
                email=email,
                app_user_id=app_user_id,
                created_at=create_at
            )
            await message.answer("🎉 Регистрация прошла успешно! Вы авторизованы.", reply_markup=get_main_reply_keyboard())
            await state.clear()  # Полностью очищаем стейт-машину
        else:
            await message.answer(f"❌ Ошибка при регистрации: {result.get('message', 'Неизвестная ошибка')}\n\nПопробуйте пройти регистрацию заново через /start.")
            await state.clear()
