import pytest
import sqlalchemy

from backend.app.models.Medication import Medication
from backend.app.models.SymptomEntry import SymptomEntry
from backend.app.models.User import User


@pytest.mark.asyncio
async def test_database_persists_user_medication_and_symptom_entry(db_session):
    user = User(
        name="Database User",
        email="database@example.com",
        hashed_password="hashed",
        age=31,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    medication = Medication(
        user_id=user.id,
        name="Magnesium",
        dosage="200mg",
        regular_medications=["Magnesium"],
        allergies=[],
    )
    symptom_entry = SymptomEntry(
        user_id=user.id,
        symptom="Headache",
        severity=4,
        duration="2h",
        sleep_quality=7,
        sleep_hours=7.5,
        stress_level=3,
        ai_insights="Stored insight",
    )
    db_session.add_all([medication, symptom_entry])
    await db_session.commit()

    result = await db_session.execute(
        sqlalchemy.select(User).where(User.email == "database@example.com")
    )
    persisted_user = result.scalar_one()

    assert persisted_user.id == user.id
    assert persisted_user.email == "database@example.com"

    medication_result = await db_session.execute(
        sqlalchemy.select(Medication).where(Medication.user_id == user.id)
    )
    assert medication_result.scalar_one().name == "Magnesium"

    symptom_result = await db_session.execute(
        sqlalchemy.select(SymptomEntry).where(SymptomEntry.user_id == user.id)
    )
    assert symptom_result.scalar_one().ai_insights == "Stored insight"
