import logging
import os
from dotenv import load_dotenv

from app.config import AZURE_MODEL, CHROMA_PATH, AZURE_ENDPOINT, COLLECTION_NAME, MAX_LENGTH, TEMPERATURE, MAX_NEW_TOKENS, TOP_P, FINETUNED_MODEL_API
from app.models.endpoint_enum import NamedEndpoint
from app.services.llm_service_azure import LLMService
from app.services.chroma_service import ChromaService
from app.services.embedding_service import EmbeddingService



load_dotenv()

USE_AZURE = os.getenv("USE_AZURE", "true").lower() == "true"

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more detail
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)


class QueryService:
    """
    A One-stop-interface combining EmbeddingService, ChromaService and LLMService to make handling user queries simple.

    This service initializes the embedding model, connects to ChromaDB, retrieves relevant document chunks,
    and sends a prompt to an LLM model to generate a response based on the retrieved context.
    All services have default parameters, so you can use this service without any arguments.
    You can also pass a custom model name to use a different embedding model.

    Attributes:
    -----------
        embedding_service (EmbeddingService): Service for generating text embeddings.
        chroma_service (ChromaService): Service for interacting with ChromaDB.
        LLMService (LLMService): Service for generating responses from a language model.

    Methods:
    --------
        run_query(user_query: str, limit: int = 5) -> str:
            Runs a query against the ChromaDB, retrieves relevant document chunks and runs this query to an LLM.

    Usage:
    ------
        from app.services.query_service import QueryService
        from app.models.endpoint_enum import NamedEndpoint (OPTIONAL)
        qs = QueryService()
        answer = qs.run_query("Hva tilbyr Digdir?", NamedEndpoint.CHATBOT (OPTIONAL)  )
        print(answer)
    """

    def __init__(
        self,
        embedder_model_name: str = 'intfloat/multilingual-e5-base',
        chroma_path: str = CHROMA_PATH,
        chroma_collection: str = COLLECTION_NAME,
        llm_model_name: str = AZURE_MODEL,
        max_tokens: int = MAX_NEW_TOKENS,
        temperature: float = TEMPERATURE,
        max_length: int = MAX_LENGTH,
        top_p: int = TOP_P,
        azure_endpoint: str = AZURE_ENDPOINT,
        named_endpoint: NamedEndpoint = NamedEndpoint.DEFAULT,
        finetuned_api_url: str = FINETUNED_MODEL_API,
        use_azure: bool = USE_AZURE

    ):


        """
        Initializes the QueryService by loading environment variables and setting up the embedding model and ChromaDB.

        Args:
            embedder_model_name (str): Optional; the name of the embedding model to use.
            chroma_path (str): Optional; the path to the ChromaDB directory. Defaults to "app/db/chroma_db".
            chroma_collection (str): Optional; the name of the collection in the ChromaDB. Defaults to "dig_docs".
            llm_model_name (str): Optional; the name of the language model to use. Defaults to the value in the environment variable 'AZURE_MODEL'.
            max_tokens (int): Optional; the maximum number of tokens to generate in the response. Defaults to 1024.
            temperature (float): Optional; the sampling temperature to use for response generation. Defaults to 0.7.
            azure_endpoint (str): Optional; the Azure endpoint for the AI model. Defaults to the value in the environment variable 'AZURE_ENDPOINT'.
            named_endpoint (NamedEndpoint): Optional; enum that tells the PromptFactory which prompt to use.
        """

        # Use azure model if True, else use finetuned
        self.use_azure = use_azure

        # Initialize the embedding model
        self.embedding_service = EmbeddingService(model_name=embedder_model_name)
        self.embedding_model = self.embedding_service.get_model()

        self.named_endpoint = named_endpoint or NamedEndpoint.DEFAULT

        # Connect to local ChromaDB
        self.chroma_service = ChromaService(
            embedding_model=self.embedding_model,
            persist_directory=chroma_path,
            collection_name=chroma_collection,
        )

        # Initialize the LLMService
        self.llm_service = LLMService(
            model_name=llm_model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            max_length=max_length,
            top_p=top_p,
            azure_endpoint=azure_endpoint,
            named_endpoint=named_endpoint,
            use_azure=use_azure,
            finetuned_api_url=finetuned_api_url
        )

    def run_query(
        self, user_query: str, limit: int = 5, named_endpoint: NamedEndpoint = None
    ) -> str:
        """
        Runs a query against the ChromaDB, retrieves relevant document chunks and runs this query to an LLM.

        Args:
            user_query (str): The user's query.
            limit (int): The maximum number of document chunks to retrieve from the ChromaDB. Defaults to 5.
            named_endpoint (NamedEndpoint): Enum that selects the preset prompt to be used.

        Returns:
            str: The response from the language model based on the retrieved context.
            Returns a predefined error message if an exception occurs during the retrieval or response generation.
        """

        # TODO: Add optional log-search-functionality


        named_endpoint = named_endpoint or self.named_endpoint

        try:
            # retriveds context from vector db
            retrieved_context = self.chroma_service.search(query=user_query, limit=limit)
            logger.info(f"retrieved {len(retrieved_context)} context chunks")
            

        except Exception as e:
            logger.error(f"Error retrieving the context from ChromaDB: {e}")
            return "An error occured while retrieving documents"


        try:
            #return self.llm_service.generate_response(user_query, retrieved_context, named_endpoint)
            context_str = "\n\n".join(retrieved_context)
            return self.llm_service.generate_response(user_query, context_str, named_endpoint)

        except Exception as e:
            logger.error(f" Error generating response from LLM {e}")
            return "An error occured while generating the response"