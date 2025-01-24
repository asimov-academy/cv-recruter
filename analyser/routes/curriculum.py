import uuid
from database.tiny_db import AnalyserDatabase
from service.llama_client import LlamaClient
from service.file_service import FileService
from factories.resume_factory import ResumFactory
from factories.analysis_factory import AnalysisFactory


DESTINATION_PATH = 'storage'

class CurriculumRoute:
    def __init__(self) -> None:
        self.database = AnalyserDatabase()
        self.jobs = [job.get('name') for job in self.database.jobs.all()]
        self.job = {}
        self._ai = LlamaClient()
        self._file_service = FileService()
        
    def resum(self, contents, job):
        results = []
        for cv, path in contents:
            result = self._ai.resume_cv(cv, job)
            results.append((result, path))
        return results
    
    def get_files(self, uploaded_files):
        saved_file_paths = self._file_service.save_uploaded_files(uploaded_files, 'storage')
        contents = self._file_service.read_all(saved_file_paths)
        return zip(contents, saved_file_paths)
    
    def create_analyse(self, uploaded_files, job_name):
        self.job = self.database.get_job_by_name(job_name)
        for content, path in self.get_files(uploaded_files):
            resum_result = self._ai.resume_cv(content)
            opnion = self._ai.generate_opnion(content, self.job)
            score = self._ai.generate_score(content, self.job)
            
            score_competence = self._ai.score_qualifications(content, self.job.get('competence'))
            score_strategies = self._ai.score_qualifications(content, self.job.get('strategies'))
            score_qualifications = self._ai.score_qualifications(content, self.job.get('qualifications'))
            
            resum_schema = ResumFactory(
                self.job.get('id'), 
                resum_result, path, 
                opnion,
                score_competence,
                score_strategies,
                score_qualifications,
            ).create()

            AnalysisFactory(
                resum_schema.content,
                self.job.get('id'),
                resum_schema.id,
                score,
            ).create()