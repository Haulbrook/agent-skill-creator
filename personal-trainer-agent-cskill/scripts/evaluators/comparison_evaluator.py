"""
Comparison Evaluator - Compares outputs for A/B testing and improvement tracking.

This module provides tools for comparing agent outputs to determine which
is better and by how much, essential for training data generation and
tracking improvement.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ComparisonResult:
    """Result of comparing two outputs."""
    winner: str  # "a", "b", or "tie"
    confidence: float  # 0-1
    score_a: float
    score_b: float
    improvement_percentage: float
    improved_dimensions: List[str]
    declined_dimensions: List[str]
    analysis: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ComparisonEvaluator:
    """
    Evaluates and compares pairs of outputs.

    Useful for:
    - A/B testing prompt changes
    - Generating preference data for DPO training
    - Tracking improvement over time
    - Validating that changes are actually improvements

    Usage:
        evaluator = ComparisonEvaluator()

        # Compare two outputs
        result = evaluator.compare(output_a, output_b, input_context)

        # Generate preference pairs for training
        pairs = evaluator.generate_preference_pairs(outputs_v1, outputs_v2)
    """

    # Quality indicators for comparison
    QUALITY_INDICATORS = {
        "positive": [
            # Structure
            ("has_headers", r"^#{1,3}\s", 1.0),
            ("has_lists", r"^[\-\*]\s|^\d+\.\s", 0.8),
            ("has_code", r"```", 1.0),

            # Content quality
            ("specific_numbers", r"\d+(?:\.\d+)?%?", 0.5),
            ("examples", r"(?:for example|e\.g\.|such as|instance)", 0.8),
            ("explanation", r"(?:because|therefore|since|due to)", 0.7),

            # Professionalism
            ("proper_length", None, 1.0),  # Custom check
            ("no_fillers", None, 0.5),  # Custom check
        ],
        "negative": [
            ("has_placeholders", r"\[.*?\]|TODO|FIXME|XXX", -1.5),
            ("has_errors", r"(?:error|bug|broken|fail)", -1.0),
            ("too_short", None, -1.0),  # Custom check
            ("too_long", None, -0.5),  # Custom check
            ("ai_preamble", r"(?:as an ai|i apologize|i'm sorry)", -0.5),
        ]
    }

    def __init__(self):
        """Initialize the comparison evaluator."""
        self._comparison_history: List[ComparisonResult] = []

    def compare(
        self,
        output_a: Dict[str, Any],
        output_b: Dict[str, Any],
        input_context: Optional[Dict[str, Any]] = None,
        domain: str = "general"
    ) -> Dict[str, Any]:
        """
        Compare two outputs and determine which is better.

        Args:
            output_a: First output (typically baseline/old version)
            output_b: Second output (typically new/improved version)
            input_context: Optional input that produced these outputs
            domain: Domain for context-specific comparison

        Returns:
            Comparison result dictionary
        """
        content_a = self._extract_content(output_a)
        content_b = self._extract_content(output_b)

        # Score both outputs
        score_a, dims_a = self._score_output(content_a, domain)
        score_b, dims_b = self._score_output(content_b, domain)

        # Determine winner
        score_diff = score_b - score_a
        if abs(score_diff) < 0.5:
            winner = "tie"
            confidence = 0.5
        elif score_diff > 0:
            winner = "b"
            confidence = min(0.95, 0.5 + score_diff * 0.1)
        else:
            winner = "a"
            confidence = min(0.95, 0.5 + abs(score_diff) * 0.1)

        # Calculate improvement
        improvement_pct = ((score_b - score_a) / max(score_a, 1)) * 100 if score_a > 0 else 0

        # Find improved/declined dimensions
        improved_dims = []
        declined_dims = []
        for dim in dims_a.keys():
            diff = dims_b.get(dim, 0) - dims_a.get(dim, 0)
            if diff > 0.5:
                improved_dims.append(dim)
            elif diff < -0.5:
                declined_dims.append(dim)

        # Generate analysis
        analysis = self._generate_analysis(
            winner, score_a, score_b, improved_dims, declined_dims
        )

        result = ComparisonResult(
            winner=winner,
            confidence=confidence,
            score_a=round(score_a, 2),
            score_b=round(score_b, 2),
            improvement_percentage=round(improvement_pct, 1),
            improved_dimensions=improved_dims,
            declined_dimensions=declined_dims,
            analysis=analysis
        )

        self._comparison_history.append(result)

        return {
            "winner": result.winner,
            "confidence": result.confidence,
            "score_a": result.score_a,
            "score_b": result.score_b,
            "improvement_percentage": result.improvement_percentage,
            "improved_dimensions": result.improved_dimensions,
            "declined_dimensions": result.declined_dimensions,
            "analysis": result.analysis
        }

    def _score_output(
        self,
        content: str,
        domain: str
    ) -> Tuple[float, Dict[str, float]]:
        """Score a single output."""
        import re

        base_score = 5.0  # Start at middle
        dimension_scores = {}

        # Check positive indicators
        for name, pattern, weight in self.QUALITY_INDICATORS["positive"]:
            if pattern:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    base_score += weight
                    dimension_scores[name] = weight
            else:
                # Custom checks
                custom_score = self._custom_check(name, content)
                base_score += custom_score
                dimension_scores[name] = custom_score

        # Check negative indicators
        for name, pattern, weight in self.QUALITY_INDICATORS["negative"]:
            if pattern:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    penalty = weight * min(matches, 3)  # Cap at 3x
                    base_score += penalty
                    dimension_scores[name] = penalty
            else:
                custom_score = self._custom_check(name, content)
                base_score += custom_score
                dimension_scores[name] = custom_score

        # Domain-specific adjustments
        domain_adjustment = self._domain_adjustment(content, domain)
        base_score += domain_adjustment
        dimension_scores["domain_fit"] = domain_adjustment

        # Clamp to 0-10
        final_score = max(0, min(10, base_score))

        return final_score, dimension_scores

    def _custom_check(self, check_name: str, content: str) -> float:
        """Perform custom checks."""
        length = len(content)

        if check_name == "proper_length":
            # Ideal length is 100-1000 characters
            if 100 <= length <= 1000:
                return 1.0
            elif 50 <= length <= 2000:
                return 0.5
            else:
                return 0.0

        elif check_name == "no_fillers":
            # Check for filler words
            import re
            fillers = re.findall(
                r'\b(basically|actually|really|very|quite|just)\b',
                content, re.IGNORECASE
            )
            return 0.5 if len(fillers) < 3 else 0.0

        elif check_name == "too_short":
            return -1.0 if length < 30 else 0.0

        elif check_name == "too_long":
            return -0.5 if length > 5000 else 0.0

        return 0.0

    def _domain_adjustment(self, content: str, domain: str) -> float:
        """Apply domain-specific scoring adjustments."""
        import re

        adjustment = 0.0

        if domain == "website_building":
            # Check for web-specific quality
            if re.search(r'<\w+[^>]*>', content):  # HTML tags
                adjustment += 0.5
            if re.search(r'@media|flex|grid', content, re.IGNORECASE):
                adjustment += 0.5
            if re.search(r'!important', content):
                adjustment -= 0.5

        elif domain == "marketing":
            # Check for marketing quality
            if re.search(r'\b(you|your)\b', content, re.IGNORECASE):
                adjustment += 0.5  # Customer-focused
            if re.search(r'\b(we|our|us)\b', content, re.IGNORECASE):
                adjustment -= 0.3  # Self-focused
            if re.search(r'(?:sign up|get started|try|buy)', content, re.IGNORECASE):
                adjustment += 0.5  # Has CTA

        elif domain == "coding":
            # Check for code quality
            if re.search(r'def \w+\([^)]*\)\s*->\s*\w+:', content):
                adjustment += 0.5  # Type hints
            if re.search(r'"""[\s\S]+?"""', content):
                adjustment += 0.5  # Docstrings
            if re.search(r'try:|except:', content):
                adjustment += 0.3  # Error handling

        return adjustment

    def _generate_analysis(
        self,
        winner: str,
        score_a: float,
        score_b: float,
        improved: List[str],
        declined: List[str]
    ) -> str:
        """Generate human-readable analysis."""
        if winner == "tie":
            return f"Both outputs are comparable (A: {score_a:.1f}, B: {score_b:.1f}). No clear winner."

        winner_label = "Output B" if winner == "b" else "Output A"
        diff = abs(score_b - score_a)

        parts = [f"{winner_label} is better ("]

        if diff > 3:
            parts.append("significantly")
        elif diff > 1:
            parts.append("moderately")
        else:
            parts.append("slightly")

        parts.append(f" better, scores: A={score_a:.1f}, B={score_b:.1f}).")

        if improved:
            parts.append(f" Improved in: {', '.join(improved[:3])}.")
        if declined:
            parts.append(f" Declined in: {', '.join(declined[:3])}.")

        return "".join(parts)

    def _extract_content(self, data: Dict[str, Any]) -> str:
        """Extract text content from data."""
        if isinstance(data, str):
            return data

        for key in ["output", "content", "text", "response", "result"]:
            if key in data:
                val = data[key]
                if isinstance(val, str):
                    return val

        return str(data)

    def generate_preference_pairs(
        self,
        outputs_v1: List[Dict[str, Any]],
        outputs_v2: List[Dict[str, Any]],
        inputs: Optional[List[Dict[str, Any]]] = None,
        domain: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Generate preference pairs for DPO training.

        Compares outputs from two versions and creates training data
        where the better output is marked as "chosen".

        Args:
            outputs_v1: Outputs from version 1 (baseline)
            outputs_v2: Outputs from version 2 (improved)
            inputs: Corresponding inputs
            domain: Domain for comparison

        Returns:
            List of preference pairs for DPO training
        """
        pairs = []
        min_len = min(len(outputs_v1), len(outputs_v2))

        for i in range(min_len):
            input_ctx = inputs[i] if inputs and i < len(inputs) else {}

            comparison = self.compare(
                outputs_v1[i],
                outputs_v2[i],
                input_ctx,
                domain
            )

            # Only include clear preferences
            if comparison["winner"] != "tie" and comparison["confidence"] > 0.6:
                content_v1 = self._extract_content(outputs_v1[i])
                content_v2 = self._extract_content(outputs_v2[i])

                if comparison["winner"] == "b":
                    chosen, rejected = content_v2, content_v1
                else:
                    chosen, rejected = content_v1, content_v2

                pairs.append({
                    "prompt": self._extract_content(input_ctx) if input_ctx else "",
                    "chosen": chosen,
                    "rejected": rejected,
                    "confidence": comparison["confidence"],
                    "score_chosen": max(comparison["score_a"], comparison["score_b"]),
                    "score_rejected": min(comparison["score_a"], comparison["score_b"])
                })

        return pairs

    def track_improvement_over_time(
        self,
        session_comparisons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Track improvement trends over multiple comparisons.

        Args:
            session_comparisons: List of comparison results from a session

        Returns:
            Summary of improvement trends
        """
        if not session_comparisons:
            return {"error": "No comparisons to analyze"}

        # Calculate win rates
        wins_b = sum(1 for c in session_comparisons if c.get("winner") == "b")
        wins_a = sum(1 for c in session_comparisons if c.get("winner") == "a")
        ties = len(session_comparisons) - wins_b - wins_a

        # Average improvement
        improvements = [c["improvement_percentage"] for c in session_comparisons if "improvement_percentage" in c]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0

        # Dimension trends
        dim_improvements = {}
        for comparison in session_comparisons:
            for dim in comparison.get("improved_dimensions", []):
                dim_improvements[dim] = dim_improvements.get(dim, 0) + 1

        # Sort dimensions by improvement frequency
        top_improved = sorted(dim_improvements.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_comparisons": len(session_comparisons),
            "version_b_wins": wins_b,
            "version_a_wins": wins_a,
            "ties": ties,
            "version_b_win_rate": wins_b / len(session_comparisons) if session_comparisons else 0,
            "average_improvement_percent": round(avg_improvement, 1),
            "top_improved_dimensions": dict(top_improved),
            "improvement_trend": "positive" if wins_b > wins_a else "negative" if wins_a > wins_b else "neutral"
        }

    def get_comparison_history(self) -> List[ComparisonResult]:
        """Get history of all comparisons."""
        return self._comparison_history
