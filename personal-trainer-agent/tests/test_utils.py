"""Tests for utility modules."""

import pytest
from pathlib import Path
import tempfile

from personal_trainer_agent.utils import TrainingSession, MetricsTracker


class TestTrainingSession:
    """Tests for TrainingSession."""

    def test_initialization(self):
        """Test session initialization."""
        session = TrainingSession(name="test-session")

        assert session.name == "test-session"
        assert session.status == "active"
        assert session.iteration_count == 0

    def test_set_plan(self):
        """Test setting improvement plan."""
        session = TrainingSession(name="test")
        plan = {"improvements": [{"action": "test"}]}

        session.set_plan(plan)

        assert session.plan == plan
        assert "plan_set_at" in session.metadata

    def test_record_iteration(self):
        """Test recording training iteration."""
        session = TrainingSession(name="test")
        result = {
            "method": "prompt_optimization",
            "before": {"score": 0.5},
            "after": {"score": 0.7},
            "improvement": {"score": 0.2},
        }

        iteration = session.record_iteration(result)

        assert session.iteration_count == 1
        assert iteration.method == "prompt_optimization"
        assert iteration.improvement["score"] == 0.2

    def test_total_improvement(self):
        """Test calculating total improvement."""
        session = TrainingSession(name="test")

        session.record_iteration({
            "method": "opt",
            "before": {"score": 0.5},
            "after": {"score": 0.6},
            "improvement": {"score": 0.1},
        })
        session.record_iteration({
            "method": "opt",
            "before": {"score": 0.6},
            "after": {"score": 0.8},
            "improvement": {"score": 0.2},
        })

        total = session.total_improvement
        assert total["score"] == pytest.approx(0.3)

    def test_latest_metrics(self):
        """Test getting latest metrics."""
        session = TrainingSession(name="test")

        session.record_iteration({
            "method": "opt",
            "before": {"score": 0.5},
            "after": {"score": 0.7, "accuracy": 0.8},
            "improvement": {},
        })

        latest = session.latest_metrics
        assert latest["score"] == 0.7
        assert latest["accuracy"] == 0.8

    def test_complete(self):
        """Test completing a session."""
        session = TrainingSession(name="test")

        session.complete()

        assert session.status == "completed"
        assert "completed_at" in session.metadata

    def test_to_dict(self):
        """Test serializing session."""
        session = TrainingSession(name="test")
        session.record_iteration({
            "method": "opt",
            "before": {},
            "after": {},
            "improvement": {},
        })

        data = session.to_dict()

        assert data["name"] == "test"
        assert data["iteration_count"] == 1
        assert "iterations" in data

    def test_from_dict(self):
        """Test deserializing session."""
        data = {
            "name": "loaded",
            "id": "test123",
            "status": "active",
            "iterations": [
                {
                    "id": "iter1",
                    "timestamp": "2024-01-01T00:00:00",
                    "method": "opt",
                    "metrics_before": {},
                    "metrics_after": {},
                    "improvement": {},
                }
            ],
        }

        session = TrainingSession.from_dict(data)

        assert session.name == "loaded"
        assert session.iteration_count == 1

    def test_save_and_load(self):
        """Test saving and loading session."""
        session = TrainingSession(name="save-test")
        session.record_iteration({
            "method": "opt",
            "before": {"score": 0.5},
            "after": {"score": 0.7},
            "improvement": {"score": 0.2},
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.json"
            session.save(path)

            loaded = TrainingSession.load(path)

            assert loaded.name == "save-test"
            assert loaded.iteration_count == 1

    def test_get_summary(self):
        """Test getting human-readable summary."""
        session = TrainingSession(name="summary-test")
        session.record_iteration({
            "method": "opt",
            "before": {},
            "after": {},
            "improvement": {"score": 0.1},
        })

        summary = session.get_summary()

        assert "summary-test" in summary
        assert "Iterations: 1" in summary


class TestMetricsTracker:
    """Tests for MetricsTracker."""

    def test_initialization(self):
        """Test tracker initialization."""
        tracker = MetricsTracker()

        assert len(tracker.metrics) == 0

    def test_record_metrics(self):
        """Test recording metrics."""
        tracker = MetricsTracker()

        tracker.record("training", {"loss": 0.5, "accuracy": 0.8})

        assert len(tracker.metrics) == 2
        assert tracker.get_latest("loss") == 0.5
        assert tracker.get_latest("accuracy") == 0.8

    def test_record_with_metadata(self):
        """Test recording metrics with metadata."""
        tracker = MetricsTracker()

        tracker.record(
            "evaluation",
            {"score": 0.9},
            metadata={"model": "v1"},
        )

        assert tracker.metrics[0].metadata["model"] == "v1"

    def test_get_metric_history(self):
        """Test getting metric history."""
        tracker = MetricsTracker()

        tracker.record("train", {"loss": 0.5})
        tracker.record("train", {"loss": 0.4})
        tracker.record("train", {"loss": 0.3})

        history = tracker.get_metric("loss")

        assert history == [0.5, 0.4, 0.3]

    def test_get_stats(self):
        """Test getting metric statistics."""
        tracker = MetricsTracker()

        tracker.record("train", {"loss": 0.5})
        tracker.record("train", {"loss": 0.4})
        tracker.record("train", {"loss": 0.3})

        stats = tracker.get_stats("loss")

        assert stats["count"] == 3
        assert stats["mean"] == pytest.approx(0.4)
        assert stats["min"] == 0.3
        assert stats["max"] == 0.5
        assert stats["latest"] == 0.3
        assert "std" in stats
        assert "trend" in stats

    def test_get_category_stats(self):
        """Test getting stats by category."""
        tracker = MetricsTracker()

        tracker.record("training", {"loss": 0.5, "accuracy": 0.7})
        tracker.record("training", {"loss": 0.3, "accuracy": 0.9})

        stats = tracker.get_category_stats("training")

        assert "loss" in stats
        assert "accuracy" in stats
        assert stats["loss"]["mean"] == pytest.approx(0.4)
        assert stats["accuracy"]["mean"] == pytest.approx(0.8)

    def test_get_summary(self):
        """Test getting metrics summary."""
        tracker = MetricsTracker()

        tracker.record("training", {"loss": 0.5})
        tracker.record("evaluation", {"score": 0.8})

        summary = tracker.get_summary()

        assert summary["total_points"] == 2
        assert "training" in summary["categories"]
        assert "evaluation" in summary["categories"]

    def test_get_trend_improving(self):
        """Test detecting improving trend."""
        tracker = MetricsTracker()

        # Simulate improving scores
        for score in [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]:
            tracker.record("eval", {"score": score})

        trend = tracker.get_trend("score", window=5)

        assert trend == "improving"

    def test_get_trend_declining(self):
        """Test detecting declining trend."""
        tracker = MetricsTracker()

        # Simulate declining scores
        for score in [0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45]:
            tracker.record("eval", {"score": score})

        trend = tracker.get_trend("score", window=5)

        assert trend == "declining"

    def test_get_trend_stable(self):
        """Test detecting stable trend."""
        tracker = MetricsTracker()

        # Simulate stable scores
        for score in [0.7, 0.71, 0.69, 0.7, 0.71, 0.7, 0.69, 0.71, 0.7, 0.7]:
            tracker.record("eval", {"score": score})

        trend = tracker.get_trend("score", window=5)

        assert trend == "stable"

    def test_clear(self):
        """Test clearing metrics."""
        tracker = MetricsTracker()

        tracker.record("train", {"loss": 0.5})
        tracker.clear()

        assert len(tracker.metrics) == 0
        assert len(tracker.by_category) == 0

    def test_to_and_from_dict(self):
        """Test serialization and deserialization."""
        tracker = MetricsTracker()
        tracker.record("train", {"loss": 0.5, "accuracy": 0.8})

        data = tracker.to_dict()
        loaded = MetricsTracker.from_dict(data)

        assert loaded.get_latest("loss") == 0.5
        assert loaded.get_latest("accuracy") == 0.8
