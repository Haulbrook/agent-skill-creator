"""
OpenRL Trainer - Integration with OpenRL framework.

This module provides integration with OpenRL for flexible reinforcement
learning training with custom environments and reward functions.

Requires: pip install openrl
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class OpenRLConfig:
    """Configuration for OpenRL training."""
    # Algorithm settings
    algorithm: str = "ppo"  # ppo, a2c, dqn, sac
    policy_network: str = "mlp"  # mlp, cnn, transformer

    # Training settings
    learning_rate: float = 3e-4
    n_steps: int = 2048
    batch_size: int = 64
    n_epochs: int = 10
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_range: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5

    # Environment settings
    n_envs: int = 4
    max_episode_steps: int = 1000

    # Output settings
    output_dir: str = "./openrl_output"
    log_interval: int = 10
    save_freq: int = 1000
    eval_freq: int = 500
    eval_episodes: int = 10

    # Hardware
    device: str = "auto"


@dataclass
class OpenRLResult:
    """Result of OpenRL training."""
    success: bool
    algorithm: str
    model_path: Optional[str]
    metrics: Dict[str, float]
    training_config: Dict[str, Any]
    duration_seconds: float
    error: Optional[str] = None
    episode_rewards: List[float] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AgentEnvironment:
    """
    Custom environment wrapper for agent training.

    Wraps agent interactions as an RL environment where:
    - Observations: Current state/context
    - Actions: Agent outputs/decisions
    - Rewards: Quality scores from evaluation
    """

    def __init__(
        self,
        agent_profile: Any,
        reward_function: Callable,
        max_steps: int = 100
    ):
        """
        Initialize the agent environment.

        Args:
            agent_profile: Profile of the agent being trained
            reward_function: Function that computes rewards for agent outputs
            max_steps: Maximum steps per episode
        """
        self.agent_profile = agent_profile
        self.reward_function = reward_function
        self.max_steps = max_steps
        self.current_step = 0
        self.current_context = None

        # Action and observation space dimensions
        self.observation_dim = 768  # Typical embedding dimension
        self.action_dim = 512  # Action representation dimension

    def reset(self) -> Dict[str, Any]:
        """Reset the environment for a new episode."""
        self.current_step = 0
        self.current_context = self._sample_context()
        return {
            "observation": self._get_observation(),
            "info": {"context": self.current_context}
        }

    def step(self, action: Any) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Take a step in the environment.

        Args:
            action: The action (agent output) to take

        Returns:
            Tuple of (observation, reward, done, info)
        """
        self.current_step += 1

        # Compute reward using the provided function
        reward = self.reward_function(self.current_context, action)

        # Check if episode is done
        done = self.current_step >= self.max_steps

        # Update context
        self.current_context = self._update_context(action)

        return (
            {"observation": self._get_observation()},
            reward,
            done,
            {"step": self.current_step, "context": self.current_context}
        )

    def _sample_context(self) -> Dict[str, Any]:
        """Sample a new context/prompt."""
        # In practice, this would sample from training data
        return {
            "type": "prompt",
            "content": "Sample context for training",
            "domain": self.agent_profile.domain
        }

    def _get_observation(self) -> List[float]:
        """Get current observation vector."""
        # In practice, this would be an embedding of the current context
        return [0.0] * self.observation_dim

    def _update_context(self, action: Any) -> Dict[str, Any]:
        """Update context based on action taken."""
        return self._sample_context()


