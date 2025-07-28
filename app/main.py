from fastapi import FastAPI
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api import upload_api
from app.exceptions import (
    validation_exception_handler,
    pydantic_validation_exception_handler,
)
from app.api.chatbot import router as chatbot
from app.api.copilot import router as copilot
from app.api.servicedesk import router as servicedesk
from app.dependencies.services import init_services

app = FastAPI()


@app.on_event('startup')
def startup_event():
    init_services()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)

# Include routers
app.include_router(chatbot, prefix='/chatbot')
app.include_router(copilot, prefix='/copilot')
app.include_router(servicedesk, prefix='/servicedesk')
app.include_router(upload_api.router, prefix='/api')

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
