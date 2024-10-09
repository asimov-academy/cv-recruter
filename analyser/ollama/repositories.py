import httpx
from typing import Any, Dict
from ollama.interfaces import APIClient

URL_PATTERN = 'http://localhost:11434/api'
TIMEOUT = 60.0

class HTTPXAsyncClient(APIClient):
    def __init__(self, base_url: str = URL_PATTERN):
        self._client = httpx.AsyncClient(base_url=base_url)
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        response = await self._client.post(endpoint, json=data, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()

    async def get(self, endpoint: str) -> Any:
        response = await self._client.get(endpoint, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()

class HTTPXSyncClient(APIClient):
    def __init__(self, base_url: str = URL_PATTERN):
        self._client = httpx.Client(base_url=base_url)
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        response = self._client.post(endpoint, json=data, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str) -> Any:
        response = self._client.get(endpoint, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
