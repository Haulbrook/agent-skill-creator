"""
Personal Trainer Agent - A meta-skill for improving AI agents and bots.

This package provides tools for:
- Analyzing agent/bot performance with structured rubrics
- Generating training data for RLHF/DPO fine-tuning
- Integrating with TRL and OpenRL for actual RL training
- Iterative coaching and prompt optimization
- Metrics tracking and comparative evaluation
"""

from .main import PersonalTrainerAgent

__version__ = "1.0.0"
__all__ = ["PersonalTrainerAgent"]
