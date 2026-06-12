from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[4]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


@dataclass(slots=True)
class BotSettings:
    token: str = os.getenv("TOKEN", "")
    backend_api_base_url: str = os.getenv("BACKEND_API_BASE_URL", "http://127.0.0.1:8000")
    request_timeout: float = float(os.getenv("BOT_REQUEST_TIMEOUT", "15"))
    retry_attempts: int = int(os.getenv("BOT_RETRY_ATTEMPTS", "2"))
    retry_backoff: float = float(os.getenv("BOT_RETRY_BACKOFF", "0.4"))
    profile_cache_ttl: int = int(os.getenv("BOT_PROFILE_CACHE_TTL", "30"))


settings = BotSettings()
