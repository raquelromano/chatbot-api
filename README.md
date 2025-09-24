# Chatbot API

A serverless chatbot API with adapter-based architecture that provides a unified interface for multiple AI model providers. Currently supports OpenAI API, local vLLM models, and OpenAI-compatible providers, with planned support for Anthropic and Google models.

**Features**: AWS Cognito authentication, serverless AWS Lambda deployment, global edge caching, and enterprise-grade security.

**Note**: This is the backend API service. The frontend UI is developed separately in `../chatbot-frontend`.

## Quick Start

### Local Development

The project uses **two separate virtual environments**:
- **Application Environment** (`.venv-app`): For running the chatbot API locally
- **Infrastructure Environment** (`.venv-cdk`): For AWS CDK deployment commands

1. **Setup Application Environment:**
   ```bash
   # Using uv (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv .venv-app && source .venv-app/bin/activate
   uv pip install -r requirements.txt

   # Or using pip
   python -m venv .venv-app && source .venv-app/bin/activate
   pip install -r requirements.txt
   ```

2. **Setup CDK Environment (for deployment only):**
   ```bash
   # Using uv (recommended)
   uv venv infrastructure/.venv-cdk && source infrastructure/.venv-cdk/bin/activate
   uv pip install -r infrastructure/requirements.txt

   # Or using pip
   python -m venv infrastructure/.venv-cdk && source infrastructure/.venv-cdk/bin/activate
   pip install -r infrastructure/requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Run locally (using Application Environment):**
   ```bash
   source .venv-app/bin/activate    # Activate application environment
   python run_server.py
   # API docs: http://localhost:8000/docs
   ```

5. **Test the API:**
   ```bash
   source .venv-app/bin/activate    # Activate application environment
   python test_api.py
   ```

### Virtual Environment Management

**For Local Development & Testing:**
```bash
source .venv-app/bin/activate      # Application environment
python run_server.py              # Run API server
python test_api.py                # Test API endpoints
```

**For AWS Deployment:**
```bash
source infrastructure/.venv-cdk/bin/activate   # CDK environment
./deploy.sh dev                               # Deploy using separate environments
```

**Environment Contents:**
- **`.venv-app`**: FastAPI, authentication, AWS SDK, model adapters, testing tools
- **`.venv-cdk`**: AWS CDK libraries, deployment tools, infrastructure code

### AWS Deployment (Docker Container)

The application uses **Docker containers** for AWS Lambda deployment, providing:
- ✅ Exact Lambda runtime environment (Python 3.11)
- ✅ Eliminates cross-platform dependency issues
- ✅ Fast rebuilds with Docker layer caching
- ✅ Industry standard container deployment

#### Prerequisites
```bash
# Check Docker is running
docker info

# Check AWS credentials
aws sts get-caller-identity

# Install AWS CDK
npm install -g aws-cdk
```

#### Development Environment

1. **Configure AWS credentials:**
   ```bash
   aws configure
   # Or set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
   ```

2. **Deploy to development:**
   ```bash
   ./deploy.sh dev
   ```
   This automatically creates secrets in AWS Secrets Manager (with placeholder values) and sets up passwordless email authentication via Cognito.

3. **Update API key with real value:**
   ```bash
   # After deployment, update the Google API key:
   aws secretsmanager put-secret-value \
     --secret-id "chatbot-api/dev/google-api-key" \
     --secret-string '{"api_key":"your-real-google-api-key-here"}'

   # Or update via AWS Console: Secrets Manager
   # Note: Only Google API key is required (OpenAI/Anthropic models are disabled)
   ```

**That's it!** The application now uses **passwordless authentication** with email verification codes, so no OAuth provider setup is needed.

**Optional: OAuth Provider Setup** (if you want to add OAuth login options):

<details>
<summary>Click to expand OAuth configuration steps</summary>

**Extract deployment values:**
Get the deployment's values for `UserPoolId`, `UserPoolClientId`, and `CognitoDomain` from infrastructure/cdk-outputs.json
```bash
USER_POOL_ID=<user-pool-id>
USER_POOL_CLIENT_ID=<user-pool-client-id>
COGNITO_DOMAIN=<cognito-domain>
```

**Configure OAuth providers:**

**First, get your OAuth app credentials:**

**Google OAuth Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials) → Create OAuth 2.0 Client
2. Set **Authorized redirect URIs** to: `https://$COGNITO_DOMAIN.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`
3. Copy your **Client ID** and **Client Secret**

