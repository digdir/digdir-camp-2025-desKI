import re
import shutil
import logging
from pathlib import Path

from fastapi import File, APIRouter, UploadFile, HTTPException

from app.models.endpoint_enum import NamedEndpoint
from app.services.llm_service import LLMService
from app.services.chroma_service import ChromaService
from app.services.caption_service import generate
from app.services.embedding_service import EmbeddingService


def strip_markdown(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # *italic*
    text = re.sub(r'`(.*?)`', r'\1', text)  # `code`
    text = re.sub(r'#+ ', '', text)  # # header
    text = re.sub(r'\n{3,}', '\n\n', text)  # ekstra mellomrom
    return text.strip()


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Defines the directory where uploaded images will be temporarily stored
UPLOAD_DIR = Path('uploaded_images')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

file_dependency = File(...)


# Endpoint to handle image upload, captioning, embedding, and response generation
@router.post('/upload-image/')
async def upload_image(file: UploadFile = file_dependency):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='Only image files are allowed')

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        caption = generate(str(file_path))

        embedder = EmbeddingService()
        embedding = embedder.embed(caption)

        chroma = ChromaService()
        docs = chroma.search_by_embedding(embedding)

        chroma.store_embedding(
            caption, embedding, metadata={'filename': file.filename, 'caption': caption}
        )

        for i, doc in enumerate(docs, 1):
            logger.info(f'Doc {i}: {doc}')

        try:
            llm = LLMService()
            retrieved_context = '\n'.join([doc.page_content for doc in docs])
            chatbot_reply = llm.generate_response(
                user_query=caption,
                retrieved_context=retrieved_context,
                named_endpoint=NamedEndpoint.IMAGE,
            )

        except Exception as llm_error:
            raise HTTPException(
                status_code=500, detail=f'LLM-feil: {llm_error}'
            ) from llm_error

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        file_path.unlink()

    clean_reply = strip_markdown(chatbot_reply)

    return {'response': clean_reply, 'used_documents': docs}
