from typing import Any, Dict, List, Optional

import httpx


class BackendApiClient:
    """Client for fetching data from your main API endpoints"""

    def __init__(self, base_url: str = 'http://localhost:3000'):
        self.base_url = base_url

    async def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f'{self.base_url}/api/clients/{client_id}')
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f'Error fetching client: {e}')
        return None

    async def get_scopes(self, client_id: str) -> Optional[List[str]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f'{self.base_url}/api/clients/{client_id}/scopes'
                )
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f'Error fetching scopes: {e}')
        return None

    async def get_jwks(self, client_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f'{self.base_url}/api/clients/{client_id}/jwks'
                )
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f'Error fetching JWKs: {e}')
        return None
