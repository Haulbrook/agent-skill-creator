"""
Personal Trainer Agent - Main Orchestrator

The central coordinator for agent training and improvement. This module orchestrates
the entire training pipeline from initial analysis through iterative coaching.

Author: Agent-Skill-Creator
Version: 1.0.0
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .analyzers.performance_analyzer import PerformanceAnalyzer
from .analyzers.output_evaluator import OutputEvaluator
from .analyzers.pattern_detector import PatternDetector
from .trainers.trl_trainer import TRLTrainer
from .trainers.openrl_trainer import OpenRLTrainer
from .trainers.prompt_optimizer import PromptOptimizer
from .evaluators.rubric_evaluator import RubricEvaluator
from .evaluators.comparison_evaluator import ComparisonEvaluator
from .utils.session_manager import SessionManager
from .utils.metrics_tracker import MetricsTracker


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingMode(Enum):
    """Available training modes for agent improvement."""
    ANALYSIS_ONLY = "analysis_only"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    TRL_RLHF = "trl_rlhf"
    TRL_DPO = "trl_dpo"
    TRL_PPO = "trl_ppo"
    OPENRL = "openrl"
    FULL_PIPELINE = "full_pipeline"


class CoachingIntensity(Enum):
    """Coaching intensity levels."""
    LIGHT = "light"  # Quick feedback, minimal iterations
    MODERATE = "moderate"  # Balanced approach
    INTENSIVE = "intensive"  # Deep analysis, many iterations


@dataclass
class AgentProfile:
    """Profile describing the agent being trained."""
    name: str
    description: str
    domain: str  # e.g., "website_building", "marketing", "coding"
    current_prompts: Dict[str, str] = field(default_factory=dict)
    sample_outputs: List[Dict[str, Any]] = field(default_factory=list)
    known_weaknesses: List[str] = field(default_factory=list)
    target_improvements: List[str] = field(default_factory=list)
    model_info: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TrainingSession:
    """Represents an active training session."""
    session_id: str
    agent_profile: AgentProfile
    mode: TrainingMode
    intensity: CoachingIntensity
    started_at: str
    iterations_completed: int = 0
    current_metrics: Dict[str, float] = field(default_factory=dict)
    improvement_history: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"


@dataclass
class EvaluationResult:
    """Result of evaluating an agent's output."""
    output_id: str
    overall_score: float  # 0-10
    dimension_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    comparative_notes: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TrainingRecommendation:
    """Recommended training actions based on analysis."""
    priority: int  # 1-5, 1 being highest
    category: str  # "prompt", "data", "model", "architecture"
    action: str
    rationale: str
    expected_impact: str
    implementation_steps: List[str]
    estimated_effort: str  # "low", "medium", "high"
    dependencies: List[str] = field(default_factory=list)


