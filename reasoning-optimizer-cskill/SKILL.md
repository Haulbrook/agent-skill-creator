# Reasoning Optimizer Skill

A comprehensive code analysis and reconstruction framework that evaluates programs against structured reasoning principles, identifies gaps in logical flow, and rebuilds code using systematic methodology. This skill acts as quality checkpoints ensuring consistent reasoning efficiency across all projects.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Capabilities](#core-capabilities)
3. [The Reasoning Assessment Framework](#the-reasoning-assessment-framework)
4. [Analysis Engine](#analysis-engine)
5. [Reconstruction Protocol](#reconstruction-protocol)
6. [Checkpoint System](#checkpoint-system)
7. [Integration Patterns](#integration-patterns)
8. [Usage Examples](#usage-examples)
9. [Quality Metrics](#quality-metrics)
10. [Quick Reference](#quick-reference)

---

## Overview

### Purpose

The Reasoning Optimizer skill transforms implicit, ad-hoc code into explicitly reasoned, verifiable implementations. It applies the 5-Phase Reasoning Model to analyze existing code, identify where reasoning breaks down, and systematically rebuild it with proper decomposition, planning, execution, review, and refinement.

### Why This Skill Matters

Most code fails not from syntax errors but from **reasoning gaps**:
- Incomplete problem understanding
- Missing edge case consideration
- Unclear solution strategy
- Absent self-verification
- No iterative refinement

This skill provides:
- **Diagnostic Analysis**: Identifies exactly where reasoning fails
- **Structured Reconstruction**: Rebuilds code with proper methodology
- **Quality Checkpoints**: Creates verification gates for future projects
- **Transferable Patterns**: Documents reasoning for reuse

### Target Use Cases

1. **Code Review Enhancement**: Analyze existing code for reasoning gaps
2. **Refactoring Guidance**: Rebuild legacy code with proper structure
3. **Project Checkpoints**: Create quality gates for ongoing development
4. **Team Standardization**: Establish reasoning standards across projects
5. **Self-Improvement**: Enable Claude to optimize its own outputs

---

## Core Capabilities

### Capability 1: Reasoning Gap Analysis

Evaluates code against the 5-Phase Reasoning Model to identify where logical flow breaks down.

**Input**: Code file, function, or project
**Output**: Detailed reasoning assessment report

```markdown
## Reasoning Gap Analysis Report

### Overall Reasoning Score: [X/100]

### Phase-by-Phase Assessment

#### Phase 1: Comprehension [Score: X/20]
- Problem Definition: [Clear/Partial/Missing]
- Requirements Identified: [X/Y requirements documented]
- Constraints Noted: [Yes/No]
- Gaps Found:
  - [Gap 1]
  - [Gap 2]

#### Phase 2: Strategy [Score: X/20]
- Approach Selection: [Documented/Implicit/Missing]
- Alternatives Considered: [Yes/No]
- Trade-offs Evaluated: [Yes/No]
- Gaps Found:
  - [Gap 1]

#### Phase 3: Execution [Score: X/20]
- Plan Adherence: [Strong/Weak/None]
- Step Documentation: [Present/Partial/Absent]
- Code-Plan Alignment: [X%]
- Gaps Found:
  - [Gap 1]

#### Phase 4: Review [Score: X/20]
- Requirements Verification: [Complete/Partial/None]
- Edge Case Coverage: [X/Y cases handled]
- Self-Check Evidence: [Present/Absent]
- Gaps Found:
  - [Gap 1]

#### Phase 5: Refinement [Score: X/20]
- Iteration Evidence: [Yes/No]
- Optimization Applied: [Yes/No]
- Polish Level: [High/Medium/Low]
- Gaps Found:
  - [Gap 1]

### Priority Recommendations
1. [Highest priority fix]
2. [Second priority fix]
3. [Third priority fix]
```

### Capability 2: Code Reconstruction

Rebuilds code following the complete reasoning methodology.

**Process**:
1. Extract original intent from existing code
2. Re-apply Phase 1 (Comprehension) properly
3. Re-apply Phase 2 (Strategy) with documented alternatives
4. Re-apply Phase 3 (Execution) with step-by-step construction
5. Re-apply Phase 4 (Review) with checklist verification
6. Re-apply Phase 5 (Refinement) with optimization

**Output**: Reconstructed code with reasoning documentation

### Capability 3: Checkpoint Creation

Generates reusable quality checkpoints for consistent project standards.

**Checkpoint Types**:
- **Pre-Development Checkpoint**: Requirements and strategy verification
- **Mid-Development Checkpoint**: Execution progress validation
- **Post-Development Checkpoint**: Complete quality assessment
- **Release Checkpoint**: Final verification before deployment

### Capability 4: Pattern Documentation

Extracts and documents reasoning patterns for future reuse.

**Pattern Categories**:
- Problem decomposition patterns
- Solution strategy patterns
- Error handling patterns
- Edge case coverage patterns
- Optimization patterns

---

## The Reasoning Assessment Framework

### The 5-Phase Reasoning Model

Every well-reasoned program demonstrates these five phases:

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: COMPREHENSION          [CONCEPTUAL]                   │
│  ├─ Parse the request                                           │
│  ├─ Identify requirements                                       │
│  ├─ Recognize constraints                                       │
│  └─ Summarize understanding                                     │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2: STRATEGY               [CONCEPTUAL]                   │
│  ├─ Brainstorm approaches                                       │
│  ├─ Evaluate trade-offs                                         │
│  ├─ Select optimal path                                         │
│  └─ Create execution plan                                       │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3: EXECUTION              [TECHNICAL]                    │
│  ├─ Implement step-by-step                                      │
│  ├─ Follow the plan                                             │
│  ├─ Document decisions                                          │
│  └─ Produce initial output                                      │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 4: REVIEW                 [CONCEPTUAL]                   │
│  ├─ Verify against requirements                                 │
│  ├─ Check edge cases                                            │
│  ├─ Identify gaps or errors                                     │
│  └─ Assess completeness                                         │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 5: REFINEMENT             [TECHNICAL]                    │
│  ├─ Address identified issues                                   │
│  ├─ Optimize solution                                           │
│  ├─ Polish output                                               │
│  └─ Final verification                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Phase Assessment Criteria

#### Phase 1: Comprehension Assessment

**Indicators of Good Comprehension**:
- Clear problem statement in comments or documentation
- Explicit input/output specifications
- Documented constraints and limitations
- Evidence of requirement parsing

**Red Flags**:
- Code starts immediately without context
- Unclear variable purposes
- Missing documentation of intent
- Ambiguous function signatures

**Assessment Questions**:
- [ ] Is the problem clearly defined?
- [ ] Are inputs and outputs specified?
- [ ] Are constraints documented?
- [ ] Can a new reader understand the intent?

#### Phase 2: Strategy Assessment

**Indicators of Good Strategy**:
- Comments explaining approach choice
- Evidence of alternative consideration
- Trade-off documentation
- Clear architectural decisions

**Red Flags**:
- No explanation of "why this approach"
- Copy-paste patterns without adaptation
- Over-engineering without justification
- Under-engineering for complex problems

**Assessment Questions**:
- [ ] Is the chosen approach documented?
- [ ] Were alternatives considered?
- [ ] Are trade-offs acknowledged?
- [ ] Does the structure match the problem?

#### Phase 3: Execution Assessment

**Indicators of Good Execution**:
- Code follows a logical progression
- Each section maps to a clear purpose
- Decision points are documented
- Consistent patterns throughout

**Red Flags**:
- Spaghetti code flow
- Unexplained magic numbers/strings
- Inconsistent styling/patterns
- Duplicated logic

**Assessment Questions**:
- [ ] Does code follow a clear plan?
- [ ] Are decisions documented inline?
- [ ] Is the progression logical?
- [ ] Is the code consistent?

#### Phase 4: Review Assessment

**Indicators of Good Review**:
- Edge case handling present
- Input validation implemented
- Error handling comprehensive
- Tests or assertions included

**Red Flags**:
- No edge case consideration
- Missing input validation
- Generic/unhelpful error handling
- No verification mechanism

**Assessment Questions**:
- [ ] Are edge cases handled?
- [ ] Is input validated?
- [ ] Are errors handled properly?
- [ ] Is there verification logic?

#### Phase 5: Refinement Assessment

**Indicators of Good Refinement**:
- Optimized algorithms where needed
- Clean, readable final code
- Performance considerations addressed
- No obvious improvements left

**Red Flags**:
- Obvious inefficiencies
- TODO comments for known issues
- Incomplete implementations
- Rough/unpolished output

**Assessment Questions**:
- [ ] Is the code optimized appropriately?
- [ ] Is it clean and readable?
- [ ] Are there obvious improvements remaining?
- [ ] Is this production-ready?

---

## Analysis Engine

### Automated Analysis Process

```
┌──────────────────────────────────────────────────────────────┐
│                    ANALYSIS ENGINE                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  INPUT: Source Code / Function / Project                      │
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │   Parse     │───►│  Extract    │───►│  Evaluate   │       │
│  │   Code      │    │  Intent     │    │  Phases     │       │
│  └─────────────┘    └─────────────┘    └─────────────┘       │
│         │                 │                  │                │
│         ▼                 ▼                  ▼                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │  Structure  │    │  Inferred   │    │  Phase      │       │
│  │  Analysis   │    │  Purpose    │    │  Scores     │       │
│  └─────────────┘    └─────────────┘    └─────────────┘       │
│         │                 │                  │                │
│         └────────────────┼──────────────────┘                │
│                          ▼                                    │
│                 ┌─────────────────┐                          │
│                 │  Gap Analysis   │                          │
│                 │  Report         │                          │
│                 └─────────────────┘                          │
│                          │                                    │
│                          ▼                                    │
│                 ┌─────────────────┐                          │
│                 │ Recommendations │                          │
│                 └─────────────────┘                          │
│                                                               │
│  OUTPUT: Detailed Reasoning Assessment                        │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Analysis Categories

#### 1. Structural Analysis

Examines code organization and architecture:

```python
STRUCTURAL_CHECKS = {
    "modularity": {
        "description": "Code is organized into logical units",
        "indicators": ["function boundaries", "class structure", "module separation"],
        "weight": 15
    },
    "cohesion": {
        "description": "Related code is grouped together",
        "indicators": ["single responsibility", "logical grouping", "clear boundaries"],
        "weight": 15
    },
    "coupling": {
        "description": "Dependencies are minimized and explicit",
        "indicators": ["import clarity", "dependency injection", "interface design"],
        "weight": 10
    }
}
```

#### 2. Documentation Analysis

Evaluates documentation quality and completeness:

```python
DOCUMENTATION_CHECKS = {
    "purpose_clarity": {
        "description": "Overall purpose is clearly stated",
        "indicators": ["module docstring", "README", "header comments"],
        "weight": 10
    },
    "function_docs": {
        "description": "Functions are documented",
        "indicators": ["docstrings", "parameter descriptions", "return descriptions"],
        "weight": 10
    },
    "decision_docs": {
        "description": "Important decisions are explained",
        "indicators": ["inline comments", "DECISIONS.md", "architecture notes"],
        "weight": 10
    }
}
```

#### 3. Logic Flow Analysis

Assesses the reasoning flow through code:

```python
LOGIC_FLOW_CHECKS = {
    "sequence_clarity": {
        "description": "Execution order is clear",
        "indicators": ["linear flow", "clear branching", "minimal jumps"],
        "weight": 10
    },
    "decision_points": {
        "description": "Conditionals are well-reasoned",
        "indicators": ["clear conditions", "complete branches", "documented logic"],
        "weight": 10
    },
    "error_paths": {
        "description": "Error handling is comprehensive",
        "indicators": ["try/catch blocks", "validation", "graceful degradation"],
        "weight": 10
    }
}
```

#### 4. Completeness Analysis

Checks for missing elements:

```python
COMPLETENESS_CHECKS = {
    "edge_cases": {
        "description": "Edge cases are handled",
        "indicators": ["empty input", "boundary values", "null checks"],
        "weight": 15
    },
    "error_handling": {
        "description": "Errors are properly managed",
        "indicators": ["specific exceptions", "helpful messages", "recovery logic"],
        "weight": 10
    },
    "input_validation": {
        "description": "Inputs are validated",
        "indicators": ["type checks", "range validation", "format verification"],
        "weight": 10
    }
}
```

### Scoring Algorithm

```python
def calculate_reasoning_score(analysis_results):
    """
    Calculate overall reasoning score from analysis results.

    Scoring breakdown:
    - Phase 1 (Comprehension): 20 points
    - Phase 2 (Strategy): 20 points
    - Phase 3 (Execution): 20 points
    - Phase 4 (Review): 20 points
    - Phase 5 (Refinement): 20 points

    Total: 100 points
    """
    phase_scores = {
        "comprehension": calculate_phase_score(analysis_results, [
            "purpose_clarity",
            "input_output_spec",
            "constraint_documentation"
        ]),
        "strategy": calculate_phase_score(analysis_results, [
            "approach_documentation",
            "alternative_consideration",
            "tradeoff_evaluation"
        ]),
        "execution": calculate_phase_score(analysis_results, [
            "plan_adherence",
            "decision_documentation",
            "code_consistency"
        ]),
        "review": calculate_phase_score(analysis_results, [
            "requirements_verification",
            "edge_case_coverage",
            "self_check_evidence"
        ]),
        "refinement": calculate_phase_score(analysis_results, [
            "optimization_applied",
            "code_polish",
            "completeness"
        ])
    }

    return {
        "overall": sum(phase_scores.values()),
        "phases": phase_scores,
        "grade": get_grade(sum(phase_scores.values()))
    }

def get_grade(score):
    if score >= 90: return "A - Excellent Reasoning"
    if score >= 80: return "B - Good Reasoning"
    if score >= 70: return "C - Adequate Reasoning"
    if score >= 60: return "D - Needs Improvement"
    return "F - Significant Reasoning Gaps"
```

---

## Reconstruction Protocol

### The Rebuild Process

When code fails the reasoning assessment, apply this reconstruction protocol:

```
┌──────────────────────────────────────────────────────────────┐
│                 RECONSTRUCTION PROTOCOL                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  STEP 1: EXTRACT ORIGINAL INTENT                             │
│  ├─ Read existing code thoroughly                            │
│  ├─ Identify what it's trying to accomplish                  │
│  ├─ Note any implicit requirements                           │
│  └─ Document extracted understanding                         │
│                                                               │
│  STEP 2: RE-APPLY COMPREHENSION PHASE                        │
│  ├─ Write clear problem statement                            │
│  ├─ List all requirements (explicit + implicit)              │
│  ├─ Document constraints                                     │
│  └─ Create specification document                            │
│                                                               │
│  STEP 3: RE-APPLY STRATEGY PHASE                             │
│  ├─ Brainstorm 2-3 alternative approaches                    │
│  ├─ Evaluate each against requirements                       │
│  ├─ Document trade-offs                                      │
│  ├─ Select optimal approach with justification               │
│  └─ Create detailed execution plan                           │
│                                                               │
│  STEP 4: RE-APPLY EXECUTION PHASE                            │
│  ├─ Implement step-by-step following plan                    │
│  ├─ Document decisions at each step                          │
│  ├─ Maintain code-plan alignment                             │
│  └─ Produce well-structured initial implementation           │
│                                                               │
│  STEP 5: RE-APPLY REVIEW PHASE                               │
│  ├─ Verify against all requirements                          │
│  ├─ Test edge cases systematically                           │
│  ├─ Check for security/performance issues                    │
│  └─ Create review checklist results                          │
│                                                               │
│  STEP 6: RE-APPLY REFINEMENT PHASE                           │
│  ├─ Address all identified issues                            │
│  ├─ Optimize where beneficial                                │
│  ├─ Polish code for readability                              │
│  └─ Final verification pass                                  │
│                                                               │
│  OUTPUT: Fully Reasoned, Documented Code                     │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Reconstruction Templates

#### Intent Extraction Template

```markdown
## Original Intent Extraction

### Code Location
- File: [path]
- Function/Class: [name]
- Lines: [start-end]

### Observed Behavior
[What the code currently does]

### Inferred Purpose
[What it's trying to accomplish]

### Implicit Requirements Found
1. [Requirement discovered from code behavior]
2. [Another implicit requirement]

### Missing Elements Identified
1. [Something the code should handle but doesn't]
2. [Another missing element]

### Constraints Inferred
1. [Constraint from context]
2. [Another constraint]
```

#### Strategy Documentation Template

```markdown
## Solution Strategy Documentation

### Problem Summary
[One paragraph problem description]

### Approach Options

#### Option A: [Name]
- **Description**: [How it works]
- **Pros**: [Advantages]
- **Cons**: [Disadvantages]
- **Complexity**: O([time]) / O([space])
- **Fit Score**: [X/10]

#### Option B: [Name]
- **Description**: [How it works]
- **Pros**: [Advantages]
- **Cons**: [Disadvantages]
- **Complexity**: O([time]) / O([space])
- **Fit Score**: [X/10]

### Selected Approach
**Choice**: Option [X]
**Justification**: [Why this is best for the requirements]

### Execution Plan
1. [First major step]
   - [Sub-step 1a]
   - [Sub-step 1b]
2. [Second major step]
   - [Sub-step 2a]
3. [Continue...]

### Risk Mitigation
- **Risk 1**: [Description] → **Mitigation**: [How to handle]
- **Risk 2**: [Description] → **Mitigation**: [How to handle]
```

#### Reconstructed Code Template

```python
"""
Module: [name]
Purpose: [clear purpose statement]

Requirements Addressed:
- REQ-1: [requirement description]
- REQ-2: [requirement description]

Constraints:
- [constraint 1]
- [constraint 2]

Approach: [brief approach description]
Selected because: [justification]
"""

# =============================================================================
# SECTION 1: [Purpose]
# Plan Step: [corresponding plan step]
# =============================================================================

def function_name(param1: Type, param2: Type) -> ReturnType:
    """
    [Clear description of what this function does]

    Args:
        param1: [description]
        param2: [description]

    Returns:
        [description of return value]

    Raises:
        [ExceptionType]: [when this is raised]

    Edge Cases Handled:
        - [edge case 1]: [how handled]
        - [edge case 2]: [how handled]
    """
    # DECISION: [explain any non-obvious choices]

    # Step 1: [description]
    # ... implementation ...

    # Step 2: [description]
    # ... implementation ...

    return result


# =============================================================================
# SECTION 2: [Purpose]
# Plan Step: [corresponding plan step]
# =============================================================================

# ... continue with same pattern ...
```

---

## Checkpoint System

### Checkpoint Types

#### 1. Pre-Development Checkpoint

Run before starting implementation to ensure requirements are clear.

```markdown
## Pre-Development Checkpoint

### Date: [YYYY-MM-DD]
### Project/Feature: [Name]

### Requirements Verification
- [ ] All requirements are documented
- [ ] Requirements are unambiguous
- [ ] Acceptance criteria defined
- [ ] Constraints identified

### Strategy Verification
- [ ] Approach is selected and documented
- [ ] Alternatives were considered
- [ ] Trade-offs are understood
- [ ] Execution plan exists

### Ready to Proceed
- [ ] All checks pass
- [ ] Blockers resolved
- [ ] Team aligned (if applicable)

### Sign-off
- Verified by: [Name/System]
- Timestamp: [DateTime]
```

#### 2. Mid-Development Checkpoint

Run during implementation to catch drift.

```markdown
## Mid-Development Checkpoint

### Date: [YYYY-MM-DD]
### Completion: [X%]

### Plan Adherence
- [ ] Following original plan
- [ ] Deviations documented
- [ ] Still aligned with requirements

### Code Quality
- [ ] Code is readable
- [ ] Decisions documented
- [ ] No technical debt accumulating

### Issues/Blockers
- [Issue 1]: [Status]
- [Issue 2]: [Status]

### Adjustments Needed
- [Adjustment 1]
- [Adjustment 2]

### Continue/Adjust/Stop
- Decision: [Continue/Adjust/Stop]
- Reason: [Explanation]
```

#### 3. Post-Development Checkpoint

Run after implementation before review.

```markdown
## Post-Development Checkpoint

### Date: [YYYY-MM-DD]
### Feature: [Name]

### Completeness Check
- [ ] All requirements implemented
- [ ] All edge cases handled
- [ ] Error handling complete
- [ ] Documentation complete

### Quality Check
- [ ] Code follows standards
- [ ] No obvious bugs
- [ ] Performance acceptable
- [ ] Security reviewed

### Test Coverage
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Edge case tests pass

### Ready for Review
- [ ] All checks pass
- [ ] Self-review completed
- [ ] Documentation updated

### Reasoning Score: [X/100]
```

#### 4. Release Checkpoint

Final verification before deployment.

```markdown
## Release Checkpoint

### Version: [X.Y.Z]
### Date: [YYYY-MM-DD]

### Final Verification
- [ ] All features complete
- [ ] All tests passing
- [ ] Documentation current
- [ ] Change log updated

### Quality Gates
- [ ] Code review approved
- [ ] QA sign-off
- [ ] Performance benchmarks met
- [ ] Security scan passed

### Reasoning Assessment
- Overall Score: [X/100]
- Phase Scores: [breakdown]
- Grade: [A-F]

### Release Approval
- Approved by: [Name]
- Timestamp: [DateTime]
- Notes: [Any notes]
```

### Checkpoint Automation

```python
class CheckpointManager:
    """Manages reasoning checkpoints throughout development."""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.checkpoints = []

    def create_checkpoint(
        self,
        checkpoint_type: str,
        code_path: str = None
    ) -> dict:
        """
        Create a checkpoint with automatic analysis.

        Args:
            checkpoint_type: "pre", "mid", "post", or "release"
            code_path: Path to code for analysis (optional)

        Returns:
            Checkpoint report dictionary
        """
        checkpoint = {
            "type": checkpoint_type,
            "timestamp": datetime.now().isoformat(),
            "project": self.project_path,
            "status": "pending"
        }

        if code_path:
            analysis = self.analyze_code(code_path)
            checkpoint["reasoning_score"] = analysis["score"]
            checkpoint["phase_scores"] = analysis["phases"]
            checkpoint["issues"] = analysis["issues"]

        self.checkpoints.append(checkpoint)
        return checkpoint

    def validate_checkpoint(self, checkpoint: dict) -> bool:
        """Validate checkpoint passes all gates."""
        required_score = {
            "pre": 0,  # No code yet
            "mid": 50,
            "post": 70,
            "release": 85
        }

        if "reasoning_score" in checkpoint:
            min_score = required_score[checkpoint["type"]]
            return checkpoint["reasoning_score"] >= min_score

        return True  # Manual checkpoints pass by default
```

---

## Integration Patterns

### Pattern 1: IDE Integration

Add reasoning assessment to development workflow:

```python
# .claude/hooks/pre-commit
"""
Pre-commit hook for reasoning validation.
Blocks commits that don't meet reasoning thresholds.
"""

def pre_commit_check():
    staged_files = get_staged_python_files()

    for file_path in staged_files:
        analysis = analyze_file_reasoning(file_path)

        if analysis["score"] < 60:
            print(f"BLOCKED: {file_path}")
            print(f"  Reasoning Score: {analysis['score']}/100")
            print(f"  Issues:")
            for issue in analysis["issues"][:3]:
                print(f"    - {issue}")
            return False

    return True
```

### Pattern 2: CI/CD Integration

Add reasoning gates to pipeline:

```yaml
# .github/workflows/reasoning-check.yml
name: Reasoning Quality Check

on: [pull_request]

jobs:
  reasoning-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Analyze Changed Files
        run: |
          python -m reasoning_optimizer analyze \
            --files "$(git diff --name-only origin/main)" \
            --min-score 70 \
            --output report.md

      - name: Post Report
        uses: actions/github-script@v5
        with:
          script: |
            const report = fs.readFileSync('report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });

      - name: Enforce Quality Gate
        run: |
          score=$(cat report.md | grep "Overall Score" | grep -oP '\d+')
          if [ $score -lt 70 ]; then
            echo "Reasoning score below threshold"
            exit 1
          fi
```

### Pattern 3: Claude Direct Integration

For Claude to self-optimize its outputs:

```markdown
## Self-Optimization Protocol

When generating code, Claude should:

1. **Before writing code**:
   - Apply Phase 1 (Comprehension) explicitly
   - Apply Phase 2 (Strategy) with documentation
   - Create execution plan

2. **While writing code**:
   - Follow Phase 3 (Execution) methodology
   - Document decisions inline
   - Maintain plan alignment

3. **After writing code**:
   - Apply Phase 4 (Review) checklist
   - Apply Phase 5 (Refinement) as needed
   - Self-score the output

4. **If score < 80**:
   - Identify gaps
   - Re-apply weak phases
   - Iterate until threshold met
```

### Pattern 4: Project Template Integration

Include reasoning structure in project scaffolding:

```
project-template/
├── REASONING.md              # Project reasoning documentation
├── docs/
│   ├── REQUIREMENTS.md       # Phase 1 documentation
│   ├── ARCHITECTURE.md       # Phase 2 documentation
│   └── DECISIONS.md          # Ongoing decision log
├── checkpoints/
│   ├── pre-dev/              # Pre-development checkpoints
│   ├── mid-dev/              # Mid-development checkpoints
│   └── release/              # Release checkpoints
└── .reasoning/
    └── config.yml            # Reasoning optimizer config
```

---

## Usage Examples

### Example 1: Analyzing Existing Code

**Input Command**:
```
Analyze this code for reasoning quality:
[paste code or file path]
```

**Output**:
```markdown
## Reasoning Analysis Report

### Code: `utils/data_processor.py`

### Overall Score: 45/100 (Grade: F)

### Phase Analysis

#### Phase 1: Comprehension - 8/20
**Issues**:
- No module docstring explaining purpose
- Function parameters lack documentation
- Input/output specifications missing
- Constraints not documented

**Evidence**:
```python
def process(data):  # What is 'data'? What does 'process' mean?
    result = []
    for item in data:
        # ... 50 lines of code ...
    return result
```

#### Phase 2: Strategy - 5/20
**Issues**:
- No explanation of chosen approach
- No evidence of alternative consideration
- No trade-off documentation

#### Phase 3: Execution - 15/20
**Strengths**:
- Code is generally consistent
- Logical flow is present
**Issues**:
- Some unexplained magic numbers
- Missing decision comments

#### Phase 4: Review - 10/20
**Issues**:
- Limited edge case handling
- Missing input validation
- Generic error handling

#### Phase 5: Refinement - 7/20
**Issues**:
- Some obvious inefficiencies
- Code could be cleaner
- TODOs present

### Priority Recommendations
1. Add comprehensive documentation (Phase 1)
2. Document the approach and why it was chosen (Phase 2)
3. Add input validation and edge case handling (Phase 4)
4. Address TODOs and optimize obvious inefficiencies (Phase 5)
```

### Example 2: Rebuilding Code

**Input Command**:
```
Rebuild this function with proper reasoning:
def calc(x, y, op):
    if op == '+': return x + y
    if op == '-': return x - y
    if op == '*': return x * y
    if op == '/': return x / y
```

**Output**:
```markdown
## Reconstruction Report

### Original Intent
A calculator function that performs basic arithmetic operations.

### Issues with Original
- No documentation
- No input validation
- Division by zero not handled
- Invalid operator not handled
- No type hints

### Reconstructed Code

```python
"""
Calculator module providing basic arithmetic operations.

Requirements:
- Support +, -, *, / operations
- Handle invalid inputs gracefully
- Return meaningful error messages

Approach: Simple dispatch with validation
Selected because: Operations are straightforward; complexity not needed
"""

from typing import Union

# Type alias for numeric inputs
Number = Union[int, float]

# Valid operations mapping
OPERATIONS = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
}


def calculate(x: Number, y: Number, operator: str) -> Number:
    """
    Perform a basic arithmetic operation on two numbers.

    Args:
        x: First operand (int or float)
        y: Second operand (int or float)
        operator: One of '+', '-', '*', '/'

    Returns:
        Result of the operation

    Raises:
        TypeError: If x or y are not numeric
        ValueError: If operator is not supported
        ZeroDivisionError: If dividing by zero

    Edge Cases:
        - Division by zero: Raises ZeroDivisionError with helpful message
        - Invalid operator: Raises ValueError with list of valid operators
        - Non-numeric input: Raises TypeError with guidance

    Examples:
        >>> calculate(10, 5, '+')
        15
        >>> calculate(10, 5, '/')
        2.0
    """
    # Step 1: Validate inputs are numeric
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise TypeError(
            f"Operands must be numeric. Got x={type(x).__name__}, y={type(y).__name__}"
        )

    # Step 2: Validate operator
    if operator not in OPERATIONS:
        valid_ops = ', '.join(OPERATIONS.keys())
        raise ValueError(
            f"Invalid operator '{operator}'. Valid operators: {valid_ops}"
        )

    # Step 3: Handle division by zero specifically
    if operator == '/' and y == 0:
        raise ZeroDivisionError("Cannot divide by zero")

    # Step 4: Perform operation
    return OPERATIONS[operator](x, y)
```

### Reasoning Score: 92/100 (Grade: A)
- Phase 1: 20/20 (Clear documentation)
- Phase 2: 18/20 (Approach documented)
- Phase 3: 18/20 (Clean execution)
- Phase 4: 18/20 (Edge cases handled)
- Phase 5: 18/20 (Polished output)
```

### Example 3: Creating a Checkpoint

**Input Command**:
```
Create a post-development checkpoint for the authentication module
```

**Output**:
```markdown
## Post-Development Checkpoint

### Module: Authentication
### Date: 2025-12-04
### Analyst: Claude Reasoning Optimizer

### Completeness Check
- [x] All requirements implemented
  - User registration: ✓
  - User login: ✓
  - Password reset: ✓
  - Session management: ✓
- [x] Edge cases handled
  - Invalid email format: ✓
  - Weak password: ✓
  - Account lockout: ✓
- [x] Error handling complete
- [x] Documentation complete

### Quality Check
- [x] Code follows standards
- [x] No obvious bugs
- [x] Performance acceptable (avg response: 45ms)
- [x] Security reviewed
  - Password hashing: bcrypt ✓
  - SQL injection: parameterized queries ✓
  - XSS: sanitized outputs ✓

### Test Coverage
- [x] Unit tests: 94% coverage
- [x] Integration tests: 12/12 passing
- [x] Edge case tests: 8/8 passing

### Reasoning Analysis

#### Score: 84/100 (Grade: B)

| Phase | Score | Notes |
|-------|-------|-------|
| Comprehension | 18/20 | Well documented |
| Strategy | 16/20 | Could document alternatives |
| Execution | 17/20 | Clean implementation |
| Review | 17/20 | Good coverage |
| Refinement | 16/20 | Minor optimizations possible |

### Recommendations Before Release
1. Document why bcrypt was chosen over alternatives
2. Add rate limiting to login endpoint
3. Consider adding 2FA support (future feature)

### Verdict: PASS - Ready for Review
```

---

## Quality Metrics

### Scoring Thresholds

| Score Range | Grade | Meaning | Action |
|-------------|-------|---------|--------|
| 90-100 | A | Excellent | Ready for production |
| 80-89 | B | Good | Minor improvements suggested |
| 70-79 | C | Adequate | Improvements recommended |
| 60-69 | D | Needs Work | Should improve before release |
| 0-59 | F | Poor | Requires reconstruction |

### Phase Weight Distribution

Each phase contributes equally (20 points) to ensure balanced reasoning:

```
Total Score = Comprehension(20) + Strategy(20) + Execution(20) + Review(20) + Refinement(20)
```

### Quality Gates by Context

| Context | Minimum Score | Recommended Score |
|---------|---------------|-------------------|
| Prototype | 50 | 60 |
| Internal Tool | 60 | 75 |
| Production Code | 75 | 85 |
| Critical System | 85 | 95 |
| Open Source | 80 | 90 |

---

## Quick Reference

### Reasoning Phases Summary

1. **Comprehend** - Understand the problem fully
2. **Strategize** - Plan the approach
3. **Execute** - Implement systematically
4. **Review** - Verify thoroughly
5. **Refine** - Polish and optimize

### Analysis Command Shortcuts

| Command | Action |
|---------|--------|
| "Analyze [code]" | Full reasoning assessment |
| "Score [code]" | Quick score only |
| "Rebuild [code]" | Full reconstruction |
| "Checkpoint [type]" | Create checkpoint |
| "Compare [before] [after]" | Compare reasoning improvements |

### Self-Check Questions

- Is the problem clearly understood?
- Is the approach documented?
- Does the code follow a plan?
- Are edge cases handled?
- Is it optimized and polished?

### Red Flag Indicators

- Code without documentation → Phase 1 failure
- No explanation of "why" → Phase 2 failure
- Spaghetti/inconsistent code → Phase 3 failure
- Missing validation/edge cases → Phase 4 failure
- TODOs and obvious issues → Phase 5 failure

---

## Activation Keywords

This skill activates for phrases including:
- "analyze reasoning", "reasoning analysis"
- "optimize code reasoning", "improve reasoning"
- "reasoning assessment", "reasoning score"
- "rebuild with reasoning", "reconstruct code"
- "create checkpoint", "quality checkpoint"
- "reasoning gaps", "find reasoning issues"
- "code quality analysis", "assess code quality"
- "systematic rebuild", "methodical reconstruction"

---

*The Reasoning Optimizer transforms implicit code into explicitly reasoned implementations. By systematically applying the 5-Phase Reasoning Model, it ensures every piece of code meets rigorous quality standards and maintains consistent excellence across all projects.*
