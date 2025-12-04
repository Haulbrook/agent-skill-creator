# Reasoning Optimizer Skill

A comprehensive code analysis and reconstruction framework that evaluates programs against structured reasoning principles, identifies gaps in logical flow, and rebuilds implementations using systematic 5-Phase methodology.

## Overview

The Reasoning Optimizer skill helps you:

- **Analyze** existing code for reasoning quality and methodology gaps
- **Score** code against the 5-Phase Reasoning Model (0-100)
- **Rebuild** code with proper reasoning structure
- **Create checkpoints** for consistent quality throughout development
- **Track progress** with detailed reports and metrics

## Quick Start

### Installation

Register the skill with Claude Code:

```bash
claude plugin marketplace add ./reasoning-optimizer-cskill
```

### Basic Usage

**Analyze code reasoning:**
```
Analyze this code for reasoning quality:
[paste your code or file path]
```

**Get a reasoning score:**
```
Score this function's reasoning:
def my_function():
    ...
```

**Rebuild with proper reasoning:**
```
Rebuild this code with proper reasoning methodology:
[paste code]
```

**Create a checkpoint:**
```
Create a post-development checkpoint for the authentication module
```

## The 5-Phase Reasoning Model

Every well-reasoned program demonstrates these five phases:

| Phase | Focus | Key Questions |
|-------|-------|---------------|
| **1. Comprehension** | Understanding | What problem are we solving? |
| **2. Strategy** | Planning | How will we approach this? |
| **3. Execution** | Implementation | Are we following the plan? |
| **4. Review** | Verification | Does it meet requirements? |
| **5. Refinement** | Optimization | Is it polished and efficient? |

### Scoring

Each phase contributes 20 points to the total score:

| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | A | Excellent - Production ready |
| 80-89 | B | Good - Minor improvements suggested |
| 70-79 | C | Adequate - Improvements recommended |
| 60-69 | D | Needs Work - Should improve before release |
| 0-59 | F | Poor - Requires reconstruction |

## Features

### 1. Reasoning Gap Analysis

Identifies where code reasoning breaks down:

```markdown
## Reasoning Analysis Report

### Overall Score: 62/100 (Grade: D)

### Issues Found
- Phase 1: Missing module documentation
- Phase 2: No approach documentation
- Phase 4: Limited edge case handling

### Priority Recommendations
1. Add comprehensive documentation
2. Document the chosen approach
3. Add input validation and edge case handling
```

### 2. Code Reconstruction

Rebuilds code with proper reasoning methodology:

- Extracts original intent
- Re-applies all 5 phases
- Adds missing documentation
- Improves structure
- Documents decisions

### 3. Checkpoint System

Four checkpoint types for development lifecycle:

| Checkpoint | When | Minimum Score |
|------------|------|---------------|
| Pre-Development | Before coding | N/A |
| Mid-Development | During implementation | 50 |
| Post-Development | Before review | 70 |
| Release | Before deployment | 85 |

### 4. Integration Options

#### CI/CD Integration

Add reasoning gates to your pipeline:

```yaml
# Example: GitHub Actions
- name: Analyze Code Reasoning
  run: |
    python -m reasoning_optimizer analyze \
      --files "$(git diff --name-only origin/main)" \
      --min-score 70
```

#### Pre-commit Hook

```bash
# Validate reasoning before commit
reasoning_optimizer analyze --threshold 60
```

## Project Structure

```
reasoning-optimizer-cskill/
├── SKILL.md                    # Full skill specification
├── README.md                   # This file
├── .claude-plugin/
│   └── marketplace.json        # Activation configuration
├── scripts/
│   ├── main.py                # Entry point
│   ├── analyzers/             # Analysis components
│   │   ├── reasoning_analyzer.py
│   │   ├── structure_analyzer.py
│   │   └── documentation_analyzer.py
│   ├── rebuilders/            # Reconstruction components
│   │   └── code_rebuilder.py
│   └── checkpoints/           # Checkpoint management
│       └── checkpoint_manager.py
├── assets/
│   └── templates/             # Checkpoint templates
│       ├── pre_checkpoint.md
│       ├── post_checkpoint.md
│       └── release_checkpoint.md
└── references/                # Supporting documentation
```

## Activation Keywords

The skill activates automatically for phrases like:

- "analyze reasoning", "reasoning analysis"
- "optimize code reasoning", "improve reasoning"
- "reasoning score", "score this code"
- "rebuild with reasoning", "reconstruct code"
- "create checkpoint", "quality checkpoint"
- "find reasoning gaps", "reasoning issues"

## Example Workflow

### 1. Analyze Existing Code

```
User: Analyze the reasoning in my data_processor.py file

Claude: Analyzing data_processor.py for reasoning quality...

## Reasoning Analysis Report

### Overall Score: 45/100 (Grade: F)

### Phase-by-Phase Assessment
| Phase | Score | Status |
|-------|-------|--------|
| Comprehension | 8/20 | WARN |
| Strategy | 5/20 | WARN |
| Execution | 15/20 | OK |
| Review | 10/20 | WARN |
| Refinement | 7/20 | WARN |

### Priority Recommendations
1. Add module documentation explaining purpose
2. Document why this approach was chosen
3. Add edge case handling for empty inputs
```

### 2. Rebuild with Reasoning

```
User: Rebuild data_processor.py with proper reasoning

Claude: Reconstructing with 5-Phase Reasoning Model...

Before Score: 45/100
After Score: 87/100

Changes Applied:
1. Added module documentation with requirements
2. Added strategy documentation section
3. Added function docstrings
4. Added input validation
5. Added edge case handling
```

### 3. Create Checkpoint

```
User: Create a post-development checkpoint

Claude: Creating post-development checkpoint...

## Post-Development Checkpoint

Status: PASS
Reasoning Score: 87/100 (Grade: B)

All requirements implemented
Edge cases handled
Documentation complete

Ready for code review.
```

## Best Practices

1. **Run analysis early** - Catch reasoning gaps before they accumulate
2. **Use checkpoints** - Create checkpoints at key development milestones
3. **Target 80+** - Aim for grade B or higher for production code
4. **Document decisions** - Use DECISION: comments for non-obvious choices
5. **Iterate** - Use the rebuild feature to improve low-scoring code

## Support

For questions or issues:
- Review the full [SKILL.md](./SKILL.md) specification
- Check the [assets/templates](./assets/templates) for checkpoint templates
- Refer to the [scripts](./scripts) for implementation details

## Version

- **Version**: 1.0.0
- **Created**: 2025-12-04
- **Compatibility**: Claude Code 1.0+
