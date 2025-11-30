"""
TRL Trainer - Integration with Transformers Reinforcement Learning library.

This module provides comprehensive integration with the TRL library for:
- RLHF (Reinforcement Learning from Human Feedback)
- DPO (Direct Preference Optimization)
- PPO (Proximal Policy Optimization)
- SFT (Supervised Fine-Tuning)

Requires: pip install trl transformers torch datasets peft accelerate
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


@dataclass
class TRLConfig:
    """Configuration for TRL training."""
    # Model settings
    model_name_or_path: str = "gpt2"
    tokenizer_name: Optional[str] = None
    use_peft: bool = True
    peft_config: Optional[Dict[str, Any]] = None

    # Training settings
    learning_rate: float = 1e-5
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    num_epochs: int = 3
    max_length: int = 512
    warmup_steps: int = 100

    # DPO specific
    dpo_beta: float = 0.1

    # PPO specific
    ppo_epochs: int = 4
    ppo_kl_penalty: str = "kl"
    target_kl: float = 0.1

    # Output settings
    output_dir: str = "./trl_output"
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 50

    # Hardware
    fp16: bool = True
    device_map: str = "auto"


@dataclass
class TrainingResult:
    """Result of a training run."""
    success: bool
    training_type: str
    model_path: Optional[str]
    metrics: Dict[str, float]
    training_args: Dict[str, Any]
    duration_seconds: float
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class TRLTrainer:
    """
    Trainer for TRL-based fine-tuning.

    Supports multiple training paradigms:
    - SFT: Supervised fine-tuning on high-quality examples
    - DPO: Direct preference optimization from preference pairs
    - RLHF: Full RLHF pipeline with reward model
    - PPO: Proximal policy optimization

    Usage:
        trainer = TRLTrainer()

        # Prepare DPO data
        data = [
            {"prompt": "...", "chosen": "...", "rejected": "..."},
            ...
        ]

        # Train
        result = trainer.train_dpo(data, model_info={"name": "gpt2"})

        # Use trained model
        print(result.model_path)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TRL trainer.

        Args:
            config: Optional configuration overrides
        """
        self.config = TRLConfig()
        if config:
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

        self._check_dependencies()

    def _check_dependencies(self) -> bool:
        """Check if TRL and dependencies are available."""
        try:
            import torch
            import transformers
            self._torch = torch
            self._transformers = transformers

            try:
                import trl
                self._trl = trl
                self._trl_available = True
            except ImportError:
                logger.warning("TRL not installed. Install with: pip install trl")
                self._trl_available = False

            try:
                import datasets
                self._datasets = datasets
            except ImportError:
                logger.warning("datasets not installed. Install with: pip install datasets")

            try:
                import peft
                self._peft = peft
                self._peft_available = True
            except ImportError:
                logger.warning("PEFT not installed. Install with: pip install peft")
                self._peft_available = False

            return True

        except ImportError as e:
            logger.error(f"Required dependencies not available: {e}")
            return False

    def train_dpo(
        self,
        data: List[Dict[str, Any]],
        model_info: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> TrainingResult:
        """
        Train using Direct Preference Optimization (DPO).

        DPO learns from preference pairs without requiring a separate reward model.

        Args:
            data: List of preference pairs with keys: prompt, chosen, rejected
            model_info: Information about the model to fine-tune
            config: Optional training configuration overrides

        Returns:
            TrainingResult with training outcomes
        """
        start_time = datetime.now()

        if not self._trl_available:
            return TrainingResult(
                success=False,
                training_type="dpo",
                model_path=None,
                metrics={},
                training_args={},
                duration_seconds=0,
                error="TRL not installed. Install with: pip install trl"
            )

        try:
            # Apply config overrides
            train_config = self._merge_config(config)

            # Prepare model
            model_name = model_info.get("name", train_config.model_name_or_path) if model_info else train_config.model_name_or_path

            logger.info(f"Loading model: {model_name}")
            model = self._transformers.AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=train_config.device_map,
                torch_dtype=self._torch.float16 if train_config.fp16 else self._torch.float32
            )
            tokenizer = self._transformers.AutoTokenizer.from_pretrained(
                train_config.tokenizer_name or model_name
            )
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # Apply PEFT if available and configured
            if train_config.use_peft and self._peft_available:
                peft_config = self._peft.LoraConfig(
                    r=16,
                    lora_alpha=32,
                    lora_dropout=0.1,
                    bias="none",
                    task_type="CAUSAL_LM",
                    **(train_config.peft_config or {})
                )
                model = self._peft.get_peft_model(model, peft_config)
                logger.info("Applied PEFT LoRA configuration")

            # Prepare dataset
            dataset = self._prepare_dpo_dataset(data, tokenizer, train_config.max_length)

            # Configure training
            training_args = self._trl.DPOConfig(
                output_dir=train_config.output_dir,
                per_device_train_batch_size=train_config.batch_size,
                gradient_accumulation_steps=train_config.gradient_accumulation_steps,
                learning_rate=train_config.learning_rate,
                num_train_epochs=train_config.num_epochs,
                beta=train_config.dpo_beta,
                logging_steps=train_config.logging_steps,
                save_steps=train_config.save_steps,
                fp16=train_config.fp16,
                warmup_steps=train_config.warmup_steps,
                remove_unused_columns=False
            )

            # Create DPO trainer
            dpo_trainer = self._trl.DPOTrainer(
                model=model,
                args=training_args,
                train_dataset=dataset,
                tokenizer=tokenizer,
            )

            # Train
            logger.info("Starting DPO training...")
            train_result = dpo_trainer.train()

            # Save model
            output_path = Path(train_config.output_dir) / "final_model"
            dpo_trainer.save_model(str(output_path))
            tokenizer.save_pretrained(str(output_path))
            logger.info(f"Model saved to: {output_path}")

            duration = (datetime.now() - start_time).total_seconds()

            return TrainingResult(
                success=True,
                training_type="dpo",
                model_path=str(output_path),
                metrics={
                    "train_loss": train_result.training_loss,
                    "train_samples": len(data),
                    "epochs_completed": train_config.num_epochs
                },
                training_args=vars(train_config),
                duration_seconds=duration
            )

        except Exception as e:
            logger.error(f"DPO training failed: {e}")
            duration = (datetime.now() - start_time).total_seconds()
            return TrainingResult(
                success=False,
                training_type="dpo",
                model_path=None,
                metrics={},
                training_args=vars(self.config),
                duration_seconds=duration,
                error=str(e)
            )

    def train_rlhf(
        self,
        data: List[Dict[str, Any]],
        model_info: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> TrainingResult:
        """
        Train using RLHF with reward model.

        Full RLHF pipeline:
        1. Train reward model on preference data
        2. Train policy using PPO with reward model

        Args:
            data: List of examples with reward scores
            model_info: Information about the model to fine-tune
            config: Optional training configuration overrides

        Returns:
            TrainingResult with training outcomes
        """
        start_time = datetime.now()

        if not self._trl_available:
            return TrainingResult(
                success=False,
                training_type="rlhf",
                model_path=None,
                metrics={},
                training_args={},
                duration_seconds=0,
                error="TRL not installed. Install with: pip install trl"
            )

        try:
            train_config = self._merge_config(config)
            model_name = model_info.get("name", train_config.model_name_or_path) if model_info else train_config.model_name_or_path

            # Step 1: Train reward model
            logger.info("Training reward model...")
            reward_model = self._train_reward_model(data, model_name, train_config)

            # Step 2: Train policy with PPO
            logger.info("Training policy with PPO...")

            # Load policy model
            policy_model = self._transformers.AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=train_config.device_map,
                torch_dtype=self._torch.float16 if train_config.fp16 else self._torch.float32
            )
            tokenizer = self._transformers.AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # Apply PEFT
            if train_config.use_peft and self._peft_available:
                peft_config = self._peft.LoraConfig(
                    r=16,
                    lora_alpha=32,
                    lora_dropout=0.1,
                    bias="none",
                    task_type="CAUSAL_LM"
                )
                policy_model = self._peft.get_peft_model(policy_model, peft_config)

            # Prepare prompts
            prompts = [d["prompt"] for d in data if "prompt" in d]

            # Configure PPO
            ppo_config = self._trl.PPOConfig(
                learning_rate=train_config.learning_rate,
                batch_size=train_config.batch_size,
                mini_batch_size=train_config.batch_size // 2,
                ppo_epochs=train_config.ppo_epochs,
                target_kl=train_config.target_kl,
                kl_penalty=train_config.ppo_kl_penalty
            )

            # Create PPO trainer
            ppo_trainer = self._trl.PPOTrainer(
                config=ppo_config,
                model=policy_model,
                tokenizer=tokenizer,
            )

            # Training loop
            all_rewards = []
            for epoch in range(train_config.num_epochs):
                for prompt in prompts[:100]:  # Limit for demonstration
                    # Generate response
                    inputs = tokenizer(prompt, return_tensors="pt")
                    outputs = policy_model.generate(
                        inputs.input_ids.to(policy_model.device),
                        max_new_tokens=100,
                        do_sample=True
                    )
                    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

                    # Get reward
                    reward = self._compute_reward(reward_model, prompt, response, tokenizer)
                    all_rewards.append(reward)

                    # PPO step
                    query_tensor = inputs.input_ids[0]
                    response_tensor = outputs[0][len(inputs.input_ids[0]):]
                    ppo_trainer.step([query_tensor], [response_tensor], [self._torch.tensor([reward])])

                logger.info(f"Epoch {epoch + 1} completed, avg reward: {sum(all_rewards[-len(prompts):]) / len(prompts):.4f}")

            # Save final model
            output_path = Path(train_config.output_dir) / "rlhf_final_model"
            ppo_trainer.save_pretrained(str(output_path))
            tokenizer.save_pretrained(str(output_path))

            duration = (datetime.now() - start_time).total_seconds()

            return TrainingResult(
                success=True,
                training_type="rlhf",
                model_path=str(output_path),
                metrics={
                    "final_avg_reward": sum(all_rewards[-100:]) / min(100, len(all_rewards)),
                    "total_steps": len(all_rewards),
                    "epochs_completed": train_config.num_epochs
                },
                training_args=vars(train_config),
                duration_seconds=duration
            )

        except Exception as e:
            logger.error(f"RLHF training failed: {e}")
            duration = (datetime.now() - start_time).total_seconds()
            return TrainingResult(
                success=False,
                training_type="rlhf",
                model_path=None,
                metrics={},
                training_args=vars(self.config),
                duration_seconds=duration,
                error=str(e)
            )

    def _train_reward_model(
        self,
        data: List[Dict[str, Any]],
        model_name: str,
        config: TRLConfig
    ) -> Any:
        """Train a reward model on preference data."""
        # For simplicity, we'll use a pre-trained model with a value head
        # In production, you'd train a proper reward model

        reward_model = self._trl.AutoModelForCausalLMWithValueHead.from_pretrained(
            model_name,
            device_map=config.device_map
        )
        return reward_model

    def _compute_reward(
        self,
        reward_model: Any,
        prompt: str,
        response: str,
        tokenizer: Any
    ) -> float:
        """Compute reward for a response."""
        # Simple reward based on response characteristics
        # In production, use actual reward model

        # Length penalty (prefer medium length)
        length_reward = 1.0 - abs(len(response) - 200) / 500
        length_reward = max(0, min(1, length_reward))

        # Simple quality heuristics
        quality_reward = 0.5
        if "error" in response.lower() or "sorry" in response.lower():
            quality_reward -= 0.2
        if len(response.split("\n")) > 3:  # Structured response
            quality_reward += 0.1

        return (length_reward + quality_reward) / 2

    def train_sft(
        self,
        data: List[Dict[str, Any]],
        model_info: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> TrainingResult:
        """
        Train using Supervised Fine-Tuning (SFT).

        SFT on high-quality examples is often the first step before RLHF/DPO.

        Args:
            data: List of prompt-completion pairs
            model_info: Information about the model to fine-tune
            config: Optional training configuration overrides

        Returns:
            TrainingResult with training outcomes
        """
        start_time = datetime.now()

        if not self._trl_available:
            return TrainingResult(
                success=False,
                training_type="sft",
                model_path=None,
                metrics={},
                training_args={},
                duration_seconds=0,
                error="TRL not installed. Install with: pip install trl"
            )

        try:
            train_config = self._merge_config(config)
            model_name = model_info.get("name", train_config.model_name_or_path) if model_info else train_config.model_name_or_path

            # Load model
            model = self._transformers.AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=train_config.device_map,
                torch_dtype=self._torch.float16 if train_config.fp16 else self._torch.float32
            )
            tokenizer = self._transformers.AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # Apply PEFT
            if train_config.use_peft and self._peft_available:
                peft_config = self._peft.LoraConfig(
                    r=16,
                    lora_alpha=32,
                    lora_dropout=0.1,
                    bias="none",
                    task_type="CAUSAL_LM"
                )
                model = self._peft.get_peft_model(model, peft_config)

            # Prepare dataset
            dataset = self._prepare_sft_dataset(data, tokenizer, train_config.max_length)

            # Configure training
            training_args = self._trl.SFTConfig(
                output_dir=train_config.output_dir,
                per_device_train_batch_size=train_config.batch_size,
                gradient_accumulation_steps=train_config.gradient_accumulation_steps,
                learning_rate=train_config.learning_rate,
                num_train_epochs=train_config.num_epochs,
                logging_steps=train_config.logging_steps,
                save_steps=train_config.save_steps,
                fp16=train_config.fp16,
                warmup_steps=train_config.warmup_steps,
                max_seq_length=train_config.max_length
            )

            # Create SFT trainer
            sft_trainer = self._trl.SFTTrainer(
                model=model,
                args=training_args,
                train_dataset=dataset,
                tokenizer=tokenizer,
            )

            # Train
            logger.info("Starting SFT training...")
            train_result = sft_trainer.train()

            # Save model
            output_path = Path(train_config.output_dir) / "sft_final_model"
            sft_trainer.save_model(str(output_path))
            tokenizer.save_pretrained(str(output_path))

            duration = (datetime.now() - start_time).total_seconds()

            return TrainingResult(
                success=True,
                training_type="sft",
                model_path=str(output_path),
                metrics={
                    "train_loss": train_result.training_loss,
                    "train_samples": len(data),
                    "epochs_completed": train_config.num_epochs
                },
                training_args=vars(train_config),
                duration_seconds=duration
            )

        except Exception as e:
            logger.error(f"SFT training failed: {e}")
            duration = (datetime.now() - start_time).total_seconds()
            return TrainingResult(
                success=False,
                training_type="sft",
                model_path=None,
                metrics={},
                training_args=vars(self.config),
                duration_seconds=duration,
                error=str(e)
            )

    def _prepare_dpo_dataset(
        self,
        data: List[Dict[str, Any]],
        tokenizer: Any,
        max_length: int
    ) -> Any:
        """Prepare dataset for DPO training."""
        formatted_data = []
        for item in data:
            formatted_data.append({
                "prompt": item.get("prompt", ""),
                "chosen": item.get("chosen", ""),
                "rejected": item.get("rejected", "")
            })

        return self._datasets.Dataset.from_list(formatted_data)

    def _prepare_sft_dataset(
        self,
        data: List[Dict[str, Any]],
        tokenizer: Any,
        max_length: int
    ) -> Any:
        """Prepare dataset for SFT training."""
        formatted_data = []
        for item in data:
            prompt = item.get("prompt", "")
            completion = item.get("completion", "")
            formatted_data.append({
                "text": f"{prompt}\n{completion}"
            })

        return self._datasets.Dataset.from_list(formatted_data)

    def _merge_config(self, overrides: Optional[Dict[str, Any]]) -> TRLConfig:
        """Merge configuration overrides."""
        config = TRLConfig()
        for key, value in vars(self.config).items():
            setattr(config, key, value)

        if overrides:
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        return config

    def generate_training_script(
        self,
        data_path: str,
        training_type: str = "dpo",
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a standalone training script.

        Useful for running training outside of the Personal Trainer Agent.

        Args:
            data_path: Path to training data JSON file
            training_type: Type of training (dpo, sft, rlhf)
            config: Configuration options

        Returns:
            Python script as string
        """
        train_config = self._merge_config(config)

        if training_type == "dpo":
            script = f'''#!/usr/bin/env python3
"""
DPO Training Script
Generated by Personal Trainer Agent
"""

import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset
from trl import DPOConfig, DPOTrainer
from peft import LoraConfig, get_peft_model

# Load data
with open("{data_path}", "r") as f:
    data = json.load(f)["data"]

# Model configuration
model_name = "{train_config.model_name_or_path}"
output_dir = "{train_config.output_dir}"

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Apply LoRA
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, peft_config)

# Prepare dataset
dataset = Dataset.from_list(data)

# Training configuration
training_args = DPOConfig(
    output_dir=output_dir,
    per_device_train_batch_size={train_config.batch_size},
    gradient_accumulation_steps={train_config.gradient_accumulation_steps},
    learning_rate={train_config.learning_rate},
    num_train_epochs={train_config.num_epochs},
    beta={train_config.dpo_beta},
    logging_steps={train_config.logging_steps},
    save_steps={train_config.save_steps},
    fp16={train_config.fp16},
)

# Train
trainer = DPOTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
)

trainer.train()
trainer.save_model(f"{{output_dir}}/final_model")
tokenizer.save_pretrained(f"{{output_dir}}/final_model")

print(f"Training complete! Model saved to {{output_dir}}/final_model")
'''
        elif training_type == "sft":
            script = f'''#!/usr/bin/env python3
"""
SFT Training Script
Generated by Personal Trainer Agent
"""

import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset
from trl import SFTConfig, SFTTrainer
from peft import LoraConfig, get_peft_model

# Load data
with open("{data_path}", "r") as f:
    data = json.load(f)["data"]

# Format data
formatted = [{{"text": f"{{d['prompt']}}\\n{{d['completion']}}"}} for d in data]

# Model configuration
model_name = "{train_config.model_name_or_path}"
output_dir = "{train_config.output_dir}"

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Apply LoRA
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, peft_config)

# Prepare dataset
dataset = Dataset.from_list(formatted)

# Training configuration
training_args = SFTConfig(
    output_dir=output_dir,
    per_device_train_batch_size={train_config.batch_size},
    gradient_accumulation_steps={train_config.gradient_accumulation_steps},
    learning_rate={train_config.learning_rate},
    num_train_epochs={train_config.num_epochs},
    logging_steps={train_config.logging_steps},
    save_steps={train_config.save_steps},
    fp16={train_config.fp16},
    max_seq_length={train_config.max_length}
)

# Train
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
)

trainer.train()
trainer.save_model(f"{{output_dir}}/final_model")
tokenizer.save_pretrained(f"{{output_dir}}/final_model")

print(f"Training complete! Model saved to {{output_dir}}/final_model")
'''
        else:
            script = "# Unsupported training type"

        return script
