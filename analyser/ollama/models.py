from typing import Dict, Any, Optional
from pydantic import BaseModel

class GenerateCompletionRequest(BaseModel):
    prompt: str
    options: Optional[Dict[str, Any]] = None
    stream: bool = False



class GenerateCompletionResponse(BaseModel):
    model: str
    response: str
    total_duration: int
