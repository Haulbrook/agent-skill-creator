# Reasoning Process Skill

A comprehensive self-improvement framework for AI reasoning through structured checklists and systematic thought processes. This skill enables Claude to enhance its own reasoning capabilities by following proven methodologies for problem decomposition, solution planning, execution, and iterative refinement.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Reasoning Phases](#core-reasoning-phases)
3. [Chain-of-Thought (CoT) Framework](#chain-of-thought-cot-framework)
4. [Code Generation Reasoning](#code-generation-reasoning)
5. [Checklists and Filters](#checklists-and-filters)
6. [Self-Correction Protocols](#self-correction-protocols)
7. [Prompting Strategy Integration](#prompting-strategy-integration)
8. [Master Checklists](#master-checklists)
9. [Integration Guide](#integration-guide)

---

## Overview

### What is AI Reasoning?

AI reasoning is the process of breaking down problems and working through them logically, simulating how a human would think through a task. Rather than producing immediate answers, reasoning involves:

- **Decomposition**: Breaking complex prompts into sub-tasks
- **Sequential Processing**: Solving each part methodically
- **Synthesis**: Combining sub-solutions into a final answer
- **Verification**: Ensuring the solution is clear, logical, and complete

### Why This Skill Matters

This skill transforms implicit reasoning into explicit, verifiable processes. By following structured checklists, Claude can:

- Reduce errors through systematic verification
- Improve solution quality through iterative refinement
- Make reasoning transparent and auditable
- Handle complex, multi-step problems more reliably
- Self-improve through reflection and correction

---

## Core Reasoning Phases

### The 5-Phase Reasoning Model

Every complex task should flow through these five interconnected phases:

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

### Phase 1: Comprehension and Problem Analysis

**Purpose**: Ensure complete understanding before proceeding.

**Checklist**:
- [ ] What exactly is being asked?
- [ ] What are the explicit requirements?
- [ ] What are the implicit requirements?
- [ ] What are the inputs and expected outputs?
- [ ] Are there any constraints or limitations?
- [ ] Can I restate this problem in my own words?
- [ ] Are there ambiguities that need clarification?

**Output**: A clear mental model or written summary of the problem.

### Phase 2: Solution Strategy Brainstorming

**Purpose**: Explore options and create a roadmap.

**Checklist**:
- [ ] What are the possible approaches to solve this?
- [ ] What patterns or algorithms apply here?
- [ ] What are the trade-offs of each approach?
- [ ] Are there any constraints that eliminate options?
- [ ] What is the optimal approach given the requirements?
- [ ] What are the steps needed to implement this approach?
- [ ] What could go wrong and how will I handle it?

**Output**: A numbered plan or pseudocode outline.

### Phase 3: Execution/Answer Drafting

**Purpose**: Implement the chosen strategy systematically.

**Checklist**:
- [ ] Am I following the planned steps?
- [ ] Is each step logically connected to the next?
- [ ] Am I documenting my reasoning as I go?
- [ ] Are there any deviations from the plan that need noting?
- [ ] Is my output aligned with the requirements?

**Output**: The initial solution or answer draft.

### Phase 4: Review and Self-Check

**Purpose**: Critically evaluate the produced output.

**Checklist**:
- [ ] Does the output address ALL requirements?
- [ ] Are there any edge cases not covered?
- [ ] Is the logic sound and consistent?
- [ ] Are there any errors or mistakes?
- [ ] Is the output clear and understandable?
- [ ] Would this satisfy the original request?
- [ ] What would a critic say about this solution?

**Output**: Confirmation of quality OR list of issues to address.

### Phase 5: Refinement

**Purpose**: Improve and finalize the solution.

**Checklist**:
- [ ] Have all identified issues been addressed?
- [ ] Is the solution optimized where possible?
- [ ] Is the output polished and professional?
- [ ] Does the final version pass all checks?
- [ ] Am I confident in this solution?

**Output**: The final, refined solution.

---

## Chain-of-Thought (CoT) Framework

### What is Chain-of-Thought?

Chain-of-Thought prompting guides the production of a step-by-step logical sequence of thoughts leading to an answer. Instead of outputting a direct answer, intermediate reasoning steps are listed, much like "showing your work."

### When to Use CoT

**Use CoT when**:
- The problem requires multiple logical steps
- Mathematical calculations are involved
- Complex reasoning or analysis is needed
- The solution benefits from transparency
- Errors need to be traceable

**Avoid CoT when**:
- The task is simple and straightforward
- Verbosity would reduce clarity
- The model already has strong built-in reasoning for the task type

### CoT Execution Template

```markdown
## Problem Understanding
[Restate the problem in your own words]

## Known Information
- [Fact 1]
- [Fact 2]
- [Fact n...]

## Reasoning Steps

### Step 1: [Description]
[Explanation and work]
→ Result: [Intermediate result]

### Step 2: [Description]
[Explanation and work]
→ Result: [Intermediate result]

### Step n: [Description]
[Explanation and work]
→ Result: [Intermediate result]

## Conclusion
[Final answer with justification]
```

### Structured Chain-of-Thought (SCoT) for Code

When generating code, align reasoning steps with programming constructs:

```markdown
## Problem Analysis
[What does the code need to do?]

## Structure Planning
- **Sequence**: [What operations happen in order?]
- **Branches**: [What conditions require if/else?]
- **Loops**: [What needs repetition?]
- **Functions**: [What logic should be encapsulated?]

## Implementation Plan
1. [First code block purpose]
2. [Second code block purpose]
3. [Continue...]

## Code
[Implementation following the plan]

## Verification
[Test cases and expected results]
```

---

## Code Generation Reasoning

### The 5-Step Code Reasoning Process

#### Step 1: Understanding the Problem

**Questions to Answer**:
- What is the program supposed to do?
- What are the inputs (types, formats, ranges)?
- What are the expected outputs?
- Are there performance requirements?
- Are there any forbidden approaches?

**Checklist**:
- [ ] I understand the functional requirements
- [ ] I know the input specifications
- [ ] I know the output specifications
- [ ] I understand any constraints
- [ ] I can explain this task to someone else

#### Step 2: Planning the Solution

**Activities**:
- Recall relevant algorithms/patterns
- Choose appropriate data structures
- Design the program architecture
- Consider edge cases upfront
- Plan error handling

**Checklist**:
- [ ] I have chosen an appropriate algorithm/approach
- [ ] I have selected suitable data structures
- [ ] I have outlined the code structure (functions, classes)
- [ ] I have identified edge cases to handle
- [ ] I have planned for error conditions

**Output Format**:
```markdown
### Solution Plan
- **Approach**: [Algorithm/pattern to use]
- **Data Structures**: [What structures and why]
- **Architecture**: [High-level structure]
- **Edge Cases**: [List of edge cases]
- **Error Handling**: [How errors will be managed]
```

#### Step 3: Step-by-Step Construction

**Process**:
- Write code segment by segment
- Each segment corresponds to a plan item
- Comment significant decisions
- Keep code clean and readable

**Checklist**:
- [ ] Each code segment matches a planned step
- [ ] Variable names are clear and descriptive
- [ ] Logic flows naturally from one section to next
- [ ] Complex sections have explanatory comments

#### Step 4: Workarounds and Decisions

**When facing challenges**:
- Document why a workaround is needed
- Explain the trade-off being made
- Note any limitations of the chosen approach
- Consider if the workaround introduces new issues

**Decision Documentation**:
```markdown
### Decision: [What was decided]
- **Context**: [Why this decision point arose]
- **Options Considered**: [Alternative approaches]
- **Choice Made**: [What was selected]
- **Rationale**: [Why this option was best]
- **Trade-offs**: [What was sacrificed]
```

#### Step 5: Iterative Refinement

**Refinement Loop**:
1. Review the code against requirements
2. Mentally trace through execution
3. Identify issues or improvements
4. Make corrections
5. Repeat until satisfied

**Code Review Checklist**:
- [ ] Does the code handle all specified inputs?
- [ ] Does the code produce correct outputs?
- [ ] Are edge cases handled properly?
- [ ] Is error handling adequate?
- [ ] Is the code efficient enough?
- [ ] Is the code readable and maintainable?
- [ ] Are there any security concerns?

---

## Checklists and Filters

### Understanding Checklists

Checklists are sets of criteria that solutions must meet. They serve as verification gates that ensure completeness and correctness.

### Types of Checklists

#### 1. Requirements Checklist
Ensures all specified requirements are addressed.

```markdown
## Requirements Verification
- [ ] Requirement 1: [Description] → [How addressed]
- [ ] Requirement 2: [Description] → [How addressed]
- [ ] Requirement n: [Description] → [How addressed]
```

#### 2. Edge Case Checklist
Ensures boundary conditions are handled.

```markdown
## Edge Case Coverage
- [ ] Empty input → [Handling]
- [ ] Single element → [Handling]
- [ ] Maximum size → [Handling]
- [ ] Invalid input → [Handling]
- [ ] Null/None values → [Handling]
- [ ] Negative numbers (if applicable) → [Handling]
- [ ] Zero values → [Handling]
- [ ] Special characters (if applicable) → [Handling]
```

#### 3. Quality Checklist
Ensures the solution meets quality standards.

```markdown
## Quality Standards
- [ ] Code is readable and well-structured
- [ ] Logic is clear and follows best practices
- [ ] Performance is acceptable
- [ ] Memory usage is reasonable
- [ ] Error messages are helpful
- [ ] Documentation is adequate
```

#### 4. Security Checklist (for code)
Ensures no vulnerabilities are introduced.

```markdown
## Security Review
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Input is properly validated
- [ ] Sensitive data is protected
- [ ] No hardcoded secrets
- [ ] Proper authentication/authorization
```

### Understanding Filters

Filters are mechanisms that weed out incorrect or low-quality reasoning paths.

#### Filter Type 1: Multiple Solution Generation

Generate multiple approaches and compare:

```markdown
## Solution Alternatives

### Approach A: [Name]
- **Description**: [How it works]
- **Pros**: [Advantages]
- **Cons**: [Disadvantages]
- **Complexity**: [Time/Space]

### Approach B: [Name]
- **Description**: [How it works]
- **Pros**: [Advantages]
- **Cons**: [Disadvantages]
- **Complexity**: [Time/Space]

### Selection
**Chosen Approach**: [A or B]
**Reasoning**: [Why this is best for the requirements]
```

#### Filter Type 2: Self-Consistency Check

Generate multiple reasoning chains and verify consistency:

```markdown
## Consistency Verification

### Reasoning Chain 1
[First approach to the problem]
→ Result: [Answer]

### Reasoning Chain 2
[Alternative approach]
→ Result: [Answer]

### Consistency Check
- Do results agree? [Yes/No]
- If no, analyze discrepancy: [Analysis]
- Correct answer determination: [Reasoning]
```

#### Filter Type 3: Test-Based Filtering

For code, generate test cases and verify:

```markdown
## Test Verification

### Test 1: [Description]
- Input: [value]
- Expected: [value]
- Actual: [value]
- Pass: [Yes/No]

### Test 2: [Description]
- Input: [value]
- Expected: [value]
- Actual: [value]
- Pass: [Yes/No]

### Summary
- Tests Passed: [X/Y]
- Issues Found: [List or None]
```

---

## Self-Correction Protocols

### The Reflective Reasoning Loop

```
┌──────────────┐
│   Generate   │
│   Solution   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Evaluate   │◄─────────────┐
│   Output     │              │
└──────┬───────┘              │
       │                      │
       ▼                      │
   ┌───────┐    No      ┌─────┴─────┐
   │ Good? ├────────────►   Revise  │
   └───┬───┘            │   Output  │
       │ Yes            └───────────┘
       ▼
┌──────────────┐
│   Finalize   │
└──────────────┘
```

### Self-Critique Protocol

After generating a solution, ask these questions:

**Accuracy Questions**:
- Is this factually correct?
- Have I made any logical errors?
- Are my assumptions valid?
- Would an expert agree with this?

**Completeness Questions**:
- Have I addressed all parts of the request?
- Are there aspects I've overlooked?
- Is anything missing that should be included?
- Would the requester be satisfied?

**Quality Questions**:
- Is this the best approach?
- Could this be improved?
- Is this clear and understandable?
- Am I confident in this answer?

### Self-Critique Template

```markdown
## Self-Critique Analysis

### What I Produced
[Brief summary of the solution]

### Accuracy Assessment
- **Factual Correctness**: [Assessment]
- **Logical Soundness**: [Assessment]
- **Assumption Validity**: [Assessment]

### Completeness Assessment
- **Requirements Coverage**: [X/Y requirements met]
- **Missing Elements**: [List or None]
- **Overlooked Aspects**: [List or None]

### Quality Assessment
- **Approach Optimality**: [Rating 1-5]
- **Clarity**: [Rating 1-5]
- **Confidence Level**: [Low/Medium/High]

### Identified Issues
1. [Issue 1]
2. [Issue 2]
3. [Continue...]

### Corrections Needed
1. [Correction 1]
2. [Correction 2]
3. [Continue...]
```

### Error Categories and Corrections

#### Logic Errors
- **Symptom**: Conclusion doesn't follow from premises
- **Detection**: Trace each step, verify logical connections
- **Correction**: Identify break in logic, reconstruct reasoning

#### Completeness Errors
- **Symptom**: Missing requirements or edge cases
- **Detection**: Check against requirements list
- **Correction**: Add missing elements

#### Accuracy Errors
- **Symptom**: Factually incorrect information
- **Detection**: Verify claims against known facts
- **Correction**: Replace with accurate information

#### Efficiency Errors
- **Symptom**: Suboptimal approach used
- **Detection**: Compare with alternative approaches
- **Correction**: Implement better algorithm/method

---

## Prompting Strategy Integration

### How to Process Different Prompt Types

#### Simple, Direct Questions
- Answer directly without excessive elaboration
- No need for extensive CoT
- Brief verification is sufficient

#### Complex, Multi-Part Questions
- Decompose into sub-questions
- Address each part systematically
- Synthesize into cohesive answer
- Use full reasoning phases

#### Coding Tasks
- Use Code Generation Reasoning process
- Apply relevant checklists
- Test mentally or actually
- Iterate until correct

#### Analysis/Research Tasks
- Gather relevant information
- Organize by themes/categories
- Present balanced perspective
- Support claims with evidence

#### Creative Tasks
- Brainstorm multiple options
- Select promising directions
- Develop chosen approach
- Refine for quality

### Prompt Analysis Checklist

When receiving any prompt:

- [ ] What type of task is this?
- [ ] What is the complexity level?
- [ ] What reasoning depth is appropriate?
- [ ] Are there specific constraints?
- [ ] What format is expected for output?
- [ ] What quality level is required?

---

## Master Checklists

### Universal Pre-Response Checklist

Before producing any response:

```markdown
## Pre-Response Check
- [ ] I understand what is being asked
- [ ] I have identified the task type
- [ ] I know the expected output format
- [ ] I have noted all constraints
- [ ] I have a plan for approaching this
```

### Universal Post-Response Checklist

After producing any response:

```markdown
## Post-Response Check
- [ ] The response addresses the actual question
- [ ] All parts of the request are covered
- [ ] The reasoning is sound and logical
- [ ] The output is clear and well-organized
- [ ] Edge cases are considered
- [ ] The quality meets expectations
- [ ] I would be satisfied receiving this response
```

### Code-Specific Master Checklist

```markdown
## Code Quality Checklist

### Correctness
- [ ] Code compiles/runs without errors
- [ ] Code produces correct output for normal inputs
- [ ] Code handles edge cases correctly
- [ ] Code handles error conditions gracefully

### Quality
- [ ] Code is readable and well-formatted
- [ ] Variable/function names are descriptive
- [ ] Complex logic is commented
- [ ] Code follows language conventions

### Robustness
- [ ] Input validation is present
- [ ] Error handling is appropriate
- [ ] No obvious security vulnerabilities
- [ ] Resource management is proper

### Efficiency
- [ ] Algorithm choice is appropriate
- [ ] No unnecessary computations
- [ ] Memory usage is reasonable
- [ ] No obvious performance issues
```

### Problem-Solving Master Checklist

```markdown
## Problem-Solving Checklist

### Understanding
- [ ] Problem is clearly defined
- [ ] Inputs are identified
- [ ] Outputs are specified
- [ ] Constraints are noted
- [ ] Success criteria are clear

### Planning
- [ ] Multiple approaches considered
- [ ] Best approach selected
- [ ] Plan is detailed and actionable
- [ ] Risks are identified

### Execution
- [ ] Following the plan
- [ ] Documenting progress
- [ ] Handling deviations
- [ ] Maintaining quality

### Verification
- [ ] Solution meets requirements
- [ ] Edge cases handled
- [ ] Quality standards met
- [ ] Stakeholder would be satisfied
```

---

## Integration Guide

### How Claude Should Use This Skill

#### Automatic Activation
This skill should be invoked when:
- Tasks require multi-step reasoning
- Code generation is requested
- Complex analysis is needed
- High accuracy is critical
- The user asks for thorough work

#### Depth Calibration
Match reasoning depth to task complexity:

| Task Complexity | Reasoning Depth | Checklists to Use |
|-----------------|-----------------|-------------------|
| Simple | Light | Post-Response only |
| Moderate | Standard | Pre + Post Response |
| Complex | Deep | Full 5-Phase Model |
| Critical | Maximum | All applicable checklists |

#### Internal vs External Reasoning

**Internal (Not shown to user)**:
- Quick verification checks
- Simple decision-making
- Routine quality assurance

**External (Shown to user)**:
- When explicitly requested
- For educational purposes
- When transparency aids understanding
- For complex problems where steps help

### Skill Invocation Patterns

#### Pattern 1: Quick Task
```
1. Pre-Response Check (mental)
2. Execute task
3. Post-Response Check (mental)
4. Deliver response
```

#### Pattern 2: Standard Task
```
1. Phase 1: Comprehension
2. Phase 2: Strategy (brief)
3. Phase 3: Execution
4. Phase 4: Review
5. Phase 5: Refinement (if needed)
6. Deliver response
```

#### Pattern 3: Complex Task
```
1. Full Phase 1 with documentation
2. Full Phase 2 with alternatives
3. Full Phase 3 with progress tracking
4. Full Phase 4 with checklist verification
5. Full Phase 5 with iteration
6. Self-critique
7. Final verification
8. Deliver response
```

#### Pattern 4: Code Task
```
1. Understand requirements
2. Plan solution (documented)
3. Write code step-by-step
4. Apply Code Quality Checklist
5. Test mentally/actually
6. Refine as needed
7. Deliver with explanation
```

### Continuous Improvement

After each significant task, briefly reflect:
- What went well?
- What could be improved?
- What patterns emerged?
- What lessons for next time?

This reflection builds implicit knowledge that improves future performance.

---

## Quick Reference Cards

### Card 1: The 5 Phases
1. **Comprehend** - Understand fully
2. **Strategize** - Plan approach
3. **Execute** - Do the work
4. **Review** - Check quality
5. **Refine** - Perfect it

### Card 2: CoT Triggers
Use Chain-of-Thought when:
- Math is involved
- Logic is complex
- Steps need verification
- Transparency helps

### Card 3: Self-Check Questions
- Is this correct?
- Is this complete?
- Is this clear?
- Is this quality?
- Would I accept this?

### Card 4: Code Essentials
- Understand → Plan → Write → Test → Refine
- Check: Correct, Complete, Clean, Secure
- Edge cases: Empty, One, Many, Invalid

### Card 5: Filter Methods
1. Generate alternatives
2. Compare systematically
3. Select best option
4. Verify selection

---

## Appendix: Reasoning Patterns Library

### Pattern: Divide and Conquer
**When**: Problem is large and complex
**How**: Break into smaller sub-problems, solve each, combine solutions
**Template**:
```
Main Problem → [Sub-problem 1] + [Sub-problem 2] + ... + [Sub-problem n]
Solve each sub-problem independently
Combine: Solution = f(Sol_1, Sol_2, ..., Sol_n)
```

### Pattern: Working Backwards
**When**: End state is clearer than path
**How**: Start from goal, determine what's needed to reach it
**Template**:
```
Goal State → What produces this? → What produces that? → ... → Starting State
Reverse the chain for solution
```

### Pattern: Analogical Reasoning
**When**: Problem resembles a known problem type
**How**: Identify the analogous problem, adapt its solution
**Template**:
```
New Problem ≈ Known Problem Type
Known Solution exists for Known Problem Type
Adapted Solution = Known Solution modified for New Problem specifics
```

### Pattern: Constraint Satisfaction
**When**: Multiple constraints must be satisfied simultaneously
**How**: Enumerate constraints, find solutions that satisfy all
**Template**:
```
Constraints: [C1, C2, ..., Cn]
For each potential solution:
  Check: Satisfies C1? C2? ... Cn?
  If all satisfied → Valid solution
```

### Pattern: Iterative Refinement
**When**: Perfect solution unlikely on first attempt
**How**: Generate initial solution, repeatedly improve
**Template**:
```
Generate Initial Solution
Loop:
  Evaluate current solution
  Identify weaknesses
  Modify to address weaknesses
  Until: Quality threshold met OR No improvement possible
```

---

*This skill document serves as a comprehensive guide for systematic reasoning. By following these frameworks, checklists, and patterns, Claude can approach any task with methodical thoroughness, producing higher quality outputs through disciplined thinking processes.*
