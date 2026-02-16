"""Agent Router - Routes requests between specialized agents."""
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from src.agents.triage_agent import TriageAgent
from src.agents.credit_agent import CreditAgent
from src.agents.credit_interview_agent import CreditInterviewAgent
from src.agents.exchange_agent import ExchangeAgent


class AgentType(Enum):
    TRIAGE = "triage"
    CREDIT = "credit"
    INTERVIEW = "interview"
    EXCHANGE = "exchange"


class AgentRouter:
    def __init__(self):
        self.triage_agent = TriageAgent()
        self.credit_agent = CreditAgent()
        self.interview_agent = CreditInterviewAgent()
        self.exchange_agent = ExchangeAgent()
        
        self.current_agent: Optional[AgentType] = None
        self.authenticated_cpf: Optional[str] = None
        self.conversation_state: Dict[str, Any] = {}
    
    async def process_message(self, user_message: str) -> str:
        # Start with triage if not authenticated
        if not self.authenticated_cpf:
            return await self.handle_triage(user_message)
        
        # Route to appropriate agent based on message content
        return await self.route_authenticated_message(user_message)
    
    async def handle_triage(self, user_message: str) -> str:
        """Handle authentication and initial triage."""
        if self.current_agent != AgentType.TRIAGE:
            self.current_agent = AgentType.TRIAGE
            response = await self.triage_agent.start_greeting()
            return response
        
        # Parse authentication attempts
        if "cpf" not in self.conversation_state:
            self.conversation_state["cpf"] = user_message.strip()
            self.conversation_state["auth_step"] = "awaiting_birth_date"
            return "Agora, qual é a sua data de nascimento? (formato: YYYY-MM-DD, ex: 1990-05-15)"
        
        # Second step - birth date
        if self.conversation_state.get("auth_step") == "awaiting_birth_date":
            cpf = self.conversation_state["cpf"]
            birth_date = user_message.strip()
            
            # Attempt authentication
            success, auth_message = self.triage_agent.authenticate_with_credentials(cpf, birth_date)
            
            if success:
                self.authenticated_cpf = cpf
                self.conversation_state = {}  # Clear state
                return auth_message + "\n\nComo posso ajudá-lo?"
            
            # Failed authentication
            if self.triage_agent.has_max_attempts_exceeded():
                self.reset()
                return auth_message
            
            # Ask for retry
            self.conversation_state["cpf"] = None
            self.conversation_state["auth_step"] = None
            return auth_message + "\n\nGostaria de tentar novamente? Por favor, forneça seu CPF:"
        
        return "Desculpe, algo deu errado. Vamos começar novamente. Qual é o seu CPF?"
    
    async def route_authenticated_message(self, user_message: str) -> str:
        """Route authenticated user message to appropriate agent."""
        user_msg_lower = user_message.lower()
        
        # Check for farewell
        if any(word in user_msg_lower for word in ["encerrar", "sair", "fim", "adeus", "tchau"]):
            self.reset()
            return "Obrigado pela preferência no Banco Ágil. Até logo!"
        
        # Check for credit operations
        if any(word in user_msg_lower for word in ["crédito", "limite", "aumento", "solicitação", "limite de crédito"]):
            self.current_agent = AgentType.CREDIT
            return await self.credit_agent.handle_request(user_message, self.authenticated_cpf)
        
        # Check for exchange operations
        if any(word in user_msg_lower for word in ["câmbio", "cotação", "dólar", "euro", "moeda", "estrangeira"]):
            self.current_agent = AgentType.EXCHANGE
            return await self.exchange_agent.handle_request(user_message)
        
        # Check for interview
        if any(word in user_msg_lower for word in ["entrevista", "score", "análise financeira", "re-análise"]):
            self.current_agent = AgentType.INTERVIEW
            return await self.interview_agent.handle_request(user_message, self.authenticated_cpf)
        
        # Default: ask for clarification
        return """Desculpe, não entendi direito. Como posso ajudá-lo?

Posso:
- Consultar ou solicitar aumento de limite de crédito
- Fornecer cotações de moedas
- Realizar uma entrevista para atualizar seu score de crédito

O que você gostaria de fazer?"""
    
    def reset(self) -> None:
        """Reset router state (used for logout)."""
        self.current_agent = None
        self.authenticated_cpf = None
        self.conversation_state = {}
        self.triage_agent.authenticated = False
        self.triage_agent.auth_attempts = 0
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.authenticated_cpf is not None
    
    def get_authenticated_cpf(self) -> Optional[str]:
        """Get authenticated user's CPF."""
        return self.authenticated_cpf
    
    def get_current_agent(self) -> Optional[str]:
        """Get current agent name."""
        if self.current_agent:
            return self.current_agent.value
        return None
