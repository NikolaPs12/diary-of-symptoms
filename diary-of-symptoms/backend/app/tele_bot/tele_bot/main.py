from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BOT_DIR = CURRENT_DIR.parent
if str(BOT_DIR) not in sys.path:
    sys.path.insert(0, str(BOT_DIR))

from main import main  # noqa: E402


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
