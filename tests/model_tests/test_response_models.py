import pytest
from pydantic import ValidationError

from app.models.response_models import StrictChatResponse


def test_valid_strict_response():
    response = StrictChatResponse(answer='Dette er et gyldig svar.', source='test.pdf')
    assert response.answer == 'Dette er et gyldig svar.'
    assert response.source == 'test.pdf'


def test_strict_response_with_sensitive_data_fnr():
    with pytest.raises(ValidationError) as exc_info:
        StrictChatResponse(answer='Svaret inneholder fødselsnummer 01020312345.')
    assert 'sensitiv informasjon' in str(exc_info.value)


def test_strict_response_with_short_text():
    with pytest.raises(ValidationError):
        StrictChatResponse(answer='Oi.')


def test_strict_response_without_source():
    response = StrictChatResponse(answer='Gyldig svar uten kilde.')
    assert response.source is None
