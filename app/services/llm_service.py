import os
import logging

from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import UserMessage, SystemMessage

logger = logging.getLogger(__name__)


# Generates a dummy answer from the language model
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

        self.azure_endpoint = azure_endpoint or os.getenv('AZURE_ENDPOINT')
        self.azure_api_key = os.getenv('AZURE_API_KEY')
        self.model_name = model_name or os.getenv('AZURE_MODEL')

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
        Dokumentasjon: {retrieved_context}
    
        Spørsmål: {user_query}
        Svar:
        """

        if not user_query.strip():
            logger.warning('Empty user query provided.')
            return 'Please provide a valid question.'
        
        try:
            response = self.client.complete(
                messages=[
                    SystemMessage(
                        content="""Du er en hjelpsom DigDir-assistent. Du svarer på spørsmål basert på denne dokumentasjonen og ingenting annet.
                        Svar på norsk om spørsmålet er på norsk, svar på engelsk om svaret er på engelsk. Om du ikke vet svaret, skriv: "Eg hakje peiling".
                        Svar konsist, men med relevante detaljer fra kildene. Ikke gjett. Ikke legg til informasjon som ikke står i dokumentasjonen.
                        Du er en chatbot som skal svare presist og effektivt, ikkje noe "jeg" eller "hmm"."""
                    ),
                    UserMessage(content=prompt),
                ],
                model=self.azure_model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        except Exception as e:
            logger.error(f'Error generating response: {e}')
            return 'There was an error generating the response. Please try again later.'

        return response.choices[0].message.content

        # TODO: Add support for self-created models