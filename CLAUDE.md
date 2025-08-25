# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a chatbot wrapper demo designed to integrate with vLLM, allowing easy switching between open-source models and API endpoints. The project is intended for data collection on chatbot usage patterns and can be deployed locally or in containers on a kubernetes cluster.

## Current Status

This repository is in the planning phase. The project structure and implementation are yet to be created based on the development plan outlined below.

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

Once implemented, the project will likely use these commands:

### Python Environment
- `python -m venv venv && source venv/bin/activate` - Create and activate virtual environment
- `pip install -r requirements.txt` - Install dependencies
- `pip install -e .` - Install project in development mode

### Running the Application
- `python -m src.main` - Start the chatbot service
- `uvicorn src.api.main:app --reload` - Start FastAPI server with hot reload

### Testing
- `pytest` - Run all tests
- `pytest tests/unit/` - Run unit tests only
- `pytest tests/integration/` - Run integration tests only

### Docker
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