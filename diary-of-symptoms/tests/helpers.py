async def create_user(client, email="patient@example.com", password="strong-password"):
    response = await client.post(
        "/api/users/register",
        json={
            "name": "Test Patient",
            "email": email,
            "password": password,
            "age": 30,
            "weight": 72,
            "height": 178,
        },
    )
    assert response.status_code == 201
    return response.json()["user"]
