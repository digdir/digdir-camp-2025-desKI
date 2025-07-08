"""
Unit tests for the LLMService class.

This test suite verifies that LLMService generates correct responses,
handles special model formats (like deepseek), empty queries, and API exceptions.

All Azure calls are mocked using unittest.mock to avoid real API usage.
"""

from unittest.mock import MagicMock, patch

from app.services.llm_service import LLMService


@patch('app.services.llm_service.ChatCompletionsClient')
class TestLLMService:
    """
    Tests for the LLMService class, using mock to replace Azure ChatCompletionsClient.

    Covers:
    - Normal response behavior
    - Regex-based cleanup (removal of <think> block)
    - Graceful handling of empty queries
    - Exception handling from the client
    """

    def setup_method(self):
        """Prepare common test inputs."""

        self.query = 'Hva er Digdir?'
        self.context = 'Her er litt dokumentasjon.'
        self.regex_model = 'deepseek-chat-r1'
        self.normal_model = 'gpt-4'

    def test_generate_response_returns_answer(self, mock_client_class):
        """
        Ensure that the LLM returns a valid string when the API call succeeds.
        """

        mock_client = MagicMock()
        mock_client.complete.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='Svar fra modellen'))]
        )
        mock_client_class.return_value = mock_client

        llm = LLMService(model_name=self.regex_model)
        result = llm.generate_response_azure(self.query, self.context)

        assert isinstance(result, str)
        assert 'Svar fra modellen' in result

    def test_generate_response_strips_think_block(self, mock_client_class):
        """
        Verify that <think>...</think> blocks are stripped for specific model names.
        """

        mock_client = MagicMock()
        mock_client.complete.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(content='<think>internal</think>\nFinal answer')
                )
            ]
        )
        mock_client_class.return_value = mock_client

        llm = LLMService(model_name=self.regex_model)
        result = llm.generate_response_azure('Test', 'doc')

        assert result == 'Final answer'

    def test_generate_response_handles_empty_query(self, mock_client_class):
        """
        Ensure that an empty or whitespace-only query returns a user-friendly warning.
        """

        llm = LLMService(model_name=self.normal_model)
        result = llm.generate_response_azure('   ', 'irrelevant')
        assert result == 'Please provide a valid question.'

    def test_generate_response_handles_exception(self, mock_client_class):
        """
        Simulate an API failure and ensure the error is caught and a fallback message is returned.
        """

        mock_client = MagicMock()
        mock_client.complete.side_effect = Exception('Boom')
        mock_client_class.return_value = mock_client

        llm = LLMService(model_name=self.normal_model)
        result = llm.generate_response_azure(self.query, self.context)

        assert (
            result
            == 'There was an error generating the response. Please try again later.'
        )
