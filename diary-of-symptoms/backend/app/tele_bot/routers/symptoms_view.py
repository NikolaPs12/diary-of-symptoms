from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from db import get_app_user_id, get_user_token
from keyb.Symptoms import get_period_keyboard
from api_requests.Symptoms import get_pdf_symptoms

router = Router()

class SymptomStates(StatesGroup):
    start_date = State()

@router.message(F.text == "📅 Посмотреть историю симптомов")
async def view_message_time(message: Message, state: FSMContext):
    # Отправляем инлайн-клавиатуру
    await message.answer("Выберите период или введите начальную дату вручную (ДД.ММ.ГГГГ):", reply_markup=get_period_keyboard())
    await state.set_state(SymptomStates.start_date)


# ХЭНДЛЕР А: Ловит нажатия на инлайн-кнопки (например, пресеты периодов)
# Ловим только те инлайн-кнопки, которые начинаются с "period:"
@router.callback_query(SymptomStates.start_date, F.data.startswith("period:"))
async def get_pdf_by_callback(callback: CallbackQuery, state: FSMContext):
    # Разрезаем строку по двоеточию. Из "period:2026-05-24" получим date_str = "2026-05-24"
    date_str = callback.data.split(":")[1]

    if date_str == "all":
        start_date = None
        end_date = None
    else:
        # Парсим дату из формата YYYY-MM-DD, который прилетел из кнопки
        start_date = datetime.strptime(date_str, "%Y-%m-%d")
        end_date = datetime.now().date()

    # Получаем данные пользователя и токен
    app_user_id = await get_app_user_id(callback.from_user.id)
    token = await get_user_token(callback.from_user.id)

    if app_user_id is None:
        await state.clear()
        await callback.message.answer("Не нашел ваш аккаунт. Пожалуйста, войдите заново через /start.")
        await callback.answer()
        return
    
    # Отправляем уже нормальный объект datetime/None в твою функцию
    pdf_bytes = await get_pdf_symptoms(token=token, 
                                 user_id=app_user_id, 
                                 start_date=start_date, 
                                 end_date=end_date)
    
    await state.clear()
    if pdf_bytes is None:
        await callback.message.answer(
            "❌ Не удалось сгенерировать отчет. Проверьте правильность URL или логи бэкенда."
        )
    else:
        # Уведомляем пользователя, что файл генерируется/отправляется
        await callback.message.answer("Генерирую ваш PDF-отчет, секунду...")

        # Упаковываем байты в объект файла aiogram
        document = BufferedInputFile(
            file=pdf_bytes, filename=f"symptoms_report_{end_date or 'all'}.pdf"
        )

        # Отправляем именно как ДОКУМЕНТ, а не текст
        await callback.message.answer_document(document=document)
    await callback.answer()  # Гасим часики на кнопке

# ХЭНДЛЕР Б: Ловит ручной ввод текста, если юзер проигнорировал кнопки и просто написал дату
@router.message(SymptomStates.start_date, F.text)
async def get_pdf_by_text(message: Message, state: FSMContext):
    try:
        start_date = datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        await message.answer("Неверный формат! Напиши дату в формате: ДД.ММ.ГГГГ (например, 31.05.2026)")
        return

    app_user_id = await get_app_user_id(message.from_user.id)
    token = await get_user_token(message.from_user.id)

    if app_user_id is None:
        await state.clear()
        await message.answer("Не нашел ваш аккаунт. Пожалуйста, войдите заново через /start.")
        return
    
    pdf = await get_pdf_symptoms(token=token, user_id=app_user_id, start_date=start_date)
    
    await state.clear()
    if pdf is None:
        await message.answer("❌ Не удалось сгенерировать отчет. Проверьте правильность URL или логи бэкенда.")
        return

    document = BufferedInputFile(file=pdf, filename=f"symptoms_report_{start_date.date()}.pdf")
    await message.answer_document(document=document)
