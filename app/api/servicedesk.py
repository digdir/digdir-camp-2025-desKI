from fastapi import APIRouter
from app.models.request_models import StrictChatRequest
from app.models.response_models import StrictChatResponse

router = APIRouter(
    tags=["Service desk"]
    )

@router.post("/", response_model=StrictChatResponse)
def ask_service_desk(req: StrictChatRequest):
      #kalle på embedder

    #kalle på vektordb

    ##kalle på LLM?
    return StrictChatResponse(answer="Hei fra servicedesk!", source=None)
