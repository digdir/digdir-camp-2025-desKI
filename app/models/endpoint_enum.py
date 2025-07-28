from enum import Enum

"""
An enumeration of supported endpoint types used by the QueryService and LLMService.

This allows the application to easily switch behavior based on which
logical service is invoking the model — such as a chatbot for citizens,
an internal copilot for Digdir employees, or a servicedesk tool for external clients.

Why use this:
-------------
- Prevents hardcoding strings across the codebase.
- Enables prompt customization per endpoint (via `PromptFactory` or similar).
- Improves type safety and clarity in service logic and routing.
- Makes future expansion trivial (e.g., adding `RESEARCH`, `DEVTOOLS`, etc.).

Example:
--------
from app.models.endpoint_enum import NamedEndpoint
from app.services.llm_service import LLMService

llm = LLMService(named_endpoint=NamedEndpoint.COPILOT)
response = llm.generate_response_azure("Hva er status på prosjektet?", retrieved_context)
"""


class NamedEndpoint(str, Enum):
    CHATBOT = 'chatbot'
    COPILOT = 'copilot'
    SERVICEDESK = 'servicedesk'
    DEFAULT = 'chatbot'
    IMAGE = 'IMAGE'
