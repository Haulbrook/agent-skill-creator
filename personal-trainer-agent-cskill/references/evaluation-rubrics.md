# Evaluation Rubrics Guide

This guide covers how to create effective evaluation rubrics for different domains and use cases.

## Rubric Structure

Every rubric consists of:
1. **Criteria** - What aspects to evaluate
2. **Weights** - Relative importance of each criterion
3. **Scoring Guide** - What each score level means
4. **Indicators** - Patterns that signal quality

## Built-in Rubrics

### Website Building Rubric

```json
{
  "name": "Website Building Quality",
  "criteria": [
    {
      "name": "visual_design",
      "weight": 0.20,
      "description": "Quality of visual design and aesthetics"
    },
    {
      "name": "code_quality",
      "weight": 0.25,
      "description": "Quality and maintainability of code"
    },
    {
      "name": "responsiveness",
      "weight": 0.20,
      "description": "Mobile-friendliness and responsive behavior"
    },
    {
      "name": "functionality",
      "weight": 0.20,
      "description": "Working features and interactivity"
    },
    {
      "name": "accessibility",
      "weight": 0.15,
      "description": "Accessibility compliance"
    }
  ]
}
```

### Marketing Content Rubric

```json
{
  "name": "Marketing Content Quality",
  "criteria": [
    {
      "name": "messaging_clarity",
      "weight": 0.25,
      "description": "Clarity and impact of core message"
    },
    {
      "name": "audience_targeting",
      "weight": 0.20,
      "description": "How well content targets intended audience"
    },
    {
      "name": "call_to_action",
      "weight": 0.20,
      "description": "Strength and clarity of CTA"
    },
    {
      "name": "persuasion",
      "weight": 0.20,
      "description": "Use of persuasion techniques"
    },
    {
      "name": "engagement",
      "weight": 0.15,
      "description": "How engaging the content is"
    }
  ]
}
```

### Code Quality Rubric

```json
{
  "name": "Code Quality",
  "criteria": [
    {
      "name": "correctness",
      "weight": 0.30,
      "description": "Code correctness and bug-free operation"
    },
    {
      "name": "readability",
      "weight": 0.25,
      "description": "Code readability and documentation"
    },
    {
      "name": "maintainability",
      "weight": 0.20,
      "description": "Code structure and maintainability"
    },
    {
      "name": "performance",
      "weight": 0.15,
      "description": "Code efficiency and performance"
    },
    {
      "name": "best_practices",
      "weight": 0.10,
      "description": "Following language best practices"
    }
  ]
}
```

## Creating Custom Rubrics

### Step 1: Define Criteria

Identify 4-6 key dimensions that matter for your use case:

```python
criteria = [
    "accuracy",       # Is the information correct?
    "completeness",   # Does it cover all aspects?
    "clarity",        # Is it easy to understand?
    "actionability",  # Can the user act on it?
]
```

### Step 2: Assign Weights

Weights should sum to 1.0. Prioritize what matters most:

```python
weights = {
    "accuracy": 0.35,      # Most important
    "completeness": 0.25,
    "clarity": 0.25,
    "actionability": 0.15  # Nice to have
}
```

### Step 3: Define Scoring Guides

Create clear descriptions for each score level:

```python
scoring_guide = {
    10: "Exceptional - Sets a new standard for quality",
    8: "Good - Meets all requirements with minor room for improvement",
    6: "Adequate - Meets basic requirements",
    4: "Below expectations - Has significant issues",
    2: "Poor - Fails to meet requirements"
}
```

### Step 4: Identify Indicators

List positive and negative patterns to detect:

```python
indicators = {
    "positive": [
        "specific",
        "example",
        "step-by-step",
        "clear",
        "actionable"
    ],
    "negative": [
        "vague",
        "unclear",
        "maybe",
        "generic",
        "placeholder"
    ]
}
```

## Complete Custom Rubric Example

