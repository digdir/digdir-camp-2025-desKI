import logging
from typing import Any, Optional

from app.config import USE_AZURE, SIMILARITY_THRESHOLD
from app.models.endpoint_enum import NamedEndpoint
from app.services.llm_service import LLMService
from app.services.chroma_service import ChromaService
from app.services.embedding_service import EmbeddingService

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
        run_query(user_query: str, named_endpoint: NamedEndpoint, external_context: Optional[dict[str, Any]], limit: int = 5) -> str:
            Runs a query against the ChromaDB, retrieves relevant document chunks and runs this query to an LLM.

    Usage:
    ------
        from app.services.query_service import QueryService
        from app.models.endpoint_enum import NamedEndpoint (OPTIONAL)
        qs = QueryService()
        answer = qs.run_query("Hva tilbyr Digdir?", NamedEndpoint.BRUKERSTOTTE (OPTIONAL)  )
        print(answer)
    """

    def __init__(
        self,
        chroma_service: ChromaService,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
    ):
        """
        Initializes the QueryService by loading environment variables and setting up the embedding model and ChromaDB.

        Args:
            chroma_service (ChromaService): The service for interacting with ChromaDB.
            embedding_service (EmbeddingService): The service for generating text embeddings.
            llm_service (LLMService): The service for generating responses from a language model.
        """

        self.chroma_service = chroma_service
        self.embedding_service = embedding_service
        self.embedding_model = embedding_service.get_model()
        self.llm_service = llm_service
        self.use_azure = llm_service.use_azure

    def run_query(
        self,
        user_query: str,
        named_endpoint: NamedEndpoint = NamedEndpoint.DEFAULT,
        previous: Optional[list[str]] = None,
        external_context: Optional[dict[str, Any]] = None,
        logs: Optional[str] = None,
        limit: Optional[int] = None,
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

        if limit is None:
            limit = 10 if USE_AZURE else 3

        faq_str = ''
        try:
            retrieved_context = self._search_docs(
                user_query, limit, endpoint=named_endpoint
            )

            if named_endpoint == NamedEndpoint.SERVICEDESK:
                retrieved_faq = self._search_faq(
                    user_query, limit, endpoint=named_endpoint
                )
                logger.debug(f'Retrieved faq: {retrieved_faq}')
                faq_str = ''.join(retrieved_faq)

            logger.info(f'retrieved {len(retrieved_context)} context chars')
            logger.info(f'retrieved {len(faq_str)} faq chars')

        except Exception as e:
            logger.error(f'Error retrieving the context from ChromaDB: {e}')
            return 'An error occured while retrieving documents'

        try:
            return self.llm_service.generate_response(
                user_query,
                retrieved_context,
                named_endpoint,
                previous,
                faq_str,
                external_context,
                logs,
            )

        except Exception as e:
            logger.error(f' Error generating response from LLM {e}')
            return 'An error occured while generating the response'

    def _search_faq(
        self,
        user_query: str,
        limit: int = 5,
        endpoint: NamedEndpoint = NamedEndpoint.DEFAULT,
    ):
        if endpoint == NamedEndpoint.SERVICEDESK:
            collection = (
                'servicedesk_qna_clean' if self.use_azure else 'servicedesk_qna'
            )
            self.chroma_service.switch_collection(collection)
        else:
            logger.info(f'Ingen FAQ-collection definert for endpoint: {endpoint.name}')
            return []

        faq_matches = (
            self.chroma_service.get_db().similarity_search_with_relevance_scores(
                user_query, k=limit
            )
        )

        formatted_faq = []
        for doc, score in faq_matches:
            if score >= SIMILARITY_THRESHOLD:
                q = doc.page_content
                a = doc.metadata.get('answer', '<no answer>')
                formatted_faq.append(f'Spørsmål: {q} Svar: {a} \n')

        return formatted_faq

    def _search_docs(
        self,
        user_query: str,
        limit: int,
        endpoint: NamedEndpoint = NamedEndpoint.DEFAULT,
    ):
        user_query = self.llm_service.clean_query(user_query)
        if endpoint == NamedEndpoint.BRUKERSTOTTE:
            self.chroma_service.switch_collection('brukerstotte_docs')
        else:
            self.chroma_service.switch_collection('servicedesk_docs')
        results = self.chroma_service.search(user_query, limit=limit)

        return_text = ''
        for doc in results:
            text = doc
            for meta_key in ['title:', 'description:', 'sidebar:', 'redirect_from:']:
                text = text.replace(meta_key, '')

            return_text += text

        return return_text
