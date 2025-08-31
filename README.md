# Chatbot Wrapper Demo

A chatbot demo with adapter-based architecture that provides a unified interface for multiple AI model providers. Currently supports OpenAI API, local vLLM models, and OpenAI-compatible providers, with planned support for Anthropic and Google models. Designed for data collection on chatbot usage patterns and can be deployed locally or in containers on Kubernetes clusters.

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
   uvicorn src.api.main:app --reload
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

The application uses an adapter-based architecture where each model provider has its own adapter. See `.env.example` for configuration options including API keys and model selection.

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

## Phase 3: Additional Model Providers (Next Phase)
**Upcoming Tasks:**
- Implement Anthropic adapter for Claude models
- Create Google adapter for Gemini models  
- Enhance model registry with provider-specific configurations
- Add model capability detection (streaming, multi-modal, etc.)

**Key Components:**
- `AnthropicAdapter` class for Claude model integration
- `GoogleAdapter` class for Gemini model support
- Extended model registry with provider-specific parameters
- Multi-modal support for text and image inputs

## Phase 4: API Endpoints & Chat Interface
**Planned Tasks:**
- Generate FastAPI application structure
- Create REST endpoints for chat interactions
- Build simple web frontend (HTML/CSS/JS)
- Implement session management

**Key Components:**
- FastAPI server with chat endpoints
- Basic web UI for chat interface
- Session persistence and conversation history
- WebSocket support for real-time chat (optional)

## Phase 5: Data Collection System
**Planned Tasks:**
- Design logging schema for conversation data
- Implement metrics collection (response times, model performance)
- Create data export utilities
- Add privacy and retention controls

**Key Components:**
- Structured logging with JSON format
- Database integration (SQLite for local, PostgreSQL for production)
- Analytics dashboard endpoints
- Data anonymization utilities

## Phase 6: Containerization & Deployment
**Planned Tasks:**
- Generate Dockerfile for the application
- Create docker-compose for local development
- Build Kubernetes manifests for AWS deployment
- Create deployment scripts and health checks

**Key Components:**
- Multi-stage Docker builds
- Environment-specific configurations
- Kubernetes deployments, services, and ingress
- Monitoring and logging integration

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