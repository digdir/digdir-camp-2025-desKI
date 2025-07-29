# app/models/response_models.py
from typing import Optional

from pydantic import Field, BaseModel, field_validator

from app.utils.desensitize import detect_sensitive_data, remove_sensitive_data


# Base model for chat responses
class BaseChatResponse(BaseModel):
    answer: str = Field(..., min_length=5, max_length=3000)
    source: Optional[str] = None


# Extended model that validates output for sensitive data
class StrictChatResponse(BaseChatResponse):
    @field_validator('answer')
    def forbid_sensetive_output(cls, v):
        if detect_sensitive_data(v):
            return remove_sensitive_data(v)
        return v
