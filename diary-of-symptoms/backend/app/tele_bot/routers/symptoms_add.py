from aiogram import Router, F
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from api_requests.Symptoms import add_symptom 
from db import get_app_user_id, get_user_token
from keyb.Symptoms import get_cancel_inline

router = Router()

class SymptomStates(StatesGroup):
    waiting_for_field = State()  # Универсальное состояние для шагов опроса

Symptoms_Fields = [
    {
        "key": "symptom", 
        "prompt": "🤕 Основной симптом:\nОпишите кратко, что именно болит или беспокоит (например: головная боль, тошнота, боль в мышцах):"
    },
    {
        "key": "body_state", 
        "prompt": "🧘 Как вы себя чувствуете?\nОпишите ваше общее состояние, уровень энергии, дискомфорт, настроение или любые важные детали:"
    },
    {
        "key": "start_at", 
        "prompt": "🕒 Когда это началось?\nВведите дату и время (например, в формате ДД.ММ.ГГГГ ЧЧ:ММ) или напишите 'сейчас':"
    },
    {
        "key": "duration", 
        "prompt": "⏳ Длительность симптома:\nСколько это продолжается? (например: 2 часа, 30 минут, весь день):"
    },
    {
        "key": "sleep_hours", 
        "prompt": "😴 Продолжительность сна:\nСколько часов вы спали в последние сутки? (можно дробным, например: 7 или 7.5):"
    },
    {
        "key": "severity", 
        "prompt": "📊 Интенсивность симптома:\nОцените силу недомогания по шкале от 0 до 10 (где 0 — вообще не болит, 10 — невыносимая боль):"
    },
    {
        "key": "stress_level", 
        "prompt": "🤯 Уровень стресса:\nОцените ваш уровень стресса за сегодня по шкале от 0 до 10:"
    },
    {
        "key": "sleep_quality", 
        "prompt": "💤 Качество сна:\nОцените, насколько хорошо вы выспались, по шкале от 0 до 10:"
    },
    {
        "key": "food_notes", 
        "prompt": "🍏 Что вы сегодня ели/пили?\nОпишите приемы пищи, питьевой режим, пили ли кофе, энергетики или сладкое:"
    },
    {
        "key": "medications_taken", 
        "prompt": "💊 Принимали ли вы лекарства?\nУкажите название и дозировку (например: Ибупрофен 400 мг, Магний B6) или напишите 'нет':"
    },
    {
        "key": "notes", 
        "prompt": "📝 Дополнительные заметки:\nЧто произошло за день, что изменилось или показалось вам необычным сегодня?"
    }
]

@router.message(F.text == "📝 Добавить симптомы")
async def symptom_add(message: Message, state: FSMContext):

    
    symptom_copy = Symptoms_Fields.copy()
    first_field = symptom_copy.pop(0)

    await state.set_data({
        "remaining_fields": symptom_copy, 
        "answers": {},
        "current_key": first_field["key"]
    })


    # И добавили кнопку "Отмена", о которой говорили ранее
    await message.answer(first_field["prompt"], reply_markup=get_cancel_inline())
    await state.set_state(SymptomStates.waiting_for_field)

