import sys
import os
import asyncio # Добавляем для запуска цикла
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine

from alembic import context

# 1. Настройка путей (оставляем как есть, это важно)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Импорты моделей и базы
from app.models.User import User
from app.models.SymptomEntry import SymptomEntry
from app.models.Medication import Medication
from app.models.Score import HealthScores
from app.services.database import engine, Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Вспомогательная функция для запуска миграций внутри синхронного контекста."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме (асинхронно)."""
    
    # Мы используем твой асинхронный движок напрямую
    connectable = engine

    async with connectable.connect() as connection:
        # Так как Alembic внутри себя синхронный, 
        # мы используем run_sync для запуска миграций
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    # Запускаем асинхронную функцию через asyncio
    asyncio.run(run_migrations_online())
