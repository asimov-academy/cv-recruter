import uuid
from streamlit_option_menu import option_menu
from database.tiny_db import AnalyserDatabase
from factories.job_factory import JobFactory
from models.job import Job
from service.llama_client import LlamaClient


DESTINATION_PATH = 'storage'
MENUS = (
    'Nova',
    'Editar',
    'Excluir'
)

class JobRoute:
    def __init__(self) -> None:
        self.llm = LlamaClient()
        self.database = AnalyserDatabase()
        self.jobs = [job.get('name') for job in self.database.jobs.all()]
        self.job = {}
        print(self.jobs)

    def render_menu(self):
        new, edition, remove = MENUS
        return option_menu(
            None, 
            [new, edition, remove], 
            icons=['clipboard-check', 'code-square', "clipboard2-x"], 
            menu_icon="cast", 
            default_index=0, 
            orientation="horizontal"
        )
    
    def new_job_form(self, st):
        sheet_name = st.text_input('Nome da Tabela do Google Sheets')        
        job_name = st.text_input('Nome da Vaga')
        main_activities = st.text_area('Atividades Principais')
        prerequisites = st.text_area('Pré Requisitos')
        differentials = st.text_area('Diferenciais')
        if st.form_submit_button('Salvar'):
            if not all([sheet_name, job_name, main_activities, prerequisites, differentials]):
                    st.error('O meu querido, não tem como salvar uma vaga sem preencher os dados!')
                    return
                
            job_dict = {
                'job_name': job_name,
                'main_activities': main_activities,
                'prerequisites': prerequisites,
                'differentials': differentials,
            }
            
            with st.spinner('Aguarde um momento...'):
            
                competence = self.llm.create_competence(job_dict)
                strategies = self.llm.create_strategies(job_dict)
                qualification = self.llm.create_qualification(job_dict)
                score_qualification = self.llm.score_competence(job_dict, qualification)
                
                print(score_qualification)
                print(type(score_qualification))
        
                JobFactory(
                    name=job_name,
                    main_activities=main_activities,
                    prerequisites=prerequisites,
                    differentials=differentials,
                    sheet_name=sheet_name,
                    competence=competence,
                    strategies=strategies,
                    qualifications=qualification,
                    score_qualification=score_qualification,
                ).create()
                
                st.warning('Compartilhe a tabela (google sheets) e a pasta do drive com o email: ga-api-client@scidata-299417.iam.gserviceaccount.com')

    def edition_job_form(self, st, options):
        all_sheet_names = self.database.get_all_sheet_names_in_jobs()
        print(all_sheet_names)
        job = self.database.get_job_by_name(options)
        sheet_name = st.selectbox('Nome da tabela', all_sheet_names, index=all_sheet_names.index(job['sheet_name']))
        job_name = st.text_input('Nome da Vaga', value=job.get('name'))
        main_activities = st.text_area('Atividades Principais', value=job.get('main_activities'))
        prerequisites = st.text_area('Pré Requisitos', value=job.get('prerequisites'))
        differentials = st.text_area('Diferenciais', value=job.get('differentials'))
        if st.form_submit_button('Salvar'):
            if not all([sheet_name, job_name, main_activities, prerequisites, differentials]):
                    st.error('O meu querido, não tem como salvar uma vaga sem preencher os dados!')
                    return
            
            job_schema = Job(
                job.get('id'),
                job_name,
                main_activities,
                prerequisites,
                differentials,
                sheet_name
            )
            
            self.database.update_job(job_schema)
            st.success('Vaga salva com sucesso')
    
    def remove_job_form(self, st, option):
        job_id = self.database.get_job_by_name(option).get('id')
        if st.button('Excluir') and option:
            self.database.delete_job_by_id(job_id)
            self.database.delete_all_resums_by_job_id(job_id)
            self.database.delete_all_files_by_job_id(job_id)
            self.database.delete_all_analysis_by_job_id(self.job.get('id'))
            st.success('Vaga excluida com sucesso')

        