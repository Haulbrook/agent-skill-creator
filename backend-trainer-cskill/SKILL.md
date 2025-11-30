# Backend Trainer - Personal Development Coach for Server-Side Excellence

## Overview

**Backend Trainer** is a specialized intelligent agent that serves as your personal development coach for all things backend. Unlike traditional code review tools, Backend Trainer operates "from the inside" - understanding not just what your code does, but why it matters in the context of your entire system architecture.

This skill is designed with **inter-agent collaboration** at its core. It can work seamlessly alongside frontend agents (like UI aesthetic trainers) to ensure full-stack compatibility and cohesive application development.

### Problem Statement

Backend development presents unique challenges:
- **Invisible complexity**: Backend code powers everything but its quality issues aren't visible to end users until they become critical
- **Architecture drift**: Systems evolve and deviate from intended patterns without systematic review
- **Integration gaps**: Backend-frontend handoffs often result in mismatched contracts and broken integrations
- **Security blind spots**: Vulnerabilities hide in business logic, authentication flows, and data access patterns
- **Performance debt**: Inefficient queries, missing indexes, and poor caching strategies accumulate silently

### Solution

Backend Trainer provides:
1. **Deep Architecture Analysis** - Understanding code from the inside out
2. **Continuous Guidance** - Mentorship-style feedback, not just error reports
3. **Frontend Collaboration Protocols** - Structured handoffs for full-stack harmony
4. **Actionable Recommendations** - Specific, implementable improvements
5. **Pattern Recognition** - Identifying both anti-patterns and opportunities for best practices

---

## Core Capabilities

### 1. Architecture Analysis Engine

Analyzes backend code structure to evaluate:

- **Layer Separation**: Controllers, Services, Repositories, Models
- **Dependency Flow**: Ensuring proper dependency injection and inversion
- **Module Boundaries**: Clear separation of concerns
- **Code Organization**: File structure and naming conventions
- **Pattern Compliance**: Repository, Factory, Strategy, Observer patterns

### 2. API Design Reviewer

Evaluates RESTful, GraphQL, and WebSocket implementations:

- **Endpoint Design**: Resource naming, HTTP method usage, URL structure
- **Request/Response Schemas**: Data validation, type safety, documentation
- **Versioning Strategy**: API evolution without breaking changes
- **Error Handling**: Consistent error response formats
- **Rate Limiting & Throttling**: Protection against abuse
- **Authentication/Authorization**: Proper security implementation

### 3. Database Architecture Validator

Reviews database design and data access patterns:

- **Schema Design**: Normalization, relationships, constraints
- **Index Strategy**: Query optimization through proper indexing
- **Query Analysis**: N+1 detection, join optimization, query plans
- **Migration Safety**: Non-breaking schema changes
- **ORM Usage**: Efficient use of ORMs without performance penalties
- **Connection Management**: Pooling, transaction handling

### 4. Business Logic Assessor

Examines the heart of your application:

- **Domain Model Integrity**: Business rules properly encapsulated
- **Validation Logic**: Input validation at appropriate layers
- **State Management**: Consistent state transitions
- **Error Recovery**: Graceful handling of edge cases
- **Transaction Boundaries**: ACID compliance where needed

### 5. Security Scanner

Identifies vulnerabilities in backend code:

- **Injection Vulnerabilities**: SQL, NoSQL, Command injection
- **Authentication Flaws**: Weak tokens, session management issues
- **Authorization Gaps**: Missing access controls, privilege escalation
- **Data Exposure**: Sensitive data in logs, responses, or error messages
- **Cryptography Review**: Proper use of encryption and hashing

### 6. Performance Analyzer

Detects bottlenecks and optimization opportunities:

- **Query Performance**: Slow queries, missing indexes
- **Caching Opportunities**: What to cache, cache invalidation
- **Memory Usage**: Object lifecycle, memory leaks
- **Concurrency**: Race conditions, deadlocks, thread safety
- **I/O Optimization**: File handling, network calls, database connections

### 7. Frontend Handoff Generator

Prepares comprehensive handoff packages for frontend agents:

