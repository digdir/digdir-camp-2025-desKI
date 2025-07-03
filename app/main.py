from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError

from app.exceptions import (
    validation_exception_handler,
    pydantic_validation_exception_handler,
)
from app.api.chatbot import router as chatbot
from app.api.copilot import router as copilot
from app.api.servicedesk import router as servicedesk
from app.api.customersupport import router as customersupport
from app.services.chroma_service import ChromaService

# Create the FastAPI application
app = FastAPI()
# Initialize chromaservice to download and cache embedder model
chroma_service = ChromaService()

# Include routers with their prefixes
app.include_router(customersupport, prefix='/customersupport')
app.include_router(chatbot, prefix='/chatbot')
app.include_router(copilot, prefix='/copilot')
app.include_router(servicedesk, prefix='/servicedesk')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
