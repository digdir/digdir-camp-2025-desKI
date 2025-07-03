from fastapi import APIRouter

from app.models.request_models import BaseChatRequest
from app.models.response_models import BaseChatResponse

router = APIRouter(tags=['Copilot'])

@router.post('/', response_model=BaseChatResponse)
def ask_copilot(req: BaseChatRequest):
    # Extract context data if available
    context = getattr(req, 'context', None) or {}
    client_info = context.get('client', {})
    available_scopes = context.get('availableScopes', {})

    # Build context-aware response
    if client_info.get('client_name'):
        answer = (
            f"Hello! I can help you with client '{client_info.get('client_name')}'. "
            f"This client has {len(client_info.get('scopes', []))} scopes, "
            f"{context.get('jwkCount', 0)} JWK keys, and {context.get('onBehalfOfCount', 0)} OnBehalfOf configurations. "
            f"Available scopes: {available_scopes.get('accessibleForAll', 0)} accessible for all, "
            f"{available_scopes.get('withDelegationSource', 0)} with delegation source, "
            f"{available_scopes.get('availableToOrganization', 0)} available to organization. "
            f"Question: {req.question}"
        )
    else:
        answer = f'Hello from DesKI Copilot! I can help you with client management. Question: {req.question}'

    return BaseChatResponse(answer=answer, source='DesKI Copilot')