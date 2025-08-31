from abc import ABC, abstractmethod
from typing import Dict, Any, List, AsyncGenerator
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Standard chat message format across all adapters."""
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    """Standard chat request format."""
    messages: List[ChatMessage]
    model_id: str
    max_tokens: int = 2048
    temperature: float = 0.7
    stream: bool = False


class ChatResponse(BaseModel):
    """Standard chat response format."""
    content: str
    model_id: str
    usage: Dict[str, int] = {}  # {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    finish_reason: str = "stop"


class BaseModelAdapter(ABC):
    """Abstract base class for all model adapters."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Generate a chat completion."""
        pass
    
    @abstractmethod
    async def chat_completion_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Generate a streaming chat completion."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the model/API is available."""
        pass