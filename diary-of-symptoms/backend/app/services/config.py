import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, field_validator, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union, Optional

# 1. Вычисляем путь до корня проекта (4 уровня вверх от backend/app/services/config.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# Загружаем переменные в окружение на случай, если другие модули используют os.getenv
load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        case_sensitive=False,  # Ставим False, чтобы не ловить ошибки из-за регистра
        extra="ignore",
    )

    # 2. Используем AnyUrl вместо PostgresDsn. 
    # Это позволит использовать и postgres:// и sqlite:// без ошибок валидации.
    database_url: AnyUrl = Field(validation_alias="DATABASE_URL")
    
    app_name: str = "Diary Of Symptoms API"
    debug: bool = True
    cors_origins: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    api_ai_key: str = ""
    static_dir: str = "backend/static"
    images_dir: str = "backend/static/images"

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on", "debug", "dev"}
        return bool(value)

# --- ЛЕНИВАЯ ЗАГРУЗКА (Синглтон) ---
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        # Pydantic сам подтянет ENV_PATH из model_config
        _settings = Settings()
    return _settings

# Глобальный объект настроек
settings = get_settings()