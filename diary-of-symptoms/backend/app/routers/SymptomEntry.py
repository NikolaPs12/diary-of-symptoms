import os
import sqlalchemy
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.SymptomEntry import SymptomEntry
from app.schema.SymptomEntry import SymptomEntryCreate, SymptomEntryResponse
from app.services.function import build_ai_insight
from app.services.database import get_db
from app.services.scoring import update_daily_health_score
from dotenv import load_dotenv


router = APIRouter(
    prefix="/api/symptom-entries",
    tags=["symptom-entries"]
)


load_dotenv()


def to_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)

@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=SymptomEntryResponse)
async def create_symptom_entry(
    symptom_entry: SymptomEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    # Вызываем ИИ-анализ
    ai_insights = build_ai_insight(symptom_entry)
    
    entry_data = symptom_entry.model_dump()
    entry_data["ai_insights"] = ai_insights
    
    # Достаем user_id, который пришел от фронтенда в JSON
    user_id = entry_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required in body")
    
    current_utc_time = datetime.now(timezone.utc)
    current_db_time = to_naive_utc(current_utc_time)
    
    if entry_data.get("start_at") is None:
        entry_data["start_at"] = current_db_time
    else:
        entry_data["start_at"] = to_naive_utc(entry_data["start_at"])

    db_entry = SymptomEntry(**entry_data)
    db.add(db_entry)
    
    # Сначала сохраняем запись в БД
    await db.commit()
    await db.refresh(db_entry)
    
    await update_daily_health_score(
        db=db,
        user_id=user_id,
        event_timestamp=db_entry.start_at,
    )
    
    return db_entry

@router.get("/{entry_id}", response_model=SymptomEntryResponse)
async def get_symptom_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    db_entry = await db.get(SymptomEntry, entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Symptom entry not found")
    return db_entry

@router.get("", response_model=list[SymptomEntryResponse])
async def list_symptom_entries(
    user_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    query = sqlalchemy.select(SymptomEntry).order_by(SymptomEntry.created_at.desc())
    if user_id is not None:
        query = query.where(SymptomEntry.user_id == user_id)

    result = await db.execute(query)
    return list(result.scalars().all())
