from pydantic import BaseModel, Field
from typing import List, Any



class Job(BaseModel):
    id: str
    name: str
    main_activities: str
    prerequisites: str
    differentials: str
    sheet_name: str
    competence: List[Any]
    strategies: List[Any]
    qualifications: List[Any]
    score_competence: List[Any]  
