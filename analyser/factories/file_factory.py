import uuid
from models.file import File
from database.tiny_db import AnalyserDatabase

DATABASE = AnalyserDatabase()

class FileFactory:
    def __init__(self, job_id: str):
        self._validate_field(job_id)
        self.job_id = job_id
    
    def _validate_field(self, field: str):
        if not field.strip():
            raise ValueError("job_id cannot be an empty string.")

    def create(self) -> File:
        file = File(
            file_id=str(uuid.uuid4()),
            job_id=self.job_id
        )
        
        DATABASE.files.insert(file.model_dump())
        return file