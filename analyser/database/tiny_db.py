from tinydb import TinyDB, Query
from models.job import Job
from models.resum import Resum
from models.analysis import Analysis



class AnalyserDatabase(TinyDB):
    def __init__(self, file_path='db.json') -> None:
        super().__init__(file_path)
        self.jobs = self.table('jobs')
        self.resums = self.table('resums')
        self.analysis = self.table('analysis')

    def insert_job(self, job: Job):
        self.jobs.insert(job.model_dump())
    
    def insert_analysis(self, analysis: Analysis):
        self.analysis.insert(analysis.model_dump())

    def insert_resum(self, resum: Resum):
        self.resums.insert(resum.model_dump())

    def get_job_by_name(self, name):
        job = Query()
        result = self.jobs.search(job.name == name)
        return result[0] if result else None
    
    def get_resum_by_id(self, id):
        resum = Query()
        result = self.resums.search(resum.id == id)
        return result[0] if result else None
    
    def get_resums_by_job_id(self, job_id):
        resum = Query()
        result = self.resums.search(resum.job_id == job_id)
        return result
    
    def get_analysis_by_job_id(self, job_id):
        analysis = Query()
        result = self.analysis.search(analysis.job_id == job_id)
        return result

    def update_job_by_id(self, id, new_data: Job):
        query = Query()
        self.jobs.update(new_data.model_dump(), query.id == id)

    def delete_job_by_id(self, id):
        query = Query()
        self.jobs.remove(query.id == id)
    
    def delete_all_resums_by_job_id(self, job_id):
        resum = Query()
        self.resums.remove(resum.job_id == job_id)
    
    def delete_all_analysis_by_job_id(self, job_id):
        analysis = Query()
        self.analysis.remove(analysis.job_id == job_id)