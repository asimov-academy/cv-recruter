from pydantic import BaseModel
from typing import List

class Analysis(BaseModel):
    id: str
    job_id: str
    resum_id: str
    name: str
    total_work_experience: List[str]
    skills: List[str]
    education: List[str]
    languages: List[str]
    salary_expectation: List[str]
    score: float
