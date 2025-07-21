from app.config import CHROMA_PATH
from app.services.chroma_service import ChromaService

chroma: ChromaService = None


def init_chroma():
    global chroma
    chroma = ChromaService(
        persist_directory=CHROMA_PATH,
        collection_name='dig_docs',
    )


def get_chroma_service() -> ChromaService:
    return chroma
