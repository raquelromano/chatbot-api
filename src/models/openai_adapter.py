from typing import Dict, Any, AsyncGenerator
import httpx
from .base import BaseModelAdapter, ChatRequest, ChatResponse, ChatMessage
from ..config.settings import settings


class OpenAIAdapter(BaseModelAdapter):
    """Adapter for OpenAI-compatible APIs (OpenAI, vLLM, etc.)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Get API key from settings
        api_key = None
        api_key_env = config.get("api_key_env")
        if api_key_env == "OPENAI_API_KEY":
            api_key = settings.openai_api_key
        
        # Set up HTTP client
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        self.client = httpx.AsyncClient(
            base_url=config.get("api_base", "https://api.openai.com/v1"),
            headers=headers,
            timeout=60.0
        )
    
    def _convert_messages(self, messages: list[ChatMessage]) -> list[dict]:
        """Convert internal message format to OpenAI format."""
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Generate a chat completion using OpenAI format."""
        payload = {
            "model": request.model_id,
            "messages": self._convert_messages(request.messages),
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stream": False
        }
        
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        
        data = response.json()
        choice = data["choices"][0]
        
        return ChatResponse(
            content=choice["message"]["content"],
            model_id=data["model"],
            usage=data.get("usage", {}),
            finish_reason=choice.get("finish_reason", "stop")
        )
    
    async def chat_completion_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Generate a streaming chat completion."""
        payload = {
            "model": request.model_id,
            "messages": self._convert_messages(request.messages),
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stream": True
        }
        
        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str.strip() == "[DONE]":
                        break
                    
                    try:
                        import json
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def health_check(self) -> bool:
        """Check if the API is available."""
        try:
            response = await self.client.get("/models")
            return response.status_code == 200
        except Exception:
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()