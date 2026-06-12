import pytest
from pydantic import ValidationError

from backend.app.schema.Medication import MedicationCreate
from backend.app.schema.SymptomEntry import SymptomEntryCreate
from backend.app.schema.User import UserCreate


def test_user_create_validates_email():
    with pytest.raises(ValidationError):
        UserCreate(
            name="Bad Email",
            email="not-an-email",
            password="password",
        )


def test_symptom_entry_create_validates_ranges():
    with pytest.raises(ValidationError):
        SymptomEntryCreate(
            symptom="Pain",
            severity=12,
            duration="1h",
            sleep_quality=5,
            sleep_hours=8,
            stress_level=5,
        )

    with pytest.raises(ValidationError):
        SymptomEntryCreate(
            symptom="Pain",
            severity=5,
            duration="1h",
            sleep_quality=5,
            sleep_hours=25,
            stress_level=5,
        )


def test_medication_create_uses_independent_default_lists():
    first = MedicationCreate(name="A", dosage="10mg")
    second = MedicationCreate(name="B", dosage="20mg")

    first.allergies.append("Latex")

    assert second.allergies == []
    assert first.regular_medications == []
