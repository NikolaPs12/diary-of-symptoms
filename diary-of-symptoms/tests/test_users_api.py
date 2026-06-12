import pytest


@pytest.mark.asyncio
async def test_register_login_get_and_update_user(client):
    register_response = await client.post(
        "/api/users/register",
        json={
            "name": "Nikola",
            "email": "nikola@example.com",
            "password": "demo12345",
            "age": 24,
            "weight": 80,
            "height": 181,
        },
    )

    assert register_response.status_code == 201
    payload = register_response.json()
    assert payload["status"] == "success"
    assert payload["token"]
    assert payload["user"]["email"] == "nikola@example.com"
    assert "hashed_password" not in payload["user"]

    user_id = payload["user"]["id"]

    login_response = await client.post(
        "/api/users/login",
        json={"email": "nikola@example.com", "password": "demo12345"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["user"]["id"] == user_id

    get_response = await client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Nikola"

    update_response = await client.put(
        f"/api/users/{user_id}",
        json={"name": "Nikola Updated", "age": 25},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Nikola Updated"
    assert update_response.json()["age"] == 25


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(client):
    user_payload = {
        "name": "First User",
        "email": "duplicate@example.com",
        "password": "demo12345",
    }

    first_response = await client.post("/api/users/register", json=user_payload)
    second_response = await client.post("/api/users/register", json=user_payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(client):
    await client.post(
        "/api/users/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "correct-password",
        },
    )

    response = await client.post(
        "/api/users/login",
        json={"email": "login@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_get_user_returns_404_for_missing_user(client):
    response = await client.get("/api/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
