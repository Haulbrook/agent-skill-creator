"""
Comparison-based evaluation of agent outputs.
"""

from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum


class ComparisonResult(str, Enum):
    """Result of comparing two outputs."""

    A_BETTER = "a_better"
    B_BETTER = "b_better"
    TIE = "tie"
    INCONCLUSIVE = "inconclusive"


@dataclass
class PairwiseComparison:
    """Result of comparing a single pair of outputs."""

    index: int
    result: ComparisonResult
    confidence: float
    reasoning: str
    scores_a: dict[str, float]
    scores_b: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "result": self.result.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "scores_a": self.scores_a,
            "scores_b": self.scores_b,
        }


class ComparisonEvaluator:
    """
    Compares agent outputs against baselines or alternatives.

    Useful for:
    - A/B testing different agent versions
    - Comparing against human baselines
    - Evaluating improvement after training

    Methods:
    - Pairwise comparison: Compare individual output pairs
    - Aggregate comparison: Compare overall distributions
    - Win rate: Calculate how often one set outperforms another
    """

    def __init__(
        self,
        comparison_dimensions: Optional[list[str]] = None,
    ) -> None:
        """
        Initialize the comparison evaluator.

        Args:
            comparison_dimensions: Dimensions to compare on
        """
        self.dimensions = comparison_dimensions or [
            "accuracy",
            "helpfulness",
            "clarity",
            "completeness",
        ]

    def compare(
        self,
        outputs_a: list[dict[str, Any]],
        outputs_b: list[dict[str, Any]],
        context: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Compare two sets of outputs.

        Args:
            outputs_a: First set of outputs (e.g., new version)
            outputs_b: Second set of outputs (e.g., baseline)
            context: Optional context for each comparison

        Returns:
            Comparison results with win rates and analysis
        """
        if len(outputs_a) != len(outputs_b):
            return {
                "error": "Output lists must have same length",
                "length_a": len(outputs_a),
                "length_b": len(outputs_b),
            }

        # Pairwise comparisons
        comparisons = []
        for i, (a, b) in enumerate(zip(outputs_a, outputs_b)):
            ctx = context[i] if context and i < len(context) else None
            comparison = self._compare_pair(i, a, b, ctx)
            comparisons.append(comparison)

        # Aggregate results
        wins_a = sum(1 for c in comparisons if c.result == ComparisonResult.A_BETTER)
        wins_b = sum(1 for c in comparisons if c.result == ComparisonResult.B_BETTER)
        ties = sum(1 for c in comparisons if c.result == ComparisonResult.TIE)

        total = len(comparisons)
        win_rate_a = wins_a / total if total > 0 else 0
        win_rate_b = wins_b / total if total > 0 else 0

        # Determine overall winner
        if win_rate_a > win_rate_b + 0.1:
            overall = "A is significantly better"
        elif win_rate_b > win_rate_a + 0.1:
            overall = "B is significantly better"
        elif abs(win_rate_a - win_rate_b) < 0.05:
            overall = "No significant difference"
        else:
            overall = "Slight difference, more data needed"

        return {
            "summary": overall,
            "win_rate_a": win_rate_a,
            "win_rate_b": win_rate_b,
            "wins_a": wins_a,
            "wins_b": wins_b,
            "ties": ties,
            "total_comparisons": total,
            "comparisons": [c.to_dict() for c in comparisons],
            "dimension_analysis": self._analyze_by_dimension(comparisons),
        }

    def _compare_pair(
        self,
        index: int,
        output_a: dict[str, Any],
        output_b: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> PairwiseComparison:
        """Compare a single pair of outputs."""
        scores_a = self._score_output(output_a, context)
        scores_b = self._score_output(output_b, context)

        # Compute aggregate scores
        total_a = sum(scores_a.values())
        total_b = sum(scores_b.values())

        # Determine result
        diff = total_a - total_b
        if diff > 1.0:
            result = ComparisonResult.A_BETTER
            confidence = min(0.9, 0.5 + diff * 0.1)
        elif diff < -1.0:
            result = ComparisonResult.B_BETTER
            confidence = min(0.9, 0.5 + abs(diff) * 0.1)
        elif abs(diff) < 0.5:
            result = ComparisonResult.TIE
            confidence = 0.8
        else:
            result = ComparisonResult.INCONCLUSIVE
            confidence = 0.4

        # Generate reasoning
        reasoning = self._generate_reasoning(scores_a, scores_b, result)

        return PairwiseComparison(
            index=index,
            result=result,
            confidence=confidence,
            reasoning=reasoning,
            scores_a=scores_a,
            scores_b=scores_b,
        )

    def _score_output(
        self,
        output: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, float]:
        """Score an output on all dimensions."""
        scores = {}
        content = str(output.get("content", ""))

        for dimension in self.dimensions:
            scores[dimension] = self._score_dimension(content, dimension, context)

        return scores

    def _score_dimension(
        self,
        content: str,
        dimension: str,
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """Score content on a single dimension."""
        if not content:
            return 0.0

        # Simple heuristic scoring - in production, would use LLM
        if dimension == "accuracy":
            # Check for confident language
            score = 5.0
            if "definitely" in content.lower() or "certainly" in content.lower():
                score += 1.0
            if "I think" in content or "maybe" in content.lower():
                score -= 1.0
            return max(0, min(10, score))

        elif dimension == "helpfulness":
            score = 5.0
            if "```" in content:  # Code example
                score += 2.0
            if "step" in content.lower():  # Step-by-step
                score += 1.0
            if len(content) > 200:
                score += 1.0
            return max(0, min(10, score))

        elif dimension == "clarity":
            score = 5.0
            sentences = content.split(".")
            avg_len = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            if 10 < avg_len < 25:
                score += 2.0
            elif avg_len > 40:
                score -= 1.0
            return max(0, min(10, score))

        elif dimension == "completeness":
            score = 5.0
            word_count = len(content.split())
            if word_count > 100:
                score += 2.0
            elif word_count < 20:
                score -= 2.0
            if content.endswith("..."):
                score -= 2.0
            return max(0, min(10, score))

        return 5.0  # Default middle score

    def _generate_reasoning(
        self,
        scores_a: dict[str, float],
        scores_b: dict[str, float],
        result: ComparisonResult,
    ) -> str:
        """Generate reasoning for the comparison result."""
        reasons = []

        for dim in self.dimensions:
            diff = scores_a.get(dim, 0) - scores_b.get(dim, 0)
            if abs(diff) > 1.0:
                winner = "A" if diff > 0 else "B"
                reasons.append(f"{winner} better on {dim} ({abs(diff):.1f} pts)")

        if not reasons:
            return "Outputs are comparable across all dimensions"

        return "; ".join(reasons)

    def _analyze_by_dimension(
        self,
        comparisons: list[PairwiseComparison],
    ) -> dict[str, dict[str, Any]]:
        """Analyze comparison results by dimension."""
        analysis = {}

        for dim in self.dimensions:
            scores_a = [c.scores_a.get(dim, 0) for c in comparisons]
            scores_b = [c.scores_b.get(dim, 0) for c in comparisons]

            avg_a = sum(scores_a) / len(scores_a) if scores_a else 0
            avg_b = sum(scores_b) / len(scores_b) if scores_b else 0

            analysis[dim] = {
                "avg_score_a": avg_a,
                "avg_score_b": avg_b,
                "difference": avg_a - avg_b,
                "winner": "A" if avg_a > avg_b + 0.5 else ("B" if avg_b > avg_a + 0.5 else "tie"),
            }

        return analysis
