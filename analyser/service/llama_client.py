from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import re

load_dotenv()


class LlamaClient:
    def __init__(self):
        self.client = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.1,
        )

    def generate_response(self, prompt):
        response = self.client.invoke(prompt)
        return response.content
    
    def score_competence(self, job, qualifications):
        prompt = f'''
                Abaixo segue um exemplo de **prompt** que, a partir da **descrição de uma vaga** e de suas **qualificações** definidas, solicita à IA que **gere o score mínimo** necessário para cada uma das qualificações. Esse score poderá ser usado como um parâmetro de corte ou referência para avaliar candidatos.

                ### Prompt: Definir Score Necessário para Vaga

                Você é um consultor de RH responsável por definir o nível mínimo de proficiência exigido para cada qualificação em uma vaga. 
                
                Receba a seguir:

                Vaga:
                {job}

                Qualificações da vaga:
                {qualifications}

                Com base na descrição da vaga, atribua um score mínimo (entre 1 e 5, podendo ser decimal) para cada uma das qualificações. 
                Esses scores representam o nível de proficiência mínimo esperado de um candidato para ser considerado adequado à vaga.
                Retorne apenas a lista de 5 scores, cada um em uma linha separada, sem comentários adicionais.

                **Exemplo de resultado esperado (meramente ilustrativo):**
                3.5
                4.0
                2.8
                4.3
                3.0
            '''
        result_raw = self.generate_response(prompt)
        scores = []
        for line in result_raw.strip().split('\n'):
            line = line.strip()
            try:
                scores.append(float(line))
            except ValueError:
                # Ignora linhas que não possam ser convertidas em float
                pass

        return scores
        
    def score_qualifications(self, cv, qualifications):
        prompt = f'''
                Abaixo está um **exemplo de prompt único** que recebe o **currículo de um candidato** e uma **lista de 5 qualificações**, pedindo à IA que avalie cada qualificação com uma **nota de 1 a 5 (com uso de decimais permitido)**, retornando cada pontuação em **linhas separadas**.

                ---

                ### Prompt

                ```
                Você é um avaliador imparcial e recebeu as seguintes informações:
                Currículo do candidato:
                {cv}

                Lista de 5 qualificações:
                {qualifications}

                Com base no que está descrito no currículo, avalie o nível de atendimento a cada uma dessas 5 qualificações 
                atribuindo uma nota de 1 a 5 (podendo usar números decimais). 
                Retorne apenas as 5 notas, cada uma em uma linha separada, sem comentários adicionais.
                ```

                **Exemplo de saída esperada** (meramente ilustrativa):
                
                2.8
                4.2
                3.0
                4.9
                1.7
            '''
        result_raw = self.generate_response(prompt)
        scores = []
        for line in result_raw.strip().split('\n'):
            line = line.strip()
            try:
                scores.append(float(line))
            except ValueError:
                # Ignora linhas que não possam ser convertidas em float
                pass

        return scores


    def resume_cv(self, cv):
        prompt = f'''
            **Solicitação de Resumo de Currículo em Markdown:**
            
            # Curriculo do candidato para resumir:
            
            {cv}

            Por favor, gere um resumo do currículo fornecido, formatado em Markdown, 
            seguindo rigorosamente o modelo abaixo. **Não adicione seções extras, 
            tabelas ou qualquer outro tipo de formatação diferente da especificada.
            * Preencha cada seção com as informações relevantes, 
            garantindo que o resumo seja preciso e focado.

            **Formato de Output Esperado:**

            ```markdown
            ## Nome Completo
            nome_completo aqui

            ## Experiência
            experiencia aqui

            ## Habilidades 
            habilidades aqui

            ## Educação 
            educacao aqui

            ## Idiomas 
            idiomas aqui

            '''

        result_raw = self.generate_response(prompt)
        try:
            result = result_raw.split('```markdown')[1]
        except:
            result = result_raw
        return result
    
    def create_competence(self, job):
        prompt = f'''
                    Você é um consultor especializado em tecnologia. 
                    Com base na vaga a seguir: {job}, crie 5 categorias para um “Radar de Competências e Ferramentas de Desenvolvimento” 
                    que abranjam linguagens de programação, frameworks, bibliotecas, sistemas de controle de versão, plataformas de cloud, 
                    ferramentas de automação e outros recursos tecnológicos relevantes para a função descrita.
                    
                    Essas categorias devem conter apenas uma palavra ou um nome composto por 2 palavras, nao mais que isso.
                    você deve responder apenas as categorias separadas por nova linha
                '''
        result_raw = self.generate_response(prompt)
        return [line.strip() for line in result_raw.strip().split('\n') if line.strip()]
    
    def create_strategies(self, job):
        prompt = f'''
                    Quero que você atue como um consultor de marketing digital para a vaga de {job}.
                    Crie uma lista de 5 categorias que destaquem as principais plataformas, estratégias e métodos de otimização de campanhas 
                    de marketing relevantes para essa vaga. 
                    Considere ferramentas de anúncios, SEO, testes A/B, CRM e outras áreas que se encaixem no contexto de {job}.
                    
                    Essas categorias devem conter apenas uma palavra ou um nome composto por 2 palavras, nao mais que isso.
                    você deve responder apenas as categorias separadas por nova linha
                '''
        result_raw = self.generate_response(prompt)
        return [line.strip() for line in result_raw.strip().split('\n') if line.strip()]


    def create_qualification(self, job):
        prompt = f'''
                Quero que você atue como um consultor de RH especializado na vaga de {job}.
                Crie 5 categorias que representem o perfil profissional e as qualificações desejadas para o candidato. 
                Pense em senioridade, formação, certificações, disponibilidade, proficiência em idiomas ou outras 
                competências comportamentais e de background relevantes para {job}.
                
                Essas categorias devem conter apenas uma palavra ou um nome composto por 2 palavras, nao mais que isso.
                você deve responder apenas as categorias separadas por nova linha
                '''
        result_raw = self.generate_response(prompt)
        return [line.strip() for line in result_raw.strip().split('\n') if line.strip()]


    def generate_score(self, cv, job):
        prompt = f'''
            **Objetivo:** Avaliar um currículo com base em uma vaga específica e calcular a pontuação final. A nota máxima é 10.0.

            **Instruções:**

            1. **Experiência (Peso: 30%)**: Avalie a relevância da experiência em relação à vaga.
            2. **Habilidades Técnicas (Peso: 25%)**: Verifique o alinhamento das habilidades técnicas com os requisitos da vaga.
            3. **Educação (Peso: 10%)**: Avalie a relevância da formação acadêmica para a vaga.
            4. **Idiomas (Peso: 10%)**: Avalie os idiomas e sua proficiência em relação à vaga.
            5. **Pontos Fortes (Peso: 15%)**: Avalie a relevância dos pontos fortes para a vaga.
            6. **Pontos Fracos (Desconto de até 10%)**: Avalie a gravidade dos pontos fracos em relação à vaga.

            **Nota Final:** Calcule a média ponderada das notas das seções, com uma nota máxima de 10.0.
            
            Curriculo do candidato
            
            {cv}
            
            Vaga que o candidato está se candidatando
            
            {job}

            **Output Esperado:**
            ```
            Pontuação Final: x.x
            ```
            
            **Atenção:** Seja rigoroso ao atribuir as notas. A nota máxima é 10.0, e o output deve conter apenas "Pontuação Final: x.x".
        
        '''
        result_raw = self.generate_response(prompt)
        pattern = r"(?i)Pontuação Final[:\s]*([\d,.]+(?:/\d{1,2})?)"
        try:
            print('===================================================================================================================')
            print(result_raw)
            re_match = re.search(pattern, result_raw).group(1)
            if '/' in re_match:
                re_match = re_match.split('/')[0]
            print(re_match)
            score = float(re_match.replace(',', '.'))
            print(f'{type(score)}: {score}')
            print('===================================================================================================================')
            return score
        except:
            return self.generate_score(cv, job)

    def generate_opnion(self, cv, job):
        prompt = f'''
            vou te pedir ajuda para avaliação de candidatos para a vaga:
            
            {job}

            Você é um assistente de IA que incorpora a persona de um gestor de Recursos Humanos (RH) de empresas em rápido crescimento. Seu papel é atuar como um parceiro estratégico do negócio, fornecendo insights sobre os candidatos e dando recomendações para ajudar na tomada de decisão de contratação. Adote as seguintes características e estilo de comunicação em todas as interações: 

            1. Mentalidade e Visão: 
            - Mostre um foco notável em entender os requisitos da vaga e saber analisar os currículos dos candidatos a partir desses requisitos
            - Pense constantemente na estrutura organizacional da empresa e como as novas pessoas que entrarem no time podem se encaixar da melhor forma possível 
            - Demonstre uma motivação incessante para encontrar talentos e pessoas que realmente agreguem valor à companhia. 

            2. Estilo de Comunicação: 

            - Comunique-se de forma direta e franca, frequentemente usando frases curtas. 
            - Incorpore jargão técnico do meio corporativo de RH e use conceitos científicos da psicologia organizacional ao discutir ideias. 
            - Seja específico, constantemente citando exemplos para ilustrar ideias que você está explicando.
            - Solicite mais informações sempre que sentir necessidade para que sua resposta não fique genérica ou incompleta.

            3. Abordagem de Resolução de Problemas:

            - Aplique o pensamento de primeiros princípios para decompor problemas complexos em verdades fundamentais.
            - Use o ciclo PDCA (Plan, Do, Check e Act) como abordagem principal para todos os projetos da empresa
            - Tenha como base os 7 hábitos das pessoas altamente eficazes descritos por Stephen R. Covey para resolver problemas (especialmente o hábito de começar pelo objetivo) 
            - Enfatize a importância da iteração rápida e da adaptação em caso de falhas. 
            4. Filosofia de Negócios:
            
            - Priorize visão e impacto a longo prazo em detrimento de lucros de curto prazo.
            - Estenda a integração vertical e o desenvolvimento interno de todo o ecossistema de negócios.
            - Inspire-se no desejo de atrair e reter talentos que gostem de um ambiente desafiador e missões inspiradoras.
            - Foque em Metas e Indicadores para analisar se os projetos atuais são sustentáveis e prever quais novos projetos valem a pena ser iniciados.

            5. Estilo de Recrutamento:
            
            - Estabeleça metas ambiciosas, mas tenha clareza do motivo por trás dessas metas.
            - Crie um ambiente de trabalho que tenha baixa tolerância para incompetência ou burocracia.
            - Saiba negociar remunerações de forma que a pessoa se sinta bem com a contraproposta e ao mesmo tempo beneficie a empresa, reduzindo custos
            
            Curriculum do candidato a ser avaliado:
            
            {cv}
        '''
        result_raw = self.generate_response(prompt)
        result = result_raw 
        return result

