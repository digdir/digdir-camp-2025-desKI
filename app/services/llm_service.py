import os
import re
import logging
from typing import Any, Optional

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from azure.ai.inference import ChatCompletionsClient
from urllib3.util.retry import Retry
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import UserMessage, SystemMessage
from azure.core.pipeline.policies import RetryPolicy

from app.config import (
    TOP_P,
    USE_AZURE,
    MAX_LENGTH,
    AZURE_MODEL,
    TEMPERATURE,
    AZURE_ENDPOINT,
    MAX_NEW_TOKENS,
    FINETUNED_MODEL_API,
)
from app.models.endpoint_enum import NamedEndpoint
from app.utils.prompt_factory import PromptFactory

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more detail
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)


class LLMService:
    """
    A service for interacting with a language model to generate responses based on user queries.

    This service initializes the embedding model, connects to ChromaDB, retrieves relevant document chunks,
    and sends a prompt to an Azure AI model to generate a response based on the retrieved retrieved_context.

    Methods:
    --------
        generate_response_azure(user_query: str, retrieved_context: dict) -> str:
            Generates a response from the language model based on the user's query and retrieved retrieved_context.

    Usage:
    ------
        from app.services.llm_service import LLMService
        llm = LLMService()
        response = llm.generate_response("Hva er Digdir?", "Noe dokumentasjon her")
        print(response)
    """

    def __init__(
        self,
        llm_model_name: str = AZURE_MODEL,
        max_tokens: int = MAX_NEW_TOKENS,
        temperature: float = TEMPERATURE,
        max_length: int = MAX_LENGTH,
        top_p: float = TOP_P,
        azure_endpoint: str = AZURE_ENDPOINT,
        named_endpoint: NamedEndpoint = NamedEndpoint.DEFAULT,
        use_azure: bool = USE_AZURE,
        finetuned_api_url: str = FINETUNED_MODEL_API,
    ):
        """
        Initializes the LLMService by loading environment variables and setting up the embedding model and ChromaDB.

        Args:
            llm_model_name  (str): Optional; the name of the embedding model to use. Defaults to the value in the environment variable 'AZURE_MODEL'.
            max_tokens (int): The maximum number of tokens to generate in the response. Defaults to 1024.
            temperature (float): The sampling temperature to use for response generation. Defaults to 0.7.
            max_length (int): The maximum length of the input text. Defaults to 2048.
            top_p (float): The top-p sampling parameter for response generation. Defaults to 0
            azure_endpoint (str): Optional; the Azure endpoint for the AI model. Defaults to the value in the environment variable 'AZURE_ENDPOINT'.
            named_endpoint (NamedEndpoint): Optional; the named endpoint to use for the LLM service. Defaults to NamedEndpoint.DEFAULT.
            use_azure (bool): Optional; whether to use Azure for LLM generation. Defaults to True.
            finetuned_api_url (str): Optional; the URL for the finetuned model API. Defaults to the value in the environment variable 'FINETUNED_MODEL_API'.

        """
        self.use_azure = use_azure
        self.llm_model_name = llm_model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_length = max_length
        self.top_p = top_p
        self.named_endpoint = named_endpoint

        if self.use_azure:
            self.azure_endpoint = azure_endpoint
            self.azure_api_key = os.getenv('AZURE_API_KEY')

            retry_policy = RetryPolicy()
            retry_policy.total_retries = 3
            retry_policy.connect_retries = 2
            retry_policy.read_retries = 2
            retry_policy.status_retries = 2
            retry_policy.backoff_factor = 0.5

            self.client = ChatCompletionsClient(
                endpoint=self.azure_endpoint,
                credential=AzureKeyCredential(self.azure_api_key),
                api_version='2024-05-01-preview',
                retry_policy=retry_policy,
            )
        else:
            self.finetuned_api_url = finetuned_api_url

    def generate_response(
        self,
        user_query: str,
        retrieved_context: dict,
        named_endpoint: NamedEndpoint = None,
        previous: Optional[list[str]] = None,
        faq_str: str = None,
        external_context: Optional[dict[str, Any]] = None,
        logs: Optional[str] = None,
    ) -> str:
        """
        Generic interface: picks Azure or finetuned backend based on config.
        """
        if self.use_azure:
            return self.generate_response_azure(
                user_query,
                retrieved_context,
                named_endpoint,
                previous,
                faq_str,
                external_context,
                logs,
            )
        else:
            return self.generate_response_finetuned(
                user_query,
                retrieved_context,
                named_endpoint,
                previous,
                faq_str,
                external_context,
                logs,
            )

    def generate_response_azure(
        self,
        user_query: str,
        retrieved_context: str,
        named_endpoint: NamedEndpoint = None,
        previous: Optional[list[str]] = None,
        faq_str: str = None,
        external_context: Optional[dict[str, Any]] = None,
        logs: Optional[str] = None,
    ) -> str:
        """
        Uses Azure model to generate response.
        """
        if not user_query.strip():
            logger.warning('Empty user query provided')
            return 'Please provide a valid question'

        logger.info(f'User info: {external_context}')
        logger.info(f'User query: {user_query}')

        prompt = PromptFactory.get_prompt(
            user_query,
            retrieved_context,
            named_endpoint,
            previous,
            faq_str,
            external_context,
            logs,
        )

        system_prompt = PromptFactory.get_system_message(
            named_endpoint or self.named_endpoint
        )
        logger.info('System prompt used: %s', system_prompt)
        logger.info(f'Generated prompt: {prompt}')

        try:
            response = self.client.complete(
                messages=[
                    SystemMessage(content=system_prompt),
                    UserMessage(content=prompt),
                ],
                model=self.llm_model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        except Exception as e:
            logger.error(f'Error generating response (Azure): {e}')
            return 'Azure model error'

        # Deepseek models include <think> tags in output – remove them
        if (
            'deepseek' in self.llm_model_name.lower()
            and 'r1' in self.llm_model_name.lower()
        ):
            return re.sub(
                r'<think>.*?</think>\n?',
                '',
                response.choices[0].message.content,
                flags=re.DOTALL,
            )

        return response.choices[0].message.content

    def generate_response_finetuned(
        self,
        user_query: str,
        retrieved_context: str,
        named_endpoint: NamedEndpoint = None,
        previous: Optional[list[str]] = None,
        faq_str: str = None,
        external_context: Optional[dict[str, Any]] = None,
        logs: Optional[str] = None,
    ) -> str:
        """
        Uses finetuned HTTP endpoint to get a response.
        """
        if not user_query.strip():
            logger.warning('Empty user query provided')
            return 'Please provide a valid question'

        prompt = PromptFactory.get_prompt(
            user_query,
            retrieved_context,
            named_endpoint or self.named_endpoint,
            previous,
            faq_str,
            external_context,
            logs,
        )

        logger.info(f'User info: {external_context}')
        logger.info(f'User Endpoint: {named_endpoint}')
        logger.info(f'Generated prompt (first 500 chars): {prompt}')

        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=['POST'],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        try:
            response = session.post(
                self.finetuned_api_url, json={'prompt': prompt}, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('response', '[No response]')
        except Exception as e:
            logger.error(f'Error generating response (finetuned): {e}')
            return 'Finetuned-model error'

    def clean_query(self, query: str) -> str:
        """
        Sends the user query to Azure to clean up formatting and remove noise.
        """
        logger.info(f'Cleaning query: {query}')
        try:
            response = self.client.complete(
                messages=[
                    SystemMessage(
                        content='Please clean the query by extracting the actual question that the user needs help with, and only that. Remove any unnecessary characters or formatting. Only return the cleaned query without any additional text or formatting. Respond in Norwegian, Bokmål. Do not return any other text.'
                    ),
                    UserMessage(content=query),
                ],
                model=self.llm_model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        except Exception as e:
            logger.error(f'Error generating response (Azure): {e}')
            return 'Azure model error'

        logger.info(f'Cleaned query: {response.choices[0].message.content}')
        return response.choices[0].message.content
