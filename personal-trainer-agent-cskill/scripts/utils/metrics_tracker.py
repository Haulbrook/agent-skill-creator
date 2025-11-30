"""
Metrics Tracker - Tracks and analyzes training metrics over time.

This module provides:
- Evaluation metrics storage
- Progress tracking
- Visualization-ready data export
- Statistical analysis
"""

import json
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MetricsTracker:
    """
    Tracks training metrics over time.

    Features:
    - Store evaluation scores per session
    - Track improvement trends
    - Calculate statistical summaries
    - Export data for visualization

    Usage:
        tracker = MetricsTracker(storage_path)

        # Initialize for session
        tracker.initialize_session(session_id, agent_name)

        # Record evaluations
        tracker.record_evaluation(session_id, score, dimensions)

        # Get summary
        summary = tracker.get_session_summary(session_id)

        # Export for visualization
        data = tracker.export_for_visualization(session_id)
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the metrics tracker.

        Args:
            storage_dir: Directory for storing metrics data
        """
        self.storage_dir = storage_dir or Path.home() / ".personal_trainer_agent" / "metrics"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self._session_metrics: Dict[str, Dict[str, Any]] = {}

    def initialize_session(
        self,
        session_id: str,
        agent_name: str
    ) -> None:
        """
        Initialize metrics tracking for a session.

        Args:
            session_id: Session ID
            agent_name: Name of the agent being trained
        """
        self._session_metrics[session_id] = {
            "agent_name": agent_name,
            "started_at": datetime.now().isoformat(),
            "evaluations": [],
            "improvements": [],
            "dimension_history": defaultdict(list)
        }

    def record_evaluation(
        self,
        session_id: str,
        overall_score: float,
        dimension_scores: Dict[str, float]
    ) -> None:
        """
        Record an evaluation result.

        Args:
            session_id: Session ID
            overall_score: Overall evaluation score (0-10)
            dimension_scores: Scores by dimension
        """
        if session_id not in self._session_metrics:
            self._session_metrics[session_id] = {
                "evaluations": [],
                "improvements": [],
                "dimension_history": defaultdict(list)
            }

        metrics = self._session_metrics[session_id]

        # Record evaluation
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score,
            "dimension_scores": dimension_scores
        }
        metrics["evaluations"].append(evaluation)

        # Update dimension history
        for dim, score in dimension_scores.items():
            metrics["dimension_history"][dim].append(score)

        # Persist
        self._save_metrics(session_id)

    def record_improvement(
        self,
        session_id: str,
        improvement_percentage: float,
        improved_dimensions: List[str]
    ) -> None:
        """
        Record an improvement observation.

        Args:
            session_id: Session ID
            improvement_percentage: Percentage improvement observed
            improved_dimensions: Dimensions that improved
        """
        if session_id not in self._session_metrics:
            return

        metrics = self._session_metrics[session_id]
        metrics["improvements"].append({
            "timestamp": datetime.now().isoformat(),
            "percentage": improvement_percentage,
            "dimensions": improved_dimensions
        })

        self._save_metrics(session_id)

    def get_all_evaluations(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all evaluations for a session.

        Args:
            session_id: Session ID

        Returns:
            List of evaluation records
        """
        if session_id in self._session_metrics:
            return self._session_metrics[session_id].get("evaluations", [])

        # Try loading from disk
        metrics = self._load_metrics(session_id)
        if metrics:
            return metrics.get("evaluations", [])

        return []

    def get_session_summary(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a session.

        Args:
            session_id: Session ID

        Returns:
            Summary statistics dictionary
        """
        metrics = self._session_metrics.get(session_id)
        if not metrics:
            metrics = self._load_metrics(session_id)

        if not metrics or not metrics.get("evaluations"):
            return {"error": "No metrics available"}

        evaluations = metrics["evaluations"]
        scores = [e["overall_score"] for e in evaluations]

        # Basic statistics
        summary = {
            "total_evaluations": len(evaluations),
            "average_score": round(statistics.mean(scores), 2),
            "min_score": round(min(scores), 2),
            "max_score": round(max(scores), 2),
            "score_std_dev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
            "first_score": scores[0] if scores else None,
            "latest_score": scores[-1] if scores else None
        }

        # Improvement calculation
        if len(scores) >= 2:
            first_avg = statistics.mean(scores[:max(1, len(scores) // 5)])
            last_avg = statistics.mean(scores[-max(1, len(scores) // 5):])
            improvement = last_avg - first_avg
            summary["overall_improvement"] = round(improvement, 2)
            summary["improvement_percentage"] = round(
                (improvement / first_avg * 100) if first_avg > 0 else 0, 1
            )
        else:
            summary["overall_improvement"] = 0
            summary["improvement_percentage"] = 0

        # Dimension summaries
        dim_history = metrics.get("dimension_history", {})
        summary["dimension_summaries"] = {}

        for dim, dim_scores in dim_history.items():
            if dim_scores:
                summary["dimension_summaries"][dim] = {
                    "average": round(statistics.mean(dim_scores), 2),
                    "trend": self._calculate_trend(dim_scores)
                }

        # Improvement events
        improvements = metrics.get("improvements", [])
        summary["improvement_events"] = len(improvements)
        if improvements:
            avg_improvement = statistics.mean([i["percentage"] for i in improvements])
            summary["average_improvement_per_event"] = round(avg_improvement, 1)

        return summary

    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction from scores."""
        if len(scores) < 3:
            return "insufficient_data"

        # Compare first third to last third
        third = max(1, len(scores) // 3)
        first_third = statistics.mean(scores[:third])
        last_third = statistics.mean(scores[-third:])

        diff = last_third - first_third
        if diff > 0.5:
            return "improving"
        elif diff < -0.5:
            return "declining"
        else:
            return "stable"

    def export_for_visualization(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Export metrics in a format suitable for visualization.

        Args:
            session_id: Session ID

        Returns:
            Data structure for charting libraries
        """
        metrics = self._session_metrics.get(session_id)
        if not metrics:
            metrics = self._load_metrics(session_id)

        if not metrics:
            return {"error": "No metrics available"}

        evaluations = metrics.get("evaluations", [])

        # Time series data
        timeline = {
            "timestamps": [],
            "overall_scores": [],
            "dimension_series": defaultdict(list)
        }

        for eval_record in evaluations:
            timeline["timestamps"].append(eval_record["timestamp"])
            timeline["overall_scores"].append(eval_record["overall_score"])

            for dim, score in eval_record.get("dimension_scores", {}).items():
                timeline["dimension_series"][dim].append(score)

        # Distribution data
        scores = [e["overall_score"] for e in evaluations]
        distribution = {
            "score_histogram": self._create_histogram(scores),
            "quartiles": self._calculate_quartiles(scores) if scores else {}
        }

        # Dimension comparison
        dim_history = metrics.get("dimension_history", {})
        dimension_comparison = {
            dim: {
                "average": statistics.mean(scores) if scores else 0,
                "latest": scores[-1] if scores else 0,
                "trend": self._calculate_trend(scores)
            }
            for dim, scores in dim_history.items()
        }

        return {
            "timeline": dict(timeline),
            "distribution": distribution,
            "dimension_comparison": dimension_comparison,
            "summary": self.get_session_summary(session_id)
        }

    def _create_histogram(
        self,
        scores: List[float],
        bins: int = 10
    ) -> Dict[str, int]:
        """Create histogram data from scores."""
        if not scores:
            return {}

        histogram = defaultdict(int)
        bin_width = 10 / bins

        for score in scores:
            bin_idx = min(int(score / bin_width), bins - 1)
            bin_label = f"{bin_idx * bin_width:.1f}-{(bin_idx + 1) * bin_width:.1f}"
            histogram[bin_label] += 1

        return dict(histogram)

    def _calculate_quartiles(
        self,
        scores: List[float]
    ) -> Dict[str, float]:
        """Calculate quartile statistics."""
        if len(scores) < 4:
            return {}

        sorted_scores = sorted(scores)
        n = len(sorted_scores)

        return {
            "q1": sorted_scores[n // 4],
            "median": statistics.median(sorted_scores),
            "q3": sorted_scores[3 * n // 4],
            "iqr": sorted_scores[3 * n // 4] - sorted_scores[n // 4]
        }

    def compare_sessions(
        self,
        session_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare metrics across multiple sessions.

        Args:
            session_ids: List of session IDs to compare

        Returns:
            Comparison data
        """
        comparisons = {}

        for session_id in session_ids:
            summary = self.get_session_summary(session_id)
            if "error" not in summary:
                comparisons[session_id] = {
                    "average_score": summary.get("average_score"),
                    "improvement": summary.get("overall_improvement"),
                    "evaluations": summary.get("total_evaluations")
                }

        if not comparisons:
            return {"error": "No valid sessions to compare"}

        # Rank sessions by improvement
        ranked = sorted(
            comparisons.items(),
            key=lambda x: x[1].get("improvement", 0),
            reverse=True
        )

        return {
            "session_metrics": comparisons,
            "best_session": ranked[0][0] if ranked else None,
            "ranking": [s[0] for s in ranked]
        }

    def get_global_statistics(self) -> Dict[str, Any]:
        """
        Get statistics across all tracked sessions.

        Returns:
            Global statistics dictionary
        """
        all_metrics_files = list(self.storage_dir.glob("*.json"))

        if not all_metrics_files:
            return {"error": "No metrics data available"}

        all_scores = []
        all_improvements = []
        session_count = 0

        for metrics_file in all_metrics_files:
            try:
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)

                evaluations = metrics.get("evaluations", [])
                for eval_record in evaluations:
                    all_scores.append(eval_record.get("overall_score", 0))

                improvements = metrics.get("improvements", [])
                for imp in improvements:
                    all_improvements.append(imp.get("percentage", 0))

                session_count += 1

            except Exception:
                continue

        if not all_scores:
            return {"error": "No evaluation data available"}

        return {
            "total_sessions": session_count,
            "total_evaluations": len(all_scores),
            "global_average_score": round(statistics.mean(all_scores), 2),
            "global_score_std_dev": round(statistics.stdev(all_scores), 2) if len(all_scores) > 1 else 0,
            "total_improvement_events": len(all_improvements),
            "average_improvement": round(statistics.mean(all_improvements), 1) if all_improvements else 0
        }

    def _save_metrics(self, session_id: str) -> None:
        """Save metrics to disk."""
        if session_id not in self._session_metrics:
            return

        metrics = self._session_metrics[session_id]
        metrics_file = self.storage_dir / f"{session_id}.json"

        # Convert defaultdict to dict for JSON serialization
        save_data = {
            **metrics,
            "dimension_history": dict(metrics.get("dimension_history", {}))
        }

        try:
            with open(metrics_file, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving metrics: {e}")

    def _load_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load metrics from disk."""
        metrics_file = self.storage_dir / f"{session_id}.json"

        if not metrics_file.exists():
            return None

        try:
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)

            # Convert dimension_history back to defaultdict
            if "dimension_history" in metrics:
                metrics["dimension_history"] = defaultdict(
                    list, metrics["dimension_history"]
                )

            # Cache in memory
            self._session_metrics[session_id] = metrics

            return metrics

        except Exception as e:
            print(f"Error loading metrics: {e}")
            return None

    def clear_session_metrics(self, session_id: str) -> bool:
        """
        Clear metrics for a session.

        Args:
            session_id: Session ID

        Returns:
            True if cleared successfully
        """
        # Remove from memory
        if session_id in self._session_metrics:
            del self._session_metrics[session_id]

        # Remove from disk
        metrics_file = self.storage_dir / f"{session_id}.json"
        if metrics_file.exists():
            try:
                metrics_file.unlink()
                return True
            except Exception:
                return False

        return True
