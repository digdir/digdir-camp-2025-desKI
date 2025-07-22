from fastapi import APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.models.request_models import StrictChatRequest
from app.models.response_models import StrictChatResponse
from app.services.query_service import QueryService

router = APIRouter(tags=['Copilot'])


# Endpoint for handling copilot queries
@router.post('/', response_model=StrictChatResponse)
async def ask_chatbot(req: StrictChatRequest) -> StrictChatResponse:
    qs = QueryService()
    response = qs.run_query(
        user_query=req.question,
        named_endpoint=NamedEndpoint.COPILOT,
        external_context=req.context,
    )

    return StrictChatResponse(answer=response or 'Hei fra copilot!', source=None)
