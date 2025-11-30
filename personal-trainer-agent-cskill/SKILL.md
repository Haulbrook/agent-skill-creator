# Personal Trainer Agent

A meta-skill for systematically improving AI agents and bots through structured evaluation, iterative coaching, and integration with reinforcement learning frameworks.

## Overview

The Personal Trainer Agent is designed to help developers who build AI agents/bots systematically improve their creations. Whether you've built a website builder bot that needs to produce better designs, a marketing agent that needs to write more compelling copy, or a coding assistant that needs to generate cleaner code, this skill provides the tools and methodology to "train up" your agents.

### Core Capabilities

1. **Performance Analysis** - Analyze agent outputs to identify strengths, weaknesses, and patterns
2. **Structured Evaluation** - Evaluate outputs using customizable rubrics with domain-specific criteria
3. **Comparison & A/B Testing** - Compare output versions to measure improvement
4. **Prompt Optimization** - Systematically improve agent prompts based on feedback
5. **Training Data Generation** - Generate formatted data for DPO, RLHF, and SFT training
6. **TRL Integration** - Direct integration with HuggingFace's TRL library for fine-tuning
7. **OpenRL Integration** - Flexible RL training with custom reward functions
8. **Iterative Coaching** - Run coaching sessions that progressively improve agents

## Architecture

```
personal-trainer-agent-cskill/
├── .claude-plugin/
│   └── marketplace.json          # Activation configuration
├── SKILL.md                      # This file
├── scripts/
│   ├── main.py                   # PersonalTrainerAgent orchestrator
│   ├── analyzers/
│   │   ├── performance_analyzer.py   # Multi-dimensional analysis
│   │   ├── output_evaluator.py       # Individual output evaluation
│   │   └── pattern_detector.py       # Pattern recognition
│   ├── trainers/
│   │   ├── trl_trainer.py           # TRL framework integration
│   │   ├── openrl_trainer.py        # OpenRL integration
│   │   └── prompt_optimizer.py      # Prompt improvement
│   ├── evaluators/
│   │   ├── rubric_evaluator.py      # Rubric-based scoring
│   │   └── comparison_evaluator.py   # A/B comparison
│   └── utils/
│       ├── session_manager.py       # Session persistence
│       └── metrics_tracker.py       # Progress tracking
├── references/
│   ├── training-methodologies.md    # Training approaches guide
│   ├── evaluation-rubrics.md        # Domain rubric templates
│   └── integration-guides.md        # TRL/OpenRL setup
├── assets/
│   ├── rubrics/                     # Pre-built rubrics
│   └── configs/                     # Training configurations
└── README.md                        # User guide
```

## Usage

### Quick Start

```python
from scripts.main import PersonalTrainerAgent, TrainingMode, CoachingIntensity

# Initialize trainer
trainer = PersonalTrainerAgent()

# Create profile for your agent
profile = trainer.create_agent_profile(
    name="WebsiteBuilder",
    description="Bot that creates frontend websites from descriptions",
    domain="website_building",
    current_prompts={
        "system": "You are a frontend developer. Create websites based on user descriptions."
    },
    sample_outputs=[
        {"input": "Create a landing page for a SaaS product", "output": "<html>..."},
        {"input": "Build a portfolio site", "output": "<html>..."}
    ],
    known_weaknesses=["designs look generic", "doesn't use modern CSS"]
)

# Start training session
session = trainer.start_training_session(
    profile,
    mode=TrainingMode.PROMPT_OPTIMIZATION,
    intensity=CoachingIntensity.MODERATE
)

# Evaluate outputs and get recommendations
results = trainer.evaluate_outputs(session, sample_outputs)
recommendations = trainer.get_recommendations(session)

# View progress
progress = trainer.get_session_progress(session)
print(f"Current score: {progress['current_metrics']['latest_average_score']}")
```

### Training Modes

#### 1. Analysis Only
Just analyze outputs without any training:
```python
session = trainer.start_training_session(
    profile,
    mode=TrainingMode.ANALYSIS_ONLY
)
```

#### 2. Prompt Optimization
Improve agent performance through prompt engineering (no model training required):
```python
session = trainer.start_training_session(
    profile,
    mode=TrainingMode.PROMPT_OPTIMIZATION
)

# Run coaching iteration
result = trainer.run_coaching_iteration(session, new_outputs)
optimized_prompts = result["optimized_prompts"]
```

