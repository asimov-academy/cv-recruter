import uuid
import streamlit as st
from streamlit_option_menu import option_menu
from routes.job import JobRoute
from routes.analyse import AnalyseRoute
from routes.curriculum import CurriculumRoute

from streamlit_agraph import agraph, Node, Edge, Config

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def radar_chart_plotly_express(categories, scores):
    """
    Radar Chart (Plotly Express) com fill='toself'.
    Cores personalizadas: linha vermelha.
    """
    df = pd.DataFrame(dict(r=scores, theta=categories))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='red')  # cor vermelha
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,5])),
        showlegend=False
    )
    return fig

def radar_chart_basic_scatterpolar(categories, scores):
    """
    Radar Chart básico com go.Scatterpolar (um único trace).
    Cor customizada (verde).
    """
    fig = go.Figure(data=go.Scatterpolar(
        r=scores, theta=categories, fill='toself', line_color='green'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,5])),
        showlegend=False
    )
    return fig

def radar_chart_multiple_trace(categories, job_scores, resum_scores):
    """
    Radar Chart com go.Scatterpolar e múltiplos traces
    (Exemplo: 'Produto A' e 'Produto B'), cada um com cor diferente.
    """
    r_values_A = job_scores
    r_values_B = resum_scores

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_values_A,
        theta=categories,
        fill='toself',
        name='Perfil da Vaga',
        line_color='blue'
    ))
    fig.add_trace(go.Scatterpolar(
        r=r_values_B,
        theta=categories,
        fill='toself',
        name='Candidato',
        line_color='orange'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,5])),
        showlegend=True
    )
    return fig


st.set_page_config(layout="wide", page_title="Recruter", page_icon=":brain:")

