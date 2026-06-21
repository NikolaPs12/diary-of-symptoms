import asyncio
import os 
import email.message
from datetime import datetime, timezone

from croniter import croniter
from sqlalchemy import text
from aiogram import Bot
import aiosmtplib  

# Твоя фабрика сессий
from database import SessionLocal

# Настройка ТГ Бота
BOT_TOKEN = os.getenv("TOKEN")
bot = Bot(token=BOT_TOKEN)

async def send_telegram_notification(chat_id: int, text: str):
    """Функция берет ID пользователя и отправляет ему текст"""
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        print(f"Сообщение успешно отправлено в ТГ для {chat_id}")
    except Exception as e:
        print(f"Не удалось отправить сообщение в ТГ: {e}")

async def send_email(to_email: str, text: str):
    """Функция отправки письма через SMTP"""
    SMTP_SERVER = "smtp.mail.ru"
    SMTP_PORT = 465
    SENDER_EMAIL = "your_bot_email@mail.ru"    # Укажи свою почту робота
    SENDER_PASSWORD = "your_app_password"     # Укажи пароль приложения

    msg = email.message.EmailMessage()
    msg["Subject"] = "Напоминание!"           
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.set_content(text)                     

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD,
            use_tls=True  
        )
        print(f"Письмо успешно улетело на {to_email}")
    except Exception as e:
        print(f"Ошибка при отправке почты: {e}")


async def reminder_loop():  # Убрали db_factory, так как SessionLocal импортирован выше
    print("Воркер уведомлений успешно запущен...")
    
    while True:
        now = datetime.now(timezone.utc)
        
        async with SessionLocal() as session:
            # 1. ОБЕРНУЛИ в text() — теперь база поймет запрос
            sql_select = text("SELECT id, user_id, message, send_telegram, send_email, cron_expr FROM reminders WHERE next_send_at <= :now AND enable = true;")

            result = await session.execute(sql_select, {"now": now})
            active_reminders = result.all()
            
            for reminder in active_reminders:
                # Отправка в Telegram
                if reminder.send_telegram:
                    # В базе user_id должен быть числом (Telegram ID)
                    await send_telegram_notification(chat_id=int(reminder.user_id), text=reminder.message)
                    
                # Отправка на Email
                if reminder.send_email:
                    # Поправили аргумент с to= на to_email=
                    await send_email(to_email=reminder.user_id, text=reminder.message)
                
                # 2. РАССЧИТЫВАЕМ новое время через croniter
                cron = croniter(reminder.cron_expr, now)
                next_send_at = cron.get_next(datetime)
                
                # 3. ОТПРАВЛЯЕМ UPDATE запрос в БД, чтобы обновить время на будущее
                sql_update = text("""
                    UPDATE reminders 
                    SET next_send_at = :next_time 
                    WHERE id = :reminder_id
                """)
                await session.execute(sql_update, {"next_time": next_send_at, "reminder_id": reminder.id})
            
            # Сохраняем все UPDATE в базе данных за этот проход цикла
            await session.commit()
            
        # Спим ровно минуту вне блока async with, чтобы не держать соединение открытым
        await asyncio.sleep(60)