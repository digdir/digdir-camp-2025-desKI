from urllib.parse import urlparse

import requests


# Ping the specified host to check if it is reachable
def ping(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port
    try:
        # Send a GET request to the /ready endpoint
        response = requests.get(f'{host}:{port}/ready', timeout=3)
        # Return True if the status code indicates success
        return response.status_code < 400
    except requests.RequestException:
        # Return False if the request failed
        return False
