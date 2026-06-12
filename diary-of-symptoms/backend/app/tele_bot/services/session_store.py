from __future__ import annotations

import logging
from pathlib import Path

import aiosqlite


logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "bot_database.db"
LEGACY_DB_PATH = Path.cwd() / "bot_database.db"


def _get_connection_context() -> aiosqlite.Connection:
    return aiosqlite.connect(DB_PATH.as_posix(), timeout=10)


async def _setup_pragmas(db: aiosqlite.Connection) -> None:
    db.row_factory = aiosqlite.Row
    await db.executescript(
        """
        PRAGMA foreign_keys = ON;
        PRAGMA journal_mode = WAL;
        PRAGMA busy_timeout = 10000;
        """
    )


async def _migrate_legacy_db() -> None:
    if LEGACY_DB_PATH == DB_PATH or not LEGACY_DB_PATH.exists():
        return

    rows = []
    try:
        async with aiosqlite.connect(LEGACY_DB_PATH.as_posix(), timeout=5) as legacy_db:
            legacy_db.row_factory = aiosqlite.Row
            async with legacy_db.execute("PRAGMA table_info(users)") as cursor:
                legacy_columns = {row[1] for row in await cursor.fetchall()}

            query = "SELECT telegram_id, auth_token, email"
            if "app_user_id" in legacy_columns:
                query += ", app_user_id"
            query += " FROM users"

            async with legacy_db.execute(query) as cursor:
                rows = await cursor.fetchall()
    except Exception as exc:
        logger.warning("Legacy bot DB unavailable, skipping migration: %s", exc)
        return

    if not rows:
        return

    async with _get_connection_context() as db:
        await _setup_pragmas(db)
        for row in rows:
            app_user_id = row["app_user_id"] if "app_user_id" in row.keys() else None
            await db.execute(
                """
                INSERT INTO users (telegram_id, auth_token, app_user_id, email)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE
                SET auth_token = excluded.auth_token,
                    app_user_id = COALESCE(excluded.app_user_id, users.app_user_id),
                    email = excluded.email
                """,
                (row["telegram_id"], row["auth_token"], app_user_id, row["email"]),
            )
        await db.commit()

    logger.info("Legacy bot DB migration completed")


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with _get_connection_context() as db:
        await _setup_pragmas(db)
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                auth_token TEXT,
                app_user_id INTEGER,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = {row[1] for row in await cursor.fetchall()}

        if "app_user_id" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN app_user_id INTEGER")

        await db.commit()

    await _migrate_legacy_db()


async def get_user_token(telegram_id: int) -> str | None:
    async with _get_connection_context() as db:
        await _setup_pragmas(db)
        async with db.execute(
            "SELECT auth_token FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row["auth_token"] if row else None


async def get_app_user_id(telegram_id: int) -> int | None:
    async with _get_connection_context() as db:
        await _setup_pragmas(db)
        async with db.execute(
            "SELECT app_user_id FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row["app_user_id"] if row else None


async def get_create_user(telegram_id: int) -> str | None:
    async with _get_connection_context() as db:
        await _setup_pragmas(db)
        async with db.execute(
            "SELECT created_at FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row["created_at"] if row else None


async def save_user_session(
    telegram_id: int,
    token: str,
    email: str | None,
    created_at: str | None,
    app_user_id: int | None = None,
) -> None:
    if not token:
        raise ValueError("Token is empty and cannot be saved")

    async with _get_connection_context() as db:
        await _setup_pragmas(db)
        await db.execute(
            """
            INSERT INTO users (telegram_id, auth_token, app_user_id, email, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE
            SET auth_token = excluded.auth_token,
                app_user_id = COALESCE(excluded.app_user_id, users.app_user_id),
                email = excluded.email,
                created_at = COALESCE(excluded.created_at, users.created_at)
            """,
            (telegram_id, token, app_user_id, email, created_at),
        )
        await db.commit()


async def clear_user_session(telegram_id: int) -> None:
    async with _get_connection_context() as db:
        await _setup_pragmas(db)
        await db.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        await db.commit()


async def get_user_session(telegram_id: int) -> dict[str, object] | None:
    async with _get_connection_context() as db:
        await _setup_pragmas(db)
        async with db.execute(
            "SELECT telegram_id, auth_token, app_user_id, email, created_at FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return dict(row)
