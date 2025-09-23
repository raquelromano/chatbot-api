# Chatbot API

A serverless chatbot API with adapter-based architecture that provides a unified interface for multiple AI model providers. Currently supports OpenAI API, local vLLM models, and OpenAI-compatible providers, with planned support for Anthropic and Google models.

**Features**: AWS Cognito authentication, serverless AWS Lambda deployment, global edge caching, and enterprise-grade security.

**Note**: This is the backend API service. The frontend UI is developed separately in `../chatbot-frontend`.

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv && source .venv/bin/activate
   uv pip install -r requirements.txt

   # Or using pip
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run locally:**
   ```bash
   python run_server.py
   # API docs: http://localhost:8000/docs
   ```

4. **Test the API:**
   ```bash
   python test_api.py
   ```

### AWS Deployment

The application supports separate development and production environments.

#### Development Environment

1. **Install AWS CDK:**
   ```bash
   npm install -g aws-cdk
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   # Or set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
   ```

3. **Setup development secrets:**
   ```bash
   ./scripts/setup-secrets.sh dev
   # Update API keys in AWS Parameter Store for dev environment
   ```

4. **Deploy to development:**
   ```bash
   ./deploy.sh dev
   ```

#### Production Environment

1. **Update production URLs** in `infrastructure/chatbot_stack.py`:
   - Replace `your-domain.com` with your actual production domain (lines 320-321, 330)

2. **Setup production secrets:**
   ```bash
   ./scripts/setup-secrets.sh prod
   # Update API keys in AWS Parameter Store for prod environment
   ```

3. **Deploy to production:**
   ```bash
   ./deploy.sh prod
   ```

#### CI/CD with GitHub Actions
Both environments can be deployed automatically via GitHub Actions workflows.

## Project Structure

```
chatbot-api/
├── src/
│   ├── config/          # Configuration management and settings
│   ├── models/          # Model adapters and abstraction layer
│   ├── api/             # FastAPI endpoints and request handling
│   ├── auth/            # Authentication (Cognito + Auth0)
│   └── utils/           # Shared utilities and helpers
├── infrastructure/      # AWS CDK infrastructure as code
├── .github/workflows/   # GitHub Actions CI/CD pipeline
├── scripts/             # Deployment and utility scripts
├── lambda_handler.py    # AWS Lambda entry point
├── deploy.sh           # Deployment script
└── requirements.txt    # Python dependencies
```

## Development

### Testing
```bash
pytest                    # Run all tests
pytest tests/unit/        # Run unit tests only
pytest tests/integration/ # Run integration tests only
```

### Code Quality
```bash
black .                   # Format code
isort .                   # Sort imports
flake8 .                  # Lint code
mypy src/                 # Type checking
```

### Docker
```bash
docker-compose up         # Start local development environment
docker build -t chatbot-demo .  # Build application container
```

## Model Providers

### Currently Supported
- **OpenAI API**: Direct integration with OpenAI models (GPT-3.5, GPT-4, etc.)
- **Local vLLM Models**: Local deployment of open-source models (Llama, Mistral, etc.) via vLLM's OpenAI-compatible server
- **OpenAI-Compatible Providers**: Any provider that implements OpenAI-compatible endpoints

### Planned Support
- **Anthropic**: Claude models via Anthropic API
- **Google**: Gemini models via Google AI API

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and configure the following settings:

### Required Environment Variables

#### Basic Application Settings
```bash
APP_NAME=Chatbot Wrapper Demo      # Application display name
DEBUG=false                        # Enable debug mode and API docs
HOST=0.0.0.0                      # Server host binding
PORT=8000                         # Server port
```

#### Model Configuration
```bash
DEFAULT_MODEL=local               # Default model to use (local/openai/anthropic)
VLLM_HOST=localhost              # vLLM server host for local models
VLLM_PORT=8001                   # vLLM server port for local models
```

#### API Keys for External Model Providers
```bash
# OpenAI API (required for OpenAI models)
OPENAI_API_KEY=your_openai_key_here

# Anthropic API (required for Claude models - planned)
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Authentication Configuration

#### AWS Cognito Setup (Primary - Deployed)
```bash
# Enable/disable authentication system
ENABLE_AUTH=true                              # Set to 'true' to enable authentication

