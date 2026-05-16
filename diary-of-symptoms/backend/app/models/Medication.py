from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .User import User

from app.services.database import Base

class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String, index=True)  
    dosage: Mapped[str | None] = mapped_column(String)

    regular_medications: Mapped[list | None] = mapped_column(JSON, default=list)
    allergies: Mapped[list | None] = mapped_column(JSON, default=list)

    diagnosis: Mapped[str | None] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates="medications")