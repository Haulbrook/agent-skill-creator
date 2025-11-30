"""
Performance analysis for agent outputs.
"""

from dataclasses import dataclass
from typing import Any, Optional
import statistics


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    overall_score: float
    accuracy: float
    consistency: float
    response_quality: float
    task_completion: float

    def to_dict(self) -> dict[str, float]:
        return {
            "overall_score": self.overall_score,
            "accuracy": self.accuracy,
            "consistency": self.consistency,
            "response_quality": self.response_quality,
            "task_completion": self.task_completion,
        }


class PerformanceAnalyzer:
    """
    Analyzes agent outputs to compute performance metrics.

    Metrics computed:
    - Overall score: Weighted combination of all metrics
    - Accuracy: How correct the outputs are (when expected available)
    - Consistency: How consistent the outputs are across similar inputs
    - Response quality: Quality of formatting, clarity, completeness
    - Task completion: Whether the task was fully completed
    """

    def __init__(
        self,
        weights: Optional[dict[str, float]] = None,
    ) -> None:
        """
        Initialize the analyzer.

        Args:
            weights: Optional custom weights for computing overall score
        """
        self.weights = weights or {
            "accuracy": 0.3,
            "consistency": 0.2,
            "response_quality": 0.25,
            "task_completion": 0.25,
        }

    def analyze(
        self,
        outputs: list[dict[str, Any]],
        expected: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Analyze agent outputs and compute performance metrics.

        Args:
            outputs: List of agent outputs to analyze
            expected: Optional expected outputs for accuracy computation

        Returns:
            Dictionary containing performance metrics
        """
        if not outputs:
            return {"error": "No outputs to analyze", "overall_score": 0}

        # Compute individual metrics
        accuracy = self._compute_accuracy(outputs, expected) if expected else 0.5
        consistency = self._compute_consistency(outputs)
        response_quality = self._compute_response_quality(outputs)
        task_completion = self._compute_task_completion(outputs)

        # Compute overall score
        overall = (
            self.weights["accuracy"] * accuracy
            + self.weights["consistency"] * consistency
            + self.weights["response_quality"] * response_quality
            + self.weights["task_completion"] * task_completion
        )

        metrics = PerformanceMetrics(
            overall_score=overall,
            accuracy=accuracy,
            consistency=consistency,
            response_quality=response_quality,
            task_completion=task_completion,
        )

        return {
            **metrics.to_dict(),
            "num_outputs": len(outputs),
            "has_expected": expected is not None,
        }

    def _compute_accuracy(
        self,
        outputs: list[dict[str, Any]],
        expected: list[dict[str, Any]],
    ) -> float:
        """Compute accuracy by comparing to expected outputs."""
        if len(outputs) != len(expected):
            # Partial comparison
            compare_count = min(len(outputs), len(expected))
        else:
            compare_count = len(outputs)

        if compare_count == 0:
            return 0.0

        matches = 0
        for i in range(compare_count):
            output = outputs[i]
            exp = expected[i]

            # Compare based on available fields
            if "content" in output and "content" in exp:
                similarity = self._text_similarity(
                    str(output["content"]),
                    str(exp["content"]),
                )
                if similarity > 0.8:
                    matches += 1
            elif "result" in output and "result" in exp:
                if output["result"] == exp["result"]:
                    matches += 1
            elif output == exp:
                matches += 1

        return matches / compare_count

    def _compute_consistency(self, outputs: list[dict[str, Any]]) -> float:
        """Compute consistency across outputs."""
        if len(outputs) < 2:
            return 1.0

        # Check for consistent structure
        structures = []
        for output in outputs:
            structure = frozenset(output.keys())
            structures.append(structure)

        # Compute structure consistency
        unique_structures = len(set(structures))
        structure_consistency = 1.0 / unique_structures

        # Check for consistent response lengths (if applicable)
        lengths = []
        for output in outputs:
            if "content" in output:
                lengths.append(len(str(output["content"])))

        if lengths:
            mean_length = statistics.mean(lengths)
            if mean_length > 0:
                std_dev = statistics.stdev(lengths) if len(lengths) > 1 else 0
                length_consistency = max(0, 1 - (std_dev / mean_length))
            else:
                length_consistency = 1.0
        else:
            length_consistency = 1.0

        return (structure_consistency + length_consistency) / 2

    def _compute_response_quality(self, outputs: list[dict[str, Any]]) -> float:
        """Compute quality of responses."""
        quality_scores = []

        for output in outputs:
            score = 0.0
            checks = 0

            # Check for content presence
            if "content" in output and output["content"]:
                score += 1.0
                checks += 1

                content = str(output["content"])

                # Check for reasonable length
                if 10 < len(content) < 10000:
                    score += 1.0
                checks += 1

                # Check for proper formatting (not just raw data)
                if not content.startswith("{") and not content.startswith("["):
                    score += 0.5
                checks += 1

            # Check for metadata
            if "metadata" in output or "confidence" in output:
                score += 0.5
                checks += 1

            # Check for error handling
            if "error" not in output or output.get("error") is None:
                score += 1.0
            checks += 1

            quality_scores.append(score / checks if checks > 0 else 0)

        return statistics.mean(quality_scores) if quality_scores else 0.0

    def _compute_task_completion(self, outputs: list[dict[str, Any]]) -> float:
        """Compute task completion rate."""
        completed = 0

        for output in outputs:
            # Check various indicators of completion
            if output.get("status") == "completed":
                completed += 1
            elif output.get("completed", False):
                completed += 1
            elif "error" not in output and output.get("content"):
                completed += 1
            elif output.get("result") is not None:
                completed += 1

        return completed / len(outputs) if outputs else 0.0

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Compute simple text similarity."""
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0
