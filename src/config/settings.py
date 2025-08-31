from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = Field(default="Chatbot Wrapper Demo", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Model configuration
    default_model: str = Field(default="local", env="DEFAULT_MODEL")
    vllm_host: str = Field(default="localhost", env="VLLM_HOST")
    vllm_port: int = Field(default=8001, env="VLLM_PORT")
    
    # API keys (optional for external models)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Data collection settings
    enable_logging: bool = Field(default=True, env="ENABLE_LOGGING")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    data_retention_days: int = Field(default=30, env="DATA_RETENTION_DAYS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()