# AWS Cognito Configuration (primary for deployment)
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx     # From CDK deployment outputs
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx  # From CDK deployment outputs
COGNITO_REGION=us-east-1                      # AWS region
AWS_ACCOUNT_ID=123456789012                   # Your AWS account ID

# JWT Token Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production  # JWT signing key
JWT_ALGORITHM=HS256                           # JWT algorithm (HS256 recommended)
JWT_EXPIRATION_HOURS=24                       # Token expiration time

# Protected Endpoints
AUTH_REQUIRED_ENDPOINTS=/v1/chat/completions,/v1/models # Comma-separated list
```

#### Auth0 Setup (Legacy Fallback)
```bash
# Auth0 Configuration (fallback for local development)
AUTH0_DOMAIN=your-tenant.auth0.com            # Your Auth0 domain
AUTH0_CLIENT_ID=your_auth0_client_id          # Auth0 application client ID
AUTH0_CLIENT_SECRET=your_auth0_client_secret  # Auth0 application client secret
AUTH0_AUDIENCE=https://your-api-identifier    # Auth0 API identifier (optional)
```

#### Cognito User Pool Setup

The CDK deployment automatically creates a Cognito User Pool with:

1. **OAuth Providers**: Google, Microsoft, SAML, GitHub support
2. **Hosted UI**: Pre-built login/signup interface
3. **JWT Tokens**: Automatic token validation via API Gateway
4. **User Management**: Admin functions for user creation/deletion

To configure OAuth providers:
1. Go to AWS Cognito Console
2. Select your User Pool (created by CDK)
3. Configure identity providers under "Sign-in experience"
4. Add OAuth app credentials for each provider

### Data Collection & Logging
```bash
ENABLE_LOGGING=true              # Enable structured logging
LOG_LEVEL=INFO                   # Log level (DEBUG/INFO/WARNING/ERROR)
DATA_RETENTION_DAYS=30           # Data retention period
```

### Example Complete .env File
```bash
# Application Configuration
APP_NAME=Chatbot Wrapper Demo
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Model Configuration
DEFAULT_MODEL=local
VLLM_HOST=localhost
VLLM_PORT=8001

# API Keys (uncomment and configure as needed)
# OPENAI_API_KEY=sk-your-openai-key-here
# ANTHROPIC_API_KEY=your-anthropic-key-here

# Authentication Configuration
ENABLE_AUTH=true
AUTH0_DOMAIN=myapp.us.auth0.com
AUTH0_CLIENT_ID=abc123def456
AUTH0_CLIENT_SECRET=supersecret123
AUTH0_AUDIENCE=https://chatbot-api
JWT_SECRET_KEY=change-this-in-production-use-long-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
AUTH_REQUIRED_ENDPOINTS=["/v1/chat/completions"]

# Data Collection
ENABLE_LOGGING=true
LOG_LEVEL=INFO
DATA_RETENTION_DAYS=30
```

### Configuration Validation

The application will validate configuration on startup:
- ✅ **Without Authentication**: Only model configuration is required
- ✅ **With Authentication**: Auth0 credentials must be provided when `ENABLE_AUTH=true`
- ⚠️ **Missing API Keys**: External model providers require their respective API keys

## API Endpoints

The application provides OpenAI-compatible REST API endpoints:

### Chat Completions
- **POST** `/v1/chat/completions` - Create chat completions (⚠️ requires authentication when enabled)
- **GET** `/v1/models` - List available models

### Authentication (when enabled)
- **GET** `/auth/login` - Initiate OAuth login flow
- **GET** `/auth/callback` - Handle OAuth callback from Auth0
- **POST** `/auth/onboarding` - Complete user role selection
- **GET** `/auth/profile` - Get current user profile (requires auth)
- **POST** `/auth/refresh` - Refresh access token (requires auth)
- **POST** `/auth/logout` - Logout and invalidate tokens (requires auth)
- **GET** `/auth/institutions` - List available educational institutions
- **GET** `/auth/status` - Authentication service status

### Health & Status  
- **GET** `/health/` - Comprehensive health check
- **GET** `/health/ready` - Kubernetes readiness probe
- **GET** `/health/live` - Kubernetes liveness probe

### Documentation
- **GET** `/docs` - Interactive API documentation (when debug=true)
- **GET** `/` - Basic service information

### Example Usage

#### Local Development (localhost:8000)

**✅ Testable endpoints when `ENABLE_AUTH=false`:**
```bash
# Core API functionality
curl http://localhost:8000/v1/models                    # List available models
curl http://localhost:8000/v1/chat/completions \        # Create chat completion
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}], "model_id": "gemini-2.5-flash"}'

