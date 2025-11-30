"""
Weakness detection for agent outputs.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import re


class Severity(str, Enum):
    """Severity levels for detected weaknesses."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Weakness:
    """Represents a detected weakness."""

    id: str
    category: str
    description: str
    severity: Severity
    suggestion: str
    impact: float = 0.1
    examples: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "description": self.description,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
            "impact": self.impact,
            "examples": self.examples,
        }


class WeaknessDetector:
    """
    Detects specific weaknesses in agent outputs.

    Categories of weaknesses:
    - Accuracy: Incorrect or inaccurate information
    - Completeness: Missing required information
    - Format: Poor formatting or structure
    - Consistency: Inconsistent behavior
    - Safety: Potential safety issues
    - Performance: Slow or inefficient responses
    """

    def __init__(self) -> None:
        """Initialize the weakness detector."""
        self.weakness_counter = 0

    def detect(
        self,
        outputs: list[dict[str, Any]],
        performance: Optional[dict[str, Any]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """
        Detect weaknesses in agent outputs.

        Args:
            outputs: List of agent outputs to analyze
            performance: Performance metrics from PerformanceAnalyzer
            context: Additional context for detection

        Returns:
            List of detected weaknesses
        """
        weaknesses = []

        # Run all detection methods
        weaknesses.extend(self._detect_accuracy_issues(outputs))
        weaknesses.extend(self._detect_completeness_issues(outputs))
        weaknesses.extend(self._detect_format_issues(outputs))
        weaknesses.extend(self._detect_consistency_issues(outputs))
        weaknesses.extend(self._detect_safety_issues(outputs))

        # Check performance-based weaknesses
        if performance:
            weaknesses.extend(self._detect_performance_weaknesses(performance))

        # Sort by severity and impact
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
        }
        weaknesses.sort(key=lambda w: (severity_order[w.severity], -w.impact))

        return [w.to_dict() for w in weaknesses]

    def _generate_id(self, category: str) -> str:
        """Generate a unique weakness ID."""
        self.weakness_counter += 1
        return f"{category[:3].upper()}-{self.weakness_counter:04d}"

    def _detect_accuracy_issues(self, outputs: list[dict[str, Any]]) -> list[Weakness]:
        """Detect accuracy-related weaknesses."""
        weaknesses = []

        for i, output in enumerate(outputs):
            content = str(output.get("content", ""))

            # Check for hedging language that might indicate uncertainty
            hedging_patterns = [
                r"\bI think\b",
                r"\bprobably\b",
                r"\bmaybe\b",
                r"\bI'm not sure\b",
                r"\bI believe\b",
            ]

            hedging_count = sum(
                len(re.findall(pattern, content, re.IGNORECASE))
                for pattern in hedging_patterns
            )

            if hedging_count > 3:
                weaknesses.append(
                    Weakness(
                        id=self._generate_id("accuracy"),
                        category="accuracy",
                        description="Excessive hedging language suggests low confidence",
                        severity=Severity.MEDIUM,
                        suggestion="Improve knowledge or confidence in responses",
                        impact=0.15,
                        examples=[i],
                    )
                )

            # Check for contradictions within a single response
            if "however" in content.lower() and "but" in content.lower():
                # Simple heuristic - real implementation would be more sophisticated
                pass

        return weaknesses

    def _detect_completeness_issues(self, outputs: list[dict[str, Any]]) -> list[Weakness]:
        """Detect completeness-related weaknesses."""
        weaknesses = []
        incomplete_indices = []

        for i, output in enumerate(outputs):
            content = str(output.get("content", ""))

            # Check for truncation indicators
            truncation_indicators = [
                content.endswith("..."),
                content.endswith("etc"),
                "to be continued" in content.lower(),
                len(content) < 20 and output.get("expected_length", 0) > 100,
            ]

            if any(truncation_indicators):
                incomplete_indices.append(i)

            # Check for missing required fields
            required_fields = output.get("_required_fields", [])
            missing_fields = [f for f in required_fields if f not in output]
            if missing_fields:
                weaknesses.append(
                    Weakness(
                        id=self._generate_id("completeness"),
                        category="completeness",
                        description=f"Missing required fields: {', '.join(missing_fields)}",
                        severity=Severity.HIGH,
                        suggestion="Ensure all required fields are populated",
                        impact=0.2,
                        examples=[i],
                    )
                )

        if incomplete_indices:
            weaknesses.append(
                Weakness(
                    id=self._generate_id("completeness"),
                    category="completeness",
                    description=f"Truncated or incomplete responses detected ({len(incomplete_indices)} instances)",
                    severity=Severity.MEDIUM,
                    suggestion="Ensure responses are complete before returning",
                    impact=0.15,
                    examples=incomplete_indices,
                )
            )

        return weaknesses

    def _detect_format_issues(self, outputs: list[dict[str, Any]]) -> list[Weakness]:
        """Detect formatting-related weaknesses."""
        weaknesses = []
        format_issues = []

        for i, output in enumerate(outputs):
            content = str(output.get("content", ""))

            issues = []

            # Check for inconsistent formatting
            if content.count("```") % 2 != 0:
                issues.append("unclosed_code_block")

            # Check for excessive whitespace
            if "   " in content or "\n\n\n" in content:
                issues.append("excessive_whitespace")

            # Check for raw JSON when prose expected
            if content.strip().startswith("{") and "expected_format" in output:
                if output["expected_format"] == "prose":
                    issues.append("wrong_format")

            if issues:
                format_issues.append((i, issues))

        if format_issues:
            all_issues = set()
            indices = []
            for idx, issues in format_issues:
                indices.append(idx)
                all_issues.update(issues)

            weaknesses.append(
                Weakness(
                    id=self._generate_id("format"),
                    category="format",
                    description=f"Formatting issues: {', '.join(all_issues)}",
                    severity=Severity.LOW,
                    suggestion="Improve output formatting consistency",
                    impact=0.1,
                    examples=indices,
                )
            )

        return weaknesses

    def _detect_consistency_issues(self, outputs: list[dict[str, Any]]) -> list[Weakness]:
        """Detect consistency-related weaknesses."""
        weaknesses = []

        if len(outputs) < 2:
            return weaknesses

        # Check for inconsistent response structure
        structures = [frozenset(o.keys()) for o in outputs]
        unique_structures = set(structures)

        if len(unique_structures) > len(outputs) / 2:
            weaknesses.append(
                Weakness(
                    id=self._generate_id("consistency"),
                    category="consistency",
                    description="Highly inconsistent response structures",
                    severity=Severity.MEDIUM,
                    suggestion="Standardize response format across similar queries",
                    impact=0.15,
                    examples=list(range(min(5, len(outputs)))),
                )
            )

        # Check for tone consistency
        tones = []
        for output in outputs:
            content = str(output.get("content", "")).lower()
            if any(word in content for word in ["sorry", "apologize", "unfortunately"]):
                tones.append("apologetic")
            elif any(word in content for word in ["great", "excellent", "perfect"]):
                tones.append("enthusiastic")
            else:
                tones.append("neutral")

        unique_tones = set(tones)
        if len(unique_tones) > 1 and len(outputs) > 3:
            weaknesses.append(
                Weakness(
                    id=self._generate_id("consistency"),
                    category="consistency",
                    description="Inconsistent tone across responses",
                    severity=Severity.LOW,
                    suggestion="Maintain consistent tone and style",
                    impact=0.1,
                    examples=[],
                )
            )

        return weaknesses

    def _detect_safety_issues(self, outputs: list[dict[str, Any]]) -> list[Weakness]:
        """Detect potential safety issues."""
        weaknesses = []

        for i, output in enumerate(outputs):
            content = str(output.get("content", ""))

            # Check for potential PII exposure
            pii_patterns = [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
                r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone
                r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",  # SSN pattern
            ]

            for pattern in pii_patterns:
                if re.search(pattern, content):
                    weaknesses.append(
                        Weakness(
                            id=self._generate_id("safety"),
                            category="safety",
                            description="Potential PII exposure detected",
                            severity=Severity.CRITICAL,
                            suggestion="Review and redact sensitive information",
                            impact=0.5,
                            examples=[i],
                        )
                    )
                    break

            # Check for potential prompt injection attempts in output
            injection_indicators = [
                "ignore previous",
                "disregard instructions",
                "new instructions:",
            ]
            if any(ind in content.lower() for ind in injection_indicators):
                weaknesses.append(
                    Weakness(
                        id=self._generate_id("safety"),
                        category="safety",
                        description="Potential prompt injection in output",
                        severity=Severity.HIGH,
                        suggestion="Review output sanitization",
                        impact=0.3,
                        examples=[i],
                    )
                )

        return weaknesses

    def _detect_performance_weaknesses(
        self,
        performance: dict[str, Any],
    ) -> list[Weakness]:
        """Detect weaknesses based on performance metrics."""
        weaknesses = []

        # Check for low overall score
        overall = performance.get("overall_score", 0)
        if overall < 0.5:
            weaknesses.append(
                Weakness(
                    id=self._generate_id("performance"),
                    category="performance",
                    description=f"Low overall performance score: {overall:.1%}",
                    severity=Severity.HIGH if overall < 0.3 else Severity.MEDIUM,
                    suggestion="Review all aspects of agent behavior",
                    impact=0.3,
                    examples=[],
                )
            )

        # Check individual metrics
        metric_thresholds = {
            "accuracy": (0.7, "Improve response accuracy"),
            "consistency": (0.6, "Standardize response patterns"),
            "response_quality": (0.6, "Enhance response quality"),
            "task_completion": (0.8, "Ensure tasks are fully completed"),
        }

        for metric, (threshold, suggestion) in metric_thresholds.items():
            value = performance.get(metric, 0)
            if value < threshold:
                weaknesses.append(
                    Weakness(
                        id=self._generate_id("performance"),
                        category="performance",
                        description=f"Low {metric}: {value:.1%} (threshold: {threshold:.1%})",
                        severity=Severity.MEDIUM,
                        suggestion=suggestion,
                        impact=0.2,
                        examples=[],
                    )
                )

        return weaknesses
