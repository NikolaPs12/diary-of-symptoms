import asyncio
import email.message
import logging
import os
from datetime import datetime
from typing import Any

from aiogram import Bot
from croniter import croniter
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

try:
    import aiosmtplib
except ImportError:  # Email delivery is optional; Telegram reminders must still work.
    aiosmtplib = None

from app.models.Reminders import Reminders
from app.services.database import SessionLocal


logger = logging.getLogger(__name__)

WEEKDAY_TO_CRON = {
    "sun": "0",
    "mon": "1",
    "tue": "2",
    "wed": "3",
    "thu": "4",
    "fri": "5",
    "sat": "6",
}
CRON_TO_WEEKDAY = {value: key for key, value in WEEKDAY_TO_CRON.items()}
RU_WEEKDAY_ALIASES = {
    "вс": "sun",
    "пн": "mon",
    "вт": "tue",
    "ср": "wed",
    "чт": "thu",
    "пт": "fri",
    "сб": "sat",
}
WRITABLE_FIELDS = {
    "type",
    "title",
    "message",
    "cron_expr",
    "send_telegram",
    "telegram_chat_id",
    "send_email",
    "enable",
    "user_id",
}


def _utc_now_naive() -> datetime:
    return datetime.utcnow()


def _normalize_weekdays(weekdays: list[str] | None) -> list[str]:
    if not weekdays:
        return []

    normalized: list[str] = []
    for value in weekdays:
        key = str(value).strip().lower()
        key = RU_WEEKDAY_ALIASES.get(key, key)
        if key not in WEEKDAY_TO_CRON:
            raise ValueError("weekdays must contain mon, tue, wed, thu, fri, sat, sun")
        if key not in normalized:
            normalized.append(key)
    return normalized


def build_cron_expr(send_time: str, weekdays: list[str] | None = None) -> str:
    try:
        hour_text, minute_text = send_time.strip().split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
    except Exception as exc:
        raise ValueError("send_time must use HH:MM format") from exc

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("send_time must be a valid 24-hour time")

    normalized_weekdays = _normalize_weekdays(weekdays)
    day_part = ",".join(WEEKDAY_TO_CRON[item] for item in normalized_weekdays) or "*"
    return f"{minute} {hour} * * {day_part}"


def parse_cron_metadata(cron_expr: str) -> tuple[str | None, list[str]]:
    parts = cron_expr.split()
    if len(parts) != 5:
        return None, []

    minute, hour, _, _, days = parts
    if not minute.isdigit() or not hour.isdigit():
        return None, []

    send_time = f"{int(hour):02d}:{int(minute):02d}"
    if days == "*":
        return send_time, []

    weekdays = [
        CRON_TO_WEEKDAY[item]
        for item in days.split(",")
        if item in CRON_TO_WEEKDAY
    ]
    return send_time, weekdays


def calculate_next_send_at(cron_expr: str, base_time: datetime | None = None) -> datetime:
    if not croniter.is_valid(cron_expr):
        raise ValueError("Invalid cron_expr")
    return croniter(cron_expr, base_time or _utc_now_naive()).get_next(datetime)


def _prepare_payload(payload: dict[str, Any], current: Reminders | None = None) -> dict[str, Any]:
    data = dict(payload)
    send_time = data.pop("send_time", None)
    weekdays = data.pop("weekdays", None)

    if send_time is not None or weekdays is not None:
        current_time, current_weekdays = parse_cron_metadata(current.cron_expr) if current else (None, [])
        data["cron_expr"] = build_cron_expr(
            send_time or current_time or "09:00",
            weekdays if weekdays is not None else current_weekdays,
        )

    if not data.get("cron_expr"):
        raise ValueError("Provide cron_expr or send_time")

    data["next_send_at"] = calculate_next_send_at(data["cron_expr"])
    return {key: value for key, value in data.items() if key in WRITABLE_FIELDS or key == "next_send_at"}


def serialize_reminder(reminder: Reminders) -> dict[str, Any]:
    send_time, weekdays = parse_cron_metadata(reminder.cron_expr)
    return {
        "id": reminder.id,
        "user_id": reminder.user_id,
        "type": reminder.type,
        "title": reminder.title,
        "message": reminder.message,
        "cron_expr": reminder.cron_expr,
        "send_time": send_time,
        "weekdays": weekdays,
        "send_telegram": reminder.send_telegram,
        "telegram_chat_id": reminder.telegram_chat_id,
        "send_email": reminder.send_email,
        "enable": reminder.enable,
        "last_send_at": reminder.last_send_at,
        "next_send_at": reminder.next_send_at,
    }


