from pydantic import BaseModel
from typing import List, Any


class Resum(BaseModel):
    id: str
    job_id: str
    content: str
    opnion: str
    file: str
    score_competence: List[Any]
    score_strategies: List[Any] 
    score_qualifications: List[Any]

