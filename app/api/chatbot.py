from fastapi import APIRouter

from app.models.endpoint_enum import NamedEndpoint
from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse
from app.services.query_service import QueryService

router = APIRouter(tags=['Chatbot'])

'''
# Endpoint for handling chatbot queries
@router.post('/', response_model=BaseChatResponse)
def ask_chatbot(req: BaseChatRequest):
    qs = QueryService()
    #response = qs.run_query(req.question, NamedEndpoint.CHATBOT)
    response = qs.run_query(user_query=req.question, named_endpoint=NamedEndpoint.CHATBOT)


    return BaseChatResponse(answer=response or 'Hei fra chatbot!', source=None)
'''


#endret litt bare for å teste litt, versjonen over kan brukes når vi skal bruke den "på ekte"
@router.post('/', response_model=BaseChatResponse)
def ask_chatbot(req: BaseChatRequest):
    use_azure = True  # eller False hvis du vil teste den andre

    qs = QueryService(use_azure=use_azure)
    response = qs.run_query(user_query=req.question, named_endpoint=NamedEndpoint.CHATBOT)
    return BaseChatResponse(answer=response or 'Hei fra chatbot!', source=None)
