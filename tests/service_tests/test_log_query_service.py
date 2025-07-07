from unittest.mock import patch

from app.services.log_query_service import LogQueryService

"""
Test suite for LogQueryService, ensuring it correctly formats logs and handles API interactions.
"""


class TestLogQueryService:
    def setup_method(self, _method):
        """Setup method to initialize the LogQueryService with a mock API base URL."""

        # Mock the ping method to always return True, simulating a successful API connection
        patcher = patch(
            'app.services.log_query_service.api_help_util.ping', return_value=True
        )
        self.mock_ping = patcher.start()
        self.addCleanup = patcher.stop  # Will be called manually in teardown

        # Initialize the LogQueryService with a dummy API base URL
        self.service = LogQueryService(api_base_url='http://dummy')

    def teardown_method(self, _method):
        """Teardown method to clean up after each test."""

        self.addCleanup()

    @patch('app.services.log_query_service.requests.get')
    def test_get_logs_formats_correctly(self, mock_get):
        """Test that get_logs correctly formats log entries from the API response."""

        # Mock the API response to simulate a successful log retrieval
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'data': {
                'result': [
                    {
                        'stream': {'job': 'test'},
                        'values': [
                            [
                                '1234567890',
                                '2025-06-25T10:15:34.890Z INFO User session created',
                            ],
                            [
                                '1234567891',
                                '2025-06-25T10:15:28.890Z INFO Fetching user profile',
                            ],
                        ],
                    }
                ]
            }
        }

        # Call the get_logs method with a sample query
        logs = self.service.get_logs(query_params={'query': '{job="test"}'})

        # Assert that the logs are formatted correctly
        assert len(logs) == 2
        assert logs[0]['level'] == 'INFO'
        assert 'User session created' in logs[0]['message']
        assert not logs[0]['level'] == 'ERROR'
