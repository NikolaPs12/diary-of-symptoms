from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class HealthScoresBase(BaseModel):
    score: int = Field(ge=1, le=100)

class HealthScoresResponse(HealthScoresBase):
    id: int
    user_id: int
    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
