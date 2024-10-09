import fitz, uuid, re, time, os
from service.sheets import AccessResume
from database.tiny_db import AnalyserDatabase
from models.file import File
from models.analysis import Analysis
from models.resum import Resum
from service.llama_client import LlamaClient


database = AnalyserDatabase()
ai = LlamaClient()


# from tinydb import Query

# file = Query()
# quit(database.files.remove(file.file_id == '14nEavbXGdXVw3XbBXmRZuucoAbrT1nfm'))


def read_uploaded_file(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_data_analysis(resum_cv, job_id, resum_id, score) -> Analysis:
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


def get_files_in_sheets():
    jobs = database.jobs.all()
    for job in jobs:
        print(job.get('sheet_name'))
        print(job.get('name'))
        sheet = AccessResume(job.get('sheet_name'))
        last_file_id = database.get_last_file_by_job_id(job.get('id'))
        print(last_file_id)
        

        if last_file_id:
            resums_ids = sheet.get_resumes_ids_unprocessed(last_file_id.get('file_id'))
            print(len(resums_ids))
        else:
            resums_ids = sheet.get_resumes_id()
            
            
            print(resums_ids)
            
            print(len(resums_ids))
                    
        for id in resums_ids:
            if not id.startswith("Faça") and not id == '104kU92P7igU9-ll1C0JVQcU5aKBz3yrT':                
                print(id)
                path = sheet.download_file(id)
                try:
                    content = read_uploaded_file(path)
                    resum = ai.resume_cv(content, job)
                    opnion = ai.generate_opnion(content, job)
                    score = ai.generate_score(resum, job)
                    print(f'esse é o retorno da func: {score}')
                    resum_schema = Resum(id=str(uuid.uuid4()), job_id=job.get('id'), content=resum, file=str(path), opnion=opnion)
                    file = File(file_id=id, job_id=job.get('id')).model_dump()
                    analysis = extract_data_analysis(resum, resum_schema.job_id, resum_schema.id, score).model_dump()
                    database.insert_resum(resum_schema)
                    database.analysis.insert(analysis)
                    database.files.insert(file)
                except Exception as err:
                    if os.path.isfile(path):
                        os.remove(path)
                    print(err.args)
                    raise err
                    
if __name__ == "__main__":
    while True:
        try:
            get_files_in_sheets()
        except Exception as err:
            print(err) 
            time.sleep(20)
            continue