def render_analyse():
    # Exemplo: supondo que você tenha uma classe para análise
    analyse_route = AnalyseRoute()

    option = st.selectbox("Escolha sua vaga:", analyse_route.jobs, index=None)
    if option:
        st.subheader('Classificação dos Candidatos')
        with st.expander('Gráfico Geral de Pontuação'):
            bar = st.empty()


        # Renderiza a tabela de candidatos (AgGrid ou outro) e retorna "candidates" se houver seleções
        candidates = analyse_route.render_grid(option)

        # Gráfico de barras geral
        bar.bar_chart(analyse_route._create_dataframe_to_analyse(), x="Nome", y="score", color="Nome", horizontal=True)

        # Botão de limpar análise
        if st.button('Limpar Análise'):
            analyse_route.clean_analyse()
            st.rerun()

        # # ----------------------------------------------------------------------------
        # #        GRAFO DE TODOS OS CANDIDATOS X SUAS HABILIDADES
        # # ----------------------------------------------------------------------------
        # if not analyse_route._create_dataframe_to_analyse().empty:
        #     st.subheader("Grafo de Candidatos x Competências")

        #     candidate_skills_dict = {}
        #     for idx, row in analyse_route._create_dataframe_to_analyse().iterrows():
        #         name = row["Nome"]
        #         skills = row["Habilidades"]  # Deve ser uma lista de strings
        #         candidate_skills_dict[name] = skills
        

        #     # Crie listas de nós (Node) e arestas (Edge)
        #     nodes = []
        #     edges = []

        #     skill_set = set()
        #     for skills_list in candidate_skills_dict.values():
        #         skill_set.update(skills_list)

        #     # Adiciona nós de candidatos (menor size e label é o próprio nome)
        #     for candidate in candidate_skills_dict:
        #         nodes.append(Node(
        #             id=candidate,
        #             label=candidate,
        #             size=8,           # <-- Deixando o nó bem menor
        #             color="#4169E1"    # Dourado
        #         ))

        #     # Adiciona nós de skills (idem, menor size)
        #     for skill in skill_set:
        #         nodes.append(Node(
        #             id=skill,
        #             label=skill,
        #             size=5,          # <-- Menor ainda que o candidato
        #             color="#2E2E2E"   # Cinza escuro
        #         ))

        #     # Cria edges (Candidate -> Skill)
        #     for candidate, skills_list in candidate_skills_dict.items():
        #         for skill in skills_list:
        #             edges.append(Edge(
        #                 source=candidate,
        #                 target=skill,
        #                 color="#787878"  # Aresta branca
        #             ))

        #     # Ajusta configuração do agraph
        #     config = Config(
        #         width="100%",          # Ocupa toda a largura disponível
        #         height=500,            # Ajuste conforme desejar
        #         directed=False,        
        #         nodeHighlightBehavior=True,
        #         highlightColor="#F0F0A0",
        #         collapsible=True,
        #         physics=True,          # Ativa o layout "força" que espalha os nós
        #         node={
        #             # Essas configs são passadas para react-d3-graph
        #             "labelProperty": "label",       # Usa o campo 'label' de cada Node
        #             "renderLabel": True,
        #             "labelPosition": "top",         # Tenta posicionar o texto acima do nó
        #             "fontColor": "#FFFFFF",       # Branco forçado
        #             "fontSize": 12,
        #             "fontWeight": "normal",
        #             "highlightFontColor": "#800000",  # Também branco no hover/seleção
        #             "highlightFontSize": 12,
        #             "highlightFontWeight": "bold", 
        #         },
        #         link={
        #             "renderLabel": True           # Se quiser rótulos nas arestas, troque para True
        #         },
        #         d3={
        #             "linkLength": 150,             # Aumenta o espaço entre os nós
        #             "gravity": -200                # Ajuste para espalhar mais ou menos
        #         }
        #     )

        #     # Renderiza o grafo
        #     agraph(
        #         nodes=nodes,
        #         edges=edges,
        #         config=config
        #     )
            
            

        

        # ----------------------------------------------------------------------------
        #         RENDERIZA A VISUALIZAÇÃO DETALHADA DE CADA CANDIDATO
        # ----------------------------------------------------------------------------
        if not candidates.empty:
            cols = st.columns(len(candidates))
            for idx, row_data in enumerate(candidates.iterrows()):
                _, row = row_data
                with cols[idx]:
                    with st.container():
                        candidate_resum = analyse_route.get_resum_by_id(row['resum_id'])
                        if candidate_resum:
                            st.header(row['Nome'])
                            
                            competence, strategies, qualifications = analyse_route.get_categories_job()

                            
                            # Exemplos de Radar Charts
                            fig1 = radar_chart_plotly_express(competence, candidate_resum.get('score_competence'))
                            fig2 = radar_chart_basic_scatterpolar(strategies, candidate_resum.get('score_strategies'))
                            fig3 = radar_chart_multiple_trace(qualifications, analyse_route.job.get('score_qualifications'), candidate_resum.get('score_competence'))

                            # Tira títulos do layout
                            fig1.update_layout(title="")
                            fig2.update_layout(title="")
                            fig3.update_layout(title="")

                            # Exibe os 3 gráficos lado a lado
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.plotly_chart(fig1, use_container_width=True)
                            with c2:
                                st.plotly_chart(fig2, use_container_width=True)
                            with c3:
                                st.plotly_chart(fig3, use_container_width=True)
                                
                            # CSS personalizado para expanders
                            st.markdown("""
                                <style>
                                .scrollable-expander {
                                    height: 900px; 
                                    overflow-y: auto;
                                    padding: 10px;
                                    background-color:rgb(253, 253, 253); /* Cinza escuro */
                                    border: 1px solidrgb(255, 0, 34); /* Borda dourada */
                                    border-radius: 5px;
                                    font-family: 'Arial', sans-serif; 
                                    line-height: 1.5; 
                                    color:rgb(20, 19, 19);  /* Texto branco */
                                }
                                </style>
                                """, unsafe_allow_html=True)

                            with st.expander('Resumo do Curriculum'):
                                st.markdown(
                                    f"""
                                    <div class="scrollable-expander">
                                    {candidate_resum.get('content')}
                                    """,
                                    unsafe_allow_html=True,
                                )
                            with st.expander('Análise do Candidato'):
                                st.markdown(
                                    f"""
                                    <div class="scrollable-expander">
                                    {candidate_resum.get('opnion')}
                                    """,
                                    unsafe_allow_html=True,
                                )

                            # Botão de download do PDF
                            with open(candidate_resum.get('file'), 'rb') as file:
                                st.download_button(
                                    label=f"Download Currículo {row['Nome']}",
                                    data=file.read(),
                                    file_name=f"{row['Nome']}.pdf",
                                    mime="application/pdf",
                                    key=str(uuid.uuid1())
                                )

def render_curriculum():
    curriculum_route = CurriculumRoute()
    option = st.selectbox("Escolha sua vaga:", curriculum_route.jobs, index=None)
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
        
    option = st.selectbox("Escolha sua vaga:", job_route.jobs, index=None)
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
        icons=['card-text', 'file-earmark-pdf', 'clipboard-data'], 
        menu_icon="cast", 
        default_index=0
    )
    st.session_state.menu_selection = menu_selection

if st.session_state.menu_selection == 'Curriculos':
    render_curriculum()
elif st.session_state.menu_selection == 'Vagas':
    render_jobs()
elif st.session_state.menu_selection == 'Analise':
    render_analyse()
