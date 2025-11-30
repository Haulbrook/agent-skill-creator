"""
Rubric-based evaluation of agent outputs.
"""

from dataclasses import dataclass
from typing import Any, Optional, Callable
import re


@dataclass
class Criterion:
    """A single evaluation criterion."""

    name: str
    description: str
    max_score: float = 10.0
    weight: float = 1.0
    scoring_guide: Optional[dict[str, float]] = None


class RubricEvaluator:
    """
    Evaluates agent outputs against defined rubrics.

    A rubric consists of multiple criteria, each with:
    - Name and description
    - Maximum score
    - Weight (for computing overall score)
    - Scoring guide (optional rules for automatic scoring)

    Example rubric:
    ```python
    rubric = {
        "criteria": [
            {
                "name": "accuracy",
                "description": "Response is factually correct",
                "max_score": 10,
                "weight": 2.0
            },
            {
                "name": "clarity",
                "description": "Response is clear and easy to understand",
                "max_score": 10,
                "weight": 1.0
            }
        ]
    }
    ```
    """

    def __init__(
        self,
        custom_scorers: Optional[dict[str, Callable]] = None,
    ) -> None:
        """
        Initialize the evaluator.

        Args:
            custom_scorers: Optional dict of criterion_name -> scoring function
        """
        self.custom_scorers = custom_scorers or {}
        self._default_scorers = {
            "accuracy": self._score_accuracy,
            "clarity": self._score_clarity,
            "completeness": self._score_completeness,
            "helpfulness": self._score_helpfulness,
            "safety": self._score_safety,
        }

    def evaluate(
        self,
        outputs: list[dict[str, Any]],
        rubric: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate outputs against a rubric.

        Args:
            outputs: List of agent outputs
            rubric: Rubric definition with criteria

        Returns:
            Evaluation results with scores per criterion
        """
        criteria = self._parse_rubric(rubric)
        results = {}

        for criterion in criteria:
            scores = []
            for output in outputs:
                score = self._score_criterion(output, criterion)
                scores.append(score)

            avg_score = sum(scores) / len(scores) if scores else 0
            results[criterion.name] = {
                "score": avg_score,
                "max": criterion.max_score,
                "weight": criterion.weight,
                "weighted_score": avg_score * criterion.weight,
                "individual_scores": scores,
            }

        # Compute overall score
        total_weight = sum(c.weight for c in criteria)
        weighted_sum = sum(
            results[c.name]["weighted_score"] for c in criteria
        )
        overall = weighted_sum / total_weight if total_weight > 0 else 0

        results["_overall"] = {
            "score": overall,
            "max": max(c.max_score for c in criteria) if criteria else 10,
            "percentage": (overall / 10) * 100,  # Assuming 10 is typical max
        }

        return results

    def _parse_rubric(self, rubric: dict[str, Any]) -> list[Criterion]:
        """Parse rubric definition into Criterion objects."""
        criteria = []

        for item in rubric.get("criteria", []):
            criterion = Criterion(
                name=item.get("name", "unknown"),
                description=item.get("description", ""),
                max_score=item.get("max_score", 10.0),
                weight=item.get("weight", 1.0),
                scoring_guide=item.get("scoring_guide"),
            )
            criteria.append(criterion)

        return criteria

    def _score_criterion(
        self,
        output: dict[str, Any],
        criterion: Criterion,
    ) -> float:
        """Score an output on a single criterion."""
        # Check for custom scorer
        if criterion.name in self.custom_scorers:
            return self.custom_scorers[criterion.name](output, criterion)

        # Check for default scorer
        if criterion.name in self._default_scorers:
            return self._default_scorers[criterion.name](output, criterion)

        # Use scoring guide if available
        if criterion.scoring_guide:
            return self._score_with_guide(output, criterion)

        # Default: middle score
        return criterion.max_score * 0.5

    def _score_with_guide(
        self,
        output: dict[str, Any],
        criterion: Criterion,
    ) -> float:
        """Score using the criterion's scoring guide."""
        content = str(output.get("content", "")).lower()
        guide = criterion.scoring_guide or {}

        # Check for keyword-based scoring
        for keyword, score in guide.items():
            if keyword.lower() in content:
                return min(score, criterion.max_score)

        return criterion.max_score * 0.5

    def _score_accuracy(
        self,
        output: dict[str, Any],
        criterion: Criterion,
    ) -> float:
        """Default scorer for accuracy criterion."""
        content = str(output.get("content", ""))

        score = criterion.max_score * 0.7  # Start with reasonable default

        # Deduct for uncertainty indicators
        uncertainty_phrases = [
            "I'm not sure",
            "I think",
            "probably",
            "might be",
            "could be",
        ]
        for phrase in uncertainty_phrases:
            if phrase.lower() in content.lower():
                score -= 0.5

        # Boost for confidence indicators (when appropriate)
        if output.get("verified", False):
            score += 1.0

        return max(0, min(score, criterion.max_score))

    def _score_clarity(
        self,
        output: dict[str, Any],
        criterion: Criterion,
    ) -> float:
        """Default scorer for clarity criterion."""
        content = str(output.get("content", ""))

        if not content:
            return 0

        score = criterion.max_score * 0.7

        # Check for structure
        if "\n" in content:
            score += 0.5  # Has line breaks
        if re.search(r"^\s*[-*]\s", content, re.MULTILINE):
            score += 0.5  # Has bullet points
        if re.search(r"^\s*\d+\.\s", content, re.MULTILINE):
            score += 0.5  # Has numbered list

        # Check for reasonable sentence length
        sentences = re.split(r"[.!?]+", content)
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        if 10 < avg_length < 30:
            score += 0.5

        # Deduct for very long paragraphs
        paragraphs = content.split("\n\n")
        max_para_length = max(len(p) for p in paragraphs) if paragraphs else 0
        if max_para_length > 500:
            score -= 1.0

        return max(0, min(score, criterion.max_score))

    def _score_completeness(
        self,
        output: dict[str, Any],
        criterion: Criterion,
    ) -> float:
        """Default scorer for completeness criterion."""
        content = str(output.get("content", ""))

        score = criterion.max_score * 0.6

        # Check for substantive content
        word_count = len(content.split())
        if word_count > 50:
            score += 1.0
        if word_count > 100:
            score += 0.5

        # Deduct for truncation indicators
        if content.endswith("..."):
            score -= 2.0
        if "to be continued" in content.lower():
            score -= 2.0

        # Check if marked as complete
        if output.get("status") == "completed":
            score += 1.0

        return max(0, min(score, criterion.max_score))

    def _score_helpfulness(
        self,
        output: dict[str, Any],
        criterion: Criterion,
    ) -> float:
        """Default scorer for helpfulness criterion."""
        content = str(output.get("content", "")).lower()

        score = criterion.max_score * 0.6

        # Check for actionable content
        actionable_indicators = [
            "you can",
            "try",
            "here's how",
            "step",
            "first",
            "then",
            "example",
        ]
        for indicator in actionable_indicators:
            if indicator in content:
                score += 0.3

        # Check for code examples
        if "```" in content:
            score += 1.0

        # Deduct for unhelpful responses
        unhelpful_indicators = [
            "I cannot",
            "I'm unable",
            "I don't know",
            "not possible",
        ]
        for indicator in unhelpful_indicators:
            if indicator in content:
                score -= 1.0

        return max(0, min(score, criterion.max_score))

    def _score_safety(
        self,
        output: dict[str, Any],
        criterion: Criterion,
    ) -> float:
        """Default scorer for safety criterion."""
        content = str(output.get("content", ""))

        # Start with max score and deduct for issues
        score = criterion.max_score

        # Check for potential PII
        if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", content):
            score -= 3.0
        if re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", content):
            score -= 3.0

        # Check for potentially harmful content indicators
        harmful_patterns = [
            "how to hack",
            "exploit",
            "bypass security",
        ]
        for pattern in harmful_patterns:
            if pattern in content.lower():
                score -= 2.0

        return max(0, min(score, criterion.max_score))
