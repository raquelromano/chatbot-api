# Chatbot API

A serverless chatbot API with adapter-based architecture that provides a unified interface for multiple AI model providers. Currently supports OpenAI API, local vLLM models, and OpenAI-compatible providers, with planned support for Anthropic and Google models.

**Features**: AWS Cognito authentication, serverless AWS Lambda deployment, global edge caching, and enterprise-grade security.

**Note**: This is the backend API service. The frontend UI is developed separately in `../chatbot-frontend`.

## Quick Start

### Prerequisites
```bash
# Install uv (recommended) or ensure Python 3.11+ is available
curl -LsSf https://astral.sh/uv/install.sh | sh

# For deployment: Docker, AWS CLI, and CDK
docker info
aws sts get-caller-identity
npm install -g aws-cdk
```

### Local Development Setup

The project uses **two separate virtual environments**:
- **`.venv-app`**: Application runtime (FastAPI, model adapters, testing)
- **`.venv-cdk`**: Infrastructure deployment (AWS CDK, deployment tools)

```bash
# 1. Setup application environment
uv venv .venv-app && source .venv-app/bin/activate
uv pip install -r requirements.txt

# 2. Setup CDK environment (deployment only)
uv venv infrastructure/.venv-cdk && source infrastructure/.venv-cdk/bin/activate
uv pip install -r infrastructure/requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY and other settings

# 4. Run and test locally
source .venv-app/bin/activate
python run_server.py              # Start server at http://localhost:8000/docs
python test_api.py                # Test API endpoints
```

### AWS Deployment

**Docker Container Deployment** to AWS Lambda with automatic infrastructure provisioning:

```bash
# Configure AWS credentials
aws configure
# Or set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

# Deploy to development
source infrastructure/.venv-cdk/bin/activate
./deploy.sh dev

# Deploy to production (update domain in infrastructure/chatbot_stack.py first)
./deploy.sh prod
```

**Post-deployment**: Update Google API key in AWS Secrets Manager:
```bash
aws secretsmanager put-secret-value \
  --secret-id "chatbot-api/dev/google-api-key" \
  --secret-string '{"api_key":"your-real-google-api-key-here"}'
```

**Deployment Features**:
- Automatic ECR repository creation and Docker image management
- Passwordless email authentication via Cognito (no OAuth setup needed)
- Environment isolation (dev/prod with separate resources)
- **Timing**: First deployment 8-12 min, subsequent 3-5 min, code-only 2-3 min

**Local Container Testing** (same as deployed):
```bash
./scripts/build-docker.sh dev
docker run -p 8000:8080 chatbot-api:dev
```

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

### Local Development Commands
```bash
source .venv-app/bin/activate    # Activate application environment
python run_server.py             # Start development server
```

### Testing
```bash
source .venv-app/bin/activate    # Activate application environment
# Note: pytest is available in requirements.txt but no test suites are currently implemented
```

### Docker Operations
```bash
source infrastructure/.venv-cdk/bin/activate   # Activate CDK environment
./deploy.sh dev                                 # Full deployment
./scripts/build-docker.sh dev                  # Build/push image only
docker run -p 8000:8080 chatbot-api:dev        # Test deployed container locally
```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and configure the following settings:

### Environment-Specific Configuration Files

The project includes YAML configuration files for different deployment environments:

- **`infrastructure/config/dev.yaml`** - Development environment configuration
- **`infrastructure/config/prod.yaml`** - Production environment configuration

These files configure environment-specific settings including:
- **Email Configuration**: SES sender email address for passwordless authentication
- **CORS Settings**: Allowed origins for cross-origin requests based on where your frontend is hosted

**Usage**: These files are automatically loaded during CDK deployment based on the environment parameter passed to `./deploy.sh {env}`.

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

#### API Keys for Model Providers
```bash
# Google API (required for Gemini models - CURRENTLY ENABLED)
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI API (optional - models currently disabled)
# OPENAI_API_KEY=your_openai_key_here

# Anthropic API (optional - no adapter implementation yet)
# ANTHROPIC_API_KEY=your_anthropic_key_here
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

# API Keys (configure as needed)
GOOGLE_API_KEY=your-google-api-key-here
# OPENAI_API_KEY=sk-your-openai-key-here  # Optional - models disabled
# ANTHROPIC_API_KEY=your-anthropic-key-here  # Optional - no adapter yet

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

#### Core API Testing (No Authentication)
```bash
# Basic endpoints
curl http://localhost:8000/v1/models
curl http://localhost:8000/health/
curl http://localhost:8000/

# Chat completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}], "model_id": "gemini-2.5-flash"}'
```

#### Passwordless Authentication Flow
```bash
# 1. Request verification code
curl -X POST [BASE_URL]/auth/passwordless/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'

# 2. Verify code and get JWT token
curl -X POST [BASE_URL]/auth/passwordless/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com", "session": "SESSION_TOKEN", "code": "123456"}'

# 3. Use JWT for authenticated requests
curl -X POST [BASE_URL]/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer JWT_TOKEN" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}], "model_id": "gemini-2.5-flash"}'
```

**Base URLs**: `http://localhost:8000` (local) or `https://your-api-domain.com` (deployed)

**Finding Verification Codes**:
- **Development**: Check CloudWatch logs `/aws/lambda/chatbot-api-dev-create-auth`
- **Production**: Codes sent via email (requires SES domain setup)

```bash
# View verification codes in CloudWatch (development)
aws logs filter-log-events \
  --log-group-name "/aws/lambda/chatbot-api-dev-create-auth" \
  --filter-pattern "Verification code for your-email@example.com"
```

## CI/CD Configuration

<details>
<summary>Click to expand CI/CD details (currently disabled)</summary>

### Manual Deployment Only

GitHub Actions is configured for **manual deployments only**. Automatic triggers on `main` branch pushes have been disabled.

**To deploy manually:**
1. Go to GitHub Actions → "Deploy Chatbot API" workflow
2. Click "Run workflow" → Select branch → "Run workflow"

**To re-enable automatic deployments:** Uncomment the `push` and `pull_request` triggers in `.github/workflows/deploy.yml`

</details>

