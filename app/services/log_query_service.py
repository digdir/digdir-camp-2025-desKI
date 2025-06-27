import logging
from urllib.parse import urlparse, urlunparse

import requests

from app.utils import api_help_util

logger = logging.getLogger(__name__) 

class LogQueryService:
    """Service for querying logs from the database."""

    def __init__(self, api_base_url: str):
        """
        Initialize the service with an API connection.

        Args:
            api_base_url (str): The base URL for the Loki API.
            If not provided, defaults to a local instance.

        Raises:
            ValueError: If the API base URL is unreachable.
        """

        self.api_base_url = api_base_url or 'loki-api:3100/loki/api/v1/'
        health_url = self._get_health_url(self.api_base_url)
        if not api_help_util.ping(health_url):
            raise ValueError(f'Could not connect to API at {self.api_base_url}')

    def get_logs(self, query_params: dict[str, any]):
        """
        Fetch logs from the API based on the provided query parameters.

        Args:
            query_params (dictionary): parameters to filter logs.

        Returns:

        Raises:
            Exception: If the API request fails or returns an error.
            TODO: ValueError: If the query parameters are invalid or empty.

        """
        # TODO: Validate query_params before making the request

        response = requests.get(f'{self.api_base_url}', params=query_params)
        if response.status_code != 200:
            raise Exception(
                f'Failed to fetch logs: {response.status_code} - {response.text}'
            )

        logger.debug("API response: %s", response.json())
        return response.json()

    def format_logs(self, logs):
        # This method would format the logs for output.
        pass

    def _get_health_url(api_base_url: str) -> str:
        parsed = urlparse(api_base_url)
        netloc = parsed.netloc or parsed.path  # handle if url without scheme
        return urlunparse((parsed.scheme or 'http', netloc, '/ready', '', '', ''))
