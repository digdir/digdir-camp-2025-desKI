import time
import logging

from fastapi import Depends, APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.models.request_models import StrictChatRequest
from app.models.response_models import StrictChatResponse
from app.services.query_service import QueryService, get_query_service

router = APIRouter(tags=['Chatbot'])

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more detail
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)


# Endpoint for handling chatbot queries
@router.post('/', response_model=StrictChatResponse)
def ask_chatbot(
    req: StrictChatRequest, qs: QueryService = Depends(get_query_service)
) -> StrictChatResponse:
    starttid = time.time()
    logger.info(f'Received request at {starttid}')
    response = qs.run_query(
        user_query=req.question, named_endpoint=NamedEndpoint.CHATBOT
    )
    logger.info(f'Returned response in {time.time() - starttid:.4f}')
    return StrictChatResponse(answer=response or 'Hei fra chatbot!', source=None)
