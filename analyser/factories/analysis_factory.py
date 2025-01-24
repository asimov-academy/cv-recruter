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
        
        self.analysis_data = self._extract_data_analysis(resum_content, job_id, resum_id, score).model_dump()
    
    def _extract_data_analysis(self, resum_cv, job_id, resum_id, score) -> Analysis:
        secoes_dict = {
            "id": str(uuid.uuid4()),
            "job_id": job_id,
            "resum_id": resum_id,
            "name": "",
            "skills": [],
            "education": [],
            "languages": [],
            "score": score
        }
        
        print(f'entrou na extração: {secoes_dict["score"]}')

        patterns = {
            "name": r"(?:## Nome Completo\s*|Nome Completo\s*\|\s*Valor\s*\|\s*\S*\s*\|\s*)(.*)",
            "skills": r"## Habilidades\s*([\s\S]*?)(?=##|$)",
            "education": r"## Educação\s*([\s\S]*?)(?=##|$)",
            "languages": r"## Idiomas\s*([\s\S]*?)(?=##|$)",
        }

        def clean_string(s: str) -> str:
            return re.sub(r"[\*\-]+", "", s).strip()

        for secao, pattern in patterns.items():
            match = re.search(pattern, resum_cv)
            if match:
                if secao == "name":
                    secoes_dict[secao] = clean_string(match.group(1))
                else:
                    secoes_dict[secao] = [clean_string(item) for item in match.group(1).split('\n') if item.strip()]

        # Validação para garantir que nenhuma seção obrigatória esteja vazia
        for key in ["name", "education", "skills"]:
            if not secoes_dict[key] or (isinstance(secoes_dict[key], list) and not any(secoes_dict[key])):
                raise ValueError(f"A seção '{key}' não pode ser vazia ou uma string vazia.")
        
        import pprint
        pprint.pp(secoes_dict)

        return Analysis(**secoes_dict)

    def create(self) -> Analysis:
        analysis = Analysis(**self.analysis_data)
        DATABASE.analysis.insert(analysis.model_dump())
        return analysis
