import pytest

from helpers import create_user


def symptom_payload(user_id):
    return {
        "user_id": user_id,
        "symptom": "Headache",
        "severity": 6,
        "duration": "3h",
        "body_state": "Tired and tense",
        "notes": "Started after lunch",
        "sleep_quality": 5,
        "sleep_hours": 6.5,
        "stress_level": 7,
        "food_notes": "Coffee and sandwich",
        "medications_taken": "Ibuprofen 200mg",
    }


@pytest.mark.asyncio
async def test_create_get_and_list_symptom_entries(client, monkeypatch):
    user = await create_user(client)
    monkeypatch.setattr(
        "app.routers.SymptomEntry.build_ai_insight",
        lambda symptom_entry: "Mocked AI insight",
    )

    create_response = await client.post(
        "/api/symptom-entries/add",
        json=symptom_payload(user["id"]),
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["symptom"] == "Headache"
    assert created["ai_insights"] == "Mocked AI insight"

    get_response = await client.get(f"/api/symptom-entries/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]

    list_response = await client.get(f"/api/symptom-entries?user_id={user['id']}")
    assert list_response.status_code == 200
    entries = list_response.json()
    assert len(entries) == 1
    assert entries[0]["id"] == created["id"]


@pytest.mark.asyncio
async def test_create_symptom_entry_validates_severity(client):
    user = await create_user(client)
    payload = symptom_payload(user["id"])
    payload["severity"] = 11

    response = await client.post("/api/symptom-entries/add", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_symptom_entry_returns_404_for_missing_entry(client):
    response = await client.get("/api/symptom-entries/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Symptom entry not found"
