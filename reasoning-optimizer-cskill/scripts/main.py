"""
Reasoning Optimizer - Main Entry Point

This module orchestrates the reasoning analysis, reconstruction, and checkpoint
functionality for evaluating code against the 5-Phase Reasoning Model.

Requirements:
- Analyze code for reasoning gaps
- Score code against reasoning phases
- Rebuild code with proper methodology
- Create and manage checkpoints

Approach: Modular architecture with phase-specific analyzers
Selected because: Each reasoning phase requires specialized analysis
"""

from typing import Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import json
import re

from .analyzers.reasoning_analyzer import ReasoningAnalyzer
from .analyzers.structure_analyzer import StructureAnalyzer
from .analyzers.documentation_analyzer import DocumentationAnalyzer
from .rebuilders.code_rebuilder import CodeRebuilder
from .checkpoints.checkpoint_manager import CheckpointManager


@dataclass
class AnalysisResult:
    """
    Container for reasoning analysis results.

    Attributes:
        overall_score: Total reasoning score (0-100)
        grade: Letter grade (A-F)
        phase_scores: Individual scores per reasoning phase
        issues: List of identified reasoning gaps
        recommendations: Priority-ordered improvement suggestions
        metadata: Additional analysis metadata
    """
    overall_score: int
    grade: str
    phase_scores: Dict[str, int]
    issues: List[Dict[str, str]]
    recommendations: List[str]
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass
class ReconstructionResult:
    """
    Container for code reconstruction results.

    Attributes:
        original_code: The input code before reconstruction
        reconstructed_code: The rebuilt code with reasoning
        documentation: Generated reasoning documentation
        before_score: Score before reconstruction
        after_score: Score after reconstruction
        changes_made: List of changes applied
    """
    original_code: str
    reconstructed_code: str
    documentation: str
    before_score: int
    after_score: int
    changes_made: List[str]


