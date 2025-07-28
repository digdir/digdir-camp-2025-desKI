import os
import base64

import requests
from dotenv import load_dotenv

"""
A service for extracting text or descriptions from images using Azure OpenAI's Vision capabilities.

This service takes an image file (e.g., a screenshot), encodes it in base64, and sends it to a deployed Azure OpenAI model 
via the chat completions endpoint. The model analyzes the image and returns a text response, which can be either a caption 
or a description of what's visible or written in the image.
"""

load_dotenv()

AZURE_API_KEY = os.getenv('AZURE_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
AZURE_MODEL = os.getenv('AZURE_MODEL')
AZURE_API_VERSION = os.getenv('AZURE_API_VERSION', '2024-05-01-preview')


def generate(image_path: str) -> str:
    with open(image_path, 'rb') as f:
        b64_image = base64.b64encode(f.read()).decode('utf-8')

    url = f'{AZURE_ENDPOINT}/openai/deployments/{AZURE_MODEL}/chat/completions?api-version={AZURE_API_VERSION}'

    headers = {
        'Content-Type': 'application/json',
        'api-key': AZURE_API_KEY,
    }

    payload = {
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {'url': f'data:image/png;base64,{b64_image}'},
                    },
                    {'type': 'text', 'text': 'Hva står det i bildet?'},
                ],
            }
        ],
        'temperature': 0.7,
        'top_p': 1,
        'max_tokens': 500,
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(response.text)

    try:
        content = response.json()['choices'][0]['message']['content']
        return content
    except Exception as parse_error:
        raise Exception(
            f'Klarte ikke å hente tekst fra svar: {parse_error}\nFull respons: {response.text}'
        ) from parse_error
