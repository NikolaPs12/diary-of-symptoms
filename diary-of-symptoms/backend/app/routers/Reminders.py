from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from datetime import datetime, timezone 
from croniter import croniter

from app.services.database import get_db
from app.schema.Reminders import ReminderCreate
from app.models.Reminders import Reminders
router = APIRouter(
    prefix="/api/reminders",
    tags=["reminders"]
)

@router.post("/create")
async def push_reminder(
    reminders: ReminderCreate,
    db: AsyncSession = Depends(get_db)
    
):
    data = reminders.model_dump()
    # 1. Берем текущее время (наша точка отсчета)
    now = datetime.now(timezone.utc)
    
    # 2. Создаем планировщик croniter, передав ему cron-строку и текущее время
    cron = croniter(data["cron_expr"], now)
    
    # 3. Говорим: "Дай нам следующее время срабатывания" 
    # и сразу сохраняем его в наш словарь
    data["next_send_at"] = cron.get_next(datetime)
    
    db_create = Reminders(**data)
    db.add(db_create)
    await db.commit()
    await db.refresh(db_create)