from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings

# Для асинхронности SQLite не требует check_same_thread в большинстве случаев,
# но мы оставим логику для универсальности.
connect_args = {"check_same_thread": False} if str(settings.database_url).startswith("sqlite") else {}

# 1. Создаем асинхронный движок
engine = create_async_engine(
    str(settings.database_url),
    connect_args=connect_args,
    echo=True  # Включаем логи, чтобы видеть SQL-запросы в терминале
)

# 2. Используем async_sessionmaker (это замена старому sessionmaker)
# expire_on_commit=False критически важно для асинхронности
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# 3. Современный стиль объявления Base (SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass

# 4. Асинхронный генератор сессий для FastAPI
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

# 5. Асинхронная инициализация таблиц
async def init_db():
    async with engine.begin() as conn:
        # run_sync нужен, так как create_all — синхронный метод внутри метадаты
        await conn.run_sync(Base.metadata.create_all)