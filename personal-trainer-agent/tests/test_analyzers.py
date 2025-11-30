"""Tests for analyzer modules."""

import pytest

from personal_trainer_agent.analyzers import PerformanceAnalyzer, WeaknessDetector


class TestPerformanceAnalyzer:
    """Tests for PerformanceAnalyzer."""

    def test_analyze_empty_outputs(self):
        """Test analyzing empty outputs."""
        analyzer = PerformanceAnalyzer()
        result = analyzer.analyze([])

        assert "error" in result
        assert result["overall_score"] == 0

    def test_analyze_single_output(self):
        """Test analyzing a single output."""
        analyzer = PerformanceAnalyzer()
        outputs = [{"content": "This is a helpful response.", "status": "completed"}]

        result = analyzer.analyze(outputs)

        assert "overall_score" in result
        assert "accuracy" in result
        assert "consistency" in result
        assert result["num_outputs"] == 1

    def test_analyze_with_expected(self):
        """Test analyzing with expected outputs."""
        analyzer = PerformanceAnalyzer()
        outputs = [{"content": "Hello world"}]
        expected = [{"content": "Hello world"}]

        result = analyzer.analyze(outputs, expected)

        assert result["has_expected"] is True
        assert result["accuracy"] > 0.5  # Should have high accuracy

    def test_analyze_mismatched_outputs(self):
        """Test analyzing with mismatched expected outputs."""
        analyzer = PerformanceAnalyzer()
        outputs = [{"content": "Hello"}]
        expected = [{"content": "Completely different response"}]

        result = analyzer.analyze(outputs, expected)

        assert result["accuracy"] < 0.8  # Should have lower accuracy

    def test_custom_weights(self):
        """Test analyzer with custom weights."""
        weights = {
            "accuracy": 0.5,
            "consistency": 0.1,
            "response_quality": 0.2,
            "task_completion": 0.2,
        }
        analyzer = PerformanceAnalyzer(weights=weights)
        outputs = [{"content": "Test", "status": "completed"}]

        result = analyzer.analyze(outputs)

        assert "overall_score" in result

    def test_consistency_single_output(self):
        """Test consistency with single output."""
        analyzer = PerformanceAnalyzer()
        outputs = [{"content": "Single output"}]

        result = analyzer.analyze(outputs)

        # Single output should have perfect consistency
        assert result["consistency"] == 1.0

    def test_consistency_multiple_outputs(self):
        """Test consistency with multiple similar outputs."""
        analyzer = PerformanceAnalyzer()
        outputs = [
            {"content": "Response one", "type": "answer"},
            {"content": "Response two", "type": "answer"},
            {"content": "Response three", "type": "answer"},
        ]

        result = analyzer.analyze(outputs)

        # Similar structure should have good consistency
        assert result["consistency"] > 0.5


class TestWeaknessDetector:
    """Tests for WeaknessDetector."""

    def test_detect_no_weaknesses(self):
        """Test detection with good outputs."""
        detector = WeaknessDetector()
        outputs = [
            {"content": "This is a clear, complete, and helpful response."}
        ]

        weaknesses = detector.detect(outputs)

        # May still find minor issues, but should be low severity
        high_severity = [w for w in weaknesses if w["severity"] in ["critical", "high"]]
        assert len(high_severity) == 0

    def test_detect_hedging(self):
        """Test detection of hedging language."""
        detector = WeaknessDetector()
        outputs = [
            {
                "content": "I think this might be correct. "
                "I believe it could work. "
                "Maybe this is the answer. "
                "Probably this is right. "
                "I'm not sure but..."
            }
        ]

        weaknesses = detector.detect(outputs)

        # Should detect hedging weakness
        hedging = [w for w in weaknesses if "confidence" in w["description"].lower()]
        assert len(hedging) > 0

    def test_detect_truncation(self):
        """Test detection of truncated outputs."""
        detector = WeaknessDetector()
        outputs = [{"content": "This response is incomplete..."}]

        weaknesses = detector.detect(outputs)

        # Should detect completeness issue
        truncation = [w for w in weaknesses if w["category"] == "completeness"]
        assert len(truncation) > 0

    def test_detect_pii(self):
        """Test detection of potential PII."""
        detector = WeaknessDetector()
        outputs = [
            {"content": "Contact me at john.doe@example.com or 555-123-4567"}
        ]

        weaknesses = detector.detect(outputs)

        # Should detect safety issue
        safety = [w for w in weaknesses if w["category"] == "safety"]
        assert len(safety) > 0
        assert any(w["severity"] == "critical" for w in safety)

    def test_detect_with_performance_metrics(self):
        """Test detection using performance metrics."""
        detector = WeaknessDetector()
        outputs = [{"content": "Test"}]
        performance = {
            "overall_score": 0.3,
            "accuracy": 0.4,
            "task_completion": 0.5,
        }

        weaknesses = detector.detect(outputs, performance=performance)

        # Should detect performance-based weaknesses
        perf_issues = [w for w in weaknesses if w["category"] == "performance"]
        assert len(perf_issues) > 0

    def test_weakness_sorting(self):
        """Test that weaknesses are sorted by severity."""
        detector = WeaknessDetector()
        outputs = [
            {
                "content": "Contact: test@email.com. I think maybe this is incomplete..."
            }
        ]

        weaknesses = detector.detect(outputs)

        # Critical should come before high, high before medium, etc.
        if len(weaknesses) > 1:
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            for i in range(len(weaknesses) - 1):
                current = severity_order[weaknesses[i]["severity"]]
                next_sev = severity_order[weaknesses[i + 1]["severity"]]
                assert current <= next_sev