- **API Contracts**: OpenAPI/Swagger specifications
- **Data Schemas**: TypeScript interfaces, JSON schemas
- **Authentication Flow Documentation**: Token handling, refresh logic
- **Error Response Catalog**: All possible errors with handling guidance
- **Real-time Communication Specs**: WebSocket events, SSE streams

---

## Architecture & Design

### Skill Architecture

```
backend-trainer-cskill/
├── .claude-plugin/
│   └── marketplace.json          # Activation & configuration
├── SKILL.md                      # This documentation (you are here)
├── README.md                     # Quick start guide
├── scripts/
│   ├── analyzers/
│   │   ├── architecture_analyzer.py    # Code structure analysis
│   │   ├── api_analyzer.py             # API design evaluation
│   │   ├── database_analyzer.py        # Schema & query analysis
│   │   ├── security_analyzer.py        # Vulnerability detection
│   │   └── performance_analyzer.py     # Bottleneck identification
│   ├── validators/
│   │   ├── pattern_validator.py        # Design pattern compliance
│   │   ├── contract_validator.py       # API contract validation
│   │   └── schema_validator.py         # Database schema validation
│   ├── generators/
│   │   ├── api_contract_generator.py   # OpenAPI spec generation
│   │   ├── handoff_report_generator.py # Frontend handoff docs
│   │   └── improvement_plan_generator.py # Action item generation
│   └── protocols/
│       ├── frontend_handoff.py         # Frontend agent communication
│       ├── sync_protocol.py            # Inter-agent synchronization
│       └── collaboration_bridge.py     # Multi-agent coordination
├── references/
│   ├── patterns/                       # Best practice patterns
│   ├── checklists/                     # Review checklists
│   └── templates/                      # Report templates
└── assets/
    └── examples/                       # Example reviews & handoffs
```

### Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND TRAINER PIPELINE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────┐   ┌────────────┐   ┌───────────┐   ┌──────────────┐ │
│  │  INGEST   │──▶│  ANALYZE   │──▶│ VALIDATE  │──▶│   GENERATE   │ │
│  │           │   │            │   │           │   │              │ │
│  │ • Files   │   │ • Arch     │   │ • Patterns│   │ • Reports    │ │
│  │ • Config  │   │ • API      │   │ • Security│   │ • Contracts  │ │
│  │ • Schema  │   │ • Database │   │ • Perf    │   │ • Handoffs   │ │
│  └───────────┘   └────────────┘   └───────────┘   └──────────────┘ │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  COLLABORATION LAYER                           │   │
│  ├───────────────────────────────────────────────────────────────┤   │
│  │  Frontend Agent ◄────── Sync Protocol ──────► Backend Trainer │   │
│  │                                                                │   │
│  │  • API Contract Validation    • Schema Compatibility Check    │   │
│  │  • Data Type Alignment        • Error Response Standards      │   │
│  │  • Auth Flow Verification     • Real-time Event Sync          │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Inter-Agent Collaboration Protocol

Backend Trainer uses a structured protocol for working with frontend agents:

#### Handoff Package Structure

```json
{
  "handoff_version": "1.0",
  "generated_by": "backend-trainer-cskill",
  "generated_at": "ISO-8601 timestamp",
  "target_agent": "frontend-trainer-cskill",

  "api_contracts": {
    "openapi_spec": "...OpenAPI 3.0 specification...",
    "endpoints": [
      {
        "path": "/api/users/{id}",
        "method": "GET",
        "request_schema": {...},
        "response_schema": {...},
        "error_responses": {...},
        "authentication": "bearer_token",
        "rate_limit": "100/minute"
      }
    ]
  },

  "data_schemas": {
    "typescript_interfaces": "...generated interfaces...",
    "json_schemas": {...}
  },

  "authentication": {
    "type": "jwt",
    "token_location": "Authorization header",
    "refresh_mechanism": "refresh_token endpoint",
    "token_lifetime": "15 minutes",
    "refresh_lifetime": "7 days"
  },

  "real_time": {
    "websocket_events": [...],
    "sse_streams": [...]
  },

  "backend_health": {
    "architecture_score": 85,
    "security_score": 90,
    "performance_score": 78,
    "issues_to_resolve": [...],
    "recommendations": [...]
  }
}
```

