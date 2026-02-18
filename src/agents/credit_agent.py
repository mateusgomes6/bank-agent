"""Credit Agent - Credit limit consultation and increase requests."""
from typing import Optional, Dict, Any
from datetime import datetime
from langchain_core.messages import HumanMessage
from src.agents.base_agent import BaseAgent
from src.tools.csv_tools import get_cliente_by_cpf, create_credit_limit_request, update_credit_limit_request_status, get_client_latest_request
from src.tools.score_tools import check_credit_limit_approval


class CreditAgent(BaseAgent):
    """Agent responsible for credit limit operations."""
    
    def __init__(self):
        """Initialize Credit Agent."""
        super().__init__("Agente de Crédito", "Especialista em Crédito")
        self.current_cpf = None
        self.current_cliente = None
    
    async def handle_request(self, user_message: str, cpf: str) -> str:
        """Handle credit-related request."""
        self.current_cpf = cpf
        self.current_cliente = get_cliente_by_cpf(cpf)
        
        if not self.current_cliente:
            return "Desculpe, não consegui recuperar suas informações de crédito."
        
        return await self.process_credit_request(user_message)
    
    async def process_credit_request(self, user_message: str) -> str:
        """Process credit request using LLM."""
        prompt = f"""
        Você é um agente de crédito bancário. Seu cliente, {self.current_cliente.get('nome')}, 
        fez a seguinte solicitação: "{user_message}"
        
        Dados do cliente:
        - Limite atual: R$ {self.current_cliente.get('limite_credito', 0):.2f}
        - Score: {self.current_cliente.get('score', 0)}
        
        Se o cliente está solicitando:
        1. CONSULTA DE LIMITE: Informar o limite atual
        2. AUMENTO DE LIMITE: Solicitar o novo limite desejado
        3. OUTRO: Informar que não pode ajudar com isso
        
        Responda de forma natural, como um atendente bancário. Se o cliente quer saber o limite, 
        informe o valor atual. Se quer aumentar, peça o novo valor desejado.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    def consult_credit_limit(self, cpf: str) -> str:
        """Consult client's current credit limit."""
        cliente = get_cliente_by_cpf(cpf)
        if not cliente:
            return "Cliente não encontrado."
        
        limite = cliente.get('limite_credito', 0)
        return f"Seu limite de crédito atual é de R$ {limite:.2f}."
    
    async def process_limit_increase_request(self, cpf: str, novo_limite: float) -> str:
        """Process credit limit increase request."""
        try:
            # Validate new limit
            if novo_limite <= 0:
                return "O novo limite deve ser maior que zero."
            
            cliente = get_cliente_by_cpf(cpf)
            if not cliente:
                return "Cliente não encontrado."
            
            limite_atual = cliente.get('limite_credito', 0)
            
            if novo_limite <= limite_atual:
                return f"O novo limite deve ser maior que o limite atual (R$ {limite_atual:.2f})."
            
            # Create the request
            success = create_credit_limit_request(
                cpf=cpf,
                limite_atual=limite_atual,
                novo_limite=novo_limite,
                status="pendente"
            )
            
            if not success:
                return "Erro ao criar a solicitação. Tente novamente."
            
            # Check credit approval
            approved, message = check_credit_limit_approval(cpf, novo_limite)
            
            # Update request status
            status = "aprovado" if approved else "rejeitado"
            update_credit_limit_request_status(cpf, status)
            
            if approved:
                return f"{message}\nSua solicitação foi aprovada!"
            else:
                return f"{message}\n\nGostaria de participar de uma entrevista de crédito para tentar melhorar seu score?"
        
        except Exception as e:
            return f"Erro ao processar solicitação: {str(e)}"
    
    def get_client_info(self, cpf: str) -> Dict[str, Any]:
        """Get client information."""
        cliente = get_cliente_by_cpf(cpf)
        if cliente:
            return {
                "nome": cliente.get('nome'),
                "cpf": cliente.get('cpf'),
                "limite_credito": cliente.get('limite_credito'),
                "score": cliente.get('score')
            }
        return {}
