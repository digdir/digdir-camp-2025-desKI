from fastapi import Depends, APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.dependencies.services import get_query_service
from app.models.request_models import StrictChatRequest
from app.models.response_models import StrictChatResponse
from app.services.query_service import QueryService

router = APIRouter(tags=['Service desk'])


@router.post('/', response_model=StrictChatResponse)
def ask_service_desk(
    req: StrictChatRequest,
    qs: QueryService = Depends(get_query_service),    
) -> StrictChatResponse:
    response = qs.run_query(
        user_query=req.question,
        named_endpoint=NamedEndpoint.SERVICEDESK,
        previous=req.previous,
        logs=req.logs
    )

    return StrictChatResponse(answer=response or 'Hei fra servicedesk!', source=None)
