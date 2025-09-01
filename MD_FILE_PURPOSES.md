Recommended Structure

  README.md - Human-focused developer documentation

  Purpose: Get developers productive quickly
  - Quick Start - Installation, setup, running locally
  - Project Overview - Brief description and architecture
  - API Documentation - Endpoints, examples, authentication
  - Configuration - Environment variables, Auth0 setup
  - Development Commands - Testing, linting, Docker
  - Contributing - Code style, workflow

  CLAUDE.md - Claude Code operational guidance

  Purpose: Help Claude Code work effectively on the project
  - Current Status - What's implemented, what's next
  - Development Commands - Commands Claude should use
  - Architecture Decisions - Key patterns to follow
  - Implementation Guidelines - Code conventions, security practices
  - Next Priority Tasks - Specific TODOs for current work

  ARCHITECTURE.md - Technical design documentation

  Purpose: Preserve design decisions and rationale for team members
  - Design Decisions - Why choices were made, alternatives considered
  - System Architecture - Detailed component interaction diagrams
  - Authentication Strategy - Full Auth0 implementation rationale
  - Model Adapter Pattern - Implementation details and extensibility
  - Deployment Strategy - Container and cloud deployment approach

  CHANGELOG.md - Project history

  Purpose: Track completed phases and changes over time
  - Phase Completion History - What was built when
  - Breaking Changes - Migration notes between versions
  - Feature Additions - New capabilities added


  Key Benefits of This Structure

  For Claude Code:
  - CLAUDE.md stays focused on current state and actionable next steps
  - Less noise from historical context and setup instructions
  - Clear development commands and patterns to follow

  For Humans:
  - README.md is the entry point for new developers
  - ARCHITECTURE.md preserves institutional knowledge
  - CHANGELOG.md tracks project evolution
  - Each file serves a single, clear purpose

  For Project Maintenance:
  - Reduces duplication and maintenance burden
  - Information lives in logical places
  - Easier to keep current and accurate
