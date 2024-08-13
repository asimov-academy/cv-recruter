import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_option_menu import option_menu
from models.job import Job
from models.resum import Resum
from models.analysis import Analysis
from database.tiny_db import AnalyserDatabase
import uuid, os
from pathlib import Path
import fitz, re
from service.llama_client import LlamaClient
from database.tiny_db import AnalyserDatabase


database = AnalyserDatabase()


st.set_page_config(layout="wide", page_title="Recruter", page_icon=":brain:")


def render_analyse():
    option = st.selectbox(
                "Escolha sua vaga:",
                [job.get('name') for job in database.jobs.all()],
                index=None
            )
    
    if option:
        job = database.get_job_by_name(option)
        
        data = database.get_analysis_by_job_id(job.get('id'))        
        
        df = pd.DataFrame(
            data, columns=[
            'name',
            'total_work_experience',
            'education',
            'skills',
            'languages',
            'salary_expectation',
            'score',
            'resum_id',
            'id'
            ]
        )
        
        df.rename(
            columns={
            'name': 'Nome',
            'total_work_experience': 'Experiência Total',
            'education': 'Educação',
            'skills': 'Habilidades',
            'languages': 'Idiomas',
            'salary_expectation': 'Pretensão Salarial',
            'score': 'score',
            'resum_id': 'resum_id',
            'id': 'id'
        }, inplace=True)
        
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        
        if data:
            gb.configure_column("score", header_name="score", sort="desc")
            gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    
        grid_options = gb.build()

        st.subheader('Classificação dos Candidatos')
        st.bar_chart(df, x="Nome", y="score", color="Nome", horizontal=True)        
        response = AgGrid(
            df,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme='streamlit',  # Tema visual
        )

        selected_candidates = response.get('selected_rows', [])
        candidates_df = pd.DataFrame(selected_candidates)
        
        
        resums = database.get_resums_by_job_id(job.get('id'))
        
        def delete_files_resum(resums):
            for resum in resums:
                path = resum.get('file')
                if os.path.isfile(path):
                    os.remove(path)

        
        if st.button('Limpar Analise'):
            database.delete_all_resums_by_job_id(job.get('id'))
            database.delete_all_analysis_by_job_id(job.get('id'))
            delete_files_resum(resums)
            st.rerun()
                    
        if not candidates_df.empty:
            cols = st.columns(len(candidates_df))
            for idx, row in enumerate(candidates_df.iterrows()):
                with cols[idx]:
                    with st.container():
                        if resum_data := database.get_resum_by_id(row[1]['resum_id']):
                            st.markdown(resum_data.get('content'))
                            
                            with open(resum_data.get('file'), "rb") as pdf_file:
                                pdf_data = pdf_file.read() 
                                st.download_button(
                                    label=f"Download Curriculo {row[1]['Nome']}",
                                    data=pdf_data,
                                    file_name=f"{row[1]['Nome']}.pdf",
                                    mime="application/pdf"
                                )


