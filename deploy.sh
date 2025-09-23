#!/bin/bash

# Deploy Chatbot API to AWS Lambda using CDK

set -e  # Exit on any error

# Default environment
ENVIRONMENT=${1:-dev}

echo "🚀 Starting Chatbot API deployment for environment: $ENVIRONMENT..."

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK is not installed. Please install it first:"
    echo "   npm install -g aws-cdk"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

echo "📋 Deploying to AWS Account: $AWS_ACCOUNT_ID"
echo "📍 Region: $AWS_REGION"
echo "🏷️  Environment: $ENVIRONMENT"

# Install Python dependencies for CDK
echo "📦 Installing CDK dependencies..."
cd infrastructure
uv pip install -r requirements.txt
cd ..

# Install application dependencies
echo "📦 Installing application dependencies..."
uv pip install -r requirements.txt

# Lint and test code
# echo "🔍 Running code quality checks..."
# python -m black . --check || {
#     echo "⚠️  Code formatting issues found. Run 'black .' to fix them."
#     exit 1
# }

# python -m isort . --check-only || {
#     echo "⚠️  Import sorting issues found. Run 'isort .' to fix them."
#     exit 1
# }

# python -m flake8 . || {
#     echo "⚠️  Linting issues found. Please fix them before deploying."
#     exit 1
# }


# Bootstrap CDK if needed
echo "🔧 Bootstrapping CDK (if needed)..."
cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION || {
    echo "⚠️  CDK bootstrap failed"
    exit 1
}

# Synthesize CloudFormation template
echo "🏗️  Synthesizing CloudFormation template..."
cdk synth --context account=$AWS_ACCOUNT_ID --context region=$AWS_REGION --context environment=$ENVIRONMENT || {
    echo "❌ CDK synthesis failed"
    exit 1
}

# Deploy the stack
echo "🚀 Deploying to AWS..."
cdk deploy --context account=$AWS_ACCOUNT_ID --context region=$AWS_REGION --context environment=$ENVIRONMENT --require-approval never || {
    echo "❌ Deployment failed"
    exit 1
}

echo "✅ Deployment completed successfully!"
echo ""
echo "🔗 Your API endpoints:"
cdk output --context account=$AWS_ACCOUNT_ID --context region=$AWS_REGION --context environment=$ENVIRONMENT

echo ""
echo "📚 Next steps:"
echo "   1. Configure your API keys in AWS Systems Manager Parameter Store using: ./scripts/setup-secrets.sh $ENVIRONMENT"
echo "   2. Test your API endpoints"
echo "   3. Configure your frontend to use the new API URL"
echo ""
echo "💡 Usage: ./deploy.sh [dev|prod]  (defaults to dev)"