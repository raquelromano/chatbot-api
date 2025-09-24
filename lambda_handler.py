"""AWS Lambda handler for FastAPI application using Mangum."""

import os
from mangum import Mangum


def initialize_secrets():
    """Initialize secrets from AWS Secrets Manager when running in Lambda."""
    if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return  # Skip if not running in Lambda

    try:
        # Import settings and load secrets
        from src.config.settings import settings
        settings.load_secrets_from_aws()
        print("Successfully loaded secrets from AWS Secrets Manager")
    except Exception as e:
        print(f"Warning: Failed to load secrets from AWS Secrets Manager: {e}")


# Initialize secrets before importing the app
initialize_secrets()

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