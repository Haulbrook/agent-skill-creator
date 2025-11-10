# Modular Program Refactor Skill

## Overview

The **Modular Program Refactor Skill** is a specialized Claude skill designed to analyze, deconstruct, and reconstruct existing programs into clean, modular architectures. Unlike simple code refactoring tools that focus on syntax improvements, this skill provides deep architectural analysis that understands *why* components exist, *how* they interact, and *what purpose* they serve in the larger system.

This skill excels at transforming monolithic, tightly-coupled, or halfway-built programs into well-structured modular systems with a clear "central nervous system" architecture - where core functionality is separated from peripheral features, dependencies are explicit, and components communicate through well-defined interfaces.

## Core Philosophy

**Understanding Over Cloning**: This skill doesn't just copy-paste or split code mechanically. It analyzes the semantic purpose of each component, understands business logic flow, identifies hidden dependencies, and reconstructs the program with intentional design patterns that maintain functionality while improving maintainability, testability, and extensibility.

**Functionality First**: All refactoring maintains 100% functional equivalence. The skill validates that reconstructed modules preserve original behavior while improving structure.

**Forward-Thinking Integration**: Designed to work hand-in-hand with the "Forward Thinker Skill" to not just maintain but evolve the architecture, identifying opportunities for improvement while preserving the project's core intentions.

## Key Capabilities

### 1. Deep Architectural Analysis
- **Code Structure Mapping**: Identifies all files, modules, classes, functions, and their relationships
- **Dependency Graph Construction**: Maps both explicit (imports, includes) and implicit (data flow, state sharing) dependencies
- **Pattern Recognition**: Detects existing design patterns (or lack thereof) and architectural anti-patterns
- **Semantic Understanding**: Analyzes *why* code exists, not just what it does
- **Business Logic Extraction**: Separates core business logic from infrastructure, UI, and utility code

### 2. Intelligent Decomposition
- **Responsibility Identification**: Determines the single responsibility of each component
- **Coupling Analysis**: Measures tight coupling and identifies opportunities for decoupling
- **Cohesion Assessment**: Evaluates whether related functionality is properly grouped
- **Interface Discovery**: Identifies natural boundaries where modules should communicate
- **Data Flow Tracking**: Maps how data moves through the system

### 3. Modular Reconstruction Planning
- **Central Nervous System Design**: Creates a core module that orchestrates the entire system
- **Layer Separation**: Organizes code into clear layers (domain, application, infrastructure, presentation)
- **Module Boundary Definition**: Establishes clear interfaces between components
- **Dependency Inversion**: Applies dependency injection principles where appropriate
- **Plugin Architecture**: Designs extensibility points for future features

### 4. Forward-Thinking Integration
- **Enhancement Identification**: Spots opportunities for architectural improvements
- **Future-Proofing**: Designs modules to accommodate anticipated changes
- **Technical Debt Assessment**: Identifies areas needing modernization
- **Best Practice Application**: Applies current industry standards and patterns
- **Collaboration Protocol**: Seamlessly passes analysis to Forward Thinker Skill for innovation

## When to Use This Skill

### Perfect Use Cases

1. **Legacy Code Modernization**
   - "This 10,000-line monolithic application needs to be broken into microservices"
   - "Refactor this spaghetti code into a clean architecture"

2. **Halfway-Built Projects**
   - "I started building this but the structure got messy - help me reorganize"
   - "The codebase has grown organically and now it's hard to maintain"

3. **Architecture Migration**
   - "Convert this MVC app to a hexagonal architecture"
   - "Transform this procedural code into an object-oriented design"

4. **Plugin System Creation**
   - "Make this application extensible with a plugin architecture"
   - "Add a modular extension system to allow third-party integrations"

5. **Preparation for Scaling**
   - "We need to make this codebase team-friendly for multiple developers"
   - "Prepare this prototype for production-grade development"

6. **Collaboration with Forward Thinker**
   - "Analyze this code and work with Forward Thinker to propose an improved architecture"
   - "Understand the current structure and help evolve it into something better"

### When NOT to Use This Skill

- **Simple Syntax Cleanup**: Use a linter or code formatter instead
- **Bug Fixes**: This skill focuses on architecture, not debugging
- **Performance Optimization**: Use a profiler and performance analysis tool
- **From-Scratch Development**: If there's no existing code to analyze, start with architecture design directly
- **Minor Refactoring**: Small local refactors don't need architectural analysis

## How It Works

### Phase 1: Discovery & Analysis
1. **Codebase Scanning**: Recursively analyzes all source files
2. **Dependency Mapping**: Constructs complete dependency graphs
3. **Pattern Detection**: Identifies existing architectural patterns
4. **Complexity Metrics**: Calculates coupling, cohesion, and complexity scores
5. **Purpose Inference**: Uses semantic analysis to understand component intent

