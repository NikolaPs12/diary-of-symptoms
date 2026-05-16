import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Импортируем твои роутеры
from app.routers.Medication import router as medication_router
from app.routers.SymptomEntry import router as symptom_entry_router
from app.routers.User import router as user_router

# Импортируем настройки и асинхронную инициализацию
from app.services.config import settings
from app.services.database import init_db 
from dotenv import load_dotenv

load_dotenv

# 1. Используем Lifespan вместо старого on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Проверка и создание таблиц (асинхронно)...")
    try:
        # ВЫЗЫВАЕМ ТВОЮ АСИНХРОННУЮ ФУНКЦИЮ ИЗ database.py
        await init_db() 
        print("Таблицы успешно проверены/созданы!")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# 2. CORS (оставляем как было)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if isinstance(settings.cors_origins, list) else [settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Подключаем роутеры
app.include_router(user_router)
app.include_router(symptom_entry_router)
app.include_router(medication_router)

port = os.getenv("PORT")

if __name__ == "__main__":
    # Запускаем сразу uvicorn, таблицы создадутся внутри lifespan
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)