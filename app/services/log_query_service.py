import re
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
            raise ValueError(f'Could not connect to API at {health_url}')

    def get_logs(self, query_params: dict[str, any]):
        """
        Fetch logs from the API based on the provided query parameters.

        Args:
            query_params (dictionary): parameters to filter logs.

        Returns:
            List: A list of formatted log entries, each containing a timestamp, level, and message
            Timestamp is in ISO 8601 format (e.g., "2023-10-01T12:34:56Z").
            Level is the log level (e.g., INFO, ERROR).
            Message is the log message (e.g., "Service started successfully").

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

        logger.debug('API response: %s', response.json())
        return self._format_logs(response.json())

    def _format_logs(self, logs) -> list[dict[str, str]]:
        """
        Format the logs from the API response.
        Args:
            logs (dict): The raw logs from the API response.

        Returns:
            A list of formatted log entries, each containing a timestamp, level, and message
            Timestamp is in ISO 8601 format (e.g., "2023-10-01T12:34:56Z").
            Level is the log level (e.g., INFO, ERROR).
            Message is the log message (e.g., "Service started successfully").

        """

        log_line_regex = re.compile(r'(?P<timestamp>\S+) (?P<level>[A-Z]+) (?P<msg>.+)')

        formatted = []
        log_result = logs.get('data', {}).get('result', [])

        for entry in log_result:
            values = entry.get('values', [])

            for _, raw_log in values:
                match = log_line_regex.match(raw_log)
                if match:
                    ts = match.group('timestamp')
                    level = match.group('level')
                    msg = match.group('msg')
                    formatted.append({'timestamp': ts, 'level': level, 'message': msg})
                else:
                    formatted.append(raw_log)
        return formatted

    def _get_health_url(self, api_base_url: str) -> str:
        """
        Construct the health check URL for the API.
        Args:
            api_base_url (str): The base URL for the API.
        Returns:
            str: The health check URL for the API.
        """

        parsed = urlparse(api_base_url)
        netloc = parsed.netloc or parsed.path  # handle if url without scheme
        return urlunparse((parsed.scheme or 'http', netloc, '/ready', '', '', ''))