def render_cv():
    
    option = st.selectbox(
                "Escolha sua vaga:",
                [job.get('name') for job in database.jobs.all()],
                index=None
            )
        
    def save_uploaded_files(uploaded_files, destination_folder):
        destination_path = Path(destination_folder)
        destination_path.mkdir(parents=True, exist_ok=True)
        
        saved_file_paths = []
        for uploaded_file in uploaded_files:
            file_path = destination_path / str(uuid.uuid4())
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_file_paths.append(file_path)
        
        return saved_file_paths

    def read_uploaded_file(file_path):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    
    if option:
        
        uploaded_files = st.file_uploader('Inserir Curriculos', accept_multiple_files=True)
        
        button_send = st.empty()
        if button_send.button('Enviar'):
            message = st.empty()
            if uploaded_files:
                destination_folder = "storage"
                saved_file_paths = save_uploaded_files(uploaded_files, destination_folder)
                cvs = []
                paths_cv = []

                job = database.get_job_by_name(option)
                ai = LlamaClient()

                
                def resume_cvs(ai, cvs, job):
                    results = []
                    for cv, path in cvs:
                        result = ai.resume_cv(cv, job)
                        results.append((result, path))
                    return results
                
                

                for file_path in saved_file_paths:
                    file_content = read_uploaded_file(file_path)
                    cvs.append(file_content)
                    paths_cv.append(file_path)
                    
                
                cv_content_path = zip(cvs, paths_cv)
                
                def extract_data_analysis(resum_cv, job_id, resum_id, score) -> Analysis:
                    secoes_dict = {
                        "id": str(uuid.uuid4()),
                        "job_id": job_id,
                        "resum_id": resum_id,
                        "name": "",
                        "total_work_experience": [],
                        "skills": [],
                        "education": [],
                        "languages": [],
                        "salary_expectation": [],
                        "score": score
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
                        # Remove asteriscos e hífens do início das linhas
                        return re.sub(r"[\*\-]+", "", s).strip()

                    # Extração dos dados usando regex e sanitização
                    for secao, pattern in patterns.items():
                        match = re.search(pattern, resum_cv)
                        if match:
                            if secao == "name":
                                secoes_dict[secao] = clean_string(match.group(1))
                            else:
                                secoes_dict[secao] = [clean_string(item) for item in match.group(1).split('\n') if item.strip()]
                    
                    
                    return Analysis(**secoes_dict)

                with st.spinner('Aguarde um momento...'):
                    button_send.empty()                
                    resums = resume_cvs(ai, cv_content_path, job)                

                    analysis = []
                    for resum, path in resums:
                        resum_schema = Resum(id=str(uuid.uuid4()), job_id=job.get('id'), content=resum, file=str(path))
                        database.insert_resum(resum_schema)
                        
                        score = ai.generate_score(resum, job)
                        analysis.append(extract_data_analysis(resum, resum_schema.job_id, resum_schema.id, score).model_dump())
                    
                    database.analysis.insert_multiple(analysis)
                    
                message.success("Pronto! Pressione 'R' para fazer novos envios")
            else:
                message.warning("No files uploaded.")


def render_jobs():
    jobs_selected = option_menu(None, ["Nova", "Editar", "Excluir"], 
    icons=['clipboard-check', 'code-square', "clipboard2-x"], 
    menu_icon="cast", default_index=0, orientation="horizontal")

    def render_form_edit_job():
        option = st.selectbox(
                "Escolha sua vaga:",
                [job.get('name') for job in database.jobs.all()],
                index=None
            )

        with st.form('jobs'):        
            if option:
                job_database = database.get_job_by_name(option)
                job_name = st.text_input('Nome da Vaga', value=job_database.get('name'))
                main_activities = st.text_area('Atividades Principais', value=job_database.get('main_activities'))
                prerequisites = st.text_area('Pré Requisitos', value=job_database.get('prerequisites'))
                differentials = st.text_area('Diferenciais', value=job_database.get('differentials'))
                if st.form_submit_button('Salvar'):
                    job = Job(id=job_database.get('id'), name=job_name, main_activities=main_activities, prerequisites=prerequisites, differentials=differentials)
                    database.update_job_by_id(job_database.get('id'), job)
    

    def render_form_delete_job():
        option = st.selectbox(
                "Escolha sua vaga:",
                [job.get('name') for job in database.jobs.all()],
                index=None
            )

        if st.button('Excluir') and option:
            database.delete_job_by_id(database.get_job_by_name(option).get('id'))

    def render_form_new_job():
        with st.form('jobs'):        
            job_name = st.text_input('Nome da Vaga')
            main_activities = st.text_area('Atividades Principais')
            prerequisites = st.text_area('Pré Requisitos')
            differentials = st.text_area('Diferenciais')
            if st.form_submit_button('Salvar'):
                job = Job(id=str(uuid.uuid4()), name=job_name, main_activities=main_activities, prerequisites=prerequisites, differentials=differentials)
                database.insert_job(job)

    if jobs_selected == 'Editar':
        render_form_edit_job()
    elif jobs_selected == 'Excluir':
        render_form_delete_job()
    elif jobs_selected == 'Nova':
        render_form_new_job()


if 'menu_selection' not in st.session_state:
    st.session_state.menu_selection = 'analise'
if 'historic_button' not in st.session_state:
    st.session_state.historic_button = None


with st.sidebar:
    menu_selection = option_menu("Recruter", ["Vagas", "Curriculos", "Analise"], 
        icons=['card-text', 'file-earmark-pdf', 'clipboard-data'], menu_icon="cast", default_index=0)

    st.session_state.menu_selection = menu_selection


if st.session_state.menu_selection == 'Curriculos':
    render_cv()
elif st.session_state.menu_selection == 'Vagas':
    render_jobs()
elif st.session_state.menu_selection == 'Analise':
    render_analyse()

