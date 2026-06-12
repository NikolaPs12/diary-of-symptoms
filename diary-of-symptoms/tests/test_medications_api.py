import pytest

from helpers import create_user


def medication_payload(user_id, name="Magnesium"):
    return {
        "user_id": user_id,
        "name": name,
        "dosage": "200mg",
        "regular_medications": [name],
        "diagnosis": "Migraine",
        "allergies": ["Penicillin"],
        "notes": "Take after dinner",
    }


@pytest.mark.asyncio
async def test_create_update_get_and_list_medications(client):
    user = await create_user(client)

    create_response = await client.post(
        "/api/medications/add",
        json=medication_payload(user["id"]),
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Magnesium"
    assert created["allergies"] == ["Penicillin"]

    update_response = await client.post(
        "/api/medications/add",
        json=medication_payload(user["id"], name="Vitamin D"),
    )
    assert update_response.status_code == 201
    updated = update_response.json()
    assert updated["id"] == created["id"]
    assert updated["name"] == "Vitamin D"

    get_response = await client.get(f"/api/medications/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Vitamin D"

    list_response = await client.get(f"/api/medications?user_id={user['id']}")
    assert list_response.status_code == 200
    medications = list_response.json()
    assert len(medications) == 1
    assert medications[0]["id"] == created["id"]


@pytest.mark.asyncio
async def test_create_medication_validates_required_fields(client):
    user = await create_user(client)

    response = await client.post(
        "/api/medications/add",
        json={"user_id": user["id"], "name": "Incomplete"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_medication_returns_404_for_missing_medication(client):
    response = await client.get("/api/medications/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Medication not found"
