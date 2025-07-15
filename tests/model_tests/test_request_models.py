import pytest
from pydantic import ValidationError

from app.models.request_models import StrictChatRequest


def test_valid_input_passes():
    model = StrictChatRequest(question='Hva gjør Digdir?', context={})
    assert model.question == 'Hva gjør Digdir?'


def test_too_short_question_fails():
    with pytest.raises(ValidationError) as exc_info:
        StrictChatRequest(question='A', context={})
    assert 'String should have at least 2 characters' in str(exc_info.value)


def test_too_long_question_fails():
    with pytest.raises(ValidationError) as exc_info:
        StrictChatRequest(question='A' * 3001, context={})
    assert 'String should have at most 3000 characters' in str(exc_info.value)


def test_sensitive_input_fails():
    with pytest.raises(ValidationError) as exc_info:
        StrictChatRequest(question='Her er mitt fødselsnummer: 12345678901')
    assert 'inneholder sensitiv informasjon' in str(exc_info.value)
