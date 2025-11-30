# Integration Guides

This guide covers how to set up and use the TRL and OpenRL integrations for training agents.

## TRL Setup

### Installation

```bash
pip install trl transformers torch peft accelerate datasets
```

### Verify Installation

```python
import trl
import transformers
import torch
import peft

print(f"TRL version: {trl.__version__}")
print(f"Transformers version: {transformers.__version__}")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

### Configuration Options

```python
from scripts.trainers.trl_trainer import TRLConfig

config = TRLConfig(
    # Model settings
    model_name_or_path="mistralai/Mistral-7B-v0.1",
    tokenizer_name=None,  # Uses model's tokenizer
    use_peft=True,  # Enable LoRA for efficiency

    # Training settings
    learning_rate=1e-5,
    batch_size=4,
    gradient_accumulation_steps=4,
    num_epochs=3,
    max_length=512,
    warmup_steps=100,

    # DPO specific
    dpo_beta=0.1,  # KL penalty coefficient

    # PPO specific
    ppo_epochs=4,
    target_kl=0.1,

    # Output
    output_dir="./trl_output",
    logging_steps=10,
    save_steps=100,

    # Hardware
    fp16=True,  # Use mixed precision
    device_map="auto"  # Auto-distribute across GPUs
)
```

### DPO Training Example

```python
from scripts.trainers.trl_trainer import TRLTrainer

# Initialize trainer
trainer = TRLTrainer({
    "model_name_or_path": "meta-llama/Llama-2-7b-hf",
    "use_peft": True,
    "learning_rate": 5e-6,
    "num_epochs": 3,
    "dpo_beta": 0.1
})

# Prepare data
preference_data = [
    {
        "prompt": "Write a greeting for a professional email",
        "chosen": "Dear [Name],\n\nI hope this email finds you well.",
        "rejected": "Hey there! What's up?"
    },
    # ... more examples
]

# Train
result = trainer.train_dpo(
    preference_data,
    model_info={"name": "meta-llama/Llama-2-7b-hf"}
)

if result.success:
    print(f"Model saved to: {result.model_path}")
    print(f"Final loss: {result.metrics['train_loss']}")
else:
    print(f"Training failed: {result.error}")
```

### SFT Training Example

```python
# Prepare high-quality examples
sft_data = [
    {
        "prompt": "Explain photosynthesis",
        "completion": "Photosynthesis is the process by which plants convert sunlight into energy..."
    },
    # ... more examples
]

result = trainer.train_sft(sft_data)
```

### Generating Training Scripts

For running training outside the agent:

```python
script = trainer.generate_training_script(
    data_path="./training_data.json",
    training_type="dpo",
    config={"learning_rate": 5e-6}
)

# Save and run
with open("train_dpo.py", "w") as f:
    f.write(script)

# Run: python train_dpo.py
```

## OpenRL Setup

### Installation

```bash
pip install openrl numpy
```

### Custom Environment Setup

```python
from scripts.trainers.openrl_trainer import OpenRLTrainer, AgentEnvironment

# Define your agent profile
class MyAgent:
    def __init__(self):
        self.domain = "general"

    def generate(self, prompt):
        # Your agent's generation logic
        return "Agent response"

# Create environment
def reward_function(context, output):
    score = 0.0

    # Your scoring logic
    if len(output) > 100:
        score += 0.3
    if "specific" in output.lower():
        score += 0.3

    return score

agent = MyAgent()
env = AgentEnvironment(
    agent_profile=agent,
    reward_function=reward_function,
    max_steps=100
)
```

### OpenRL Training Example

```python
openrl_trainer = OpenRLTrainer({
    "algorithm": "ppo",
    "learning_rate": 3e-4,
    "n_steps": 2048,
    "batch_size": 64,
    "n_epochs": 10,
    "gamma": 0.99
})

# Create reward function from rubric
reward_fn = openrl_trainer.create_reward_function(
    rubric=custom_rubric,
    weights={"quality": 0.4, "relevance": 0.3, "completeness": 0.3}
)