**Microsoft OAuth Setup:**
1. Go to [Azure App Registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps) → New Registration
2. Set **Redirect URI** to: `https://$COGNITO_DOMAIN.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`
3. Copy your **Application (client) ID** and create a **Client Secret**

**GitHub OAuth Setup:**
1. Go to Settings → Developer settings → OAuth Apps → New OAuth App
2. Set **Authorization callback URL** to: `https://$COGNITO_DOMAIN.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`
3. Copy your **Client ID** and **Client Secret**

**Then configure providers via AWS CLI:**
```bash
# Configure Google OAuth provider
aws cognito-idp create-identity-provider \
  --user-pool-id "$USER_POOL_ID" \
  --provider-name "Google" \
  --provider-type "Google" \
  --provider-details '{
    "client_id": "your-google-client-id.apps.googleusercontent.com",
    "client_secret": "your-google-client-secret",
    "authorize_scopes": "openid email profile"
  }' \
  --attribute-mapping '{
    "email": "email",
    "given_name": "given_name",
    "family_name": "family_name"
  }'

# Enable OAuth providers on your User Pool Client
aws cognito-idp update-user-pool-client \
  --user-pool-id "$USER_POOL_ID" \
  --client-id "$USER_POOL_CLIENT_ID" \
  --supported-identity-providers "Google" "COGNITO" \
  --callback-urls "http://localhost:3000/callback" \
  --logout-urls "http://localhost:3000/logout"
```

</details>

The deployment automatically:
   - Creates ECR repository (if needed)
   - Builds and pushes Docker image
   - Deploys Lambda function with container

   **Local Testing** (same container as deployed):
   ```bash
   # Build image locally (after first deployment)
   ./scripts/build-docker.sh dev

   # Test same container locally
   docker run -p 8000:8080 chatbot-api:dev
   ```

**First-time deployment:** 8-12 minutes (includes CDK bootstrap, infrastructure setup, ECR setup)
**Subsequent deployments:** 3-5 minutes (Docker layer caching + CDK asset caching)
**Code-only changes:** 2-3 minutes (only changed layers rebuild)

#### Production Environment

1. **Update production URLs** in `infrastructure/chatbot_stack.py`:
   - Replace `your-domain.com` with your actual production domain (lines 320-321, 330)

2. **Deploy to production:**
   ```bash
   ./deploy.sh prod
   ```
   This automatically creates secrets in AWS Secrets Manager.

3. **Update API key with real value:**
   ```bash
   # After deployment, update the Google API key:
   aws secretsmanager put-secret-value \
     --secret-id "chatbot-api/prod/google-api-key" \
     --secret-string '{"api_key":"your-real-google-api-key-here"}'
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
source .venv-app/bin/activate   # Activate application environment
pytest                          # Run all tests
pytest tests/unit/              # Run unit tests only
pytest tests/integration/       # Run integration tests only
```

### Code Quality
```bash
source .venv-app/bin/activate   # Activate application environment
black .                         # Format code
isort .                         # Sort imports
flake8 .                        # Lint code
mypy src/                       # Type checking
```

### Docker Deployment
```bash
source infrastructure/.venv-cdk/bin/activate   # Activate CDK environment
./deploy.sh dev                                 # Full deployment (creates ECR, builds/pushes image, deploys Lambda)
./scripts/build-docker.sh dev                  # Build and push Docker image only (after ECR exists)

# Test deployed container locally (no venv needed for Docker)
docker run -p 8000:8080 chatbot-api:dev        # Test same container locally that's deployed
docker build -t chatbot-demo .                 # Build local development container (different from deployed)
```

## Model Providers

### Currently Supported (ENABLED)
- **Google Gemini**: Gemini 2.5 Pro and Gemini 2.5 Flash via Google AI API
  - Requires `GOOGLE_API_KEY`
  - 2M token context (Pro), 1M token context (Flash)

### Available but Disabled
- **OpenAI API**: GPT-3.5, GPT-4, etc. (can be re-enabled in `src/config/models.py`)
- **Local vLLM Models**: Llama, Mistral, etc. via OpenAI-compatible server
- **OpenAI-Compatible Providers**: Any OpenAI-compatible endpoint

### Partially Implemented
- **Anthropic**: Model configs exist, but adapter implementation needed for Claude models

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

