import logging
from typing import Optional

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

CHROMA_PATH = 'app/db/chroma_db'
COLLECTION_NAME = 'dig_docs'


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
        embedding_model: Optional[HuggingFaceEmbeddings] = None
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

    def search(self, query: str, limit: int = 5) -> Optional[dict]:
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

        # use similarity_search_with_relevance_score for more detailed results
        results = self.db.similarity_search(query, k=limit)

        if not results:
            logger.info('No results found for the query.')
            return []

        combined_chunks = []
        used_sources = set()

        for doc in results:
            source = doc.metadata.get('source', 'ukjent fil')
            page = doc.metadata.get('page', 'ukjent side')
            used_sources.add(f'{source}, side {page}')
            combined = f'[Kilde: {source}, side {page}]\n{doc.page_content}'
            combined_chunks.append(combined)

        retrieved_context = '\n\n'.join(combined_chunks)
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