#### Sync Points with Frontend Agent

| Sync Point | Backend Provides | Frontend Confirms |
|------------|------------------|-------------------|
| API Contract | Endpoint specs, schemas | Consumption compatibility |
| Data Types | Type definitions | UI binding requirements |
| Auth Flow | Token handling specs | Client-side implementation |
| Error Handling | Error response catalog | UI error display mapping |
| Real-time Events | Event definitions | Subscription patterns |

---

## Detailed Component Specifications

### Architecture Analyzer (`scripts/analyzers/architecture_analyzer.py`)

**Purpose**: Evaluate overall backend code structure and organization

**Analysis Dimensions**:

1. **Layer Analysis**
   - Presentation Layer (Controllers/Routes)
   - Business Logic Layer (Services)
   - Data Access Layer (Repositories/DAOs)
   - Domain Layer (Models/Entities)

2. **Dependency Analysis**
   - Dependency direction (should flow inward)
   - Circular dependency detection
   - Coupling metrics
   - Cohesion assessment

3. **Pattern Detection**
   - Repository Pattern
   - Unit of Work
   - CQRS (Command Query Responsibility Segregation)
   - Event Sourcing
   - Domain-Driven Design patterns

**Output Format**:
```python
{
    "architecture_type": "layered|hexagonal|clean|monolith|microservice",
    "layer_compliance": {
        "presentation": {"score": 85, "issues": [...]},
        "business": {"score": 90, "issues": [...]},
        "data_access": {"score": 75, "issues": [...]}
    },
    "patterns_detected": ["repository", "dependency_injection"],
    "anti_patterns_detected": ["god_class", "feature_envy"],
    "recommendations": [
        {
            "priority": "high",
            "category": "separation_of_concerns",
            "description": "Move database logic from UserController to UserRepository",
            "file": "controllers/user_controller.py",
            "line": 45
        }
    ]
}
```

### API Analyzer (`scripts/analyzers/api_analyzer.py`)

**Purpose**: Evaluate API design quality and RESTful compliance

**Analysis Dimensions**:

1. **Resource Design**
   - Noun-based resource naming
   - Proper HTTP method usage
   - Hierarchical URL structure
   - Query parameter conventions

2. **Request/Response Quality**
   - Input validation presence
   - Response envelope consistency
   - Pagination implementation
   - HATEOAS compliance (if applicable)

3. **Documentation & Discoverability**
   - OpenAPI/Swagger completeness
   - Example request/response presence
   - Error documentation

**Scoring Criteria**:
| Aspect | Weight | Criteria |
|--------|--------|----------|
| Resource Naming | 20% | RESTful conventions followed |
| HTTP Methods | 15% | Correct verb usage |
| Status Codes | 15% | Appropriate codes returned |
| Validation | 20% | Input properly validated |
| Error Handling | 15% | Consistent error format |
| Documentation | 15% | OpenAPI completeness |

### Database Analyzer (`scripts/analyzers/database_analyzer.py`)

**Purpose**: Evaluate database design, queries, and data access patterns

**Analysis Types**:

1. **Schema Analysis**
   ```python
   {
       "tables": [...],
       "relationships": [...],
       "normalization_level": "3NF",
       "denormalization_justified": [...],
       "missing_indexes": [...],
       "constraint_coverage": 85
   }
   ```

2. **Query Analysis**
   ```python
   {
       "total_queries": 150,
       "n_plus_one_detected": [
           {"location": "services/order_service.py:45", "query": "..."}
       ],
       "slow_queries": [...],
       "missing_eager_loading": [...],
       "optimization_opportunities": [...]
   }
   ```

3. **ORM Usage Analysis**
   ```python
   {
       "orm_used": "SQLAlchemy",
       "raw_sql_usage": 5,
       "proper_relationship_loading": true,
       "transaction_handling": "good",
       "connection_pooling": true
   }
   ```

### Security Analyzer (`scripts/analyzers/security_analyzer.py`)

**Purpose**: Identify security vulnerabilities and risks

**Vulnerability Categories**:

| Category | Detection Method | Severity |
|----------|-----------------|----------|
| SQL Injection | Pattern matching, taint analysis | Critical |
| Command Injection | Shell command analysis | Critical |
| Auth Bypass | Flow analysis | Critical |
| XSS (stored) | Output encoding check | High |
| IDOR | Authorization check presence | High |
| Mass Assignment | Input filtering analysis | Medium |
| Info Disclosure | Log/error message analysis | Medium |
| Weak Crypto | Algorithm detection | Medium |

**Output Format**:
```python
{
    "security_score": 75,
    "critical_issues": [...],
    "high_issues": [...],
    "medium_issues": [...],
    "low_issues": [...],
    "owasp_coverage": {
        "A01_broken_access_control": "partial",
        "A02_cryptographic_failures": "good",
        "A03_injection": "needs_improvement"
    }
}
```

### Performance Analyzer (`scripts/analyzers/performance_analyzer.py`)

**Purpose**: Identify performance bottlenecks and optimization opportunities

**Analysis Areas**:

1. **Database Performance**
   - Query execution plans
   - Index utilization
   - Connection pool efficiency

2. **Application Performance**
   - Algorithmic complexity
   - Memory allocation patterns
   - Caching opportunities

3. **I/O Performance**
   - File operation efficiency
   - Network call optimization
   - Async operation usage

---

## Frontend Collaboration Protocols

### Protocol 1: API Contract Handoff

When preparing backend for frontend integration:

```python
# Step 1: Generate comprehensive API contract
api_contract = {
    "openapi": "3.0.0",
    "info": {"title": "Backend API", "version": "1.0.0"},
    "paths": {
        "/api/users": {
            "get": {
                "summary": "List users",
                "parameters": [...],
                "responses": {
                    "200": {"content": {"application/json": {"schema": {...}}}}
                }
            }
        }
    },
    "components": {
        "schemas": {...},
        "securitySchemes": {...}
    }
}

# Step 2: Generate TypeScript interfaces for frontend
typescript_interfaces = """
export interface User {
    id: string;
    email: string;
    name: string;
    createdAt: string;
}

export interface UserListResponse {
    users: User[];
    pagination: Pagination;
}
"""

# Step 3: Document authentication flow
auth_documentation = {
    "login": {"endpoint": "/api/auth/login", "method": "POST"},
    "refresh": {"endpoint": "/api/auth/refresh", "method": "POST"},
    "token_storage": "httpOnly cookie recommended",
    "token_lifetime": "15 minutes",
    "refresh_lifetime": "7 days"
}
```

### Protocol 2: Real-time Event Sync

For WebSocket/SSE implementations:

```python
realtime_contract = {
    "websocket": {
        "endpoint": "/ws",
        "events": {
            "user.updated": {
                "payload": {"userId": "string", "changes": "object"},
                "direction": "server_to_client"
            },
            "message.new": {
                "payload": {"messageId": "string", "content": "string"},
                "direction": "bidirectional"
            }
        },
        "authentication": "token_in_query_param",
        "heartbeat_interval": 30000
    }
}
```

### Protocol 3: Error Response Standardization

Ensuring frontend can properly handle all error cases:

```python
error_catalog = {
    "error_format": {
        "code": "string (machine-readable)",
        "message": "string (human-readable)",
        "details": "object (optional additional info)",
        "timestamp": "ISO-8601 string"
    },
    "error_codes": {
        "AUTH_001": {"status": 401, "message": "Invalid credentials"},
        "AUTH_002": {"status": 401, "message": "Token expired"},
        "AUTH_003": {"status": 403, "message": "Insufficient permissions"},
        "VAL_001": {"status": 400, "message": "Validation failed", "has_details": True},
        "RES_001": {"status": 404, "message": "Resource not found"},
        "SRV_001": {"status": 500, "message": "Internal server error"}
    }
}
```

---

## Usage Examples

### Example 1: Full Backend Review

**User Request**: "Review my backend architecture"

**Backend Trainer Response**:

