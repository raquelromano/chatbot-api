# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Docker containerization and deployment (Phase 5)
- SQLite database integration for persistent storage (Phase 6)
- Anthropic adapter for Claude models (Phase 7)
- Google adapter for Gemini models (Phase 7)
- Enhanced data collection and analytics system (Phase 8)

## [0.4.0] - 2024-12-XX

### Added
- **Authentication System (Phase 4)**
  - Auth0 integration with OAuth2/OIDC flows
  - Institution registry for educational SSO pilot
  - JWT middleware for token validation and user context
  - User onboarding flow with role selection
  - Authentication API endpoints (login, callback, onboarding, profile, logout)
  - In-memory user and session management
  - Support for Google, Microsoft, SAML, GitHub, and individual accounts
  - Institution auto-detection from email domains

### Changed
- FastAPI application now includes authentication middleware
- API endpoints can be configured to require authentication
- Enhanced settings management with Auth0 configuration

### Security
- JWT token-based authentication with configurable expiration
- Secure token validation and user context injection
- Environment variable-based secrets management for Auth0

## [0.3.0] - 2024-11-XX

### Added
- **API Endpoints & Chat Interface (Phase 3)**
  - FastAPI application with complete web server
  - OpenAI-compatible REST API endpoints
  - Chat completion endpoints (streaming and non-streaming)
  - Model listing endpoint (`/v1/models`)
  - Health check endpoints (`/health/`, `/health/live`, `/health/ready`)
  - Request/response models with Pydantic validation
  - Error handling and logging middleware
  - Interactive API documentation at `/docs`
  - Testing infrastructure (`test_api.py`, `run_server.py`)

### Changed
- Integrated adapter factory with FastAPI application
- Enhanced error handling with structured responses
- Added comprehensive logging for monitoring and debugging

### Developer Experience
- Simple server startup with `python run_server.py`
- Comprehensive API testing with `test_api.py`
- Kubernetes-ready health probes for container orchestration

## [0.2.0] - 2024-11-XX

### Added
- **Core Model Adapters (Phase 2)**
  - OpenAI adapter supporting multiple backends (OpenAI API, vLLM, compatible providers)
  - Model registry system for dynamic configuration
  - Unified chat completion interface across providers
  - Adapter factory for runtime provider management
  - Settings management with Pydantic and environment variables
  - Health checking for model adapters

### Changed
- Centralized configuration in `src/config/models.py`
- Environment-based model selection and API key management
- Standardized chat completion response format across all adapters

### Technical
- Abstract base adapter interface for consistent provider implementation
- Factory pattern for adapter creation and lifecycle management
- Provider-agnostic error handling and response normalization

## [0.1.0] - 2024-10-XX

### Added
- **Project Foundation (Phase 1)**
  - Python project structure with proper package organization
  - Virtual environment and dependency management setup
  - Base configuration system for model switching
  - Requirements files (`requirements.txt`, `requirements-api-only.txt`)
  - Project metadata and development tools (`pyproject.toml`)
  - Environment configuration (`.env.example`, `.gitignore`)
  - Documentation structure (README.md, development guidelines)

### Infrastructure
- FastAPI and vLLM dependencies for web API and local model support
- Development tools for code quality (black, isort, flake8, mypy)
- Project scaffolding for planned modules (config, models, api, auth, utils)

### Documentation
- Comprehensive setup instructions supporting both `uv` and `pip`
- Development workflow and command reference
- Configuration strategy for multi-provider architecture

---

## Phase Completion History

### Phase 4: Authentication System ✅ (December 2024)
**Objective**: Multi-provider educational SSO with Auth0 integration
**Key Achievements**:
- Simplified pilot approach for <5 partner institutions
- Universal SSO compatibility with vendor lock-in avoidance
- Institution registry with auto-detection and role selection
- Standards-based OAuth2/OIDC implementation with JWT tokens

### Phase 3: API Endpoints & Chat Interface ✅ (November 2024) 
**Objective**: RESTful API with OpenAI compatibility
**Key Achievements**:
- Complete FastAPI web server with middleware
- OpenAI-compatible endpoints for easy integration
- Health monitoring for container orchestration
- Comprehensive testing and development tools

### Phase 2: Core Model Adapters ✅ (November 2024)
**Objective**: Unified interface for multiple AI model providers  
**Key Achievements**:
- Single adapter supporting OpenAI API, vLLM, and compatible providers
- Dynamic model configuration and provider switching
- Standardized response format across all backends
- Robust error handling and provider abstraction

### Phase 1: Project Foundation ✅ (October 2024)
**Objective**: Production-ready Python project structure
**Key Achievements**:
- Clean project architecture with proper packaging
- Comprehensive dependency management and tooling
- Environment-based configuration system
- Developer-friendly setup and documentation

---

## Breaking Changes

### Version 0.4.0
- **Authentication Required**: When `ENABLE_AUTH=true`, protected endpoints now require JWT authentication
- **Environment Variables**: New Auth0 configuration variables required for authentication
- **API Changes**: Authentication endpoints added to API surface

### Version 0.3.0
- **Endpoint Structure**: Moved from custom endpoints to OpenAI-compatible `/v1/*` structure
- **Health Checks**: Health endpoint paths changed for Kubernetes compatibility
- **Configuration**: Model configuration moved to centralized registry system

### Version 0.2.0
- **Provider Interface**: Custom model provider implementations now require `BaseAdapter` interface
- **Configuration Format**: Model configurations now use Pydantic models instead of plain dictionaries
- **Import Paths**: Model adapter imports moved to `src.models.adapters` package structure

---

## Migration Notes

### Upgrading to 0.4.0
1. **Environment Setup**: Add Auth0 configuration variables if enabling authentication
2. **API Integration**: Update client code to handle JWT tokens for protected endpoints
3. **Institution Registry**: Configure institution settings in `src/auth/auth0_client.py`

### Upgrading to 0.3.0
1. **Endpoint URLs**: Update API client URLs from custom paths to `/v1/chat/completions`
2. **Health Checks**: Update monitoring to use new health check endpoints
3. **Server Startup**: Use `python run_server.py` instead of direct uvicorn commands

### Upgrading to 0.2.0
1. **Model Configuration**: Update model configs to use new Pydantic-based registry
2. **Provider Implementation**: Implement `BaseAdapter` interface for custom providers
3. **Environment Variables**: Update model selection environment variables

---

## Development Milestones

- **October 2024**: Project foundation and initial structure
- **November 2024**: Core adapters and API implementation  
- **December 2024**: Authentication system completion
- **Q1 2025**: Planned containerization and deployment (Phase 5)
- **Q2 2025**: Planned database integration and additional providers (Phases 6-7)
- **Q3 2025**: Planned enhanced analytics and data collection (Phase 8)