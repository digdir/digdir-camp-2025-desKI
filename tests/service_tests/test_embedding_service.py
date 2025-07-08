"""
Unit tests for the EmbeddingService class.

This test suite ensures that the embed() method returns a non-empty list of floats
for a given input string. These tests are intended to verify the functional behavior
of the embedding layer, assuming the model loads correctly.

Note: This test uses the actual HuggingFace embedding model, so it may require internet
access and model caching.
"""

from app.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """
    Test suite for the EmbeddingService.

    Validates that the returned embeddings are correctly typed and non-empty.
    """

    def setup_method(self):
        """
        Create a new instance of EmbeddingService before each test.

        This will use a cached variant if available.
        """

        self.es = EmbeddingService()

    def test_embed_return_list(self):
        """
        Test that embed() returns a non-empty list of floats for a valid input string.
        """

        result = self.es.embed('Digdir er kult')

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(x, float) for x in result)
