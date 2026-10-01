import json
import logging
from datetime import datetime
from typing import Any

from google import genai
from google.genai import types


def _build_prompt(transcript: str | None = None) -> str:
    current_datetime = datetime.now().isoformat(timespec="seconds")

    source_instruction = (
        f"Расшифровка:\n{transcript}"
        if transcript is not None
        else "Аудио приложено к запросу. Сначала распознай речь, затем извлеки данные."
    )

    return f"""
Ты — модуль структурирования медицинского дневника.

Извлеки данные из голосового сообщения и верни только JSON.

Правила:
- Не ставь диагнозы.
- Не назначай лечение.
- Не придумывай отсутствующие сведения.
- Для неизвестных значений используй null.
- severity, sleep_quality и stress_level должны быть от 1 до 10.
- sleep_hours должно быть числом от 0 до 24.
- start_at верни в формате ISO 8601.
- Не возвращай id, user_id, created_at и ai_insights.

Текущая дата и время:
{current_datetime}

{source_instruction}
"""


def _response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "start_at": {
                "type": ["string", "null"],
                "description": "Время начала симптомов в ISO 8601",
            },
            "symptom": {
                "type": ["string", "null"],
            },
            "severity": {
                "type": ["integer", "null"],
                "minimum": 1,
                "maximum": 10,
            },
            "duration": {
                "type": ["string", "null"],
            },
            "body_state": {
                "type": ["string", "null"],
            },
            "notes": {
                "type": ["string", "null"],
            },
            "sleep_quality": {
                "type": ["integer", "null"],
                "minimum": 1,
                "maximum": 10,
            },
            "sleep_hours": {
                "type": ["number", "null"],
                "minimum": 0,
                "maximum": 24,
            },
            "stress_level": {
                "type": ["integer", "null"],
                "minimum": 1,
                "maximum": 10,
            },
            "food_notes": {
                "type": ["string", "null"],
            },
            "medications_taken": {
                "type": ["string", "null"],
            },
        },
        "required": [
            "start_at",
            "symptom",
            "severity",
            "duration",
            "body_state",
            "notes",
            "sleep_quality",
            "sleep_hours",
            "stress_level",
            "food_notes",
            "medications_taken",
        ],
        "additionalProperties": False,
    }


async def _generate_symptom_json(
    contents: list[Any] | str,
    api_key: str,
) -> dict[str, Any]:
    client = genai.Client(api_key=api_key)
    last_error: Exception | None = None

    for model_name in [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
    ]:
        try:
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_json_schema=_response_schema(),
                ),
            )

            if not response.text:
                raise RuntimeError("Gemini вернул пустой ответ")

            return json.loads(response.text)

        except Exception as exc:
            last_error = exc
            logging.warning(
                "AI model %s failed: %s",
                model_name,
                exc,
            )

    raise RuntimeError(
        "Не удалось структурировать голосовое сообщение"
    ) from last_error


async def extract_symptom_json(
    transcript: str,
    api_key: str,
) -> dict[str, Any]:
    return await _generate_symptom_json(
        contents=_build_prompt(transcript),
        api_key=api_key,
    )


async def extract_symptom_json_from_audio(
    audio_bytes: bytes,
    api_key: str,
    mime_type: str = "audio/ogg",
) -> dict[str, Any]:
    return await _generate_symptom_json(
        contents=[
            _build_prompt(),
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
        ],
        api_key=api_key,
    )
