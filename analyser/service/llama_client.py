from dotenv import load_dotenv
from ollama.repositories import HTTPXSyncClient
from ollama.services import SyncCompletionService
from ollama.models import GenerateCompletionRequest
import re

load_dotenv()


class LlamaClient:
    def __init__(self, model_id="llama3.1:8b-instruct-fp16", keep_alive = '50s'):
        self.sync_client = HTTPXSyncClient(base_url="http://localhost:11434/api")
        self.client = SyncCompletionService(self.sync_client, model=model_id, keep_alive=keep_alive)
        self.model_id = model_id
        
    def generate_response(self, prompt: GenerateCompletionRequest):
        response = self.client.generate_completion(prompt)
        return response.response

    def resume_cv(self, cv, job):
        prompt = f'''
            **Solicitação de Resumo de Currículo em Markdown:**
            
            # Curriculo do candidato para resumir:
            
            {cv}

            Por favor, gere um resumo do currículo fornecido, formatado em Markdown, seguindo rigorosamente o modelo abaixo. **Não adicione seções extras, tabelas ou qualquer outro tipo de formatação diferente da especificada.** Preencha cada seção com as informações relevantes, garantindo que o resumo seja preciso e focado.

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

        result_raw = self.generate_response(GenerateCompletionRequest(prompt=prompt))
        try:
            result = result_raw.split('```markdown')[1]
        except:
            result = result_raw
        return result

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
        result_raw = self.generate_response(GenerateCompletionRequest(prompt=prompt))
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
        result_raw = self.generate_response(GenerateCompletionRequest(prompt=prompt))
        result = result_raw        
        return result

