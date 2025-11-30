# Personal Trainer Agent

> A meta-skill for systematically improving AI agents and bots through structured evaluation, iterative coaching, and integration with reinforcement learning frameworks.

## Overview

Built an AI agent that doesn't perform quite how you want? The Personal Trainer Agent helps you systematically improve your bots through:

- **Structured Evaluation** - Score outputs using domain-specific rubrics
- **Pattern Detection** - Identify recurring strengths and weaknesses
- **Prompt Optimization** - Improve prompts without model training
- **RL Training** - Integrate with TRL (DPO, RLHF, PPO) and OpenRL for actual fine-tuning
- **Progress Tracking** - Monitor improvement over time

## Quick Start

### Installation

```bash
# Core dependencies
pip install transformers datasets numpy rich

# For TRL training (optional)
pip install trl torch peft accelerate

# For OpenRL training (optional)
pip install openrl
```

### Basic Usage

```python
from scripts.main import PersonalTrainerAgent, TrainingMode

# Initialize trainer
trainer = PersonalTrainerAgent()

# Create profile for your bot
profile = trainer.create_agent_profile(
    name="WebsiteBuilder",
    description="Creates frontend websites from descriptions",
    domain="website_building",
    sample_outputs=[
        {"input": "Create a landing page", "output": "<html>..."},
    ],
    known_weaknesses=["designs look generic"]
)

# Start training session
session = trainer.start_training_session(
    profile,
    mode=TrainingMode.PROMPT_OPTIMIZATION
)

# Evaluate and improve
results = trainer.evaluate_outputs(session, your_bot_outputs)
recommendations = trainer.get_recommendations(session)

print(f"Average score: {results[0].overall_score}")
for rec in recommendations:
    print(f"- {rec.action}")
```

## Use Cases

### 1. Improve a Website Builder Bot

```python
profile = trainer.create_agent_profile(
    name="WebsiteBuilder",
    domain="website_building",
    known_weaknesses=["designs look generic", "uses inline styles"]
)

# Coaching loop
for i in range(10):
    outputs = run_bot(current_prompts)
    result = trainer.run_coaching_iteration(session, outputs)
    current_prompts = result["optimized_prompts"]

    print(f"Iteration {i+1}: {result['average_score']:.1f}/10")
```

### 2. Train a Marketing Bot with DPO

```python
profile = trainer.create_agent_profile(
    name="MarketingBot",
    domain="marketing",
    sample_outputs=marketing_samples
)

session = trainer.start_training_session(
    profile,
    mode=TrainingMode.TRL_DPO
)

# Generate training data from evaluations
training_data = trainer.generate_training_data(session, format_type="dpo")

# Run training
result = trainer.run_trl_training(session, training_data)
print(f"Model saved: {result.model_path}")
```

### 3. A/B Test Prompt Changes

```python
from scripts.evaluators.comparison_evaluator import ComparisonEvaluator

evaluator = ComparisonEvaluator()

# Compare outputs from two prompt versions
comparison = evaluator.compare(output_v1, output_v2)
print(f"Winner: Version {'B' if comparison['winner'] == 'b' else 'A'}")
print(f"Improvement: {comparison['improvement_percentage']}%")
```

## Training Modes

| Mode | Description | Compute | Use When |
|------|-------------|---------|----------|
| `ANALYSIS_ONLY` | Just analyze outputs | None | Understanding baseline |
| `PROMPT_OPTIMIZATION` | Improve prompts only | None | Using API-based models |
| `TRL_DPO` | Direct Preference Optimization | Medium | Have preference data |
| `TRL_RLHF` | Full RLHF pipeline | High | Need maximum control |
| `TRL_PPO` | PPO training | High | Online learning |
| `OPENRL` | Custom RL with environments | High | Custom reward functions |

## Supported Domains

Built-in evaluation rubrics for:
- **Website Building** - Visual design, code quality, responsiveness, accessibility
- **Marketing** - Messaging, audience targeting, CTAs, persuasion
- **Coding** - Correctness, readability, maintainability, performance
- **General** - Accuracy, completeness, clarity, usefulness

Create custom rubrics for any domain.

## Architecture

```
personal-trainer-agent-cskill/
├── scripts/
│   ├── main.py                    # Main orchestrator
│   ├── analyzers/                 # Output analysis
│   ├── trainers/                  # TRL, OpenRL, Prompt optimization
│   ├── evaluators/                # Rubric and comparison evaluation
│   └── utils/                     # Session and metrics management
├── references/                    # Documentation
└── assets/                        # Rubrics and configs
```

## Key Features

### Iterative Coaching
```python
for i in range(5):
    result = trainer.run_coaching_iteration(session, new_outputs)
    print(f"Score: {result['average_score']:.1f}, Change: {result['improvement_from_last']:+.1f}")
```

### Pattern Detection
```python
patterns = trainer.pattern_detector.detect(outputs, domain="coding")
for p in patterns:
    if p.pattern_type == "negative":
        print(f"Issue: {p.description} (in {p.frequency*100}% of outputs)")
```

### Training Data Generation
```python
# For DPO
dpo_data = trainer.generate_training_data(session, "dpo")
# {"prompt": ..., "chosen": ..., "rejected": ...}

# For SFT (high-quality only)
sft_data = trainer.generate_training_data(session, "sft")
# {"prompt": ..., "completion": ...}
```

### Progress Tracking
```python
progress = trainer.get_session_progress(session)
print(f"Improvement: {progress['overall_improvement']['percentage_improvement']}%")
```

## Dependencies

**Required:**
- Python >= 3.9
- transformers
- datasets
- numpy
- rich

**For TRL Training:**
- trl
- torch
- peft
- accelerate

**For OpenRL:**
- openrl

## Documentation

- [SKILL.md](SKILL.md) - Complete skill documentation
- [references/training-methodologies.md](references/training-methodologies.md) - Training approach guide
- [references/evaluation-rubrics.md](references/evaluation-rubrics.md) - Rubric creation guide
- [references/integration-guides.md](references/integration-guides.md) - TRL/OpenRL setup

## Example: Full Training Pipeline

```python
from scripts.main import PersonalTrainerAgent, TrainingMode, CoachingIntensity

trainer = PersonalTrainerAgent()

# 1. Create profile
profile = trainer.create_agent_profile(
    name="MyBot",
    description="Does something useful",
    domain="general",
    sample_outputs=my_outputs
)

# 2. Prompt optimization phase
session = trainer.start_training_session(
    profile, mode=TrainingMode.PROMPT_OPTIMIZATION
)

for _ in range(5):
    result = trainer.run_coaching_iteration(session, outputs)
    prompts = result["optimized_prompts"]

# 3. Collect preference data
# ... run bot with optimized prompts, collect ratings ...

# 4. DPO training phase
session = trainer.start_training_session(
    profile, mode=TrainingMode.TRL_DPO
)

training_data = trainer.generate_training_data(session, "dpo")
result = trainer.run_trl_training(session, training_data)

# 5. Verify improvement
final_report = trainer.end_session(session)
print(f"Total improvement: {final_report['overall_improvement']}")
```

## License

MIT License - see LICENSE file for details.

## Support

For issues or questions:
- Check [references/](references/) for detailed documentation
- Open an issue in the repository
