import os

from api_client.client import BackendAPIError, api_client

BACKEND_API_BASE_URL = os.getenv("BACKEND_API_BASE_URL", "http://127.0.0.1:8000")
API_URL = f"{BACKEND_API_BASE_URL}/api/users"


async def login_user(url_login, payload):
    try:
        auth = await api_client.login(email=payload["email"], password=payload["password"])
        return {"status": "success", **auth}
    except BackendAPIError as exc:
        return {"status": "error", "message": str(exc)}


async def reg_user(url_reg, payload):
    try:
        auth = await api_client.register(payload)
        return {"status": "success", **auth}
    except BackendAPIError as exc:
        return {"status": "error", "message": str(exc)}