```python
custom_rubric = {
    "name": "Customer Support Response Quality",
    "version": "1.0",
    "criteria": [
        {
            "name": "problem_resolution",
            "description": "How well the response addresses the customer's issue",
            "weight": 0.30,
            "scoring_guide": {
                10: "Completely resolves issue with clear solution",
                8: "Addresses issue well with minor gaps",
                6: "Partially addresses issue",
                4: "Misses key aspects of the issue",
                2: "Does not address the issue"
            },
            "indicators": {
                "positive": ["solution", "resolve", "fix", "steps to"],
                "negative": ["cannot help", "not possible", "refer to"]
            }
        },
        {
            "name": "empathy",
            "description": "Shows understanding of customer frustration",
            "weight": 0.20,
            "scoring_guide": {
                10: "Exceptional empathy, customer feels truly heard",
                8: "Good empathy, acknowledges feelings",
                6: "Some empathy present",
                4: "Cold or dismissive tone",
                2: "No empathy, robotic response"
            },
            "indicators": {
                "positive": ["understand", "frustrating", "sorry", "appreciate"],
                "negative": ["policy states", "unfortunately cannot", "rules"]
            }
        },
        {
            "name": "clarity",
            "description": "How clear and easy to follow the response is",
            "weight": 0.25,
            "scoring_guide": {
                10: "Crystal clear, any customer could follow",
                8: "Clear with good structure",
                6: "Understandable but could be clearer",
                4: "Confusing or hard to follow",
                2: "Very unclear or incomprehensible"
            },
            "indicators": {
                "positive": ["step 1", "first", "then", "finally", "here's how"],
                "negative": ["might", "possibly", "various", "multiple options"]
            }
        },
        {
            "name": "professionalism",
            "description": "Maintains professional tone while being helpful",
            "weight": 0.15,
            "scoring_guide": {
                10: "Perfectly professional and warm",
                8: "Professional with friendly tone",
                6: "Professional but impersonal",
                4: "Unprofessional elements present",
                2: "Unprofessional response"
            },
            "indicators": {
                "positive": ["happy to help", "please", "thank you"],
                "negative": ["obviously", "as I said", "again"]
            }
        },
        {
            "name": "completeness",
            "description": "Covers all aspects of the request",
            "weight": 0.10,
            "scoring_guide": {
                10: "Comprehensive, anticipates follow-up questions",
                8: "Complete coverage of the issue",
                6: "Covers main points",
                4: "Missing important details",
                2: "Very incomplete"
            },
            "indicators": {
                "positive": ["also", "additionally", "note that", "if you need"],
                "negative": ["only", "just", "basic"]
            }
        }
    ]
}
```

## Rubric Calibration

### Test with Edge Cases
Evaluate your rubric with:
- Obviously excellent outputs (should score 9-10)
- Obviously poor outputs (should score 2-4)
- Borderline cases (should score 5-7)

### Adjust Weights Based on Results
If important issues aren't reflected in scores:
- Increase weight of relevant criterion
- Add new criterion if needed
- Strengthen indicators

### Validate Inter-rater Reliability
Have multiple people score same outputs:
- Calculate agreement percentage
- Refine scoring guides where disagreement occurs

## Domain-Specific Indicator Libraries

### Technical Writing
**Positive:** accuracy, precision, citations, examples, diagrams
**Negative:** jargon, ambiguous, unclear, outdated

### Creative Writing
**Positive:** vivid, engaging, original, evocative, flowing
**Negative:** cliché, repetitive, awkward, confusing

### Data Analysis
**Positive:** insight, trend, correlation, significant, evidence
**Negative:** assumption, guess, maybe, unclear methodology

### Sales/Persuasion
**Positive:** benefit, value, ROI, proof, testimonial, guarantee
**Negative:** pushy, aggressive, misleading, exaggerated

## Using Rubrics Programmatically

```python
from scripts.evaluators.rubric_evaluator import RubricEvaluator

evaluator = RubricEvaluator()

# Load built-in rubric
evaluator.load_domain_rubric("website_building")

# Or set custom rubric
evaluator.set_rubric(custom_rubric)

# Evaluate single output
result = evaluator.evaluate({"output": "Your agent's output here"})
print(f"Overall: {result['overall_score']}")
print(f"Dimensions: {result['dimension_scores']}")
print(f"Strengths: {result['strengths']}")
print(f"Improvements: {result['areas_for_improvement']}")

# Batch evaluation
results = evaluator.batch_evaluate(outputs)
summary = evaluator.get_evaluation_summary(results)
```
