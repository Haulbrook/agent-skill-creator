---
name: agent-skill-creator
description: Meta-skill for creating production-ready Claude Code agents and skills. Activates when users want to automate workflows, create agents, or build custom skills. Claude autonomously researches APIs, designs architecture, and implements complete functional code.
---

# Agent Skill Creator

A meta-skill that teaches Claude how to autonomously create complete, production-ready agents and skills for Claude Code.

## When to Activate This Skill

### Trigger Phrases

**Direct Requests:**
- "Create an agent for [objective]"
- "Create a skill for [domain]"
- "Develop an agent to automate [workflow]"
- "Build a skill that [description]"

**Workflow Automation:**
- "Automate this process: [description]"
- "Turn this workflow into an agent"
- "I need to automate [task]"

**Repetitive Task Signals:**
- "Every day I have to [task]"
- "Daily I need to [process]"
- "I repeatedly do [workflow]"
- "This takes X hours every week"

**Advanced Requests:**
- "Create a multi-agent suite for [domain]"
- "Build agents from this transcript"
- "Use the [template-name] template"

### When NOT to Activate

- General programming questions
- Using existing skills (not creating new ones)
- Modifying/debugging existing code without agent context
- Documentation questions about skills

---

## The 5-Phase Creation Pipeline

When activated, Claude executes these phases autonomously:

```
PHASE 1: DISCOVERY
├── Research available APIs for the domain
├── Compare options (free vs paid, rate limits, data quality)
└── DECIDE which API to use with justification

PHASE 2: DESIGN
├── Identify valuable use cases
├── Define analyses and methodologies
└── Specify user interactions and outputs

PHASE 3: ARCHITECTURE
├── Structure folders and files optimally
├── Design Python scripts and modules
├── Plan caching, error handling, performance
└── Apply naming convention: [name]-cskill

PHASE 4: DETECTION
├── Determine 50+ activation keywords
├── Create regex patterns for variations
└── Generate precise skill description

PHASE 5: IMPLEMENTATION
├── Create marketplace.json (MANDATORY FIRST!)
├── Write SKILL.md (comprehensive documentation)
├── Implement functional Python scripts
├── Generate references and configs
├── Create README with instructions
└── Test installation
```

**Output**: Complete skill in subdirectory, ready to install.

---

## Skill Architectures

### Simple Skill (Single Focused Capability)

```
skill-name-cskill/
├── SKILL.md              # Single comprehensive skill file
├── scripts/              # Supporting Python code
├── references/           # Documentation
└── assets/               # Templates, configs
```

*Use when: Single objective, simple workflow, <1000 lines code*

### Complex Skill Suite (Multiple Components)

```
skill-suite-cskill/
├── .claude-plugin/
│   └── marketplace.json  # Organizes multiple skills
├── component-1-cskill/
│   └── SKILL.md          # Specialized sub-skill
├── component-2-cskill/
│   └── SKILL.md          # Another sub-skill
└── shared/               # Shared resources
```

*Use when: Multiple workflows, >2000 lines code, team maintenance*

---

## Naming Convention

**All created skills use the `-cskill` suffix:**

- `pdf-text-extractor-cskill/`
- `financial-analysis-cskill/`
- `weather-monitoring-cskill/`

**Purpose:**
- Clear identification as Claude Skill
- Origin attribution (created by Agent-Skill-Creator)
- Distinguishes from manually created skills

---

## Quality Standards

### Autonomy Principles

