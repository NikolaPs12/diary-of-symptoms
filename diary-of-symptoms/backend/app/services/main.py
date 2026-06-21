import os
import asyncio
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.routers.Generation import router as generation_router
from app.routers.Medication import router as medication_router
from app.routers.Reminders import router as reminders_router
from app.routers.Score import router as score_router
from app.routers.SymptomEntry import router as symptom_entry_router
from app.routers.User import router as user_router
from app.services.config import settings
from app.services.database import init_db, SessionLocal  # Импортируем SessionLocal
from app.services.reminders import reminder_loop

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Сначала инициализируем базу данных (создаем таблицы, если их нет)
    await init_db()
    
    print("=== Запуск фонового воркера уведомлений ===")
    # 2. АКТИВИРУЕМ ВОРКЕРА на заднем плане, передавая ему фабрику сессий
    worker_task = asyncio.create_task(reminder_loop(session_factory=SessionLocal))
    
    yield  # Здесь приложение запускается и готово принимать запросы от пользователей
    
    print("=== Остановка фонового воркера ===")
    # 3. Когда сервер тушится, аккуратно закрываем воркер
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Simple request-logging middleware for debugging incoming requests and bodies.
logger = logging.getLogger("uvicorn.error")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            body_bytes = await request.body()
        except Exception:
            body_bytes = b""

        try:
            body_text = body_bytes.decode("utf-8")
        except Exception:
            body_text = str(body_bytes)

        logger.info("Incoming request: %s %s headers=%s body=%s", request.method, request.url.path, dict(request.headers), body_text[:2000])

        # Recreate receive so downstream handlers can read the body again
        async def receive() -> dict:
            return {"type": "http.request", "body": body_bytes}

        request._receive = receive
        response = await call_next(request)
        return response


app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if isinstance(settings.cors_origins, list) else [settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(symptom_entry_router)
app.include_router(medication_router)
app.include_router(generation_router)
app.include_router(score_router)
app.include_router(reminders_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.services.main:app", host="127.0.0.1", port=int(os.getenv("PORT") or 8000), reload=True)
