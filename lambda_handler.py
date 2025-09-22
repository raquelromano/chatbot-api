"""AWS Lambda handler for FastAPI application using Mangum."""

import os
import boto3
from mangum import Mangum


def load_parameters_from_ssm():
    """Load configuration from AWS Systems Manager Parameter Store."""
    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return  # Skip if not running in Lambda

    try:
        ssm = boto3.client('ssm')

        # Get environment from Lambda environment variable
        environment = os.getenv("ENVIRONMENT", "dev")

        # Get all parameters for the chatbot API environment
        response = ssm.get_parameters_by_path(
            Path=f'/chatbot-api/{environment}',
            Recursive=True,
            WithDecryption=True
        )

        # Map parameter names to environment variables
        param_mapping = {
            f'/chatbot-api/{environment}/app-name': 'APP_NAME',
            f'/chatbot-api/{environment}/debug': 'DEBUG',
            f'/chatbot-api/{environment}/log-level': 'LOG_LEVEL',
            f'/chatbot-api/{environment}/default-model': 'DEFAULT_MODEL',
            f'/chatbot-api/{environment}/openai-api-key': 'OPENAI_API_KEY',
            f'/chatbot-api/{environment}/anthropic-api-key': 'ANTHROPIC_API_KEY',
            f'/chatbot-api/{environment}/jwt-secret-key': 'JWT_SECRET_KEY',
            f'/chatbot-api/{environment}/jwt-algorithm': 'JWT_ALGORITHM',
            f'/chatbot-api/{environment}/jwt-expiration-hours': 'JWT_EXPIRATION_HOURS',
            f'/chatbot-api/{environment}/enable-auth': 'ENABLE_AUTH',
            f'/chatbot-api/{environment}/auth-required-endpoints': 'AUTH_REQUIRED_ENDPOINTS',
            f'/chatbot-api/{environment}/enable-logging': 'ENABLE_LOGGING',
            f'/chatbot-api/{environment}/data-retention-days': 'DATA_RETENTION_DAYS',
        }

        # Set environment variables from parameters
        for param in response['Parameters']:
            param_name = param['Name']
            if param_name in param_mapping:
                env_var = param_mapping[param_name]
                os.environ[env_var] = param['Value']

    except Exception as e:
        print(f"Warning: Failed to load parameters from SSM: {e}")


# Load parameters before importing the app
load_parameters_from_ssm()

# Configure for Lambda environment
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    # Running in Lambda - disable reload and debugging
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("LOG_LEVEL", "INFO")

# Import app after parameters are loaded
from src.api.main import app

# Create the Lambda handler
handler = Mangum(app, lifespan="off")

# Export for Lambda
lambda_handler = handler