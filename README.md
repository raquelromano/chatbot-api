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

## Phase 1: Project Foundation ✅ COMPLETED
**Completed Tasks:**
- ✅ Initialize Python project with proper structure
- ✅ Set up virtual environment and dependency management
- ✅ Create base configuration system for model switching
- ✅ Generate requirements.txt and pyproject.toml

**Key Components:**
- Configuration management for different model types
- Environment variable handling
- Basic project scaffolding

## Phase 2: Core Model Adapters ✅ COMPLETED
**Completed Tasks:**
- ✅ Implement OpenAI adapter supporting multiple backends
- ✅ Create model registry for dynamic model configuration
- ✅ Build unified chat completion interface
- ✅ Add environment-based settings management

**Key Components:**
- `OpenAIAdapter` class supporting OpenAI API, vLLM, and compatible providers
- `ModelRegistry` for model configuration management
- Standardized chat completion responses
- Settings management with Pydantic

## Phase 3: API Endpoints & Chat Interface ✅ COMPLETED
**Completed Tasks:**
- ✅ Generate FastAPI application structure
- ✅ Create REST endpoints for chat interactions using existing OpenAI adapter
- ✅ Add health check and status endpoints
- ✅ Implement request/response models with Pydantic validation
- ✅ Add error handling and logging middleware

**Key Components:**
- FastAPI server with chat endpoints
- Request/response models for chat completions
- Health monitoring and status endpoints
- Middleware for logging and error handling

## Phase 4: Authentication System ✅ COMPLETED
**Completed Tasks:**
- ✅ Auth0 configuration settings and environment variables
- ✅ Authentication data models (users, sessions, institutions)
- ✅ Auth module structure (`src/auth/`)
- ✅ Auth0 client implementation with institution registry
- ✅ JWT middleware for token validation and user context injection
- ✅ Authentication API endpoints (login, callback, onboarding, profile, logout)
- ✅ User management system with in-memory storage for pilot
- ✅ FastAPI integration with authentication middleware

**Key Components:**
- **Institution Registry**: Curated list of partner educational institutions
- **Multi-Provider SSO**: Support for Google, Microsoft, SAML, and individual accounts
- **User Onboarding**: Role selection flow for institutional and individual users
- **Standards-Based**: OAuth2/OIDC with JWT tokens for portability

**Authentication Strategy:**
- Simplified approach for 6-month pilot with <5 partner institutions
- Manual institution registry with auto-detection from email domains
- User role selection during first login (Student/Educator/Individual)
- Auth0 as universal authentication hub to avoid vendor lock-in
- Support for educational SSO (SAML) and social login fallbacks

## Phase 5: Containerization & Deployment (Next Priority)
**Planned Tasks:**
- **Docker Implementation**: Create Dockerfile with multi-stage builds for optimized container size
- **Docker Compose**: Local development environment with all services (API, Auth0, optional vLLM)
- **Container Optimization**: Dependency caching, security hardening, health checks
- **Environment Configuration**: Container-friendly environment variable handling
- **Cloud Integration**: Integration with infrastructure being developed in `../augmented-infra`
- **Kubernetes Manifests**: Deployments, services, ingress, and ConfigMaps for cloud deployment
- **CI/CD Pipeline**: Automated testing, building, and deployment workflows

**Key Components:**
- `Dockerfile` with multi-stage builds for production optimization
- `docker-compose.yml` for local development with service dependencies
- Kubernetes manifests (deployment, service, ingress, configmap)
- Health check endpoints optimized for container orchestration
- Environment-specific configuration management
- Integration points with `../augmented-infra` cloud infrastructure

**Benefits:**
- **Deployment Ready**: Containerized application ready for cloud deployment
- **Development Consistency**: Identical environments across development, testing, and production
- **Scalability**: Kubernetes-ready for horizontal scaling and load balancing
- **Infrastructure Integration**: Seamless integration with existing cloud infrastructure
- **CI/CD Ready**: Automated deployment pipeline for continuous delivery

