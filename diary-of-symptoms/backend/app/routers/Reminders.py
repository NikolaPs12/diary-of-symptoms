from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.Reminders import ReminderCreate, ReminderResponse, ReminderUpdate
from app.services.database import get_db
from app.services.reminders import (
    create_reminder,
    delete_reminder,
    get_reminder,
    list_reminders,
    serialize_reminder,
    set_reminder_enabled,
    update_reminder,
)


router = APIRouter(
    prefix="/api/reminders",
    tags=["reminders"],
)


def _bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReminderResponse)
@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ReminderResponse)
async def push_reminder(
    reminder: ReminderCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        created = await create_reminder(db, reminder.model_dump(exclude_none=True))
    except ValueError as exc:
        raise _bad_request(exc) from exc
    return serialize_reminder(created)


@router.get("", response_model=list[ReminderResponse])
async def get_reminders(
    user_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    reminders = await list_reminders(db, user_id=user_id)
    return [serialize_reminder(item) for item in reminders]


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder_by_id(
    reminder_id: int,
    user_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    reminder = await get_reminder(db, reminder_id=reminder_id, user_id=user_id)
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return serialize_reminder(reminder)


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder_by_id(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    user_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    reminder = await get_reminder(db, reminder_id=reminder_id, user_id=user_id)
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    try:
        updated = await update_reminder(db, reminder, reminder_update.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise _bad_request(exc) from exc
    return serialize_reminder(updated)


@router.patch("/{reminder_id}/toggle", response_model=ReminderResponse)
async def toggle_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    user_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    reminder = await get_reminder(db, reminder_id=reminder_id, user_id=user_id)
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    if reminder_update.enable is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="enable is required")

    updated = await set_reminder_enabled(db, reminder, reminder_update.enable)
    return serialize_reminder(updated)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder_by_id(
    reminder_id: int,
    user_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    reminder = await get_reminder(db, reminder_id=reminder_id, user_id=user_id)
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    await delete_reminder(db, reminder)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
