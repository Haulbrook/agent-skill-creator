"""
Trainers for RL-based agent improvement.

Provides integrations with:
- TRL (Transformers Reinforcement Learning) for RLHF, DPO, PPO
- OpenRL for flexible RL training
- Prompt optimization for non-model training approaches
"""

from .trl_trainer import TRLTrainer
from .openrl_trainer import OpenRLTrainer
from .prompt_optimizer import PromptOptimizer

__all__ = ["TRLTrainer", "OpenRLTrainer", "PromptOptimizer"]
