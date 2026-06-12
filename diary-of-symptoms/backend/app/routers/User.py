import hashlib
import secrets  # Встроенная библиотека Python для генерации случайных токенов
import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.User import User
from app.schema.User import UserCreate, UserLogin, UserResponse, UserUpdate, UserAuthResponse
from app.services.database import get_db

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.post("/register", response_model=UserAuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем, существует ли пользователь
    result = await db.execute(
        sqlalchemy.select(User).where(User.email == user.email)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Переводим Pydantic-модель в словарь и хешируем пароль (ВОЗВРАЩАЕМ ТВОЙ КОД)
    user_data = user.model_dump()
    raw_password = user_data.pop("password")
    user_data["hashed_password"] = hash_password(raw_password)

    # 3. Создаем объект пользователя для БД
    db_user = User(**user_data)
    
    # 4. Генерируем токен
    generated_token = secrets.token_hex(32)
    
    # Если в SQLAlchemy-модели User есть колонка auth_token, раскомментируй строку ниже:
    # db_user.auth_token = generated_token

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return {
        "status": "success",
        "token": generated_token,
        "user": db_user
    }


@router.post("/login", response_model=UserAuthResponse)
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    # 1. Ищем пользователя по email
    result = await db.execute(
        sqlalchemy.select(User).where(User.email == user.email)
    )
    db_user = result.scalar_one_or_none()

    # 2. Проверяем пароль
    if not db_user or db_user.hashed_password != hash_password(user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    # 3. Генерируем токен для клиента. Сейчас токен не хранится в модели User.
    generated_token = secrets.token_hex(32)

    # Закрываем read-only транзакцию явно, чтобы в логах не выглядело как ошибка.
    await db.commit()

    return {
        "status": "success",
        "token": generated_token,
        "user": db_user
    }

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, user_id) 
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user
