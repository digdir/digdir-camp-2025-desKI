from app.config import (
    TOP_P,
    USE_AZURE,
    MAX_LENGTH,
    AZURE_MODEL,
    CHROMA_PATH,
    TEMPERATURE,
    AZURE_ENDPOINT,
    MAX_NEW_TOKENS,
    FINETUNED_MODEL_API_MAP,
)
from app.services.llm_service import LLMService
from app.services.query_service import QueryService
from app.services.chroma_service import ChromaService
from app.services.caption_service import CaptionService
from app.services.embedding_service import EmbeddingService

# Global shared instances
chroma_service: ChromaService = None
embedding_service: EmbeddingService = None
llm_service: LLMService = None
query_service: QueryService = None
caption_service: CaptionService = None


def init_services():
    global chroma_service, embedding_service, llm_service, query_service

    chroma_service = ChromaService(
        persist_directory=CHROMA_PATH, collection_name='dig_docs'
    )
    embedding_service = EmbeddingService(model_name='intfloat/multilingual-e5-base')
    llm_service = LLMService(
        llm_model_name=AZURE_MODEL,
        max_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        max_length=MAX_LENGTH,
        top_p=TOP_P,
        azure_endpoint=AZURE_ENDPOINT,
        named_endpoint=None,
        use_azure=USE_AZURE,
        finetuned_api_url=FINETUNED_MODEL_API_MAP,
    )
    caption_service = CaptionService(
        llm_service=llm_service, embedding_service=embedding_service
    )

    query_service = QueryService(
        chroma_service=chroma_service,
        embedding_service=embedding_service,
        llm_service=llm_service,
        caption_service=caption_service,
    )


def get_query_service() -> QueryService:
    return query_service


def get_chroma_service() -> ChromaService:
    return chroma_service


def get_embedding_service() -> EmbeddingService:
    return embedding_service


def get_llm_service() -> LLMService:
    return llm_service


def get_caption_service() -> CaptionService:
    return caption_service
