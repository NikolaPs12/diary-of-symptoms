from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

class MedicationBase(BaseModel):
    name: str
    dosage: str
    regular_medications: List[str] = Field(default_factory=list)
    diagnosis: Optional[str] = None
    allergies: List[str] = Field(default_factory=list)

class MedicationCreate(MedicationBase):
    notes: Optional[str] = None
    user_id: Optional[int] = None

class MedicationResponse(MedicationBase):
    id: int
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
