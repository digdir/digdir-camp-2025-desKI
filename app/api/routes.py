from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


# Enkle dummy-modeller
class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post('/', response_model=ChatResponse)
def chat(req: ChatRequest):
    # Bare returner et statisk svar for testing
    return ChatResponse(
        answer=f"Ditt spørsmål var: '{req.question}'. Dette er et dummy-svar."
    )