class PersonalTrainerAgent:
    """
    Main orchestrator for agent training and improvement.

    This class coordinates all training activities including:
    - Performance analysis and evaluation
    - Training data generation
    - Integration with TRL/OpenRL frameworks
    - Prompt optimization
    - Iterative coaching sessions

    Usage:
        trainer = PersonalTrainerAgent()

        # Create agent profile
        profile = trainer.create_agent_profile(
            name="WebsiteBuilder",
            description="Bot that creates frontend websites",
            domain="website_building"
        )

        # Start training session
        session = trainer.start_training_session(
            profile,
            mode=TrainingMode.PROMPT_OPTIMIZATION,
            intensity=CoachingIntensity.MODERATE
        )

        # Evaluate outputs
        results = trainer.evaluate_outputs(session, sample_outputs)

        # Get improvement recommendations
        recommendations = trainer.get_recommendations(session)

        # Apply improvements
        trainer.apply_improvements(session, recommendations)
    """

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        trl_config: Optional[Dict[str, Any]] = None,
        openrl_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Personal Trainer Agent.

        Args:
            storage_dir: Directory for storing session data and metrics
            trl_config: Configuration for TRL training
            openrl_config: Configuration for OpenRL training
        """
        self.storage_dir = storage_dir or Path.home() / ".personal_trainer_agent"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.performance_analyzer = PerformanceAnalyzer()
        self.output_evaluator = OutputEvaluator()
        self.pattern_detector = PatternDetector()
        self.trl_trainer = TRLTrainer(trl_config or {})
        self.openrl_trainer = OpenRLTrainer(openrl_config or {})
        self.prompt_optimizer = PromptOptimizer()
        self.rubric_evaluator = RubricEvaluator()
        self.comparison_evaluator = ComparisonEvaluator()
        self.session_manager = SessionManager(self.storage_dir / "sessions")
        self.metrics_tracker = MetricsTracker(self.storage_dir / "metrics")

        # Active sessions
        self._active_sessions: Dict[str, TrainingSession] = {}

        # Load any saved sessions
        self._load_active_sessions()

        logger.info("Personal Trainer Agent initialized successfully")

    def _load_active_sessions(self) -> None:
        """Load previously active sessions from storage."""
        saved_sessions = self.session_manager.load_all_active()
        for session_data in saved_sessions:
            session = self._deserialize_session(session_data)
            if session.status == "active":
                self._active_sessions[session.session_id] = session
        logger.info(f"Loaded {len(self._active_sessions)} active sessions")

    def _deserialize_session(self, data: Dict[str, Any]) -> TrainingSession:
        """Deserialize session data from storage."""
        profile = AgentProfile(**data["agent_profile"])
        return TrainingSession(
            session_id=data["session_id"],
            agent_profile=profile,
            mode=TrainingMode(data["mode"]),
            intensity=CoachingIntensity(data["intensity"]),
            started_at=data["started_at"],
            iterations_completed=data.get("iterations_completed", 0),
            current_metrics=data.get("current_metrics", {}),
            improvement_history=data.get("improvement_history", []),
            status=data.get("status", "active")
        )

    def create_agent_profile(
        self,
        name: str,
        description: str,
        domain: str,
        current_prompts: Optional[Dict[str, str]] = None,
        sample_outputs: Optional[List[Dict[str, Any]]] = None,
        known_weaknesses: Optional[List[str]] = None,
        target_improvements: Optional[List[str]] = None,
        model_info: Optional[Dict[str, Any]] = None
    ) -> AgentProfile:
        """
        Create a profile for the agent to be trained.

        Args:
            name: Name identifier for the agent
            description: What the agent does
            domain: Primary domain (e.g., "website_building", "marketing", "coding")
            current_prompts: Dictionary of current prompts used by the agent
            sample_outputs: List of sample outputs for initial analysis
            known_weaknesses: List of known issues with the agent
            target_improvements: Specific improvements the user wants
            model_info: Information about the underlying model

        Returns:
            AgentProfile instance
        """
        profile = AgentProfile(
            name=name,
            description=description,
            domain=domain,
            current_prompts=current_prompts or {},
            sample_outputs=sample_outputs or [],
            known_weaknesses=known_weaknesses or [],
            target_improvements=target_improvements or [],
            model_info=model_info
        )

        logger.info(f"Created agent profile: {name} in domain {domain}")
        return profile

    def start_training_session(
        self,
        profile: AgentProfile,
        mode: TrainingMode = TrainingMode.PROMPT_OPTIMIZATION,
        intensity: CoachingIntensity = CoachingIntensity.MODERATE,
        custom_rubric: Optional[Dict[str, Any]] = None
    ) -> TrainingSession:
        """
        Start a new training session for an agent.

        Args:
            profile: The agent's profile
            mode: Training mode to use
            intensity: How intensive the coaching should be
            custom_rubric: Optional custom evaluation rubric

        Returns:
            New TrainingSession instance
        """
        session_id = self.session_manager.generate_session_id()

        session = TrainingSession(
            session_id=session_id,
            agent_profile=profile,
            mode=mode,
            intensity=intensity,
            started_at=datetime.now().isoformat()
        )

        # Configure rubric evaluator with custom or domain-specific rubric
        if custom_rubric:
            self.rubric_evaluator.set_rubric(custom_rubric)
        else:
            self.rubric_evaluator.load_domain_rubric(profile.domain)

        # Initialize metrics tracking for this session
        self.metrics_tracker.initialize_session(session_id, profile.name)

        # Perform initial analysis if sample outputs provided
        if profile.sample_outputs:
            initial_analysis = self._perform_initial_analysis(session)
            session.current_metrics = initial_analysis.get("metrics", {})

        # Store session
        self._active_sessions[session_id] = session
        self.session_manager.save_session(session)

        logger.info(f"Started training session {session_id} for {profile.name}")
        return session

    def _perform_initial_analysis(
        self,
        session: TrainingSession
    ) -> Dict[str, Any]:
        """Perform initial analysis of the agent's outputs."""
        outputs = session.agent_profile.sample_outputs

        # Analyze performance patterns
        performance_analysis = self.performance_analyzer.analyze(outputs)

        # Detect common patterns (good and bad)
        patterns = self.pattern_detector.detect(outputs)

        # Evaluate with rubric
        rubric_scores = []
        for output in outputs:
            score = self.rubric_evaluator.evaluate(output)
            rubric_scores.append(score)

        avg_score = sum(s["overall_score"] for s in rubric_scores) / len(rubric_scores) if rubric_scores else 0

        return {
            "metrics": {
                "initial_average_score": avg_score,
                "sample_count": len(outputs),
                "performance_summary": performance_analysis.get("summary", {}),
                "detected_patterns": len(patterns)
            },
            "performance_analysis": performance_analysis,
            "patterns": patterns,
            "rubric_scores": rubric_scores
        }

    def evaluate_outputs(
        self,
        session: TrainingSession,
        outputs: List[Dict[str, Any]],
        inputs: Optional[List[Dict[str, Any]]] = None
    ) -> List[EvaluationResult]:
        """
        Evaluate a batch of agent outputs.

        Args:
            session: The active training session
            outputs: List of outputs to evaluate
            inputs: Optional corresponding inputs for context

        Returns:
            List of EvaluationResult objects
        """
        results = []

        for i, output in enumerate(outputs):
            input_context = inputs[i] if inputs and i < len(inputs) else None

            # Get rubric evaluation
            rubric_eval = self.rubric_evaluator.evaluate(output, input_context)

            # Get output-specific evaluation
            output_eval = self.output_evaluator.evaluate(
                output,
                session.agent_profile.domain,
                input_context
            )

            # Combine evaluations
            result = EvaluationResult(
                output_id=f"{session.session_id}_{i}_{datetime.now().timestamp()}",
                overall_score=rubric_eval["overall_score"],
                dimension_scores=rubric_eval["dimension_scores"],
                strengths=output_eval["strengths"],
                weaknesses=output_eval["weaknesses"],
                improvement_suggestions=output_eval["suggestions"]
            )

            results.append(result)

            # Track metrics
            self.metrics_tracker.record_evaluation(
                session.session_id,
                result.overall_score,
                result.dimension_scores
            )

        # Update session metrics
        if results:
            avg_score = sum(r.overall_score for r in results) / len(results)
            session.current_metrics["latest_average_score"] = avg_score
            session.current_metrics["total_evaluations"] = session.current_metrics.get("total_evaluations", 0) + len(results)

        return results

    def compare_outputs(
        self,
        session: TrainingSession,
        output_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]],
        inputs: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Compare pairs of outputs (e.g., before/after improvement).

        Args:
            session: The active training session
            output_pairs: List of (output_a, output_b) tuples to compare
            inputs: Optional corresponding inputs for context

        Returns:
            List of comparison results
        """
        comparisons = []

        for i, (output_a, output_b) in enumerate(output_pairs):
            input_context = inputs[i] if inputs and i < len(inputs) else None

            comparison = self.comparison_evaluator.compare(
                output_a,
                output_b,
                input_context,
                session.agent_profile.domain
            )

            comparisons.append(comparison)

            # Track improvement
            if comparison.get("winner") == "b":
                improvement = comparison.get("improvement_percentage", 0)
                self.metrics_tracker.record_improvement(
                    session.session_id,
                    improvement,
                    comparison.get("improved_dimensions", [])
                )

        return comparisons

    def get_recommendations(
        self,
        session: TrainingSession,
        focus_areas: Optional[List[str]] = None
    ) -> List[TrainingRecommendation]:
        """
        Generate training recommendations based on analysis.

        Args:
            session: The active training session
            focus_areas: Optional specific areas to focus on

        Returns:
            Prioritized list of TrainingRecommendation objects
        """
        recommendations = []

        # Analyze current state
        weaknesses = session.agent_profile.known_weaknesses
        targets = session.agent_profile.target_improvements
        patterns = self.pattern_detector.get_negative_patterns(session.session_id)

        # Generate prompt-based recommendations
        prompt_recs = self.prompt_optimizer.analyze_prompts(
            session.agent_profile.current_prompts,
            session.agent_profile.domain,
            weaknesses
        )

        for rec in prompt_recs:
            recommendations.append(TrainingRecommendation(
                priority=rec["priority"],
                category="prompt",
                action=rec["action"],
                rationale=rec["rationale"],
                expected_impact=rec["expected_impact"],
                implementation_steps=rec["steps"],
                estimated_effort=rec["effort"]
            ))

        # Generate data-based recommendations
        if session.mode in [TrainingMode.TRL_RLHF, TrainingMode.TRL_DPO, TrainingMode.TRL_PPO]:
            data_recs = self._generate_data_recommendations(session, patterns)
            recommendations.extend(data_recs)

        # Generate model-based recommendations
        if session.mode in [TrainingMode.TRL_RLHF, TrainingMode.TRL_PPO, TrainingMode.OPENRL]:
            model_recs = self._generate_model_recommendations(session)
            recommendations.extend(model_recs)

        # Sort by priority
        recommendations.sort(key=lambda x: x.priority)

        # Filter by focus areas if specified
        if focus_areas:
            recommendations = [r for r in recommendations if r.category in focus_areas]

        return recommendations

    def _generate_data_recommendations(
        self,
        session: TrainingSession,
        patterns: List[Dict[str, Any]]
    ) -> List[TrainingRecommendation]:
        """Generate recommendations for training data."""
        recommendations = []

        # Check for data quantity
        sample_count = len(session.agent_profile.sample_outputs)
        if sample_count < 100:
            recommendations.append(TrainingRecommendation(
                priority=2,
                category="data",
                action="Collect more training examples",
                rationale=f"Current sample size ({sample_count}) is insufficient for effective RL training. Target 500+ examples.",
                expected_impact="Significantly improved model generalization",
                implementation_steps=[
                    "Run agent on diverse inputs to generate more outputs",
                    "Have humans rate outputs on quality scale",
                    "Create preference pairs (good vs bad) for DPO/RLHF",
                    "Ensure coverage of edge cases and failure modes"
                ],
                estimated_effort="medium"
            ))

        # Check for pattern-based improvements
        negative_patterns = [p for p in patterns if p.get("type") == "negative"]
        if negative_patterns:
            recommendations.append(TrainingRecommendation(
                priority=1,
                category="data",
                action=f"Create targeted training data for {len(negative_patterns)} identified failure patterns",
                rationale="Negative patterns indicate systematic issues that can be addressed with targeted training",
                expected_impact="Direct improvement in known failure cases",
                implementation_steps=[
                    "For each negative pattern, create 10-20 corrective examples",
                    "Include the problematic input type with ideal outputs",
                    "Add negative examples (what NOT to do) for contrast",
                    "Weight these examples higher in training"
                ],
                estimated_effort="medium",
                dependencies=["Pattern analysis complete"]
            ))

        return recommendations

    def _generate_model_recommendations(
        self,
        session: TrainingSession
    ) -> List[TrainingRecommendation]:
        """Generate recommendations for model training."""
        recommendations = []

        mode = session.mode
        model_info = session.agent_profile.model_info or {}

        if mode == TrainingMode.TRL_PPO:
            recommendations.append(TrainingRecommendation(
                priority=2,
                category="model",
                action="Configure PPO training with appropriate hyperparameters",
                rationale="PPO is effective for agents requiring exploration and iterative improvement",
                expected_impact="Improved output quality through policy optimization",
                implementation_steps=[
                    "Set learning rate between 1e-5 and 5e-5",
                    "Configure KL divergence penalty (0.1-0.3)",
                    "Set batch size based on available memory",
                    "Run for 3-10 epochs with early stopping",
                    "Monitor reward curves for convergence"
                ],
                estimated_effort="high"
            ))
        elif mode == TrainingMode.TRL_DPO:
            recommendations.append(TrainingRecommendation(
                priority=2,
                category="model",
                action="Set up DPO training with preference pairs",
                rationale="DPO is simpler than RLHF and effective for preference learning",
                expected_impact="Model learns to prefer higher-quality outputs",
                implementation_steps=[
                    "Format data as (prompt, chosen, rejected) triples",
                    "Use beta=0.1 as starting point",
                    "Set learning rate to 1e-6 to 5e-6",
                    "Train for 1-3 epochs",
                    "Validate on held-out preference pairs"
                ],
                estimated_effort="medium"
            ))
        elif mode == TrainingMode.OPENRL:
            recommendations.append(TrainingRecommendation(
                priority=2,
                category="model",
                action="Configure OpenRL environment and training",
                rationale="OpenRL provides flexible RL training with environment interactions",
                expected_impact="Agent learns through environment feedback loop",
                implementation_steps=[
                    "Define reward function based on evaluation rubric",
                    "Set up environment wrapper for agent interactions",
                    "Configure observation and action spaces",
                    "Choose appropriate algorithm (PPO, A2C, etc.)",
                    "Monitor training stability and reward progression"
                ],
                estimated_effort="high",
                dependencies=["OpenRL installed", "Reward function defined"]
            ))

        return recommendations

    def generate_training_data(
        self,
        session: TrainingSession,
        format_type: str = "dpo"
    ) -> Dict[str, Any]:
        """
        Generate formatted training data from session evaluations.

        Args:
            session: The active training session
            format_type: Format for training data ("dpo", "rlhf", "sft")

        Returns:
            Dictionary with formatted training data
        """
        evaluations = self.metrics_tracker.get_all_evaluations(session.session_id)
        samples = session.agent_profile.sample_outputs

        if format_type == "dpo":
            return self._format_dpo_data(evaluations, samples)
        elif format_type == "rlhf":
            return self._format_rlhf_data(evaluations, samples)
        elif format_type == "sft":
            return self._format_sft_data(evaluations, samples)
        else:
            raise ValueError(f"Unknown format type: {format_type}")

    def _format_dpo_data(
        self,
        evaluations: List[Dict[str, Any]],
        samples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format data for DPO training."""
        preference_pairs = []

        # Group by input and sort by score
        input_groups: Dict[str, List] = {}
        for i, sample in enumerate(samples):
            input_key = json.dumps(sample.get("input", {}), sort_keys=True)
            eval_score = evaluations[i]["overall_score"] if i < len(evaluations) else 5.0

            if input_key not in input_groups:
                input_groups[input_key] = []
            input_groups[input_key].append({
                "output": sample.get("output", ""),
                "score": eval_score
            })

        # Create preference pairs
        for input_key, outputs in input_groups.items():
            if len(outputs) >= 2:
                outputs.sort(key=lambda x: x["score"], reverse=True)
                for i in range(len(outputs) - 1):
                    if outputs[i]["score"] > outputs[i + 1]["score"]:
                        preference_pairs.append({
                            "prompt": json.loads(input_key),
                            "chosen": outputs[i]["output"],
                            "rejected": outputs[i + 1]["output"]
                        })

        return {
            "format": "dpo",
            "count": len(preference_pairs),
            "data": preference_pairs
        }

    def _format_rlhf_data(
        self,
        evaluations: List[Dict[str, Any]],
        samples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format data for RLHF training (reward modeling)."""
        reward_data = []

        for i, sample in enumerate(samples):
            eval_score = evaluations[i]["overall_score"] if i < len(evaluations) else 5.0

            reward_data.append({
                "prompt": sample.get("input", {}),
                "response": sample.get("output", ""),
                "reward": eval_score / 10.0  # Normalize to 0-1
            })

        return {
            "format": "rlhf",
            "count": len(reward_data),
            "data": reward_data
        }

    def _format_sft_data(
        self,
        evaluations: List[Dict[str, Any]],
        samples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format data for supervised fine-tuning (high-quality examples only)."""
        sft_data = []
        threshold = 7.0  # Only include high-quality examples

        for i, sample in enumerate(samples):
            eval_score = evaluations[i]["overall_score"] if i < len(evaluations) else 5.0

            if eval_score >= threshold:
                sft_data.append({
                    "prompt": sample.get("input", {}),
                    "completion": sample.get("output", "")
                })

        return {
            "format": "sft",
            "count": len(sft_data),
            "threshold": threshold,
            "data": sft_data
        }

    def run_trl_training(
        self,
        session: TrainingSession,
        training_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run TRL-based training.

        Args:
            session: The active training session
            training_data: Formatted training data
            config: Optional training configuration overrides

        Returns:
            Training results
        """
        format_type = training_data["format"]

        if format_type == "dpo":
            return self.trl_trainer.train_dpo(
                training_data["data"],
                session.agent_profile.model_info,
                config
            )
        elif format_type == "rlhf":
            return self.trl_trainer.train_rlhf(
                training_data["data"],
                session.agent_profile.model_info,
                config
            )
        else:
            return self.trl_trainer.train_sft(
                training_data["data"],
                session.agent_profile.model_info,
                config
            )

    def run_openrl_training(
        self,
        session: TrainingSession,
        environment_config: Dict[str, Any],
        reward_function: Callable,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run OpenRL-based training.

        Args:
            session: The active training session
            environment_config: Configuration for the RL environment
            reward_function: Function that computes rewards for outputs
            config: Optional training configuration overrides

        Returns:
            Training results
        """
        return self.openrl_trainer.train(
            session.agent_profile,
            environment_config,
            reward_function,
            config
        )

    def optimize_prompts(
        self,
        session: TrainingSession,
        evaluation_results: List[EvaluationResult]
    ) -> Dict[str, str]:
        """
        Optimize agent prompts based on evaluation feedback.

        Args:
            session: The active training session
            evaluation_results: Recent evaluation results

        Returns:
            Dictionary of optimized prompts
        """
        current_prompts = session.agent_profile.current_prompts

        # Extract weaknesses from evaluations
        all_weaknesses = []
        all_suggestions = []
        for result in evaluation_results:
            all_weaknesses.extend(result.weaknesses)
            all_suggestions.extend(result.improvement_suggestions)

        # Generate optimized prompts
        optimized = self.prompt_optimizer.optimize(
            current_prompts,
            all_weaknesses,
            all_suggestions,
            session.agent_profile.domain
        )

        return optimized

    def run_coaching_iteration(
        self,
        session: TrainingSession,
        new_outputs: List[Dict[str, Any]],
        new_inputs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Run a single coaching iteration.

        This is the main method for iterative improvement. Each call:
        1. Evaluates new outputs
        2. Generates recommendations
        3. Applies prompt optimizations
        4. Tracks progress

        Args:
            session: The active training session
            new_outputs: New outputs to evaluate
            new_inputs: Corresponding inputs

        Returns:
            Iteration results with recommendations and improvements
        """
        # Evaluate new outputs
        evaluations = self.evaluate_outputs(session, new_outputs, new_inputs)

        # Get current average score
        current_avg = sum(e.overall_score for e in evaluations) / len(evaluations) if evaluations else 0

        # Compare with previous iteration
        previous_avg = session.current_metrics.get("previous_average_score", current_avg)
        improvement = current_avg - previous_avg

        # Generate recommendations
        recommendations = self.get_recommendations(session)

        # Optimize prompts
        optimized_prompts = self.optimize_prompts(session, evaluations)

        # Update session
        session.iterations_completed += 1
        session.current_metrics["previous_average_score"] = current_avg
        session.current_metrics["latest_average_score"] = current_avg
        session.improvement_history.append({
            "iteration": session.iterations_completed,
            "average_score": current_avg,
            "improvement": improvement,
            "timestamp": datetime.now().isoformat()
        })

        # Save session
        self.session_manager.save_session(session)

        return {
            "iteration": session.iterations_completed,
            "evaluations": evaluations,
            "average_score": current_avg,
            "improvement_from_last": improvement,
            "recommendations": recommendations[:5],  # Top 5
            "optimized_prompts": optimized_prompts,
            "session_metrics": session.current_metrics
        }

    def get_session_progress(
        self,
        session: TrainingSession
    ) -> Dict[str, Any]:
        """
        Get detailed progress report for a session.

        Args:
            session: The active training session

        Returns:
            Comprehensive progress report
        """
        metrics = self.metrics_tracker.get_session_summary(session.session_id)

        return {
            "session_id": session.session_id,
            "agent_name": session.agent_profile.name,
            "mode": session.mode.value,
            "intensity": session.intensity.value,
            "started_at": session.started_at,
            "iterations_completed": session.iterations_completed,
            "current_metrics": session.current_metrics,
            "improvement_history": session.improvement_history,
            "overall_improvement": self._calculate_overall_improvement(session),
            "detailed_metrics": metrics,
            "recommendations_applied": self._get_applied_recommendations(session),
            "next_steps": self._generate_next_steps(session)
        }

    def _calculate_overall_improvement(
        self,
        session: TrainingSession
    ) -> Dict[str, Any]:
        """Calculate overall improvement metrics."""
        history = session.improvement_history

        if len(history) < 2:
            return {"status": "insufficient_data", "message": "Need at least 2 iterations"}

        initial_score = history[0]["average_score"]
        latest_score = history[-1]["average_score"]

        return {
            "initial_score": initial_score,
            "current_score": latest_score,
            "absolute_improvement": latest_score - initial_score,
            "percentage_improvement": ((latest_score - initial_score) / initial_score * 100) if initial_score > 0 else 0,
            "trend": "improving" if latest_score > initial_score else "declining" if latest_score < initial_score else "stable"
        }

    def _get_applied_recommendations(
        self,
        session: TrainingSession
    ) -> List[Dict[str, Any]]:
        """Get list of recommendations that have been applied."""
        return self.session_manager.get_applied_recommendations(session.session_id)

    def _generate_next_steps(
        self,
        session: TrainingSession
    ) -> List[str]:
        """Generate next steps based on current progress."""
        steps = []

        improvement = self._calculate_overall_improvement(session)

        if improvement.get("status") == "insufficient_data":
            steps.append("Run more coaching iterations to gather data")
            steps.append("Collect diverse sample outputs for comprehensive analysis")
        elif improvement.get("trend") == "improving":
            if improvement["percentage_improvement"] < 10:
                steps.append("Continue current approach - slow but steady improvement")
                steps.append("Consider more intensive coaching to accelerate improvement")
            else:
                steps.append("Excellent progress! Consider transitioning to RL training for further gains")
        elif improvement.get("trend") == "declining":
            steps.append("Review recent prompt changes - may need to revert")
            steps.append("Analyze failing cases in detail")
            steps.append("Consider adjusting coaching intensity or approach")
        else:
            steps.append("Scores are stable - try different optimization strategies")
            steps.append("Collect more training data for RL training")

        return steps

    def end_session(
        self,
        session: TrainingSession,
        save_artifacts: bool = True
    ) -> Dict[str, Any]:
        """
        End a training session and generate final report.

        Args:
            session: The session to end
            save_artifacts: Whether to save training artifacts

        Returns:
            Final session report
        """
        session.status = "completed"

        # Generate final report
        final_report = self.get_session_progress(session)
        final_report["completed_at"] = datetime.now().isoformat()

        # Save artifacts
        if save_artifacts:
            artifacts_dir = self.storage_dir / "artifacts" / session.session_id
            artifacts_dir.mkdir(parents=True, exist_ok=True)

            # Save optimized prompts
            if session.agent_profile.current_prompts:
                with open(artifacts_dir / "optimized_prompts.json", "w") as f:
                    json.dump(session.agent_profile.current_prompts, f, indent=2)

            # Save training data
            training_data = self.generate_training_data(session, "dpo")
            with open(artifacts_dir / "training_data_dpo.json", "w") as f:
                json.dump(training_data, f, indent=2)

            # Save final report
            with open(artifacts_dir / "final_report.json", "w") as f:
                json.dump(final_report, f, indent=2, default=str)

            final_report["artifacts_saved_to"] = str(artifacts_dir)

        # Remove from active sessions
        if session.session_id in self._active_sessions:
            del self._active_sessions[session.session_id]

        # Update saved session
        self.session_manager.save_session(session)

        logger.info(f"Ended training session {session.session_id}")

        return final_report

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active training sessions."""
        return [
            {
                "session_id": s.session_id,
                "agent_name": s.agent_profile.name,
                "mode": s.mode.value,
                "iterations": s.iterations_completed,
                "started_at": s.started_at
            }
            for s in self._active_sessions.values()
        ]

    def resume_session(self, session_id: str) -> Optional[TrainingSession]:
        """Resume a previously active session."""
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]

        # Try to load from storage
        session_data = self.session_manager.load_session(session_id)
        if session_data:
            session = self._deserialize_session(session_data)
            session.status = "active"
            self._active_sessions[session_id] = session
            return session

        return None


# Convenience functions for quick usage
def quick_evaluate(
    outputs: List[Dict[str, Any]],
    domain: str = "general"
) -> List[EvaluationResult]:
    """Quickly evaluate outputs without creating a full session."""
    trainer = PersonalTrainerAgent()
    profile = trainer.create_agent_profile(
        name="QuickEval",
        description="Quick evaluation",
        domain=domain,
        sample_outputs=outputs
    )
    session = trainer.start_training_session(profile, mode=TrainingMode.ANALYSIS_ONLY)
    results = trainer.evaluate_outputs(session, outputs)
    trainer.end_session(session, save_artifacts=False)
    return results


def quick_recommendations(
    prompts: Dict[str, str],
    domain: str = "general",
    known_issues: Optional[List[str]] = None
) -> List[TrainingRecommendation]:
    """Quickly get prompt improvement recommendations."""
    trainer = PersonalTrainerAgent()
    profile = trainer.create_agent_profile(
        name="QuickRec",
        description="Quick recommendations",
        domain=domain,
        current_prompts=prompts,
        known_weaknesses=known_issues or []
    )
    session = trainer.start_training_session(profile, mode=TrainingMode.PROMPT_OPTIMIZATION)
    recommendations = trainer.get_recommendations(session)
    trainer.end_session(session, save_artifacts=False)
    return recommendations
