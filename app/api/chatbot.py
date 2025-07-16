from fastapi import APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.models.request_models import StrictChatRequest
from app.models.response_models import StrictChatResponse
from app.services.query_service import QueryService

router = APIRouter(tags=['Chatbot'])


# Endpoint for handling chatbot queries
@router.post('/', response_model=StrictChatResponse)
def ask_chatbot(req: StrictChatRequest) -> StrictChatResponse:
    query = req.question
    qs = QueryService()
    response = qs.run_query(
        user_query=req.question, named_endpoint=NamedEndpoint.CHATBOT
    )

    return StrictChatResponse(answer=response or 'Hei fra chatbot!', source=None)
