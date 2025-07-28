# app/models/request_models.py
from typing import Any, Dict, Optional

from pydantic import Field, BaseModel, field_validator

from app.utils.desensitize import detect_sensitive_data


# Base model for chat requests
class BaseChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=5000)
    context: Optional[Dict[str, Any]] = None


# Extended model with input validation for sensitive data
class StrictChatRequest(BaseChatRequest):
    @field_validator('question')
    def check_for_sensitive_input(cls, v):
        if detect_sensitive_data(v):
            # Pydantic captures ValueError as a validation error on the 'question' field
            raise ValueError(
                'Spørsmålet inneholder sensitiv informasjon. '
                'Vennligst fjern den eller kontakt kundeservice.'
            )
        return v
