import time
import logging

from fastapi import Depends, APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.dependencies.services import get_query_service
from app.models.request_models import StrictChatRequest
from app.models.response_models import StrictChatResponse
from app.services.query_service import QueryService

router = APIRouter(tags=['Chatbot'])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post('/', response_model=StrictChatResponse)
def ask_chatbot(
    req: StrictChatRequest,
    qs: QueryService = Depends(get_query_service),
) -> StrictChatResponse:
    starttid = time.time()
    logger.info('⚡ Received chatbot request')

    response = qs.run_query(
        user_query=req.question,
        named_endpoint=NamedEndpoint.CHATBOT,
        previous=req.previous,
    )

    logger.info(f'✅ Responded in {time.time() - starttid:.2f}s')
    return StrictChatResponse(answer=response or 'Hei fra chatbot!', source=None)
