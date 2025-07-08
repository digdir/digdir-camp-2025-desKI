"""
Unit tests for the ChromaService class.

These tests verify the functionality of the ChromaService by mocking out all external dependencies,
including HuggingFaceEmbeddings and Chroma vector store.

The goal is to ensure that the logic for searching and adding documents behaves correctly
without relying on actual disk I/O, model downloads, or a real ChromaDB instance.

Tested methods:
- search(): checks for document retrieval and formatting
- add_doc
"""

from unittest.mock import MagicMock, patch

from app.services.chroma_service import ChromaService


@patch('app.services.chroma_service.Chroma')
@patch('app.services.chroma_service.HuggingFaceEmbeddings')
class TestChromaService:
    """
    Test suite for ChromaService using unittest.mock to replace external dependencies.
    All tests run offline and simulate expected behaviors.
    """

    def setup_method(self):
        """Initialize common test data before each test."""
        self.test_query = 'Hva er Digdir?'
        self.mock_docs = [
            MagicMock(
                page_content='Doc text', metadata={'source': 'file.txt', 'page': '1'}
            )
        ]

    def test_search_returns_combined_chunks(self, mock_embed, mock_chroma):
        """
        Test that search returns combined document chunks when documents are found.
        """

        mock_db = MagicMock()
        mock_db.get.return_value = {'documents': ['...']}
        mock_db.similarity_search_with_relevance_scores.return_value = [
            (self.mock_docs[0], 0.9)
        ]
        mock_chroma.return_value = mock_db

        cs = ChromaService()
        result = cs.search(self.test_query)

        assert isinstance(result, str)
        assert 'file.txt' in result
        assert 'Doc text' in result

    def test_add_documents_success(self, mock_embed, mock_chroma):
        """
        Test that add_documents calls the underlying DB methods when documents are provided.
        """

        mock_db = MagicMock()
        mock_chroma.return_value = mock_db

        cs = ChromaService()
        result = cs.add_documents(['Dette er et dokument.'])

        mock_db.add_documents.assert_called_once()
        mock_db.persist.assert_called_once()
        assert result is True

    def test_add_documents_empty_list(self, mock_embed, mock_chroma):
        """
        Test that add_documents returns False and does not call DB methods when input is empty.
        """

        cs = ChromaService()
        result = cs.add_documents([])

        assert result is False

    def test_search_empty_query_returns_none(self, mock_embed, mock_chroma):
        """
        Test that search returns an empty list when query is blank or whitespace.
        """

        cs = ChromaService()
        result = cs.search('   ')

        assert result == []
