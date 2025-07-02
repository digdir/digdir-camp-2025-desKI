from fastapi import APIRouter

from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse

router = APIRouter(tags=['Copilot'])


# Endpoint for handling copilot queries
@router.post('/', response_model=BaseChatResponse)
def ask_copilot(req: BaseChatRequest):
    # Call embedder
    # Include extra context from the website
    # Call language model if needed
    return BaseChatResponse(answer='Hei! fra copiliot', source=None)
