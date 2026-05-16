from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Medication import Medication
from app.schema.Medication import MedicationCreate, MedicationResponse
from app.services.database import get_db

import sqlalchemy
import asyncio

router = APIRouter(
    prefix="/api/medications",
    tags=["medications"],
)

@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=MedicationResponse)
async def create_medication(medication: MedicationCreate, db: AsyncSession = Depends(get_db)):
    # 1. Ищем существующую запись ПО USER_ID (один пользователь — одна карта)
    result = await db.execute(
        sqlalchemy.select(Medication).where(Medication.user_id == medication.user_id)
    )
    db_medication = result.scalar_one_or_none()

    obj_data = medication.model_dump(exclude_unset=True)

    if db_medication:
        # 2. Если нашли — обновляем поля
        for key, value in obj_data.items():
            setattr(db_medication, key, value)
    else:
        # 3. Если нет — создаем новую
        db_medication = Medication(**obj_data)
        db.add(db_medication)

    await db.commit()
    await db.refresh(db_medication)
    return db_medication

@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication(medication_id: int, db: AsyncSession = Depends(get_db)):
    db_medication = await db.get(Medication, medication_id)
    if not db_medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    return db_medication

@router.get("", response_model=list[MedicationResponse])
async def list_medications(
    user_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    query = sqlalchemy.select(Medication).order_by(Medication.created_at.desc())
    if user_id is not None:
        query = query.where(Medication.user_id == user_id)

    result = await db.execute(query)
    return list(result.scalars().all())
