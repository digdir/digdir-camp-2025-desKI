import requests
from urllib.parse import urlparse

def ping(url: str) -> bool:
    """
    Private method to ping the specified host to check if it is reachable.
        
    Args:
        host (str): The hostname or IP address to ping.
        
    Returns:
        bool: True if the host is reachable, False otherwise.
    """
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port
    try:
        response = requests.get(f"{host}:{port}/ready", timeout=3)
        return response.status_code < 400
    except requests.RequestException:
        return False