import logging
from typing import Optional

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from app.config import CHROMA_PATH, COLLECTION_NAME

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more detail
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)


class ChromaService:
    """
    A service for interacting with a ChromaDB vector store.
    This service allows for searching and adding documents to the ChromaDB.

    Attributes:
    -----------
        persist_directory : str
        The directory where the ChromaDB is persisted. Defaults to "app/db/chroma_db".

        collection_name : str
        The name of the collection in the ChromaDB. Defaults to "dig_docs".

        embedding_model : str
        The name of the embedding model used for document embeddings. Defaults to 'intfloat/multilingual-e5-base'.

    Methods:
    --------
        search(query: str, limit: int = 5) -> Optional[dict]:
            Searches the ChromaDB for documents similar to the query text.

        add_documents(documents: list) -> bool:
            Adds a list of documents to the ChromaDB.

    Usage:
    ------
        from app.services.chroma_service import ChromaService
        chroma = ChromaService()
        result = chroma.search("Hvordan søker jeg støtte?")
        print(result)
    """

    def __init__(
        self,
        persist_directory: str = CHROMA_PATH,
        collection_name: str = COLLECTION_NAME,
        embedding_model: Optional[HuggingFaceEmbeddings] = None,
    ):
        self.embedding_model = embedding_model or HuggingFaceEmbeddings(
            model_name='intfloat/multilingual-e5-base',
        )
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model,
            collection_name=self.collection_name,
        )
        logger.info(len(self.db.get()))

    def get_db(self):
        return self.db

    def search(self, query: str, limit: int = 10) -> Optional[dict]:
        """
        Search the ChromaDB for documents similar to the query text.

        Args:
            query (str): The text to search for.
            limit (int): The maximum number of results to return.

        Returns:
            Optional[dict]: A dictionary containing the search results.
            Empty if no results found or no query provided.
        """

        if not query.strip():
            logger.warning('Empty query provided. Returning None.')
            return []

        count = len(self.db.get()['documents'])
        logger.info(f'Documents in collection: {count}')
        query = query.lower()
        results = self.db.similarity_search_with_relevance_scores("query: "+ query, k=limit)
        logger.info(results)

        if not results:
            logger.info('No results found for the query.')
            return []

        combined_chunks = []
        used_sources = set()

        for doc, _ in results:
            source = doc.metadata.get('source', 'ukjent fil')
            page = doc.metadata.get('page', 'ukjent side')
            used_sources.add(f'{source}, side {page}')
            combined = doc.page_content
            combined_chunks.append(combined)

        retrieved_context = '\n'.join(combined_chunks)
        return retrieved_context

    def add_documents(self, documents: list) -> bool:
        """
        Add a list of documents to the ChromaDB.

        Args:
            documents (list): A list of document strings to add.
        Returns:
            bool: True if documents were added successfully, False otherwise. Debugging purpose.
        Raises:
            Exception: If there is an error adding documents to the database.
        """

        if not documents:
            logger.warning('No documents provided to add to ChromaDB.')
            return False
        try:
            self.db.add_documents(documents)
            self.db.persist()
            return True
        except Exception as e:
            logger.error(f'Error adding documents to ChromaDB: {e}')
            return False

    def switch_collection(self, collection_name: str):
        """
        Switch to a different collection. Useful for FAQs vs docs separation.
        """
        self.collection_name = collection_name
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model,
            collection_name=collection_name,
        )
        logger.info(
            f"Switched to collection {collection_name}, docs={len(self.db.get()['documents'])}"
        )
