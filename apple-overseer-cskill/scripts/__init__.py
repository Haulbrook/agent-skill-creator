"""
Apple Overseer - Multi-Level Quality Control System for Apple Platforms

This package provides a comprehensive validation system for Apple platform projects,
structured like a multi-story building with checkpoint managers at each level.
"""
from .main import AppleOverseer
from .models import (
    CheckpointStatus,
    CheckpointLevel,
    Platform,
    Issue,
    CheckpointReport,
    PlatformValidationResult,
    OverseerReport
)

__version__ = "1.0.0"

__all__ = [
    "AppleOverseer",
    "CheckpointStatus",
    "CheckpointLevel",
    "Platform",
    "Issue",
    "CheckpointReport",
    "PlatformValidationResult",
    "OverseerReport",
]
