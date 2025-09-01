# Architecture Documentation

This document captures the technical design decisions, system architecture, and implementation strategies for the chatbot wrapper API project.

## System Overview

The chatbot wrapper API is designed as a unified interface for multiple AI model providers using an adapter-based architecture. The system supports OpenAI API, local vLLM models, OpenAI-compatible providers, with planned support for Anthropic and Google models.

## Core Architecture Decisions

### Adapter Pattern Implementation
- **Design Choice**: Each model provider has its own adapter implementing a common interface
- **Rationale**: Provides consistent API regardless of underlying provider, enables easy addition of new providers
- **Implementation**: Abstract base class `BaseAdapter` with provider-specific implementations
- **Benefits**: Provider independence, unified response format, easy testing and mocking

### OpenAI Compatibility Strategy
- **Design Choice**: Local vLLM models use OpenAI-compatible endpoints for consistency
- **Rationale**: Minimizes code differences between local and remote providers
- **Implementation**: Single `OpenAIAdapter` handles OpenAI API, vLLM, and compatible providers
- **Benefits**: Reduced complexity, consistent request/response handling, easier migration

### Factory Pattern for Adapter Management
- **Design Choice**: Runtime adapter creation and management through adapter factory
- **Rationale**: Centralized adapter lifecycle management, health monitoring, configuration loading
- **Implementation**: `AdapterFactory` class with provider registration and health checks
- **Benefits**: Dynamic model switching, centralized error handling, consistent initialization

### Configuration Architecture
- **Design Choice**: Environment-based configuration with centralized model registry
- **Rationale**: Single source of truth for model configs, environment-specific deployments
- **Implementation**: Pydantic models in `src/config/models.py` with environment variable overrides
- **Benefits**: Type safety, validation, easy deployment configuration management

## Authentication Strategy

### Auth0-Based Universal SSO Architecture

#### Long-term Vision
- **Standards-Based Approach**: OAuth2/OIDC with JWT tokens for vendor independence
- **Universal Compatibility**: Support for educational institutions' existing SSO systems
- **Migration Path**: Standard protocols enable easy provider switching

#### Current Simplified Implementation
For the initial 6-month pilot with <5 partner institutions:

**Institution Registry Pattern**:
- Manually curated list of partner institutions with metadata
- Auto-detection based on email domains
- Institution-specific configuration (branding, auth providers, SAML/OIDC settings)

**Institution Configuration Structure**:
```python
# Example from src/auth/auth0_client.py
InstitutionConfig(
    institution_id="example",               # Unique identifier for database
    name="Example University",              # Display name for UI
    domain="example.edu",                   # Email domain for auto-detection
    auth_provider=AuthProvider.GOOGLE,      # Preferred SSO provider (Google/Microsoft/SAML)
    saml_config={...},                     # SAML configuration if applicable
    oidc_config={...},                     # OIDC configuration if applicable  
    logo_url="https://example.edu/logo",   # Institution branding for UI
    primary_color="#003366",               # Institution brand color
    enabled=True                           # Whether institution is currently active
)
```

**Authentication Flow Design**:
1. User initiates login via Auth0 (Google, Microsoft, GitHub, SAML)
2. System extracts email domain and checks institution registry
3. If institutional email detected: suggest institution and default role
4. If not detected or individual: user selects "Individual" + role  
5. Store institution_id and role in user database
6. Include institution/role in JWT claims for authorization

**Supported Authentication Methods**:
- **Google Workspace**: Most common for educational institutions
- **Microsoft Azure AD/Office 365**: Enterprise and education accounts  
- **SAML**: Custom enterprise SSO systems used by schools
- **GitHub**: Individual developer accounts
- **Individual**: Non-institutional users with manual role selection

### Benefits of Simplified Approach
- **Low Maintenance**: Manual registry manageable for small number of institutions
- **User Friendly**: Clear role selection, works for both institutional and individual users
- **Scalable**: Easy to add SAML attributes or Auth0 custom claims later
- **Standards-Based**: Uses OAuth2/OIDC, preserves migration path to full implementation

## Model Adapter Architecture

### Current Implementation: OpenAI Adapter
- **Unified Interface**: Single adapter supporting OpenAI API, local vLLM, and compatible providers
- **Provider Detection**: Automatic detection of local vs. remote endpoints
- **Response Standardization**: Consistent chat completion format across all providers
- **Error Handling**: Provider-specific error mapping to standard format

### Planned Extensions
- **Anthropic Adapter**: Direct Claude model integration via Anthropic API
- **Google Adapter**: Gemini model support via Google AI API
- **Enhanced Model Registry**: Provider-specific configurations and capability detection
- **Fallback Mechanisms**: Automatic failover between providers for reliability

