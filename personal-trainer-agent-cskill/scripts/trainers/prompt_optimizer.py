"""
Prompt Optimizer - Optimizes agent prompts based on evaluation feedback.

This module provides systematic prompt improvement without requiring
model fine-tuning, making it accessible for any agent setup.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class PromptOptimization:
    """Result of prompt optimization."""
    original_prompt: str
    optimized_prompt: str
    changes_made: List[str]
    rationale: str
    expected_improvement: str
    confidence: float  # 0-1


@dataclass
class PromptAnalysis:
    """Analysis of a prompt's characteristics."""
    clarity_score: float
    specificity_score: float
    structure_score: float
    issues: List[str]
    suggestions: List[str]


class PromptOptimizer:
    """
    Optimizes agent prompts based on evaluation feedback.

    Techniques used:
    - Clarity enhancement (simplify, specify)
    - Structure improvement (organization, formatting)
    - Context enrichment (examples, constraints)
    - Weakness addressing (based on evaluation feedback)

    Usage:
        optimizer = PromptOptimizer()

        # Analyze prompts
        analysis = optimizer.analyze_prompts(
            prompts={"system": "You are a helpful assistant"},
            domain="general"
        )

        # Optimize based on feedback
        optimized = optimizer.optimize(
            prompts={"system": "You are a helpful assistant"},
            weaknesses=["outputs are too generic", "lacks structure"],
            suggestions=["add specific examples", "define output format"]
        )
    """

    # Domain-specific prompt templates
    DOMAIN_TEMPLATES = {
        "website_building": {
            "structure": """You are an expert frontend developer specializing in {specialty}.

## Core Principles
- Write clean, semantic HTML5
- Use modern CSS (Flexbox/Grid)
- Ensure mobile-first responsive design
- Follow accessibility guidelines (WCAG 2.1)

## Output Format
1. HTML structure with semantic elements
2. CSS with organized sections
3. Brief explanation of design choices

## Quality Standards
- No inline styles (use CSS classes)
- All images must have alt text
- Use relative units (rem, em, %)
- Include hover/focus states""",
            "additions": [
                "Always explain your design decisions",
                "Include comments for complex sections",
                "Provide mobile and desktop layouts"
            ]
        },
        "marketing": {
            "structure": """You are a marketing strategist with expertise in {specialty}.

## Core Focus
- Customer-centric messaging (focus on "you", not "we")
- Clear value propositions with specific benefits
- Strong calls-to-action

## Output Format
1. Headline (attention-grabbing, benefit-focused)
2. Key message (unique value proposition)
3. Supporting points (3-5 benefits)
4. Call-to-action (clear, compelling)

## Quality Standards
- Avoid generic superlatives ("best", "leading")
- Use specific numbers and proof points
- Address target audience pain points directly""",
            "additions": [
                "Include social proof when relevant",
                "Create urgency without being manipulative",
                "Tailor tone to target audience"
            ]
        },
        "coding": {
            "structure": """You are a senior software engineer specializing in {specialty}.

## Core Principles
- Write clean, maintainable code
- Include type hints and docstrings
- Handle errors appropriately
- Follow language conventions

## Output Format
1. Code with proper structure
2. Brief explanation of approach
3. Usage examples when helpful

## Quality Standards
- No TODO/FIXME markers in final code
- All edge cases handled
- No hardcoded values (use constants/config)
- Include error handling where appropriate""",
            "additions": [
                "Explain any non-obvious design decisions",
                "Note potential optimizations if relevant",
                "Include type hints for all function signatures"
            ]
        },
        "general": {
            "structure": """You are a helpful assistant specializing in {specialty}.

## Core Principles
- Provide clear, accurate information
- Structure responses for easy reading
- Be concise but comprehensive

## Output Format
- Use headers for organization when appropriate
- Use bullet points for lists
- Include examples when helpful

## Quality Standards
- Verify accuracy before responding
- Acknowledge uncertainty when present
- Stay focused on the question asked""",
            "additions": [
                "Ask clarifying questions if needed",
                "Provide actionable next steps when relevant"
            ]
        }
    }

    # Common prompt improvements
    IMPROVEMENT_PATTERNS = {
        "generic_output": {
            "pattern": r"(?:be helpful|assist|help)",
            "improvement": "Include specific output format requirements and examples",
            "example_addition": "\n\n## Output Requirements\nFormat your response as:\n1. [Summary]\n2. [Detailed explanation]\n3. [Examples/code]"
        },
        "lacks_structure": {
            "pattern": r"^(?!.*format|.*structure|.*organize)",
            "improvement": "Add explicit structure requirements",
            "example_addition": "\n\n## Response Structure\n- Start with a brief overview\n- Organize content with clear sections\n- End with key takeaways or next steps"
        },
        "no_examples": {
            "pattern": r"^(?!.*example|.*for instance|.*such as)",
            "improvement": "Include example outputs or demonstrations",
            "example_addition": "\n\n## Example Output\nWhen asked about X, respond like:\n[Your example here]"
        },
        "vague_role": {
            "pattern": r"^you are (?:an?|the) \w+\s*$",
            "improvement": "Expand role definition with specific expertise and behaviors",
            "example_addition": " with deep expertise in [domain]. You excel at [specific skills] and always [key behaviors]."
        },
        "missing_constraints": {
            "pattern": r"^(?!.*must|.*always|.*never|.*important)",
            "improvement": "Add clear constraints and requirements",
            "example_addition": "\n\n## Important Constraints\n- ALWAYS [requirement]\n- NEVER [anti-pattern]\n- When uncertain, [fallback behavior]"
        }
    }

    def __init__(self):
        """Initialize the prompt optimizer."""
        self._optimization_history: List[PromptOptimization] = []

    def analyze_prompts(
        self,
        prompts: Dict[str, str],
        domain: str = "general",
        known_weaknesses: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze prompts and identify improvement opportunities.

        Args:
            prompts: Dictionary of prompt names to prompt content
            domain: Domain for context-specific analysis
            known_weaknesses: Known issues with the agent

        Returns:
            List of analysis results with recommendations
        """
        analyses = []

        for name, prompt in prompts.items():
            analysis = self._analyze_single_prompt(prompt, domain)

            # Add weakness-based recommendations
            if known_weaknesses:
                weakness_suggestions = self._get_weakness_suggestions(known_weaknesses)
                analysis["suggestions"].extend(weakness_suggestions)

            analyses.append({
                "prompt_name": name,
                "prompt_length": len(prompt),
                "priority": self._calculate_priority(analysis),
                **analysis
            })

        return analyses

    def _analyze_single_prompt(
        self,
        prompt: str,
        domain: str
    ) -> Dict[str, Any]:
        """Analyze a single prompt."""
        issues = []
        suggestions = []

        # Check for common issues
        for issue_name, issue_config in self.IMPROVEMENT_PATTERNS.items():
            if re.search(issue_config["pattern"], prompt, re.IGNORECASE | re.MULTILINE):
                issues.append(issue_name)
                suggestions.append({
                    "action": issue_config["improvement"],
                    "priority": self._get_issue_priority(issue_name)
                })

        # Calculate scores
        clarity_score = self._calculate_clarity_score(prompt)
        specificity_score = self._calculate_specificity_score(prompt)
        structure_score = self._calculate_structure_score(prompt)

        return {
            "clarity_score": clarity_score,
            "specificity_score": specificity_score,
            "structure_score": structure_score,
            "overall_score": (clarity_score + specificity_score + structure_score) / 3,
            "issues": issues,
            "suggestions": suggestions
        }

    def _calculate_clarity_score(self, prompt: str) -> float:
        """Calculate clarity score for a prompt."""
        score = 0.5  # Baseline

        # Positive indicators
        if re.search(r'^you are', prompt, re.IGNORECASE):
            score += 0.1  # Clear role definition
        if re.search(r'##?\s+\w+', prompt):
            score += 0.15  # Has headers
        if len(prompt.split('.')) >= 3:
            score += 0.1  # Multiple sentences
        if re.search(r'\d+\.', prompt):
            score += 0.1  # Numbered instructions

        # Negative indicators
        if len(prompt) < 50:
            score -= 0.2  # Too short
        if re.search(r'(?:\w+,\s*){5,}\w+', prompt):
            score -= 0.1  # Long comma lists (hard to read)

        return max(0, min(1, score))

    def _calculate_specificity_score(self, prompt: str) -> float:
        """Calculate specificity score for a prompt."""
        score = 0.3  # Baseline

        # Positive indicators
        specific_terms = [
            r'\b(always|never|must|ensure|require)\b',
            r'\b(specifically|exactly|precisely)\b',
            r'\b\d+\b',  # Numbers
            r'\b(format|structure|organize)\b',
            r'\b(example|instance|such as)\b'
        ]

        for pattern in specific_terms:
            if re.search(pattern, prompt, re.IGNORECASE):
                score += 0.1

        # Domain-specific terms increase specificity
        if re.search(r'\b(HTML|CSS|JavaScript|React|API)\b', prompt, re.IGNORECASE):
            score += 0.15
        if re.search(r'\b(CTA|conversion|engagement|audience)\b', prompt, re.IGNORECASE):
            score += 0.15

        return max(0, min(1, score))

    def _calculate_structure_score(self, prompt: str) -> float:
        """Calculate structure score for a prompt."""
        score = 0.3  # Baseline

        # Check for structural elements
        if re.search(r'^##?\s+', prompt, re.MULTILINE):
            score += 0.2  # Headers
        if re.search(r'^\s*[-*]\s', prompt, re.MULTILINE):
            score += 0.15  # Bullet lists
        if re.search(r'^\s*\d+\.\s', prompt, re.MULTILINE):
            score += 0.15  # Numbered lists
        if prompt.count('\n\n') >= 2:
            score += 0.1  # Paragraph breaks
        if re.search(r'```', prompt):
            score += 0.1  # Code blocks

        return max(0, min(1, score))

    def _get_issue_priority(self, issue_name: str) -> int:
        """Get priority for an issue (1-5, 1 being highest)."""
        priorities = {
            "vague_role": 1,
            "generic_output": 2,
            "lacks_structure": 2,
            "missing_constraints": 3,
            "no_examples": 3
        }
        return priorities.get(issue_name, 4)

    def _calculate_priority(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall priority for improvements."""
        avg_score = analysis.get("overall_score", 0.5)
        num_issues = len(analysis.get("issues", []))

        if avg_score < 0.4 or num_issues >= 3:
            return 1  # High priority
        elif avg_score < 0.6 or num_issues >= 2:
            return 2
        elif avg_score < 0.8 or num_issues >= 1:
            return 3
        else:
            return 4  # Low priority

    def _get_weakness_suggestions(
        self,
        weaknesses: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions based on known weaknesses."""
        suggestions = []

        weakness_mappings = {
            "generic": {
                "action": "Add specific output format and examples to reduce generic responses",
                "priority": 1
            },
            "structure": {
                "action": "Include explicit structure requirements with templates",
                "priority": 2
            },
            "verbose": {
                "action": "Add conciseness constraints (e.g., 'Be concise. Aim for 200-300 words.')",
                "priority": 2
            },
            "incomplete": {
                "action": "Add completeness checklist to ensure all aspects are covered",
                "priority": 1
            },
            "inaccurate": {
                "action": "Add verification requirements (e.g., 'Double-check facts before responding')",
                "priority": 1
            },
            "formatting": {
                "action": "Provide explicit formatting templates and examples",
                "priority": 2
            },
            "tone": {
                "action": "Define specific tone guidelines (formal, casual, professional)",
                "priority": 3
            }
        }

        for weakness in weaknesses:
            weakness_lower = weakness.lower()
            for key, suggestion in weakness_mappings.items():
                if key in weakness_lower:
                    suggestions.append(suggestion)
                    break
            else:
                # Generic suggestion for unmatched weaknesses
                suggestions.append({
                    "action": f"Add explicit guidance to address: {weakness}",
                    "priority": 2
                })

        return suggestions

    def optimize(
        self,
        prompts: Dict[str, str],
        weaknesses: List[str],
        suggestions: List[str],
        domain: str = "general"
    ) -> Dict[str, str]:
        """
        Optimize prompts based on feedback.

        Args:
            prompts: Dictionary of prompt names to content
            weaknesses: List of identified weaknesses
            suggestions: List of improvement suggestions
            domain: Domain for context-specific optimization

        Returns:
            Dictionary of optimized prompts
        """
        optimized_prompts = {}

        for name, prompt in prompts.items():
            optimized = self._optimize_single_prompt(
                prompt, weaknesses, suggestions, domain
            )
            optimized_prompts[name] = optimized.optimized_prompt

            # Store in history
            self._optimization_history.append(optimized)

        return optimized_prompts

    def _optimize_single_prompt(
        self,
        prompt: str,
        weaknesses: List[str],
        suggestions: List[str],
        domain: str
    ) -> PromptOptimization:
        """Optimize a single prompt."""
        optimized = prompt
        changes_made = []

        # Get domain template
        template = self.DOMAIN_TEMPLATES.get(domain, self.DOMAIN_TEMPLATES["general"])

        # Check if prompt needs restructuring
        if len(prompt) < 100 or self._calculate_structure_score(prompt) < 0.4:
            # Use domain template as base
            specialty = self._extract_specialty(prompt)
            optimized = template["structure"].format(specialty=specialty or domain)
            changes_made.append("Applied domain-specific template structure")

        # Apply improvements for each weakness
        weakness_actions = self._get_optimization_actions(weaknesses)
        for action in weakness_actions:
            result, change = self._apply_optimization_action(optimized, action)
            if change:
                optimized = result
                changes_made.append(change)

        # Apply suggestions
        for suggestion in suggestions[:3]:  # Top 3 suggestions
            result, change = self._apply_suggestion(optimized, suggestion)
            if change:
                optimized = result
                changes_made.append(change)

        # Add domain-specific additions if not present
        for addition in template.get("additions", []):
            if addition.lower() not in optimized.lower():
                if "## Additional Guidelines" not in optimized:
                    optimized += "\n\n## Additional Guidelines"
                optimized += f"\n- {addition}"
                changes_made.append(f"Added guideline: {addition[:50]}...")

        return PromptOptimization(
            original_prompt=prompt,
            optimized_prompt=optimized,
            changes_made=changes_made,
            rationale=self._generate_rationale(weaknesses, changes_made),
            expected_improvement=self._estimate_improvement(changes_made),
            confidence=min(0.9, 0.5 + len(changes_made) * 0.1)
        )

    def _extract_specialty(self, prompt: str) -> Optional[str]:
        """Extract specialty/focus from existing prompt."""
        # Look for role definition
        match = re.search(r'you are (?:an? )?(\w+(?:\s+\w+){0,3})', prompt, re.IGNORECASE)
        if match:
            return match.group(1)

        # Look for expertise mentions
        match = re.search(r'expert(?:ise)? in (\w+(?:\s+\w+){0,3})', prompt, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def _get_optimization_actions(
        self,
        weaknesses: List[str]
    ) -> List[Dict[str, Any]]:
        """Get optimization actions for weaknesses."""
        actions = []

        action_mapping = {
            "generic": {
                "type": "add_specificity",
                "content": "\n\n## Specificity Requirements\n- Provide concrete examples\n- Use specific numbers and details\n- Avoid generic phrases like 'high-quality' or 'best'"
            },
            "structure": {
                "type": "add_structure",
                "content": "\n\n## Output Structure\n1. Overview (1-2 sentences)\n2. Main content (organized sections)\n3. Summary/next steps"
            },
            "incomplete": {
                "type": "add_completeness",
                "content": "\n\n## Completeness Checklist\nBefore responding, ensure you've covered:\n- [ ] Main question answered\n- [ ] All parts addressed\n- [ ] Examples provided\n- [ ] Next steps if applicable"
            },
            "verbose": {
                "type": "add_conciseness",
                "content": "\n\n## Conciseness Guidelines\n- Keep responses focused and relevant\n- Aim for 200-400 words unless more detail is requested\n- Use bullet points for lists\n- Avoid unnecessary preamble"
            }
        }

        for weakness in weaknesses:
            weakness_lower = weakness.lower()
            for key, action in action_mapping.items():
                if key in weakness_lower:
                    actions.append(action)
                    break

        return actions

    def _apply_optimization_action(
        self,
        prompt: str,
        action: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        """Apply an optimization action to a prompt."""
        action_type = action.get("type", "")
        content = action.get("content", "")

        # Check if similar content already exists
        if any(line in prompt for line in content.split('\n') if line.strip()):
            return prompt, None

        # Add the content
        return prompt + content, f"Added {action_type.replace('_', ' ')}"

    def _apply_suggestion(
        self,
        prompt: str,
        suggestion: str
    ) -> Tuple[str, Optional[str]]:
        """Apply a suggestion to a prompt."""
        suggestion_lower = suggestion.lower()

        # Specific suggestion implementations
        if "example" in suggestion_lower:
            addition = "\n\n## Example\n[Provide a relevant example that demonstrates the expected output format]"
            if "example" not in prompt.lower():
                return prompt + addition, "Added example section"

        elif "format" in suggestion_lower:
            addition = "\n\n## Output Format\nStructure your response with clear headers and organized sections."
            if "format" not in prompt.lower():
                return prompt + addition, "Added format guidance"

        elif "constraint" in suggestion_lower or "rule" in suggestion_lower:
            addition = "\n\n## Constraints\n- Follow the specified format strictly\n- Stay within the requested scope"
            if "constraint" not in prompt.lower():
                return prompt + addition, "Added constraints section"

        return prompt, None

    def _generate_rationale(
        self,
        weaknesses: List[str],
        changes: List[str]
    ) -> str:
        """Generate rationale for optimizations."""
        if not weaknesses and not changes:
            return "No significant changes needed."

        parts = []
        if weaknesses:
            parts.append(f"Addressed {len(weaknesses)} identified weaknesses")
        if changes:
            parts.append(f"Made {len(changes)} improvements")

        return ". ".join(parts) + "."

    def _estimate_improvement(self, changes: List[str]) -> str:
        """Estimate expected improvement from changes."""
        num_changes = len(changes)

        if num_changes >= 4:
            return "Significant improvement expected (30-50%)"
        elif num_changes >= 2:
            return "Moderate improvement expected (15-30%)"
        elif num_changes >= 1:
            return "Minor improvement expected (5-15%)"
        else:
            return "Minimal change - prompt was already well-structured"

    def get_optimization_history(self) -> List[PromptOptimization]:
        """Get history of all optimizations."""
        return self._optimization_history

    def generate_ab_test_variants(
        self,
        prompt: str,
        domain: str = "general",
        num_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate A/B test variants of a prompt.

        Args:
            prompt: The original prompt
            domain: Domain for optimization
            num_variants: Number of variants to generate

        Returns:
            List of prompt variants with descriptions
        """
        variants = [
            {
                "name": "Original",
                "prompt": prompt,
                "changes": [],
                "hypothesis": "Baseline for comparison"
            }
        ]

        # Variant 1: Enhanced structure
        structured = self._add_structure_variant(prompt, domain)
        variants.append({
            "name": "Enhanced Structure",
            "prompt": structured,
            "changes": ["Added clear sections and hierarchy"],
            "hypothesis": "Better structure improves output organization"
        })

        # Variant 2: Added examples
        with_examples = self._add_examples_variant(prompt, domain)
        variants.append({
            "name": "With Examples",
            "prompt": with_examples,
            "changes": ["Added concrete examples"],
            "hypothesis": "Examples help produce more relevant outputs"
        })

        # Variant 3: Strict constraints
        if num_variants > 3:
            constrained = self._add_constraints_variant(prompt, domain)
            variants.append({
                "name": "Strict Constraints",
                "prompt": constrained,
                "changes": ["Added explicit constraints and requirements"],
                "hypothesis": "Constraints reduce errors and improve consistency"
            })

        return variants[:num_variants + 1]  # Include original

    def _add_structure_variant(self, prompt: str, domain: str) -> str:
        """Create a variant with enhanced structure."""
        if "##" in prompt:
            return prompt

        sections = [
            "## Role",
            prompt.strip(),
            "",
            "## Output Guidelines",
            "- Structure your response clearly",
            "- Use appropriate formatting",
            "- Be thorough but concise"
        ]
        return "\n".join(sections)

    def _add_examples_variant(self, prompt: str, domain: str) -> str:
        """Create a variant with examples."""
        if "example" in prompt.lower():
            return prompt

        example_section = """

## Example
Input: [Sample input]
Output: [Sample output showing expected format and quality]
"""
        return prompt + example_section

    def _add_constraints_variant(self, prompt: str, domain: str) -> str:
        """Create a variant with strict constraints."""
        constraints = """

## Strict Requirements
1. ALWAYS follow the specified format
2. NEVER include placeholder text or TODOs
3. ALWAYS verify accuracy before responding
4. Keep responses focused and relevant
"""
        return prompt + constraints
