import uuid
from models.resum import Resum
from database.tiny_db import AnalyserDatabase

DATABASE = AnalyserDatabase()

class ResumFactory:
    def __init__(
        self, 
        job_id: str, 
        content: str, 
        file: str, 
        opnion: str,
        competence: list,
        strategies: list,
        qualifications: list,
    ):
        self.job_id = job_id
        self.content = content
        self.file = file
        self.opnion = opnion
        self.competence = competence
        self.strategies = strategies
        self.qualifications = qualifications

    def create(self) -> Resum:
        resum = Resum(
            id=str(uuid.uuid4()),
            job_id=self.job_id,
            content=self.content,
            file=str(self.file),
            opnion=self.opnion,
            score_competence=self.competence,
            score_strategies=self.strategies,
            score_qualifications=self.qualifications
        )
        
        DATABASE.resums.insert(resum.model_dump())
        return resum