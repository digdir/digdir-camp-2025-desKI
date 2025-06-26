from fastapi import APIRouter

from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse

router = APIRouter(tags=['Copilot'])


@router.post('/', response_model=BaseChatResponse)
def ask_copilot(req: BaseChatRequest):
    # kalle på embedder

    # ta med ekstrakontekst fra nettsiden

    ##kalle på LLM?
    return BaseChatResponse(answer='Hei! fra copiliot', source=None)
