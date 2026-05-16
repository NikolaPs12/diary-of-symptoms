import os
import sqlalchemy
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.SymptomEntry import SymptomEntry
from app.schema.SymptomEntry import SymptomEntryCreate, SymptomEntryResponse
from app.services.function import build_ai_insight
from app.services.database import get_db
from dotenv import load_dotenv


router = APIRouter(
    prefix="/api/symptom-entries",
    tags=["symptom-entries"],
)


load_dotenv()

@router.post("/add", status_code=status.HTTP_201_CREATED)
async def create_symptom_entry(symptom_entry: SymptomEntryCreate, db: AsyncSession = Depends(get_db)):
    # Вызываем ИИ-анализ
    ai_insights = build_ai_insight(symptom_entry)
    
    entry_data = symptom_entry.model_dump()
    entry_data["ai_insights"] = ai_insights
    
    if entry_data.get("start_at") is None:
        entry_data["start_at"] = datetime.utcnow()

    db_entry = SymptomEntry(**entry_data)
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
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
