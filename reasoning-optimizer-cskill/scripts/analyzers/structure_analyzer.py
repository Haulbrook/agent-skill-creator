"""
Structure Analyzer

Analyzes code structure, organization, and quality metrics.

Requirements:
- Assess code organization and modularity
- Detect consistency issues
- Find magic values and code duplication
- Estimate complexity metrics
"""

import re
from typing import Dict, List, Optional, Tuple
from collections import Counter


class StructureAnalyzer:
    """
    Analyzes code structure and organization quality.

    Evaluates:
    - Modularity and organization
    - Code consistency
    - Magic values (unexplained constants)
    - Code duplication
    - Complexity metrics
    - Error handling patterns

    Example:
        >>> analyzer = StructureAnalyzer()
        >>> structure = analyzer.analyze_structure(code)
        >>> print(f"Well organized: {structure['is_well_organized']}")
    """

    # Common magic number patterns to ignore
    COMMON_CONSTANTS = {0, 1, 2, -1, 100, 1000}
    COMMON_STRINGS = {"", " ", "\n", "\t", ",", ".", ":", "/", "\\"}

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Structure Analyzer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    def analyze_structure(self, code: str, language: str = "python") -> Dict:
        """
        Analyze overall code structure.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with structure analysis results
        """
        lines = code.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]

        # Count structural elements
        functions = self._count_functions(code, language)
        classes = self._count_classes(code, language)
        imports = self._count_imports(code, language)

        # Calculate metrics
        total_lines = len(lines)
        code_lines = len(non_empty_lines)

        # Assess organization
        is_well_organized = self._assess_organization(
            functions=functions,
            classes=classes,
            total_lines=total_lines,
            code=code,
            language=language
        )

        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "is_well_organized": is_well_organized,
            "structure_score": self._calculate_structure_score(
                functions, classes, code_lines
            )
        }

    def analyze_types(self, code: str, language: str = "python") -> Dict:
        """
        Analyze type annotation usage.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with type analysis results
        """
        type_patterns = {
            "python": {
                "param_type": r":\s*(?:int|str|float|bool|List|Dict|Optional|Union|Any|Tuple|Set)\b",
                "return_type": r"->\s*(?:int|str|float|bool|List|Dict|Optional|Union|Any|Tuple|Set|None)\b",
                "type_comment": r"#\s*type:\s*",
            },
            "typescript": {
                "param_type": r":\s*(?:number|string|boolean|Array|object|any|void|never)\b",
                "return_type": r":\s*(?:number|string|boolean|Array|object|any|void|never|Promise)\b",
            },
            "java": {
                "param_type": r"(?:int|String|boolean|long|double|float|Object|List|Map)\s+\w+",
            }
        }

        patterns = type_patterns.get(language, type_patterns.get("python"))

        type_annotations = 0
        for pattern in patterns.values():
            type_annotations += len(re.findall(pattern, code))

        # Count function definitions
        func_count = self._count_functions(code, language)

        return {
            "has_type_hints": type_annotations > 0,
            "type_annotation_count": type_annotations,
            "coverage_ratio": (
                type_annotations / max(func_count * 2, 1)
                if func_count > 0 else 0
            )
        }

    def check_consistency(self, code: str, language: str = "python") -> Dict:
        """
        Check code consistency.

        Evaluates:
        - Naming conventions
        - Indentation consistency
        - Quote style consistency
        - Spacing patterns

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with consistency score and issues
        """
        issues = []
        score = 1.0  # Start perfect

        # Check naming conventions
        naming_issues = self._check_naming_consistency(code, language)
        if naming_issues:
            issues.extend(naming_issues)
            score -= 0.1 * len(naming_issues)

        # Check indentation
        indent_issues = self._check_indentation_consistency(code)
        if indent_issues:
            issues.extend(indent_issues)
            score -= 0.15 * len(indent_issues)

        # Check quote style
        quote_issues = self._check_quote_consistency(code, language)
        if quote_issues:
            issues.extend(quote_issues)
            score -= 0.05 * len(quote_issues)

        return {
            "score": max(0, score),
            "issues": issues,
            "is_consistent": score >= 0.8
        }

    def find_magic_values(self, code: str, language: str = "python") -> Dict:
        """
        Find unexplained magic numbers and strings.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with magic value analysis
        """
        magic_numbers = []
        magic_strings = []

        # Find numeric literals
        number_pattern = r"(?<![a-zA-Z_])(\d+(?:\.\d+)?)"
        for match in re.finditer(number_pattern, code):
            num_str = match.group(1)
            try:
                num = float(num_str) if "." in num_str else int(num_str)
                if num not in self.COMMON_CONSTANTS:
                    # Check if it's assigned to a constant
                    line_start = code.rfind("\n", 0, match.start()) + 1
                    line = code[line_start:match.end()]
                    if not re.match(r"^\s*[A-Z_]+\s*=", line):
                        magic_numbers.append({
                            "value": num,
                            "position": match.start()
                        })
            except ValueError:
                pass

        # Find string literals (excluding docstrings)
        string_pattern = r'(?<!["\'])(["\'])(?!\1\1)([^"\'\\]*(?:\\.[^"\'\\]*)*)(\1)'
        for match in re.finditer(string_pattern, code):
            string_val = match.group(2)
            if (
                string_val not in self.COMMON_STRINGS and
                len(string_val) > 3 and
                not string_val.startswith("http") and
                not re.match(r"^[A-Z_]+$", string_val)  # Not a constant name
            ):
                magic_strings.append({
                    "value": string_val[:50],
                    "position": match.start()
                })

        return {
            "count": len(magic_numbers) + len(magic_strings),
            "magic_numbers": magic_numbers[:10],  # Limit output
            "magic_strings": magic_strings[:10],
            "severity": self._assess_magic_severity(
                len(magic_numbers) + len(magic_strings),
                len(code.split("\n"))
            )
        }

    def analyze_error_handling(self, code: str, language: str = "python") -> Dict:
        """
        Analyze error handling patterns.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with error handling analysis
        """
        error_patterns = {
            "python": {
                "try_block": r"\btry\s*:",
                "except_generic": r"\bexcept\s*:",
                "except_specific": r"\bexcept\s+\w+",
                "raise": r"\braise\s+\w+",
                "finally": r"\bfinally\s*:",
            },
            "javascript": {
                "try_block": r"\btry\s*\{",
                "catch_generic": r"\bcatch\s*\(\s*\w+\s*\)",
                "throw": r"\bthrow\s+",
                "finally": r"\bfinally\s*\{",
            }
        }

        patterns = error_patterns.get(language, error_patterns["python"])

        results = {}
        for name, pattern in patterns.items():
            results[name] = len(re.findall(pattern, code))

        has_error_handling = results.get("try_block", 0) > 0
        has_specific = results.get("except_specific", 0) > 0

        return {
            "has_error_handling": has_error_handling,
            "has_specific_exceptions": has_specific,
            "try_blocks": results.get("try_block", 0),
            "raises": results.get("raise", 0) or results.get("throw", 0),
            "quality": self._assess_error_handling_quality(results)
        }

    def estimate_complexity(self, code: str, language: str = "python") -> Dict:
        """
        Estimate cyclomatic complexity.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with complexity metrics
        """
        # Count decision points
        decision_patterns = [
            r"\bif\b",
            r"\belif\b",
            r"\belse\b",
            r"\bfor\b",
            r"\bwhile\b",
            r"\band\b",
            r"\bor\b",
            r"\btry\b",
            r"\bexcept\b",
            r"\bcase\b",
        ]

        total_complexity = 1  # Base complexity
        for pattern in decision_patterns:
            total_complexity += len(re.findall(pattern, code))

        # Count functions for average
        func_count = max(self._count_functions(code, language), 1)
        avg_complexity = total_complexity / func_count

        return {
            "total": total_complexity,
            "average": round(avg_complexity, 2),
            "function_count": func_count,
            "assessment": self._assess_complexity(avg_complexity)
        }

    def detect_duplication(self, code: str, language: str = "python") -> Dict:
        """
        Detect potential code duplication.

        Uses a simple n-gram approach to find repeated patterns.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with duplication metrics
        """
        lines = [l.strip() for l in code.split("\n") if l.strip()]

        # Skip very short code
        if len(lines) < 10:
            return {"ratio": 0, "duplicates": [], "assessment": "clean"}

        # Find 3-line sequences (n-grams)
        ngrams = []
        for i in range(len(lines) - 2):
            ngram = tuple(lines[i:i+3])
            # Skip common patterns
            if not self._is_trivial_pattern(ngram):
                ngrams.append(ngram)

        # Count duplicates
        ngram_counts = Counter(ngrams)
        duplicates = [
            {"pattern": list(k), "count": v}
            for k, v in ngram_counts.items()
            if v > 1
        ]

        duplicate_lines = sum(
            d["count"] * 3 for d in duplicates
        )
        ratio = duplicate_lines / max(len(lines), 1)

        return {
            "ratio": round(ratio, 3),
            "duplicates": duplicates[:5],  # Top 5
            "assessment": self._assess_duplication(ratio)
        }

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _count_functions(self, code: str, language: str) -> int:
        """Count function definitions."""
        patterns = {
            "python": r"\bdef\s+\w+\s*\(",
            "javascript": r"(?:function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\()",
            "typescript": r"(?:function\s+\w+|(?:const|let)\s+\w+\s*=\s*(?:async\s*)?\()",
            "java": r"(?:public|private|protected)?\s*(?:static)?\s*\w+\s+\w+\s*\(",
            "go": r"\bfunc\s+\w+\s*\(",
        }
        pattern = patterns.get(language, patterns["python"])
        return len(re.findall(pattern, code))

    def _count_classes(self, code: str, language: str) -> int:
        """Count class definitions."""
        patterns = {
            "python": r"\bclass\s+\w+",
            "javascript": r"\bclass\s+\w+",
            "typescript": r"\bclass\s+\w+",
            "java": r"\bclass\s+\w+",
        }
        pattern = patterns.get(language, patterns["python"])
        return len(re.findall(pattern, code))

    def _count_imports(self, code: str, language: str) -> int:
        """Count import statements."""
        patterns = {
            "python": r"^(?:import|from)\s+",
            "javascript": r"^(?:import|require)\s*\(",
            "typescript": r"^import\s+",
            "java": r"^import\s+",
            "go": r"^import\s+",
        }
        pattern = patterns.get(language, patterns["python"])
        return len(re.findall(pattern, code, re.MULTILINE))

    def _assess_organization(
        self,
        functions: int,
        classes: int,
        total_lines: int,
        code: str,
        language: str
    ) -> bool:
        """Assess if code is well organized."""
        # Very short code is hard to assess
        if total_lines < 20:
            return True

        # Check function-to-lines ratio
        if functions > 0:
            avg_func_length = total_lines / functions
            if avg_func_length > 50:  # Functions too long
                return False

        # Check for some structure
        has_structure = functions > 0 or classes > 0

        # Check for section comments
        section_markers = len(re.findall(r"^#\s*={3,}|^#\s*-{3,}", code, re.MULTILINE))

        return has_structure or section_markers > 0

    def _calculate_structure_score(
        self,
        functions: int,
        classes: int,
        code_lines: int
    ) -> int:
        """Calculate structure quality score (0-10)."""
        score = 5  # Base score

        if code_lines < 10:
            return 10  # Too small to assess

        # Function presence
        if functions > 0:
            score += 2

        # Good function size
        if functions > 0:
            avg_size = code_lines / functions
            if 10 <= avg_size <= 30:
                score += 2
            elif avg_size <= 50:
                score += 1

        # Class usage for larger code
        if code_lines > 100 and classes > 0:
            score += 1

        return min(10, score)

    def _check_naming_consistency(
        self,
        code: str,
        language: str
    ) -> List[str]:
        """Check naming convention consistency."""
        issues = []

        # Find function names
        func_pattern = r"def\s+(\w+)" if language == "python" else r"function\s+(\w+)"
        func_names = re.findall(func_pattern, code)

        # Check for mixed styles
        snake_case = [n for n in func_names if "_" in n and n.islower()]
        camel_case = [n for n in func_names if n[0].islower() and any(c.isupper() for c in n)]

        if snake_case and camel_case:
            issues.append("Mixed naming conventions (snake_case and camelCase)")

        return issues

    def _check_indentation_consistency(self, code: str) -> List[str]:
        """Check indentation consistency."""
        issues = []
        lines = code.split("\n")

        # Detect indent style
        spaces = 0
        tabs = 0

        for line in lines:
            if line.startswith("    "):
                spaces += 1
            elif line.startswith("\t"):
                tabs += 1

        if spaces > 0 and tabs > 0:
            issues.append("Mixed tabs and spaces for indentation")

        return issues

    def _check_quote_consistency(self, code: str, language: str) -> List[str]:
        """Check quote style consistency."""
        issues = []

        single_quotes = len(re.findall(r"'[^']*'", code))
        double_quotes = len(re.findall(r'"[^"]*"', code))

        # Ignore if very small difference
        total = single_quotes + double_quotes
        if total > 10:
            ratio = min(single_quotes, double_quotes) / total
            if 0.3 < ratio < 0.7:
                issues.append("Inconsistent quote style")

        return issues

    def _assess_magic_severity(self, count: int, line_count: int) -> str:
        """Assess severity of magic value usage."""
        ratio = count / max(line_count, 1)
        if ratio < 0.01:
            return "low"
        elif ratio < 0.05:
            return "medium"
        else:
            return "high"

    def _assess_error_handling_quality(self, results: Dict) -> str:
        """Assess error handling quality."""
        has_try = results.get("try_block", 0) > 0
        has_specific = results.get("except_specific", 0) > 0

        if has_try and has_specific:
            return "good"
        elif has_try:
            return "basic"
        else:
            return "none"

    def _assess_complexity(self, avg: float) -> str:
        """Assess complexity level."""
        if avg <= 5:
            return "low"
        elif avg <= 10:
            return "moderate"
        elif avg <= 20:
            return "high"
        else:
            return "very_high"

    def _assess_duplication(self, ratio: float) -> str:
        """Assess duplication level."""
        if ratio < 0.05:
            return "clean"
        elif ratio < 0.15:
            return "some_duplication"
        else:
            return "significant_duplication"

    def _is_trivial_pattern(self, ngram: Tuple[str, ...]) -> bool:
        """Check if pattern is trivial (e.g., closing braces)."""
        trivial_patterns = {
            ("}", "", ""),
            ("", "}", ""),
            ("pass", "", ""),
            ("return", "", ""),
        }

        # Check for empty/whitespace only
        if all(not line.strip() for line in ngram):
            return True

        # Check for common trivial patterns
        normalized = tuple(line.strip()[:10] for line in ngram)
        if normalized in trivial_patterns:
            return True

        return False
