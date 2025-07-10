from fastapi import APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse
from app.services.query_service import QueryService
from app.services.validation_service import ValidationService

router = APIRouter(tags=['Chatbot'])


# Endpoint for handling chatbot queries
@router.post('/', response_model=BaseChatResponse)
def ask_chatbot(req: BaseChatRequest):
    vs = ValidationService()
    query = req.question
    length_validation = vs.validate_length(query)
    
    if length_validation == -1:
        return BaseChatResponse(answer="Spørsmål er for kort / Query is too short")
    elif length_validation == 0:
        return BaseChatResponse(answer="Spørsmål er for langt / Query is too long")
    else:
        validated = vs.validate(query)
        qs = QueryService()
        response = qs.run_query(validated, NamedEndpoint.CHATBOT)

        return BaseChatResponse(answer=response or 'Hei fra chatbot!', source=None)
