# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chatbot wrapper API with adapter-based architecture supporting multiple AI model providers. Currently supports OpenAI API, local vLLM models, and OpenAI-compatible providers.

**Note**: Backend API service. Frontend: `../chatbot-frontend`. Infrastructure: `../augmented-infra`.

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


## Development Commands

### Key Commands for Claude
- `python run_server.py` - Start the chatbot service
- `python test_api.py` - Test API endpoints
- `uv pip install -r requirements-api-only.txt` - Install dependencies
- `black . && isort . && flake8 . && mypy src/` - Code quality checks

## Implementation Guidelines

### Code Conventions
- Follow existing adapter pattern when adding new providers
- Use Pydantic models for configuration and validation
- Implement structured logging with JSON format
- Never commit API keys or sensitive configuration
- Use environment variables for secrets management

## Authentication Implementation

**Current Status**: Auth0-based SSO with institution registry for educational pilot

**Key Components**:
- **Auth Models** (`src/auth/models.py`): User, session, and institution data structures
- **Auth0 Client** (`src/auth/auth0_client.py`): OAuth flows + institution registry lookup
- **JWT Middleware** (`src/auth/middleware.py`): Token validation and user context
- **Auth Endpoints** (`src/auth/auth.py`): Login, callback, onboarding, profile management
- **User Manager** (`src/auth/user_manager.py`): In-memory user and session management

**Supported Methods**: Google, Microsoft, SAML, GitHub, Individual accounts

## Next Steps (Phase 5+ Implementation)

1. **Containerization & Deployment** (Phase 5 - Next Priority):
   - **Docker Implementation**: Create Dockerfile and docker-compose for containerized deployment
   - **Container Optimization**: Multi-stage builds, dependency caching, security hardening
   - **Environment Configuration**: Container-specific environment variable handling
   - **Health Checks**: Docker and Kubernetes health probe configuration
   - **Cloud Integration**: Integration with infrastructure in `../augmented-infra`
   - **CI/CD Pipeline**: Automated testing, building, and deployment workflows

2. **Database Integration** (Phase 6):
   - **SQLite Implementation**: Replace in-memory user storage with persistent SQLite database
   - **Database Schema**: User profiles, sessions, chat history, and analytics tables
   - **Migration System**: Database versioning and upgrade scripts
   - **Analytics Queries**: SQL queries for user behavior analysis and reporting
   - **Data Export**: Backup and analysis data export capabilities
   - **Container Persistence**: Database file persistence in containerized environments

3. **Additional Model Providers** (Phase 7):
   - **Anthropic Adapter** (`src/models/adapters/anthropic_adapter.py`): Claude model integration
   - **Google Adapter** (`src/models/adapters/google_adapter.py`): Gemini model support
   - **Enhanced Model Registry**: Provider-specific configurations and capability detection

4. **Enhanced Data Collection System** (Phase 8):
   - **Conversation Analytics**: Track usage patterns, model performance, user engagement
   - **Real-time Metrics**: API response times, error rates, user activity dashboards
   - **Data Analysis Tools**: Built-in analytics endpoints for team insights
   - **Privacy Controls**: FERPA compliance, data retention policies, user data deletion

## Current Implementation Status

### Completed Components
- ✅ **OpenAI Adapter** (`src/models/openai_adapter.py`): Supports OpenAI API, vLLM, and compatible providers
- ✅ **Model Configuration** (`src/config/models.py`): Centralized model registry with Pydantic validation
- ✅ **Adapter Factory** (`src/models/adapter_factory.py`): Runtime adapter management and health checks
- ✅ **Settings Management** (`src/config/settings.py`): Environment-based configuration with Auth0 support
- ✅ **FastAPI Application** (`src/api/main.py`): Complete web server with middleware and error handling
- ✅ **API Routes** (`src/api/routes/`): Chat completions, health checks, model listing, and authentication
- ✅ **API Models** (`src/api/models.py`): OpenAI-compatible request/response models
- ✅ **Base Interfaces** (`src/models/base.py`): Abstract adapter interface and common models
- ✅ **Authentication System** (`src/auth/`): Complete Auth0 integration with JWT middleware
  - ✅ **Auth0 Client** (`src/auth/auth0_client.py`): OAuth flows and institution registry
  - ✅ **JWT Middleware** (`src/auth/middleware.py`): Token validation and user context
  - ✅ **Auth Endpoints** (`src/auth/auth.py`): Login, callback, onboarding, profile management
  - ✅ **User Manager** (`src/auth/user_manager.py`): In-memory user and session management
- ✅ **Testing Infrastructure** (`test_api.py`, `run_server.py`): Development and testing tools
- ✅ **Installation Setup** (`requirements-api-only.txt`): Lightweight dependency management


## Current Working State

The application is now **fully functional** for Phase 3 objectives:

### ✅ Ready to Use
- **Installation**: `uv pip install -r requirements-api-only.txt`
- **Startup**: `python run_server.py`
- **Testing**: `python test_api.py`
- **API Docs**: `http://localhost:8000/docs`

### ✅ Working Features
- OpenAI-compatible REST API endpoints
- Health checks and status monitoring
- Model listing and discovery
- Chat completions (streaming and non-streaming)
- Error handling with structured logging
- Kubernetes-ready health probes

### ⚠️ Configuration Required
To use actual models, users need to:
1. **For OpenAI**: Set `OPENAI_API_KEY` environment variable
2. **For local vLLM**: Start vLLM server on `localhost:8001` with OpenAI-compatible API
3. **For other providers**: Configure API endpoints in model registry

### 🔧 Development Tools
- `run_server.py`: Simple server startup with graceful shutdown
- `test_api.py`: Comprehensive API endpoint testing
- `requirements-api-only.txt`: Fast installation without heavy ML dependencies
- Interactive API documentation at `/docs` endpoint