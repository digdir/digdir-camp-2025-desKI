from fastapi import APIRouter

from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse

router = APIRouter(tags=['Customer Support'])

# Endpoint for handling customer support queries
@router.post('/', response_model=BaseChatResponse)
def ask_customer_support(req: BaseChatRequest):
    # Call embedder
    # Query vector database
    # Call language model if needed
    return BaseChatResponse(answer='Hei fra customersupport!', source=None)
