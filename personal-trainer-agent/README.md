# Personal Trainer Agent

A meta-tool for systematically improving AI agents through evaluation, coaching, and RL training.

[![CI](https://github.com/Haulbrook/personal-trainer-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Haulbrook/personal-trainer-agent/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/personal-trainer-agent.svg)](https://badge.fury.io/py/personal-trainer-agent)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Personal Trainer Agent is a framework for analyzing, evaluating, and improving AI agent performance. It provides:

- **Performance Analysis**: Identify strengths and weaknesses in agent outputs
- **Rubric-based Evaluation**: Score outputs against custom criteria
- **Comparison Evaluation**: A/B test different agent versions
- **Prompt Optimization**: Evolutionary optimization of prompts
- **RL Training**: Fine-tune models with TRL (DPO, PPO)
- **Session Management**: Track training progress over time

## Installation

```bash
# Core installation
pip install personal-trainer-agent

# With TRL support (for RL training)
pip install personal-trainer-agent[trl]

# With all optional dependencies
pip install personal-trainer-agent[all]

# Development installation
pip install personal-trainer-agent[dev]
```

## Quick Start

### Analyze Agent Performance

```python
from personal_trainer_agent import PersonalTrainerAgent

trainer = PersonalTrainerAgent()

# Analyze agent outputs
outputs = [
    {"content": "Here's a helpful response...", "status": "completed"},
    {"content": "Another response...", "status": "completed"},
]

analysis = trainer.analyze(outputs)
print(f"Overall Score: {analysis['performance']['overall_score']:.1%}")
print(f"Weaknesses Found: {len(analysis['weaknesses'])}")
```

### Evaluate with Rubrics

```python
from personal_trainer_agent import PersonalTrainerAgent

trainer = PersonalTrainerAgent()

rubric = {
    "criteria": [
        {"name": "accuracy", "description": "Factually correct", "max_score": 10, "weight": 2.0},
        {"name": "clarity", "description": "Clear and readable", "max_score": 10, "weight": 1.0},
        {"name": "helpfulness", "description": "Actionable advice", "max_score": 10, "weight": 1.5},
    ]
}

outputs = [{"content": "Your detailed response here..."}]
results = trainer.evaluate(outputs, rubric)

print(f"Overall: {results['_overall']['percentage']:.1f}%")
for criterion in rubric["criteria"]:
    name = criterion["name"]
    print(f"  {name}: {results[name]['score']:.1f}/{results[name]['max']}")
```

### Compare Agent Versions

```python
from personal_trainer_agent import PersonalTrainerAgent

trainer = PersonalTrainerAgent()

# Compare old vs new agent outputs
old_outputs = [{"content": "Old response..."}]
new_outputs = [{"content": "New improved response..."}]

comparison = trainer.compare(old_outputs, new_outputs)
print(f"Result: {comparison['summary']}")
print(f"New version win rate: {comparison['win_rate_a']:.1%}")
```

### Optimize Prompts

```python
from personal_trainer_agent import PersonalTrainerAgent

trainer = PersonalTrainerAgent()

# Create improvement plan
analysis = trainer.analyze(outputs)
plan = trainer.create_improvement_plan(analysis)

# Run prompt optimization
result = trainer.train(plan)
print(f"Optimized prompt:\n{result['optimized_prompt']}")
print(f"Improvement: {result['improvement']:.1%}")
```

## CLI Usage

```bash
# Analyze agent outputs
trainer-agent analyze outputs.json --output analysis.json

# Evaluate with rubric
trainer-agent evaluate outputs.json --rubric rubric.json

# Run training
trainer-agent train plan.json --data training_data.json

# Manage sessions
trainer-agent session --load session.json
```

## Architecture

```
personal_trainer_agent/
├── main.py              # PersonalTrainerAgent orchestrator
├── cli.py               # Command-line interface
├── analyzers/           # Performance analysis
│   ├── performance.py   # Metrics computation
│   └── weakness.py      # Weakness detection
├── evaluators/          # Output evaluation
│   ├── rubric.py        # Rubric-based scoring
│   └── comparison.py    # A/B comparison
├── trainers/            # Training methods
│   ├── trl_trainer.py   # TRL (DPO/PPO)
│   └── prompt_optimizer.py  # Evolutionary optimization
└── utils/               # Utilities
    ├── session.py       # Training sessions
    └── metrics.py       # Metrics tracking
```

## Training Methods

### Prompt Optimization (Default)

Uses evolutionary algorithms to optimize prompts without model fine-tuning:

```python
from personal_trainer_agent.trainers import PromptOptimizer

optimizer = PromptOptimizer()
result = optimizer.optimize(
    plan={"improvements": [...]},
    examples=training_examples,
)
```

### TRL Training

Fine-tune models using Direct Preference Optimization (DPO) or PPO:

```python
from personal_trainer_agent.trainers import TRLTrainer

trainer = TRLTrainer()
result = trainer.train(
    plan={"training_method": "dpo"},
    dataset=[
        {"prompt": "...", "chosen": "good response", "rejected": "bad response"},
    ],
)
```

## Evaluation Metrics

### Performance Metrics
- **Overall Score**: Weighted combination of all metrics
- **Accuracy**: Correctness compared to expected outputs
- **Consistency**: Uniformity across similar queries
- **Response Quality**: Formatting, clarity, completeness
- **Task Completion**: Whether tasks are fully completed

### Weakness Categories
- **Accuracy**: Incorrect or uncertain information
- **Completeness**: Truncated or missing information
- **Format**: Structural or formatting issues
- **Consistency**: Behavioral inconsistencies
- **Safety**: PII exposure, injection risks

## Session Management

Track training progress across multiple iterations:

```python
from personal_trainer_agent import PersonalTrainerAgent

# Start a training session
trainer = PersonalTrainerAgent()
trainer.analyze(outputs)
plan = trainer.create_improvement_plan(analysis)
trainer.train(plan)

# Save session
trainer.save_session("session.json")

# Resume later
trainer = PersonalTrainerAgent.load_session("session.json")
print(trainer.session.get_summary())
```

## Configuration

```python
from personal_trainer_agent import PersonalTrainerAgent
from personal_trainer_agent.main import TrainingConfig

config = TrainingConfig(
    name="my-training-session",
    target_agent="my-agent-v1",
    training_method="prompt_optimization",  # or "trl"
    max_iterations=10,
    improvement_threshold=0.1,
)

trainer = PersonalTrainerAgent(config=config)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install dev dependencies (`pip install -e ".[dev]"`)
4. Make your changes
5. Run tests (`pytest`)
6. Run linting (`ruff check . && black .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [TRL](https://github.com/huggingface/trl) - Transformer Reinforcement Learning
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Click](https://click.palletsprojects.com/) - CLI framework
