from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class SymptomBase(BaseModel):
    symptom: str
    severity: int = Field(..., ge=0, le=10)
    duration: str
    sleep_quality: int = Field(..., ge=0, le=10)
    sleep_hours: float = Field(..., ge=0, le=24)
    stress_level: int = Field(..., ge=0, le=10)

class SymptomEntryCreate(SymptomBase):
    user_id: Optional[int] = None
    start_at: Optional[datetime] = None
    body_state: Optional[str] = None
    notes: Optional[str] = None
    food_notes: Optional[str] = None
    medications_taken: Optional[str] = None

class SymptomEntryResponse(SymptomBase):
    id: int
    start_at: datetime
    body_state: Optional[str] = None
    notes: Optional[str] = None
    food_notes: Optional[str] = None
    medications_taken: Optional[str] = None
    ai_insights: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