```markdown
## Backend Architecture Review

### Overall Assessment: B+ (85/100)

#### Architecture Type: Layered (MVC variant)

**Strengths:**
- Clear separation between routes, controllers, and services
- Consistent use of dependency injection
- Good use of repository pattern for data access

**Areas for Improvement:**

1. **Controller Bloat** (Priority: High)
   - `UserController` contains business logic that should be in `UserService`
   - Location: `controllers/user_controller.py:45-120`
   - Recommendation: Extract validation and business rules to service layer

2. **Missing Service Layer for Orders** (Priority: Medium)
   - Order-related logic is split between controller and repository
   - Create `OrderService` to encapsulate business rules

3. **Inconsistent Error Handling** (Priority: Medium)
   - Some endpoints return raw exceptions
   - Implement global error handler middleware

### API Design Review

| Endpoint | Score | Issues |
|----------|-------|--------|
| GET /users | 90 | None |
| POST /users | 75 | Missing input validation |
| GET /orders | 60 | N+1 query detected |

### Database Review

- Schema normalization: Good (3NF)
- Missing indexes on: `orders.user_id`, `products.category_id`
- Query optimization needed: 3 slow queries identified

### Security Assessment

- **Critical**: None found
- **High**: 1 (SQL injection risk in search endpoint)
- **Medium**: 3 (see detailed report)

### Recommended Action Items

1. [ ] Fix SQL injection in `/api/search` endpoint
2. [ ] Add missing database indexes
3. [ ] Refactor UserController business logic to UserService
4. [ ] Implement global error handling middleware
5. [ ] Add input validation to POST /users
```

### Example 2: Frontend Handoff Preparation

**User Request**: "Prepare API contract for frontend handoff"

**Backend Trainer Response**:

```markdown
## Frontend Handoff Package Generated

### API Contract Summary

I've generated a complete handoff package for the frontend team/agent.

**Included:**
- OpenAPI 3.0 specification (47 endpoints documented)
- TypeScript interfaces for all response types
- Authentication flow documentation
- Error response catalog (23 error codes)
- WebSocket event definitions

### Quick Reference for Frontend

**Authentication:**
```typescript
// Login
POST /api/auth/login
Body: { email: string, password: string }
Response: { token: string, refreshToken: string, user: User }

// All authenticated requests
Header: Authorization: Bearer <token>
```

**Core Endpoints:**
| Resource | Create | Read | Update | Delete |
|----------|--------|------|--------|--------|
| Users | POST /users | GET /users/:id | PUT /users/:id | DELETE /users/:id |
| Orders | POST /orders | GET /orders/:id | PUT /orders/:id | - |
| Products | POST /products | GET /products/:id | PUT /products/:id | DELETE /products/:id |

**Generated Files:**
- `handoff/api-contract.json` - Full OpenAPI spec
- `handoff/types.ts` - TypeScript interfaces
- `handoff/auth-flow.md` - Authentication documentation
- `handoff/error-codes.md` - Error handling guide

### Compatibility Notes for Frontend Agent

When the frontend agent processes this handoff:
1. All date fields are ISO-8601 strings
2. IDs are UUIDs (string format)
3. Pagination uses cursor-based approach
4. File uploads use multipart/form-data
```

### Example 3: Collaborative Full-Stack Review

**User Request**: "Work with the frontend agent to ensure full stack compatibility"

**Backend Trainer Response**:

```markdown
## Full-Stack Compatibility Analysis

### Sync Protocol Initiated

I've prepared a compatibility report that can be shared with the frontend agent.

### Backend Status

| Component | Status | Frontend Dependency |
|-----------|--------|-------------------|
| User API | Ready | User management UI |
| Auth System | Ready | Login/Register forms |
| Order API | Needs work | Order flow UI |
| WebSocket | Ready | Real-time updates |

### Identified Compatibility Issues

1. **Type Mismatch: Order.total**
   - Backend sends: `number` (float)
   - Frontend expects: `string` (formatted currency)
   - **Recommendation**: Backend should send raw number, frontend formats for display

2. **Missing Endpoint: Order History**
   - Frontend needs: `GET /api/users/:id/orders`
   - Backend status: Not implemented
   - **Action Required**: Implement endpoint before frontend integration

3. **Pagination Inconsistency**
   - `/api/products` uses offset-based pagination
   - `/api/orders` uses cursor-based pagination
   - **Recommendation**: Standardize to cursor-based for better performance

### Handoff Checklist for Frontend Agent

```json
{
  "ready_for_integration": [
    "User CRUD operations",
    "Authentication flow",
    "Product catalog",
    "WebSocket notifications"
  ],
  "pending_backend_work": [
    "Order history endpoint",
    "Pagination standardization"
  ],
  "frontend_considerations": [
    "Handle token refresh on 401",
    "Implement optimistic updates for better UX",
    "Cache product catalog locally"
  ]
}
```

### Recommended Collaboration Workflow

1. Backend Trainer completes pending items
2. Generate updated API contract
3. Frontend agent validates consumption compatibility
4. Both agents verify integration test scenarios
```

