import os
import logging
import re

from app.config import AZURE_ENDPOINT, AZURE_MODEL
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import UserMessage, SystemMessage

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more detail
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)


class LLMService:
    """
    A service for interacting with a language model to generate responses based on user queries.

    This service initializes the embedding model, connects to ChromaDB, retrieves relevant document chunks,
    and sends a prompt to an Azure AI model to generate a response based on the retrieved context.

    Attributes:
    -----------
        model_name (str): The name of the language model to use. Defaults to the value in the environment variable 'AZURE_MODEL'.
        max_tokens (int): The maximum number of tokens to generate in the response. Defaults to 1024.
        temperature (float): The sampling temperature to use for response generation. Defaults to 0.7.
        azure_endpoint (str): The Azure endpoint for the AI model. Defaults to the value in the environment variable 'AZURE_ENDPOINT'.

    Methods:
    --------
        generate_response_azure(user_query: str, retrieved_context: dict) -> str:
            Generates a response from the language model based on the user's query and retrieved context.

    Usage:
    ------
        from app.services.llm_service import LLMService
        llm = LLMService()
        response = llm.generate_response("Hva er Digdir?", "Noe dokumentasjon her")
        print(response)
    """

    def __init__(
        self,
        model_name: str = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        azure_endpoint: str = None,
    ):
        """
        Initializes the LLMService by loading environment variables and setting up the embedding model and ChromaDB.

        Args:
            model_name (str): Optional; the name of the embedding model to use. Defaults to the value in the environment variable 'AZURE_MODEL'.
            max_tokens (int): The maximum number of tokens to generate in the response. Defaults to 1024.
            temperature (float): The sampling temperature to use for response generation. Defaults to 0.7.
            azure_endpoint (str): Optional; the Azure endpoint for the AI model. Defaults to the value in the environment variable 'AZURE_ENDPOINT'.
        """
        # Load environment variables from .env file
        load_dotenv()

        self.azure_endpoint = azure_endpoint or AZURE_ENDPOINT
        self.azure_api_key = os.getenv('AZURE_API_KEY')
        self.model_name = model_name or AZURE_MODEL

        self.client = ChatCompletionsClient(
            endpoint=self.azure_endpoint,
            credential=AzureKeyCredential(self.azure_api_key),
            api_version='2024-05-01-preview',
        )

        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_response_azure(self, user_query: str, retrieved_context: dict) -> str:
        """
        Generates a response from the language model based on the user's query and retrieved context.

        Args:
            user_query (str): The user's query.
            retrieved_context (str): The context retrieved from the document chunks.

        Returns:
            str: The response from the language model based on the retrieved context.
        """

        prompt = f"""
        Du er en hjelpsom DigDir-assistent. Du svarer på spørsmål basert på denne dokumentasjonen, men dersom digdir sin dokumentasjon er tom må du være hyggelig å si at du ikke vet.
                        Svar på norsk om spørsmålet er på norsk, svar på engelsk om svaret er på engelsk.
                        Svar konsist, men med relevante detaljer fra kildene. Ikke gjett. Dersom det ikke står noe i dokumentasjonen kan du prøve fritt.
                        Vær hyggelig og serviceinnstillt. Dersom løsningen krever en handling fra Digdir, si at en av de ansatte må fikse det.
        
        Digdir-dokumentasjon: {retrieved_context}
    
        Spørsmål: {user_query}
        Svar:
        """

        if not user_query.strip():
            logger.warning('Empty user query provided.')
            return 'Please provide a valid question.'

        try:
            response = self.client.complete(
                messages=[
                    SystemMessage(content="""Du er en hjelpsom DigDir-assistent. Skriv svaret i klartekst, ikke noe \n eller markdown syntaks."""),
                    UserMessage(content=prompt),
                ],
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        except Exception as e:
            logger.error(f'Error generating response: {e}')
            return 'There was an error generating the response. Please try again later.'
        if "deepseek" in self.model_name.lower() and "r1" in self.model_name.lower():
            return re.sub(r"<think>.*?</think>\n?", "", response.choices[0].message.content, flags=re.DOTALL)
        return response.choices[0].message.content

        # TODO: Add support for self-created models
