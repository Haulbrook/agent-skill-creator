"""
Output Evaluator - Evaluates individual agent outputs for quality.

This module provides detailed evaluation of individual outputs, identifying
specific strengths, weaknesses, and improvement opportunities.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class OutputEvaluation:
    """Detailed evaluation of a single output."""
    output_id: str
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    dimension_scores: Dict[str, float]
    detailed_feedback: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class OutputEvaluator:
    """
    Evaluates individual agent outputs for quality and improvement opportunities.

    Provides detailed feedback on:
    - Content quality and accuracy
    - Structure and organization
    - Domain-specific requirements
    - Style and presentation
    """

    # Domain-specific evaluation criteria
    EVALUATION_CRITERIA = {
        "website_building": {
            "dimensions": {
                "visual_design": {
                    "weight": 0.25,
                    "indicators": {
                        "positive": ["color scheme", "typography", "spacing", "layout", "visual hierarchy"],
                        "negative": ["cluttered", "inconsistent", "poor contrast", "cramped"]
                    }
                },
                "code_quality": {
                    "weight": 0.25,
                    "indicators": {
                        "positive": ["semantic HTML", "clean CSS", "organized", "commented", "DRY"],
                        "negative": ["inline styles", "div soup", "redundant", "messy", "no structure"]
                    }
                },
                "responsiveness": {
                    "weight": 0.20,
                    "indicators": {
                        "positive": ["mobile-first", "media queries", "flexible", "fluid", "viewport"],
                        "negative": ["fixed width", "not responsive", "overflow", "horizontal scroll"]
                    }
                },
                "functionality": {
                    "weight": 0.15,
                    "indicators": {
                        "positive": ["interactive", "working links", "functional forms", "smooth transitions"],
                        "negative": ["broken links", "non-functional", "buggy", "errors"]
                    }
                },
                "accessibility": {
                    "weight": 0.15,
                    "indicators": {
                        "positive": ["alt text", "ARIA", "keyboard nav", "focus states", "contrast"],
                        "negative": ["missing alt", "no ARIA", "mouse-only", "poor focus"]
                    }
                }
            }
        },
        "marketing": {
            "dimensions": {
                "messaging": {
                    "weight": 0.30,
                    "indicators": {
                        "positive": ["clear value prop", "compelling headline", "benefit-focused", "unique"],
                        "negative": ["generic", "feature-focused", "weak headline", "confusing"]
                    }
                },
                "audience_targeting": {
                    "weight": 0.25,
                    "indicators": {
                        "positive": ["persona-aware", "pain points", "needs addressed", "relevant"],
                        "negative": ["broad", "unfocused", "irrelevant", "tone-deaf"]
                    }
                },
                "call_to_action": {
                    "weight": 0.20,
                    "indicators": {
                        "positive": ["clear CTA", "compelling", "urgency", "action-oriented"],
                        "negative": ["no CTA", "weak CTA", "passive", "unclear next step"]
                    }
                },
                "persuasion": {
                    "weight": 0.15,
                    "indicators": {
                        "positive": ["social proof", "credibility", "emotional appeal", "logic"],
                        "negative": ["no proof", "unsubstantiated", "pushy", "manipulative"]
                    }
                },
                "engagement": {
                    "weight": 0.10,
                    "indicators": {
                        "positive": ["engaging", "memorable", "shareable", "conversation starter"],
                        "negative": ["boring", "forgettable", "dry", "uninteresting"]
                    }
                }
            }
        },
        "coding": {
            "dimensions": {
                "correctness": {
                    "weight": 0.30,
                    "indicators": {
                        "positive": ["works correctly", "handles edge cases", "robust", "tested"],
                        "negative": ["bugs", "errors", "fails", "incomplete", "crashes"]
                    }
                },
                "readability": {
                    "weight": 0.25,
                    "indicators": {
                        "positive": ["clear names", "well-organized", "documented", "formatted"],
                        "negative": ["cryptic names", "messy", "no comments", "poor formatting"]
                    }
                },
                "maintainability": {
                    "weight": 0.20,
                    "indicators": {
                        "positive": ["modular", "DRY", "extensible", "decoupled", "clean"],
                        "negative": ["monolithic", "duplicated", "tightly coupled", "spaghetti"]
                    }
                },
                "performance": {
                    "weight": 0.15,
                    "indicators": {
                        "positive": ["efficient", "optimized", "fast", "low memory"],
                        "negative": ["slow", "memory leak", "O(n^2)", "inefficient"]
                    }
                },
                "best_practices": {
                    "weight": 0.10,
                    "indicators": {
                        "positive": ["type hints", "error handling", "logging", "testing"],
                        "negative": ["no types", "swallows exceptions", "no logging", "untested"]
                    }
                }
            }
        },
        "general": {
            "dimensions": {
                "clarity": {
                    "weight": 0.30,
                    "indicators": {
                        "positive": ["clear", "understandable", "well-explained", "precise"],
                        "negative": ["confusing", "vague", "ambiguous", "unclear"]
                    }
                },
                "completeness": {
                    "weight": 0.25,
                    "indicators": {
                        "positive": ["comprehensive", "thorough", "complete", "addresses all points"],
                        "negative": ["incomplete", "partial", "missing info", "gaps"]
                    }
                },
                "accuracy": {
                    "weight": 0.25,
                    "indicators": {
                        "positive": ["accurate", "correct", "factual", "verified"],
                        "negative": ["inaccurate", "wrong", "errors", "misleading"]
                    }
                },
                "usefulness": {
                    "weight": 0.20,
                    "indicators": {
                        "positive": ["helpful", "actionable", "practical", "valuable"],
                        "negative": ["unhelpful", "impractical", "useless", "theoretical only"]
                    }
                }
            }
        }
    }

    def __init__(self):
        """Initialize the output evaluator."""
        pass

    def evaluate(
        self,
        output: Dict[str, Any],
        domain: str = "general",
        input_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single output.

        Args:
            output: The output to evaluate
            domain: The domain for context-specific evaluation
            input_context: Optional input that produced this output

        Returns:
            Evaluation dictionary with scores, strengths, weaknesses, suggestions
        """
        content = self._extract_content(output)
        criteria = self.EVALUATION_CRITERIA.get(domain, self.EVALUATION_CRITERIA["general"])

        # Evaluate each dimension
        dimension_scores = {}
        all_strengths = []
        all_weaknesses = []

        for dim_name, dim_config in criteria["dimensions"].items():
            score, strengths, weaknesses = self._evaluate_dimension(
                content, dim_name, dim_config
            )
            dimension_scores[dim_name] = score
            all_strengths.extend(strengths)
            all_weaknesses.extend(weaknesses)

        # Calculate overall score (weighted average)
        overall_score = sum(
            dimension_scores[dim] * criteria["dimensions"][dim]["weight"]
            for dim in dimension_scores
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(all_weaknesses, domain)

        # Check against input if provided
        if input_context:
            context_feedback = self._evaluate_against_input(content, input_context)
            if context_feedback.get("missed_requirements"):
                all_weaknesses.extend(context_feedback["missed_requirements"])
            if context_feedback.get("extra_credit"):
                all_strengths.extend(context_feedback["extra_credit"])

        return {
            "overall_score": round(overall_score, 2),
            "dimension_scores": {k: round(v, 2) for k, v in dimension_scores.items()},
            "strengths": list(set(all_strengths))[:5],
            "weaknesses": list(set(all_weaknesses))[:5],
            "suggestions": suggestions[:5]
        }

    def _evaluate_dimension(
        self,
        content: str,
        dimension_name: str,
        config: Dict[str, Any]
    ) -> tuple:
        """Evaluate a single dimension."""
        indicators = config.get("indicators", {})
        positive = indicators.get("positive", [])
        negative = indicators.get("negative", [])

        content_lower = content.lower()

        # Count matches
        positive_matches = []
        for ind in positive:
            if ind.lower() in content_lower or re.search(rf'\b{re.escape(ind)}\b', content, re.IGNORECASE):
                positive_matches.append(ind)

        negative_matches = []
        for ind in negative:
            if ind.lower() in content_lower or re.search(rf'\b{re.escape(ind)}\b', content, re.IGNORECASE):
                negative_matches.append(ind)

        # Calculate score
        max_positive = len(positive)
        positive_ratio = len(positive_matches) / max_positive if max_positive > 0 else 0.5

        # Apply penalty for negatives
        penalty = len(negative_matches) * 1.0
        base_score = positive_ratio * 10
        score = max(0, min(10, base_score - penalty))

        # Build strengths and weaknesses
        strengths = [f"Good {dimension_name}: {m}" for m in positive_matches[:2]]
        weaknesses = [f"{dimension_name} issue: {m}" for m in negative_matches[:2]]

        return score, strengths, weaknesses

    def _generate_suggestions(
        self,
        weaknesses: List[str],
        domain: str
    ) -> List[str]:
        """Generate improvement suggestions based on weaknesses."""
        suggestions = []

        suggestion_map = {
            # Website building
            "inline styles": "Move styles to CSS classes or a stylesheet",
            "div soup": "Use semantic HTML elements (header, nav, main, section, footer)",
            "not responsive": "Add media queries and use flexible units (%, rem, vw/vh)",
            "no contrast": "Ensure text has at least 4.5:1 contrast ratio with background",
            "missing alt": "Add descriptive alt text to all images",

            # Marketing
            "generic": "Add specific details, numbers, and unique value propositions",
            "no CTA": "Add a clear call-to-action that tells users what to do next",
            "weak headline": "Use action words and address the main benefit in the headline",
            "unfocused": "Define a specific target audience and tailor messaging",

            # Coding
            "no types": "Add type hints to function signatures and variables",
            "swallows exceptions": "Log or re-raise exceptions with context",
            "no comments": "Add docstrings to functions and comments for complex logic",
            "duplicated": "Extract common code into reusable functions",

            # General
            "confusing": "Simplify language and break into shorter sentences",
            "incomplete": "Address all aspects of the request",
            "inaccurate": "Verify facts and cite sources",
        }

        for weakness in weaknesses:
            weakness_lower = weakness.lower()
            for key, suggestion in suggestion_map.items():
                if key in weakness_lower:
                    suggestions.append(suggestion)
                    break
            else:
                # Generic suggestion based on the weakness
                suggestions.append(f"Address: {weakness}")

        return list(set(suggestions))

    def _evaluate_against_input(
        self,
        content: str,
        input_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate output against the input requirements."""
        result = {
            "missed_requirements": [],
            "extra_credit": []
        }

        # Extract requirements from input
        input_text = self._extract_content(input_context)
        requirements = self._extract_requirements(input_text)

        content_lower = content.lower()

        for req in requirements:
            if req.lower() not in content_lower:
                result["missed_requirements"].append(f"Missing: {req}")

        return result

    def _extract_requirements(self, input_text: str) -> List[str]:
        """Extract explicit requirements from input."""
        requirements = []

        # Look for requirement patterns
        patterns = [
            r'must (?:have|include|contain|be) ([^.!?]+)',
            r'should (?:have|include|contain|be) ([^.!?]+)',
            r'need(?:s)? (?:to have|to include|) ([^.!?]+)',
            r'require(?:s|d)? ([^.!?]+)',
            r'make sure (?:to |it |there\'s )?([^.!?]+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, input_text, re.IGNORECASE)
            requirements.extend(matches)

        return requirements[:5]  # Top 5 requirements

    def _extract_content(self, data: Dict[str, Any]) -> str:
        """Extract text content from data dict."""
        if isinstance(data, str):
            return data

        for key in ["output", "content", "text", "response", "result", "message"]:
            if key in data:
                val = data[key]
                if isinstance(val, str):
                    return val
                elif isinstance(val, dict):
                    return str(val)

        return str(data)

    def batch_evaluate(
        self,
        outputs: List[Dict[str, Any]],
        domain: str = "general",
        inputs: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate multiple outputs.

        Args:
            outputs: List of outputs to evaluate
            domain: The domain for evaluation
            inputs: Optional corresponding inputs

        Returns:
            List of evaluation results
        """
        results = []
        for i, output in enumerate(outputs):
            input_ctx = inputs[i] if inputs and i < len(inputs) else None
            result = self.evaluate(output, domain, input_ctx)
            results.append(result)

        return results
