import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from .secrets import get_api_key, get_jwt_secret


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
    
    # API keys (loaded from Secrets Manager in AWS, environment variables locally)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    
    # Auth0 configuration (legacy)
    auth0_domain: Optional[str] = Field(default=None, env="AUTH0_DOMAIN")
    auth0_client_id: Optional[str] = Field(default=None, env="AUTH0_CLIENT_ID")
    auth0_client_secret: Optional[str] = Field(default=None, env="AUTH0_CLIENT_SECRET")
    auth0_audience: Optional[str] = Field(default=None, env="AUTH0_AUDIENCE")

    # AWS Cognito configuration
    cognito_user_pool_id: Optional[str] = Field(default=None, env="COGNITO_USER_POOL_ID")
    cognito_client_id: Optional[str] = Field(default=None, env="COGNITO_CLIENT_ID")
    cognito_region: Optional[str] = Field(default=None, env="COGNITO_REGION")
    aws_account_id: Optional[str] = Field(default=None, env="AWS_ACCOUNT_ID")

    # JWT configuration
    jwt_secret_key: str = Field(default="development-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Authentication settings
    enable_auth: bool = Field(default=False, env="ENABLE_AUTH")
    auth_required_endpoints: List[str] = Field(default_factory=lambda: ["/v1/chat/completions"], env="AUTH_REQUIRED_ENDPOINTS")
    
    # Data collection settings
    enable_logging: bool = Field(default=True, env="ENABLE_LOGGING")

    # Email settings
    ses_from_email: str = Field(default="noreply@chatbot-api.com", env="SES_FROM_EMAIL")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    data_retention_days: int = Field(default=30, env="DATA_RETENTION_DAYS")

    # AWS Lambda configuration (set automatically in Lambda)
    aws_lambda_function_name: Optional[str] = Field(default=None, env="AWS_LAMBDA_FUNCTION_NAME")
    aws_region: Optional[str] = Field(default=None, env="AWS_REGION")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def load_secrets_from_aws(self) -> None:
        """Load secrets from AWS Secrets Manager when running in Lambda."""
        # Check if we're running in AWS Lambda
        if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            return  # Running locally, use environment variables

        environment = os.getenv("ENVIRONMENT", "dev")
        aws_region = os.getenv("AWS_REGION", "us-east-1")

        # Load Google API key (currently enabled)
        if not self.google_api_key:
            google_key = get_api_key("google", region_name=aws_region, environment=environment)
            if google_key:
                self.google_api_key = google_key

        # Load JWT secret
        if self.jwt_secret_key == "development-key-change-in-production":
            jwt_secret = get_jwt_secret(region_name=aws_region, environment=environment)
            if jwt_secret:
                self.jwt_secret_key = jwt_secret

        # Commented out - uncomment when OpenAI/Anthropic adapters are enabled
        # if not self.openai_api_key:
        #     openai_key = get_api_key("openai", region_name=aws_region, environment=environment)
        #     if openai_key:
        #         self.openai_api_key = openai_key

        # if not self.anthropic_api_key:
        #     anthropic_key = get_api_key("anthropic", region_name=aws_region, environment=environment)
        #     if anthropic_key:
        #         self.anthropic_api_key = anthropic_key


# Global settings instance
settings = Settings()