### Phase 2: Architectural Planning
1. **Module Identification**: Determines logical module boundaries
2. **Interface Design**: Defines clean contracts between modules
3. **Layer Architecture**: Establishes architectural layers and flow
4. **Central System Design**: Creates the orchestration layer (CNS)
5. **Migration Strategy**: Plans incremental refactoring approach

### Phase 3: Reconstruction
1. **Module Scaffolding**: Creates new modular structure
2. **Code Migration**: Moves code to appropriate modules
3. **Interface Implementation**: Implements clean boundaries
4. **Dependency Injection**: Applies inversion of control patterns
5. **Integration Testing**: Validates functional equivalence

### Phase 4: Forward-Thinking Collaboration
1. **Analysis Export**: Packages architectural insights for Forward Thinker
2. **Enhancement Opportunities**: Identifies areas for innovation
3. **Constraint Documentation**: Explains limitations and requirements
4. **Vision Alignment**: Ensures proposals maintain project intentions
5. **Iterative Refinement**: Collaborates on architectural evolution

## Integration with Forward Thinker Skill

This skill is designed to work seamlessly with the Forward Thinker Skill:

**Modular Program Refactor → Forward Thinker Flow:**
1. MPR analyzes existing architecture and creates modular structure
2. MPR identifies enhancement opportunities and constraints
3. MPR exports structured analysis to Forward Thinker
4. Forward Thinker proposes innovative improvements within constraints
5. MPR validates proposals for structural soundness
6. Combined output: Evolution plan that's both innovative and feasible

**Automatic Handoff Triggers:**
- User requests "improve" or "enhance" during refactoring
- User asks for "forward-thinking" or "innovative" solutions
- Analysis reveals significant technical debt or missed opportunities
- Reconstruction complete and user wants next-generation features

## Technical Approach

### Supported Languages
- **Primary**: Python, JavaScript/TypeScript, Java, C#, Go, Rust
- **Secondary**: Ruby, PHP, C++, Kotlin, Swift
- **Framework-Aware**: React, Vue, Angular, Django, Flask, Spring Boot, Express, etc.

### Analysis Techniques
- **Static Analysis**: AST parsing, symbol resolution, call graph construction
- **Pattern Matching**: Design pattern recognition, anti-pattern detection
- **Metrics Calculation**: Cyclomatic complexity, coupling metrics, cohesion scores
- **Semantic Analysis**: NLP-based intent understanding, documentation analysis
- **Dependency Resolution**: Import tracking, package management analysis

### Output Formats
- **Architecture Diagrams**: Module relationships, layer diagrams, dependency graphs
- **Migration Plans**: Step-by-step refactoring guides
- **Module Specifications**: Interface definitions, contracts, documentation
- **Code Scaffolds**: New modular structure with TODO markers
- **Test Strategies**: How to validate functional equivalence

## Example Workflows

### Example 1: Monolithic Web App Decomposition

**Input:**
```
User: "I have a 5000-line Python Flask app in app.py that handles
authentication, database operations, API routes, and email sending
all mixed together. Help me break it into a clean modular architecture."
```

**Skill Actions:**
1. Analyzes app.py to identify distinct responsibilities
2. Maps dependencies between authentication, database, API, and email logic
3. Identifies implicit coupling through shared global state
4. Proposes modular structure:
   - `core/` - Central orchestrator (CNS)
   - `auth/` - Authentication module
   - `data/` - Database abstraction layer
   - `api/` - Route handlers
   - `notifications/` - Email service
   - `config/` - Configuration management
5. Designs clean interfaces between modules
6. Creates migration plan with validation tests
7. Implements refactored structure maintaining 100% functionality

### Example 2: Halfway-Built Project Restructuring

**Input:**
```
User: "I'm building a data processing pipeline but the code got messy.
I have functions scattered across multiple files with circular dependencies.
Help me reorganize this into something maintainable."
```

**Skill Actions:**
1. Scans all files to map current structure
2. Constructs dependency graph revealing circular dependencies
3. Identifies data flow from input → processing → output
4. Recognizes pipeline pattern opportunity
5. Proposes pipeline architecture:
   - `pipeline/core.py` - Orchestrator (CNS)
   - `pipeline/stages/` - Individual processing stages
   - `pipeline/connectors/` - Stage communication
   - `pipeline/config/` - Pipeline configuration
6. Breaks circular dependencies through interface abstraction
7. Implements stage-based architecture with clear data contracts
8. Adds plugin system for extensibility

### Example 3: Forward-Thinking Collaboration

