from __future__ import annotations

from dataclasses import dataclass

from api_client.client import TelegramBackendClient
from services.formatters import compute_health_stats


@dataclass(slots=True)
class ProfileContext:
    user: dict
    entries: list[dict]
    medications: list[dict]
    stats: dict[str, object]


async def load_profile_context(client: TelegramBackendClient, user_id: int, token: str | None) -> ProfileContext:
    user, entries, medications = await _fetch_profile_sources(client, user_id, token)
    stats = compute_health_stats(entries)
    return ProfileContext(user=user, entries=entries, medications=medications, stats=stats)


async def _fetch_profile_sources(
    client: TelegramBackendClient,
    user_id: int,
    token: str | None,
) -> tuple[dict, list[dict], list[dict]]:
    import asyncio

    user_task = client.get_user(user_id, token=token)
    entries_task = client.list_symptom_entries(user_id, token=token)
    medications_task = client.list_medications(user_id, token=token)
    user_result, entries_result, medications_result = await asyncio.gather(
        user_task,
        entries_task,
        medications_task,
        return_exceptions=True,
    )

    if isinstance(user_result, Exception):
        raise user_result

    entries = [] if isinstance(entries_result, Exception) else entries_result
    medications = [] if isinstance(medications_result, Exception) else medications_result
    return user_result, entries, medications
