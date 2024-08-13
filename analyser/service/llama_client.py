from dotenv import load_dotenv
from langchain_groq import ChatGroq
import re

load_dotenv()


class LlamaClient:
    def __init__(self, model_id="llama-3.1-70b-versatile"):
        self.model_id = model_id
        self.client = ChatGroq(model=model_id)
        
        
    def generate_response(self, prompt):
        response = self.client.invoke(prompt)
        return response.content

    def resume_cv(self, cv, job):
        prompt = f'''
            **Backstory:**
        **Backstory:**
        **Backstory:**
        - O objetivo é criar um prompt para um assistente que resuma um currículo em formato Markdown, incluindo a duração total de experiência do candidato. O resumo deve abranger os principais pontos do currículo, comparando-os com os requisitos da vaga. O assistente deve ser crítico ao analisar a compatibilidade do candidato com a vaga, destacando tanto pontos fortes quanto pontos fracos, como períodos curtos de emprego. A pretensão salarial deve ser mencionada em uma seção própria, se existir.

        **Expected Result:**
        - O assistente deve produzir um resumo claro e estruturado, destacando experiência, habilidades, educação, idiomas e uma análise crítica da compatibilidade com a vaga. A duração total da experiência profissional deve ser calculada e mencionada, e deve incluir uma avaliação detalhada de pontos fortes e fracos, além de uma seção separada para pretensão salarial, se mencionada.
        - O estilo deve ser formal e direto, semelhante a um relatório profissional ou revisão de desempenho.

        **Prompt:**

        Por favor, pegue o currículo completo fornecido e crie um resumo conciso em formato Markdown com base nos seguintes pontos:

        1. **Nome Completo**: Identificação do candidato.
        2. **Experiência**: Resumo das principais experiências profissionais, incluindo cargos, empresas e duração em anos.
        3. **Duração Total de Experiência**: Cálculo e menção da duração total de experiência profissional.
        4. **Habilidades**: Competências técnicas e interpessoais relevantes.
        5. **Educação**: Formação acadêmica.
        6. **Idiomas**: Idiomas falados e níveis de proficiência.
        7. **Pretensão Salarial**: Menção da pretensão salarial, caso exista no currículo.
        8. **Opinião**: Analise os pontos do currículo que combinam com a descrição da vaga e destaque os pontos que talvez estejam faltando em relação ao que a vaga esperava. Seja crítico e detalhado, mencionando períodos curtos de emprego.

        ---

        **Input Curriculo:**

        **Currículo Completo:**
        ```
        {cv}
        ```

        **Input Vaga:**

        **Descrição da Vaga:**
        ```
        {job}
        ```

        **Resumo do Currículo em Markdown:**

        ```markdown
        ## Nome Completo
        - Identificação do candidato.

        ## Experiência
        - Resumo das principais experiências profissionais, incluindo cargos, empresas e duração em anos.

        ## Duração Total de Experiência
        - Cálculo e menção da duração total de experiência profissional.

        ## Habilidades
        - Competências técnicas e interpessoais relevantes.

        ## Educação
        - Formação acadêmica.

        ## Idiomas
        - Idiomas falados e níveis de proficiência.

        ## Pretensão Salarial
        - Menção da pretensão salarial, caso exista no currículo.

        ## Opinião
        - Análise dos fatores do currículo que combinam com a descrição da vaga e destaque dos pontos que talvez estejam faltando em relação ao que a vaga esperava. Seja crítico e detalhado, mencionando períodos curtos de emprego. Essa parte tem que estar descritiva, como se fosse um feedback ultra detalhado com um comparativo entre a vaga e o candidato
        ```
        '''
        result_raw = self.generate_response(prompt)
        try:
            result = result_raw.split('```markdown')[1]
        except:
            result = result_raw
        return result

    def generate_score(self, resum, job):
        prompt = f'''
            **Objetivo:** Avaliar e pontuar um currículo com base na descrição de uma vaga específica. A avaliação deve considerar diferentes seções do currículo, atribuindo uma nota de 0 a 10 para cada seção, de acordo com os critérios definidos. A nota final será uma média ponderada dessas avaliações.

            **Instruções:**

            Com base na **descrição da vaga** fornecida abaixo:

            **Descrição da Vaga:** `{job}`

            E no **resumo do currículo** fornecido abaixo:

            **Resumo do Currículo:** `{resum}`

            Por favor, avalie e atribua uma nota para cada uma das seguintes seções:

            1. **Experiência (Peso: 30%)**:
                - Avalie a relevância da experiência profissional do candidato em relação à vaga.
                - Considere a duração total de experiência, a continuidade dos empregos e a profundidade das responsabilidades desempenhadas.
                - Se a experiência não tiver nenhuma relação com a vaga, a pontuação deve ser 0.
                - Atribua uma nota de 0 a 10, onde 0 indica nenhuma relevância e 10 indica alta relevância e adequação para a vaga.

            2. **Habilidades Técnicas (Peso: 25%)**:
                - Verifique se as habilidades técnicas mencionadas no currículo estão alinhadas com os requisitos da vaga.
                - Considere o nível de proficiência em cada habilidade e a diversidade das tecnologias conhecidas.
                - Se as habilidades técnicas não tiverem nenhuma relação com a vaga, a pontuação deve ser 0.
                - Atribua uma nota de 0 a 10, onde 0 indica ausência de habilidades relevantes e 10 indica plena adequação.

            3. **Educação (Peso: 10%)**:
                - Avalie o nível de educação do candidato em relação aos requisitos da vaga.
                - Considere a relevância da formação acadêmica e quaisquer certificações adicionais.
                - Se a educação não tiver nenhuma relação com a vaga, a pontuação deve ser 0.
                - Atribua uma nota de 0 a 10, onde 0 indica nenhuma educação relevante e 10 indica a educação ideal para a vaga.

            4. **Idiomas (Peso: 10%)**:
                - Analise os idiomas conhecidos pelo candidato e sua importância para a vaga.
                - Considere o nível de proficiência em cada idioma e sua aplicabilidade no contexto do trabalho.
                - Mesmo que os idiomas não sejam críticos para a vaga, ainda assim atribua uma nota com base na proficiência demonstrada, podendo variar de 0 a 10.

            5. **Pontos Fortes (Peso: 15%)**:
                - Avalie os pontos fortes mencionados no currículo e sua relevância para a vaga.
                - Considere como essas qualidades podem agregar valor à posição oferecida.
                - Se os pontos fortes não tiverem nenhuma relação com a vaga, a pontuação deve ser 0.
                - Atribua uma nota de 0 a 10, onde 0 indica nenhuma qualidade relevante e 10 indica qualidades ideais para a vaga.

            6. **Pontos Fracos (Desconto de até 10%)**:
                - Identifique os pontos fracos mencionados ou implícitos no currículo.
                - Avalie a gravidade desses pontos fracos em relação às exigências da vaga.
                - Atribua uma nota de 0 a 10, onde 0 indica que os pontos fracos são extremamente prejudiciais e 10 indica que os pontos fracos são insignificantes ou inexistentes.
                - **Nota:** Essa seção pode reduzir a pontuação final; utilize-a com cuidado para ajustar a nota de acordo com a importância desses pontos fracos.

            **Nota Importante:** Seja extremamente criterioso e técnico ao atribuir as notas. Uma nota 7.0 ou superior deve ser considerada uma boa pontuação, refletindo uma forte adequação às exigências da vaga. Todos os critérios da vaga devem ser rigorosamente avaliados antes de atribuir as notas.

            **Atenção:** Não inclua observações ou justificativas, apenas as pontuações.

            **Exemplo de Output Esperado:**

            ```
            **Experiência:** Nota x.x/10
            **Habilidades Técnicas:** Nota x.x/10
            **Educação:** Nota x.x/10
            **Idiomas:** Nota x.x/10
            **Pontos Fortes:** Nota x.x/10
            **Pontos Fracos:** Nota x.x/10

            **Pontuação Final:** x.x/10
            ```
        '''
        result_raw = self.generate_response(prompt)
        pattern = r"\*\*Pontuação Final:\*\* (\d+\.\d+)/10"
        try:
            score = float(re.search(pattern, result_raw).group(1))
            return score if score > 0.0 else 0.1
        except:
            self.generate_score(resum, job)
         

