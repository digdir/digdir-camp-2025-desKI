import base64
import logging
from typing import Optional
import os, base64, logging, requests
from dotenv import load_dotenv; load_dotenv()

import requests

from app.config import (
    AZURE_MODEL,
    AZURE_ENDPOINT_IMAGE,
    AZURE_API_VERSION_IMAGE,
)

from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService

load_dotenv()  
logger = logging.getLogger(__name__)

AZURE_API_KEY_IMAGE = os.getenv("AZURE_API_KEY_IMAGE")

class CaptionService:
    """
    Service for extracting text from images using Azure OpenAI Vision.

    Usage:
        captioner = CaptionService()
        text = captioner.generate("path/to/image.png")
    """

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        api_key: str = AZURE_API_KEY_IMAGE,
        endpoint: str = AZURE_ENDPOINT_IMAGE,
        model: str = AZURE_MODEL,
        api_version: str = AZURE_API_VERSION_IMAGE,
    ):
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
        self.api_version = api_version

        if not all([self.api_key, self.endpoint, self.model, self.api_version]):
            raise ValueError('Azure API credentials and model config must be set')

    def generate(self, image_path: str, prompt_text: str = 'Hva er problemet?') -> str:
        try:
            with open(image_path, 'rb') as f:
                b64_image = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f'Kunne ikke lese bilde: {e}') from e

        url = f'{self.endpoint}/openai/deployments/{self.model}/chat/completions?api-version={self.api_version}'

        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
        }

        payload = {
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt_text},
                        {
                            'type': 'image_url',
                            'image_url': {'url': f'data:image/png;base64,{b64_image}'},
                        },
                    ],
                }
            ],
            'temperature': 0.7,
            'top_p': 1,
            'max_tokens': 500,
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f'Azure API-feil {response.status_code}: {response.text}')

        try:
            return response.json()['choices'][0]['message']['content']
        except Exception as parse_error:
            raise Exception(
                f'Klarte ikke å hente tekst fra svar: {parse_error}\nFull respons: {response.text}'
            ) from parse_error
