# app/exceptions.py

import logging

from fastapi import Request
from pydantic import ValidationError as PydanticValidationError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.utils.desensitize import remove_sensitive_data

logger = logging.getLogger('uvicorn.error')


# Handle validation errors from FastAPI request parsing
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Read and sanitize the raw request body
    raw = await request.body()
    sanitized = remove_sensitive_data(raw.decode('utf-8', errors='ignore'))

    # First, check if this is a simple ValueError from a field validator
    for err in exc.errors():
        if err.get('type') == 'value_error':
            return JSONResponse(
                status_code=422,
                content={'detail': err['msg']},
            )

    # Otherwise, build a JSON-friendly error list
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


# Handle validation errors raised by Pydantic models directly
async def pydantic_validation_exception_handler(
    request: Request, exc: PydanticValidationError
):
    # Read and sanitize the raw request body
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
