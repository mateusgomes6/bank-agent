"""Base agent class for all specialized agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from src.utils.config import OPENAI_API_KEY, GOOGLE_API_KEY, LLM_MODEL, LLM_PROVIDER


class GoogleGeminiWrapper:
    """Wrapper for Google Gemini API that mimics langchain interface."""

    def __init__(self, model: str, api_key: str, temperature: float = 0.7):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.temperature = temperature

    def invoke(self, messages: List[BaseMessage]):
        """Invoke the model with messages."""
        # Convert langchain messages to text
        prompt = ""
        for msg in messages:
            if isinstance(msg, HumanMessage):
                prompt += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                prompt += f"Assistant: {msg.content}\n"
            else:
                prompt += f"{msg.content}\n"

        # Generate response
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
            )
        )

        # Create a response object that mimics langchain
        class Response:
            def __init__(self, text):
                self.content = text

        return Response(response.text)


class BaseAgent(ABC):
    """Base class for all banking agents."""

    def __init__(self, agent_name: str, agent_role: str):
        """Initialize base agent."""
        self.agent_name = agent_name
        self.agent_role = agent_role

        # Choose LLM provider based on configuration
        if LLM_PROVIDER == "google":
            # Use custom Google Gemini wrapper
            self.llm = GoogleGeminiWrapper(
                model=LLM_MODEL,
                api_key=GOOGLE_API_KEY,
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
        """Clear history."""
        self.conversation_history = []
