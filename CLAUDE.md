# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chatbot wrapper API with adapter-based architecture supporting multiple AI model providers. Currently supports OpenAI API, local vLLM models, and OpenAI-compatible providers.

**Note**: Backend API service. Frontend: `../chatbot-frontend`. Deployment: AWS Lambda + API Gateway + Cognito serverless architecture.

## Current Status

**Phase 1 - Project Foundation: ✅ COMPLETED**
- ✅ Directory structure created with all planned modules
- ✅ Python package structure with `__init__.py` files
- ✅ Requirements.txt with FastAPI, vLLM, and essential dependencies
- ✅ pyproject.toml with project metadata and development tools
- ✅ Environment configuration (.env.example, .gitignore)
- ✅ Updated README.md with setup instructions (including uv support)

**Phase 2 - Core Model Adapters: ✅ COMPLETED**
- ✅ OpenAI adapter implementation supporting OpenAI API, local vLLM models, and OpenAI-compatible providers
- ✅ Model registry system for dynamic model configuration
- ✅ Settings management with environment variable support
- ✅ Unified chat completion interface across different model backends

**Phase 3 - API Endpoints & Chat Interface: ✅ COMPLETED**
- ✅ FastAPI application structure with main app file
- ✅ Chat completion endpoints using existing OpenAI adapter
- ✅ Health check and status endpoints (live, ready, comprehensive)
- ✅ Request/response models with Pydantic validation
- ✅ Error handling and logging middleware
- ✅ Adapter factory integrating with model configuration
- ✅ OpenAI-compatible API endpoints
- ✅ Streaming and non-streaming chat completions
- ✅ Model listing endpoint
- ✅ Installation and testing infrastructure

**Phase 4 - Authentication System: ✅ COMPLETED**
- ✅ Auth0 configuration settings added to settings.py
- ✅ Authentication models created (src/auth/models.py)
- ✅ Auth module structure established (src/auth/)
- ✅ Auth0 client implementation with institution registry
- ✅ JWT middleware for token validation
- ✅ Authentication API endpoints with onboarding flow
- ✅ User management system with role storage
- ✅ Integration with main FastAPI application

**Phase 5 - AWS Lambda Deployment: ✅ COMPLETED**
- ✅ Mangum wrapper for FastAPI on AWS Lambda
- ✅ AWS CDK infrastructure stack (Lambda, API Gateway, Cognito, CloudFront)
- ✅ AWS Cognito User Pools integration with OAuth providers
- ✅ API Gateway HTTP API with Cognito JWT authorizer
- ✅ AWS Systems Manager Parameter Store for secrets management
- ✅ GitHub Actions CI/CD pipeline for automated deployment
- ✅ CloudFront distribution for global edge caching
- ✅ IAM roles and security policies
- ✅ **Docker Container Deployment** - Replaced Lambda layers with container images


## Development Commands

### Key Commands for Claude
- `python run_server.py` - Start the chatbot service locally
- `python test_api.py` - Test API endpoints
- `uv pip install -r requirements.txt` - Install dependencies
- `black . && isort . && flake8 . && mypy src/` - Code quality checks
- `./deploy.sh` - Deploy to AWS Lambda using CDK with Docker containers
- `./scripts/build-docker.sh` - Build and push Docker image to ECR
- `./scripts/setup-secrets.sh` - Configure AWS Parameter Store secrets

## Implementation Guidelines

### Code Conventions
- Follow existing adapter pattern when adding new providers
- Use Pydantic models for configuration and validation
- Implement structured logging with JSON format
- Never commit API keys or sensitive configuration
- Use environment variables for secrets management

## Authentication Implementation

**Current Status**: AWS Cognito User Pools with Auth0 fallback support for educational pilot

**Key Components**:
- **Auth Models** (`src/auth/models.py`): User, session, and institution data structures
- **Cognito Client** (`src/auth/cognito_client.py`): AWS Cognito OAuth flows + institution registry
- **Auth0 Client** (`src/auth/auth0_client.py`): Legacy Auth0 support (fallback)
- **JWT Middleware** (`src/auth/middleware.py`): Token validation for both providers
- **Auth Endpoints** (`src/auth/auth.py`): Login, callback, onboarding, profile management
- **User Manager** (`src/auth/user_manager.py`): In-memory user and session management

**Supported Methods**: Google, Microsoft, SAML, GitHub, Individual accounts via Cognito Hosted UI

## Next Steps (Phase 6+ Implementation)

1. **Database Integration** (Phase 6 - Next Priority):
   - **DynamoDB Implementation**: Replace in-memory user storage with AWS DynamoDB
   - **Database Schema**: User profiles, sessions, chat history, and analytics tables
   - **Migration System**: DynamoDB table creation and schema management
   - **Analytics Queries**: DynamoDB queries for user behavior analysis and reporting
   - **Data Export**: S3 data lake integration for analytics and reporting
   - **Serverless Persistence**: Native AWS serverless database integration

2. **Additional Model Providers** (Phase 7):
   - **Anthropic Adapter** (`src/models/adapters/anthropic_adapter.py`): Claude model integration
   - **Google Adapter** (`src/models/adapters/google_adapter.py`): Gemini model support
   - **Enhanced Model Registry**: Provider-specific configurations and capability detection

