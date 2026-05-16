from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .Medication import MedicationResponse

class UserBase(BaseModel):
    name: str = Field(..., description="Имя пользователя")
    email: EmailStr
    google_id: Optional[str] = None
    email_verified: Optional[bool] = False
    plan_type: Optional[str] = "free"
    weight: Optional[int] = None
    height: Optional[int] = None
    puls_is_normal: Optional[int] = None
    pressure_is_normal: Optional[str] = None


class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    puls_is_normal: Optional[int] = None
    pressure_is_normal: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserWithDetails(UserResponse):
    medications: List[MedicationResponse] = Field(default_factory=list)
