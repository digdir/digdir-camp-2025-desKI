from app.services.chroma_service import ChromaService
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.query_service import QueryService

from app.config import (
    CHROMA_PATH,
    AZURE_MODEL,
    MAX_LENGTH,
    TOP_P,
    TEMPERATURE,
    MAX_NEW_TOKENS,
    AZURE_ENDPOINT,
    FINETUNED_MODEL_API,
    USE_AZURE
)

# Global shared instances
chroma_service: ChromaService = None
embedding_service: EmbeddingService = None
llm_service: LLMService = None
query_service: QueryService = None

def init_services():
    global chroma_service, embedding_service, llm_service, query_service

    chroma_service = ChromaService(persist_directory=CHROMA_PATH, collection_name="dig_docs")
    embedding_service = EmbeddingService(model_name="intfloat/multilingual-e5-base")
    llm_service = LLMService(
        llm_model_name=AZURE_MODEL,
        max_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        max_length=MAX_LENGTH,
        top_p=TOP_P,
        azure_endpoint=AZURE_ENDPOINT,
        named_endpoint=None,
        use_azure=USE_AZURE,
        finetuned_api_url=FINETUNED_MODEL_API,
    )

    query_service = QueryService(
        chroma_service=chroma_service,
        embedding_service=embedding_service,
        llm_service=llm_service
    )

def get_query_service() -> QueryService:
    return query_service
def get_chroma_service() -> ChromaService:
    return chroma_service
def get_embedding_service() -> EmbeddingService:
    return embedding_service