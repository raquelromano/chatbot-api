"""AWS Secrets Manager client for secure secret retrieval."""

import json
import logging
from typing import Dict, Any, Optional
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class SecretsManager:
    """AWS Secrets Manager client with caching and error handling."""

    def __init__(self, region_name: str = "us-east-1", environment: str = "dev"):
        """Initialize Secrets Manager client.

        Args:
            region_name: AWS region for Secrets Manager
            environment: Environment (dev/prod) for secret naming
        """
        self.region_name = region_name
        self.environment = environment
        self.client = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize boto3 Secrets Manager client."""
        try:
            self.client = boto3.client('secretsmanager', region_name=self.region_name)
            logger.info(f"Initialized Secrets Manager client for region: {self.region_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Unable to initialize Secrets Manager client.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Secrets Manager client: {e}")
            raise

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve a secret value from AWS Secrets Manager.

        Args:
            secret_name: Name of the secret (without environment prefix)

        Returns:
            Secret value as string, or None if not found
        """
        if not self.client:
            logger.error("Secrets Manager client not initialized")
            return None

        # Construct full secret name with environment prefix
        full_secret_name = f"chatbot-api/{self.environment}/{secret_name}"

        try:
            response = self.client.get_secret_value(SecretId=full_secret_name)
            logger.debug(f"Successfully retrieved secret: {full_secret_name}")
            return response['SecretString']
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.warning(f"Secret not found: {full_secret_name}")
            elif error_code == 'InvalidRequestException':
                logger.error(f"Invalid request for secret: {full_secret_name}")
            elif error_code == 'InvalidParameterException':
                logger.error(f"Invalid parameter for secret: {full_secret_name}")
            elif error_code == 'DecryptionFailureException':
                logger.error(f"Decryption failed for secret: {full_secret_name}")
            elif error_code == 'InternalServiceErrorException':
                logger.error(f"Internal service error retrieving secret: {full_secret_name}")
            else:
                logger.error(f"Unexpected error retrieving secret {full_secret_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving secret {full_secret_name}: {e}")
            return None

    def get_secret_json(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve and parse a JSON secret from AWS Secrets Manager.

        Args:
            secret_name: Name of the secret (without environment prefix)

        Returns:
            Parsed JSON as dictionary, or None if not found or invalid JSON
        """
        secret_value = self.get_secret(secret_name)
        if not secret_value:
            return None

        try:
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON secret {secret_name}: {e}")
            return None

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider.

        Args:
            provider: Provider name (openai, anthropic, google)

        Returns:
            API key string, or None if not found
        """
        secret_data = self.get_secret_json(f"{provider}-api-key")
        if secret_data and "api_key" in secret_data:
            return secret_data["api_key"]

        logger.warning(f"API key not found for provider: {provider}")
        return None

    def get_jwt_secret(self) -> Optional[str]:
        """Get JWT secret key.

        Returns:
            JWT secret string, or None if not found
        """
        secret_data = self.get_secret_json("jwt-secret")
        if secret_data and "secret" in secret_data:
            return secret_data["secret"]

        logger.warning("JWT secret not found")
        return None

    def clear_cache(self) -> None:
        """Clear the secrets cache."""
        self.get_secret.cache_clear()
        logger.info("Secrets cache cleared")


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager(region_name: str = "us-east-1", environment: str = "dev") -> SecretsManager:
    """Get global secrets manager instance.

    Args:
        region_name: AWS region for Secrets Manager
        environment: Environment (dev/prod) for secret naming

    Returns:
        SecretsManager instance
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager(region_name=region_name, environment=environment)
    return _secrets_manager


def get_api_key(provider: str, region_name: str = "us-east-1", environment: str = "dev") -> Optional[str]:
    """Convenience function to get API key for a provider.

    Args:
        provider: Provider name (openai, anthropic, google)
        region_name: AWS region for Secrets Manager
        environment: Environment (dev/prod) for secret naming

    Returns:
        API key string, or None if not found
    """
    secrets_manager = get_secrets_manager(region_name=region_name, environment=environment)
    return secrets_manager.get_api_key(provider)


def get_jwt_secret(region_name: str = "us-east-1", environment: str = "dev") -> Optional[str]:
    """Convenience function to get JWT secret.

    Args:
        region_name: AWS region for Secrets Manager
        environment: Environment (dev/prod) for secret naming

    Returns:
        JWT secret string, or None if not found
    """
    secrets_manager = get_secrets_manager(region_name=region_name, environment=environment)
    return secrets_manager.get_jwt_secret()