import uuid
from models.job import Job
from database.tiny_db import AnalyserDatabase

DATABASE = AnalyserDatabase()

class JobFactory:
    def __init__(self, 
                 name: str, 
                 main_activities: str, 
                 prerequisites: str, 
                 differentials: str, 
                 sheet_name: str,
                 competence: list,
                 strategies: list,
                 qualifications: list,
                 score_qualification: list,
    ):
        self._validate_fields(name, main_activities, prerequisites, differentials, sheet_name)
        
        self.name = name
        self.main_activities = main_activities
        self.prerequisites = prerequisites
        self.differentials = differentials
        self.sheet_name = sheet_name
        self.competence = competence
        self.strategies = strategies
        self.qualifications = qualifications
        self.score_qualification = score_qualification
    
    def _validate_fields(self, *fields):
        for field in fields:
            if not field.strip():
                raise ValueError("Fields cannot be empty strings.")

    def create(self) -> Job:
        job = Job(
            id=str(uuid.uuid4()),
            name=self.name,
            main_activities=self.main_activities,
            prerequisites=self.prerequisites,
            differentials=self.differentials,
            sheet_name=self.sheet_name,
            competence=self.competence,
            strategies=self.strategies,
            qualifications=self.qualifications,
            score_competence=self.score_qualification,
        )
        DATABASE.jobs.insert(job.model_dump())
        return job