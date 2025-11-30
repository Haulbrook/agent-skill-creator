# Training Methodologies Guide

This guide covers the different approaches for improving AI agents, from prompt optimization to full reinforcement learning.

## Training Approach Decision Tree

```
Is your agent's base model fixed (e.g., API-based)?
├── YES → Use Prompt Optimization
│         (No model weights to change)
│
└── NO → Do you have preference/rating data?
         ├── YES → Do you have >1000 preference pairs?
         │         ├── YES → Use DPO or RLHF
         │         └── NO → Start with SFT on best examples
         │
         └── NO → Can you define a reward function?
                  ├── YES → Use OpenRL with custom rewards
                  └── NO → Collect data first, then DPO
```

## 1. Prompt Optimization

**Best for:** API-based agents, quick improvements, no compute resources needed

### When to Use
- You don't have access to model weights (using GPT-4, Claude, etc.)
- You want quick improvements without training infrastructure
- You're iterating rapidly on agent behavior

### How It Works
1. Analyze current prompts and output patterns
2. Identify weaknesses through evaluation
3. Systematically improve prompts based on feedback
4. A/B test prompt variants

### Key Techniques

#### Structure Improvement
Add explicit output format requirements:
```
# Before
You are a helpful assistant.

# After
You are a helpful assistant.

## Output Format
1. Brief acknowledgment of the request
2. Structured response with clear sections
3. Summary and next steps if applicable
```

#### Constraint Addition
Add explicit constraints to prevent common issues:
```
## Important Constraints
- ALWAYS include specific examples
- NEVER use placeholder text
- Keep responses under 500 words unless asked for more
```

#### Example Injection
Include example outputs in the prompt:
```
## Example
User: How do I reset my password?
Assistant: I'll help you reset your password. Here are the steps:
1. Go to the login page
2. Click "Forgot Password"
3. Enter your email address
...
```

## 2. Supervised Fine-Tuning (SFT)

**Best for:** Establishing baseline behavior, limited high-quality data

### When to Use
- You have examples of ideal outputs
- Starting point before RLHF/DPO
- Less than 1000 examples available

### How It Works
1. Collect high-quality output examples
2. Filter to only the best outputs (score >= 7/10)
3. Fine-tune model to reproduce these outputs

### Data Requirements
- 100-500 high-quality examples minimum
- Diverse inputs covering expected use cases
- Clear, consistent output style

### Best Practices
- Use quality threshold (only include outputs rated 7+/10)
- Include diverse examples, not just easy cases
- Validate on held-out set to prevent overfitting

## 3. Direct Preference Optimization (DPO)

**Best for:** Learning from human preferences without complex RL

### When to Use
- You have preference pairs (better vs worse outputs)
- Want simpler training than full RLHF
- 500+ preference pairs available

### How It Works
1. Collect pairs of outputs for same input
2. Label which output is preferred
3. Train model to prefer better outputs directly

### Data Format
```json
{
    "prompt": "Write a product description for a fitness tracker",
    "chosen": "Transform your fitness journey with the FitPro X...",
    "rejected": "This is a fitness tracker that tracks your steps..."
}
```

### Best Practices
- Ensure clear preference signal (don't use similar quality pairs)
- Include diverse prompt types
- Balance easy and hard comparisons
- Use 0.1 ≤ β ≤ 0.3 (start with 0.1)

## 4. RLHF (Reinforcement Learning from Human Feedback)

**Best for:** Maximum control over behavior, large-scale training

### When to Use
- You have significant training resources
- Need fine-grained control over behavior
- Have infrastructure for reward model training

### How It Works
1. Train reward model on human preferences
2. Use reward model to score outputs
3. Train policy with PPO to maximize reward

### Pipeline
```
Human Preferences → Reward Model Training → PPO Training
```

### Best Practices
- Train robust reward model first (validate on held-out data)
- Use KL penalty to prevent reward hacking
- Monitor for mode collapse
- Start with conservative hyperparameters

## 5. PPO Training

**Best for:** Online learning, exploration-exploitation balance

### When to Use
- Agent needs to explore different strategies
- Environment feedback available
- Fine-grained behavior control needed

### Key Hyperparameters
- `learning_rate`: 1e-5 to 5e-5 (lower for stability)
- `clip_range`: 0.1 to 0.3 (lower = more conservative)
- `kl_penalty`: 0.1 to 0.3 (prevents drift from reference)
- `ppo_epochs`: 4-10 per batch

## 6. OpenRL Custom Training

**Best for:** Custom environments, complex reward functions

### When to Use
- Need custom reward logic
- Want to simulate agent interactions
- Building agents for specific environments

### Custom Reward Functions
```python
def custom_reward(context, output):
    reward = 0.0

    # Task completion reward
    if task_completed(output):
        reward += 1.0

    # Quality bonus
    quality_score = evaluate_quality(output)
    reward += quality_score * 0.5

    # Efficiency penalty
    if len(output) > max_length:
        reward -= 0.2

    return reward
```

## Comparison Table

| Approach | Compute | Data Needed | Improvement | Complexity |
|----------|---------|-------------|-------------|------------|
| Prompt Optimization | None | Examples | 10-30% | Low |
| SFT | Medium | 100-500 | 20-40% | Medium |
| DPO | Medium | 500-2000 pairs | 30-50% | Medium |
| RLHF | High | 1000+ ratings | 40-60% | High |
| PPO | High | Reward signal | 30-50% | High |
| OpenRL | High | Custom rewards | Variable | High |

## Recommended Progression

1. **Start with Prompt Optimization**
   - Quick wins with no infrastructure
   - Identify what needs to improve

2. **Collect Training Data**
   - Save good and bad outputs
   - Have humans rate outputs

3. **Try SFT on Best Examples**
   - Establish baseline behavior
   - Quick training, clear results

4. **Move to DPO**
   - Learn from preference data
   - Simpler than full RLHF

5. **Full RLHF if Needed**
   - Maximum control
   - Requires significant resources

## Common Pitfalls

### Reward Hacking
Model finds shortcuts to maximize reward without genuine improvement.
**Solution:** Use diverse evaluation, KL penalty, human spot-checks

### Overfitting
Model memorizes training data instead of learning generalizable patterns.
**Solution:** Use validation set, early stopping, data augmentation

### Mode Collapse
Model converges to single output style, losing diversity.
**Solution:** Entropy bonus, diverse training data, temperature tuning

### Distribution Shift
Improved model produces outputs very different from training distribution.
**Solution:** KL penalty, conservative updates, gradual training
