# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chatbot wrapper API with adapter-based architecture supporting multiple AI model providers. Currently supports Google Gemini, with placeholders for OpenAI-compatible providers and local vLLM models.

## Guidelines

### Code Conventions
- Follow existing adapter pattern when adding new providers
- Use Pydantic models for configuration and validation
- Implement structured logging with JSON format
- Never commit API keys or sensitive configuration
- Use environment variables for secrets management
- Check current date with `date +"%Y"` before web searches for latest documentation

### Documentation Guidelines
- Never write information about the repository into .md files without first verifying it exists
- Always check the actual codebase structure before documenting features, tests, or commands
- Use Glob, Grep, or Read tools to verify files and directories exist before referencing them
- Ignore paths that contain cdk.out, .venv* to exclude those directories when doing local searches
- Also exclude the ./backup/ directory in the project root

## Architecture

### Model Providers
- **Google Gemini** (ENABLED): 2.5 Pro (2M context) and 2.5 Flash (1M context) via `GOOGLE_API_KEY`
- **OpenAI API** (DISABLED): GPT models, can be re-enabled in `src/config/models.py`
- **Local vLLM** (DISABLED): Llama, Mistral via OpenAI-compatible server
- **Anthropic** (PARTIAL): Model configs exist, adapter implementation needed

### Authentication
**Current**: AWS Cognito User Pools with passwordless email verification codes
- **Endpoints**: `POST /auth/passwordless/login`, `POST /auth/passwordless/verify`
- **Components**: Auth models, Cognito client, JWT middleware, user manager
- **Files**: `src/auth/models.py`, `src/auth/cognito_client.py`, `src/auth/middleware.py`, `src/auth/auth.py`, `src/auth/user_manager.py`

### Infrastructure (AWS Serverless)
- **Compute**: Lambda (FastAPI + Mangum adapter) with Docker containers via ECR
- **API**: API Gateway with Cognito JWT authorization
- **CDN**: CloudFront for global edge caching
- **Storage**: S3 for static assets, Secrets Manager for configuration
- **Monitoring**: CloudWatch logging and alerting
- **Environments**: Dev/prod separation with resource suffixes and isolated configurations


