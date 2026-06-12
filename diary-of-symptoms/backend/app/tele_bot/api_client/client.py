from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import httpx

from services.config import settings


logger = logging.getLogger(__name__)


class BackendAPIError(RuntimeError):
    pass


def _to_iso_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()

    text = str(value).strip()
    if not text:
        return None

    try:
        return datetime.fromisoformat(text).date().isoformat()
    except ValueError:
        try:
            return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
        except ValueError:
            return text


@dataclass(slots=True)
class BackendRequestResult:
    data: Any
    status_code: int
    headers: dict[str, str] | None = None


class TelegramBackendClient:
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=settings.backend_api_base_url,
                timeout=settings.request_timeout,
                headers={"Content-Type": "application/json"},
            )

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _client_or_start(self) -> httpx.AsyncClient:
        if self._client is None:
            await self.start()
        assert self._client is not None
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        expect_json: bool = True,
    ) -> BackendRequestResult:
        client = await self._client_or_start()
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        last_error: Exception | None = None
        for attempt in range(settings.retry_attempts + 1):
            try:
                response = await client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json_body,
                    headers=headers,
                )

                if response.status_code >= 500 and attempt < settings.retry_attempts:
                    logger.warning(
                        "Backend returned %s for %s %s, retry %s/%s",
                        response.status_code,
                        method,
                        path,
                        attempt + 1,
                        settings.retry_attempts,
                    )
                    await asyncio.sleep(settings.retry_backoff * (attempt + 1))
                    continue

                if not response.is_success:
                    raise BackendAPIError(self._extract_error(response))

                payload = response.json() if expect_json else response.content
                headers = dict(response.headers)
                return BackendRequestResult(data=payload, status_code=response.status_code, headers=headers)
            except (httpx.TimeoutException, httpx.NetworkError, BackendAPIError) as exc:
                last_error = exc
                if attempt < settings.retry_attempts and not isinstance(exc, BackendAPIError):
                    logger.warning(
                        "Request failed for %s %s (%s), retry %s/%s",
                        method,
                        path,
                        exc,
                        attempt + 1,
                        settings.retry_attempts,
                    )
                    await asyncio.sleep(settings.retry_backoff * (attempt + 1))
                    continue
                break

        raise BackendAPIError(str(last_error) if last_error else "Backend request failed")

    @staticmethod
    def _extract_error(response: httpx.Response) -> str:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                detail = payload.get("detail") or payload.get("message")
                if isinstance(detail, list):
                    return "; ".join(str(item) for item in detail)
                if detail:
                    return str(detail)
                return str(payload)
            return str(payload)
        except Exception:
            return response.text or f"HTTP {response.status_code}"

    async def login(self, email: str, password: str) -> dict[str, Any]:
        result = await self._request(
            "POST",
            "/api/users/login",
            json_body={"email": email, "password": password},
        )
        return self._validate_auth_payload(result.data)

    async def register(self, payload: dict[str, Any]) -> dict[str, Any]:
        result = await self._request("POST", "/api/users/register", json_body=payload)
        return self._validate_auth_payload(result.data)

    async def get_user(self, user_id: int, token: str | None = None) -> dict[str, Any]:
        result = await self._request("GET", f"/api/users/{user_id}", token=token)
        if not isinstance(result.data, dict):
            raise BackendAPIError("Invalid user payload")
        return result.data

    async def list_symptom_entries(self, user_id: int, token: str | None = None) -> list[dict[str, Any]]:
        result = await self._request("GET", "/api/symptom-entries", token=token, params={"user_id": user_id})
        if not isinstance(result.data, list):
            raise BackendAPIError("Invalid symptom list payload")
        return result.data

    async def list_medications(self, user_id: int, token: str | None = None) -> list[dict[str, Any]]:
        result = await self._request("GET", "/api/medications", token=token, params={"user_id": user_id})
        if not isinstance(result.data, list):
            raise BackendAPIError("Invalid medication list payload")
        return result.data

    async def create_symptom_entry(self, payload: dict[str, Any], token: str | None = None) -> dict[str, Any]:
        result = await self._request("POST", "/api/symptom-entries/add", token=token, json_body=payload)
        if not isinstance(result.data, dict):
            raise BackendAPIError("Invalid symptom entry payload")
        return result.data

    async def download_pdf_report(
        self,
        *,
        user_id: int,
        token: str | None = None,
        start_date: Any | None = None,
        end_date: Any | None = None,
    ) -> tuple[bytes, str]:
        params = {
            "user_id": user_id,
            "start_date": _to_iso_date(start_date),
            "end_date": _to_iso_date(end_date),
        }
        params = {key: value for key, value in params.items() if value not in {None, ""}}

        result = await self._request(
            "GET",
            "/api/generation/pdf",
            token=token,
            params=params,
            expect_json=False,
        )

        filename = "symptoms_report.pdf"
        headers = result.headers or {}
        content_disposition = ""
        for key, value in headers.items():
            if key.lower() == "content-disposition":
                content_disposition = value
                break
        if "filename=" in content_disposition:
            try:
                filename = content_disposition.split("filename=")[1].strip('"')
            except Exception:
                pass

        return bytes(result.data), filename

    @staticmethod
    def _validate_auth_payload(payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise BackendAPIError("Invalid auth payload")
        user = payload.get("user") or {}
        token = payload.get("token") or payload.get("access_token")
        if not isinstance(user, dict) or not user.get("id"):
            raise BackendAPIError("Auth response does not contain a valid user")
        if not token:
            raise BackendAPIError("Auth response does not contain a token")
        return {"status": payload.get("status", "success"), "token": token, "user": user}


api_client = TelegramBackendClient()
