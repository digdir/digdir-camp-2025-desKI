from fastapi import APIRouter

from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse

router = APIRouter(tags=['Customer Support'])


@router.post('/', response_model=BaseChatResponse)
def ask_customer_support(req: BaseChatRequest):
    # kalle på embedder

    # kalle på vektordb

    ##kalle på LLM?
    return BaseChatResponse(answer='Hei fra customersupport!', source=None)
