import os
from typing import Dict, Any, AsyncGenerator
import httpx
from .base import BaseModelAdapter, ChatRequest, ChatResponse, ChatMessage


class GoogleAdapter(BaseModelAdapter):
    """Adapter for Google Gemini API."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Get API key
        api_key = None
        if config.get("api_key_env"):
            api_key = os.getenv(config["api_key_env"])

        if not api_key:
            raise ValueError("Google API key is required")

        # Set up HTTP client
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url="https://generativelanguage.googleapis.com/v1beta",
            timeout=60.0
        )

    def _convert_messages(self, messages: list[ChatMessage]) -> Dict[str, Any]:
        """Convert internal message format to Gemini format."""
        # Gemini uses a different format - contents array with parts
        contents = []

        for msg in messages:
            if msg.role == "system":
                # System messages go in the system_instruction field
                continue
            elif msg.role == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif msg.role == "assistant":
                contents.append({
                    "role": "model",  # Gemini uses "model" instead of "assistant"
                    "parts": [{"text": msg.content}]
                })

        # Handle system message separately if present
        system_instruction = None
        for msg in messages:
            if msg.role == "system":
                system_instruction = {"parts": [{"text": msg.content}]}
                break

        return {
            "contents": contents,
            "systemInstruction": system_instruction
        }

    def _build_generation_config(self, request: ChatRequest) -> Dict[str, Any]:
        """Build generation config for Gemini API."""
        return {
            "temperature": request.temperature,
            "maxOutputTokens": request.max_tokens,
            "topP": 0.95,  # Gemini default
            "topK": 40     # Gemini default
        }

    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Generate a chat completion using Gemini API."""
        # Build the request payload
        message_data = self._convert_messages(request.messages)
        payload = {
            **message_data,
            "generationConfig": self._build_generation_config(request)
        }

        # Make the API call
        url = f"/models/{request.model_id}:generateContent?key={self.api_key}"
        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        # Extract response content
        if "candidates" not in data or not data["candidates"]:
            raise ValueError("No response candidates from Gemini API")

        candidate = data["candidates"][0]
        if "content" not in candidate or "parts" not in candidate["content"]:
            raise ValueError("Invalid response format from Gemini API")

        content = candidate["content"]["parts"][0]["text"]
        finish_reason = candidate.get("finishReason", "STOP").lower()

        # Map Gemini finish reasons to OpenAI format
        if finish_reason == "stop":
            finish_reason = "stop"
        elif finish_reason == "max_tokens":
            finish_reason = "length"
        else:
            finish_reason = "stop"  # Default fallback

        # Extract usage information if available
        usage = {}
        if "usageMetadata" in data:
            metadata = data["usageMetadata"]
            usage = {
                "prompt_tokens": metadata.get("promptTokenCount", 0),
                "completion_tokens": metadata.get("candidatesTokenCount", 0),
                "total_tokens": metadata.get("totalTokenCount", 0)
            }

        return ChatResponse(
            content=content,
            model_id=request.model_id,
            usage=usage,
            finish_reason=finish_reason
        )

    async def chat_completion_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Generate a streaming chat completion using Gemini API."""
        # Build the request payload
        message_data = self._convert_messages(request.messages)
        payload = {
            **message_data,
            "generationConfig": self._build_generation_config(request)
        }

        # Make the streaming API call
        url = f"/models/{request.model_id}:streamGenerateContent?key={self.api_key}"

        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        import json
                        # Gemini streaming returns newline-delimited JSON
                        data = json.loads(line)

                        if "candidates" in data and data["candidates"]:
                            candidate = data["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                for part in candidate["content"]["parts"]:
                                    if "text" in part:
                                        yield part["text"]
                    except json.JSONDecodeError:
                        continue

    async def health_check(self) -> bool:
        """Check if the Gemini API is available."""
        try:
            # Use the models list endpoint to check availability
            url = f"/models?key={self.api_key}"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception:
            return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()