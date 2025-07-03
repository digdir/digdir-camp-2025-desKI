import logging

from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    A service for generating text embeddings using a HuggingFace model.
    This service uses the HuggingFaceEmbeddings class to create embeddings for text inputs.

    Attributes:
        model (HuggingFaceEmbeddings): The HuggingFace model instance used for generating embeddings.
        
    Methods:
        get_model() -> HuggingFaceEmbeddings:
            Returns the embedding model instance.
        embed(text: str) -> list[float]:
            Generates an embedding for the given text using the HuggingFace model.
            Returns a list of floats representing the embedding vector for the text.

    Usage:
        from app.services.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        embedding = embedding_service.embed("Hva er Digdir?")
        print(embedding)
    """

    def __init__(self, model_name: str = 'intfloat/multilingual-e5-base'):
        """
        Initializes the EmbeddingService with a HuggingFace model for generating embeddings.

        Args:
            model_name (str): The name of the HuggingFace model to use for embeddings.
            Default is 'intfloat/multilingual-e5-base', which supports multiple languages.
        """

        self.model = HuggingFaceEmbeddings(model_name=model_name)

    def get_model(self) -> HuggingFaceEmbeddings:
        """
        Returns the embedding model instance.
        This can be used to access the model's methods directly if needed.
        """

        return self.model

    def embed(self, text: str) -> list[float]:
        """
        Generates an embedding for the given text using the HuggingFace model.

        Args:
            text (str): The text to embed.
        Returns:
            list[float]: The embedding vector for the text.
        """
        try:
            return self.model.embed_query(text)
        except Exception as e:
            logger.error(f'Error generating embedding for text: {text}. Error: {e}')
            return []
