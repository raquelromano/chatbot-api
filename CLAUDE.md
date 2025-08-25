# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a chatbot wrapper demo designed to integrate with vLLM, allowing easy switching between open-source models and API endpoints. The project is intended for data collection on chatbot usage patterns and can be deployed locally or in containers on a kubernetes cluster.

## Current Status

**Phase 1 - Project Foundation: ✅ COMPLETED**
- ✅ Directory structure created with all planned modules
- ✅ Python package structure with `__init__.py` files
- ✅ Requirements.txt with FastAPI, vLLM, and essential dependencies
- ✅ pyproject.toml with project metadata and development tools
- ✅ Environment configuration (.env.example, .gitignore)
- ✅ Updated README.md with setup instructions (including uv support)

**Next Phase: Phase 2 - vLLM Wrapper Service**
Ready to implement core model management and API abstraction layer.

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

### Model Management
- The `ModelManager` class should handle lifecycle of both local vLLM models and API clients
- Configuration should support easy switching between different model backends
- Implement fallback mechanisms for API failures

### Data Collection
- Structure logging for conversation analytics
- Implement proper data retention and privacy controls
- Use structured JSON logging format for analysis

### Deployment
- Support both local development and cloud deployment
- Use environment-specific configurations
- Include proper health checks and monitoring

## Configuration Strategy

The application should support:
- Local vLLM models (Llama, Mistral, etc.)
- External API integration (OpenAI, Anthropic, others)
- Environment-specific deployment configurations

## Security Considerations

- Never commit API keys or sensitive configuration
- Use environment variables for secrets management
- Implement proper authentication for data collection endpoints
- Sanitize and anonymize collected data appropriately

## Next Steps (Phase 2 Implementation)

1. **Create configuration system** (`src/config/`):
   - Settings class with Pydantic for environment variables
   - Model configuration management
   - API client configuration

2. **Implement model management** (`src/models/`):
   - `ModelManager` class for model lifecycle
   - `BaseModel` abstract class for model interfaces
   - `VLLMModel` and `APIModel` concrete implementations

3. **Build API abstraction** (`src/utils/`):
   - HTTP client utilities for external APIs
   - Request/response standardization
   - Error handling and retry mechanisms

Ready to begin Phase 2 implementation with the foundation in place.