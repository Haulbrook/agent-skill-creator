"""
Personal Trainer Agent - A meta-tool for systematically improving AI agents.

This package provides tools for:
- Analyzing agent performance and identifying weaknesses
- Evaluating agent outputs with rubrics and comparisons
- Training agents using RL (TRL, OpenRL) and prompt optimization
- Coaching agents through iterative improvement cycles
"""

from personal_trainer_agent.main import PersonalTrainerAgent
from personal_trainer_agent.analyzers import PerformanceAnalyzer, WeaknessDetector
from personal_trainer_agent.evaluators import RubricEvaluator, ComparisonEvaluator
from personal_trainer_agent.trainers import TRLTrainer, PromptOptimizer
from personal_trainer_agent.utils import TrainingSession, MetricsTracker

__version__ = "0.1.0"

__all__ = [
    "PersonalTrainerAgent",
    "PerformanceAnalyzer",
    "WeaknessDetector",
    "RubricEvaluator",
    "ComparisonEvaluator",
    "TRLTrainer",
    "PromptOptimizer",
    "TrainingSession",
    "MetricsTracker",
]
