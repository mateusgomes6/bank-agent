"""Credit Interview Agent - Financial interview for credit score recalculation."""
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.agents.base_agent import BaseAgent
from src.tools.score_tools import calculate_credit_score, update_score_in_database
from src.tools.csv_tools import get_cliente_by_cpf
from src.utils.constants import SCORE_WEIGHTS
from src.utils.config import GOOGLE_API_KEY, LLM_MODEL


class CreditInterviewAgent(BaseAgent):
    """Agent responsible for conducting financial interviews."""
    
    def __init__(self):
        """Initialize Credit Interview Agent."""
        super().__init__("Agente de Entrevista de Crédito", "Especialista em Análise Financeira")
        self.current_cpf = None
        self.interview_data: Dict[str, Any] = {}
        self.interview_step = 0
        self.interview_questions = [
            "Qual é sua renda mensal aproximada (em reais)?",
            "Qual é seu tipo de emprego? (formal, autônomo ou desempregado)",
            "Quais são suas despesas fixas mensais (aluguel, contas, etc)?",
            "Quantas pessoas dependem financeiramente de você? (incluindo você mesmo)",
            "Você possui dívidas ativas? (Responda sim ou não)"
        ]
    
    async def handle_request(self, user_message: str, cpf: str) -> str:
        """Handle interview request."""
        self.current_cpf = cpf
        
        if self.interview_step == 0:
            self.interview_step = 1
            return self._get_welcome_message() + "\n\n" + self.interview_questions[0]
        
        return await self.process_interview_answer(user_message)
    
    def _get_welcome_message(self) -> str:
        """Get welcome message for interview."""
        cliente = get_cliente_by_cpf(self.current_cpf)
        name = cliente.get('nome', 'Cliente') if cliente else 'Cliente'
        
        return f"""
        Olá {name}! 
        
        Obrigado por escolher participar da entrevista de crédito. 
        Vou fazer algumas perguntas sobre sua situação financeira para recalcular seu score de crédito.
        
        Suas respostas serão confidenciais e usadas apenas para análise creditícia.
        """
    
    async def process_interview_answer(self, user_response: str) -> str:
        """Process interview answer and move to next question."""
        try:
            # Store answer based on current step
            if self.interview_step == 1:
                self.interview_data['renda_mensal'] = float(user_response.replace(",", "."))
                self.interview_step = 2
                return self.interview_questions[1]
            
            elif self.interview_step == 2:
                emprego_tipo = user_response.lower().strip()
                if emprego_tipo not in ["formal", "autônomo", "desempregado"]:
                    return "Por favor, responda com: formal, autônomo ou desempregado"
                self.interview_data['tipo_emprego'] = emprego_tipo
                self.interview_step = 3
                return self.interview_questions[2]
            
            elif self.interview_step == 3:
                self.interview_data['despesas_fixas'] = float(user_response.replace(",", "."))
                self.interview_step = 4
                return self.interview_questions[3]
            
            elif self.interview_step == 4:
                self.interview_data['num_dependentes'] = int(user_response)
                self.interview_step = 5
                return self.interview_questions[4]
            
            elif self.interview_step == 5:
                divida_response = user_response.lower().strip()
                if divida_response not in ["sim", "não", "yes", "no", "s", "n"]:
                    return "Por favor, responda com: sim ou não"
                self.interview_data['tem_dividas'] = divida_response
                
                # Calculate new score
                return await self.finalize_interview()
        
        except ValueError:
            return "Por favor, forneça uma resposta válida."
    
    async def finalize_interview(self) -> str:
        """Finalize interview and calculate new score."""
        try:
            # Calculate new score
            new_score = calculate_credit_score(
                renda_mensal=self.interview_data['renda_mensal'],
                tipo_emprego=self.interview_data['tipo_emprego'],
                despesas_fixas=self.interview_data['despesas_fixas'],
                num_dependentes=self.interview_data['num_dependentes'],
                tem_dividas=self.interview_data['tem_dividas']
            )
            
            # Update score in database
            success, message = update_score_in_database(self.current_cpf, new_score)
            
            if success:
                self.interview_step = 0  # Reset for next client
                return f"""{message}

Agora que seu score foi atualizado, gostaria que você retornasse ao Agente de Crédito 
para renovar sua solicitação de aumento de limite com seu novo score.

ROUTE:CREDITO"""
            else:
                return f"Houve um erro ao atualizar seu score. {message}"
        
        except Exception as e:
            return f"Erro ao finalizar entrevista: {str(e)}"
    
    def get_interview_progress(self) -> Dict[str, Any]:
        """Get current interview progress."""
        return {
            "etapa_atual": self.interview_step,
            "total_etapas": len(self.interview_questions),
            "dados_coletados": self.interview_data,
            "proxima_pergunta": self.interview_questions[self.interview_step] if self.interview_step < len(self.interview_questions) else None
        }
