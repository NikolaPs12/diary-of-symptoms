from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .Medication import Medication
    from .SymptomEntry import SymptomEntry

from app.services.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    google_id: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)

    email_verified: Mapped[Boolean] = mapped_column(Boolean, default=False)
    plan_type: Mapped[str] = mapped_column(String, default="free") # план подписки пользователя, например, "free", "premium" и т.д.

    weight: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    puls_is_normal: Mapped[int] = mapped_column(Integer)
    pressure_is_normal: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    
    medications: Mapped[List["Medication"]] = relationship("Medication", back_populates="user")
    symptom_entries: Mapped[List["SymptomEntry"]] = relationship("SymptomEntry", back_populates="user")
