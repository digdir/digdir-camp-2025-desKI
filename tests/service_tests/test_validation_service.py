import pytest
from app.services.validation_service import ValidationService

@pytest.fixture
def validator():
    return ValidationService()

def test_validate_too_short(validator):
    result = validator.validate("")
    assert result == "Spørsmål er for kort / Query is too short"

def test_validate_too_long(validator):
    long_input = "x" * 2001
    result = validator.validate(long_input)
    assert result == "Spørsmål er for langt / Query is too long"

def test_validate_no_sensitive_data(validator):
    clean = "Hvordan logger jeg inn på Altinn?"
    redacted, found = validator.validate(clean)
    assert redacted == clean
    assert found == []

def test_validate_with_fnr(validator):
    raw = "FNR: 12345678901"
    redacted, found = validator.validate(raw)
    assert "[REDACTED_FNR]" in redacted
    assert "FNR" in found

def test_validate_multiple_hits(validator):
    raw = "Kontakt meg på navn@eksempel.no og bruk kort 1234-5678-8765-4321"
    redacted, found = validator.validate(raw)
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_CARD]" in redacted
    assert "EMAIL" in found and "CARD" in found

def test_validate_non_string_input_raises(validator):
    with pytest.raises(ValueError):
        validator.validate(1234)
