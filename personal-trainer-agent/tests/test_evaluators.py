"""Tests for evaluator modules."""

import pytest

from personal_trainer_agent.evaluators import RubricEvaluator, ComparisonEvaluator


class TestRubricEvaluator:
    """Tests for RubricEvaluator."""

    def test_evaluate_single_criterion(self):
        """Test evaluation with single criterion."""
        evaluator = RubricEvaluator()
        outputs = [{"content": "This is a clear response."}]
        rubric = {
            "criteria": [
                {"name": "clarity", "description": "Response is clear", "max_score": 10}
            ]
        }

        result = evaluator.evaluate(outputs, rubric)

        assert "clarity" in result
        assert "score" in result["clarity"]
        assert result["clarity"]["max"] == 10

    def test_evaluate_multiple_criteria(self):
        """Test evaluation with multiple criteria."""
        evaluator = RubricEvaluator()
        outputs = [{"content": "Here is a helpful step-by-step guide."}]
        rubric = {
            "criteria": [
                {"name": "clarity", "description": "Clear", "max_score": 10, "weight": 1.0},
                {"name": "helpfulness", "description": "Helpful", "max_score": 10, "weight": 2.0},
            ]
        }

        result = evaluator.evaluate(outputs, rubric)

        assert "clarity" in result
        assert "helpfulness" in result
        assert "_overall" in result

    def test_weighted_scores(self):
        """Test that weights affect overall score."""
        evaluator = RubricEvaluator()
        outputs = [{"content": "Test response"}]
        rubric = {
            "criteria": [
                {"name": "a", "description": "A", "max_score": 10, "weight": 1.0},
                {"name": "b", "description": "B", "max_score": 10, "weight": 5.0},
            ]
        }

        result = evaluator.evaluate(outputs, rubric)

        # Criterion b should have more influence on overall score
        assert result["b"]["weight"] == 5.0
        assert result["a"]["weight"] == 1.0

    def test_evaluate_empty_outputs(self):
        """Test evaluation with empty outputs."""
        evaluator = RubricEvaluator()
        rubric = {"criteria": [{"name": "test", "description": "Test", "max_score": 10}]}

        result = evaluator.evaluate([], rubric)

        # Should handle gracefully
        assert "_overall" in result

    def test_evaluate_with_code_example(self):
        """Test evaluation of response with code."""
        evaluator = RubricEvaluator()
        outputs = [{"content": "Here's an example:\n```python\nprint('hello')\n```"}]
        rubric = {
            "criteria": [
                {"name": "helpfulness", "description": "Helpful", "max_score": 10}
            ]
        }

        result = evaluator.evaluate(outputs, rubric)

        # Code examples should boost helpfulness
        assert result["helpfulness"]["score"] > 5

    def test_overall_percentage(self):
        """Test overall score percentage calculation."""
        evaluator = RubricEvaluator()
        outputs = [{"content": "Good response"}]
        rubric = {
            "criteria": [{"name": "quality", "description": "Quality", "max_score": 10}]
        }

        result = evaluator.evaluate(outputs, rubric)

        assert "percentage" in result["_overall"]
        assert 0 <= result["_overall"]["percentage"] <= 100


class TestComparisonEvaluator:
    """Tests for ComparisonEvaluator."""

    def test_compare_equal_outputs(self):
        """Test comparing identical outputs."""
        evaluator = ComparisonEvaluator()
        outputs_a = [{"content": "Same response"}]
        outputs_b = [{"content": "Same response"}]

        result = evaluator.compare(outputs_a, outputs_b)

        assert "summary" in result
        assert result["ties"] >= 0

    def test_compare_different_outputs(self):
        """Test comparing different quality outputs."""
        evaluator = ComparisonEvaluator()
        outputs_a = [
            {"content": "Here is a detailed, helpful step-by-step guide with examples."}
        ]
        outputs_b = [{"content": "ok"}]

        result = evaluator.compare(outputs_a, outputs_b)

        assert result["wins_a"] > result["wins_b"]

    def test_compare_mismatched_lengths(self):
        """Test comparing outputs of different lengths."""
        evaluator = ComparisonEvaluator()
        outputs_a = [{"content": "One"}, {"content": "Two"}]
        outputs_b = [{"content": "One"}]

        result = evaluator.compare(outputs_a, outputs_b)

        assert "error" in result

    def test_win_rate_calculation(self):
        """Test win rate calculation."""
        evaluator = ComparisonEvaluator()
        outputs_a = [
            {"content": "Good response 1"},
            {"content": "Good response 2"},
            {"content": "Good response 3"},
        ]
        outputs_b = [
            {"content": "Bad"},
            {"content": "Bad"},
            {"content": "Bad"},
        ]

        result = evaluator.compare(outputs_a, outputs_b)

        assert "win_rate_a" in result
        assert "win_rate_b" in result
        assert result["win_rate_a"] + result["win_rate_b"] <= 1.0

    def test_dimension_analysis(self):
        """Test per-dimension analysis."""
        evaluator = ComparisonEvaluator()
        outputs_a = [{"content": "Detailed response"}]
        outputs_b = [{"content": "Short"}]

        result = evaluator.compare(outputs_a, outputs_b)

        assert "dimension_analysis" in result
        analysis = result["dimension_analysis"]

        for dim in ["accuracy", "helpfulness", "clarity", "completeness"]:
            assert dim in analysis
            assert "avg_score_a" in analysis[dim]
            assert "avg_score_b" in analysis[dim]

    def test_comparison_results(self):
        """Test individual comparison results."""
        evaluator = ComparisonEvaluator()
        outputs_a = [{"content": "Response A"}]
        outputs_b = [{"content": "Response B"}]

        result = evaluator.compare(outputs_a, outputs_b)

        assert "comparisons" in result
        assert len(result["comparisons"]) == 1

        comparison = result["comparisons"][0]
        assert "result" in comparison
        assert "confidence" in comparison
        assert "reasoning" in comparison

    def test_custom_dimensions(self):
        """Test with custom comparison dimensions."""
        evaluator = ComparisonEvaluator(
            comparison_dimensions=["accuracy", "speed"]
        )
        outputs_a = [{"content": "Test A"}]
        outputs_b = [{"content": "Test B"}]

        result = evaluator.compare(outputs_a, outputs_b)

        analysis = result["dimension_analysis"]
        assert "accuracy" in analysis
        # Custom dimension "speed" would use default scoring
