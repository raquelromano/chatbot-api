"""API request and response models."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from ..models.base import ChatMessage


class ChatCompletionRequest(BaseModel):
    """Request model for chat completion endpoint."""
    messages: List[ChatMessage] = Field(
        ..., 
        description="List of messages in the conversation"
    )
    model_id: str = Field(
        ..., 
        description="ID of the model to use for completion"
    )
    max_tokens: int = Field(
        default=2048, 
        ge=1, 
        le=8192,
        description="Maximum number of tokens to generate"
    )
    temperature: float = Field(
        default=0.7, 
        ge=0.0, 
        le=2.0,
        description="Sampling temperature (0.0 to 2.0)"
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"}
                ],
                "model_id": "gpt-3.5-turbo",
                "max_tokens": 150,
                "temperature": 0.7,
                "stream": False
            }
        }


class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = Field(description="Number of tokens in the prompt")
    completion_tokens: int = Field(description="Number of tokens in the completion")
    total_tokens: int = Field(description="Total number of tokens used")


class ChatCompletionResponse(BaseModel):
    """Response model for chat completion endpoint."""
    id: str = Field(description="Unique identifier for the completion")
    object: str = Field(default="chat.completion", description="Object type")
    created: int = Field(description="Unix timestamp of when the completion was created")
    model: str = Field(description="Model used for the completion")
    choices: List[Dict[str, Any]] = Field(description="List of completion choices")
    usage: Usage = Field(description="Token usage information")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "gpt-3.5-turbo",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Hello! I'm doing well, thank you for asking."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 9,
                    "completion_tokens": 12,
                    "total_tokens": 21
                }
            }
        }


class StreamingChatCompletionChunk(BaseModel):
    """Response model for streaming chat completion chunks."""
    id: str = Field(description="Unique identifier for the completion")
    object: str = Field(default="chat.completion.chunk", description="Object type")
    created: int = Field(description="Unix timestamp of when the completion was created")
    model: str = Field(description="Model used for the completion")
    choices: List[Dict[str, Any]] = Field(description="List of completion choices")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(description="Error message")
    status_code: int = Field(description="HTTP status code")
    path: str = Field(description="API path that caused the error")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(description="Service status")
    timestamp: str = Field(description="ISO timestamp of health check")
    version: str = Field(description="Application version")
    models: Dict[str, Dict[str, Any]] = Field(
        description="Status of available models"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2023-01-01T12:00:00Z",
                "version": "1.0.0",
                "models": {
                    "openai": {
                        "status": "available",
                        "models": ["gpt-3.5-turbo", "gpt-4"]
                    },
                    "local": {
                        "status": "available", 
                        "models": ["llama-2-7b"]
                    }
                }
            }
        }


class ModelInfo(BaseModel):
    """Information about an available model."""
    id: str = Field(description="Model identifier")
    provider: str = Field(description="Model provider (openai, anthropic, etc.)")
    name: str = Field(description="Human-readable model name")
    description: Optional[str] = Field(description="Model description")
    max_tokens: int = Field(description="Maximum tokens supported")
    supports_streaming: bool = Field(description="Whether model supports streaming")


class ModelListResponse(BaseModel):
    """Response model for listing available models."""
    object: str = Field(default="list", description="Object type")
    data: List[ModelInfo] = Field(description="List of available models")

    class Config:
        json_schema_extra = {
            "example": {
                "object": "list",
                "data": [
                    {
                        "id": "gpt-3.5-turbo",
                        "provider": "openai",
                        "name": "GPT-3.5 Turbo",
                        "description": "Fast and efficient model for most tasks",
                        "max_tokens": 4096,
                        "supports_streaming": True
                    },
                    {
                        "id": "local-llama-2-7b",
                        "provider": "local",
                        "name": "Llama 2 7B",
                        "description": "Local Llama 2 model with 7B parameters",
                        "max_tokens": 4096,
                        "supports_streaming": True
                    }
                ]
            }
        }