from abc import ABC, abstractmethod
from typing import Any, Dict

class APIClient(ABC):
    @abstractmethod
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def get(self, endpoint: str) -> Any:
        pass