class OpenRLTrainer:
    """
    Trainer using OpenRL framework.

    OpenRL provides flexible RL training with:
    - Multiple algorithms (PPO, A2C, DQN, SAC)
    - Custom environments
    - Distributed training support
    - Extensive logging and evaluation

    Usage:
        trainer = OpenRLTrainer()

        def reward_fn(context, output):
            # Your reward logic
            return score

        result = trainer.train(
            agent_profile,
            env_config={"max_steps": 100},
            reward_function=reward_fn
        )
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OpenRL trainer.

        Args:
            config: Optional configuration overrides
        """
        self.config = OpenRLConfig()
        if config:
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

        self._openrl_available = self._check_dependencies()

    def _check_dependencies(self) -> bool:
        """Check if OpenRL and dependencies are available."""
        try:
            import numpy as np
            self._np = np

            try:
                import openrl
                self._openrl = openrl
                return True
            except ImportError:
                logger.warning("OpenRL not installed. Install with: pip install openrl")
                return False

        except ImportError as e:
            logger.error(f"Required dependencies not available: {e}")
            return False

    def train(
        self,
        agent_profile: Any,
        environment_config: Dict[str, Any],
        reward_function: Callable,
        config: Optional[Dict[str, Any]] = None
    ) -> OpenRLResult:
        """
        Train agent using OpenRL.

        Args:
            agent_profile: Profile of the agent being trained
            environment_config: Configuration for the RL environment
            reward_function: Function computing rewards for outputs
            config: Optional training configuration overrides

        Returns:
            OpenRLResult with training outcomes
        """
        start_time = datetime.now()

        # Even without OpenRL, we can provide a simulation/fallback
        if not self._openrl_available:
            return self._simulate_training(
                agent_profile, environment_config, reward_function, config
            )

        try:
            train_config = self._merge_config(config)

            # Create environment
            env = AgentEnvironment(
                agent_profile,
                reward_function,
                max_steps=environment_config.get("max_steps", train_config.max_episode_steps)
            )

            # Create algorithm
            if train_config.algorithm == "ppo":
                from openrl.algorithms import PPO
                algorithm = PPO(
                    policy=train_config.policy_network,
                    learning_rate=train_config.learning_rate,
                    n_steps=train_config.n_steps,
                    batch_size=train_config.batch_size,
                    n_epochs=train_config.n_epochs,
                    gamma=train_config.gamma,
                    gae_lambda=train_config.gae_lambda,
                    clip_range=train_config.clip_range,
                    ent_coef=train_config.ent_coef,
                    vf_coef=train_config.vf_coef,
                    max_grad_norm=train_config.max_grad_norm,
                    device=train_config.device
                )
            else:
                raise ValueError(f"Unsupported algorithm: {train_config.algorithm}")

            # Training loop
            logger.info(f"Starting OpenRL training with {train_config.algorithm}...")
            episode_rewards = []
            total_steps = 0
            n_episodes = 100  # Default number of training episodes

            for episode in range(n_episodes):
                obs = env.reset()
                episode_reward = 0
                done = False

                while not done:
                    action = algorithm.predict(obs["observation"])
                    obs, reward, done, info = env.step(action)
                    episode_reward += reward
                    total_steps += 1

                    # Update algorithm
                    algorithm.learn(total_timesteps=1)

                episode_rewards.append(episode_reward)

                if episode % train_config.log_interval == 0:
                    avg_reward = sum(episode_rewards[-10:]) / min(10, len(episode_rewards))
                    logger.info(f"Episode {episode}, Avg Reward: {avg_reward:.4f}")

                if episode % train_config.save_freq == 0:
                    save_path = Path(train_config.output_dir) / f"checkpoint_{episode}"
                    algorithm.save(str(save_path))

            # Save final model
            output_path = Path(train_config.output_dir) / "final_model"
            output_path.mkdir(parents=True, exist_ok=True)
            algorithm.save(str(output_path))

            duration = (datetime.now() - start_time).total_seconds()

            return OpenRLResult(
                success=True,
                algorithm=train_config.algorithm,
                model_path=str(output_path),
                metrics={
                    "final_avg_reward": sum(episode_rewards[-10:]) / min(10, len(episode_rewards)),
                    "max_reward": max(episode_rewards),
                    "total_episodes": len(episode_rewards),
                    "total_steps": total_steps
                },
                training_config=vars(train_config),
                duration_seconds=duration,
                episode_rewards=episode_rewards
            )

        except Exception as e:
            logger.error(f"OpenRL training failed: {e}")
            duration = (datetime.now() - start_time).total_seconds()
            return OpenRLResult(
                success=False,
                algorithm=self.config.algorithm,
                model_path=None,
                metrics={},
                training_config=vars(self.config),
                duration_seconds=duration,
                error=str(e)
            )

    def _simulate_training(
        self,
        agent_profile: Any,
        environment_config: Dict[str, Any],
        reward_function: Callable,
        config: Optional[Dict[str, Any]]
    ) -> OpenRLResult:
        """
        Simulate training when OpenRL is not available.

        This provides useful feedback about what training would look like
        and validates the configuration.
        """
        start_time = datetime.now()
        train_config = self._merge_config(config)

        logger.info("OpenRL not available - running simulation...")

        # Create environment for validation
        env = AgentEnvironment(
            agent_profile,
            reward_function,
            max_steps=environment_config.get("max_steps", 10)
        )

        # Simulate some episodes to validate reward function
        episode_rewards = []
        for episode in range(5):
            obs = env.reset()
            episode_reward = 0

            for step in range(10):
                # Random action for simulation
                action = {"output": f"Simulated output {step}"}
                obs, reward, done, info = env.step(action)
                episode_reward += reward
                if done:
                    break

            episode_rewards.append(episode_reward)

        duration = (datetime.now() - start_time).total_seconds()

        return OpenRLResult(
            success=True,
            algorithm=f"{train_config.algorithm} (simulated)",
            model_path=None,
            metrics={
                "simulated_avg_reward": sum(episode_rewards) / len(episode_rewards),
                "episodes_simulated": len(episode_rewards),
                "note": "OpenRL not installed - results are simulated"
            },
            training_config=vars(train_config),
            duration_seconds=duration,
            episode_rewards=episode_rewards,
            error="OpenRL not installed. Install with: pip install openrl for actual training."
        )

    def _merge_config(self, overrides: Optional[Dict[str, Any]]) -> OpenRLConfig:
        """Merge configuration overrides."""
        config = OpenRLConfig()
        for key, value in vars(self.config).items():
            setattr(config, key, value)

        if overrides:
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        return config

    def create_reward_function(
        self,
        rubric: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Callable:
        """
        Create a reward function from an evaluation rubric.

        Args:
            rubric: Evaluation rubric with criteria
            weights: Optional weights for different criteria

        Returns:
            Reward function that can be used for training
        """
        default_weights = {
            "quality": 0.3,
            "relevance": 0.25,
            "completeness": 0.25,
            "efficiency": 0.2
        }
        weights = weights or default_weights

        def reward_function(context: Dict[str, Any], output: Any) -> float:
            """Compute reward based on rubric evaluation."""
            total_reward = 0.0

            # Extract output content
            if isinstance(output, dict):
                content = output.get("output", str(output))
            else:
                content = str(output)

            # Quality: Check for positive indicators
            quality_score = 0.5  # Baseline
            if len(content) > 50:  # Non-trivial response
                quality_score += 0.2
            if "\n" in content:  # Structured
                quality_score += 0.15
            if any(word in content.lower() for word in ["because", "therefore", "specifically"]):
                quality_score += 0.15
            total_reward += quality_score * weights.get("quality", 0.3)

            # Relevance: Check if output relates to context
            context_content = context.get("content", "")
            context_words = set(context_content.lower().split())
            output_words = set(content.lower().split())
            overlap = len(context_words & output_words)
            relevance_score = min(1.0, overlap / max(len(context_words), 1) * 2)
            total_reward += relevance_score * weights.get("relevance", 0.25)

            # Completeness: Check for thorough response
            completeness_score = min(1.0, len(content) / 500)  # Up to 500 chars
            total_reward += completeness_score * weights.get("completeness", 0.25)

            # Efficiency: Penalize very long responses
            efficiency_score = 1.0 - max(0, (len(content) - 1000) / 2000)
            efficiency_score = max(0.2, efficiency_score)
            total_reward += efficiency_score * weights.get("efficiency", 0.2)

            return total_reward

        return reward_function

    def generate_training_config(
        self,
        agent_profile: Any,
        difficulty: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Generate recommended training configuration.

        Args:
            agent_profile: Profile of the agent
            difficulty: Training difficulty (easy, moderate, hard)

        Returns:
            Recommended configuration dictionary
        """
        base_config = {
            "algorithm": "ppo",
            "learning_rate": 3e-4,
            "n_steps": 2048,
            "batch_size": 64,
            "n_epochs": 10,
            "gamma": 0.99
        }

        difficulty_adjustments = {
            "easy": {
                "learning_rate": 1e-3,
                "n_epochs": 5,
                "clip_range": 0.3
            },
            "moderate": {
                "learning_rate": 3e-4,
                "n_epochs": 10,
                "clip_range": 0.2
            },
            "hard": {
                "learning_rate": 1e-4,
                "n_epochs": 20,
                "clip_range": 0.1
            }
        }

        config = {**base_config, **difficulty_adjustments.get(difficulty, {})}

        # Domain-specific adjustments
        domain = agent_profile.domain if hasattr(agent_profile, 'domain') else "general"
        if domain == "coding":
            config["n_steps"] = 4096  # Longer episodes for code generation
            config["max_episode_steps"] = 200
        elif domain == "marketing":
            config["ent_coef"] = 0.02  # More exploration for creative tasks
        elif domain == "website_building":
            config["n_steps"] = 4096
            config["max_episode_steps"] = 150

        return config