@router.message(SymptomStates.waiting_for_field)
async def process_symptom_field(message: Message, state: FSMContext):
    user_input = message.text.strip()
    
    # Получаем текущие данные из FSM
    data = await state.get_data()
    current_key = data.get("current_key")
    answers = data.get("answers", {})
    remaining_fields = data.get("remaining_fields", [])

    # =================================================================
    #  БЛОК ВАЛИДАЦИИ И ПРИВЕДЕНИЯ ТИПОВ ПОД СХЕМУ PYDANTIC
    # =================================================================
    
    # 1. Валидация целых чисел со шкалой от 0 до 10
    if current_key in ["severity", "sleep_quality", "stress_level"]:
        if not user_input.isdigit() or not (0 <= int(user_input) <= 10):
            await message.answer(
                "❌ **Ошибка ввода!**\nПожалуйста, введите только целое число от **0 до 10**:",
                reply_markup=get_cancel_inline()
            )
            return # Прерываем выполнение, бот ждет повторного ввода на этом же шаге
        user_input = int(user_input) # Приводим к int

    # 2. Валидация часов сна (число с плавающей точкой)
    elif current_key == "sleep_hours":
        try:
            # Заменяем запятую на точку на случай ввода "7,5"
            hours = float(user_input.replace(",", "."))
            if not (0.0 <= hours <= 24.0):
                raise ValueError
            user_input = hours # Приводим к float
        except ValueError:
            await message.answer(
                "❌ **Ошибка ввода!**\nВведите корректное количество часов сна цифрами (например, `7` или `7.5`) в диапазоне от **0 до 24**:",
                reply_markup=get_cancel_inline()
            )
            return

    # 3. Валидация даты и времени (самое коварное место!)
    elif current_key == "start_at":
        if user_input.lower() in ["сейчас", "now", "today", "сегодня"]:
            # Превращаем в ISO-строку, которую Pydantic на бэкенде гарантированно распарсит в datetime
            user_input = datetime.now().isoformat()
        else:
            # Пытаемся распарсить ручной ввод пользователя (ожидаем формат ДД.ММ.ГГГГ ЧЧ:ММ)
            # Например: 24.05.2026 14:30
            try:
                parsed_date = datetime.strptime(user_input, "%d.%m.%Y %H:%M")
                user_input = parsed_date.isoformat()
            except ValueError:
                await message.answer(
                    "❌ **Неверный формат даты!**\n"
                    "Напишите слово **сейчас** или введите дату и время строго в формате:\n"
                    "`ДД.ММ.ГГГГ ЧЧ:ММ` (например: `24.05.2026 11:15`):",
                    reply_markup=get_cancel_inline()
                )
                return

    # =================================================================
    #  ЗАПИСЬ РЕЗУЛЬТАТА И ПЕРЕХОД К СЛЕДУЮЩЕМУ ВОПРОСУ
    # =================================================================
    
    # Сохраняем уже валидированное и приведенное к нужному типу значение
    answers[current_key] = user_input

    # Если еще остались вопросы в списке
    if remaining_fields:
        next_field = remaining_fields.pop(0)
        
        # Обновляем стейт: перезаписываем answers и уменьшенный список полей
        await state.update_data(
            remaining_fields=remaining_fields,
            answers=answers,
            current_key=next_field["key"]
        )
        
        # Задаем следующий вопрос
        await message.answer(next_field["prompt"], reply_markup=get_cancel_inline())
    
    # Если это был последний вопрос — отправляем данные на бэкенд
    else:
        # Индикатор отправки
        processing_msg = await message.answer("🔄 Анализирую симптомы с помощью ИИ и сохраняю запись...")
        
        # Получаем токен из твоей локальной БД (мы чинили эту функцию в db.py)
        token = await get_user_token(message.from_user.id)
        app_user_id = await get_app_user_id(message.from_user.id)

        if not app_user_id:
            await processing_msg.delete()
            await message.answer(
                "❌ Не удалось определить ваш аккаунт приложения. Войдите в бота заново через /start."
            )
            await state.clear()
            return

        answers["user_id"] = app_user_id
        
        # Отправляем готовый чистый словарь на бэкенд
        result = await add_symptom(payload=answers, token=token)
        
        await processing_msg.delete()
        
        if result.get("status") == "success":
            ai_text = result.get("ai_insights", "Анализ ИИ временно недоступен.")
            
            # Собираем красивый аккуратный ответ в одну плашку
            response_text = (
                f"🤖 **Анализ ИИ:**\n{ai_text}\n\n"
                f"-----------------------------------------\n"
                f"🎉 Запись успешно добавлена в Дневник симптомов!"
            )
            await message.answer(response_text)
            await state.clear() # Полностью очищаем FSM
        else:
            # Если вдруг бэкенд все равно выдаст ошибку, мы ее увидим
            error_detail = result.get("detail") or result.get("message") or "Неизвестная ошибка"
            await message.answer(
                f"❌ Ошибка при сохранении на сервере:\n`{error_detail}`\n\n"
                f"Попробуйте запустить процесс заново."
            )
            await state.clear()

@router.callback_query(F.data == "cancel_fsm")
async def cancel_fsm_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Заполнение отменено")
    await state.clear() # Полностью сбрасываем FSM
    
    # Меняем текст сообщения, под которым была кнопка, чтобы интерфейс остался чистым
    await callback.message.edit_text("❌ Заполнение дневника прервано. Данные не сохранились.")            