async def create_reminder(db: AsyncSession, payload: dict[str, Any]) -> Reminders:
    data = _prepare_payload(payload)
    reminder = Reminders(**data)
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def list_reminders(db: AsyncSession, user_id: int | None = None) -> list[Reminders]:
    query = select(Reminders).order_by(Reminders.next_send_at.asc())
    if user_id is not None:
        query = query.where(Reminders.user_id == user_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_reminder(db: AsyncSession, reminder_id: int, user_id: int | None = None) -> Reminders | None:
    query = select(Reminders).where(Reminders.id == reminder_id)
    if user_id is not None:
        query = query.where(Reminders.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_reminder(db: AsyncSession, reminder: Reminders, payload: dict[str, Any]) -> Reminders:
    data = _prepare_payload(payload, current=reminder) if any(
        key in payload for key in {"cron_expr", "send_time", "weekdays"}
    ) else {key: value for key, value in payload.items() if key in WRITABLE_FIELDS}

    for key, value in data.items():
        setattr(reminder, key, value)

    await db.commit()
    await db.refresh(reminder)
    return reminder


async def set_reminder_enabled(db: AsyncSession, reminder: Reminders, enabled: bool) -> Reminders:
    reminder.enable = enabled
    if enabled and reminder.next_send_at <= _utc_now_naive():
        reminder.next_send_at = calculate_next_send_at(reminder.cron_expr)
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def delete_reminder(db: AsyncSession, reminder: Reminders) -> None:
    await db.delete(reminder)
    await db.commit()


async def send_telegram_notification(chat_id: int, text: str, bot: Bot | None = None) -> None:
    token = os.getenv("TOKEN")
    if bot is None and not token:
        logger.warning("TOKEN is not configured, Telegram reminder skipped for chat_id=%s", chat_id)
        return

    local_bot = bot or Bot(token=token)
    close_after_send = bot is None
    try:
        await local_bot.send_message(chat_id=chat_id, text=text)
        logger.info("Telegram reminder sent to %s", chat_id)
    except Exception:
        logger.exception("Telegram reminder delivery failed for %s", chat_id)
    finally:
        if close_after_send:
            await local_bot.session.close()


async def send_email(to_email: str, text: str) -> None:
    if aiosmtplib is None:
        logger.warning("aiosmtplib is not installed, email reminder skipped for %s", to_email)
        return

    smtp_server = os.getenv("REMINDER_SMTP_SERVER", "smtp.mail.ru")
    smtp_port = int(os.getenv("REMINDER_SMTP_PORT", "465"))
    sender_email = os.getenv("REMINDER_EMAIL")
    sender_password = os.getenv("REMINDER_EMAIL_PASSWORD")
    if not sender_email or not sender_password:
        logger.warning("Email reminder credentials are not configured, skipped for %s", to_email)
        return

    msg = email.message.EmailMessage()
    msg["Subject"] = "Напоминание"
    msg["From"] = sender_email
    msg["To"] = to_email
    msg.set_content(text)

    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_server,
            port=smtp_port,
            username=sender_email,
            password=sender_password,
            use_tls=True,
        )
        logger.info("Email reminder sent to %s", to_email)
    except Exception:
        logger.exception("Email reminder delivery failed for %s", to_email)


async def _process_due_reminders(session: AsyncSession, bot: Bot | None = None) -> None:
    now = _utc_now_naive()
    result = await session.execute(
        select(Reminders)
        .options(selectinload(Reminders.user))
        .where(Reminders.enable.is_(True), Reminders.next_send_at <= now)
    )
    reminders = list(result.scalars().all())

    for reminder in reminders:
        if reminder.send_telegram and reminder.telegram_chat_id:
            await send_telegram_notification(chat_id=int(reminder.telegram_chat_id), text=reminder.message, bot=bot)
        elif reminder.send_telegram:
            logger.warning("Telegram reminder %s skipped: telegram_chat_id is not set", reminder.id)

        if reminder.send_email:
            user_email = reminder.user.email if getattr(reminder, "user", None) else None
            if user_email:
                await send_email(to_email=str(user_email), text=reminder.message)
            else:
                logger.warning("Email reminder %s skipped: user email is not available", reminder.id)

        reminder.last_send_at = now
        reminder.next_send_at = calculate_next_send_at(reminder.cron_expr, now)

    if reminders:
        await session.commit()


async def reminder_loop(
    session_factory: async_sessionmaker[AsyncSession] = SessionLocal,
    poll_interval: int = 60,
) -> None:
    logger.info("Reminder worker started")
    token = os.getenv("TOKEN")
    bot = Bot(token=token) if token else None

    try:
        while True:
            try:
                async with session_factory() as session:
                    await _process_due_reminders(session, bot=bot)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Reminder worker iteration failed")

            await asyncio.sleep(poll_interval)
    finally:
        if bot is not None:
            await bot.session.close()
        logger.info("Reminder worker stopped")
