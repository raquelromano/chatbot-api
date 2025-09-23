from typing import Dict, Any, AsyncGenerator
import httpx
import logging
from .base import BaseModelAdapter, ChatRequest, ChatResponse, ChatMessage
from ..config.settings import settings

logger = logging.getLogger(__name__)


class GoogleAdapter(BaseModelAdapter):
    """Adapter for Google Gemini API.

    Note: Google's latest models are the 2.5 series (released March 2025):
    - gemini-2.5-pro (flagship model, 2M token context)
    - gemini-2.5-flash (fast model, 1M token context)
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Get API key from settings
        api_key = None
        if config.get("api_key_env") == "GOOGLE_API_KEY":
            api_key = settings.google_api_key

        # Store API key for URL parameters (Gemini uses query param, not headers)
        self.api_key = api_key

        # Set up HTTP client
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
        url = f"/models/{request.model_id}:generateContent"
        if self.api_key:
            url += f"?key={self.api_key}"

        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        # Debug logging to understand the response structure
        logger.debug(f"Gemini API response: {data}")

        # Extract response content
        if "candidates" not in data or not data["candidates"]:
            logger.error(f"No candidates in response: {data}")
            raise ValueError("No response candidates from Gemini API")

        candidate = data["candidates"][0]
        logger.debug(f"Candidate structure: {candidate}")

        if "content" not in candidate:
            logger.error(f"Invalid candidate structure: {candidate}")
            raise ValueError("Invalid response format from Gemini API")

        # Handle cases where parts field might be missing (e.g., MAX_TOKENS finish reason)
        if "parts" not in candidate["content"]:
            logger.warning(f"No parts in content, finish reason: {candidate.get('finishReason', 'UNKNOWN')}")
            content = ""  # Empty content when no parts are returned
        else:
            parts = candidate["content"]["parts"]
            if not parts or "text" not in parts[0]:
                logger.error(f"No text in parts: {parts}")
                raise ValueError("No text content in Gemini API response")
            content = parts[0]["text"]
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
        url = f"/models/{request.model_id}:streamGenerateContent"
        if self.api_key:
            url += f"?key={self.api_key}"

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
            url = "/models"
            if self.api_key:
                url += f"?key={self.api_key}"

            response = await self.client.get(url)
            return response.status_code == 200
        except Exception:
            return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
