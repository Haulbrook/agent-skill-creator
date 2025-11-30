"""
Prompt optimization for improving agent performance.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Callable
import json
import re


@dataclass
class OptimizationConfig:
    """Configuration for prompt optimization."""

    max_iterations: int = 10
    population_size: int = 5
    mutation_rate: float = 0.3
    crossover_rate: float = 0.5
    elite_count: int = 2
    improvement_threshold: float = 0.05


@dataclass
class PromptCandidate:
    """A candidate prompt being optimized."""

    prompt: str
    score: float = 0.0
    generation: int = 0
    parent_ids: list[str] = field(default_factory=list)
    mutations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "score": self.score,
            "generation": self.generation,
            "parent_ids": self.parent_ids,
            "mutations": self.mutations,
        }


class PromptOptimizer:
    """
    Optimizes prompts to improve agent performance.

    Techniques:
    - Evolutionary optimization (mutation + crossover)
    - Gradient-free optimization
    - Template-based refinement
    - Few-shot example selection

    Example:
        ```python
        optimizer = PromptOptimizer()

        result = optimizer.optimize(
            plan={"improvements": [...]},
            examples=[{"input": "...", "expected": "..."}, ...],
        )

        print(result["optimized_prompt"])
        ```
    """

    def __init__(
        self,
        config: Optional[OptimizationConfig] = None,
        llm_client: Optional[Any] = None,
    ) -> None:
        """
        Initialize the prompt optimizer.

        Args:
            config: Optimization configuration
            llm_client: LLM client for evaluation (optional)
        """
        self.config = config or OptimizationConfig()
        self.llm_client = llm_client
        self.history: list[PromptCandidate] = []

    def optimize(
        self,
        plan: dict[str, Any],
        examples: Optional[list[dict[str, Any]]] = None,
        base_prompt: Optional[str] = None,
        evaluator: Optional[Callable[[str, list[dict]], float]] = None,
    ) -> dict[str, Any]:
        """
        Optimize a prompt based on the improvement plan.

        Args:
            plan: Improvement plan with objectives
            examples: Training examples for evaluation
            base_prompt: Starting prompt to optimize
            evaluator: Custom evaluation function

        Returns:
            Optimization results with best prompt
        """
        # Initialize base prompt
        if base_prompt is None:
            base_prompt = self._generate_base_prompt(plan)

        # Initialize population
        population = self._initialize_population(base_prompt)

        # Evaluate initial population
        eval_func = evaluator or self._default_evaluator
        for candidate in population:
            candidate.score = eval_func(candidate.prompt, examples or [])

        # Track best
        best_candidate = max(population, key=lambda c: c.score)
        initial_score = best_candidate.score
        self.history.append(best_candidate)

        # Evolution loop
        for generation in range(self.config.max_iterations):
            # Select parents
            parents = self._select_parents(population)

            # Generate offspring
            offspring = self._generate_offspring(parents, generation + 1)

            # Evaluate offspring
            for candidate in offspring:
                candidate.score = eval_func(candidate.prompt, examples or [])

            # Select next generation
            population = self._select_survivors(population + offspring)

            # Update best
            current_best = max(population, key=lambda c: c.score)
            if current_best.score > best_candidate.score:
                best_candidate = current_best
                self.history.append(best_candidate)

            # Check for convergence
            if self._check_convergence(population):
                break

        # Compute improvement
        improvement = best_candidate.score - initial_score

        return {
            "status": "completed",
            "optimized_prompt": best_candidate.prompt,
            "before": {"score": initial_score},
            "after": {"score": best_candidate.score},
            "improvement": improvement,
            "generations": generation + 1,
            "candidates_evaluated": len(self.history),
            "history": [c.to_dict() for c in self.history[-5:]],
        }

    def _generate_base_prompt(self, plan: dict[str, Any]) -> str:
        """Generate a base prompt from the improvement plan."""
        improvements = plan.get("improvements", [])

        prompt_parts = [
            "You are a helpful AI assistant.",
            "",
            "Guidelines:",
        ]

        for imp in improvements[:5]:  # Top 5 improvements
            action = imp.get("action", "")
            if action:
                prompt_parts.append(f"- {action}")

        prompt_parts.extend([
            "",
            "Respond clearly and helpfully to the user's request.",
        ])

        return "\n".join(prompt_parts)

    def _initialize_population(self, base_prompt: str) -> list[PromptCandidate]:
        """Initialize the population with variations of the base prompt."""
        population = [
            PromptCandidate(prompt=base_prompt, generation=0)
        ]

        # Generate variations
        for i in range(self.config.population_size - 1):
            variant = self._mutate_prompt(base_prompt, strength=0.3)
            population.append(
                PromptCandidate(
                    prompt=variant,
                    generation=0,
                    mutations=[f"initial_variation_{i}"],
                )
            )

        return population

    def _select_parents(
        self,
        population: list[PromptCandidate],
    ) -> list[PromptCandidate]:
        """Select parents for reproduction using tournament selection."""
        import random

        parents = []
        num_parents = max(2, len(population) // 2)

        for _ in range(num_parents):
            # Tournament selection
            tournament = random.sample(population, min(3, len(population)))
            winner = max(tournament, key=lambda c: c.score)
            parents.append(winner)

        return parents

    def _generate_offspring(
        self,
        parents: list[PromptCandidate],
        generation: int,
    ) -> list[PromptCandidate]:
        """Generate offspring through crossover and mutation."""
        import random

        offspring = []

        for i in range(self.config.population_size):
            if len(parents) >= 2 and random.random() < self.config.crossover_rate:
                # Crossover
                p1, p2 = random.sample(parents, 2)
                child_prompt = self._crossover(p1.prompt, p2.prompt)
                mutations = ["crossover"]
            else:
                # Clone and mutate
                parent = random.choice(parents)
                child_prompt = parent.prompt
                mutations = []

            # Apply mutation
            if random.random() < self.config.mutation_rate:
                child_prompt = self._mutate_prompt(child_prompt)
                mutations.append("mutation")

            offspring.append(
                PromptCandidate(
                    prompt=child_prompt,
                    generation=generation,
                    mutations=mutations,
                )
            )

        return offspring

    def _crossover(self, prompt1: str, prompt2: str) -> str:
        """Perform crossover between two prompts."""
        lines1 = prompt1.split("\n")
        lines2 = prompt2.split("\n")

        # Simple line-based crossover
        result = []
        max_lines = max(len(lines1), len(lines2))

        for i in range(max_lines):
            if i < len(lines1) and i < len(lines2):
                # Randomly choose from either parent
                import random
                result.append(random.choice([lines1[i], lines2[i]]))
            elif i < len(lines1):
                result.append(lines1[i])
            else:
                result.append(lines2[i])

        return "\n".join(result)

    def _mutate_prompt(self, prompt: str, strength: float = 0.2) -> str:
        """Apply mutation to a prompt."""
        import random

        mutations = [
            self._add_emphasis,
            self._rephrase_instruction,
            self._add_example_indicator,
            self._add_constraint,
            self._simplify,
        ]

        # Apply random mutation
        mutation = random.choice(mutations)
        return mutation(prompt)

    def _add_emphasis(self, prompt: str) -> str:
        """Add emphasis to key instructions."""
        emphasis_words = ["Important:", "Note:", "Key point:", "Remember:"]
        import random

        lines = prompt.split("\n")
        if lines:
            idx = random.randint(0, len(lines) - 1)
            if lines[idx].strip() and not any(e in lines[idx] for e in emphasis_words):
                lines[idx] = f"{random.choice(emphasis_words)} {lines[idx]}"

        return "\n".join(lines)

    def _rephrase_instruction(self, prompt: str) -> str:
        """Rephrase an instruction."""
        replacements = [
            ("You should", "Please"),
            ("Make sure to", "Ensure you"),
            ("Don't", "Avoid"),
            ("Always", "Consistently"),
            ("helpful", "useful and informative"),
        ]

        import random
        if replacements:
            old, new = random.choice(replacements)
            return prompt.replace(old, new, 1)
        return prompt

    def _add_example_indicator(self, prompt: str) -> str:
        """Add indicator for examples."""
        if "example" not in prompt.lower():
            return prompt + "\n\nProvide examples where helpful."
        return prompt

    def _add_constraint(self, prompt: str) -> str:
        """Add a quality constraint."""
        constraints = [
            "Be concise and direct.",
            "Structure your response clearly.",
            "Focus on the most important points.",
            "Verify accuracy before responding.",
        ]

        import random
        constraint = random.choice(constraints)
        if constraint not in prompt:
            return prompt + f"\n{constraint}"
        return prompt

    def _simplify(self, prompt: str) -> str:
        """Simplify the prompt."""
        # Remove redundant lines
        lines = prompt.split("\n")
        seen = set()
        result = []

        for line in lines:
            normalized = line.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(line)
            elif not normalized:
                result.append(line)  # Keep blank lines

        return "\n".join(result)

    def _select_survivors(
        self,
        population: list[PromptCandidate],
    ) -> list[PromptCandidate]:
        """Select survivors for the next generation."""
        # Sort by score
        sorted_pop = sorted(population, key=lambda c: c.score, reverse=True)

        # Keep elites
        survivors = sorted_pop[: self.config.elite_count]

        # Fill rest with tournament selection
        remaining = self.config.population_size - len(survivors)
        import random

        while len(survivors) < self.config.population_size:
            tournament = random.sample(sorted_pop, min(3, len(sorted_pop)))
            winner = max(tournament, key=lambda c: c.score)
            if winner not in survivors:
                survivors.append(winner)

        return survivors[: self.config.population_size]

    def _check_convergence(self, population: list[PromptCandidate]) -> bool:
        """Check if population has converged."""
        if len(population) < 2:
            return True

        scores = [c.score for c in population]
        score_range = max(scores) - min(scores)

        return score_range < self.config.improvement_threshold

    def _default_evaluator(
        self,
        prompt: str,
        examples: list[dict[str, Any]],
    ) -> float:
        """Default prompt evaluator using heuristics."""
        score = 5.0  # Base score

        # Length check (not too short, not too long)
        length = len(prompt)
        if 100 < length < 500:
            score += 1.0
        elif length < 50 or length > 1000:
            score -= 1.0

        # Structure check
        if "\n" in prompt:
            score += 0.5
        if any(c in prompt for c in ["-", "*", "1."]):
            score += 0.5  # Has list formatting

        # Clarity indicators
        clarity_words = ["clear", "specific", "concise", "helpful"]
        for word in clarity_words:
            if word in prompt.lower():
                score += 0.2

        # Constraint indicators
        if any(word in prompt.lower() for word in ["must", "should", "always", "never"]):
            score += 0.3

        return min(10.0, max(0.0, score))
