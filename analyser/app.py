import uuid
import streamlit as st
from streamlit_option_menu import option_menu
from routes.job import JobRoute
from routes.analyse import AnalyseRoute
from routes.curriculum import CurriculumRoute




st.set_page_config(layout="wide", page_title="Recruter", page_icon=":brain:")


def render_analyse():
    analyse_route = AnalyseRoute()

    option = st.selectbox(
        "Escolha sua vaga:",
        analyse_route.jobs,
        index=None
    )


    if option:
        st.subheader('Classificação dos Candidatos')
        with st.expander('Grafico Geral de Pontuação'):
            bar = st.empty()  
        candidates = analyse_route.render_grid(option)
        bar.bar_chart(analyse_route._create_dataframe_to_analyse(), x="Nome", y="score", color="Nome", horizontal=True)  
    
        # if st.button('Limpar Analise'):
        #     analyse_route.clean_analyse()
        #     st.rerun()
    
    
        if not candidates.empty:
            cols = st.columns(len(candidates))
            for idx, row in enumerate(candidates.iterrows()):
                with cols[idx]:
                    with st.container():
                        candidate_resum = analyse_route.get_resum_by_id(row[1]['resum_id'])
                        if candidate_resum:
                            st.markdown(candidate_resum.get('content'))
                            st.markdown(candidate_resum.get('opnion'))

                        
                            with open(candidate_resum.get('file'), 'rb') as file:
                                st.download_button(
                                    label=f"Download Curriculo {row[1]['Nome']}",
                                    data=file.read(),
                                    file_name=f"{row[1]['Nome']}.pdf",
                                    mime="application/pdf",
                                    key=str(uuid.uuid1())
                                )
           

def render_curriculum():
    curriculum_route = CurriculumRoute()
    
    option = st.selectbox(
        "Escolha sua vaga:",
        curriculum_route.jobs,
        index=None
    )

    if option:
        uploaded_files = st.file_uploader('Inserir Curriculos', accept_multiple_files=True)
        button_send = st.empty()
        
        if button_send.button('Enviar'):
            button_send.empty()
            message_element = st.empty()
            
            if uploaded_files:
                with st.spinner('Aguarde um momento...'):
                    curriculum_route.create_analyse(uploaded_files, option)
                
                message_element.success("Pronto! Pressione 'R' para fazer novos envios")
                return
            
            message_element.warning('Você não subiu arquivos para processar!')


def render_jobs():
    job_route = JobRoute()
    menu_choice = job_route.render_menu()
    
    if not menu_choice in ['Excluir', 'Editar']:
        with st.form(menu_choice):
            job_route.new_job_form(st)
        return
        
    option = st.selectbox(
        "Escolha sua vaga:",
        job_route.jobs,
        index=None
    )
    if option:
        with st.form(menu_choice):
            if menu_choice == 'Editar':
                job_route.edition_job_form(st, option)
                return
    
        job_route.remove_job_form(st, option)


with st.sidebar:
    menu_selection = option_menu(
        "Recruter",
        ["Vagas", "Curriculos", "Analise"], 
        icons=['card-text', 'file-earmark-pdf', 'clipboard-data'], menu_icon="cast", default_index=0
    )

    st.session_state.menu_selection = menu_selection

if st.session_state.menu_selection == 'Curriculos':
    render_curriculum()
elif st.session_state.menu_selection == 'Vagas':
    render_jobs()
elif st.session_state.menu_selection == 'Analise':
    render_analyse()
