"""
Documentation Analyzer

Analyzes code documentation quality and completeness.

Requirements:
- Evaluate docstring presence and quality
- Check comment coverage
- Assess documentation completeness
- Identify documentation gaps
"""

import re
from typing import Dict, List, Optional, Tuple


class DocumentationAnalyzer:
    """
    Analyzes documentation quality in code.

    Evaluates:
    - Module/file documentation
    - Function/method docstrings
    - Class documentation
    - Inline comments
    - Parameter documentation
    - Return value documentation

    Example:
        >>> analyzer = DocumentationAnalyzer()
        >>> result = analyzer.analyze_docstrings(code)
        >>> print(f"Coverage: {result['documented_functions_ratio']}")
    """

    # Docstring patterns by language
    DOCSTRING_PATTERNS = {
        "python": {
            "module_doc": r'^(?:\s*#[^\n]*\n)*\s*(?:"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')',
            "func_doc": r'def\s+\w+[^:]+:\s*\n\s*(?:"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')',
            "class_doc": r'class\s+\w+[^:]*:\s*\n\s*(?:"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')',
        },
        "javascript": {
            "module_doc": r'^(?:\s*/\*\*[\s\S]*?\*/|\s*//[^\n]*\n)+',
            "func_doc": r'/\*\*[\s\S]*?\*/\s*\n\s*(?:function|const|let|var)',
            "class_doc": r'/\*\*[\s\S]*?\*/\s*\n\s*class',
        },
        "java": {
            "module_doc": r'^(?:\s*/\*\*[\s\S]*?\*/)',
            "func_doc": r'/\*\*[\s\S]*?\*/\s*\n\s*(?:public|private|protected)',
            "class_doc": r'/\*\*[\s\S]*?\*/\s*\n\s*(?:public\s+)?class',
        }
    }

    # Quality indicators in docstrings
    QUALITY_INDICATORS = {
        "has_description": r"[A-Z][^.]*\.",
        "has_args": r"(?:Args|Parameters|Params|@param):",
        "has_returns": r"(?:Returns|@returns|@return):",
        "has_raises": r"(?:Raises|Throws|@throws|@raises):",
        "has_example": r"(?:Example|Examples|Usage|@example):",
        "has_type_info": r":\s*(?:int|str|float|bool|List|Dict|Optional|number|string)",
    }

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Documentation Analyzer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    def analyze_docstrings(self, code: str, language: str = "python") -> Dict:
        """
        Analyze docstring presence and quality.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with docstring analysis results
        """
        patterns = self.DOCSTRING_PATTERNS.get(
            language,
            self.DOCSTRING_PATTERNS["python"]
        )

        # Check module documentation
        has_module_doc = bool(re.match(patterns["module_doc"], code))

        # Find all functions
        func_pattern = self._get_function_pattern(language)
        all_functions = re.findall(func_pattern, code)

        # Find documented functions
        doc_func_pattern = patterns["func_doc"]
        documented_functions = len(re.findall(doc_func_pattern, code))

        # Calculate ratio
        total_functions = len(all_functions)
        ratio = (
            documented_functions / total_functions
            if total_functions > 0 else 1.0
        )

        # Analyze documentation quality
        docstrings = self._extract_docstrings(code, language)
        quality_scores = [
            self._assess_docstring_quality(doc)
            for doc in docstrings
        ]
        avg_quality = (
            sum(quality_scores) / len(quality_scores)
            if quality_scores else 0
        )

        return {
            "has_module_doc": has_module_doc,
            "total_functions": total_functions,
            "documented_functions": documented_functions,
            "documented_functions_ratio": round(ratio, 2),
            "docstring_count": len(docstrings),
            "average_quality": round(avg_quality, 2),
            "quality_assessment": self._assess_overall_quality(ratio, avg_quality)
        }

    def analyze_comments(self, code: str, language: str = "python") -> Dict:
        """
        Analyze inline comment coverage.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with comment analysis results
        """
        lines = code.split("\n")
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not self._is_comment_line(l, language)])

        # Count different comment types
        inline_comments = 0
        block_comments = 0
        section_markers = 0

        for line in lines:
            stripped = line.strip()

            # Section markers (dividers)
            if re.match(r"#\s*={3,}|#\s*-{3,}|//\s*={3,}", stripped):
                section_markers += 1
            # Regular comments
            elif self._is_comment_line(stripped, language):
                inline_comments += 1

        # Count block comments
        block_pattern = r'/\*[\s\S]*?\*/' if language != "python" else r'"""[\s\S]*?"""'
        block_comments = len(re.findall(block_pattern, code))

        # Calculate comment density
        total_comments = inline_comments + block_comments
        comment_ratio = total_comments / max(code_lines, 1)

        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "inline_comments": inline_comments,
            "block_comments": block_comments,
            "section_markers": section_markers,
            "comment_ratio": round(comment_ratio, 3),
            "has_section_organization": section_markers >= 2,
            "assessment": self._assess_comment_coverage(comment_ratio, section_markers)
        }

    def find_documentation_gaps(
        self,
        code: str,
        language: str = "python"
    ) -> List[Dict]:
        """
        Find functions/classes missing documentation.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            List of documentation gaps with locations
        """
        gaps = []

        # Find all function definitions
        func_pattern = self._get_function_pattern(language)
        doc_pattern = self.DOCSTRING_PATTERNS.get(
            language, self.DOCSTRING_PATTERNS["python"]
        )["func_doc"]

        # Get function positions
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1) if match.groups() else "unknown"
            func_start = match.start()

            # Check if there's a docstring after this function
            func_end = code.find(":", func_start)
            if func_end != -1:
                # Look for docstring in next ~100 chars
                after_def = code[func_end:func_end + 100]
                has_doc = bool(re.search(r':\s*\n\s*(?:"""|\'\'\')' , after_def))

                if not has_doc:
                    line_num = code[:func_start].count("\n") + 1
                    gaps.append({
                        "type": "function",
                        "name": func_name,
                        "line": line_num,
                        "suggestion": f"Add docstring to function '{func_name}'"
                    })

        # Find undocumented classes
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            class_start = match.start()

            # Check for class docstring
            class_end = code.find(":", class_start)
            if class_end != -1:
                after_class = code[class_end:class_end + 100]
                has_doc = bool(re.search(r':\s*\n\s*(?:"""|\'\'\')' , after_class))

                if not has_doc:
                    line_num = code[:class_start].count("\n") + 1
                    gaps.append({
                        "type": "class",
                        "name": class_name,
                        "line": line_num,
                        "suggestion": f"Add docstring to class '{class_name}'"
                    })

        return gaps

    def analyze_docstring_content(self, docstring: str) -> Dict:
        """
        Analyze the content quality of a single docstring.

        Args:
            docstring: The docstring text to analyze

        Returns:
            Dictionary with content analysis
        """
        indicators_found = {}

        for indicator, pattern in self.QUALITY_INDICATORS.items():
            indicators_found[indicator] = bool(
                re.search(pattern, docstring, re.IGNORECASE)
            )

        # Calculate completeness score
        score = sum(indicators_found.values()) / len(indicators_found)

        # Assess sections present
        sections = []
        if indicators_found["has_description"]:
            sections.append("description")
        if indicators_found["has_args"]:
            sections.append("parameters")
        if indicators_found["has_returns"]:
            sections.append("returns")
        if indicators_found["has_raises"]:
            sections.append("exceptions")
        if indicators_found["has_example"]:
            sections.append("examples")

        return {
            "indicators": indicators_found,
            "sections_present": sections,
            "completeness_score": round(score, 2),
            "word_count": len(docstring.split()),
            "assessment": self._assess_docstring_completeness(score, len(sections))
        }

    def suggest_documentation(
        self,
        code: str,
        language: str = "python"
    ) -> List[Dict]:
        """
        Generate documentation suggestions for the code.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            List of documentation suggestions
        """
        suggestions = []

        # Check module documentation
        analysis = self.analyze_docstrings(code, language)

        if not analysis["has_module_doc"]:
            suggestions.append({
                "priority": "high",
                "type": "module",
                "location": "top of file",
                "suggestion": "Add module docstring explaining the file's purpose",
                "template": self._get_module_doc_template(language)
            })

        # Get documentation gaps
        gaps = self.find_documentation_gaps(code, language)
        for gap in gaps:
            suggestions.append({
                "priority": "medium",
                "type": gap["type"],
                "location": f"line {gap['line']}",
                "suggestion": gap["suggestion"],
                "template": self._get_docstring_template(gap["type"], language)
            })

        # Check for improved existing docs
        if analysis["average_quality"] < 0.5 and analysis["docstring_count"] > 0:
            suggestions.append({
                "priority": "low",
                "type": "enhancement",
                "location": "existing docstrings",
                "suggestion": "Enhance existing docstrings with Args, Returns, and Examples sections",
                "template": None
            })

        return suggestions

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _get_function_pattern(self, language: str) -> str:
        """Get regex pattern for function definitions."""
        patterns = {
            "python": r"def\s+(\w+)\s*\(",
            "javascript": r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()",
            "typescript": r"(?:function\s+(\w+)|(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?\()",
            "java": r"(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(",
            "go": r"func\s+(\w+)\s*\(",
        }
        return patterns.get(language, patterns["python"])

    def _extract_docstrings(self, code: str, language: str) -> List[str]:
        """Extract all docstrings from code."""
        if language == "python":
            pattern = r'"""([\s\S]*?)"""|\'\'\'([\s\S]*?)\'\'\''
        else:
            pattern = r'/\*\*([\s\S]*?)\*/'

        matches = re.findall(pattern, code)

        # Flatten and filter empty
        docstrings = []
        for match in matches:
            if isinstance(match, tuple):
                doc = next((m for m in match if m), "")
            else:
                doc = match
            if doc.strip():
                docstrings.append(doc.strip())

        return docstrings

    def _assess_docstring_quality(self, docstring: str) -> float:
        """Assess quality of a single docstring (0-1)."""
        if not docstring:
            return 0

        score = 0.2  # Base score for having any docstring

        # Check for quality indicators
        for indicator, pattern in self.QUALITY_INDICATORS.items():
            if re.search(pattern, docstring, re.IGNORECASE):
                score += 0.15

        # Length bonus
        word_count = len(docstring.split())
        if word_count >= 10:
            score += 0.1
        if word_count >= 30:
            score += 0.1

        return min(1.0, score)

    def _assess_overall_quality(self, ratio: float, avg_quality: float) -> str:
        """Assess overall documentation quality."""
        combined = (ratio * 0.6) + (avg_quality * 0.4)

        if combined >= 0.8:
            return "excellent"
        elif combined >= 0.6:
            return "good"
        elif combined >= 0.4:
            return "adequate"
        elif combined >= 0.2:
            return "needs_improvement"
        else:
            return "poor"

    def _is_comment_line(self, line: str, language: str) -> bool:
        """Check if line is a comment."""
        stripped = line.strip()

        if language == "python":
            return stripped.startswith("#")
        elif language in ["javascript", "typescript", "java", "go", "c", "cpp"]:
            return stripped.startswith("//") or stripped.startswith("/*")
        else:
            return stripped.startswith("#") or stripped.startswith("//")

    def _assess_comment_coverage(
        self,
        ratio: float,
        section_markers: int
    ) -> str:
        """Assess comment coverage quality."""
        if ratio >= 0.15 and section_markers >= 2:
            return "excellent"
        elif ratio >= 0.1 or section_markers >= 1:
            return "good"
        elif ratio >= 0.05:
            return "adequate"
        else:
            return "sparse"

    def _assess_docstring_completeness(
        self,
        score: float,
        section_count: int
    ) -> str:
        """Assess docstring completeness."""
        if score >= 0.8 and section_count >= 4:
            return "comprehensive"
        elif score >= 0.5 and section_count >= 2:
            return "good"
        elif score >= 0.3:
            return "basic"
        else:
            return "minimal"

    def _get_module_doc_template(self, language: str) -> str:
        """Get module documentation template."""
        if language == "python":
            return '''"""
Module Name

Brief description of what this module does.

Requirements:
- Requirement 1
- Requirement 2

Approach: Description of the chosen approach
"""'''
        else:
            return '''/**
 * Module Name
 *
 * Brief description of what this module does.
 *
 * Requirements:
 * - Requirement 1
 * - Requirement 2
 */'''

    def _get_docstring_template(self, doc_type: str, language: str) -> str:
        """Get docstring template for function/class."""
        if language == "python":
            if doc_type == "function":
                return '''"""
Brief description of function.

Args:
    param1: Description of param1
    param2: Description of param2

Returns:
    Description of return value

Raises:
    ExceptionType: When this exception is raised

Example:
    >>> function_name(arg1, arg2)
    expected_result
"""'''
            else:  # class
                return '''"""
Brief description of class.

Attributes:
    attr1: Description of attr1
    attr2: Description of attr2

Example:
    >>> obj = ClassName()
    >>> obj.method()
"""'''
        else:
            return '''/**
 * Brief description.
 *
 * @param {Type} param1 - Description
 * @returns {Type} Description
 */'''
