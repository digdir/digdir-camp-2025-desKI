from fastapi import APIRouter

from app.models.request_models import StrictChatRequest
from app.models.response_models import StrictChatResponse

router = APIRouter(tags=['Service desk'])


# Endpoint for handling service desk queries
@router.post('/', response_model=StrictChatResponse)
def ask_service_desk(req: StrictChatRequest):
    # Call embedder
    # Query vector database
    # Call language model if needed
    return StrictChatResponse(answer='Hei fra servicedesk!', source=None)
