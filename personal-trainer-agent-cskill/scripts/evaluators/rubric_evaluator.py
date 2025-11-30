"""
Rubric Evaluator - Structured evaluation using customizable rubrics.

This module provides rubric-based evaluation of agent outputs with
configurable criteria, weights, and scoring scales.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RubricCriterion:
    """A single criterion in an evaluation rubric."""
    name: str
    description: str
    weight: float  # 0-1, should sum to 1 across all criteria
    scoring_guide: Dict[int, str]  # score -> description
    indicators: Dict[str, List[str]]  # positive/negative indicators


@dataclass
class Rubric:
    """Complete evaluation rubric."""
    name: str
    domain: str
    criteria: List[RubricCriterion]
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RubricScore:
    """Result of rubric evaluation."""
    overall_score: float  # 0-10
    dimension_scores: Dict[str, float]
    dimension_feedback: Dict[str, str]
    strengths: List[str]
    areas_for_improvement: List[str]
    rubric_used: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RubricEvaluator:
    """
    Evaluates outputs using structured rubrics.

    Rubrics provide consistent, repeatable evaluation with:
    - Clear criteria definitions
    - Weighted scoring
    - Specific indicators for each score level
    - Domain-specific customization

    Usage:
        evaluator = RubricEvaluator()

        # Load domain-specific rubric
        evaluator.load_domain_rubric("website_building")

        # Evaluate output
        score = evaluator.evaluate(output)

        # Or use custom rubric
        evaluator.set_rubric(custom_rubric_dict)
    """

    # Built-in domain rubrics
    DOMAIN_RUBRICS = {
        "website_building": {
            "name": "Website Building Quality Rubric",
            "criteria": [
                {
                    "name": "visual_design",
                    "description": "Quality of visual design and aesthetics",
                    "weight": 0.20,
                    "scoring_guide": {
                        10: "Exceptional design with professional aesthetics, perfect color harmony, typography, and spacing",
                        8: "Strong design with good visual hierarchy, appropriate colors, and clean layout",
                        6: "Adequate design, functional but not visually impressive",
                        4: "Weak design with issues in color, spacing, or layout",
                        2: "Poor design that looks unprofessional or broken"
                    },
                    "indicators": {
                        "positive": ["color scheme", "visual hierarchy", "whitespace", "typography", "modern", "clean"],
                        "negative": ["cluttered", "inconsistent", "ugly", "cramped", "dated"]
                    }
                },
                {
                    "name": "code_quality",
                    "description": "Quality and maintainability of code",
                    "weight": 0.25,
                    "scoring_guide": {
                        10: "Exemplary code - semantic HTML, organized CSS, well-commented, follows best practices",
                        8: "Good code quality with proper structure and reasonable organization",
                        6: "Functional code but could be better organized",
                        4: "Messy code with poor organization or practices",
                        2: "Very poor code quality, hard to understand or maintain"
                    },
                    "indicators": {
                        "positive": ["semantic", "organized", "commented", "BEM", "modular", "DRY"],
                        "negative": ["inline style", "div soup", "!important", "duplicate", "spaghetti"]
                    }
                },
                {
                    "name": "responsiveness",
                    "description": "Mobile-friendliness and responsive behavior",
                    "weight": 0.20,
                    "scoring_guide": {
                        10: "Perfect responsive design, works flawlessly on all screen sizes",
                        8: "Good responsive behavior with minor issues on edge cases",
                        6: "Basic responsiveness, works on common screen sizes",
                        4: "Limited responsiveness, issues on mobile or tablet",
                        2: "Not responsive, breaks on different screen sizes"
                    },
                    "indicators": {
                        "positive": ["responsive", "mobile-first", "media query", "flexible", "fluid", "viewport"],
                        "negative": ["fixed width", "overflow", "horizontal scroll", "not responsive"]
                    }
                },
                {
                    "name": "functionality",
                    "description": "Working features and interactivity",
                    "weight": 0.20,
                    "scoring_guide": {
                        10: "All features work perfectly with smooth interactions",
                        8: "Features work well with minor issues",
                        6: "Core features work, some edge cases may have issues",
                        4: "Some features broken or not working as expected",
                        2: "Major functionality issues, core features don't work"
                    },
                    "indicators": {
                        "positive": ["functional", "working", "interactive", "smooth"],
                        "negative": ["broken", "error", "bug", "crash", "not working"]
                    }
                },
                {
                    "name": "accessibility",
                    "description": "Accessibility compliance and inclusive design",
                    "weight": 0.15,
                    "scoring_guide": {
                        10: "Fully accessible, WCAG 2.1 AA compliant",
                        8: "Good accessibility with ARIA labels and semantic HTML",
                        6: "Basic accessibility considerations present",
                        4: "Limited accessibility, missing key features",
                        2: "Poor accessibility, not usable with assistive technology"
                    },
                    "indicators": {
                        "positive": ["alt text", "aria", "semantic", "contrast", "focus", "keyboard"],
                        "negative": ["no alt", "poor contrast", "not accessible", "mouse only"]
                    }
                }
            ]
        },
        "marketing": {
            "name": "Marketing Content Quality Rubric",
            "criteria": [
                {
                    "name": "messaging_clarity",
                    "description": "Clarity and impact of core message",
                    "weight": 0.25,
                    "scoring_guide": {
                        10: "Crystal clear, compelling message that immediately resonates",
                        8: "Clear message with strong value proposition",
                        6: "Message is understandable but could be stronger",
                        4: "Unclear or confusing message",
                        2: "No clear message or value proposition"
                    },
                    "indicators": {
                        "positive": ["clear", "compelling", "value", "benefit", "unique"],
                        "negative": ["confusing", "vague", "generic", "unclear"]
                    }
                },
                {
                    "name": "audience_targeting",
                    "description": "How well content targets the intended audience",
                    "weight": 0.20,
                    "scoring_guide": {
                        10: "Perfectly tailored to audience pain points and desires",
                        8: "Well-targeted with relevant messaging",
                        6: "Somewhat targeted but could be more specific",
                        4: "Generic messaging not specific to audience",
                        2: "Completely misses the target audience"
                    },
                    "indicators": {
                        "positive": ["you", "your", "pain point", "solution", "benefit"],
                        "negative": ["we", "our", "generic", "one-size-fits-all"]
                    }
                },
                {
                    "name": "call_to_action",
                    "description": "Strength and clarity of call-to-action",
                    "weight": 0.20,
                    "scoring_guide": {
                        10: "Compelling, clear CTA that drives action",
                        8: "Strong CTA with clear next step",
                        6: "CTA present but could be stronger",
                        4: "Weak or unclear CTA",
                        2: "No CTA or completely ineffective"
                    },
                    "indicators": {
                        "positive": ["get started", "sign up", "try", "download", "learn more", "buy now"],
                        "negative": ["no cta", "passive", "unclear", "weak"]
                    }
                },
                {
                    "name": "persuasion",
                    "description": "Use of persuasion techniques and social proof",
                    "weight": 0.20,
                    "scoring_guide": {
                        10: "Masterful use of persuasion with strong proof points",
                        8: "Good persuasion with credible evidence",
                        6: "Some persuasive elements present",
                        4: "Weak persuasion, lacking proof",
                        2: "Not persuasive or uses manipulative tactics"
                    },
                    "indicators": {
                        "positive": ["proof", "testimonial", "statistic", "case study", "guarantee"],
                        "negative": ["unproven", "no evidence", "pushy", "manipulative"]
                    }
                },
                {
                    "name": "engagement",
                    "description": "How engaging and memorable the content is",
                    "weight": 0.15,
                    "scoring_guide": {
                        10: "Highly engaging, memorable, and shareable",
                        8: "Engaging content that holds attention",
                        6: "Moderately engaging",
                        4: "Boring or uninteresting",
                        2: "Completely fails to engage"
                    },
                    "indicators": {
                        "positive": ["story", "emotion", "hook", "curiosity", "surprise"],
                        "negative": ["boring", "dry", "forgettable", "bland"]
                    }
                }
            ]
        },
        "coding": {
            "name": "Code Quality Rubric",
            "criteria": [
                {
                    "name": "correctness",
                    "description": "Code correctness and bug-free operation",
                    "weight": 0.30,
                    "scoring_guide": {
                        10: "Perfect - handles all cases correctly including edge cases",
                        8: "Correct for main cases, minor edge case issues",
                        6: "Works for basic cases but has some bugs",
                        4: "Has significant bugs or incorrect behavior",
                        2: "Fundamentally broken or doesn't work"
                    },
                    "indicators": {
                        "positive": ["correct", "works", "tested", "handles", "validates"],
                        "negative": ["bug", "error", "crash", "incorrect", "broken"]
                    }
                },
                {
                    "name": "readability",
                    "description": "Code readability and documentation",
                    "weight": 0.25,
                    "scoring_guide": {
                        10: "Exceptionally readable with excellent documentation",
                        8: "Good readability with helpful comments",
                        6: "Readable but documentation could improve",
                        4: "Hard to read or poorly documented",
                        2: "Unreadable, cryptic, or no documentation"
                    },
                    "indicators": {
                        "positive": ["docstring", "comment", "clear name", "type hint", "formatted"],
                        "negative": ["cryptic", "no comment", "confusing", "poor names"]
                    }
                },
                {
                    "name": "maintainability",
                    "description": "Code structure and maintainability",
                    "weight": 0.20,
                    "scoring_guide": {
                        10: "Excellent architecture, easy to extend and modify",
                        8: "Good structure, maintainable with minor improvements",
                        6: "Functional but could be better organized",
                        4: "Difficult to maintain or modify",
                        2: "Nightmare to maintain, tightly coupled"
                    },
                    "indicators": {
                        "positive": ["modular", "DRY", "SOLID", "decoupled", "extensible"],
                        "negative": ["monolithic", "duplicate", "coupled", "spaghetti"]
                    }
                },
                {
                    "name": "performance",
                    "description": "Code efficiency and performance",
                    "weight": 0.15,
                    "scoring_guide": {
                        10: "Optimally efficient, excellent performance",
                        8: "Good performance with appropriate algorithms",
                        6: "Acceptable performance for most cases",
                        4: "Performance issues or inefficient code",
                        2: "Severely inefficient, unusable at scale"
                    },
                    "indicators": {
                        "positive": ["efficient", "optimized", "O(n)", "cached", "fast"],
                        "negative": ["slow", "O(n^2)", "memory leak", "inefficient"]
                    }
                },
                {
                    "name": "best_practices",
                    "description": "Following language and industry best practices",
                    "weight": 0.10,
                    "scoring_guide": {
                        10: "Exemplary - follows all best practices perfectly",
                        8: "Follows most best practices consistently",
                        6: "Generally follows best practices",
                        4: "Ignores some important best practices",
                        2: "Violates many best practices"
                    },
                    "indicators": {
                        "positive": ["type hints", "error handling", "logging", "testing", "linting"],
                        "negative": ["no types", "bare except", "print debug", "untested"]
                    }
                }
            ]
        },
        "general": {
            "name": "General Quality Rubric",
            "criteria": [
                {
                    "name": "accuracy",
                    "description": "Factual accuracy of content",
                    "weight": 0.30,
                    "scoring_guide": {
                        10: "Completely accurate with verified facts",
                        8: "Accurate with minor imprecisions",
                        6: "Mostly accurate but some errors",
                        4: "Several inaccuracies present",
                        2: "Largely inaccurate or misleading"
                    },
                    "indicators": {
                        "positive": ["accurate", "correct", "verified", "factual"],
                        "negative": ["incorrect", "wrong", "misleading", "false"]
                    }
                },
                {
                    "name": "completeness",
                    "description": "Thoroughness of response",
                    "weight": 0.25,
                    "scoring_guide": {
                        10: "Comprehensive coverage of all aspects",
                        8: "Thorough with minor gaps",
                        6: "Covers main points but missing some details",
                        4: "Incomplete, missing significant aspects",
                        2: "Very incomplete or superficial"
                    },
                    "indicators": {
                        "positive": ["comprehensive", "thorough", "complete", "detailed"],
                        "negative": ["incomplete", "partial", "missing", "superficial"]
                    }
                },
                {
                    "name": "clarity",
                    "description": "Clarity and understandability",
                    "weight": 0.25,
                    "scoring_guide": {
                        10: "Crystal clear, easily understood",
                        8: "Clear with good explanations",
                        6: "Understandable but could be clearer",
                        4: "Confusing or hard to follow",
                        2: "Very unclear or incomprehensible"
                    },
                    "indicators": {
                        "positive": ["clear", "easy to understand", "well-explained", "organized"],
                        "negative": ["confusing", "unclear", "vague", "disorganized"]
                    }
                },
                {
                    "name": "usefulness",
                    "description": "Practical usefulness of the response",
                    "weight": 0.20,
                    "scoring_guide": {
                        10: "Extremely useful and actionable",
                        8: "Very useful with practical value",
                        6: "Moderately useful",
                        4: "Limited usefulness",
                        2: "Not useful or irrelevant"
                    },
                    "indicators": {
                        "positive": ["useful", "helpful", "actionable", "practical", "valuable"],
                        "negative": ["useless", "unhelpful", "impractical", "irrelevant"]
                    }
                }
            ]
        }
    }

    def __init__(self):
        """Initialize the rubric evaluator."""
        self._current_rubric: Optional[Rubric] = None
        self._evaluation_history: List[RubricScore] = []

    def load_domain_rubric(self, domain: str) -> None:
        """
        Load a built-in domain-specific rubric.

        Args:
            domain: Domain name (website_building, marketing, coding, general)
        """
        if domain not in self.DOMAIN_RUBRICS:
            domain = "general"

        rubric_data = self.DOMAIN_RUBRICS[domain]
        self._current_rubric = self._parse_rubric(rubric_data, domain)

    def set_rubric(self, rubric_dict: Dict[str, Any]) -> None:
        """
        Set a custom rubric.

        Args:
            rubric_dict: Dictionary defining the rubric
        """
        self._current_rubric = self._parse_rubric(rubric_dict, "custom")

    def _parse_rubric(
        self,
        rubric_data: Dict[str, Any],
        domain: str
    ) -> Rubric:
        """Parse rubric data into Rubric object."""
        criteria = []
        for crit_data in rubric_data.get("criteria", []):
            criteria.append(RubricCriterion(
                name=crit_data["name"],
                description=crit_data["description"],
                weight=crit_data["weight"],
                scoring_guide={int(k): v for k, v in crit_data["scoring_guide"].items()},
                indicators=crit_data.get("indicators", {"positive": [], "negative": []})
            ))

        return Rubric(
            name=rubric_data.get("name", f"{domain} rubric"),
            domain=domain,
            criteria=criteria,
            version=rubric_data.get("version", "1.0")
        )

    def evaluate(
        self,
        output: Dict[str, Any],
        input_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate output against current rubric.

        Args:
            output: The output to evaluate
            input_context: Optional input for context

        Returns:
            Dictionary with scores and feedback
        """
        if not self._current_rubric:
            self.load_domain_rubric("general")

        content = self._extract_content(output)

        dimension_scores = {}
        dimension_feedback = {}
        all_strengths = []
        all_improvements = []

        for criterion in self._current_rubric.criteria:
            score, feedback, strengths, improvements = self._evaluate_criterion(
                content, criterion
            )
            dimension_scores[criterion.name] = score
            dimension_feedback[criterion.name] = feedback
            all_strengths.extend(strengths)
            all_improvements.extend(improvements)

        # Calculate weighted overall score
        overall_score = sum(
            dimension_scores[c.name] * c.weight
            for c in self._current_rubric.criteria
        )

        result = {
            "overall_score": round(overall_score, 2),
            "dimension_scores": {k: round(v, 2) for k, v in dimension_scores.items()},
            "dimension_feedback": dimension_feedback,
            "strengths": list(set(all_strengths))[:5],
            "areas_for_improvement": list(set(all_improvements))[:5],
            "rubric_used": self._current_rubric.name
        }

        return result

    def _evaluate_criterion(
        self,
        content: str,
        criterion: RubricCriterion
    ) -> tuple:
        """Evaluate content against a single criterion."""
        content_lower = content.lower()

        # Count indicator matches
        positive_matches = []
        negative_matches = []

        for indicator in criterion.indicators.get("positive", []):
            if indicator.lower() in content_lower:
                positive_matches.append(indicator)

        for indicator in criterion.indicators.get("negative", []):
            if indicator.lower() in content_lower:
                negative_matches.append(indicator)

        # Calculate base score
        max_positive = len(criterion.indicators.get("positive", [1]))
        positive_ratio = len(positive_matches) / max_positive if max_positive > 0 else 0.5

        # Start with indicator-based score
        base_score = positive_ratio * 8 + 2  # Scale to 2-10

        # Apply negative penalty
        negative_penalty = len(negative_matches) * 1.5
        score = max(2, min(10, base_score - negative_penalty))

        # Generate feedback
        scoring_guide = criterion.scoring_guide
        closest_level = min(scoring_guide.keys(), key=lambda x: abs(x - score))
        feedback = scoring_guide[closest_level]

        # Build strengths and improvements
        strengths = [f"{criterion.name}: {ind}" for ind in positive_matches[:2]]
        improvements = [f"{criterion.name}: address '{ind}'" for ind in negative_matches[:2]]

        if score < 6 and not improvements:
            improvements.append(f"Improve {criterion.name}: {criterion.description}")

        return score, feedback, strengths, improvements

    def _extract_content(self, data: Dict[str, Any]) -> str:
        """Extract text content from data."""
        if isinstance(data, str):
            return data

        for key in ["output", "content", "text", "response", "result"]:
            if key in data:
                val = data[key]
                if isinstance(val, str):
                    return val

        return str(data)

    def get_rubric_template(self, domain: str = "general") -> Dict[str, Any]:
        """Get a template for creating custom rubrics."""
        return {
            "name": "Custom Rubric",
            "version": "1.0",
            "criteria": [
                {
                    "name": "criterion_name",
                    "description": "What this criterion measures",
                    "weight": 0.25,
                    "scoring_guide": {
                        10: "Exceptional performance",
                        8: "Good performance",
                        6: "Adequate performance",
                        4: "Below expectations",
                        2: "Poor performance"
                    },
                    "indicators": {
                        "positive": ["good_indicator_1", "good_indicator_2"],
                        "negative": ["bad_indicator_1", "bad_indicator_2"]
                    }
                }
            ]
        }

    def batch_evaluate(
        self,
        outputs: List[Dict[str, Any]],
        inputs: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Evaluate multiple outputs."""
        results = []
        for i, output in enumerate(outputs):
            input_ctx = inputs[i] if inputs and i < len(inputs) else None
            result = self.evaluate(output, input_ctx)
            results.append(result)
        return results

    def get_evaluation_summary(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get summary statistics for multiple evaluations."""
        if not results:
            return {"error": "No results to summarize"}

        overall_scores = [r["overall_score"] for r in results]
        dimension_avgs = {}

        for dim in results[0]["dimension_scores"].keys():
            scores = [r["dimension_scores"][dim] for r in results]
            dimension_avgs[dim] = sum(scores) / len(scores)

        return {
            "count": len(results),
            "average_overall": sum(overall_scores) / len(overall_scores),
            "min_overall": min(overall_scores),
            "max_overall": max(overall_scores),
            "dimension_averages": dimension_avgs,
            "rubric_used": results[0].get("rubric_used", "unknown")
        }
