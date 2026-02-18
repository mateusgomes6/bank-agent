"""Base agent class for all specialized agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from src.utils.config import OPENAI_API_KEY, GOOGLE_API_KEY, LLM_MODEL, LLM_PROVIDER


class BaseAgent(ABC):
    """Base class for all banking agents."""

    def __init__(self, agent_name: str, agent_role: str):
        """Initialize base agent."""
        self.agent_name = agent_name
        self.agent_role = agent_role

        # Choose LLM provider based on configuration
        if LLM_PROVIDER == "google":
            self.llm = ChatGoogleGenerativeAI(
                model=LLM_MODEL,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.7
            )
        else:  # default to openai
            self.llm = ChatOpenAI(
                model=LLM_MODEL,
                api_key=OPENAI_API_KEY,
                temperature=0.7
            )

        self.context: Dict[str, Any] = {}
        self.conversation_history: List[BaseMessage] = []
    
    @abstractmethod
    async def handle_request(self, user_message: str) -> str:
        """Handle user request. Must be implemented by subclasses."""
        pass
    
    def set_context(self, key: str, value: Any) -> None:
        """Set context variable."""
        self.context[key] = value
    
    def get_context(self, key: str) -> Optional[Any]:
        """Get context variable."""
        return self.context.get(key)
    
    def add_message(self, role: str, content: str) -> None:
        """Add message to conversation history."""
        if role == "user":
            self.conversation_history.append(HumanMessage(content=content))
        elif role == "assistant":
            self.conversation_history.append(AIMessage(content=content))
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