# Train
result = openrl_trainer.train(
    agent_profile=agent,
    environment_config={"max_steps": 100},
    reward_function=reward_fn
)

print(f"Final average reward: {result.metrics['final_avg_reward']}")
```

### Custom Reward Functions

```python
def comprehensive_reward(context, output):
    """
    Multi-factor reward function for agent training.
    """
    reward = 0.0

    # Content quality (0-0.4)
    if output and len(output) > 50:
        reward += 0.1  # Non-trivial response
    if "\n" in output:
        reward += 0.1  # Structured response
    if any(word in output.lower() for word in ["because", "therefore", "since"]):
        reward += 0.1  # Explanatory
    if any(word in output.lower() for word in ["example", "instance", "such as"]):
        reward += 0.1  # Includes examples

    # Relevance (0-0.3)
    context_keywords = set(context.get("content", "").lower().split())
    output_keywords = set(output.lower().split())
    overlap = len(context_keywords & output_keywords)
    relevance = min(overlap / max(len(context_keywords), 1), 0.3)
    reward += relevance

    # Penalties (-0.3 to 0)
    if "sorry" in output.lower() or "apologize" in output.lower():
        reward -= 0.1
    if "as an ai" in output.lower():
        reward -= 0.1
    if len(output) > 2000:  # Too long
        reward -= 0.1

    return max(0, min(1, reward))  # Clamp to 0-1
```

## Integration with Personal Trainer Agent

### Full Training Pipeline

```python
from scripts.main import PersonalTrainerAgent, TrainingMode

# Initialize
trainer = PersonalTrainerAgent()

# Create profile
profile = trainer.create_agent_profile(
    name="MyBot",
    description="A bot that does X",
    domain="general",
    sample_outputs=load_outputs(),
    known_weaknesses=["issue1", "issue2"]
)

# Phase 1: Prompt Optimization
session = trainer.start_training_session(
    profile,
    mode=TrainingMode.PROMPT_OPTIMIZATION
)

for i in range(5):
    outputs = run_agent(current_prompts)
    result = trainer.run_coaching_iteration(session, outputs)
    current_prompts = result["optimized_prompts"]

    if result["average_score"] > 8:
        break

# Phase 2: Generate Training Data
training_data = trainer.generate_training_data(session, format_type="dpo")

# Phase 3: Run TRL Training
session = trainer.start_training_session(
    profile,
    mode=TrainingMode.TRL_DPO
)

result = trainer.run_trl_training(session, training_data, config={
    "learning_rate": 5e-6,
    "num_epochs": 3
})

# Phase 4: Evaluate Trained Model
# Load trained model and evaluate
final_outputs = run_trained_model(result.model_path)
final_eval = trainer.evaluate_outputs(session, final_outputs)
print(f"Post-training score: {final_eval}")
```

## Hardware Requirements

### Minimum Requirements
- 16GB RAM
- NVIDIA GPU with 8GB VRAM (for 7B models with PEFT)
- 50GB disk space

### Recommended Requirements
- 32GB RAM
- NVIDIA GPU with 24GB VRAM (for full fine-tuning)
- 100GB SSD

### Memory Optimization

```python
config = {
    "use_peft": True,  # LoRA reduces memory 4-8x
    "fp16": True,  # Half precision
    "gradient_accumulation_steps": 8,  # Simulate larger batches
    "batch_size": 1,  # Minimum batch size
}
```

## Troubleshooting

### CUDA Out of Memory

```python
# Reduce batch size
config["batch_size"] = 1
config["gradient_accumulation_steps"] = 16

# Enable gradient checkpointing (in TRL)
training_args.gradient_checkpointing = True

# Use smaller model
config["model_name_or_path"] = "gpt2"  # For testing
```

### Slow Training

```python
# Increase batch size if memory allows
config["batch_size"] = 8

# Use multiple GPUs
config["device_map"] = "balanced"

# Enable mixed precision
config["fp16"] = True
```

### Training Instability

```python
# Lower learning rate
config["learning_rate"] = 1e-6

# Increase warmup
config["warmup_steps"] = 500

# Lower DPO beta
config["dpo_beta"] = 0.05
```
