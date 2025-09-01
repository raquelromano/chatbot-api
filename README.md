# Chatbot Wrapper Demo

A chatbot demo with adapter-based architecture that provides a unified interface for multiple AI model providers. Currently supports OpenAI API, local vLLM models, and OpenAI-compatible providers, with planned support for Anthropic and Google models. Designed for data collection on chatbot usage patterns and can be deployed locally or in containers on Kubernetes clusters.

**Note**: This is the backend API service. The frontend UI is developed separately in `../chatbot-frontend`.

## Quick Start

### Option 1: Using uv (recommended - faster)

1. **Install uv:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up Python environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   
   For API-only (faster, recommended for testing):
   ```bash
   uv pip install -r requirements-api-only.txt
   ```
   
   For full installation including vLLM (takes longer):
   ```bash
   uv pip install -r requirements.txt
   ```

### Option 2: Using traditional pip

1. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   
   For API-only (faster, recommended for testing):
   ```bash
   pip install -r requirements-api-only.txt
   ```
   
   For full installation including vLLM (takes longer):
   ```bash
   pip install -r requirements.txt
   ```

### Both options: Configure and run

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Run the application:**
   ```bash
   python run_server.py
   # or
   uvicorn src.api.main:app --reload
   ```

5. **Test the API:**
   ```bash
   # In another terminal
   python test_api.py
   ```

## Project Structure

```
chatbot-wrapper-demo/
├── src/
│   ├── config/          # Configuration management for model switching
│   ├── models/          # Model management and abstraction layer
│   ├── api/             # FastAPI endpoints and request handling
│   ├── web/             # Frontend chat interface
│   └── utils/           # Shared utilities and helpers
├── docker/              # Docker configurations
├── k8s/                 # Kubernetes manifests
├── scripts/             # Deployment and utility scripts
├── tests/               # Test suites
├── data/                # Data storage and exports
└── docs/                # Additional documentation
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

#### Auth0 Setup (Required for Authentication)
```bash
# Enable/disable authentication system
ENABLE_AUTH=false                 # Set to 'true' to enable authentication

# Auth0 Configuration (required when ENABLE_AUTH=true)
AUTH0_DOMAIN=your-tenant.auth0.com              # Your Auth0 domain
AUTH0_CLIENT_ID=your_auth0_client_id            # Auth0 application client ID
AUTH0_CLIENT_SECRET=your_auth0_client_secret    # Auth0 application client secret
AUTH0_AUDIENCE=https://your-api-identifier      # Auth0 API identifier (optional)

# JWT Token Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production  # JWT signing key
JWT_ALGORITHM=HS256                             # JWT algorithm (HS256 recommended)
JWT_EXPIRATION_HOURS=24                         # Token expiration time

# Protected Endpoints
AUTH_REQUIRED_ENDPOINTS=["/v1/chat/completions"] # Comma-separated list of protected endpoints
```

#### Auth0 Application Setup

To use authentication, you need to configure an Auth0 application:

1. **Create Auth0 Account**: Sign up at [auth0.com](https://auth0.com)

2. **Create Application**:
   - Go to Applications > Create Application
   - Choose "Regular Web Applications"
   - Note the Domain, Client ID, and Client Secret

3. **Configure Application**:
   - **Allowed Callback URLs**: `http://localhost:8000/auth/callback`
   - **Allowed Logout URLs**: `http://localhost:8000/`
   - **Allowed Web Origins**: `http://localhost:8000`

4. **Enable Social Connections** (optional):
   - Go to Authentication > Social
   - Enable Google, Microsoft, GitHub as needed
   - Configure with your OAuth apps

5. **Create API** (optional but recommended):
   - Go to Applications > APIs > Create API
   - Set identifier (e.g., `https://chatbot-api`)
   - Use this as AUTH0_AUDIENCE

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

#### Without Authentication
```bash
# List available models
curl http://localhost:8000/v1/models

# Create a chat completion (when ENABLE_AUTH=false)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "model_id": "gpt-3.5-turbo",
    "max_tokens": 150
  }'

# Health check
curl http://localhost:8000/health/
```

#### With Authentication
```bash
# Check auth status
curl http://localhost:8000/auth/status

# Get login URL (redirect user to this URL)
curl "http://localhost:8000/auth/login?redirect_uri=http://localhost:8000/auth/callback"

# Create authenticated chat completion (after getting JWT token)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "model_id": "gpt-3.5-turbo",
    "max_tokens": 150
  }'

# Get user profile
curl http://localhost:8000/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```



## Project Status

The application is currently **fully functional** with completed authentication, model adapters, and API endpoints. Next priority is containerization and deployment (Phase 5).