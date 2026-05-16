from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .User import User

from app.services.database import Base

class SymptomEntry(Base):
    __tablename__ = "symptom_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    start_at: Mapped[datetime] = mapped_column(default=func.now())

    symptom: Mapped[str | None] = mapped_column(String)
    severity: Mapped[int] = mapped_column(Integer)
    duration: Mapped[str | None] = mapped_column(String)
    body_state: Mapped[str | None] = mapped_column(String)

    notes: Mapped[str | None] = mapped_column(String)

    sleep_quality: Mapped[int] = mapped_column(Integer)
    sleep_hours: Mapped[float] = mapped_column(Float)
    stress_level: Mapped[int] = mapped_column(Integer)
    food_notes: Mapped[str | None] = mapped_column(String)
    medications_taken: Mapped[str | None] = mapped_column(String)

    ai_insights: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates= "symptom_entries")