---

## Quality Standards

### Code Review Principles

1. **Constructive Feedback**: All feedback is actionable and includes specific remediation steps
2. **Priority-Based**: Issues are categorized by severity and business impact
3. **Context-Aware**: Recommendations consider the project's specific architecture and constraints
4. **Best Practice Aligned**: Suggestions follow industry-standard patterns and conventions

### Output Requirements

- No vague recommendations ("improve code quality")
- Every issue includes file location and line numbers
- Suggested fixes include code examples
- Performance impacts are quantified where possible
- Security issues include CVSS-like severity ratings

---

## Error Handling & Recovery

### Analysis Errors

| Error Type | Handling Strategy |
|------------|-------------------|
| Missing files | Report which files couldn't be found, continue with available |
| Syntax errors | Report parsing failures, skip affected files |
| Large codebase | Use sampling strategy, report coverage percentage |
| Missing dependencies | Note assumptions made, suggest dependency verification |

### Collaboration Errors

| Error Type | Handling Strategy |
|------------|-------------------|
| Frontend agent unavailable | Generate standalone handoff package |
| Incompatible protocol version | Fall back to basic JSON export |
| Sync timeout | Queue changes for async processing |

---

## Extension Points

### Adding New Analyzers

```python
# Create new analyzer in scripts/analyzers/
class CustomAnalyzer:
    def __init__(self, config: dict):
        self.config = config

    def analyze(self, codebase_path: str) -> AnalysisResult:
        # Implementation
        pass

    def get_recommendations(self) -> list[Recommendation]:
        # Implementation
        pass
```

### Adding New Collaboration Protocols

```python
# Create new protocol in scripts/protocols/
class CustomProtocol:
    def __init__(self, target_agent: str):
        self.target = target_agent

    def generate_handoff(self, analysis_result: dict) -> HandoffPackage:
        # Implementation
        pass

    def receive_feedback(self, feedback: dict) -> None:
        # Implementation
        pass
```

---

## Testing Strategy

### Unit Tests

- Each analyzer has isolated unit tests
- Mock file system for consistent testing
- Pattern detection accuracy tests

### Integration Tests

- Full pipeline tests with sample codebases
- Collaboration protocol tests with mock agents
- Report generation validation

### Validation Tests

- Ensure generated contracts are valid OpenAPI
- TypeScript interface compilation tests
- JSON schema validation

---

## Performance Considerations

- **Large Codebase Handling**: Sampling strategies for repositories > 10k files
- **Incremental Analysis**: Cache previous results, only analyze changes
- **Parallel Processing**: Analyzers run concurrently where possible
- **Memory Management**: Stream large files, don't load entirely into memory

---

## Deployment & Installation

### Prerequisites

- Python 3.9+
- Access to target codebase
- (Optional) Frontend agent for collaboration features

### Installation

1. Copy `backend-trainer-cskill/` to your Claude Code skills directory
2. Verify activation by saying "review my backend"
3. (Optional) Configure collaboration settings in `marketplace.json`

### Configuration

Edit `marketplace.json` to customize:
- Activation keywords for your workflow
- Compatible agent list for collaboration
- Analysis depth and coverage settings

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial release with full analysis suite |

---

## Credits

Generated by **Agent-Skill-Creator** meta-skill.

Designed for seamless collaboration with frontend development agents to enable comprehensive full-stack development training and review.
