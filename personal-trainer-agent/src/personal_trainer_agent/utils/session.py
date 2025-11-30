"""
Training session management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import json
from pathlib import Path
import uuid


@dataclass
class Iteration:
    """A single training iteration."""

    id: str
    timestamp: str
    method: str
    metrics_before: dict[str, float]
    metrics_after: dict[str, float]
    improvement: dict[str, float]
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "method": self.method,
            "metrics_before": self.metrics_before,
            "metrics_after": self.metrics_after,
            "improvement": self.improvement,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Iteration":
        return cls(**data)


@dataclass
class TrainingSession:
    """
    Manages a training session with history and state.

    Tracks:
    - Training iterations and their results
    - Improvement plans
    - Cumulative metrics
    - Session metadata
    """

    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "active"
    plan: Optional[dict[str, Any]] = None
    iterations: list[Iteration] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def set_plan(self, plan: dict[str, Any]) -> None:
        """Set the improvement plan for this session."""
        self.plan = plan
        self.metadata["plan_set_at"] = datetime.now().isoformat()

    def record_iteration(self, result: dict[str, Any]) -> Iteration:
        """Record a training iteration."""
        iteration = Iteration(
            id=f"{self.id}-{len(self.iterations):03d}",
            timestamp=datetime.now().isoformat(),
            method=result.get("method", "unknown"),
            metrics_before=result.get("before", {}),
            metrics_after=result.get("after", {}),
            improvement=result.get("improvement", {}),
            notes=result.get("notes", ""),
        )

        self.iterations.append(iteration)
        return iteration

    @property
    def iteration_count(self) -> int:
        """Number of iterations in this session."""
        return len(self.iterations)

    @property
    def total_improvement(self) -> dict[str, float]:
        """Calculate total improvement across all iterations."""
        if not self.iterations:
            return {}

        total = {}
        for iteration in self.iterations:
            for key, value in iteration.improvement.items():
                total[key] = total.get(key, 0) + value

        return total

    @property
    def latest_metrics(self) -> dict[str, float]:
        """Get metrics from the latest iteration."""
        if not self.iterations:
            return {}
        return self.iterations[-1].metrics_after

    def complete(self) -> None:
        """Mark the session as complete."""
        self.status = "completed"
        self.metadata["completed_at"] = datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "name": self.name,
            "id": self.id,
            "created_at": self.created_at,
            "status": self.status,
            "plan": self.plan,
            "iterations": [i.to_dict() for i in self.iterations],
            "iteration_count": self.iteration_count,
            "total_improvement": self.total_improvement,
            "latest_metrics": self.latest_metrics,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrainingSession":
        """Create session from dictionary."""
        iterations = [
            Iteration.from_dict(i)
            for i in data.get("iterations", [])
        ]

        return cls(
            name=data.get("name", "unknown"),
            id=data.get("id", str(uuid.uuid4())[:8]),
            created_at=data.get("created_at", datetime.now().isoformat()),
            status=data.get("status", "active"),
            plan=data.get("plan"),
            iterations=iterations,
            metadata=data.get("metadata", {}),
        )

    def save(self, path: Path) -> None:
        """Save session to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "TrainingSession":
        """Load session from file."""
        with open(path) as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_summary(self) -> str:
        """Get a human-readable summary of the session."""
        lines = [
            f"Session: {self.name} ({self.id})",
            f"Status: {self.status}",
            f"Created: {self.created_at}",
            f"Iterations: {self.iteration_count}",
        ]

        if self.total_improvement:
            lines.append("Total Improvement:")
            for key, value in self.total_improvement.items():
                sign = "+" if value > 0 else ""
                lines.append(f"  {key}: {sign}{value:.3f}")

        return "\n".join(lines)
