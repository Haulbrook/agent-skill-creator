"""
Metrics tracking for training sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from collections import defaultdict
import statistics


@dataclass
class MetricPoint:
    """A single metric measurement."""

    name: str
    value: float
    timestamp: str
    category: str = "general"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
            "category": self.category,
            "metadata": self.metadata,
        }


class MetricsTracker:
    """
    Tracks and aggregates metrics during training.

    Features:
    - Record metrics with timestamps
    - Aggregate by category
    - Compute statistics (mean, std, min, max)
    - Track trends over time
    """

    def __init__(self) -> None:
        """Initialize the metrics tracker."""
        self.metrics: list[MetricPoint] = []
        self.by_category: dict[str, list[MetricPoint]] = defaultdict(list)
        self.by_name: dict[str, list[MetricPoint]] = defaultdict(list)

    def record(
        self,
        category: str,
        values: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Record metrics for a category.

        Args:
            category: Category name (e.g., "analysis", "training")
            values: Dictionary of metric names to values
            metadata: Optional metadata
        """
        timestamp = datetime.now().isoformat()

        for name, value in values.items():
            if isinstance(value, (int, float)):
                point = MetricPoint(
                    name=name,
                    value=float(value),
                    timestamp=timestamp,
                    category=category,
                    metadata=metadata or {},
                )
                self.metrics.append(point)
                self.by_category[category].append(point)
                self.by_name[name].append(point)

    def get_metric(self, name: str) -> list[float]:
        """Get all values for a metric."""
        return [p.value for p in self.by_name.get(name, [])]

    def get_latest(self, name: str) -> Optional[float]:
        """Get the latest value for a metric."""
        points = self.by_name.get(name, [])
        return points[-1].value if points else None

    def get_stats(self, name: str) -> dict[str, float]:
        """Get statistics for a metric."""
        values = self.get_metric(name)

        if not values:
            return {}

        stats = {
            "count": len(values),
            "mean": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1],
        }

        if len(values) > 1:
            stats["std"] = statistics.stdev(values)
            stats["trend"] = values[-1] - values[0]

        return stats

    def get_category_stats(self, category: str) -> dict[str, dict[str, float]]:
        """Get statistics for all metrics in a category."""
        points = self.by_category.get(category, [])
        names = set(p.name for p in points)

        return {name: self.get_stats(name) for name in names}

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all tracked metrics."""
        summary = {
            "total_points": len(self.metrics),
            "categories": list(self.by_category.keys()),
            "metrics": list(self.by_name.keys()),
        }

        # Add per-category summaries
        category_summaries = {}
        for category in self.by_category:
            stats = self.get_category_stats(category)
            category_summaries[category] = {
                name: {
                    "latest": s.get("latest"),
                    "mean": s.get("mean"),
                }
                for name, s in stats.items()
            }

        summary["by_category"] = category_summaries

        return summary

    def get_trend(
        self,
        name: str,
        window: int = 5,
    ) -> Optional[str]:
        """
        Determine the trend direction for a metric.

        Returns: "improving", "declining", or "stable"
        """
        values = self.get_metric(name)

        if len(values) < window:
            return None

        recent = values[-window:]
        older = values[-2 * window : -window] if len(values) >= 2 * window else values[: window]

        recent_mean = statistics.mean(recent)
        older_mean = statistics.mean(older)

        diff = recent_mean - older_mean
        threshold = 0.05 * abs(older_mean) if older_mean != 0 else 0.01

        if diff > threshold:
            return "improving"
        elif diff < -threshold:
            return "declining"
        else:
            return "stable"

    def to_dict(self) -> dict[str, Any]:
        """Convert tracker to dictionary."""
        return {
            "metrics": [m.to_dict() for m in self.metrics],
            "summary": self.get_summary(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetricsTracker":
        """Create tracker from dictionary."""
        tracker = cls()

        for m in data.get("metrics", []):
            point = MetricPoint(
                name=m["name"],
                value=m["value"],
                timestamp=m["timestamp"],
                category=m.get("category", "general"),
                metadata=m.get("metadata", {}),
            )
            tracker.metrics.append(point)
            tracker.by_category[point.category].append(point)
            tracker.by_name[point.name].append(point)

        return tracker

    def clear(self) -> None:
        """Clear all recorded metrics."""
        self.metrics.clear()
        self.by_category.clear()
        self.by_name.clear()
