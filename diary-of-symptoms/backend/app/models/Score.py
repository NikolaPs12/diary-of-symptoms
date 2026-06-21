from datetime import datetime
from sqlalchemy import ForeignKey, Integer, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .User import User

from app.services.database import Base

class HealthScores(Base):
    __tablename__ = "health_scores" 
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="health_scores")

    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 100", name="check_score_range"),
        UniqueConstraint("user_id", "calculated_at", name="uq_health_scores_user_day"),
    )
