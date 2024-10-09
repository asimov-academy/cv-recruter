import uuid
from models.resum import Resum
from database.tiny_db import AnalyserDatabase

DATABASE = AnalyserDatabase()

class ResumFactory:
    def __init__(self, job_id: str, content: str, file: str):
        self.job_id = job_id
        self.content = content
        self.file = file

    def create(self) -> Resum:
        resum = Resum(
            id=str(uuid.uuid4()),
            job_id=self.job_id,
            content=self.content,
            file=str(self.file)
        )
        
        DATABASE.resums.insert(resum.model_dump())
        return resum