"""Triage Agent - Customer authentication and routing."""
from typing import Tuple, Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.agents.base_agent import BaseAgent
from src.tools.auth_tools import authenticate_client, validate_cpf_format, validate_date_format
from src.utils.constants import MESSAGES
from src.utils.config import GOOGLE_API_KEY, LLM_MODEL


class TriageAgent(BaseAgent):
    """Agent responsible for customer authentication and initial triage."""
    
    def __init__(self):
        """Initialize Triage Agent."""
        super().__init__("Agente de Triagem", "Recepcionista bancário")
        self.auth_attempts = 0
        self.max_attempts = 3
        self.authenticated = False
        self.authenticated_client: Optional[Dict[str, Any]] = None
    
    async def handle_request(self, user_message: str) -> str:
        """Handle triage request."""
        return await self.process_message(user_message)
    
    async def process_message(self, user_message: str) -> str:
        """Process user message in triage flow."""
        
        # If not authenticated yet, proceed with authentication
        if not self.authenticated:
            return await self.authenticate()
        
        # If authenticated, identify next step
        return await self.identify_next_agent(user_message)
    
    async def start_greeting(self) -> str:
        """Start the conversation with greeting."""
        self.set_context("step", "greeting")
        return MESSAGES["greeting"]
    
    async def authenticate(self) -> str:
        """Conduct authentication process."""
        step = self.get_context("step")
        
        if step is None:
            self.set_context("step", "ask_cpf")
            return "Para iniciar, preciso verificar algumas informações. Qual é o seu CPF?"
        
        if step == "ask_cpf":
            # Will be handled in the main flow
            return ""
        
        if step == "ask_birth_date":
            # Will be handled in the main flow
            return ""
    
    def authenticate_with_credentials(self, cpf: str, data_nascimento: str) -> Tuple[bool, str]:
        """Authenticate customer with CPF and birth date."""
        # Validate formats
        if not validate_cpf_format(cpf):
            return False, "CPF inválido. Por favor, forneça um CPF com 11 dígitos."
        
        if not validate_date_format(data_nascimento):
            return False, "Data inválida. Por favor, use o formato YYYY-MM-DD (ex: 1990-05-15)."
        
        # Attempt authentication
        success, client_data = authenticate_client(cpf, data_nascimento)
        
        if success:
            self.authenticated = True
            self.authenticated_client = client_data
            self.set_context("authenticated_client", client_data)
            self.set_context("cpf", cpf)
            return True, f"{MESSAGES['auth_success']} Bem-vindo, {client_data.get('nome')}!"
        
        # Track failed attempt
        self.auth_attempts += 1
        
        if self.auth_attempts < self.max_attempts:
            remaining = self.max_attempts - self.auth_attempts
            return False, f"{MESSAGES['auth_failed']} Você tem mais {remaining} tentativa(s)."
        
        return False, MESSAGES["max_attempts"]
    
    async def identify_next_agent(self, user_message: str) -> str:
        """
        Use LLM to identify which agent should handle the request.
        Returns routing instruction or response.
        """
        prompt = f"""
        Você é um assistente de triagem bancário. Com base na mensagem do cliente abaixo, 
        classifique qual tipo de atendimento é necessário:
        
        Categorias:
        - CREDITO: Para consultar limite de crédito ou solicitar aumento
        - ENTREVISTA: Para atualizar score de crédito (apenas se o cliente aceitar após rejeição)
        - CAMBIO: Para consultar cotação de moedas
        - ENCERRAMENTO: Se o cliente quer encerrar
        - OUTRO: Se não se encaixa nas categorias
        
        Mensagem do cliente: "{user_message}"
        
        Responda APENAS com: CREDITO, ENTREVISTA, CAMBIO, ENCERRAMENTO ou OUTRO
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        category = response.content.strip().upper()
        
        self.set_context("next_agent", category)
        
        if category == "ENCERRAMENTO":
            return f"{MESSAGES['farewell']}"
        
        # Return category for router to handle
        return f"ROUTE:{category}"
    
    def is_authenticated(self) -> bool:
        """Check if customer is authenticated."""
        return self.authenticated
    
    def has_max_attempts_exceeded(self) -> bool:
        """Check if max authentication attempts exceeded."""
        return self.auth_attempts >= self.max_attempts