Claude must:
- **DECIDE** which API to use (don't ask user unless critical)
- **DEFINE** analyses to perform (based on value)
- **STRUCTURE** optimally (best practices)
- **IMPLEMENT** complete code (no placeholders)

### Code Quality

- Production-ready (no TODOs)
- Robust error handling
- Real configurations (no placeholders)
- Functional scripts (1000+ lines total)
- Comprehensive tests

### Documentation Quality

- Complete SKILL.md (5000+ words)
- References with useful content (3000+ words)
- README with clear instructions
- Working examples

### Questions to Ask (Only if Critical)

- "Prefer free API or paid is ok?"
- "Need historical data for how many years?"
- "Focus on which geography?"

**Rule**: Minimize questions. Infer/decide whenever possible.

---

## marketplace.json Structure

### Single Skill Format

```json
{
  "name": "skill-name-cskill",
  "owner": {
    "name": "Skill Author",
    "email": "author@example.com"
  },
  "metadata": {
    "description": "Clear description of what the skill does",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "skill-plugin",
      "description": "Detailed activation description with trigger phrases",
      "source": "./",
      "skills": ["./"]
    }
  ],
  "activation": {
    "keywords": [
      "primary keyword phrase",
      "secondary keyword",
      "action verb + domain"
    ],
    "patterns": [
      "(?i)(analyze|check|monitor)\\s+(the\\s+)?domain",
      "(?i)domain\\s+(analysis|report|data)"
    ]
  }
}
```

### Multi-Skill Suite Format

```json
{
  "name": "suite-name-cskill",
  "metadata": {
    "description": "Suite description",
    "version": "1.0.0",
    "suite_type": "domain_type"
  },
  "plugins": [
    {
      "name": "component-1-plugin",
      "description": "Component 1 activation description",
      "source": "./component-1-cskill/",
      "skills": ["./SKILL.md"]
    },
    {
      "name": "component-2-plugin",
      "description": "Component 2 activation description",
      "source": "./component-2-cskill/",
      "skills": ["./SKILL.md"]
    }
  ]
}
```

---

## SKILL.md Template

```markdown
---
name: skill-name-cskill
description: One-paragraph description with activation phrases and key functionality.
---

# Skill Name

## Overview
What this skill does and its value proposition.

## Capabilities
- Capability 1: Description
- Capability 2: Description
- Capability 3: Description

## Usage Examples

### Example 1: [Use Case]
```
User: "Example prompt"
Result: What happens
```

## Technical Implementation

### API Integration
Details about API setup, authentication, rate limits.

### Data Processing
How data is fetched, processed, and analyzed.

## Scripts Reference

### script_name.py
Purpose and main functions.

## Configuration
Required environment variables and setup.

## Troubleshooting
Common issues and solutions.
```

---

## Available Templates

### Financial Analysis Template
```
Domain: Finance & Investments
APIs: Alpha Vantage, Yahoo Finance
Analyses: Fundamental, Technical, Portfolio
Time: 15-20 minutes
```

### Climate Analysis Template
```
Domain: Climate & Environmental
APIs: Open-Meteo, NOAA
Analyses: Anomalies, Trends, Seasonal
Time: 20-25 minutes
```

### E-commerce Analytics Template
```
Domain: Business & E-commerce
APIs: Analytics, Payment, Commerce platforms
Analyses: Traffic, Revenue, Cohort, Products
Time: 25-30 minutes
```

---

## Creation Modes

### Single Agent Creation
```
"Create an agent for stock analysis"
→ ./stock-analysis-cskill/
```

### Multi-Agent Suite
```
"Create a financial suite with 4 agents:
fundamental, technical, portfolio, risk"
→ ./financial-suite-cskill/
   ├── fundamental-analysis-cskill/
   ├── technical-analysis-cskill/
   ├── portfolio-management-cskill/
   └── risk-assessment-cskill/
```

### Template-Based Creation
```
"Create agent using financial-analysis template"
→ Uses pre-configured structure, 80% faster
```

### Transcript Processing
```
"Here's a YouTube transcript about analytics,
create agents for all workflows described"
→ Extracts workflows, creates integrated suite
```

### Interactive Mode
```
"Help me create an agent with preview options"
→ Step-by-step wizard with preview and refinement
```

---

## Phase Details

### Phase 1: Discovery

**Objective**: Research and select the best API for the domain.

**Process**:
1. Identify domain requirements
2. Search for available APIs (free and paid)
3. Compare: data quality, rate limits, authentication, cost
4. Select best option with documented justification

**Output**: API decision with rationale

### Phase 2: Design

**Objective**: Define valuable analyses and methodologies.

**Process**:
1. Identify meaningful use cases for the domain
2. Define specific analyses (with methodologies)
3. Specify output formats and visualizations
4. Plan user interaction patterns

**Output**: Analysis specification document

### Phase 3: Architecture

**Objective**: Structure the skill optimally.

**Process**:
1. Determine simple skill vs suite architecture
2. Plan directory structure
3. Design script organization
4. Plan caching and performance optimization
5. Apply `-cskill` naming convention

**Output**: Architecture decision with folder structure

### Phase 4: Detection

**Objective**: Create reliable activation system.

**Process**:
1. Generate 50+ keywords covering variations
2. Create regex patterns for flexible matching
3. Write precise skill description
4. Define positive and negative test queries

**Output**: Activation configuration

### Phase 5: Implementation

**Objective**: Create complete, production-ready skill.

**Mandatory Order**:
1. **marketplace.json** (FIRST - enables skill recognition)
2. **SKILL.md** (comprehensive documentation)
3. **Python scripts** (functional, tested)
4. **References** (useful documentation)
5. **README.md** (installation instructions)
6. **Test installation**

**Output**: Complete skill directory

---

## Activation Patterns Library

### Action + Domain Patterns
```regex
(?i)(create|build|develop|make)\s+(an?\s+)?(agent|skill)\s+(for|to|that)
(?i)(analyze|check|monitor|track)\s+(the\s+)?DOMAIN
(?i)DOMAIN\s+(analysis|report|data|metrics)
```

### Automation Patterns
```regex
(?i)(automate|automation)\s+(this\s+)?(workflow|process|task)
(?i)(every day|daily|repeatedly)\s+(I|we)\s+(have to|need to|do)
(?i)(turn|convert|transform)\s+(this\s+)?(process|workflow)\s+into\s+(an?\s+)?agent
```

### Request Patterns
```regex
(?i)need\s+to\s+automate
(?i)(create|need)\s+a\s+custom\s+skill
(?i)I\s+(repeatedly|constantly|always)\s+(need to|have to)
```

---

## Directory Structure Example

```
stock-analyzer-cskill/
├── .claude-plugin/
│   └── marketplace.json
├── SKILL.md
├── README.md
├── DECISIONS.md
├── scripts/
│   ├── __init__.py
│   ├── api_client.py
│   ├── data_processor.py
│   ├── analyzer.py
│   └── reporter.py
├── references/
│   ├── api-documentation.md
│   ├── methodology.md
│   └── troubleshooting.md
├── assets/
│   ├── config.json
│   └── templates/
└── tests/
    ├── test_api.py
    ├── test_analyzer.py
    └── test_integration.py
```

---

## Checklist Before Completion

### Structure
- [ ] marketplace.json exists and is valid
- [ ] SKILL.md is comprehensive (5000+ words)
- [ ] README.md has clear instructions
- [ ] All scripts are functional

### Code Quality
- [ ] No TODOs or placeholders
- [ ] Error handling implemented
- [ ] Real API endpoints configured
- [ ] Tests included

### Documentation
- [ ] Activation keywords defined (50+)
- [ ] Regex patterns tested
- [ ] Examples provided
- [ ] Troubleshooting section included

### Testing
- [ ] Scripts execute without errors
- [ ] API calls work (or mock correctly)
- [ ] Skill activates on test queries

---

## Requirements Extraction

When user describes workflow vaguely, extract:

**From user input**:
- Domain (finance? weather? e-commerce?)
- Data source (API mentioned? need research?)
- Main tasks (download? analyze? compare?)
- Frequency (daily? weekly? on-demand?)
- Current time spent (for ROI calculation)

**Enhanced Analysis**:
- Multi-agent detection (look for "suite", "multiple", "separate")
- Transcript analysis (detect video/document input)
- Template matching (identify domain-specific templates)
- Integration needs (should agents communicate?)

---

## Cross-Platform Export

Skills can be exported for:

- **Claude Code**: Native installation
- **Claude Desktop**: .zip upload
- **claude.ai Web**: .zip upload
- **Claude API**: Programmatic integration

Use `scripts/export_utils.py` for automated packaging.

---

## Success Metrics

A well-created skill should have:

- **Activation Reliability**: >99%
- **False Positive Rate**: <1%
- **Code Coverage**: 1000+ lines
- **Documentation**: 5000+ words
- **Test Coverage**: Comprehensive

---

## Reference Documentation

For detailed guidance, see:

- `references/phase1-discovery.md` - API research guide
- `references/phase2-design.md` - Analysis design
- `references/phase3-architecture.md` - Structure planning
- `references/phase4-detection.md` - Activation system
- `references/phase5-implementation.md` - Implementation details
- `references/activation-patterns-guide.md` - Pattern library
- `references/quality-standards.md` - Quality checklist
- `docs/CLAUDE_SKILLS_ARCHITECTURE.md` - Architecture guide
