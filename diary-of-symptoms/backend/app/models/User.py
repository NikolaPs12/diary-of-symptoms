from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .Score import HealthScores
    from .Medication import Medication
    from .SymptomEntry import SymptomEntry
    from .Reminders import Reminders

from app.services.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    google_id: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True, default=None)

    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    plan_type: Mapped[str] = mapped_column(String, default="free")

    weight: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    puls_is_normal: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    pressure_is_normal: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    
    medications: Mapped[List["Medication"]] = relationship("Medication", back_populates="user")
    symptom_entries: Mapped[List["SymptomEntry"]] = relationship("SymptomEntry", back_populates="user")
    health_scores: Mapped[List["HealthScores"]] = relationship("HealthScores", back_populates="user")
    reminders: Mapped[List["Reminders"]] = relationship("Reminders")