# Architecture Documentation

This document captures the technical design decisions, system architecture, and implementation strategies for the chatbot wrapper API project.

## System Overview

The chatbot API is designed as a serverless unified interface for multiple AI model providers using an adapter-based architecture. The system supports OpenAI API, local vLLM models, OpenAI-compatible providers, with planned support for Anthropic and Google models. The application deploys as a serverless architecture on AWS Lambda with Cognito authentication and global edge caching.

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

### AWS Cognito Universal SSO Architecture

#### Production Implementation
- **Standards-Based Approach**: OAuth2/OIDC with JWT tokens via AWS Cognito User Pools
- **Serverless Native**: Integrated with API Gateway JWT authorizer for automatic validation
- **Multi-Provider Support**: Support for educational institutions' existing SSO systems
- **Enterprise Ready**: AWS-managed security, scalability, and compliance features

#### Current Cognito Implementation
Production deployment with AWS Cognito User Pools for educational pilot:

**Institution Registry Pattern**:
- Manually curated list of partner institutions with metadata
- Auto-detection based on email domains
- Institution-specific configuration (branding, auth providers, SAML/OIDC settings)

**Institution Configuration Structure**:
```python
# Example from src/auth/cognito_client.py
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
1. User accesses Cognito Hosted UI (Google, Microsoft, GitHub, SAML providers)
2. API Gateway validates Cognito JWT token automatically
3. System extracts email domain and checks institution registry
4. If institutional email detected: suggest institution and default role
5. If not detected or individual: user selects "Individual" + role
6. Store institution_id and role in user profile
7. Include institution/role in JWT claims for authorization

**Supported Authentication Methods**:
- **Google Workspace**: OAuth integration via Cognito identity providers
- **Microsoft Azure AD/Office 365**: SAML/OIDC integration via Cognito
- **SAML**: Custom enterprise SSO systems via Cognito SAML provider
- **GitHub**: OAuth integration via Cognito social providers
- **Individual**: Username/password with Cognito User Pool

**Auth0 Fallback Support**:
- Legacy Auth0 client maintained for local development
- Dual authentication provider support in middleware
- Seamless migration path between providers

### Benefits of Cognito Architecture
- **AWS Native**: Integrated with Lambda, API Gateway, and other AWS services
- **Serverless Scaling**: Automatic scaling and management by AWS
- **Enterprise Security**: SOC2, HIPAA, and GDPR compliant authentication
- **Cost Effective**: Pay-per-user pricing model suitable for educational pilot
- **Standards-Based**: OAuth2/OIDC compatible with existing SSO systems

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
- **Planned**: DynamoDB database for serverless persistence and analytics
- **Design Choice**: User profiles, sessions, chat history in NoSQL format optimized for serverless
- **Benefits**: Serverless-native persistence, automatic scaling, cost-effective storage, FERPA compliance support

## Deployment Architecture

### AWS Serverless Strategy (Production)
- **Design Choice**: AWS Lambda + API Gateway + Cognito + CloudFront serverless architecture with dev/prod environment separation
- **Rationale**: Cost-effective for educational use cases, auto-scaling, no server management, isolated environments
- **Implementation**: FastAPI with Mangum wrapper, CDK infrastructure as code, Cognito User Pools, environment-specific resource naming
- **Benefits**: Pay-per-request pricing (~$2-6/month), automatic scaling, global distribution, safe deployment practices

### Complete Infrastructure Stack
- **AWS Lambda**: FastAPI application with Mangum ASGI adapter (environment-specific function names)
- **API Gateway**: HTTP API with Cognito JWT authorizer for authentication (environment-specific APIs)
- **Cognito User Pools**: OAuth authentication with multiple identity providers (separate pools per environment)
- **CloudFront**: Global CDN for edge caching and performance optimization
- **S3**: Static asset storage with CloudFront integration (environment-specific buckets)
- **Parameter Store**: Encrypted secrets and configuration management (environment-specific paths: `/chatbot-api/{env}/`)
- **CloudWatch**: Monitoring, logging, and alerting

### API Gateway Integration
- **Design Choice**: HTTP API with Cognito User Pool authorizer
- **Implementation**: CORS configuration, automatic JWT validation, rate limiting support
- **Rationale**: Lower cost than REST API, built-in Cognito authentication, serverless-native
- **Benefits**: Integrated auth, automatic scaling, cost optimization, global distribution

### Health Check Architecture
- **Design Choice**: Lambda-compatible health endpoints with API Gateway integration
- **Implementation**: `/health/live`, `/health/ready`, `/health/` with Lambda warmup handling
- **Rationale**: Serverless-compatible monitoring, CloudWatch integration
- **Benefits**: Native AWS monitoring, cost-effective health checks, auto-scaling compatibility

### Secrets Management Architecture
- **Design Choice**: AWS Systems Manager Parameter Store for encrypted configuration with environment separation
- **Implementation**: Lambda function loads parameters at startup with IAM permissions, environment-specific parameter paths
- **Rationale**: Serverless-native secrets management, encrypted storage, cost-effective, environment isolation
- **Benefits**: AWS-native security, automatic encryption, centralized configuration, dev/prod separation

### CI/CD Pipeline Architecture
- **Design Choice**: GitHub Actions with AWS CDK deployment supporting multiple environments
- **Implementation**: Automated testing, code quality checks, CDK synthesis and deployment with environment parameters
- **Rationale**: Version-controlled infrastructure, automated validation, consistent deployments, environment-specific pipelines
- **Benefits**: Infrastructure as code, automated quality gates, rollback capabilities, safe promotion workflows

## Security Architecture

### API Key Management
- **Design Choice**: AWS Parameter Store encrypted secrets with runtime loading
- **Implementation**: No secrets in code, encrypted storage, IAM-controlled access
- **Security Controls**: Never commit keys, sanitize logs, encrypted at rest and in transit

### Authentication Security
- **Cognito JWT Strategy**: AWS Cognito User Pool JWT tokens with automatic API Gateway validation
- **Token Validation**: API Gateway built-in Cognito authorizer with Lambda context injection
- **Authorization**: Role-based access control via JWT claims and middleware validation
- **Multi-Provider Support**: Cognito primary with Auth0 fallback for development

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
- **Design Choice**: Backend API service with separate React frontend
- **Benefits**: Technology independence, scalability, deployment flexibility
- **API Design**: RESTful endpoints with OpenAI compatibility for easy integration
- **Deployment**: React app on S3 + CloudFront, API on Lambda + API Gateway + CloudFront

### AWS Serverless Integration (Production)
- **Cloud Infrastructure**: Native AWS services (Lambda, API Gateway, Cognito, S3, CloudFront, Parameter Store)
- **Service Orchestration**: API Gateway routing, Lambda auto-scaling, CloudWatch monitoring
- **Global Distribution**: CloudFront edge locations for worldwide performance
- **CI/CD Integration**: GitHub Actions with AWS CDK for infrastructure as code deployment

## Future Architecture Considerations

### Database Migration Path
- **Phase 6**: DynamoDB for serverless persistence and analytics
- **Benefits**: Serverless-native scaling, cost-effective storage, backup/recovery, compliance support
- **Migration Strategy**: Backward-compatible data models, DynamoDB table creation scripts

### Multi-Modal Support
- **Architecture**: Extensible message format for text, image, and other content types
- **Provider Support**: Adapter interface extensions for multi-modal capabilities
- **API Evolution**: Maintain OpenAI compatibility while adding new content types

### Analytics Architecture
- **Data Collection**: Conversation metadata, performance metrics, user patterns
- **Privacy Controls**: Configurable data retention, anonymization, FERPA compliance
- **Export Capabilities**: SQL-based analytics queries, data export utilities