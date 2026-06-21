from datetime import datetime
from sqlalchemy import ForeignKey, Integer, CheckConstraint, UniqueConstraint, String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
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
    corn_expr: Mapped[str] = mapped_column(String)
    send_telegram: Mapped[bool] = mapped_column(Boolean, default=False)
    send_email: Mapped[bool] = mapped_column(Boolean, default=False)
    enable: Mapped[bool] = mapped_column(Boolean, default=False)
    last_send_at: Mapped[datetime] = mapped_column(DateTime)
    next_send_at: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="health_scores")