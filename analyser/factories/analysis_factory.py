import uuid
import re
from models.analysis import Analysis
from database.tiny_db import AnalyserDatabase

DATABASE = AnalyserDatabase()

class AnalysisFactory:
    def __init__(self, resum_content: str, job_id: str, resum_id: str, score: float):
        self.resum_cv = resum_content
        self.job_id = job_id
        self.resum_id = resum_id
        self.score = score
        
        self.analysis_data = self._extract_data_analysis()
    
    def _extract_data_analysis(self) -> dict:
        secoes_dict = {
            "id": str(uuid.uuid4()),
            "job_id": self.job_id,
            "resum_id": self.resum_id,
            "name": "",
            "total_work_experience": [],
            "skills": [],
            "education": [],
            "languages": [],
            "salary_expectation": [],
            "score": self.score
        }

        # Regex patterns para capturar as seções
        patterns = {
            "name": r"## Nome Completo\s*(.*)",
            "total_work_experience": r"## Duração Total de Experiência\s*([\s\S]*?)(?=##|$)",
            "skills": r"## Habilidades\s*([\s\S]*?)(?=##|$)",
            "education": r"## Educação\s*([\s\S]*?)(?=##|$)",
            "languages": r"## Idiomas\s*([\s\S]*?)(?=##|$)",
            "salary_expectation": r"## Pretensão Salarial\s*([\s\S]*?)(?=##|$)"
        }

        # Função para sanitizar as strings
        def clean_string(s: str) -> str:
            return re.sub(r"[\*\-]+", "", s).strip()

        # Extração dos dados usando regex e sanitização
        for secao, pattern in patterns.items():
            match = re.search(pattern, self.resum_cv)
            if match:
                if secao == "name":
                    secoes_dict[secao] = clean_string(match.group(1))
                else:
                    secoes_dict[secao] = [clean_string(item) for item in match.group(1).split('\n') if item.strip()]

        return secoes_dict

    def create(self) -> Analysis:
        analysis = Analysis(**self.analysis_data)
        DATABASE.analysis.insert(analysis.model_dump())
        return analysis
