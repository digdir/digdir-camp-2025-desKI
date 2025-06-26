# app/models/response_models.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.utils.desensitize import detect_sensitive_data

class BaseChatResponse(BaseModel):
    answer: str = Field(..., min_length=5, max_length=1000)
    source: Optional[str] = None

class StrictChatResponse(BaseChatResponse):
    @field_validator("answer")
    def forbid_sensetive_output(cls, v):
        if detect_sensitive_data(v):
            raise ValueError(
                "Svaret inneholder sensitiv informasjon. "
                "Vennligst fjern den eller kontakt kundeservice."
            )
        return v
