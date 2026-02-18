"""Exchange Agent - Currency exchange rate queries."""
from typing import Optional
from langchain_core.messages import HumanMessage
from src.agents.base_agent import BaseAgent
from src.tools.exchange_tools import get_exchange_rate, format_exchange_rate


class ExchangeAgent(BaseAgent):
    """Agent responsible for currency exchange operations."""
    
    def __init__(self):
        """Initialize Exchange Agent."""
        super().__init__("Agente de Câmbio", "Especialista em Câmbio")
        self.supported_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
    
    async def handle_request(self, user_message: str) -> str:
        """Handle exchange request."""
        return await self.process_exchange_request(user_message)
    
    async def process_exchange_request(self, user_message: str) -> str:
        """Process exchange rate request."""
        # Use LLM to identify which currency the user wants
        prompt = f"""
        O cliente perguntou: "{user_message}"
        
        Identifique qual moeda estrangeira o cliente está interessado em consultar a cotação.
        Moedas suportadas: USD (Dólar), EUR (Euro), GBP (Libra), JPY (Iene), CAD (Dólar Canadense), AUD (Dólar Australiano)
        
        Responda APENAS com a sigla da moeda (USD, EUR, etc) ou NENHUMA se não conseguir identificar.
        """
        
        llm_response = self.llm.invoke([HumanMessage(content=prompt)])
        currency = llm_response.content.strip().upper()
        
        # Validate currency
        if currency not in self.supported_currencies:
            return """Desculpe, não consegui identificar qual moeda você gostaria de consultar.

Moedas suportadas:
- USD (Dólar)
- EUR (Euro)
- GBP (Libra Esterlina)
- JPY (Iene Japonês)
- CAD (Dólar Canadense)
- AUD (Dólar Australiano)

Qual delas você gostaria de saber a cotação em relação ao Real (BRL)?"""
        
        # Get exchange rate
        exchange_data = get_exchange_rate(currency)
        
        if not exchange_data:
            return f"Desculpe, não consegui obter a cotação para {currency} no momento. Tente novamente mais tarde."
        
        exchange_message = format_exchange_rate(exchange_data)
        
        follow_up = """

Posso ajudá-lo com outra consulta de câmbio? Caso contrário, posso redirecioná-lo para outro serviço bancário."""
        
        return exchange_message + follow_up
    
    def get_all_rates(self) -> str:
        """Get all supported exchange rates."""
        message = "Cotações atuais (BRL como base):\n\n"
        
        for currency in self.supported_currencies:
            rate_data = get_exchange_rate(currency)
            if rate_data:
                message += f"• {rate_data['moeda']}: {format_exchange_rate(rate_data)}\n"
        
        return message
