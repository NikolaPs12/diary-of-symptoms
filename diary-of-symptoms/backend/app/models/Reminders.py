from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .User import User

from app.services.database import Base

class Reminders(Base):
    __tablename__ = "reminders" 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    cron_expr: Mapped[str] = mapped_column(String)
    send_telegram: Mapped[bool] = mapped_column(Boolean, default=False)
    telegram_chat_id: Mapped[int | None] = mapped_column(nullable=True, default=None)
    send_email: Mapped[bool] = mapped_column(Boolean, default=False)
    enable: Mapped[bool] = mapped_column(Boolean, default=True)
    last_send_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    next_send_at: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="reminders")
