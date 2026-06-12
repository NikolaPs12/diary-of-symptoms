import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.Generation import router as generation_router
from app.routers.Medication import router as medication_router
from app.routers.SymptomEntry import router as symptom_entry_router
from app.routers.User import router as user_router
from app.services.config import settings
from app.services.database import init_db

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if isinstance(settings.cors_origins, list) else [settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(symptom_entry_router)
app.include_router(medication_router)
app.include_router(generation_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.services.main:app", host="127.0.0.1", port=int(os.getenv("PORT") or 8000), reload=True)