**Input:**
```
User: "Analyze this e-commerce codebase and work with Forward Thinker
to propose a modern, scalable architecture that maintains the current
features but prepares us for growth."
```

**Skill Actions:**
1. **MPR Phase**:
   - Analyzes current monolithic structure
   - Identifies modules: Products, Cart, Checkout, Payments, Users
   - Maps tight coupling through shared database access
   - Documents business logic and constraints

2. **Handoff to Forward Thinker**:
   - Exports: Current architecture, module boundaries, business rules
   - Requests: Scalable architecture proposal, modern patterns, growth enablers

3. **Forward Thinker Phase**:
   - Proposes event-driven microservices architecture
   - Suggests CQRS pattern for read/write separation
   - Recommends API gateway and service mesh

4. **MPR Validation Phase**:
   - Validates proposal maintains business logic
   - Ensures functional equivalence during migration
   - Creates incremental migration strategy

5. **Combined Output**:
   - Phased evolution plan from monolith → modular monolith → microservices
   - Maintains functionality at each stage
   - Includes testing strategy and rollback plans

## Best Practices

### Before Starting
1. **Backup Your Code**: Always version control before major refactoring
2. **Have Tests**: Existing tests help validate functional equivalence
3. **Document Business Logic**: Explain any non-obvious requirements
4. **Define Success Criteria**: What does "done" look like?

### During Refactoring
1. **Incremental Changes**: Refactor in small, testable steps
2. **Continuous Validation**: Run tests after each module migration
3. **Interface-First**: Define module boundaries before moving code
4. **Document Decisions**: Keep track of architectural choices

### After Refactoring
1. **Comprehensive Testing**: Validate all functionality still works
2. **Performance Checks**: Ensure refactoring didn't degrade performance
3. **Documentation Updates**: Update README, architecture docs, etc.
4. **Team Review**: Get feedback from other developers
5. **Consider Forward Thinking**: Think about next evolution steps

## Configuration Options

The skill supports various configuration flags:

```python
{
  "analysis_depth": "deep",  # "shallow" | "medium" | "deep"
  "preserve_comments": true,  # Keep original code comments
  "strict_equivalence": true,  # Require 100% functional match
  "target_architecture": "layered",  # "layered" | "hexagonal" | "microservices" | "plugin"
  "language_version": "auto",  # Auto-detect or specify
  "forward_thinking_integration": true,  # Auto-handoff to Forward Thinker
  "generate_tests": true,  # Generate equivalence tests
  "documentation_level": "comprehensive"  # "minimal" | "standard" | "comprehensive"
}
```

## Output Structure

After completing analysis and refactoring, you'll receive:

1. **Architecture Analysis Report**
   - Current structure assessment
   - Identified issues and opportunities
   - Complexity metrics

2. **Modular Design Specification**
   - Module hierarchy
   - Interface definitions
   - Dependency graph

3. **Refactored Code**
   - New modular structure
   - Clean interfaces
   - Documentation

4. **Migration Guide**
   - Step-by-step instructions
   - Testing strategy
   - Rollback procedures

5. **Forward-Thinking Recommendations**
   - Enhancement opportunities
   - Future evolution paths
   - Technical debt priorities

## Limitations & Constraints

- **Not a Magic Wand**: Cannot fix fundamentally flawed business logic
- **Human Oversight Required**: Architectural decisions need validation
- **Testing Dependency**: Functional validation relies on existing or generated tests
- **Context Matters**: Some architectural choices depend on team/organizational context
- **Performance Trade-offs**: Modularization may introduce minimal overhead

## Support & Resources

- **Architecture Patterns**: See `references/architecture-patterns.md`
- **Refactoring Strategies**: See `references/refactoring-strategies.md`
- **Example Projects**: See `references/examples/`
- **Forward Thinker Integration**: See `references/forward-thinker-integration.md`

## Version

**Current Version**: 1.0.0
**Last Updated**: 2025-11-10
**Compatibility**: Claude Sonnet 4+

---

## Quick Start

To use this skill:

1. **Provide Your Codebase**: Share the code you want to refactor
2. **Describe the Goal**: Explain what you want to achieve
3. **Specify Constraints**: Mention any limitations or requirements
4. **Let the Skill Work**: It will analyze, plan, and refactor
5. **Review & Iterate**: Validate the output and request adjustments

**Example Command:**
```
"Use the modular program refactor skill to analyze my Flask application
in src/app.py and break it into a clean modular architecture with proper
separation of concerns. Focus on making it maintainable and testable."
```

The skill will activate automatically when you use phrases like:
- "refactor into modular architecture"
- "break down this monolithic code"
- "restructure this program into modules"
- "analyze and modularize this codebase"
- "decompose this application into components"
