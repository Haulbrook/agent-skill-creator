"""Tests for trainer modules."""

import pytest

from personal_trainer_agent.trainers import TRLTrainer, PromptOptimizer
from personal_trainer_agent.trainers.trl_trainer import TRLConfig
from personal_trainer_agent.trainers.prompt_optimizer import OptimizationConfig


class TestTRLTrainer:
    """Tests for TRLTrainer."""

    def test_initialization(self):
        """Test trainer initialization."""
        trainer = TRLTrainer()

        assert trainer.config is not None
        assert trainer.model is None  # Not loaded until training

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = TRLConfig(
            model_name="gpt2",
            learning_rate=1e-4,
            batch_size=8,
        )
        trainer = TRLTrainer(config=config)

        assert trainer.config.learning_rate == 1e-4
        assert trainer.config.batch_size == 8

    def test_train_without_trl(self):
        """Test training when TRL is not installed."""
        trainer = TRLTrainer()

        # If TRL is not available, should return error
        if not trainer._trl_available:
            result = trainer.train(
                plan={"training_method": "dpo"},
                dataset=[{"prompt": "test", "chosen": "good", "rejected": "bad"}],
            )

            assert result["status"] == "error"
            assert "TRL not available" in result["error"]

    def test_train_without_dataset(self):
        """Test training without dataset."""
        trainer = TRLTrainer()

        result = trainer.train(plan={"training_method": "dpo"}, dataset=None)

        assert result["status"] == "error"
        assert "No training dataset" in result["error"]

    def test_config_to_dict(self):
        """Test config serialization."""
        config = TRLConfig(model_name="test-model")
        data = config.to_dict()

        assert data["model_name"] == "test-model"
        assert "learning_rate" in data
        assert "output_dir" in data


class TestPromptOptimizer:
    """Tests for PromptOptimizer."""

    def test_initialization(self):
        """Test optimizer initialization."""
        optimizer = PromptOptimizer()

        assert optimizer.config is not None
        assert len(optimizer.history) == 0

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = OptimizationConfig(
            max_iterations=5,
            population_size=3,
        )
        optimizer = PromptOptimizer(config=config)

        assert optimizer.config.max_iterations == 5
        assert optimizer.config.population_size == 3

    def test_optimize_basic(self):
        """Test basic optimization."""
        optimizer = PromptOptimizer(
            config=OptimizationConfig(max_iterations=3, population_size=3)
        )

        plan = {
            "improvements": [
                {"action": "Be more helpful"},
                {"action": "Be clearer"},
            ]
        }

        result = optimizer.optimize(plan)

        assert result["status"] == "completed"
        assert "optimized_prompt" in result
        assert "before" in result
        assert "after" in result

    def test_optimize_with_base_prompt(self):
        """Test optimization with base prompt."""
        optimizer = PromptOptimizer(
            config=OptimizationConfig(max_iterations=2, population_size=2)
        )

        result = optimizer.optimize(
            plan={"improvements": []},
            base_prompt="You are a helpful assistant.",
        )

        assert result["status"] == "completed"
        # Optimized prompt should be based on the input
        assert len(result["optimized_prompt"]) > 0

    def test_optimize_with_examples(self):
        """Test optimization with training examples."""
        optimizer = PromptOptimizer(
            config=OptimizationConfig(max_iterations=2, population_size=2)
        )

        examples = [
            {"input": "Hello", "expected": "Hi there!"},
            {"input": "Help", "expected": "How can I assist?"},
        ]

        result = optimizer.optimize(
            plan={"improvements": []},
            examples=examples,
        )

        assert result["status"] == "completed"

    def test_optimize_with_custom_evaluator(self):
        """Test optimization with custom evaluator."""
        optimizer = PromptOptimizer(
            config=OptimizationConfig(max_iterations=2, population_size=2)
        )

        def custom_evaluator(prompt, examples):
            # Simple evaluator that prefers longer prompts
            return min(10.0, len(prompt) / 50)

        result = optimizer.optimize(
            plan={"improvements": []},
            base_prompt="Short",
            evaluator=custom_evaluator,
        )

        assert result["status"] == "completed"

    def test_history_tracking(self):
        """Test that optimization history is tracked."""
        optimizer = PromptOptimizer(
            config=OptimizationConfig(max_iterations=3, population_size=2)
        )

        optimizer.optimize(plan={"improvements": []})

        assert len(optimizer.history) > 0

    def test_improvement_calculation(self):
        """Test that improvement is calculated correctly."""
        optimizer = PromptOptimizer(
            config=OptimizationConfig(max_iterations=5, population_size=3)
        )

        result = optimizer.optimize(plan={"improvements": []})

        before_score = result["before"]["score"]
        after_score = result["after"]["score"]
        improvement = result["improvement"]

        assert improvement == pytest.approx(after_score - before_score, rel=0.01)
