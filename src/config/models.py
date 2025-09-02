from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ClientType(str, Enum):
    """Types of API clients/adapters supported."""
    OPENAI_COMPATIBLE = "openai_compatible"  # OpenAI API format (covers vLLM, OpenAI, many others)
    ANTHROPIC = "anthropic"                  # Anthropic's messages format
    GOOGLE = "google"                        # Google Vertex AI/Gemini format


class ModelConfig(BaseModel):
    """Configuration for a single model."""
    name: str = Field(..., description="Human-readable model name")
    model_id: str = Field(..., description="Model identifier (e.g., 'gpt-4o', 'meta-llama/Meta-Llama-3.1-8B-Instruct')")
    client_type: ClientType = Field(..., description="Which client adapter to use")
    
    # Connection settings
    api_base: Optional[str] = Field(default=None, description="API base URL")
    api_key_env: Optional[str] = Field(default=None, description="Environment variable name for API key")
    
    # Model parameters
    max_tokens: int = Field(default=2048, description="Maximum tokens per response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Default sampling temperature")
    context_length: Optional[int] = Field(default=None, description="Model's context window size")
    
    # Availability
    enabled: bool = Field(default=True, description="Whether this model is available")
    
    # Provider metadata
    provider: str = Field(..., description="Provider name (e.g., 'OpenAI', 'Local vLLM', 'Anthropic')")
    is_local: bool = Field(default=False, description="Whether this is a locally hosted model")


class ModelRegistry:
    """Registry of available models and their configurations."""
    
    def __init__(self):
        self._models: Dict[str, ModelConfig] = {}
        self._load_default_models()
    
    def _load_default_models(self):
        """Load default model configurations."""
        default_models = [
            # Local vLLM models (OpenAI-compatible API)
            ModelConfig(
                name="Llama 3.1 8B Instruct",
                model_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
                client_type=ClientType.OPENAI_COMPATIBLE,
                provider="Local vLLM",
                is_local=True,
                api_base="http://localhost:8001/v1",
                max_tokens=2048,
                context_length=131072
            ),
            ModelConfig(
                name="Mistral Nemo 12B",
                model_id="mistralai/Mistral-Nemo-Instruct-2407",
                client_type=ClientType.OPENAI_COMPATIBLE,
                provider="Local vLLM",
                is_local=True,
                api_base="http://localhost:8001/v1",
                max_tokens=2048,
                context_length=128000
            ),
            
            # OpenAI models
            ModelConfig(
                name="GPT-3.5 Turbo",
                model_id="gpt-3.5-turbo",
                client_type=ClientType.OPENAI_COMPATIBLE,
                provider="OpenAI",
                api_base="https://api.openai.com/v1",
                api_key_env="OPENAI_API_KEY",
                max_tokens=4096,
                context_length=16385
            ),
            ModelConfig(
                name="GPT-4o",
                model_id="gpt-4o",
                client_type=ClientType.OPENAI_COMPATIBLE,
                provider="OpenAI",
                api_base="https://api.openai.com/v1",
                api_key_env="OPENAI_API_KEY",
                max_tokens=4096,
                context_length=128000
            ),
            
            # Anthropic models
            ModelConfig(
                name="Claude 3.5 Sonnet",
                model_id="claude-3-5-sonnet-20241022",
                client_type=ClientType.ANTHROPIC,
                provider="Anthropic",
                api_key_env="ANTHROPIC_API_KEY",
                max_tokens=4096,
                context_length=200000
            ),
            
            # Google models
            ModelConfig(
                name="Gemini 2.5 Pro",
                model_id="gemini-2.5-pro",
                client_type=ClientType.GOOGLE,
                provider="Google",
                api_key_env="GOOGLE_API_KEY",
                max_tokens=2048,
                context_length=1000000
            )
        ]
        
        for model in default_models:
            self.register_model(model)
    
    def register_model(self, model: ModelConfig) -> None:
        """Register a new model configuration."""
        self._models[model.model_id] = model
    
    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """Get model configuration by ID."""
        return self._models.get(model_id)
    
    def list_models(self, enabled_only: bool = True) -> List[ModelConfig]:
        """List all available models."""
        models = list(self._models.values())
        if enabled_only:
            models = [m for m in models if m.enabled]
        return models
    
    def list_models_by_client_type(self, client_type: ClientType, enabled_only: bool = True) -> List[ModelConfig]:
        """List models by client type."""
        models = [m for m in self._models.values() if m.client_type == client_type]
        if enabled_only:
            models = [m for m in models if m.enabled]
        return models
    
    def list_local_models(self, enabled_only: bool = True) -> List[ModelConfig]:
        """List locally hosted models."""
        models = [m for m in self._models.values() if m.is_local]
        if enabled_only:
            models = [m for m in models if m.enabled]
        return models
    
    def disable_model(self, model_id: str) -> bool:
        """Disable a model (e.g., if API key is missing)."""
        if model_id in self._models:
            self._models[model_id].enabled = False
            return True
        return False
    
    def enable_model(self, model_id: str) -> bool:
        """Enable a model."""
        if model_id in self._models:
            self._models[model_id].enabled = True
            return True
        return False


# Global model registry instance
model_registry = ModelRegistry()