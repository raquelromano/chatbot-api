#!/bin/bash

# Setup secrets in AWS Systems Manager Parameter Store

set -e

# Disable AWS CLI pager to prevent interactive editor issues
export AWS_PAGER=""

# Get environment from command line argument or default to dev
ENVIRONMENT=${1:-dev}

if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "prod" ]; then
    echo "❌ Invalid environment. Use 'dev' or 'prod'"
    echo "Usage: $0 [dev|prod]"
    exit 1
fi

echo "🔐 Setting up secrets in AWS Systems Manager Parameter Store for environment: $ENVIRONMENT"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Function to create or update a parameter
create_parameter() {
    local name=$1
    local value=$2
    local type=${3:-"String"}

    echo "Setting parameter: $name"

    # Check if parameter exists
    if aws ssm get-parameter --name "$name" &> /dev/null; then
        aws ssm put-parameter --name "$name" --value "$value" --type "$type" --overwrite
    else
        aws ssm put-parameter --name "$name" --value "$value" --type "$type"
    fi
}

# Application configuration
echo "📋 Creating application configuration parameters..."
create_parameter "/chatbot-api/$ENVIRONMENT/app-name" "Chatbot API ($ENVIRONMENT)"
create_parameter "/chatbot-api/$ENVIRONMENT/debug" "$([ "$ENVIRONMENT" = "dev" ] && echo "true" || echo "false")"
create_parameter "/chatbot-api/$ENVIRONMENT/log-level" "$([ "$ENVIRONMENT" = "dev" ] && echo "DEBUG" || echo "INFO")"

# Model configuration
echo "🤖 Creating model configuration parameters..."
create_parameter "/chatbot-api/$ENVIRONMENT/default-model" "openai"

# API Keys (SecureString type for encryption)
echo "🔑 Creating API key parameters..."
echo "Note: You'll need to update these with your actual API keys"
create_parameter "/chatbot-api/$ENVIRONMENT/openai-api-key" "your-openai-api-key-here" "SecureString"
create_parameter "/chatbot-api/$ENVIRONMENT/anthropic-api-key" "your-anthropic-api-key-here" "SecureString"

# JWT configuration
echo "🎫 Creating JWT configuration parameters..."
create_parameter "/chatbot-api/$ENVIRONMENT/jwt-secret-key" "$(openssl rand -base64 32)" "SecureString"
create_parameter "/chatbot-api/$ENVIRONMENT/jwt-algorithm" "HS256"
create_parameter "/chatbot-api/$ENVIRONMENT/jwt-expiration-hours" "24"

# Authentication settings
echo "🔒 Creating authentication configuration parameters..."
create_parameter "/chatbot-api/$ENVIRONMENT/enable-auth" "true"
create_parameter "/chatbot-api/$ENVIRONMENT/auth-required-endpoints" "/v1/chat/completions,/v1/models"

# Data collection settings
echo "📊 Creating data collection configuration parameters..."
create_parameter "/chatbot-api/$ENVIRONMENT/enable-logging" "true"
create_parameter "/chatbot-api/$ENVIRONMENT/data-retention-days" "30"

echo "✅ All parameters created successfully for environment: $ENVIRONMENT!"
echo ""
echo "🔧 Next steps:"
echo "   1. Update the API key parameters with your actual keys:"
echo "      aws ssm put-parameter --name '/chatbot-api/$ENVIRONMENT/openai-api-key' --value 'your-actual-key' --type SecureString --overwrite"
echo "   2. Configure Cognito parameters after CDK deployment"
echo ""
echo "📝 View all parameters for this environment:"
echo "   aws ssm get-parameters-by-path --path '/chatbot-api/$ENVIRONMENT' --recursive"
echo ""
echo "💡 Usage: ./scripts/setup-secrets.sh [dev|prod]  (defaults to dev)"