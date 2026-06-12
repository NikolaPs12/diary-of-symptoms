from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String
from db import get_user_token as _get_user_token, save_user_session as _save_user_session


class Base(DeclarativeBase):
    pass

# Твоя модель пользователя
class User(Base):
    __tablename__ = "bot_users"
    
    # Для Telegram ID обязательно используем BigInteger
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    auth_token: Mapped[str] = mapped_column(String, nullable=True)
    app_user_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)



async def get_user_token(telegram_id: int) -> str | None:
    """Получаем токен пользователя по его telegram_id."""
    return await _get_user_token(telegram_id)

async def save_user_token(telegram_id: int, token: str, email: str):
    """Сохраняем или обновляем токен пользователя."""
    await _save_user_session(telegram_id, token, email)
