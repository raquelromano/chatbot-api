#!/bin/bash

# Setup secrets in AWS Systems Manager Parameter Store

set -e

echo "🔐 Setting up secrets in AWS Systems Manager Parameter Store..."

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
create_parameter "/chatbot-api/app-name" "Chatbot API"
create_parameter "/chatbot-api/debug" "false"
create_parameter "/chatbot-api/log-level" "INFO"

# Model configuration
echo "🤖 Creating model configuration parameters..."
create_parameter "/chatbot-api/default-model" "openai"

# API Keys (SecureString type for encryption)
echo "🔑 Creating API key parameters..."
echo "Note: You'll need to update these with your actual API keys"
create_parameter "/chatbot-api/openai-api-key" "your-openai-api-key-here" "SecureString"
create_parameter "/chatbot-api/anthropic-api-key" "your-anthropic-api-key-here" "SecureString"

# JWT configuration
echo "🎫 Creating JWT configuration parameters..."
create_parameter "/chatbot-api/jwt-secret-key" "$(openssl rand -base64 32)" "SecureString"
create_parameter "/chatbot-api/jwt-algorithm" "HS256"
create_parameter "/chatbot-api/jwt-expiration-hours" "24"

# Authentication settings
echo "🔒 Creating authentication configuration parameters..."
create_parameter "/chatbot-api/enable-auth" "true"
create_parameter "/chatbot-api/auth-required-endpoints" "/v1/chat/completions,/v1/models"

# Data collection settings
echo "📊 Creating data collection configuration parameters..."
create_parameter "/chatbot-api/enable-logging" "true"
create_parameter "/chatbot-api/data-retention-days" "30"

echo "✅ All parameters created successfully!"
echo ""
echo "🔧 Next steps:"
echo "   1. Update the API key parameters with your actual keys:"
echo "      aws ssm put-parameter --name '/chatbot-api/openai-api-key' --value 'your-actual-key' --type SecureString --overwrite"
echo "   2. Configure Cognito parameters after CDK deployment"
echo ""
echo "📝 View all parameters:"
echo "   aws ssm get-parameters-by-path --path '/chatbot-api' --recursive"