## Data Architecture Decisions

### Logging Strategy
- **Design Choice**: Structured JSON logging format
- **Rationale**: Machine-readable logs for monitoring, debugging, and analytics
- **Implementation**: FastAPI middleware with structured log formats
- **Benefits**: Searchable logs, integration with log aggregation systems, performance monitoring

### Session Management
- **Current**: In-memory storage for pilot phase simplicity
- **Planned**: SQLite database for persistence and analytics
- **Design Choice**: User profiles, sessions, chat history, and analytics in relational format
- **Benefits**: Query capabilities for analytics, backup and recovery, FERPA compliance support

## Deployment Architecture

### Container Strategy
- **Design Choice**: Docker containerization with multi-stage builds
- **Rationale**: Consistent deployment across environments, dependency isolation
- **Implementation**: Optimized containers with dependency caching, security hardening
- **Benefits**: Environment consistency, scalability, cloud-ready deployment

### Health Check Architecture
- **Design Choice**: Multiple health check endpoints for different orchestration needs
- **Implementation**: `/health/live` (liveness), `/health/ready` (readiness), `/health/` (comprehensive)
- **Rationale**: Kubernetes-compatible health probes, detailed service monitoring
- **Benefits**: Proper container orchestration, service mesh compatibility, monitoring integration

### Environment Configuration Pattern
- **Design Choice**: Environment variable-based configuration with validation
- **Implementation**: Pydantic Settings classes with environment overrides
- **Rationale**: 12-factor app compliance, secure secrets management
- **Benefits**: Cloud-native deployment, easy configuration management, type safety

## Security Architecture

### API Key Management
- **Design Choice**: Environment variable-based secrets with runtime validation
- **Implementation**: No secrets in code, environment-specific configuration
- **Security Controls**: Never commit keys, sanitize logs, validate at startup

### Authentication Security
- **JWT Token Strategy**: Standard JWT with configurable expiration
- **Token Validation**: Middleware-based token verification with user context injection
- **Authorization**: Role-based endpoint protection with configurable requirements

### Data Privacy
- **Design Choice**: Structured logging with data sanitization capabilities
- **Implementation**: Configurable data retention policies, anonymization utilities
- **Compliance**: FERPA compliance support for educational use cases

## Extensibility Design

### Provider Addition Pattern
1. Implement `BaseAdapter` interface
2. Register in `AdapterFactory` 
3. Add configuration to model registry
4. Update settings for provider-specific options

### Model Registry Extension
- **Configuration Schema**: Pydantic models for type safety and validation
- **Provider-Specific Parameters**: Temperature, max_tokens, streaming support per provider
- **Capability Detection**: Model feature detection and advertisement

### API Versioning Strategy
- **Current**: OpenAI-compatible v1 API endpoints
- **Future**: Version prefix pattern for API evolution
- **Backward Compatibility**: Maintain v1 compatibility while adding new versions

## Performance Considerations

### Async Architecture
- **Design Choice**: FastAPI with async/await for I/O operations
- **Benefits**: High concurrency, efficient resource utilization, non-blocking operations

### Caching Strategy
- **Model Registry**: In-memory caching of model configurations
- **Token Validation**: Efficient JWT validation with cached secrets
- **Health Checks**: Cached adapter health status with TTL

### Resource Management
- **Connection Pooling**: HTTP client reuse for external API calls
- **Memory Management**: Streaming response handling for large completions
- **Error Recovery**: Circuit breaker patterns for external service resilience

## Integration Architecture

### Frontend Separation
- **Design Choice**: Backend API service with separate frontend in `../chatbot-frontend`
- **Benefits**: Technology independence, scalability, deployment flexibility
- **API Design**: RESTful endpoints with OpenAI compatibility for easy integration

### Infrastructure Integration
- **Cloud Infrastructure**: Integration points with `../augmented-infra` 
- **Container Orchestration**: Kubernetes-ready with proper health checks and service discovery
- **CI/CD Integration**: Automated testing, building, and deployment workflows

## Future Architecture Considerations

### Database Migration Path
- **Phase 6**: SQLite for persistence and analytics
- **Benefits**: Query capabilities, backup/recovery, compliance support
- **Migration Strategy**: Backward-compatible data models, migration scripts

### Multi-Modal Support
- **Architecture**: Extensible message format for text, image, and other content types
- **Provider Support**: Adapter interface extensions for multi-modal capabilities
- **API Evolution**: Maintain OpenAI compatibility while adding new content types

### Analytics Architecture
- **Data Collection**: Conversation metadata, performance metrics, user patterns
- **Privacy Controls**: Configurable data retention, anonymization, FERPA compliance
- **Export Capabilities**: SQL-based analytics queries, data export utilities