#### 3. TRL DPO Training
Train using Direct Preference Optimization:
```python
session = trainer.start_training_session(
    profile,
    mode=TrainingMode.TRL_DPO
)

# Generate training data
training_data = trainer.generate_training_data(session, format_type="dpo")

# Run training
result = trainer.run_trl_training(session, training_data)
print(f"Model saved to: {result.model_path}")
```

#### 4. TRL RLHF Training
Full RLHF pipeline with reward model:
```python
session = trainer.start_training_session(
    profile,
    mode=TrainingMode.TRL_RLHF
)

training_data = trainer.generate_training_data(session, format_type="rlhf")
result = trainer.run_trl_training(session, training_data)
```

#### 5. OpenRL Training
Flexible RL with custom environments and rewards:
```python
from scripts.trainers.openrl_trainer import OpenRLTrainer

session = trainer.start_training_session(
    profile,
    mode=TrainingMode.OPENRL
)

# Define custom reward function
def reward_fn(context, output):
    # Your custom scoring logic
    score = evaluate_output_quality(output)
    return score

# Run training
result = trainer.run_openrl_training(
    session,
    environment_config={"max_steps": 100},
    reward_function=reward_fn
)
```

## Evaluation System

### Built-in Domain Rubrics

The skill includes optimized rubrics for common domains:

#### Website Building
- **Visual Design** (20%) - Aesthetics, color, typography, layout
- **Code Quality** (25%) - Semantic HTML, CSS organization, best practices
- **Responsiveness** (20%) - Mobile-first, media queries, flexibility
- **Functionality** (20%) - Working features, interactivity
- **Accessibility** (15%) - WCAG compliance, ARIA, keyboard navigation

#### Marketing
- **Messaging Clarity** (25%) - Clear value proposition, compelling message
- **Audience Targeting** (20%) - Customer-focused, addresses pain points
- **Call-to-Action** (20%) - Clear, compelling CTAs
- **Persuasion** (20%) - Social proof, credibility, evidence
- **Engagement** (15%) - Memorable, shareable content

#### Coding
- **Correctness** (30%) - Works correctly, handles edge cases
- **Readability** (25%) - Clear names, documentation, formatting
- **Maintainability** (20%) - Modular, DRY, extensible
- **Performance** (15%) - Efficient algorithms, optimization
- **Best Practices** (10%) - Type hints, error handling, testing

### Custom Rubrics

Create your own evaluation criteria:
```python
custom_rubric = {
    "name": "Customer Support Quality",
    "criteria": [
        {
            "name": "empathy",
            "description": "Shows understanding and care for customer issues",
            "weight": 0.25,
            "scoring_guide": {
                10: "Exceptional empathy, makes customer feel heard",
                8: "Good empathy, acknowledges feelings",
                6: "Some empathy shown",
                4: "Cold or dismissive tone",
                2: "No empathy, robotic response"
            },
            "indicators": {
                "positive": ["understand", "sorry to hear", "appreciate", "help"],
                "negative": ["policy", "cannot", "not possible", "refer to"]
            }
        },
        # ... more criteria
    ]
}

trainer.rubric_evaluator.set_rubric(custom_rubric)
```

## Pattern Detection

The skill automatically detects recurring patterns in agent outputs:

### Negative Patterns (Auto-detected)
- Placeholder text (TODO, FIXME, Lorem ipsum)
- Code issues (bare excepts, hardcoded secrets, eval())
- Design issues (inline styles, !important, div soup)
- Style issues (AI self-references, excessive fillers)

### Positive Patterns (Reinforced)
- Good structure (headers, lists, code blocks)
- Quality indicators (type hints, docstrings, semantic HTML)
- Domain best practices (media queries, error handling, CTAs)

## Training Data Generation

### DPO Format
```python
data = trainer.generate_training_data(session, format_type="dpo")
# Output:
# {
#     "format": "dpo",
#     "data": [
#         {"prompt": "...", "chosen": "...", "rejected": "..."},
#         ...
#     ]
# }
```

### RLHF Format
```python
data = trainer.generate_training_data(session, format_type="rlhf")
# Output:
# {
#     "format": "rlhf",
#     "data": [
#         {"prompt": "...", "response": "...", "reward": 0.85},
#         ...
#     ]
# }
```

