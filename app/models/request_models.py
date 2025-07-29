# app/models/request_models.py
from typing import Any, Dict, Optional

from pydantic import Field, BaseModel, field_validator

from app.utils.desensitize import detect_sensitive_data, remove_sensitive_data


# Base model for chat requests
class BaseChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=3000)
    context: Optional[Dict[str, Any]] = None
    previous: Optional[list[str]] = None
    logs: Optional[str] = None


# Extended model with input validation for sensitive data
class StrictChatRequest(BaseChatRequest):
    @field_validator('question')
    def check_for_sensitive_input(cls, v):
        if detect_sensitive_data(v):
            # Pydantic captures ValueError as a validation error on the 'question' field
            return remove_sensitive_data(v)
        return v
    
    @field_validator('logs')
    def truncate_logs_if_too_long(cls, v):
        if v is not None and len(v) > 10000:
            return v[:10000]  # Kutter uten å klage
        return v
