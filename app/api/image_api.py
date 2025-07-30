import shutil
from typing import Optional
from pathlib import Path

from fastapi import File, Form, Depends, APIRouter, UploadFile, HTTPException

from app.models.endpoint_enum import NamedEndpoint
from app.dependencies.services import get_query_service
from app.models.response_models import StrictChatResponse
from app.services.query_service import QueryService

router = APIRouter(tags=['Image'])

UPLOAD_DIR = Path('uploaded_images')
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post('/', response_model=StrictChatResponse)
async def ask_from_image(
    file: UploadFile = File(...),  # noqa: B008
    question: Optional[str] = Form(None),
    qs: QueryService = Depends(get_query_service),
):
    if file is None:
        raise HTTPException(status_code=422, detail='Du må sende inn et bilde.')

    file_path = None

    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        response, docs = qs.run_image_query(
            str(file_path), user_input=question, named_endpoint=NamedEndpoint.IMAGE
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f'Feil under bildebehandling: {e}'
        ) from e

    finally:
        if file_path and file_path.exists():
            file_path.unlink()

    return StrictChatResponse(
        answer=response,
        source='\n\n'.join([doc.page_content for doc in docs]) if docs else '',
    )
