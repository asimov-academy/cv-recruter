from pydantic import BaseModel

class Resum(BaseModel):
    id: str
    job_id: str
    content: str
    file: str