3. **Enhanced Data Collection System** (Phase 8):
   - **Conversation Analytics**: Track usage patterns, model performance, user engagement
   - **Real-time Metrics**: API response times, error rates, user activity dashboards
   - **Data Analysis Tools**: Built-in analytics endpoints for team insights
   - **Privacy Controls**: FERPA compliance, data retention policies, user data deletion

## Current Implementation Status

### Completed Components
- ✅ **OpenAI Adapter** (`src/models/openai_adapter.py`): Supports OpenAI API, vLLM, and compatible providers
- ✅ **Model Configuration** (`src/config/models.py`): Centralized model registry with Pydantic validation
- ✅ **Adapter Factory** (`src/models/adapter_factory.py`): Runtime adapter management and health checks
- ✅ **Settings Management** (`src/config/settings.py`): Environment-based configuration with Cognito + Auth0 support
- ✅ **FastAPI Application** (`src/api/main.py`): Complete web server with middleware and error handling
- ✅ **API Routes** (`src/api/routes/`): Chat completions, health checks, model listing, and authentication
- ✅ **API Models** (`src/api/models.py`): OpenAI-compatible request/response models
- ✅ **Base Interfaces** (`src/models/base.py`): Abstract adapter interface and common models
- ✅ **Authentication System** (`src/auth/`): Complete Cognito + Auth0 integration with JWT middleware
  - ✅ **Cognito Client** (`src/auth/cognito_client.py`): AWS Cognito OAuth flows and user management
  - ✅ **Auth0 Client** (`src/auth/auth0_client.py`): Legacy Auth0 OAuth flows and institution registry
  - ✅ **JWT Middleware** (`src/auth/middleware.py`): Multi-provider token validation and user context
  - ✅ **Auth Endpoints** (`src/auth/auth.py`): Login, callback, onboarding, profile management
  - ✅ **User Manager** (`src/auth/user_manager.py`): In-memory user and session management
- ✅ **AWS Infrastructure** (`infrastructure/`): Complete CDK stack for serverless deployment
  - ✅ **Lambda Handler** (`lambda_handler.py`): Mangum FastAPI wrapper with Parameter Store integration
  - ✅ **CDK Stack** (`infrastructure/chatbot_stack.py`): Lambda, API Gateway, Cognito, CloudFront, S3
  - ✅ **Secrets Management** (`scripts/setup-secrets.sh`): AWS Parameter Store configuration
  - ✅ **CI/CD Pipeline** (`.github/workflows/deploy.yml`): Automated testing and deployment
- ✅ **Testing Infrastructure** (`test_api.py`, `run_server.py`): Development and testing tools
- ✅ **Deployment Tools** (`deploy.sh`, `requirements.txt`): Production deployment and dependency management


## Current Working State

The application is now **fully functional** for Phase 5 objectives with serverless AWS deployment:

### ✅ Local Development
- **Installation**: `uv pip install -r requirements.txt`
- **Startup**: `python run_server.py`
- **Testing**: `python test_api.py`
- **API Docs**: `http://localhost:8000/docs`

### ✅ AWS Deployment
- **Setup Secrets**: `./scripts/setup-secrets.sh`
- **Deploy**: `./deploy.sh`
- **CI/CD**: Automated deployment via GitHub Actions
- **Monitoring**: CloudWatch logs and Lambda metrics

### ✅ Working Features
- OpenAI-compatible REST API endpoints
- AWS Cognito authentication with OAuth providers
- Health checks and status monitoring
- Model listing and discovery
- Chat completions (streaming and non-streaming)
- Error handling with structured logging
- Global edge caching via CloudFront
- Secure secrets management via Parameter Store

### ⚠️ Configuration Required

**For Development Environment:**
1. **AWS Setup**: Configure AWS credentials and account ID
2. **Secrets**: Run `./scripts/setup-secrets.sh dev` and update API keys
3. **Deploy**: Run `./deploy.sh dev`
4. **OAuth**: Dev environment uses `http://localhost:3000` for OAuth callbacks

**For Production Environment:**
1. **Update Production URLs**: Edit `infrastructure/chatbot_stack.py` lines 320-321 and 330 to replace `your-domain.com` with your actual production domain
2. **Secrets**: Run `./scripts/setup-secrets.sh prod` and update API keys
3. **Deploy**: Run `./deploy.sh prod`
4. **OAuth**: Configure production OAuth providers in Cognito User Pool

**Environment Separation:**
- **Resources**: Each environment gets separate Lambda functions, S3 buckets, Cognito pools
- **Parameters**: Environment-specific Parameter Store paths (`/chatbot-api/dev/` vs `/chatbot-api/prod/`)
- **Naming**: All resources include environment suffix (e.g., `chatbot-api-dev-lambda`)
- **CORS**: Dev allows localhost, prod restricts to production domains

### 🔧 Development Tools
- `run_server.py`: Local server startup with graceful shutdown
- `test_api.py`: Comprehensive API endpoint testing
- `deploy.sh`: Production deployment with validation
- `scripts/setup-secrets.sh`: AWS Parameter Store configuration
- Interactive API documentation at `/docs` endpoint