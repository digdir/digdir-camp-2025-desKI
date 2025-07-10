from fastapi import APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse
from app.services.query_service import QueryService
from app.services.query_service import QueryService

router = APIRouter(tags=['Chatbot'])


# Endpoint for handling chatbot queries
@router.post('/', response_model=BaseChatResponse)
def ask_chatbot(req: BaseChatRequest):
    qs = QueryService()
    response = qs.run_query(req.question, NamedEndpoint.CHATBOT)

    return BaseChatResponse(answer=response or 'Hei fra chatbot!', source=None)
