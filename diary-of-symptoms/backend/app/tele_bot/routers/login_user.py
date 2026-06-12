from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery 
from keyb.user import get_start_inline_keyboard
from keyb.Symptoms import get_main_reply_keyboard
from api_requests.user import login_user, API_URL
from db import save_user_session

router = Router()

url_login = f"{API_URL}/login"

class LoginStates(StatesGroup):
    waiting_for_email = State()     # Шаг 1: Ожидание почты
    waiting_for_password = State()  # Шаг 2: Ожидание пароля

@router.message(CommandStart())
async def start_cmd(message: Message):
    # ИСПРАВЛЕНО: Вызываем импортированную функцию клавиатуры
    await message.answer(
        "👋 Добро пожаловать! Зарегистрируйтесь или войдите в уже существующий аккаунт:", 
        reply_markup=get_start_inline_keyboard()
    )

# ИСПРАВЛЕНО: Так как кнопка называется "auth_login" (для Входа), 
# лучше ловить её callback_data, который ты настроил в клавиатуре
@router.callback_query(F.data == "auth_login")
async def login_start(callback: CallbackQuery, state: FSMContext):
    # Обязательно гасим часики на кнопке
    await callback.answer() 
    
    # ИСПРАВЛЕНО: Отправляем полноценное сообщение в чат через callback.message
    await callback.message.answer("📥 Пожалуйста, введите вашу электронную почту (email):")
    
    await state.set_state(LoginStates.waiting_for_email)

@router.message(LoginStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip() # .strip() убирает случайные пробелы по бокам

    # ИСПРАВЛЕНО: Добавлен return, чтобы прервать функцию при ошибке
    if '@' not in email:
        await message.answer("❌ Вы ввели неправильную почту. Попробуйте еще раз:")
        return # Бот останавливается и ждет от пользователя НОВЫЙ ввод в этот же стейт
    
    await state.update_data(user_email=email)

    await message.answer("🔑 Отлично, теперь введите ваш пароль:")
    await state.set_state(LoginStates.waiting_for_password)

@router.message(LoginStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip() # Очищаем от случайных пробелов

    user_data = await state.get_data()
    email = user_data.get("user_email")

    processing_msg = await message.answer("🔄 Проверяю данные на сервере...")

    payload = {
        "password": password,
        "email": email
    }

    # Делаем запрос к FastAPI бэкенду
    result = await login_user(url_login, payload)
    
    # ИСПРАВЛЕНО: Безопасная проверка через .get(), чтобы не поймать KeyError
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
        
        await processing_msg.delete()
        
        # Возвращаем универсальное главное меню (Reply-клавиатуру)
        await message.answer(
            "🎉 Авторизация прошла успешно! Вход выполнен.", 
            reply_markup=get_main_reply_keyboard()
        )
        await state.clear()  
        
    else:
        await processing_msg.delete()
        
        # Если бэкенд вернул ошибку в ключе 'message' или 'detail' — выводим её
        error_msg = result.get("message") or result.get("detail") or "Неверный email или пароль"
        
        await message.answer(
            f"❌ Ошибка авторизации: {error_msg}\n\n"
            f"Попробуйте ввести пароль заново:"
        )
        # Стейт остается прежним, ждем повторный ввод пароля
