from .models import GenerateCompletionRequest, GenerateCompletionResponse
from .interfaces import APIClient

class AsyncCompletionService:
    def __init__(self, client: APIClient, model: str, keep_alive: str = "5s"):
        self._client = client
        self._model = model
        self._keep_alive = keep_alive

    async def generate_completion(self, request: GenerateCompletionRequest) -> GenerateCompletionResponse:
        request_data = {
            "model": self._model,
            "prompt": request.prompt,
            "options": request.options,
            "stream": request.stream,
            "keep_alive": self._keep_alive
        }
        response_data = await self._client.post("/generate", json=request_data)
        return GenerateCompletionResponse(**response_data)


class SyncCompletionService:
    def __init__(self, client: APIClient, model: str, keep_alive: str = "5s"):
        self._client = client
        self._model = model
        self._keep_alive = keep_alive

    def generate_completion(self, request: GenerateCompletionRequest) -> GenerateCompletionResponse:
        request_data = {
            "model": self._model,
            "prompt": request.prompt,
            "options": request.options,
            "stream": request.stream,
            "keep_alive": self._keep_alive
        }
        response_data = self._client.post("/generate", data=request_data)
        return GenerateCompletionResponse(**response_data)
