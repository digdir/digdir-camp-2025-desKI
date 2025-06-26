# app/models/request_models.py
from pydantic import Field, BaseModel, field_validator

from app.utils.desensitize import detect_sensitive_data


class BaseChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500)


class StrictChatRequest(BaseChatRequest):
    @field_validator('question')
    def check_for_sensitive_input(cls, v):
        if detect_sensitive_data(v):
            # Pydantic fanger ValueError som en validation error på feltet 'question'
            raise ValueError(
                'Spørsmålet inneholder sensitiv informasjon. '
                'Vennligst fjern den eller kontakt kundeservice.'
            )
        return v
