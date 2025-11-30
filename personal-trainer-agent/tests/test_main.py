"""Tests for the main PersonalTrainerAgent class."""

import pytest
from pathlib import Path
import tempfile
import json

from personal_trainer_agent import PersonalTrainerAgent
from personal_trainer_agent.main import TrainingConfig


class TestTrainingConfig:
    """Tests for TrainingConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TrainingConfig(name="test", target_agent="test-agent")

        assert config.name == "test"
        assert config.target_agent == "test-agent"
        assert config.training_method == "prompt_optimization"
        assert config.max_iterations == 10
        assert config.improvement_threshold == 0.1

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = TrainingConfig(name="test", target_agent="agent1")
        data = config.to_dict()

        assert data["name"] == "test"
        assert data["target_agent"] == "agent1"
        assert "output_dir" in data

    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "name": "loaded",
            "target_agent": "agent2",
            "max_iterations": 5,
        }
        config = TrainingConfig.from_dict(data)

        assert config.name == "loaded"
        assert config.target_agent == "agent2"
        assert config.max_iterations == 5


class TestPersonalTrainerAgent:
    """Tests for PersonalTrainerAgent."""

    def test_initialization(self):
        """Test agent initialization."""
        trainer = PersonalTrainerAgent()

        assert trainer.config is not None
        assert trainer.analyzer is not None
        assert trainer.weakness_detector is not None

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = TrainingConfig(
            name="custom",
            target_agent="my-agent",
            max_iterations=5,
        )
        trainer = PersonalTrainerAgent(config=config)

        assert trainer.config.name == "custom"
        assert trainer.config.max_iterations == 5

    def test_analyze_empty_outputs(self):
        """Test analyzing empty outputs."""
        trainer = PersonalTrainerAgent()
        result = trainer.analyze([])

        assert "error" in result.get("performance", {})

    def test_analyze_with_outputs(self):
        """Test analyzing outputs."""
        trainer = PersonalTrainerAgent()
        outputs = [
            {"content": "This is a helpful response.", "status": "completed"},
            {"content": "Another good response here.", "status": "completed"},
        ]

        result = trainer.analyze(outputs)

        assert "performance" in result
        assert "weaknesses" in result
        assert "recommendations" in result

    def test_analyze_with_expected(self):
        """Test analyzing with expected outputs."""
        trainer = PersonalTrainerAgent()
        outputs = [{"content": "Hello world", "status": "completed"}]
        expected = [{"content": "Hello world", "status": "completed"}]

        result = trainer.analyze(outputs, expected)

        assert "performance" in result
        assert result["performance"].get("has_expected") is True

    def test_evaluate_with_rubric(self):
        """Test evaluation with rubric."""
        trainer = PersonalTrainerAgent()
        outputs = [{"content": "This is a clear and helpful response."}]
        rubric = {
            "criteria": [
                {"name": "clarity", "description": "Response is clear", "max_score": 10},
                {"name": "helpfulness", "description": "Response is helpful", "max_score": 10},
            ]
        }

        result = trainer.evaluate(outputs, rubric)

        assert "clarity" in result
        assert "helpfulness" in result
        assert "_overall" in result

    def test_create_improvement_plan(self):
        """Test creating an improvement plan."""
        trainer = PersonalTrainerAgent()
        analysis = {
            "performance": {"overall_score": 0.6},
            "weaknesses": [
                {"id": "W1", "severity": "high", "description": "Test weakness"},
            ],
            "recommendations": [
                {"weakness_id": "W1", "priority": "high", "suggestion": "Fix it"},
            ],
        }

        plan = trainer.create_improvement_plan(analysis)

        assert "target_agent" in plan
        assert "improvements" in plan
        assert "success_criteria" in plan

    def test_session_report(self):
        """Test getting session report."""
        trainer = PersonalTrainerAgent()
        report = trainer.get_session_report()

        assert "session" in report
        assert "metrics" in report
        assert "config" in report

    def test_save_and_load_session(self):
        """Test saving and loading session."""
        trainer = PersonalTrainerAgent(
            config=TrainingConfig(name="save-test", target_agent="test")
        )

        # Analyze something to create data
        trainer.analyze([{"content": "Test content"}])

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.json"
            trainer.save_session(path)

            assert path.exists()

            # Load and verify
            loaded = PersonalTrainerAgent.load_session(path)
            assert loaded.config.name == "save-test"


class TestCoachingSession:
    """Tests for coaching sessions."""

    def test_coaching_without_llm(self):
        """Test coaching session without LLM client."""
        trainer = PersonalTrainerAgent()
        outputs = [{"content": "Test output"}]

        result = trainer.coaching_session(outputs)

        assert "error" in result
        assert "LLM client required" in result["error"]

    def test_coaching_with_feedback(self):
        """Test coaching session with human feedback."""
        trainer = PersonalTrainerAgent()
        outputs = [{"content": "Test output"}]

        result = trainer.coaching_session(outputs, feedback="Needs improvement")

        # Without LLM, should return error
        assert "error" in result
