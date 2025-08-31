# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a chatbot wrapper demo designed to provide a unified interface for multiple AI model providers through adapter-based architecture. The project supports local vLLM models, OpenAI API, and other OpenAI-compatible providers, with planned support for Anthropic and Google models. It's intended for data collection on chatbot usage patterns and can be deployed locally or in containers on a kubernetes cluster.

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

**Next Phase: Phase 4 - Additional Model Providers (Future)**
Ready to implement Anthropic and Google model adapters when needed.

## Planned Architecture

The project will follow this structure:
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

## Development Commands

### Python Environment (Choose one option)

**Option 1: Using uv (recommended - faster)**
- `uv venv` - Create virtual environment
- `source .venv/bin/activate` - Activate environment  
- `uv pip install -r requirements.txt` - Install dependencies

**Option 2: Using traditional pip**
- `python -m venv venv && source venv/bin/activate` - Create and activate virtual environment
- `pip install -r requirements.txt` - Install dependencies
- `pip install -e .` - Install project in development mode

### Running the Application (Once implemented)
- `python -m src.main` - Start the chatbot service
- `uvicorn src.api.main:app --reload` - Start FastAPI server with hot reload

### Testing (Once implemented)
- `pytest` - Run all tests
- `pytest tests/unit/` - Run unit tests only
- `pytest tests/integration/` - Run integration tests only

### Code Quality
- `black .` - Format code
- `isort .` - Sort imports  
- `flake8 .` - Lint code
- `mypy src/` - Type checking

### Docker (Once implemented)
- `docker-compose up` - Start local development environment
- `docker build -t chatbot-demo .` - Build application container

## Key Implementation Considerations

### Model Adapter Architecture
- **OpenAI Adapter**: Unified interface supporting OpenAI API, local vLLM models, and OpenAI-compatible providers
- **Anthropic Adapter** (planned): Direct integration with Claude models via Anthropic API
- **Google Adapter** (planned): Integration with Gemini models via Google AI API
- **Model Registry**: Dynamic model configuration and provider switching
- **Fallback Mechanisms**: Automatic failover between model providers for reliability

### Data Collection
- Structure logging for conversation analytics
- Implement proper data retention and privacy controls
- Use structured JSON logging format for analysis

### Deployment
- Support both local development and cloud deployment
- Use environment-specific configurations
- Include proper health checks and monitoring

## Configuration Strategy

The application supports multiple model providers through adapters:
- **OpenAI Adapter**: OpenAI API, local vLLM models, and OpenAI-compatible endpoints
- **Anthropic Adapter** (planned): Claude models via Anthropic API
- **Google Adapter** (planned): Gemini models via Google AI API
- Environment-specific deployment configurations with provider-specific settings

## Security Considerations

- Never commit API keys or sensitive configuration
- Use environment variables for secrets management
- Implement proper authentication for data collection endpoints
- Sanitize and anonymize collected data appropriately

## Next Steps (Phase 4+ Implementation)

1. **Additional Model Providers** (Optional Enhancement):
   - **Anthropic Adapter** (`src/models/adapters/anthropic_adapter.py`): Claude model integration
   - **Google Adapter** (`src/models/adapters/google_adapter.py`): Gemini model support
   - **Enhanced Model Registry**: Provider-specific configurations and capability detection

2. **Data Collection System** (Phase 5):
   - Conversation logging and analytics
   - Database integration for data persistence
   - Export utilities and data analysis tools
   - Privacy controls and data retention policies

3. **Web Interface** (Optional):
   - Simple chat interface using FastAPI static files or separate frontend
   - WebSocket support for real-time streaming
   - Session management and conversation history

4. **Deployment & Production** (Phase 6):
   - Docker containers and docker-compose setup
   - Kubernetes manifests for cloud deployment
   - CI/CD pipeline and automated testing
   - Monitoring and observability setup

## Current Implementation Status

### Completed Components
- ✅ **OpenAI Adapter** (`src/models/openai_adapter.py`): Supports OpenAI API, vLLM, and compatible providers
- ✅ **Model Configuration** (`src/config/models.py`): Centralized model registry with Pydantic validation
- ✅ **Adapter Factory** (`src/models/adapter_factory.py`): Runtime adapter management and health checks
- ✅ **Settings Management** (`src/config/settings.py`): Environment-based configuration
- ✅ **FastAPI Application** (`src/api/main.py`): Complete web server with middleware and error handling
- ✅ **API Routes** (`src/api/routes/`): Chat completions, health checks, and model listing
- ✅ **API Models** (`src/api/models.py`): OpenAI-compatible request/response models
- ✅ **Base Interfaces** (`src/models/base.py`): Abstract adapter interface and common models
- ✅ **Testing Infrastructure** (`test_api.py`, `run_server.py`): Development and testing tools
- ✅ **Installation Setup** (`requirements-api-only.txt`): Lightweight dependency management

### Architecture Decisions Made
- **Adapter Pattern**: Each model provider has its own adapter implementing a common interface
- **OpenAI Compatibility**: Local vLLM models use OpenAI-compatible endpoints for consistency
- **Unified Response Format**: All adapters return standardized chat completion responses
- **Environment-Based Configuration**: Model selection and API keys managed via environment variables
- **Centralized Configuration**: Single source of truth for model configs in `src/config/models.py`
- **Factory Pattern**: Runtime adapter creation and management through adapter factory
- **Structured Logging**: JSON-formatted logs with structured data for monitoring and debugging

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