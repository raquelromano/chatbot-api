"""Factory for creating and managing model adapters based on configuration."""

from typing import Dict, Optional
import structlog

from ..config.models import model_registry, ClientType
from .base import BaseModelAdapter
from .openai_adapter import OpenAIAdapter
from .google_adapter import GoogleAdapter

logger = structlog.get_logger()


class AdapterFactory:
    """Factory for creating and managing model adapters."""
    
    def __init__(self):
        self._adapters: Dict[str, BaseModelAdapter] = {}
    
    def get_adapter(self, model_id: str) -> Optional[BaseModelAdapter]:
        """Get or create an adapter for the specified model."""
        
        # Get model configuration
        model_config = model_registry.get_model(model_id)
        if not model_config or not model_config.enabled:
            logger.warning("Model not found or disabled", model_id=model_id)
            return None
        
        # Create adapter key based on provider and api_base to reuse connections
        adapter_key = f"{model_config.provider}:{model_config.api_base or 'default'}"
        
        # Return existing adapter if available
        if adapter_key in self._adapters:
            return self._adapters[adapter_key]
        
        # Create new adapter based on client type
        adapter = None
        
        if model_config.client_type == ClientType.OPENAI_COMPATIBLE:
            adapter_config = {
                "api_base": model_config.api_base,
                "api_key_env": model_config.api_key_env
            }
            adapter = OpenAIAdapter(adapter_config)
            logger.info("Created OpenAI-compatible adapter", 
                       model_id=model_id, 
                       provider=model_config.provider,
                       api_base=model_config.api_base)
        
        elif model_config.client_type == ClientType.ANTHROPIC:
            logger.warning("Anthropic adapter not yet implemented", model_id=model_id)
            return None
            
        elif model_config.client_type == ClientType.GOOGLE:
            try:
                adapter_config = {
                    "api_key_env": model_config.api_key_env
                }
                adapter = GoogleAdapter(adapter_config)
                logger.info("Created Google adapter",
                           model_id=model_id,
                           provider=model_config.provider)
            except Exception as e:
                logger.warning("Failed to create Google adapter",
                             model_id=model_id,
                             error=str(e))
                return None
        
        else:
            logger.error("Unknown client type", 
                        model_id=model_id, 
                        client_type=model_config.client_type)
            return None
        
        # Cache the adapter
        if adapter:
            self._adapters[adapter_key] = adapter
        
        return adapter
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get model information from the registry."""
        model_config = model_registry.get_model(model_id)
        if not model_config:
            return None
            
        return {
            "id": model_config.model_id,
            "provider": model_config.provider,
            "name": model_config.name,
            "description": f"{model_config.provider} - {model_config.name}",
            "max_tokens": model_config.max_tokens,
            "supports_streaming": True,  # All current adapters support streaming
            "context_length": model_config.context_length,
            "is_local": model_config.is_local
        }
    
    def list_available_models(self) -> Dict:
        """List all available models from the registry."""
        models = model_registry.list_models(enabled_only=True)
        
        model_data = []
        for model_config in models:
            model_data.append({
                "id": model_config.model_id,
                "provider": model_config.provider,
                "name": model_config.name,
                "description": f"{model_config.provider} - {model_config.name}",
                "max_tokens": model_config.max_tokens,
                "supports_streaming": True,
                "context_length": model_config.context_length,
                "is_local": model_config.is_local
            })
        
        return {"object": "list", "data": model_data}
    
    async def health_check_all(self) -> Dict[str, Dict]:
        """Check health of all adapters."""
        health_status = {}
        
        # Group models by adapter to avoid duplicate health checks
        adapter_to_models = {}
        for model_config in model_registry.list_models(enabled_only=True):
            adapter_key = f"{model_config.provider}:{model_config.api_base or 'default'}"
            if adapter_key not in adapter_to_models:
                adapter_to_models[adapter_key] = []
            adapter_to_models[adapter_key].append(model_config)
        
        # Check health for each unique adapter
        for adapter_key, models in adapter_to_models.items():
            provider = models[0].provider
            model_ids = [m.model_id for m in models]
            
            try:
                # Get or create adapter
                adapter = self.get_adapter(models[0].model_id)
                if adapter:
                    is_healthy = await adapter.health_check()
                    health_status[provider] = {
                        "status": "available" if is_healthy else "unavailable",
                        "models": model_ids
                    }
                else:
                    health_status[provider] = {
                        "status": "unavailable",
                        "models": model_ids,
                        "error": "Failed to create adapter"
                    }
                    
            except Exception as e:
                logger.warning("Health check failed", 
                             provider=provider, 
                             error=str(e))
                health_status[provider] = {
                    "status": "error",
                    "models": model_ids,
                    "error": str(e)
                }
        
        return health_status
    
    async def close_all(self):
        """Close all adapter connections."""
        for adapter in self._adapters.values():
            if hasattr(adapter, '__aexit__'):
                try:
                    await adapter.__aexit__(None, None, None)
                except Exception as e:
                    logger.warning("Error closing adapter", error=str(e))
        
        self._adapters.clear()
        logger.info("All adapters closed")


# Global adapter factory instance
_adapter_factory: Optional[AdapterFactory] = None


def get_adapter_factory() -> AdapterFactory:
    """Get the global adapter factory instance."""
    global _adapter_factory
    if _adapter_factory is None:
        _adapter_factory = AdapterFactory()
    return _adapter_factory


async def close_adapter_factory():
    """Close the global adapter factory."""
    global _adapter_factory
    if _adapter_factory is not None:
        await _adapter_factory.close_all()
        _adapter_factory = None