class ReasoningOptimizer:
    """
    Main orchestrator for reasoning analysis and optimization.

    This class coordinates the analysis of code against the 5-Phase
    Reasoning Model, identifies gaps, and facilitates reconstruction.

    The 5 Phases:
        1. Comprehension - Understanding the problem
        2. Strategy - Planning the approach
        3. Execution - Implementing the solution
        4. Review - Verifying the output
        5. Refinement - Polishing the result

    Example:
        >>> optimizer = ReasoningOptimizer()
        >>> result = optimizer.analyze_code(code_string)
        >>> print(f"Score: {result.overall_score}/100")
    """

    # Phase weights (each phase = 20 points for balanced assessment)
    PHASE_WEIGHTS = {
        "comprehension": 20,
        "strategy": 20,
        "execution": 20,
        "review": 20,
        "refinement": 20
    }

    # Grade thresholds
    GRADE_THRESHOLDS = {
        90: "A",
        80: "B",
        70: "C",
        60: "D",
        0: "F"
    }

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Reasoning Optimizer.

        Args:
            config: Optional configuration dictionary
                - threshold: Minimum passing score (default: 70)
                - verbosity: Output detail level (default: "standard")
                - output_format: Report format (default: "markdown")
        """
        self.config = config or {}
        self.threshold = self.config.get("threshold", 70)
        self.verbosity = self.config.get("verbosity", "standard")
        self.output_format = self.config.get("output_format", "markdown")

        # Initialize sub-analyzers
        self.reasoning_analyzer = ReasoningAnalyzer()
        self.structure_analyzer = StructureAnalyzer()
        self.documentation_analyzer = DocumentationAnalyzer()
        self.code_rebuilder = CodeRebuilder()
        self.checkpoint_manager = CheckpointManager()

    def analyze_code(
        self,
        code: str,
        language: str = "python",
        context: Optional[str] = None
    ) -> AnalysisResult:
        """
        Perform comprehensive reasoning analysis on code.

        Args:
            code: Source code to analyze
            language: Programming language (default: "python")
            context: Optional context about the code's purpose

        Returns:
            AnalysisResult with scores, issues, and recommendations

        Edge Cases:
            - Empty code: Returns score of 0 with appropriate message
            - Invalid syntax: Still analyzes reasoning aspects
            - Very short code: Adjusts expectations accordingly
        """
        # Handle edge case: empty code
        if not code or not code.strip():
            return AnalysisResult(
                overall_score=0,
                grade="F",
                phase_scores={phase: 0 for phase in self.PHASE_WEIGHTS},
                issues=[{"phase": "all", "issue": "No code provided"}],
                recommendations=["Provide code to analyze"],
                metadata={"error": "empty_input"}
            )

        # Phase 1: Comprehension Analysis
        comprehension_result = self._analyze_comprehension(code, language, context)

        # Phase 2: Strategy Analysis
        strategy_result = self._analyze_strategy(code, language)

        # Phase 3: Execution Analysis
        execution_result = self._analyze_execution(code, language)

        # Phase 4: Review Analysis
        review_result = self._analyze_review(code, language)

        # Phase 5: Refinement Analysis
        refinement_result = self._analyze_refinement(code, language)

        # Aggregate results
        phase_scores = {
            "comprehension": comprehension_result["score"],
            "strategy": strategy_result["score"],
            "execution": execution_result["score"],
            "review": review_result["score"],
            "refinement": refinement_result["score"]
        }

        overall_score = sum(phase_scores.values())
        grade = self._calculate_grade(overall_score)

        # Collect all issues
        all_issues = (
            comprehension_result["issues"] +
            strategy_result["issues"] +
            execution_result["issues"] +
            review_result["issues"] +
            refinement_result["issues"]
        )

        # Generate prioritized recommendations
        recommendations = self._generate_recommendations(
            phase_scores, all_issues
        )

        return AnalysisResult(
            overall_score=overall_score,
            grade=grade,
            phase_scores=phase_scores,
            issues=all_issues,
            recommendations=recommendations,
            metadata={
                "language": language,
                "analyzed_at": datetime.now().isoformat(),
                "code_length": len(code),
                "line_count": len(code.splitlines())
            }
        )

    def analyze_file(self, file_path: Union[str, Path]) -> AnalysisResult:
        """
        Analyze a code file for reasoning quality.

        Args:
            file_path: Path to the code file

        Returns:
            AnalysisResult for the file

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file encoding is unsupported
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect language from extension
        language = self._detect_language(path.suffix)

        # Read file content
        code = path.read_text(encoding="utf-8")

        return self.analyze_code(code, language)

    def reconstruct_code(
        self,
        code: str,
        language: str = "python",
        target_score: int = 85
    ) -> ReconstructionResult:
        """
        Rebuild code with proper reasoning methodology.

        Args:
            code: Original code to reconstruct
            language: Programming language
            target_score: Target reasoning score (default: 85)

        Returns:
            ReconstructionResult with before/after comparison
        """
        # Analyze original
        before_analysis = self.analyze_code(code, language)

        # Extract intent
        intent = self.code_rebuilder.extract_intent(code, language)

        # Rebuild with reasoning
        reconstructed = self.code_rebuilder.rebuild(
            code=code,
            language=language,
            intent=intent,
            issues=before_analysis.issues
        )

        # Analyze reconstructed
        after_analysis = self.analyze_code(
            reconstructed["code"], language
        )

        return ReconstructionResult(
            original_code=code,
            reconstructed_code=reconstructed["code"],
            documentation=reconstructed["documentation"],
            before_score=before_analysis.overall_score,
            after_score=after_analysis.overall_score,
            changes_made=reconstructed["changes"]
        )

    def create_checkpoint(
        self,
        checkpoint_type: str,
        project_path: Optional[str] = None,
        code_path: Optional[str] = None
    ) -> Dict:
        """
        Create a reasoning checkpoint.

        Args:
            checkpoint_type: "pre", "mid", "post", or "release"
            project_path: Path to the project
            code_path: Optional specific code to analyze

        Returns:
            Checkpoint dictionary with analysis and status
        """
        return self.checkpoint_manager.create_checkpoint(
            checkpoint_type=checkpoint_type,
            project_path=project_path,
            code_path=code_path,
            analyzer=self
        )

    def generate_report(
        self,
        analysis: AnalysisResult,
        format: str = "markdown"
    ) -> str:
        """
        Generate a formatted analysis report.

        Args:
            analysis: AnalysisResult to format
            format: Output format ("markdown", "json", "html")

        Returns:
            Formatted report string
        """
        if format == "json":
            return self._generate_json_report(analysis)
        elif format == "html":
            return self._generate_html_report(analysis)
        else:
            return self._generate_markdown_report(analysis)

    # =========================================================================
    # Private Methods - Phase Analysis
    # =========================================================================

    def _analyze_comprehension(
        self,
        code: str,
        language: str,
        context: Optional[str]
    ) -> Dict:
        """
        Analyze Phase 1: Comprehension.

        Checks:
        - Problem definition clarity
        - Requirement documentation
        - Constraint identification
        - Input/output specification
        """
        score = 0
        issues = []
        max_score = self.PHASE_WEIGHTS["comprehension"]

        # Check for module/file docstring
        doc_analysis = self.documentation_analyzer.analyze_docstrings(
            code, language
        )
        if doc_analysis["has_module_doc"]:
            score += 5
        else:
            issues.append({
                "phase": "comprehension",
                "severity": "high",
                "issue": "Missing module/file documentation",
                "suggestion": "Add a docstring explaining the module's purpose"
            })

        # Check for requirement indicators
        req_patterns = [
            r"requirement[s]?",
            r"input[s]?.*:",
            r"output[s]?.*:",
            r"constraint[s]?",
            r"purpose"
        ]
        req_found = sum(
            1 for p in req_patterns
            if re.search(p, code, re.IGNORECASE)
        )
        score += min(5, req_found * 2)
        if req_found < 2:
            issues.append({
                "phase": "comprehension",
                "severity": "medium",
                "issue": "Requirements not clearly documented",
                "suggestion": "Document inputs, outputs, and constraints"
            })

        # Check for function documentation
        if doc_analysis["documented_functions_ratio"] > 0.7:
            score += 5
        elif doc_analysis["documented_functions_ratio"] > 0.3:
            score += 2
            issues.append({
                "phase": "comprehension",
                "severity": "medium",
                "issue": "Some functions lack documentation",
                "suggestion": "Add docstrings to all public functions"
            })
        else:
            issues.append({
                "phase": "comprehension",
                "severity": "high",
                "issue": "Most functions lack documentation",
                "suggestion": "Document all functions with purpose and parameters"
            })

        # Check for type hints (language-specific)
        type_analysis = self.structure_analyzer.analyze_types(code, language)
        if type_analysis["has_type_hints"]:
            score += 5
        elif language in ["python", "typescript"]:
            issues.append({
                "phase": "comprehension",
                "severity": "low",
                "issue": "Missing type hints",
                "suggestion": "Add type annotations for better clarity"
            })

        return {
            "score": min(score, max_score),
            "issues": issues
        }

    def _analyze_strategy(self, code: str, language: str) -> Dict:
        """
        Analyze Phase 2: Strategy.

        Checks:
        - Approach documentation
        - Alternative consideration evidence
        - Trade-off discussion
        - Architectural decisions
        """
        score = 0
        issues = []
        max_score = self.PHASE_WEIGHTS["strategy"]

        # Check for approach/strategy comments
        strategy_indicators = [
            r"approach",
            r"strategy",
            r"algorithm",
            r"method",
            r"selected.*because",
            r"chose.*because",
            r"trade-?off",
            r"alternative"
        ]

        strategy_mentions = sum(
            1 for p in strategy_indicators
            if re.search(p, code, re.IGNORECASE)
        )

        if strategy_mentions >= 3:
            score += 8
        elif strategy_mentions >= 1:
            score += 4
            issues.append({
                "phase": "strategy",
                "severity": "medium",
                "issue": "Limited strategy documentation",
                "suggestion": "Explain why this approach was chosen"
            })
        else:
            issues.append({
                "phase": "strategy",
                "severity": "high",
                "issue": "No strategy/approach documentation",
                "suggestion": "Document the chosen approach and why alternatives were rejected"
            })

        # Check for structural planning (functions, classes)
        structure = self.structure_analyzer.analyze_structure(code, language)
        if structure["is_well_organized"]:
            score += 6
        else:
            issues.append({
                "phase": "strategy",
                "severity": "medium",
                "issue": "Code structure could be improved",
                "suggestion": "Organize code into logical functions/classes"
            })

        # Check for DECISION comments or documentation
        decision_pattern = r"(?:DECISION|CHOICE|NOTE|WHY).*?:"
        decisions = re.findall(decision_pattern, code, re.IGNORECASE)
        if len(decisions) >= 2:
            score += 6
        elif len(decisions) >= 1:
            score += 3
            issues.append({
                "phase": "strategy",
                "severity": "low",
                "issue": "Few decision points documented",
                "suggestion": "Document non-obvious decisions with DECISION: comments"
            })
        else:
            issues.append({
                "phase": "strategy",
                "severity": "medium",
                "issue": "No documented decisions",
                "suggestion": "Add DECISION: comments explaining non-obvious choices"
            })

        return {
            "score": min(score, max_score),
            "issues": issues
        }

    def _analyze_execution(self, code: str, language: str) -> Dict:
        """
        Analyze Phase 3: Execution.

        Checks:
        - Code consistency
        - Logical flow
        - Step documentation
        - Plan adherence indicators
        """
        score = 0
        issues = []
        max_score = self.PHASE_WEIGHTS["execution"]

        # Check for step/section comments
        step_patterns = [
            r"step\s*\d",
            r"#\s*\d+\.",
            r"//\s*\d+\.",
            r"section",
            r"phase"
        ]
        step_mentions = sum(
            len(re.findall(p, code, re.IGNORECASE))
            for p in step_patterns
        )

        if step_mentions >= 3:
            score += 6
        elif step_mentions >= 1:
            score += 3
            issues.append({
                "phase": "execution",
                "severity": "low",
                "issue": "Limited step documentation",
                "suggestion": "Add comments marking major steps (# Step 1: ...)"
            })
        else:
            issues.append({
                "phase": "execution",
                "severity": "medium",
                "issue": "No step markers in code",
                "suggestion": "Document the execution flow with step comments"
            })

        # Check code consistency
        consistency = self.structure_analyzer.check_consistency(code, language)
        if consistency["score"] >= 0.8:
            score += 7
        elif consistency["score"] >= 0.5:
            score += 4
            issues.extend([
                {
                    "phase": "execution",
                    "severity": "low",
                    "issue": f"Consistency issue: {issue}",
                    "suggestion": "Maintain consistent coding style"
                }
                for issue in consistency["issues"][:2]
            ])
        else:
            issues.append({
                "phase": "execution",
                "severity": "medium",
                "issue": "Code has consistency problems",
                "suggestion": "Apply consistent formatting and naming conventions"
            })

        # Check for magic numbers/strings
        magic_analysis = self.structure_analyzer.find_magic_values(code, language)
        if magic_analysis["count"] == 0:
            score += 7
        elif magic_analysis["count"] <= 3:
            score += 4
            issues.append({
                "phase": "execution",
                "severity": "low",
                "issue": f"Found {magic_analysis['count']} magic values",
                "suggestion": "Extract magic numbers/strings to named constants"
            })
        else:
            issues.append({
                "phase": "execution",
                "severity": "medium",
                "issue": f"Found {magic_analysis['count']} unexplained magic values",
                "suggestion": "Replace magic values with named constants"
            })

        return {
            "score": min(score, max_score),
            "issues": issues
        }

    def _analyze_review(self, code: str, language: str) -> Dict:
        """
        Analyze Phase 4: Review.

        Checks:
        - Edge case handling
        - Input validation
        - Error handling
        - Verification logic
        """
        score = 0
        issues = []
        max_score = self.PHASE_WEIGHTS["review"]

        # Check for edge case handling
        edge_patterns = [
            r"if.*(?:is\s+)?(?:None|null|nil|empty|zero|negative)",
            r"if.*(?:len|length|size).*(?:==|<=|<)\s*[01]",
            r"if not\s+\w+",
            r"edge\s*case",
            r"boundary"
        ]
        edge_handling = sum(
            len(re.findall(p, code, re.IGNORECASE))
            for p in edge_patterns
        )

        if edge_handling >= 3:
            score += 7
        elif edge_handling >= 1:
            score += 3
            issues.append({
                "phase": "review",
                "severity": "medium",
                "issue": "Limited edge case handling",
                "suggestion": "Add checks for empty, null, and boundary conditions"
            })
        else:
            issues.append({
                "phase": "review",
                "severity": "high",
                "issue": "No edge case handling detected",
                "suggestion": "Add validation for edge cases (empty input, null, boundaries)"
            })

        # Check for error handling
        error_analysis = self.structure_analyzer.analyze_error_handling(
            code, language
        )
        if error_analysis["has_error_handling"]:
            score += 6
            if not error_analysis["has_specific_exceptions"]:
                issues.append({
                    "phase": "review",
                    "severity": "low",
                    "issue": "Using generic exception handling",
                    "suggestion": "Use specific exception types"
                })
        else:
            issues.append({
                "phase": "review",
                "severity": "high",
                "issue": "No error handling present",
                "suggestion": "Add try/except blocks for potential failure points"
            })

        # Check for validation
        validation_patterns = [
            r"valid",
            r"check",
            r"verify",
            r"assert",
            r"isinstance",
            r"typeof"
        ]
        validation = sum(
            len(re.findall(p, code, re.IGNORECASE))
            for p in validation_patterns
        )

        if validation >= 3:
            score += 7
        elif validation >= 1:
            score += 3
            issues.append({
                "phase": "review",
                "severity": "medium",
                "issue": "Limited input validation",
                "suggestion": "Add validation for function inputs"
            })
        else:
            issues.append({
                "phase": "review",
                "severity": "medium",
                "issue": "No input validation detected",
                "suggestion": "Validate inputs before processing"
            })

        return {
            "score": min(score, max_score),
            "issues": issues
        }

    def _analyze_refinement(self, code: str, language: str) -> Dict:
        """
        Analyze Phase 5: Refinement.

        Checks:
        - Code optimization
        - Cleanup and polish
        - TODO/FIXME presence
        - Overall code quality
        """
        score = 0
        issues = []
        max_score = self.PHASE_WEIGHTS["refinement"]

        # Check for TODO/FIXME comments (indicate incomplete refinement)
        todo_pattern = r"(?:TODO|FIXME|HACK|XXX|BUG)"
        todos = re.findall(todo_pattern, code, re.IGNORECASE)

        if len(todos) == 0:
            score += 6
        elif len(todos) <= 2:
            score += 3
            issues.append({
                "phase": "refinement",
                "severity": "low",
                "issue": f"Found {len(todos)} TODO/FIXME comments",
                "suggestion": "Address TODO items before release"
            })
        else:
            issues.append({
                "phase": "refinement",
                "severity": "medium",
                "issue": f"Found {len(todos)} unresolved TODO/FIXME items",
                "suggestion": "Complete or remove TODO items"
            })

        # Check code complexity
        complexity = self.structure_analyzer.estimate_complexity(code, language)
        if complexity["average"] <= 5:
            score += 7
        elif complexity["average"] <= 10:
            score += 4
            issues.append({
                "phase": "refinement",
                "severity": "low",
                "issue": "Some functions have moderate complexity",
                "suggestion": "Consider breaking down complex functions"
            })
        else:
            issues.append({
                "phase": "refinement",
                "severity": "medium",
                "issue": "High cyclomatic complexity detected",
                "suggestion": "Refactor complex functions into smaller units"
            })

        # Check for code duplication indicators
        duplication = self.structure_analyzer.detect_duplication(code, language)
        if duplication["ratio"] < 0.1:
            score += 7
        elif duplication["ratio"] < 0.2:
            score += 4
            issues.append({
                "phase": "refinement",
                "severity": "low",
                "issue": "Some code duplication detected",
                "suggestion": "Extract duplicated code into reusable functions"
            })
        else:
            issues.append({
                "phase": "refinement",
                "severity": "medium",
                "issue": "Significant code duplication",
                "suggestion": "DRY: Extract common patterns into shared functions"
            })

        return {
            "score": min(score, max_score),
            "issues": issues
        }

    # =========================================================================
    # Private Methods - Utilities
    # =========================================================================

    def _calculate_grade(self, score: int) -> str:
        """Calculate letter grade from numeric score."""
        for threshold, grade in sorted(
            self.GRADE_THRESHOLDS.items(),
            reverse=True
        ):
            if score >= threshold:
                return grade
        return "F"

    def _generate_recommendations(
        self,
        phase_scores: Dict[str, int],
        issues: List[Dict]
    ) -> List[str]:
        """Generate prioritized recommendations based on analysis."""
        recommendations = []

        # Find weakest phases
        sorted_phases = sorted(
            phase_scores.items(),
            key=lambda x: x[1]
        )

        # Add recommendations for weak phases
        for phase, score in sorted_phases[:3]:
            if score < 15:  # Less than 75% of phase max
                phase_issues = [
                    i for i in issues
                    if i.get("phase") == phase and i.get("severity") == "high"
                ]
                if phase_issues:
                    recommendations.append(
                        f"Priority: Address {phase} phase - {phase_issues[0]['suggestion']}"
                    )

        # Add high-severity issues
        high_issues = [
            i for i in issues
            if i.get("severity") == "high" and
            i["suggestion"] not in str(recommendations)
        ]
        for issue in high_issues[:3]:
            recommendations.append(issue["suggestion"])

        return recommendations[:5]  # Top 5 recommendations

    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".rb": "ruby",
            ".php": "php"
        }
        return extension_map.get(extension.lower(), "unknown")

    def _generate_markdown_report(self, analysis: AnalysisResult) -> str:
        """Generate markdown-formatted analysis report."""
        report = f"""## Reasoning Analysis Report

### Overall Score: {analysis.overall_score}/100 (Grade: {analysis.grade})

### Phase-by-Phase Assessment

| Phase | Score | Status |
|-------|-------|--------|
| Comprehension | {analysis.phase_scores['comprehension']}/20 | {'✓' if analysis.phase_scores['comprehension'] >= 14 else '⚠'} |
| Strategy | {analysis.phase_scores['strategy']}/20 | {'✓' if analysis.phase_scores['strategy'] >= 14 else '⚠'} |
| Execution | {analysis.phase_scores['execution']}/20 | {'✓' if analysis.phase_scores['execution'] >= 14 else '⚠'} |
| Review | {analysis.phase_scores['review']}/20 | {'✓' if analysis.phase_scores['review'] >= 14 else '⚠'} |
| Refinement | {analysis.phase_scores['refinement']}/20 | {'✓' if analysis.phase_scores['refinement'] >= 14 else '⚠'} |

### Issues Found

"""
        for issue in analysis.issues:
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                issue.get("severity", "medium"), "⚪"
            )
            report += f"- {severity_icon} **{issue['phase'].title()}**: {issue['issue']}\n"

        report += "\n### Priority Recommendations\n\n"
        for i, rec in enumerate(analysis.recommendations, 1):
            report += f"{i}. {rec}\n"

        return report

    def _generate_json_report(self, analysis: AnalysisResult) -> str:
        """Generate JSON-formatted analysis report."""
        return json.dumps({
            "overall_score": analysis.overall_score,
            "grade": analysis.grade,
            "phase_scores": analysis.phase_scores,
            "issues": analysis.issues,
            "recommendations": analysis.recommendations,
            "metadata": analysis.metadata
        }, indent=2)

    def _generate_html_report(self, analysis: AnalysisResult) -> str:
        """Generate HTML-formatted analysis report."""
        # Basic HTML report generation
        return f"""
        <div class="reasoning-report">
            <h2>Reasoning Analysis Report</h2>
            <div class="score">
                <span class="overall">{analysis.overall_score}/100</span>
                <span class="grade">Grade: {analysis.grade}</span>
            </div>
            <div class="phases">
                {''.join(f'<div class="phase"><span>{p}</span><span>{s}/20</span></div>'
                         for p, s in analysis.phase_scores.items())}
            </div>
        </div>
        """


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """Command-line interface for Reasoning Optimizer."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze code for reasoning quality"
    )
    parser.add_argument(
        "command",
        choices=["analyze", "rebuild", "checkpoint"],
        help="Command to execute"
    )
    parser.add_argument(
        "target",
        help="File path or code to analyze"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "html"],
        default="markdown",
        help="Output format"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=70,
        help="Minimum passing score"
    )

    args = parser.parse_args()

    optimizer = ReasoningOptimizer({"threshold": args.threshold})

    if args.command == "analyze":
        if Path(args.target).exists():
            result = optimizer.analyze_file(args.target)
        else:
            result = optimizer.analyze_code(args.target)
        print(optimizer.generate_report(result, args.format))

    elif args.command == "rebuild":
        if Path(args.target).exists():
            code = Path(args.target).read_text()
        else:
            code = args.target
        result = optimizer.reconstruct_code(code)
        print(f"Before: {result.before_score}/100")
        print(f"After: {result.after_score}/100")
        print("\n" + result.reconstructed_code)

    elif args.command == "checkpoint":
        result = optimizer.create_checkpoint(
            checkpoint_type=args.target,
            project_path="."
        )
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
