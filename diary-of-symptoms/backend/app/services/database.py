from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings

database_url = str(settings.database_url)

if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif database_url.startswith("postgresql+asyncpg"):
    connect_args = {"timeout": 5}
else:
    connect_args = {}

engine = create_async_engine(
    database_url,
    connect_args=connect_args,
    echo=settings.debug,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Existing PostgreSQL tables are not altered by create_all,
        # so we add the age column explicitly for older deployments.
        if database_url.startswith("postgresql"):
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS age INTEGER"))
            await conn.execute(text("ALTER TABLE reminders ADD COLUMN IF NOT EXISTS cron_expr VARCHAR"))
            await conn.execute(text("ALTER TABLE reminders ADD COLUMN IF NOT EXISTS telegram_chat_id BIGINT"))
            await conn.execute(text("ALTER TABLE reminders ALTER COLUMN last_send_at DROP NOT NULL"))
            await conn.execute(text("ALTER TABLE reminders ALTER COLUMN enable SET DEFAULT true"))
