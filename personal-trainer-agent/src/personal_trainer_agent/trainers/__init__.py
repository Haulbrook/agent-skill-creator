"""
Training modules for improving agents.
"""

from personal_trainer_agent.trainers.trl_trainer import TRLTrainer
from personal_trainer_agent.trainers.prompt_optimizer import PromptOptimizer

__all__ = ["TRLTrainer", "PromptOptimizer"]
