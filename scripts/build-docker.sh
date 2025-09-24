#!/bin/bash

# Build Docker image for Lambda container deployment
# Replaces the complex Lambda layers approach with a simple Docker build

set -e  # Exit on any error

# Default environment
ENVIRONMENT=${1:-dev}

echo "🐳 Building Docker image for Chatbot API - Environment: $ENVIRONMENT..."

# Get AWS account ID and region for ECR
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
AWS_REGION=${AWS_REGION:-us-east-1}

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# ECR repository details
ECR_REPOSITORY="chatbot-api-${ENVIRONMENT}"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

echo "📋 Build Information:"
echo "   🏷️  Environment: $ENVIRONMENT"
echo "   📦 ECR Repository: $ECR_REPOSITORY"
echo "   🌍 Region: $AWS_REGION"
echo "   🏦 Account: $AWS_ACCOUNT_ID"
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop or Docker daemon."
    exit 1
fi

# Login to ECR
echo "🔐 Logging into Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI || {
    echo "❌ ECR login failed. Make sure the repository exists and you have permissions."
    exit 1
}

# Build the Docker image
echo "🏗️  Building Docker image..."
docker build \
    --platform linux/amd64 \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    -t chatbot-api:$ENVIRONMENT \
    -t chatbot-api:latest \
    -t $ECR_URI:$ENVIRONMENT \
    -t $ECR_URI:latest \
    . || {
    echo "❌ Docker build failed"
    exit 1
}

# Push the image to ECR
echo "📤 Pushing image to ECR..."
docker push $ECR_URI:$ENVIRONMENT || {
    echo "❌ Docker push failed"
    exit 1
}

docker push $ECR_URI:latest || {
    echo "❌ Docker push (latest) failed"
    exit 1
}

echo "✅ Docker image built and pushed successfully!"
echo ""
echo "📊 Image Information:"
echo "   🏷️  Tag: $ENVIRONMENT"
echo "   📍 URI: $ECR_URI:$ENVIRONMENT"
echo "   📏 Size: $(docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}' | grep chatbot-api:$ENVIRONMENT | awk '{print $2}')"
echo ""
echo "🚀 Ready for Lambda deployment!"
echo ""
echo "💡 Benefits of Docker approach:"
echo "   ✅ No more cross-platform dependency issues"
echo "   ✅ Exact Lambda runtime environment"
echo "   ✅ Faster iteration with Docker layer caching"
echo "   ✅ Industry standard container deployment"
echo ""
echo "Next: Run './deploy.sh $ENVIRONMENT' to deploy the container to Lambda"