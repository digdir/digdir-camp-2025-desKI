from fastapi import APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.models.request_models import StrictChatRequest
from app.models.response_models import StrictChatResponse
from app.services.chroma_service import ChromaService
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.query_service import QueryService

router = APIRouter(tags=['Service desk'])


@router.post('/', response_model=StrictChatResponse)
def ask_service_desk(req: StrictChatRequest) -> StrictChatResponse:
    query = req.question

    chroma = ChromaService()
    embedding = EmbeddingService()
    llm = LLMService()

    qs = QueryService(
        chroma_service=chroma,
        embedding_service=embedding,
        llm_service=llm,
    )

    response = qs.run_query(
        user_query=query,
        named_endpoint=NamedEndpoint.SERVICEDESK,
    )

    return StrictChatResponse(answer=response or 'Noe gikk galt', source=None)

