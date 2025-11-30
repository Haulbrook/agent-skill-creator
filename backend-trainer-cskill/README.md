# Backend Trainer Skill

A personal development coach for backend excellence. Analyzes, validates, and guides your code architecture from the inside out.

## Overview

Backend Trainer is your dedicated backend development mentor that:
- Reviews code architecture and design patterns
- Analyzes API design for RESTful compliance
- Validates database schemas and query performance
- Scans for security vulnerabilities
- Identifies performance bottlenecks
- Prepares handoff packages for frontend agents

**Key Feature**: Designed for **inter-agent collaboration** - works seamlessly with frontend agents for full-stack compatibility.

## Quick Start

### Activation

Simply say any of these to activate the Backend Trainer:

```
"Review my backend architecture"
"Analyze this API design"
"Check my database schema"
"Help me prepare the backend for frontend integration"
"Train me on backend best practices"
```

### Example Usage

#### Full Backend Review

```
User: Review my backend code

Backend Trainer: ## Backend Architecture Review

### Overall Assessment: B+ (85/100)

**Architecture Type**: Layered (MVC variant)

**Strengths:**
- Clear separation between routes, controllers, and services
- Consistent use of dependency injection
- Good use of repository pattern

**Areas for Improvement:**
1. **Controller Bloat** - UserController contains business logic
   Location: controllers/user_controller.py:45-120
   Recommendation: Extract to UserService

2. **Missing Service Layer** - Order logic split across layers
   Recommendation: Create OrderService

### API Design: 78/100
- 3 endpoints missing input validation
- Inconsistent error response format

### Security: 90/100
- No critical issues
- 2 medium issues (see report)

### Performance: 82/100
- N+1 query detected in OrderController
- Missing indexes on orders.user_id
```

#### Frontend Handoff

```
User: Prepare API contract for frontend

Backend Trainer: ## Frontend Handoff Package Generated

**Included:**
- OpenAPI 3.0 specification (47 endpoints)
- TypeScript interfaces for all types
- Authentication flow documentation
- Error response catalog

**Generated Files:**
- handoff/api-contract.json
- handoff/types.ts
- handoff/auth-flow.md

**Compatibility Notes:**
- All dates are ISO-8601 strings
- IDs are UUIDs
- Pagination is cursor-based
```

## Capabilities

### 1. Architecture Analysis

Evaluates your code structure:
- Layer separation (Controllers, Services, Repositories)
- Design pattern compliance
- Dependency flow analysis
- Anti-pattern detection

### 2. API Review

Checks your API design:
- RESTful compliance
- Input validation coverage
- Error handling consistency
- Documentation completeness

### 3. Database Analysis

Reviews your data layer:
- Schema normalization
- Index optimization
- N+1 query detection
- ORM usage efficiency

### 4. Security Scanning

Identifies vulnerabilities:
- SQL/Command injection
- Authentication flaws
- Sensitive data exposure
- OWASP Top 10 coverage

### 5. Performance Analysis

Finds bottlenecks:
- Algorithmic complexity
- Database query efficiency
- Memory usage patterns
- I/O optimization opportunities

### 6. Frontend Handoff

Generates integration packages:
- OpenAPI specifications
- TypeScript interfaces
- Authentication documentation
- Error code catalogs

## Inter-Agent Collaboration

Backend Trainer can work alongside other agents:

### Supported Agents

| Agent | Collaboration Type |
|-------|-------------------|
| Frontend Trainer | Full handoff & sync |
| UI Aesthetic | Data schema sharing |
| Full-Stack Coordinator | Orchestrated reviews |

### Collaboration Example

```
User: Work with the frontend agent on this feature

Backend Trainer: ## Collaboration Session Started

**Session ID**: session_20241201_001
**Participants**: backend-trainer, frontend-trainer

**Sync Points:**
1. API Contract Validation - Pending
2. Data Type Compatibility - Pending
3. Authentication Flow - Pending
4. Error Response Standards - Pending

I'll prepare the backend components and notify the
frontend agent when ready for integration.
```

## File Structure

```
backend-trainer-cskill/
├── .claude-plugin/
│   └── marketplace.json      # Activation config
├── SKILL.md                  # Full documentation
├── README.md                 # This file
├── scripts/
│   ├── analyzers/
│   │   ├── architecture_analyzer.py
│   │   ├── api_analyzer.py
│   │   ├── database_analyzer.py
│   │   ├── security_analyzer.py
│   │   └── performance_analyzer.py
│   ├── protocols/
│   │   ├── frontend_handoff.py
│   │   └── collaboration_bridge.py
│   └── __init__.py
├── references/              # Best practices & patterns
└── assets/                  # Examples & templates
```

## Analysis Output Formats

### Summary Report

```json
{
  "overall_score": 85,
  "architecture": {
    "score": 90,
    "type": "layered",
    "patterns": ["repository", "dependency_injection"]
  },
  "api": {
    "score": 78,
    "endpoints": 47,
    "issues": 5
  },
  "database": {
    "score": 82,
    "type": "postgresql",
    "orm": "sqlalchemy"
  },
  "security": {
    "score": 90,
    "risk_level": "low",
    "critical_issues": 0
  },
  "performance": {
    "score": 75,
    "bottlenecks": 3
  }
}
```

### Handoff Package

```json
{
  "handoff_version": "1.0",
  "generated_by": "backend-trainer-cskill",
  "api_contracts": {...},
  "data_schemas": {...},
  "typescript_interfaces": "...",
  "authentication": {...},
  "error_codes": [...],
  "backend_health": {...}
}
```

## Best Practices Covered

- Clean Architecture principles
- SOLID design patterns
- RESTful API conventions
- Database normalization
- OWASP security guidelines
- Performance optimization techniques

## Supported Technologies

### Languages
- Python
- JavaScript/TypeScript
- Go
- Rust
- Java

### Frameworks
- FastAPI, Django, Flask (Python)
- Express, NestJS (Node.js)
- Gin (Go)
- Actix (Rust)
- Spring Boot (Java)

### Databases
- PostgreSQL
- MySQL
- SQLite
- MongoDB
- Redis

### ORMs
- SQLAlchemy
- Django ORM
- TypeORM
- Prisma
- Sequelize

## Related Skills

- **Frontend Trainer** - UI/UX development coaching
- **Full-Stack Coordinator** - End-to-end project management
- **Security Auditor** - Deep security analysis

## Version

**Current Version**: 1.0.0

## License

Part of the Agent-Skill-Creator ecosystem.