## Phase 6: Database Integration
**Planned Tasks:**
- **SQLite Implementation**: Replace in-memory user storage with persistent SQLite database
- **Database Schema**: Design tables for users, sessions, chat history, and analytics
- **Container Persistence**: Database file persistence and backup in containerized environments
- **Migration System**: Database versioning and upgrade scripts for schema changes
- **Analytics Queries**: SQL queries for user behavior analysis and team reporting
- **Data Export**: Backup capabilities and data analysis export utilities

**Key Components:**
- `DatabaseManager` class for SQLite operations and connection management
- Database models with SQLAlchemy for users, sessions, conversations, and analytics
- Container volume management for database persistence
- Migration scripts for database schema versioning and upgrades
- Analytics endpoints for real-time user behavior and usage reporting

**Benefits:**
- **Demo Persistence**: User accounts and chat history survive restarts and deployments
- **Container-Ready**: Database persistence works seamlessly in containerized environments
- **Analytics Ready**: SQL-based user behavior analysis for team insights
- **Backup & Recovery**: Database file backup and restoration capabilities

## Phase 7: Additional Model Providers
**Planned Tasks:**
- Implement Anthropic adapter for Claude models
- Create Google adapter for Gemini models  
- Enhance model registry with provider-specific configurations
- Add model capability detection (streaming, multi-modal, etc.)

**Key Components:**
- `AnthropicAdapter` class for Claude model integration
- `GoogleAdapter` class for Gemini model support
- Extended model registry with provider-specific parameters
- Multi-modal support for text and image inputs

## Phase 8: Enhanced Data Collection System
**Planned Tasks:**
- Design logging schema for conversation data
- Implement metrics collection (response times, model performance)
- Create data export utilities
- Add privacy and retention controls

**Key Components:**
- Structured logging with JSON format
- Enhanced analytics dashboard endpoints
- Data anonymization utilities
- FERPA compliance and privacy controls

## Configuration Strategy

### Model Configuration
- **OpenAI Adapter**: Support for OpenAI API, local vLLM models, and OpenAI-compatible providers
- **Anthropic Adapter** (planned): Direct Claude model integration
- **Google Adapter** (planned): Gemini model support
- Model-specific parameters (temperature, max_tokens, etc.) mapped per provider

### Deployment Configurations
- **Local Development**: Docker Compose with vLLM server
- **AWS Container**: ECS/EKS deployment with auto-scaling
- **Hybrid**: Local models + API fallbacks

## Data Collection Schema
- Conversation metadata (timestamps, session IDs)
- Message content and responses
- Model performance metrics
- User interaction patterns
- System resource usage

## Development Workflow

### Getting Started with Claude Code
1. Create new repository and navigate to directory
2. Run Claude Code to initialize project structure
3. Use Claude Code to generate core components iteratively
4. Test each phase before moving to the next

### Suggested Claude Code Sessions
1. **"Set up a Python project for a chatbot demo with FastAPI and vLLM dependencies"**
2. **"Create a model manager class that can switch between local vLLM models and API calls"**
3. **"Build FastAPI endpoints for a simple chat interface with session management"**
4. **"Add data collection and logging for conversation analytics"**
5. **"Create Docker and Kubernetes configs for AWS deployment"**

## Success Criteria
- [ ] Can swap between different models without code changes
- [ ] Handles both local vLLM and API-based models
- [ ] Collects comprehensive usage data
- [ ] Deploys successfully in both local and cloud environments
- [ ] Provides simple but functional chat interface
- [ ] Includes proper error handling and monitoring

## Next Steps
1. Initialize repository structure using Claude Code
2. Begin with Phase 1 implementation
3. Iterate through phases, testing each component
4. Deploy and validate in target environments
5. Begin data collection for analysis

## Notes for Claude Code Usage
- Focus on generating cohesive, production-ready code
- Ensure proper error handling and logging throughout
- Generate comprehensive tests for each component
- Include detailed documentation in code comments
- Consider security best practices for API key management