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

        # Get all parameters for the chatbot API
        response = ssm.get_parameters_by_path(
            Path='/chatbot-api',
            Recursive=True,
            WithDecryption=True
        )

        # Map parameter names to environment variables
        param_mapping = {
            '/chatbot-api/app-name': 'APP_NAME',
            '/chatbot-api/debug': 'DEBUG',
            '/chatbot-api/log-level': 'LOG_LEVEL',
            '/chatbot-api/default-model': 'DEFAULT_MODEL',
            '/chatbot-api/openai-api-key': 'OPENAI_API_KEY',
            '/chatbot-api/anthropic-api-key': 'ANTHROPIC_API_KEY',
            '/chatbot-api/jwt-secret-key': 'JWT_SECRET_KEY',
            '/chatbot-api/jwt-algorithm': 'JWT_ALGORITHM',
            '/chatbot-api/jwt-expiration-hours': 'JWT_EXPIRATION_HOURS',
            '/chatbot-api/enable-auth': 'ENABLE_AUTH',
            '/chatbot-api/auth-required-endpoints': 'AUTH_REQUIRED_ENDPOINTS',
            '/chatbot-api/enable-logging': 'ENABLE_LOGGING',
            '/chatbot-api/data-retention-days': 'DATA_RETENTION_DAYS',
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