# Health and status
curl http://localhost:8000/health/                      # Comprehensive health check
curl http://localhost:8000/                             # Basic service info
```

**⚠️ Limited auth endpoints when `ENABLE_AUTH=true` (no frontend):**
```bash
# Auth service status and configuration
curl http://localhost:8000/auth/status                  # Check auth configuration
curl http://localhost:8000/auth/institutions            # List educational institutions
curl "http://localhost:8000/auth/login?redirect_uri=http://localhost:3000/callback"  # Generate OAuth URL

# ❌ Cannot complete full OAuth flow without frontend at localhost:3000
# ❌ Cannot test: /auth/callback, /auth/profile, /auth/onboarding, /auth/logout
```

#### Dev/Prod Deployment (with frontend)

**✅ Full authentication flow available:**
```bash
# Complete OAuth login flow (via frontend)
curl "https://your-api-domain.com/auth/login?redirect_uri=https://your-frontend-domain.com/callback"

# Authenticated API calls (after OAuth completion)
curl -X POST https://your-api-domain.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "model_id": "gemini-2.5-flash",
    "max_tokens": 150
  }'

# User management
curl https://your-api-domain.com/auth/profile \          # Get user profile
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
curl -X POST https://your-api-domain.com/auth/onboarding \  # Complete user onboarding
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"role": "student", "institution_id": "example"}'
```

**Note**: Full authentication testing requires both backend API and frontend application running, as OAuth callbacks are handled by the frontend at `localhost:3000` (dev) or your production domain (prod).



## Deployment Architecture

The application deploys as a serverless architecture on AWS with full dev/prod environment separation:

**Infrastructure Components:**
- **AWS Lambda**: FastAPI application with Mangum adapter
- **API Gateway**: HTTP API with Cognito JWT authorization
- **Cognito User Pools**: OAuth authentication with multiple providers
- **CloudFront**: Global CDN for edge caching and performance
- **S3**: Static asset storage with secure access
- **Parameter Store**: Encrypted secrets and configuration management
- **CloudWatch**: Monitoring, logging, and alerting

**Environment Separation:**
- **Resources**: Each environment gets isolated Lambda functions, S3 buckets, Cognito pools
- **Naming**: All resources include environment suffix (e.g., `chatbot-api-dev-lambda`, `chatbot-api-prod-lambda`)
- **Configuration**: Environment-specific Parameter Store paths (`/chatbot-api/dev/`, `/chatbot-api/prod/`)
- **Security**: Dev allows localhost CORS, prod restricts to production domains
- **OAuth**: Dev uses `localhost:3000` callbacks, prod uses your production domain

## Project Status

**✅ PRODUCTION READY** - Fully functional serverless API with enterprise authentication, global deployment, and CI/CD pipeline.

### Completed Features
- ✅ Multi-provider model adapters (OpenAI, vLLM, compatible APIs)
- ✅ AWS Cognito authentication with OAuth providers
- ✅ Serverless AWS Lambda deployment with CDK
- ✅ Global edge caching via CloudFront
- ✅ Secure secrets management via Parameter Store
- ✅ Automated CI/CD with GitHub Actions
- ✅ Health monitoring and structured logging

### Next Steps
- 🔄 **Phase 6**: DynamoDB integration for persistent user storage
- 🔄 **Phase 7**: Additional model providers (Anthropic, Google)
- 🔄 **Phase 8**: Enhanced analytics and usage tracking