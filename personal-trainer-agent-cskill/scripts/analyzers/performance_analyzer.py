"""
Performance Analyzer - Analyzes overall agent performance patterns.

This module provides comprehensive analysis of agent outputs to identify
performance characteristics, trends, and areas for improvement.
"""

import re
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class PerformanceMetric:
    """A single performance metric."""
    name: str
    value: float
    unit: str
    trend: str  # "improving", "declining", "stable"
    benchmark: Optional[float] = None


@dataclass
class PerformanceAnalysis:
    """Complete performance analysis result."""
    summary: Dict[str, Any]
    metrics: List[PerformanceMetric]
    strengths: List[str]
    weaknesses: List[str]
    trends: Dict[str, str]
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PerformanceAnalyzer:
    """
    Analyzes agent performance across multiple dimensions.

    Dimensions analyzed:
    - Output quality (coherence, relevance, accuracy)
    - Consistency (variation across similar inputs)
    - Completeness (coverage of required elements)
    - Efficiency (verbosity, redundancy)
    - Domain-specific metrics
    """

    # Domain-specific quality indicators
    DOMAIN_INDICATORS = {
        "website_building": {
            "positive": [
                r"responsive", r"mobile-first", r"accessible", r"semantic",
                r"flexbox|grid", r"css-variables", r"clean\s+code", r"well-structured"
            ],
            "negative": [
                r"inline\s+styles?", r"!important", r"deprecated", r"table\s+layout",
                r"fixed\s+width", r"missing\s+alt", r"no\s+contrast"
            ],
            "required_elements": ["html", "css", "responsive", "semantic tags"]
        },
        "marketing": {
            "positive": [
                r"call\s+to\s+action", r"CTA", r"value\s+proposition", r"benefit",
                r"audience", r"engagement", r"conversion", r"compelling"
            ],
            "negative": [
                r"generic", r"clich[eé]", r"buzzword", r"unclear\s+message",
                r"no\s+CTA", r"weak\s+headline"
            ],
            "required_elements": ["headline", "value proposition", "CTA", "target audience"]
        },
        "coding": {
            "positive": [
                r"type\s+hints?", r"docstring", r"error\s+handling", r"tested",
                r"clean", r"modular", r"efficient", r"readable"
            ],
            "negative": [
                r"TODO", r"FIXME", r"hardcoded", r"magic\s+number", r"no\s+types?",
                r"duplicate", r"complex", r"nested"
            ],
            "required_elements": ["error handling", "documentation", "type hints"]
        },
        "general": {
            "positive": [
                r"clear", r"concise", r"accurate", r"helpful", r"complete",
                r"well-organized", r"relevant"
            ],
            "negative": [
                r"unclear", r"verbose", r"inaccurate", r"incomplete",
                r"off-topic", r"confusing"
            ],
            "required_elements": ["clarity", "relevance", "completeness"]
        }
    }

    def __init__(self):
        """Initialize the performance analyzer."""
        self._history: Dict[str, List[PerformanceAnalysis]] = defaultdict(list)

    def analyze(
        self,
        outputs: List[Dict[str, Any]],
        domain: str = "general",
        previous_analyses: Optional[List[PerformanceAnalysis]] = None
    ) -> PerformanceAnalysis:
        """
        Analyze a batch of outputs for performance patterns.

        Args:
            outputs: List of agent outputs to analyze
            domain: The domain for context-specific analysis
            previous_analyses: Previous analyses for trend detection

        Returns:
            PerformanceAnalysis with comprehensive results
        """
        if not outputs:
            return PerformanceAnalysis(
                summary={"status": "no_data", "message": "No outputs to analyze"},
                metrics=[],
                strengths=[],
                weaknesses=[],
                trends={},
                recommendations=["Provide output samples for analysis"]
            )

        # Analyze each dimension
        quality_scores = self._analyze_quality(outputs, domain)
        consistency_scores = self._analyze_consistency(outputs)
        completeness_scores = self._analyze_completeness(outputs, domain)
        efficiency_scores = self._analyze_efficiency(outputs)

        # Calculate metrics
        metrics = self._calculate_metrics(
            quality_scores,
            consistency_scores,
            completeness_scores,
            efficiency_scores
        )

        # Identify patterns
        strengths = self._identify_strengths(outputs, domain)
        weaknesses = self._identify_weaknesses(outputs, domain)

        # Detect trends
        trends = self._detect_trends(metrics, previous_analyses)

        # Generate recommendations
        recommendations = self._generate_recommendations(weaknesses, trends)

        # Build summary
        summary = self._build_summary(
            quality_scores,
            consistency_scores,
            completeness_scores,
            efficiency_scores,
            len(outputs)
        )

        analysis = PerformanceAnalysis(
            summary=summary,
            metrics=metrics,
            strengths=strengths,
            weaknesses=weaknesses,
            trends=trends,
            recommendations=recommendations
        )

        return analysis

    def _analyze_quality(
        self,
        outputs: List[Dict[str, Any]],
        domain: str
    ) -> List[float]:
        """Analyze output quality based on domain indicators."""
        indicators = self.DOMAIN_INDICATORS.get(domain, self.DOMAIN_INDICATORS["general"])
        positive_patterns = [re.compile(p, re.IGNORECASE) for p in indicators["positive"]]
        negative_patterns = [re.compile(p, re.IGNORECASE) for p in indicators["negative"]]

        scores = []
        for output in outputs:
            content = self._extract_content(output)

            # Count positive and negative indicators
            positive_count = sum(1 for p in positive_patterns if p.search(content))
            negative_count = sum(1 for p in negative_patterns if p.search(content))

            # Calculate score (0-10 scale)
            max_positive = len(positive_patterns)
            positive_ratio = positive_count / max_positive if max_positive > 0 else 0.5

            # Penalty for negative indicators
            penalty = min(negative_count * 0.5, 3)  # Max 3 point penalty

            score = max(0, min(10, (positive_ratio * 10) - penalty))
            scores.append(score)

        return scores

    def _analyze_consistency(
        self,
        outputs: List[Dict[str, Any]]
    ) -> List[float]:
        """Analyze consistency across outputs."""
        if len(outputs) < 2:
            return [7.5]  # Default neutral score

        contents = [self._extract_content(o) for o in outputs]

        # Analyze structure consistency
        structure_scores = self._check_structure_consistency(contents)

        # Analyze length consistency
        lengths = [len(c) for c in contents]
        length_variance = statistics.stdev(lengths) / statistics.mean(lengths) if statistics.mean(lengths) > 0 else 0
        length_score = max(0, 10 - (length_variance * 10))

        # Combine scores
        return [(s + length_score) / 2 for s in structure_scores]

    def _check_structure_consistency(
        self,
        contents: List[str]
    ) -> List[float]:
        """Check if outputs follow consistent structure."""
        if not contents:
            return []

        # Check for common structural elements
        structure_features = [
            r"^#",  # Headers
            r"\n-\s",  # Bullet points
            r"\n\d+\.",  # Numbered lists
            r"```",  # Code blocks
            r"\n\n",  # Paragraph breaks
        ]

        feature_presence = []
        for content in contents:
            features = [bool(re.search(p, content, re.MULTILINE)) for p in structure_features]
            feature_presence.append(features)

        # Calculate consistency for each output compared to the majority
        scores = []
        if len(feature_presence) >= 2:
            # Find the most common pattern
            feature_counts = [sum(f[i] for f in feature_presence) for i in range(len(structure_features))]
            majority = [c > len(contents) / 2 for c in feature_counts]

            for features in feature_presence:
                matches = sum(1 for i, f in enumerate(features) if f == majority[i])
                score = (matches / len(structure_features)) * 10
                scores.append(score)
        else:
            scores = [7.5] * len(contents)

        return scores

    def _analyze_completeness(
        self,
        outputs: List[Dict[str, Any]],
        domain: str
    ) -> List[float]:
        """Analyze completeness of outputs."""
        indicators = self.DOMAIN_INDICATORS.get(domain, self.DOMAIN_INDICATORS["general"])
        required_elements = indicators.get("required_elements", [])

        scores = []
        for output in outputs:
            content = self._extract_content(output).lower()

            # Check for required elements
            found = sum(1 for elem in required_elements if elem.lower() in content)
            completeness = found / len(required_elements) if required_elements else 0.7

            # Check for structural completeness
            has_intro = bool(re.search(r'^[A-Z]', content))
            has_conclusion = len(content) > 100  # Reasonable length
            has_body = '\n' in content

            structure_score = sum([has_intro, has_conclusion, has_body]) / 3

            # Combine scores
            score = (completeness * 6 + structure_score * 4)
            scores.append(score)

        return scores

    def _analyze_efficiency(
        self,
        outputs: List[Dict[str, Any]]
    ) -> List[float]:
        """Analyze output efficiency (avoiding verbosity and redundancy)."""
        scores = []

        for output in outputs:
            content = self._extract_content(output)
            words = content.split()

            if not words:
                scores.append(5.0)
                continue

            # Check for redundancy (repeated phrases)
            phrases = self._extract_phrases(content, 3)
            unique_phrases = len(set(phrases))
            total_phrases = len(phrases)
            redundancy_ratio = unique_phrases / total_phrases if total_phrases > 0 else 1

            # Check for verbosity indicators
            verbose_patterns = [
                r'\b(basically|essentially|actually|really|very|quite)\b',
                r'\b(in order to|due to the fact that|at this point in time)\b',
                r'\b(it is|there is|there are)\s+\w+\s+that\b'
            ]
            verbosity_count = sum(len(re.findall(p, content, re.IGNORECASE)) for p in verbose_patterns)
            verbosity_penalty = min(verbosity_count * 0.3, 2)

            # Calculate score
            score = max(0, min(10, (redundancy_ratio * 8) + 2 - verbosity_penalty))
            scores.append(score)

        return scores

    def _extract_phrases(self, content: str, n: int) -> List[str]:
        """Extract n-word phrases from content."""
        words = re.findall(r'\b\w+\b', content.lower())
        return [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]

    def _calculate_metrics(
        self,
        quality_scores: List[float],
        consistency_scores: List[float],
        completeness_scores: List[float],
        efficiency_scores: List[float]
    ) -> List[PerformanceMetric]:
        """Calculate aggregate performance metrics."""
        metrics = []

        def calc_stat(scores: List[float], name: str) -> PerformanceMetric:
            if not scores:
                return PerformanceMetric(name=name, value=0, unit="score", trend="unknown")
            avg = statistics.mean(scores)
            return PerformanceMetric(
                name=name,
                value=round(avg, 2),
                unit="score (0-10)",
                trend="stable",  # Trend calculated separately
                benchmark=7.0
            )

        metrics.append(calc_stat(quality_scores, "quality"))
        metrics.append(calc_stat(consistency_scores, "consistency"))
        metrics.append(calc_stat(completeness_scores, "completeness"))
        metrics.append(calc_stat(efficiency_scores, "efficiency"))

        # Overall score
        all_scores = quality_scores + consistency_scores + completeness_scores + efficiency_scores
        if all_scores:
            overall = statistics.mean(all_scores)
            metrics.append(PerformanceMetric(
                name="overall",
                value=round(overall, 2),
                unit="score (0-10)",
                trend="stable",
                benchmark=7.0
            ))

        return metrics

    def _identify_strengths(
        self,
        outputs: List[Dict[str, Any]],
        domain: str
    ) -> List[str]:
        """Identify strengths in the outputs."""
        strengths = []
        indicators = self.DOMAIN_INDICATORS.get(domain, self.DOMAIN_INDICATORS["general"])
        positive_patterns = indicators["positive"]

        # Count occurrences of positive indicators
        pattern_counts = defaultdict(int)
        for output in outputs:
            content = self._extract_content(output)
            for pattern in positive_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    pattern_counts[pattern] += 1

        # Identify frequently occurring strengths
        threshold = len(outputs) * 0.5  # Present in at least 50% of outputs
        for pattern, count in pattern_counts.items():
            if count >= threshold:
                strength = self._pattern_to_description(pattern, positive=True)
                if strength:
                    strengths.append(strength)

        return strengths[:5]  # Top 5 strengths

    def _identify_weaknesses(
        self,
        outputs: List[Dict[str, Any]],
        domain: str
    ) -> List[str]:
        """Identify weaknesses in the outputs."""
        weaknesses = []
        indicators = self.DOMAIN_INDICATORS.get(domain, self.DOMAIN_INDICATORS["general"])
        negative_patterns = indicators["negative"]

        # Count occurrences of negative indicators
        pattern_counts = defaultdict(int)
        for output in outputs:
            content = self._extract_content(output)
            for pattern in negative_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    pattern_counts[pattern] += 1

        # Identify frequently occurring weaknesses
        threshold = max(1, len(outputs) * 0.2)  # Present in at least 20% of outputs
        for pattern, count in pattern_counts.items():
            if count >= threshold:
                weakness = self._pattern_to_description(pattern, positive=False)
                if weakness:
                    weaknesses.append(weakness)

        return weaknesses[:5]  # Top 5 weaknesses

    def _pattern_to_description(self, pattern: str, positive: bool) -> Optional[str]:
        """Convert regex pattern to human-readable description."""
        descriptions = {
            # Positive
            r"responsive": "Implements responsive design",
            r"mobile-first": "Uses mobile-first approach",
            r"accessible": "Considers accessibility",
            r"semantic": "Uses semantic HTML",
            r"clean\s+code": "Produces clean, readable code",
            r"call\s+to\s+action": "Includes clear calls to action",
            r"value\s+proposition": "Articulates value proposition",
            r"type\s+hints?": "Uses type hints",
            r"error\s+handling": "Implements error handling",
            # Negative
            r"inline\s+styles?": "Uses inline styles (avoid for maintainability)",
            r"!important": "Overuses !important declarations",
            r"deprecated": "Uses deprecated elements",
            r"generic": "Content is too generic",
            r"clich[eé]": "Uses clichés",
            r"TODO": "Contains incomplete TODO markers",
            r"hardcoded": "Contains hardcoded values",
            r"duplicate": "Has duplicate code",
        }

        for p, desc in descriptions.items():
            if p in pattern or pattern in p:
                return desc

        # Fallback: clean up the pattern
        clean = re.sub(r'[\\()|\[\]]', '', pattern)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if positive:
            return f"Demonstrates: {clean}"
        else:
            return f"Issue: {clean}"

    def _detect_trends(
        self,
        current_metrics: List[PerformanceMetric],
        previous_analyses: Optional[List[PerformanceAnalysis]]
    ) -> Dict[str, str]:
        """Detect trends compared to previous analyses."""
        trends = {}

        if not previous_analyses:
            for metric in current_metrics:
                trends[metric.name] = "baseline"
            return trends

        # Get previous metric values
        previous_values: Dict[str, List[float]] = defaultdict(list)
        for analysis in previous_analyses:
            for metric in analysis.metrics:
                previous_values[metric.name].append(metric.value)

        # Compare current to historical average
        for metric in current_metrics:
            prev = previous_values.get(metric.name, [])
            if prev:
                avg_prev = statistics.mean(prev)
                diff = metric.value - avg_prev

                if diff > 0.5:
                    trends[metric.name] = "improving"
                elif diff < -0.5:
                    trends[metric.name] = "declining"
                else:
                    trends[metric.name] = "stable"
            else:
                trends[metric.name] = "baseline"

        return trends

    def _generate_recommendations(
        self,
        weaknesses: List[str],
        trends: Dict[str, str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Address weaknesses
        for weakness in weaknesses:
            if "inline styles" in weakness.lower():
                recommendations.append("Move inline styles to CSS classes for better maintainability")
            elif "generic" in weakness.lower():
                recommendations.append("Add more specific, contextual details to content")
            elif "todo" in weakness.lower():
                recommendations.append("Complete all TODO items before finalizing output")
            elif "hardcoded" in weakness.lower():
                recommendations.append("Replace hardcoded values with configurable parameters")
            elif "deprecated" in weakness.lower():
                recommendations.append("Update deprecated elements to modern equivalents")
            else:
                recommendations.append(f"Address: {weakness}")

        # Address declining trends
        for metric, trend in trends.items():
            if trend == "declining":
                recommendations.append(f"Investigate recent decline in {metric} scores")

        return recommendations[:7]  # Top 7 recommendations

    def _build_summary(
        self,
        quality_scores: List[float],
        consistency_scores: List[float],
        completeness_scores: List[float],
        efficiency_scores: List[float],
        sample_count: int
    ) -> Dict[str, Any]:
        """Build a summary of the analysis."""
        def safe_mean(scores: List[float]) -> float:
            return statistics.mean(scores) if scores else 0

        overall = safe_mean(quality_scores + consistency_scores + completeness_scores + efficiency_scores)

        # Determine overall rating
        if overall >= 8:
            rating = "excellent"
        elif overall >= 6:
            rating = "good"
        elif overall >= 4:
            rating = "needs_improvement"
        else:
            rating = "poor"

        return {
            "sample_count": sample_count,
            "overall_score": round(overall, 2),
            "rating": rating,
            "quality_avg": round(safe_mean(quality_scores), 2),
            "consistency_avg": round(safe_mean(consistency_scores), 2),
            "completeness_avg": round(safe_mean(completeness_scores), 2),
            "efficiency_avg": round(safe_mean(efficiency_scores), 2)
        }

    def _extract_content(self, output: Dict[str, Any]) -> str:
        """Extract text content from output dict."""
        if isinstance(output, str):
            return output

        # Try common keys
        for key in ["output", "content", "text", "response", "result"]:
            if key in output:
                val = output[key]
                if isinstance(val, str):
                    return val
                elif isinstance(val, dict):
                    return str(val)

        # Fallback to string representation
        return str(output)
