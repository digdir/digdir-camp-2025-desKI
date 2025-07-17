from fastapi import APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.models.request_models import StrictChatRequest
from app.models.response_models import StrictChatResponse
from app.services.query_service import QueryService

router = APIRouter(tags=['Service desk'])


# Endpoint for handling service desk queries
@router.post('/', response_model=StrictChatResponse)
def ask_service_desk(req: StrictChatRequest) -> StrictChatResponse:
    query = req.question
    qs = QueryService()
    response = qs.run_query(query, NamedEndpoint.SERVICEDESK)

    return StrictChatResponse(answer=response or 'Noe gikk galt', source=None)