### SFT Format (High-quality examples only)
```python
data = trainer.generate_training_data(session, format_type="sft")
# Output:
# {
#     "format": "sft",
#     "threshold": 7.0,  # Only includes outputs scoring >= 7
#     "data": [
#         {"prompt": "...", "completion": "..."},
#         ...
#     ]
# }
```

## Iterative Coaching

The coaching system provides systematic improvement:

```python
# Run coaching iterations
for iteration in range(5):
    # Collect new outputs from your agent
    new_outputs = run_agent_on_test_cases(optimized_prompts)

    # Run coaching iteration
    result = trainer.run_coaching_iteration(session, new_outputs)

    print(f"Iteration {iteration + 1}:")
    print(f"  Score: {result['average_score']:.2f}")
    print(f"  Improvement: {result['improvement_from_last']:+.2f}")

    # Update prompts for next iteration
    optimized_prompts = result["optimized_prompts"]

    # Check recommendations
    for rec in result["recommendations"][:3]:
        print(f"  Recommendation: {rec.action}")
```

## Metrics & Progress Tracking

### Session Progress
```python
progress = trainer.get_session_progress(session)

print(f"Session: {progress['session_id']}")
print(f"Iterations: {progress['iterations_completed']}")
print(f"Current Score: {progress['current_metrics']['latest_average_score']}")
print(f"Overall Improvement: {progress['overall_improvement']['percentage_improvement']}%")
```

### Visualization Export
```python
from scripts.utils.metrics_tracker import MetricsTracker

tracker = MetricsTracker()
viz_data = tracker.export_for_visualization(session.session_id)

# Returns data ready for charting libraries:
# - timeline: scores over time
# - distribution: score histogram
# - dimension_comparison: per-dimension analysis
```

## Comparison & A/B Testing

```python
from scripts.evaluators.comparison_evaluator import ComparisonEvaluator

evaluator = ComparisonEvaluator()

# Compare two versions
comparison = evaluator.compare(output_v1, output_v2, input_context)
print(f"Winner: {comparison['winner']}")
print(f"Improvement: {comparison['improvement_percentage']}%")

# Generate preference pairs for training
pairs = evaluator.generate_preference_pairs(
    outputs_v1=baseline_outputs,
    outputs_v2=improved_outputs,
    inputs=test_inputs
)
# Use pairs for DPO training
```

## TRL Integration Details

### DPO Training
```python
from scripts.trainers.trl_trainer import TRLTrainer, TRLConfig

trl_trainer = TRLTrainer({
    "model_name_or_path": "mistralai/Mistral-7B-v0.1",
    "learning_rate": 5e-6,
    "num_epochs": 3,
    "dpo_beta": 0.1,
    "use_peft": True  # Uses LoRA for efficient training
})

result = trl_trainer.train_dpo(preference_data, model_info)
```

### PPO Training
```python
result = trl_trainer.train_ppo(
    prompts=training_prompts,
    reward_model=reward_model,
    config={
        "ppo_epochs": 4,
        "target_kl": 0.1
    }
)
```

### Generate Standalone Training Script
```python
script = trl_trainer.generate_training_script(
    data_path="./training_data.json",
    training_type="dpo"
)

with open("train.py", "w") as f:
    f.write(script)
# Can run training outside the agent
```

## OpenRL Integration Details

### Custom Reward Functions
```python
from scripts.trainers.openrl_trainer import OpenRLTrainer

openrl_trainer = OpenRLTrainer()

# Create reward function from rubric
reward_fn = openrl_trainer.create_reward_function(
    rubric=custom_rubric,
    weights={
        "quality": 0.4,
        "relevance": 0.3,
        "completeness": 0.3
    }
)

# Or define custom reward logic
def custom_reward(context, output):
    score = 0.0

    # Check for required elements
    if "call to action" in output.lower():
        score += 0.3

    # Check for quality indicators
    if len(output) > 200:
        score += 0.2

    # Penalize negative indicators
    if "sorry" in output.lower():
        score -= 0.2

    return score

result = openrl_trainer.train(
    agent_profile,
    {"max_steps": 100},
    custom_reward
)
```

## Quick Evaluation Functions

For one-off evaluations without full sessions:

