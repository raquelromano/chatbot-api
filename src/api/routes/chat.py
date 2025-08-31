"""Chat completion endpoints."""

import time
import uuid
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import structlog

from ...models.adapter_factory import get_adapter_factory
from ...models.base import ChatRequest
from ..models import (
    ChatCompletionRequest, 
    ChatCompletionResponse, 
    Usage, 
    ModelListResponse,
    StreamingChatCompletionChunk
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest, http_request: Request):
    """
    Create a chat completion using the specified model.
    
    This endpoint accepts OpenAI-compatible requests and routes them to the 
    appropriate model adapter based on the model_id.
    """
    try:
        # Get the adapter for this model
        factory = get_adapter_factory()
        adapter = factory.get_adapter(request.model_id)
        
        if not adapter:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{request.model_id}' not found or not available"
            )
        
        # Convert API request to internal format
        chat_request = ChatRequest(
            messages=request.messages,
            model_id=request.model_id,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream
        )
        
        # Log the request
        logger.info(
            "Chat completion request",
            model_id=request.model_id,
            message_count=len(request.messages),
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream,
            client_host=http_request.client.host if http_request.client else None,
        )
        
        # Handle streaming response
        if request.stream:
            return StreamingResponse(
                _stream_chat_completion(adapter, chat_request),
                media_type="text/plain"
            )
        
        # Handle non-streaming response
        start_time = time.time()
        response = await adapter.chat_completion(chat_request)
        duration = time.time() - start_time
        
        # Create response in OpenAI format
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created_timestamp = int(time.time())
        
        # Convert internal response to API format
        api_response = ChatCompletionResponse(
            id=completion_id,
            object="chat.completion",
            created=created_timestamp,
            model=request.model_id,
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.content
                    },
                    "finish_reason": response.finish_reason
                }
            ],
            usage=Usage(
                prompt_tokens=response.usage.get("prompt_tokens", 0),
                completion_tokens=response.usage.get("completion_tokens", 0),
                total_tokens=response.usage.get("total_tokens", 0)
            )
        )
        
        # Log the response
        logger.info(
            "Chat completion response",
            model_id=request.model_id,
            completion_id=completion_id,
            finish_reason=response.finish_reason,
            response_length=len(response.content),
            duration_seconds=duration,
            prompt_tokens=response.usage.get("prompt_tokens", 0),
            completion_tokens=response.usage.get("completion_tokens", 0),
        )
        
        return api_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Chat completion failed",
            model_id=request.model_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error during chat completion"
        )


async def _stream_chat_completion(adapter, chat_request: ChatRequest):
    """Stream chat completion chunks in OpenAI format."""
    
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created_timestamp = int(time.time())
    
    try:
        # Send initial chunk
        initial_chunk = StreamingChatCompletionChunk(
            id=completion_id,
            object="chat.completion.chunk",
            created=created_timestamp,
            model=chat_request.model_id,
            choices=[
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": ""},
                    "finish_reason": None
                }
            ]
        )
        yield f"data: {initial_chunk.json()}\n\n"
        
        # Stream content chunks
        async for content_chunk in adapter.chat_completion_stream(chat_request):
            chunk = StreamingChatCompletionChunk(
                id=completion_id,
                object="chat.completion.chunk", 
                created=created_timestamp,
                model=chat_request.model_id,
                choices=[
                    {
                        "index": 0,
                        "delta": {"content": content_chunk},
                        "finish_reason": None
                    }
                ]
            )
            yield f"data: {chunk.json()}\n\n"
        
        # Send final chunk
        final_chunk = StreamingChatCompletionChunk(
            id=completion_id,
            object="chat.completion.chunk",
            created=created_timestamp,
            model=chat_request.model_id,
            choices=[
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        )
        yield f"data: {final_chunk.json()}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(
            "Streaming chat completion failed",
            model_id=chat_request.model_id,
            completion_id=completion_id,
            error=str(e),
            exc_info=True
        )
        # Send error as final chunk
        error_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created_timestamp,
            "model": chat_request.model_id,
            "error": {
                "message": "Stream interrupted due to error",
                "type": "server_error"
            }
        }
        yield f"data: {error_chunk}\n\n"
        yield "data: [DONE]\n\n"


@router.get("/models", response_model=ModelListResponse)
async def list_models():
    """
    List all available models.
    
    Returns information about all models that are currently configured and available.
    """
    try:
        factory = get_adapter_factory()
        models_data = factory.list_available_models()
        
        logger.info(
            "Models listed", 
            model_count=len(models_data["data"])
        )
        
        return ModelListResponse(**models_data)
        
    except Exception as e:
        logger.error("Failed to list models", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve model list"
        )