import requests


def ping(url: str) -> bool:
    """
    Private method to ping the specified host to check if it is reachable.

    Args:
        url (str): The hostname or IP address to ping.

    Returns:
        bool: True if the host is reachable, False otherwise.
    """
    print(f'Pinging {url}...')
        
    try:
        response = requests.get(url, timeout=3)
        return response.status_code < 400
    except requests.RequestException:
        return False
