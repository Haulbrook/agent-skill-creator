"""
Pattern Detector - Detects recurring patterns in agent outputs.

This module identifies both positive and negative patterns across multiple
outputs to help understand systematic behaviors that need to be reinforced
or corrected.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class DetectedPattern:
    """A detected pattern in agent outputs."""
    pattern_id: str
    pattern_type: str  # "positive", "negative", "neutral"
    description: str
    frequency: float  # 0-1, proportion of outputs containing pattern
    examples: List[str]
    severity: str  # "low", "medium", "high"
    category: str  # "structural", "content", "style", "domain"
    correction_suggestion: Optional[str] = None
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())


class PatternDetector:
    """
    Detects recurring patterns in agent outputs.

    Identifies:
    - Structural patterns (formatting, organization)
    - Content patterns (repeated phrases, templates)
    - Style patterns (tone, voice, word choice)
    - Domain-specific patterns (code patterns, design patterns)
    - Error patterns (common mistakes, failure modes)
    """

    # Common negative patterns to detect
    NEGATIVE_PATTERNS = {
        "general": [
            {
                "regex": r'\b(TODO|FIXME|XXX|HACK)\b',
                "description": "Contains unfinished markers",
                "category": "content",
                "severity": "medium"
            },
            {
                "regex": r'(?:\b\w+\b)(?:\s+\1){2,}',
                "description": "Excessive word repetition",
                "category": "style",
                "severity": "low"
            },
            {
                "regex": r'^\s*$\n^\s*$\n^\s*$',
                "description": "Multiple blank lines",
                "category": "structural",
                "severity": "low"
            },
            {
                "regex": r'(?:Lorem ipsum|placeholder|sample text|example text)',
                "description": "Contains placeholder text",
                "category": "content",
                "severity": "high"
            },
            {
                "regex": r'(?:I apologize|I\'m sorry|As an AI)',
                "description": "Unnecessary AI self-references",
                "category": "style",
                "severity": "low"
            }
        ],
        "website_building": [
            {
                "regex": r'style\s*=\s*["\'][^"\']{20,}["\']',
                "description": "Long inline styles",
                "category": "code",
                "severity": "medium"
            },
            {
                "regex": r'!important',
                "description": "Uses !important (specificity issue)",
                "category": "code",
                "severity": "medium"
            },
            {
                "regex": r'<div>\s*<div>\s*<div>',
                "description": "Nested div soup",
                "category": "structural",
                "severity": "medium"
            },
            {
                "regex": r'px\s*[;}\)]',
                "description": "Uses fixed pixel units",
                "category": "code",
                "severity": "low"
            },
            {
                "regex": r'<img[^>]*(?!alt=)[^>]*>',
                "description": "Images without alt text",
                "category": "accessibility",
                "severity": "high"
            },
            {
                "regex": r'onclick\s*=',
                "description": "Inline event handlers",
                "category": "code",
                "severity": "medium"
            }
        ],
        "marketing": [
            {
                "regex": r'\b(synergy|leverage|paradigm|disrupt|innovative)\b',
                "description": "Overused buzzwords",
                "category": "style",
                "severity": "low"
            },
            {
                "regex": r'(?:best|leading|top|premier|ultimate)\s+(?:in class|quality|service)',
                "description": "Generic superlatives",
                "category": "content",
                "severity": "medium"
            },
            {
                "regex": r'(?:we|our|us)\s+(?:\w+\s+){0,3}(?:we|our|us)',
                "description": "Too self-focused (not customer-centric)",
                "category": "style",
                "severity": "medium"
            }
        ],
        "coding": [
            {
                "regex": r'except:\s*(?:pass|\.\.\.)',
                "description": "Bare except with pass",
                "category": "code",
                "severity": "high"
            },
            {
                "regex": r'eval\s*\(',
                "description": "Uses eval (security risk)",
                "category": "security",
                "severity": "high"
            },
            {
                "regex": r'print\s*\([^)]*\)',
                "description": "Uses print instead of logging",
                "category": "code",
                "severity": "low"
            },
            {
                "regex": r'(?:password|secret|key)\s*=\s*["\'][^"\']+["\']',
                "description": "Hardcoded secrets",
                "category": "security",
                "severity": "high"
            },
            {
                "regex": r'# type:\s*ignore',
                "description": "Type checking disabled",
                "category": "code",
                "severity": "low"
            },
            {
                "regex": r'time\.sleep\s*\(\s*\d+\s*\)',
                "description": "Fixed sleep duration",
                "category": "code",
                "severity": "low"
            }
        ]
    }

    # Common positive patterns to detect
    POSITIVE_PATTERNS = {
        "general": [
            {
                "regex": r'(?:##?#?)\s+[A-Z]',
                "description": "Uses proper headings",
                "category": "structural"
            },
            {
                "regex": r'(?:\n-\s|\n\*\s|\n\d+\.\s)',
                "description": "Uses organized lists",
                "category": "structural"
            }
        ],
        "website_building": [
            {
                "regex": r'@media\s*\(',
                "description": "Uses media queries",
                "category": "code"
            },
            {
                "regex": r'(?:flex|grid)',
                "description": "Uses modern layout",
                "category": "code"
            },
            {
                "regex": r'(?:rem|em|%|vw|vh)',
                "description": "Uses relative units",
                "category": "code"
            },
            {
                "regex": r'alt\s*=\s*["\'][^"\']+["\']',
                "description": "Provides alt text",
                "category": "accessibility"
            },
            {
                "regex": r'(?:header|nav|main|section|article|footer)>',
                "description": "Uses semantic HTML",
                "category": "code"
            }
        ],
        "marketing": [
            {
                "regex": r'(?:you|your)\s+(?:\w+\s+){0,3}(?:you|your)',
                "description": "Customer-focused language",
                "category": "style"
            },
            {
                "regex": r'(?:\d+%|\d+x|\$\d+)',
                "description": "Uses specific numbers",
                "category": "content"
            },
            {
                "regex": r'(?:click|sign up|get started|try|download|learn more)',
                "description": "Has call-to-action",
                "category": "content"
            }
        ],
        "coding": [
            {
                "regex": r'def\s+\w+\([^)]*\)\s*->\s*\w+',
                "description": "Uses return type hints",
                "category": "code"
            },
            {
                "regex": r'"""[^"]+"""',
                "description": "Has docstrings",
                "category": "documentation"
            },
            {
                "regex": r'(?:try|except|finally):',
                "description": "Has error handling",
                "category": "code"
            },
            {
                "regex": r'logging\.',
                "description": "Uses logging",
                "category": "code"
            },
            {
                "regex": r'(?:assert|pytest|unittest)',
                "description": "Includes testing",
                "category": "code"
            }
        ]
    }

    def __init__(self):
        """Initialize the pattern detector."""
        self._session_patterns: Dict[str, List[DetectedPattern]] = defaultdict(list)
        self._pattern_counter = 0

    def detect(
        self,
        outputs: List[Dict[str, Any]],
        domain: str = "general"
    ) -> List[DetectedPattern]:
        """
        Detect patterns across multiple outputs.

        Args:
            outputs: List of outputs to analyze
            domain: Domain for context-specific pattern detection

        Returns:
            List of detected patterns
        """
        if not outputs:
            return []

        patterns = []
        contents = [self._extract_content(o) for o in outputs]

        # Detect negative patterns
        negative_patterns = self._detect_defined_patterns(
            contents, domain, "negative"
        )
        patterns.extend(negative_patterns)

        # Detect positive patterns
        positive_patterns = self._detect_defined_patterns(
            contents, domain, "positive"
        )
        patterns.extend(positive_patterns)

        # Detect emergent patterns (recurring phrases, structures)
        emergent_patterns = self._detect_emergent_patterns(contents)
        patterns.extend(emergent_patterns)

        # Detect structural patterns
        structural_patterns = self._detect_structural_patterns(contents)
        patterns.extend(structural_patterns)

        return patterns

    def _detect_defined_patterns(
        self,
        contents: List[str],
        domain: str,
        pattern_type: str
    ) -> List[DetectedPattern]:
        """Detect predefined patterns."""
        detected = []

        pattern_defs = (
            self.NEGATIVE_PATTERNS if pattern_type == "negative"
            else self.POSITIVE_PATTERNS
        )

        # Get domain-specific and general patterns
        all_patterns = pattern_defs.get(domain, []) + pattern_defs.get("general", [])

        for pattern_def in all_patterns:
            regex = pattern_def["regex"]
            matches = []
            examples = []

            for content in contents:
                found = re.findall(regex, content, re.IGNORECASE | re.MULTILINE)
                if found:
                    matches.append(content)
                    examples.extend(found[:2])

            frequency = len(matches) / len(contents) if contents else 0

            if frequency > 0.1:  # At least 10% occurrence
                self._pattern_counter += 1
                detected.append(DetectedPattern(
                    pattern_id=f"pat_{self._pattern_counter}",
                    pattern_type=pattern_type,
                    description=pattern_def["description"],
                    frequency=round(frequency, 2),
                    examples=list(set(examples))[:3],
                    severity=pattern_def.get("severity", "medium") if pattern_type == "negative" else "positive",
                    category=pattern_def.get("category", "general"),
                    correction_suggestion=self._get_correction(pattern_def["description"]) if pattern_type == "negative" else None
                ))

        return detected

    def _detect_emergent_patterns(
        self,
        contents: List[str]
    ) -> List[DetectedPattern]:
        """Detect recurring phrases and templates."""
        detected = []

        if len(contents) < 2:
            return detected

        # Find common n-grams
        ngram_counts: Dict[str, int] = defaultdict(int)

        for content in contents:
            words = re.findall(r'\b\w+\b', content.lower())
            # Check for 3-grams to 6-grams
            for n in range(3, 7):
                for i in range(len(words) - n + 1):
                    ngram = ' '.join(words[i:i+n])
                    ngram_counts[ngram] += 1

        # Find ngrams appearing in multiple outputs
        threshold = max(2, len(contents) * 0.3)
        common_ngrams = [
            (ngram, count) for ngram, count in ngram_counts.items()
            if count >= threshold
        ]

        # Filter out overlapping/redundant ngrams
        common_ngrams.sort(key=lambda x: (-len(x[0].split()), -x[1]))
        seen_phrases: Set[str] = set()

        for ngram, count in common_ngrams[:10]:
            # Skip if this is a subset of an already-seen phrase
            if any(ngram in seen for seen in seen_phrases):
                continue

            seen_phrases.add(ngram)
            frequency = count / len(contents)

            # Determine if this is positive or negative
            is_template = self._is_template_phrase(ngram)

            self._pattern_counter += 1
            detected.append(DetectedPattern(
                pattern_id=f"pat_{self._pattern_counter}",
                pattern_type="negative" if is_template else "neutral",
                description=f"Recurring phrase: '{ngram}'",
                frequency=round(frequency, 2),
                examples=[ngram],
                severity="low" if is_template else "info",
                category="content",
                correction_suggestion="Vary phrasing to avoid repetitive templates" if is_template else None
            ))

        return detected

    def _is_template_phrase(self, phrase: str) -> bool:
        """Check if a phrase looks like a rigid template."""
        template_indicators = [
            r'^(?:here is|here are|this is|i will|let me)',
            r'(?:as follows|listed below|shown below)',
            r'^(?:in conclusion|to summarize|in summary)',
        ]

        for indicator in template_indicators:
            if re.match(indicator, phrase, re.IGNORECASE):
                return True

        return False

    def _detect_structural_patterns(
        self,
        contents: List[str]
    ) -> List[DetectedPattern]:
        """Detect structural patterns across outputs."""
        detected = []

        if len(contents) < 2:
            return detected

        # Check for consistent structure
        structures = []
        for content in contents:
            structure = self._extract_structure(content)
            structures.append(structure)

        # Find common structural elements
        all_elements = [elem for s in structures for elem in s]
        element_counts = defaultdict(int)
        for elem in all_elements:
            element_counts[elem] += 1

        threshold = len(contents) * 0.5
        common_elements = [elem for elem, count in element_counts.items() if count >= threshold]

        if common_elements:
            self._pattern_counter += 1
            detected.append(DetectedPattern(
                pattern_id=f"pat_{self._pattern_counter}",
                pattern_type="positive",
                description=f"Consistent structure: uses {', '.join(common_elements)}",
                frequency=1.0,
                examples=common_elements,
                severity="positive",
                category="structural"
            ))

        # Check for inconsistency
        unique_structures = len(set(tuple(s) for s in structures))
        if unique_structures > len(contents) * 0.7:
            self._pattern_counter += 1
            detected.append(DetectedPattern(
                pattern_id=f"pat_{self._pattern_counter}",
                pattern_type="negative",
                description="Inconsistent output structure",
                frequency=unique_structures / len(contents),
                examples=["Structure varies significantly across outputs"],
                severity="medium",
                category="structural",
                correction_suggestion="Establish a consistent output template"
            ))

        return detected

    def _extract_structure(self, content: str) -> List[str]:
        """Extract structural elements from content."""
        elements = []

        if re.search(r'^#', content, re.MULTILINE):
            elements.append("headers")
        if re.search(r'```', content):
            elements.append("code_blocks")
        if re.search(r'^\s*[-*]\s', content, re.MULTILINE):
            elements.append("bullet_lists")
        if re.search(r'^\s*\d+\.\s', content, re.MULTILINE):
            elements.append("numbered_lists")
        if re.search(r'\n\n', content):
            elements.append("paragraphs")
        if re.search(r'\|.+\|', content):
            elements.append("tables")

        return elements

    def _get_correction(self, description: str) -> str:
        """Get correction suggestion for a pattern."""
        corrections = {
            "Contains unfinished markers": "Complete all TODO/FIXME items before output",
            "Uses !important": "Improve CSS specificity instead of using !important",
            "Long inline styles": "Move styles to CSS classes",
            "Nested div soup": "Use semantic HTML elements",
            "Uses fixed pixel units": "Use relative units (rem, em, %) for responsiveness",
            "Images without alt text": "Add descriptive alt text to all images",
            "Inline event handlers": "Move event handlers to JavaScript",
            "Overused buzzwords": "Use specific, concrete language",
            "Generic superlatives": "Provide specific evidence and numbers",
            "Bare except with pass": "Handle specific exceptions or log errors",
            "Uses eval": "Use safer alternatives like ast.literal_eval",
            "Uses print instead of logging": "Use the logging module for better control",
            "Hardcoded secrets": "Use environment variables or secret management",
            "Contains placeholder text": "Replace placeholder text with actual content",
        }

        for key, correction in corrections.items():
            if key.lower() in description.lower():
                return correction

        return f"Address: {description}"

    def get_negative_patterns(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Get negative patterns for a session."""
        patterns = self._session_patterns.get(session_id, [])
        return [
            {
                "pattern_id": p.pattern_id,
                "type": p.pattern_type,
                "description": p.description,
                "frequency": p.frequency,
                "severity": p.severity,
                "correction": p.correction_suggestion
            }
            for p in patterns if p.pattern_type == "negative"
        ]

    def store_session_patterns(
        self,
        session_id: str,
        patterns: List[DetectedPattern]
    ) -> None:
        """Store detected patterns for a session."""
        self._session_patterns[session_id].extend(patterns)

    def _extract_content(self, data: Dict[str, Any]) -> str:
        """Extract text content from data dict."""
        if isinstance(data, str):
            return data

        for key in ["output", "content", "text", "response", "result"]:
            if key in data:
                val = data[key]
                if isinstance(val, str):
                    return val

        return str(data)
