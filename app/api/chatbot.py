from fastapi import APIRouter

from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse

router = APIRouter(tags=['Chatbot'])

# Endpoint for handling chatbot queries
@router.post('/', response_model=BaseChatResponse)
def ask_chatbot(req: BaseChatRequest):
    # Call embedder
    # Query vector database
    # Call language model if needed
    return BaseChatResponse(answer='Hei fra chatbot!', source=None)