```python
from scripts.main import quick_evaluate, quick_recommendations

# Quickly evaluate outputs
results = quick_evaluate(
    outputs=[{"output": "..."}],
    domain="website_building"
)

# Quickly get prompt recommendations
recommendations = quick_recommendations(
    prompts={"system": "You are a helpful assistant"},
    domain="general",
    known_issues=["responses are too generic"]
)
```

## Dependencies

### Required
- Python >= 3.9
- transformers >= 4.35.0
- datasets >= 2.14.0
- numpy >= 1.24.0
- rich >= 13.0.0 (for display)

### For TRL Training
- trl >= 0.7.0
- torch >= 2.0.0
- peft >= 0.6.0
- accelerate >= 0.24.0

### For OpenRL Training
- openrl >= 0.2.0

### Optional
- wandb >= 0.15.0 (experiment tracking)
- tensorboard >= 2.14.0 (visualization)
- matplotlib >= 3.7.0 (local plotting)

## Best Practices

### 1. Start with Analysis
Before training, analyze current performance:
```python
results = trainer.evaluate_outputs(session, sample_outputs)
patterns = trainer.pattern_detector.detect(sample_outputs, domain)
```

### 2. Try Prompt Optimization First
Often you can achieve significant improvements without model training:
```python
optimized = trainer.optimize_prompts(session, evaluation_results)
# Test the optimized prompts before moving to RL training
```

### 3. Collect Quality Training Data
For RL training, quality matters more than quantity:
- Include diverse inputs covering edge cases
- Have humans rate outputs when possible
- Create clear preference pairs with meaningful differences

### 4. Iterate Gradually
Run multiple coaching iterations:
- Track improvement after each iteration
- Stop when improvements plateau
- Use recommendations to guide focus areas

### 5. Monitor for Regression
When making changes, compare to baseline:
```python
comparison = evaluator.compare(baseline_output, new_output)
if comparison["winner"] == "a":  # Baseline is better
    print("Warning: Regression detected!")
```

## Example: Training a Website Builder Bot

```python
from scripts.main import PersonalTrainerAgent, TrainingMode, CoachingIntensity

# Initialize
trainer = PersonalTrainerAgent()

# Profile your bot
profile = trainer.create_agent_profile(
    name="WebsiteBuilderBot",
    description="Creates responsive website frontends",
    domain="website_building",
    current_prompts={
        "system": """You are a frontend developer.
        Create responsive HTML/CSS based on user descriptions."""
    },
    sample_outputs=load_sample_outputs("./samples/"),
    known_weaknesses=[
        "Designs look generic",
        "Uses inline styles",
        "Not mobile-responsive"
    ],
    target_improvements=[
        "Create unique, modern designs",
        "Use semantic HTML and organized CSS",
        "Implement mobile-first responsive design"
    ]
)

# Start training
session = trainer.start_training_session(
    profile,
    mode=TrainingMode.PROMPT_OPTIMIZATION,
    intensity=CoachingIntensity.INTENSIVE
)

# Coaching loop
for i in range(10):
    # Get outputs from your bot
    outputs = run_bot_on_test_cases(current_prompts)

    # Run coaching iteration
    result = trainer.run_coaching_iteration(session, outputs)

    print(f"Iteration {i+1}: Score = {result['average_score']:.2f}")

    # Update prompts
    current_prompts = result["optimized_prompts"]

    # Check for convergence
    if result["improvement_from_last"] < 0.1 and result["average_score"] > 8:
        print("Training converged!")
        break

# Get final report
report = trainer.end_session(session)
print(f"Final improvement: {report['overall_improvement']['percentage_improvement']}%")
```

## Troubleshooting

### "TRL not installed"
```bash
pip install trl torch peft accelerate
```

### "OpenRL not installed"
```bash
pip install openrl
```

### Low improvement rates
- Ensure sample outputs are diverse
- Check that prompts include clear structure requirements
- Try intensive coaching mode
- Consider adding domain-specific examples to prompts

### Memory issues during training
- Enable PEFT/LoRA (use_peft=True)
- Reduce batch size
- Use gradient accumulation
- Try a smaller base model

## Version History

- **1.0.0** (2025-11-30): Initial release
  - Full TRL integration (DPO, RLHF, SFT, PPO)
  - OpenRL integration
  - Prompt optimization system
  - Domain-specific rubrics
  - Pattern detection
  - Session management
  - Metrics tracking