**✅ Passwordless authentication when `ENABLE_AUTH=true`:**
```bash
# 1. Request verification code (sent to email)
curl -X POST http://localhost:8000/auth/passwordless/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'

# Returns: {"message": "Code sent", "session": "SESSION_TOKEN"}

# 2. Verify code and get JWT token
curl -X POST http://localhost:8000/auth/passwordless/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "session": "SESSION_TOKEN_FROM_STEP1",
    "code": "123456"
  }'

# Returns: {"access_token": "JWT_TOKEN", "user": {...}}

# 3. Use JWT for authenticated requests
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer JWT_TOKEN" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}], "model_id": "gemini-2.5-flash"}'

# Auth service status and configuration
curl http://localhost:8000/auth/status                  # Check auth configuration
curl http://localhost:8000/auth/institutions            # List educational institutions
```

**📧 Finding Verification Codes:**
- **Development**: Codes are logged to CloudWatch when email sending fails
- **Production**: Codes sent via email (requires SES domain setup)

#### Dev/Prod Deployment (AWS)

**✅ Passwordless authentication flow:**
```bash
# 1. Request verification code
curl -X POST https://your-api-domain.com/auth/passwordless/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com"}'

# 2. Get verification code from CloudWatch logs (development)
aws logs filter-log-events \
  --log-group-name "/aws/lambda/chatbot-api-dev-create-auth" \
  --filter-pattern "Verification code for your-email@example.com" \
  --no-cli-pager \
  --output text

# 3. Verify code and get JWT token
curl -X POST https://your-api-domain.com/auth/passwordless/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "session": "SESSION_TOKEN",
    "code": "123456"
  }'

# 4. Use JWT for authenticated API calls
curl -X POST https://your-api-domain.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "model_id": "gemini-2.5-flash",
    "max_tokens": 150
  }'
```

**📧 CloudWatch Log Access:**
```bash
# View recent verification codes (development)
aws logs filter-log-events \
  --log-group-name "/aws/lambda/chatbot-api-dev-create-auth" \
  --start-time $(date -d '10 minutes ago' +%s)000

# Or view in AWS Console: CloudWatch → Log Groups → /aws/lambda/chatbot-api-dev-create-auth
```

**Note**: Full authentication testing requires both backend API and frontend application running, as OAuth callbacks are handled by the frontend at `localhost:3000` (dev) or your production domain (prod).



## Deployment Architecture

The application deploys as a serverless architecture on AWS with full dev/prod environment separation:

**Infrastructure Components:**
- **AWS Lambda**: FastAPI application with Mangum adapter (Docker container deployment)
- **Amazon ECR**: Container registry for Docker images with automatic lifecycle management
- **API Gateway**: HTTP API with Cognito JWT authorization
- **Cognito User Pools**: OAuth authentication with multiple providers
- **CloudFront**: Global CDN for edge caching and performance
- **S3**: Static asset storage with secure access
- **Secrets Manager**: Encrypted secrets with automatic rotation support
- **CloudWatch**: Monitoring, logging, and alerting

**Environment Separation:**
- **Resources**: Each environment gets isolated Lambda functions, S3 buckets, Cognito pools
- **Naming**: All resources include environment suffix (e.g., `chatbot-api-dev-lambda`, `chatbot-api-prod-lambda`)
- **Configuration**: Environment-specific Secrets Manager paths (`chatbot-api/dev/`, `chatbot-api/prod/`)
- **Security**: Dev allows localhost CORS, prod restricts to production domains
- **OAuth**: Dev uses `localhost:3000` callbacks, prod uses your production domain

## Project Status

**✅ PRODUCTION READY** - Fully functional serverless API with enterprise authentication, global deployment, and CI/CD pipeline.

### Completed Features
- ✅ Google Gemini model adapter (2.5 Pro and 2.5 Flash) - ENABLED
- ✅ Multi-provider model adapters (OpenAI, vLLM, compatible APIs) - Available but disabled
- ✅ AWS Cognito authentication with OAuth providers
- ✅ Serverless AWS Lambda deployment with Docker containers via CDK
- ✅ Global edge caching via CloudFront
- ✅ Secure secrets management via Secrets Manager
- ✅ Automated CI/CD with GitHub Actions
- ✅ Health monitoring and structured logging

### Next Steps
- 🔄 **Phase 6**: DynamoDB integration for persistent user storage
- ✅ **Phase 7**: Google Gemini models (COMPLETED) - Anthropic adapter implementation still needed
- 🔄 **Phase 8**: Enhanced analytics and usage tracking