from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Общие поля, которые есть везде
class ReminderBase(BaseModel):
    type: str = Field(..., description="Тип напоминания (symptom_log, medication, etc.)")
    title: str = Field(..., max_length=100)
    message: str
    cron_expr: Optional[str] = Field(default=None, description="Cron-выражение, например: '0 20 * * *'")
    send_time: Optional[str] = Field(default=None, description="Время отправки в формате HH:MM")
    weekdays: Optional[list[str]] = Field(default=None, description="Дни недели: mon, tue, wed, thu, fri, sat, sun")
    send_telegram: bool = False
    telegram_chat_id: Optional[int] = None
    send_email: bool = False
    enable: bool = True

# 1. Схема для создания (принимаем с фронта / бота)
class ReminderCreate(ReminderBase):
    user_id: int

# 2. Схема для частичного обновления (все поля опциональны)
class ReminderUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    cron_expr: Optional[str] = None
    send_time: Optional[str] = None
    weekdays: Optional[list[str]] = None
    send_telegram: Optional[bool] = None
    telegram_chat_id: Optional[int] = None
    send_email: Optional[bool] = None
    enable: Optional[bool] = None

# 3. Схема для ответа сервера (возвращаем клиенту)
class ReminderResponse(ReminderBase):
    id: int
    user_id: int
    cron_expr: str
    last_send_at: Optional[datetime] = None
    next_send_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Это вместо orm_mode в Pydantic v2
