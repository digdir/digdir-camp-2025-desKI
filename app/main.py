from fastapi import FastAPI
from app.api.customersupport import router as customersupport
from app.api.chatbot import router as chatbot
from app.api.copilot import router as copilot
from app.api.servicedesk import router as servicedesk
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.exceptions import validation_exception_handler, pydantic_validation_exception_handler

app = FastAPI()

app.include_router(customersupport, prefix="/customersupport")
app.include_router(chatbot, prefix="/chatbot")
app.include_router(copilot, prefix="/copilot")
app.include_router(servicedesk, prefix="/servicedesk")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
