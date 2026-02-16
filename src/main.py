"""Main application orchestrator."""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from src.agents.agent_router import AgentRouter


@dataclass
class Message:
    """Message data structure."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str


class BancoAgilApp:
    """Main application for Banco Ágil."""
    
    def __init__(self):
        """Initialize the application."""
        self.router = AgentRouter()
        self.conversation_history: List[Message] = []
        self.is_active = False
    
    async def start_conversation(self) -> str:
        """Start a new conversation."""
        self.is_active = True
        self.conversation_history = []
        
        # Trigger greeting from triage agent
        greeting = await self.router.handle_triage("")
        self._add_to_history("assistant", greeting)
        
        return greeting
    
    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input and return agent response.
        
        Args:
            user_input: User's message
            
        Returns:
            Agent's response
        """
        if not self.is_active:
            return "Conversa não iniciada. Por favor, inicie uma nova conversa."
        
        # Add user message to history
        self._add_to_history("user", user_input)
        
        # Process through router
        response = await self.router.process_message(user_input)
        
        # Handle special routing instructions
        if response.startswith("ROUTE:"):
            # Extract agent type
            agent_type = response.replace("ROUTE:", "").strip()
            # This would be handled by specific agent rules
            # For now, just return appropriate message
            return self._get_agent_transition_message(agent_type)
        
        # Add response to history
        self._add_to_history("assistant", response)
        
        # Check if conversation should end
        if "Obrigado pela preferência" in response:
            self.is_active = False
        
        return response
    
    def _add_to_history(self, role: str, content: str) -> None:
        """Add message to conversation history."""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        self.conversation_history.append(message)
    
    def _get_agent_transition_message(self, agent_type: str) -> str:
        """Get message for agent transition."""
        messages = {
            "CREDITO": "Transferindo para Agente de Crédito...",
            "ENTREVISTA": "Transferindo para Agente de Entrevista de Crédito...",
            "CAMBIO": "Transferindo para Agente de Câmbio...",
            "ENCERRAMENTO": "Encerrando conversa..."
        }
        return messages.get(agent_type, "Processando solicitação...")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get full conversation history."""
        return [asdict(msg) for msg in self.conversation_history]
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary."""
        if not self.conversation_history:
            return {
                "total_messages": 0,
                "authenticated": False,
                "duration": "0s"
            }
        
        start_time = datetime.fromisoformat(self.conversation_history[0].timestamp)
        end_time = datetime.fromisoformat(self.conversation_history[-1].timestamp)
        duration = (end_time - start_time).total_seconds()
        
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": sum(1 for msg in self.conversation_history if msg.role == "user"),
            "assistant_messages": sum(1 for msg in self.conversation_history if msg.role == "assistant"),
            "authenticated": self.router.is_authenticated(),
            "authenticated_cpf": self.router.get_authenticated_cpf(),
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    
    def reset(self) -> None:
        """Reset application state."""
        self.router.reset()
        self.conversation_history = []
        self.is_active = False
    
    def is_conversation_active(self) -> bool:
        """Check if conversation is active."""
        return self.is_active


async def main():
    """Main entry point for testing."""
    app = BancoAgilApp()
    
    # Start conversation
    print("=== Banco Ágil - Sistema de Atendimento ===\n")
    greeting = await app.start_conversation()
    print(f"Agente: {greeting}\n")
    
    # Test conversation loop
    test_inputs = [
        "12345678901",
        "1990-05-15",
        "Gostaria de saber meu limite de crédito",
        "Quero aumentar para 10000",
        "Encerrar"
    ]
    
    for user_input in test_inputs:
        print(f"Você: {user_input}")
        response = await app.process_user_input(user_input)
        print(f"Agente: {response}\n")
        
        if not app.is_conversation_active():
            break
    
    # Print summary
    print("\n=== Resumo da Conversa ===")
    summary = app.get_conversation_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
