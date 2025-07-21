from fastapi import FastAPI
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.exceptions import (
    validation_exception_handler,
    pydantic_validation_exception_handler,
)
from app.api.chatbot import router as chatbot
from app.api.copilot import router as copilot
from app.api.servicedesk import router as servicedesk
from app.dependencies.chroma import init_chroma
from app.services.chroma_service import ChromaService

# Create the FastAPI application
app = FastAPI()
chroma: ChromaService  # type hint global instance


@app.on_event('startup')
def startup_event():
    global chroma
    chroma = init_chroma()


def get_chroma_service() -> ChromaService:
    return chroma


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],  # React app URL
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)

# Include routers with their prefixes
app.include_router(chatbot, prefix='/chatbot')
app.include_router(copilot, prefix='/copilot')
app.include_router(servicedesk, prefix='/servicedesk')

# Register custom exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
