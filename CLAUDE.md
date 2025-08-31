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

**Next Phase: Phase 3 - Additional Model Providers**
Ready to implement Anthropic and Google model adapters.

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

## Next Steps (Phase 3 Implementation)

1. **Implement Anthropic Adapter** (`src/models/adapters/anthropic_adapter.py`):
   - Direct integration with Anthropic API
   - Claude model support with proper message formatting
   - Streaming and non-streaming completion support

2. **Implement Google Adapter** (`src/models/adapters/google_adapter.py`):
   - Integration with Google AI API (Gemini models)
   - Proper content formatting for Google's API structure
   - Multi-modal support for text and image inputs

3. **Enhance Model Registry**:
   - Add Anthropic and Google model configurations
   - Implement provider-specific parameter mapping
   - Add model capability detection (streaming, multi-modal, etc.)

4. **Build API Endpoints** (`src/api/`):
   - FastAPI endpoints for chat completions
   - Provider selection and model switching
   - Request logging and analytics collection

## Current Implementation Status

### Completed Components
- ✅ **OpenAI Adapter** (`src/models/adapters/openai_adapter.py`)
- ✅ **Model Registry** (`src/models/registry.py`)
- ✅ **Settings Management** (`src/config/settings.py`)
- ✅ **Environment Configuration** (`.env.example`)

### Architecture Decisions Made
- **Adapter Pattern**: Each model provider has its own adapter implementing a common interface
- **OpenAI Compatibility**: Local vLLM models use OpenAI-compatible endpoints for consistency
- **Unified Response Format**: All adapters return standardized chat completion responses
- **Environment-Based Configuration**: Model selection and API keys managed via environment variables