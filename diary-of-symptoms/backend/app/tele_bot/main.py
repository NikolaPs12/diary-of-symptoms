from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from api_client.client import api_client
from handlers import auth_router, menu_router, notifications_router, profile_router, report_router, symptoms_router
from services.config import settings
from services.session_store import init_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


async def main() -> None:
    if not settings.token:
        raise RuntimeError("TOKEN is not configured")

    await init_db()
    await api_client.start()

    bot = Bot(
        token=settings.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(menu_router)
    dp.include_router(auth_router)
    dp.include_router(profile_router)
    dp.include_router(notifications_router)
    dp.include_router(report_router)
    dp.include_router(symptoms_router)

    try:
        await dp.start_polling(bot)
    finally:
        await api_client.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
