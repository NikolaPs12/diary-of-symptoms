import hashlib
import sqlalchemy

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.User import User
from app.schema.User import UserCreate, UserLogin, UserResponse, UserUpdate
from app.services.database import get_db

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        sqlalchemy.select(User).where(User.email == user.email)
    )

    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = user.model_dump()

    raw_password = user_data.pop("password")

    user_data["hashed_password"] = hash_password(raw_password)

    db_user = User(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=UserResponse)
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await db.execute(
        sqlalchemy.select(User).where(User.email == user.email)
    )
    
    db_user = db_user.scalar_one_or_none()

    if not db_user or db_user.hashed_password != hash_password(user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession= Depends(get_db)):
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
