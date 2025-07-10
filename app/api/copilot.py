from fastapi import APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse
from app.services.query_service import QueryService

router = APIRouter(tags=['Copilot'])


# Endpoint for handling copilot queries
@router.post('/', response_model=BaseChatResponse)
def ask_chatbot(req: BaseChatRequest):
    qs = QueryService() 
    response = qs.run_query(user_query=req.question, named_endpoint=NamedEndpoint.COPILOT)

    return BaseChatResponse(answer=response or 'Hei fra copilot!', source=None)
