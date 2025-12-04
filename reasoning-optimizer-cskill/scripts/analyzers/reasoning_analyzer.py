"""
Reasoning Analyzer

Analyzes code for reasoning patterns and logical flow alignment
with the 5-Phase Reasoning Model.

Requirements:
- Detect reasoning phase indicators in code
- Identify logical flow patterns
- Assess reasoning completeness
- Map code sections to reasoning phases
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ReasoningPattern:
    """Represents a detected reasoning pattern in code."""
    phase: str
    pattern_type: str
    location: Tuple[int, int]  # (start_line, end_line)
    confidence: float
    evidence: str


class ReasoningAnalyzer:
    """
    Analyzes code for reasoning methodology alignment.

    This analyzer maps code patterns to the 5-Phase Reasoning Model:
    1. Comprehension - Problem understanding
    2. Strategy - Approach planning
    3. Execution - Implementation
    4. Review - Verification
    5. Refinement - Optimization

    Example:
        >>> analyzer = ReasoningAnalyzer()
        >>> patterns = analyzer.find_reasoning_patterns(code)
        >>> coverage = analyzer.calculate_phase_coverage(patterns)
    """

    # Phase indicator patterns
    PHASE_PATTERNS = {
        "comprehension": [
            # Docstrings and documentation
            (r'"""[\s\S]*?"""', "docstring", 0.8),
            (r"'''[\s\S]*?'''", "docstring", 0.8),
            # Purpose/requirement comments
            (r"#.*(?:purpose|requirement|input|output|goal)", "purpose_comment", 0.7),
            (r"//.*(?:purpose|requirement|input|output|goal)", "purpose_comment", 0.7),
            # Type annotations
            (r"def\s+\w+\s*\([^)]*:\s*\w+", "type_hint", 0.5),
            (r":\s*(?:int|str|float|bool|List|Dict|Optional)", "type_hint", 0.5),
        ],
        "strategy": [
            # Approach documentation
            (r"#.*(?:approach|strategy|algorithm|method)", "approach_comment", 0.8),
            (r"#.*(?:selected|chose|decision|because)", "decision_comment", 0.7),
            (r"#.*(?:trade-?off|alternative|option)", "tradeoff_comment", 0.8),
            # Architecture patterns
            (r"class\s+\w+.*:", "class_definition", 0.5),
            (r"def\s+(?:setup|init|configure|create)", "setup_function", 0.6),
        ],
        "execution": [
            # Step markers
            (r"#\s*step\s*\d", "step_marker", 0.9),
            (r"#\s*\d+\.", "numbered_step", 0.8),
            (r"#.*(?:section|phase|part)\s*\d", "section_marker", 0.8),
            # Implementation patterns
            (r"for\s+\w+\s+in", "loop_construct", 0.4),
            (r"while\s+", "loop_construct", 0.4),
            (r"if\s+.*:", "conditional", 0.3),
        ],
        "review": [
            # Validation patterns
            (r"(?:assert|validate|check|verify)\s*\(", "validation_call", 0.8),
            (r"if\s+.*(?:is\s+)?(?:None|null|empty)", "null_check", 0.7),
            (r"if\s+(?:not\s+)?\w+:", "existence_check", 0.5),
            # Error handling
            (r"try\s*:", "try_block", 0.6),
            (r"except\s+\w+", "exception_handler", 0.7),
            (r"raise\s+\w+", "raise_statement", 0.6),
            # Edge case comments
            (r"#.*(?:edge\s*case|boundary|corner\s*case)", "edge_case_comment", 0.9),
        ],
        "refinement": [
            # Optimization indicators
            (r"#.*(?:optimi|improve|enhance|refactor)", "optimization_comment", 0.8),
            (r"#.*(?:TODO|FIXME|HACK)", "todo_marker", 0.3),  # Low = incomplete refinement
            # Clean code patterns
            (r"@(?:cache|lru_cache|memoize)", "caching_decorator", 0.8),
            (r"lambda\s+", "lambda_usage", 0.4),
            # Documentation completeness
            (r"Returns:\s*\n\s+\w+", "return_docs", 0.6),
            (r"Raises:\s*\n\s+\w+", "raises_docs", 0.6),
        ],
    }

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Reasoning Analyzer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.min_confidence = self.config.get("min_confidence", 0.5)

    def find_reasoning_patterns(
        self,
        code: str,
        language: str = "python"
    ) -> List[ReasoningPattern]:
        """
        Find all reasoning patterns in the code.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            List of detected ReasoningPattern objects
        """
        patterns_found = []
        lines = code.split("\n")

        for phase, patterns in self.PHASE_PATTERNS.items():
            for pattern, pattern_type, confidence in patterns:
                # Adjust patterns for language if needed
                adjusted_pattern = self._adjust_pattern_for_language(
                    pattern, language
                )

                matches = re.finditer(adjusted_pattern, code, re.IGNORECASE)
                for match in matches:
                    start_line = code[:match.start()].count("\n") + 1
                    end_line = code[:match.end()].count("\n") + 1

                    patterns_found.append(ReasoningPattern(
                        phase=phase,
                        pattern_type=pattern_type,
                        location=(start_line, end_line),
                        confidence=confidence,
                        evidence=match.group()[:100]  # First 100 chars
                    ))

        return patterns_found

    def calculate_phase_coverage(
        self,
        patterns: List[ReasoningPattern]
    ) -> Dict[str, Dict]:
        """
        Calculate coverage metrics for each reasoning phase.

        Args:
            patterns: List of detected patterns

        Returns:
            Dictionary with coverage metrics per phase
        """
        phase_coverage = {}

        for phase in self.PHASE_PATTERNS.keys():
            phase_patterns = [p for p in patterns if p.phase == phase]

            # Calculate metrics
            count = len(phase_patterns)
            avg_confidence = (
                sum(p.confidence for p in phase_patterns) / count
                if count > 0 else 0
            )

            # Determine quality level
            if count >= 3 and avg_confidence >= 0.7:
                quality = "strong"
            elif count >= 1 and avg_confidence >= 0.5:
                quality = "moderate"
            elif count >= 1:
                quality = "weak"
            else:
                quality = "absent"

            phase_coverage[phase] = {
                "pattern_count": count,
                "average_confidence": round(avg_confidence, 2),
                "quality": quality,
                "patterns": [p.pattern_type for p in phase_patterns]
            }

        return phase_coverage

    def analyze_logical_flow(self, code: str, language: str = "python") -> Dict:
        """
        Analyze the logical flow of the code.

        Checks for:
        - Linear progression
        - Clear entry/exit points
        - Logical grouping
        - Control flow complexity

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with flow analysis results
        """
        lines = code.split("\n")

        # Find entry points
        entry_patterns = {
            "python": r"if\s+__name__\s*==\s*['\"]__main__['\"]",
            "javascript": r"(?:module\.exports|export\s+default)",
            "default": r"(?:main|start|run|init)\s*\("
        }

        entry_pattern = entry_patterns.get(language, entry_patterns["default"])
        has_clear_entry = bool(re.search(entry_pattern, code))

        # Analyze control flow
        control_structures = {
            "if_statements": len(re.findall(r"\bif\s+", code)),
            "loops": len(re.findall(r"\b(?:for|while)\s+", code)),
            "functions": len(re.findall(r"\bdef\s+", code)),
            "classes": len(re.findall(r"\bclass\s+", code)),
            "returns": len(re.findall(r"\breturn\s+", code)),
        }

        # Calculate nesting depth
        max_depth = self._calculate_max_nesting(code, language)

        # Assess flow quality
        flow_score = 10  # Start at 10/10

        if not has_clear_entry:
            flow_score -= 1

        if max_depth > 4:
            flow_score -= 2
        elif max_depth > 3:
            flow_score -= 1

        # High complexity penalty
        total_control = sum(control_structures.values())
        lines_count = len(lines)
        complexity_ratio = total_control / max(lines_count, 1)

        if complexity_ratio > 0.3:
            flow_score -= 2
        elif complexity_ratio > 0.2:
            flow_score -= 1

        return {
            "has_clear_entry": has_clear_entry,
            "control_structures": control_structures,
            "max_nesting_depth": max_depth,
            "flow_score": max(0, flow_score),
            "assessment": self._assess_flow(flow_score)
        }

    def detect_reasoning_gaps(
        self,
        code: str,
        language: str = "python"
    ) -> List[Dict]:
        """
        Detect gaps in reasoning methodology.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            List of identified reasoning gaps
        """
        gaps = []
        patterns = self.find_reasoning_patterns(code, language)
        coverage = self.calculate_phase_coverage(patterns)

        # Check each phase for gaps
        gap_checks = {
            "comprehension": {
                "check": lambda c: c["quality"] in ["absent", "weak"],
                "message": "Insufficient problem documentation",
                "suggestion": "Add module docstring and function documentation"
            },
            "strategy": {
                "check": lambda c: c["quality"] in ["absent", "weak"],
                "message": "Missing approach/strategy documentation",
                "suggestion": "Document why this approach was chosen"
            },
            "execution": {
                "check": lambda c: c["pattern_count"] < 2,
                "message": "Limited execution step documentation",
                "suggestion": "Add step markers (# Step 1: ...)"
            },
            "review": {
                "check": lambda c: c["quality"] in ["absent", "weak"],
                "message": "Insufficient verification/validation",
                "suggestion": "Add input validation and edge case handling"
            },
            "refinement": {
                "check": lambda c: "todo_marker" in c["patterns"],
                "message": "Incomplete refinement (TODOs present)",
                "suggestion": "Address TODO items and polish code"
            }
        }

        for phase, check in gap_checks.items():
            phase_coverage = coverage.get(phase, {"quality": "absent"})
            if check["check"](phase_coverage):
                gaps.append({
                    "phase": phase,
                    "gap_type": check["message"],
                    "suggestion": check["suggestion"],
                    "current_quality": phase_coverage.get("quality", "absent")
                })

        return gaps

    def map_code_to_phases(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Map code sections to reasoning phases.

        Creates a visual map of which code lines correspond to
        which reasoning phase.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary mapping phases to line ranges
        """
        patterns = self.find_reasoning_patterns(code, language)

        phase_map = {phase: [] for phase in self.PHASE_PATTERNS.keys()}

        for pattern in patterns:
            if pattern.confidence >= self.min_confidence:
                phase_map[pattern.phase].append(pattern.location)

        # Merge overlapping ranges
        for phase in phase_map:
            phase_map[phase] = self._merge_ranges(phase_map[phase])

        return phase_map

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _adjust_pattern_for_language(
        self,
        pattern: str,
        language: str
    ) -> str:
        """Adjust regex pattern for specific language syntax."""
        if language in ["javascript", "typescript", "java", "c", "cpp", "go"]:
            # Convert Python comment syntax to C-style
            pattern = pattern.replace("#", "//")

        if language in ["javascript", "typescript"]:
            # Adjust function patterns
            pattern = pattern.replace(r"def\s+", r"(?:function\s+|const\s+\w+\s*=)")

        return pattern

    def _calculate_max_nesting(self, code: str, language: str) -> int:
        """Calculate maximum nesting depth in code."""
        max_depth = 0
        current_depth = 0

        indent_pattern = r"^(\s*)"

        for line in code.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            indent_match = re.match(indent_pattern, line)
            if indent_match:
                indent = len(indent_match.group(1))
                # Assuming 4-space indent
                depth = indent // 4
                max_depth = max(max_depth, depth)

        return max_depth

    def _assess_flow(self, score: int) -> str:
        """Assess flow quality from score."""
        if score >= 8:
            return "excellent"
        elif score >= 6:
            return "good"
        elif score >= 4:
            return "adequate"
        else:
            return "needs_improvement"

    def _merge_ranges(
        self,
        ranges: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """Merge overlapping line ranges."""
        if not ranges:
            return []

        sorted_ranges = sorted(ranges, key=lambda x: x[0])
        merged = [sorted_ranges[0]]

        for current in sorted_ranges[1:]:
            prev = merged[-1]
            if current[0] <= prev[1] + 1:
                merged[-1] = (prev[0], max(prev[1], current[1]))
            else:
                merged.append(current)

        return merged
