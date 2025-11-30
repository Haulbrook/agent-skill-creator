"""
Main PersonalTrainerAgent class - the core orchestrator for agent improvement.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path
import json

from personal_trainer_agent.analyzers import PerformanceAnalyzer, WeaknessDetector
from personal_trainer_agent.evaluators import RubricEvaluator, ComparisonEvaluator
from personal_trainer_agent.trainers import TRLTrainer, PromptOptimizer
from personal_trainer_agent.utils import TrainingSession, MetricsTracker


@dataclass
class TrainingConfig:
    """Configuration for a training session."""

    name: str
    target_agent: str
    evaluation_rubric: Optional[dict[str, Any]] = None
    training_method: str = "prompt_optimization"  # or "trl", "openrl"
    max_iterations: int = 10
    improvement_threshold: float = 0.1
    output_dir: Path = field(default_factory=lambda: Path("./training_output"))

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "name": self.name,
            "target_agent": self.target_agent,
            "evaluation_rubric": self.evaluation_rubric,
            "training_method": self.training_method,
            "max_iterations": self.max_iterations,
            "improvement_threshold": self.improvement_threshold,
            "output_dir": str(self.output_dir),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrainingConfig":
        """Create config from dictionary."""
        data = data.copy()
        if "output_dir" in data:
            data["output_dir"] = Path(data["output_dir"])
        return cls(**data)


class PersonalTrainerAgent:
    """
    A meta-agent that systematically improves other AI agents.

    The Personal Trainer Agent works through a cycle of:
    1. Analysis - Identify current performance and weaknesses
    2. Evaluation - Score outputs against rubrics or baselines
    3. Training - Apply improvements via RL or prompt optimization
    4. Verification - Confirm improvements and iterate

    Example:
        ```python
        trainer = PersonalTrainerAgent()

        # Analyze an agent's performance
        analysis = trainer.analyze(
            agent_outputs=outputs,
            expected_outputs=expected
        )

        # Create improvement plan
        plan = trainer.create_improvement_plan(analysis)

        # Execute training
        result = trainer.train(plan)
        ```
    """

    def __init__(
        self,
        config: Optional[TrainingConfig] = None,
        llm_client: Optional[Any] = None,
    ) -> None:
        """
        Initialize the Personal Trainer Agent.

        Args:
            config: Training configuration. If None, uses defaults.
            llm_client: LLM client for analysis/coaching. Supports Anthropic or OpenAI.
        """
        self.config = config or TrainingConfig(name="default", target_agent="unknown")
        self.llm_client = llm_client

        # Initialize components
        self.analyzer = PerformanceAnalyzer()
        self.weakness_detector = WeaknessDetector()
        self.rubric_evaluator = RubricEvaluator()
        self.comparison_evaluator = ComparisonEvaluator()
        self.prompt_optimizer = PromptOptimizer()
        self.trl_trainer: Optional[TRLTrainer] = None

        # Session tracking
        self.session = TrainingSession(name=self.config.name)
        self.metrics = MetricsTracker()

    def analyze(
        self,
        agent_outputs: list[dict[str, Any]],
        expected_outputs: Optional[list[dict[str, Any]]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Analyze agent performance to identify strengths and weaknesses.

        Args:
            agent_outputs: List of agent outputs to analyze
            expected_outputs: Optional expected/ideal outputs for comparison
            context: Additional context for analysis

        Returns:
            Analysis results including performance metrics and identified issues
        """
        # Run performance analysis
        performance = self.analyzer.analyze(agent_outputs, expected_outputs)

        # Detect specific weaknesses
        weaknesses = self.weakness_detector.detect(
            outputs=agent_outputs,
            performance=performance,
            context=context,
        )

        # Track metrics
        self.metrics.record("analysis", {
            "num_outputs": len(agent_outputs),
            "performance_score": performance.get("overall_score", 0),
            "num_weaknesses": len(weaknesses),
        })

        return {
            "performance": performance,
            "weaknesses": weaknesses,
            "recommendations": self._generate_recommendations(performance, weaknesses),
        }

    def evaluate(
        self,
        outputs: list[dict[str, Any]],
        rubric: Optional[dict[str, Any]] = None,
        baseline_outputs: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Evaluate agent outputs against rubrics or baselines.

        Args:
            outputs: Outputs to evaluate
            rubric: Evaluation rubric with criteria and scoring
            baseline_outputs: Optional baseline for comparison

        Returns:
            Evaluation results with scores and feedback
        """
        results: dict[str, Any] = {}

        # Rubric-based evaluation
        if rubric or self.config.evaluation_rubric:
            eval_rubric = rubric or self.config.evaluation_rubric
            results["rubric_scores"] = self.rubric_evaluator.evaluate(
                outputs=outputs,
                rubric=eval_rubric,
            )

        # Comparison-based evaluation
        if baseline_outputs:
            results["comparison"] = self.comparison_evaluator.compare(
                outputs_a=outputs,
                outputs_b=baseline_outputs,
            )

        # Track metrics
        self.metrics.record("evaluation", results)

        return results

    def create_improvement_plan(
        self,
        analysis: dict[str, Any],
        focus_areas: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Create a structured improvement plan based on analysis.

        Args:
            analysis: Results from analyze()
            focus_areas: Specific areas to focus on

        Returns:
            Improvement plan with prioritized actions
        """
        weaknesses = analysis.get("weaknesses", [])
        recommendations = analysis.get("recommendations", [])

        # Prioritize based on impact and feasibility
        prioritized = self._prioritize_improvements(
            weaknesses=weaknesses,
            recommendations=recommendations,
            focus_areas=focus_areas,
        )

        plan = {
            "target_agent": self.config.target_agent,
            "training_method": self.config.training_method,
            "improvements": prioritized,
            "estimated_iterations": min(len(prioritized), self.config.max_iterations),
            "success_criteria": {
                "improvement_threshold": self.config.improvement_threshold,
                "target_weaknesses": [w["id"] for w in weaknesses[:3]],
            },
        }

        self.session.set_plan(plan)
        return plan

    def train(
        self,
        plan: dict[str, Any],
        training_data: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Execute training based on the improvement plan.

        Args:
            plan: Improvement plan from create_improvement_plan()
            training_data: Optional training examples

        Returns:
            Training results with before/after metrics
        """
        method = plan.get("training_method", self.config.training_method)

        if method == "prompt_optimization":
            result = self.prompt_optimizer.optimize(
                plan=plan,
                examples=training_data,
            )
        elif method == "trl":
            if self.trl_trainer is None:
                self.trl_trainer = TRLTrainer()
            result = self.trl_trainer.train(
                plan=plan,
                dataset=training_data,
            )
        else:
            raise ValueError(f"Unknown training method: {method}")

        # Record results
        self.session.record_iteration(result)
        self.metrics.record("training", result)

        return result

    def coaching_session(
        self,
        agent_outputs: list[dict[str, Any]],
        feedback: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Run an interactive coaching session for the agent.

        This provides detailed, actionable feedback on outputs.

        Args:
            agent_outputs: Outputs to coach on
            feedback: Optional human feedback to incorporate

        Returns:
            Coaching feedback with specific suggestions
        """
        if not self.llm_client:
            return {
                "error": "LLM client required for coaching sessions",
                "suggestion": "Initialize with llm_client parameter",
            }

        # Analyze current outputs
        analysis = self.analyze(agent_outputs)

        # Generate coaching feedback
        coaching = self._generate_coaching_feedback(
            outputs=agent_outputs,
            analysis=analysis,
            human_feedback=feedback,
        )

        return {
            "analysis_summary": analysis,
            "coaching_feedback": coaching,
            "action_items": self._extract_action_items(coaching),
        }

    def get_session_report(self) -> dict[str, Any]:
        """Get a summary report of the current training session."""
        return {
            "session": self.session.to_dict(),
            "metrics": self.metrics.get_summary(),
            "config": self.config.to_dict(),
        }

    def save_session(self, path: Optional[Path] = None) -> Path:
        """Save the current session to disk."""
        save_path = path or self.config.output_dir / f"{self.session.name}_session.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w") as f:
            json.dump(self.get_session_report(), f, indent=2, default=str)

        return save_path

    @classmethod
    def load_session(cls, path: Path) -> "PersonalTrainerAgent":
        """Load a session from disk."""
        with open(path) as f:
            data = json.load(f)

        config = TrainingConfig.from_dict(data.get("config", {}))
        trainer = cls(config=config)
        trainer.session = TrainingSession.from_dict(data.get("session", {}))
        trainer.metrics = MetricsTracker.from_dict(data.get("metrics", {}))

        return trainer

    def _generate_recommendations(
        self,
        performance: dict[str, Any],
        weaknesses: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate improvement recommendations."""
        recommendations = []

        for weakness in weaknesses:
            recommendations.append({
                "weakness_id": weakness.get("id"),
                "priority": weakness.get("severity", "medium"),
                "suggestion": weakness.get("suggestion", "Review and improve"),
                "estimated_impact": weakness.get("impact", 0.1),
            })

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 2))

        return recommendations

    def _prioritize_improvements(
        self,
        weaknesses: list[dict[str, Any]],
        recommendations: list[dict[str, Any]],
        focus_areas: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """Prioritize improvements based on impact and focus areas."""
        improvements = []

        for rec in recommendations:
            improvement = {
                "id": rec.get("weakness_id"),
                "action": rec.get("suggestion"),
                "priority": rec.get("priority"),
                "expected_impact": rec.get("estimated_impact"),
            }

            # Boost priority if in focus areas
            if focus_areas:
                weakness = next(
                    (w for w in weaknesses if w.get("id") == rec.get("weakness_id")),
                    None
                )
                if weakness and any(
                    area.lower() in weakness.get("category", "").lower()
                    for area in focus_areas
                ):
                    improvement["boosted"] = True

            improvements.append(improvement)

        return improvements

    def _generate_coaching_feedback(
        self,
        outputs: list[dict[str, Any]],
        analysis: dict[str, Any],
        human_feedback: Optional[str] = None,
    ) -> str:
        """Generate coaching feedback using LLM."""
        # This would use the LLM client to generate detailed feedback
        # Placeholder implementation
        feedback_parts = [
            "## Coaching Feedback\n",
            f"Analyzed {len(outputs)} outputs.\n",
        ]

        if analysis.get("weaknesses"):
            feedback_parts.append("\n### Areas for Improvement:\n")
            for w in analysis["weaknesses"][:3]:
                feedback_parts.append(f"- {w.get('description', 'Unknown issue')}\n")

        if human_feedback:
            feedback_parts.append(f"\n### Human Feedback:\n{human_feedback}\n")

        return "".join(feedback_parts)

    def _extract_action_items(self, coaching: str) -> list[str]:
        """Extract action items from coaching feedback."""
        # Simple extraction - would be more sophisticated with LLM
        action_items = []
        for line in coaching.split("\n"):
            if line.strip().startswith("- "):
                action_items.append(line.strip()[2:])
        return action_items
