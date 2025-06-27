# app/exceptions.py

import logging

from fastapi import Request
from pydantic import ValidationError as PydanticValidationError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.utils.desensitize import remove_sensitive_data

logger = logging.getLogger('uvicorn.error')


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raw = await request.body()
    sanitized = remove_sensitive_data(raw.decode('utf-8', errors='ignore'))

    # Først sjekk om vi har en enkel ValueError fra felt-validator:
    for err in exc.errors():
        if err.get('type') == 'value_error':
            return JSONResponse(
                status_code=422,
                content={'detail': err['msg']},
            )

    # Ellers bygg en JSON-vennlig errors-liste:
    formatted = []
    for err in exc.errors():
        fe = {'type': err['type'], 'loc': err['loc'], 'msg': err['msg']}
        if 'ctx' in err:
            fe['ctx'] = {k: str(v) for k, v in err['ctx'].items()}
        formatted.append(fe)

    logger.warning(f'[422] Validation failed: {formatted} – body: {sanitized}')
    return JSONResponse(
        status_code=422,
        content={
            'detail': 'Ugyldig forespørsel. Validering feilet.',
            'errors': formatted,
        },
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: PydanticValidationError
):
    raw = await request.body()
    sanitized = remove_sensitive_data(raw.decode('utf-8', errors='ignore'))

    logger.warning(
        f'[422] Pydantic ValidationError: {exc.errors()} – body: {sanitized}'
    )
    return JSONResponse(
        status_code=422,
        content={
            'detail': 'Ugyldig data i modellen. Validering feilet.',
            'errors': [{'loc': e.loc_tuple(), 'msg': e.msg} for e in exc.raw_errors],
        },
    )
