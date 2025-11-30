"""
Performance Analyzer for Backend Trainer

Identifies performance bottlenecks, optimization opportunities,
and efficiency issues in backend code.
"""

import re
import ast
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class PerformanceCategory(Enum):
    DATABASE = "database"
    ALGORITHM = "algorithm"
    MEMORY = "memory"
    IO = "io"
    CONCURRENCY = "concurrency"
    CACHING = "caching"
    NETWORK = "network"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class PerformanceIssue:
    severity: Severity
    category: PerformanceCategory
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    estimated_impact: str = ""
    recommendation: str = ""
    code_pattern: str = ""


@dataclass
class PerformanceAnalysisResult:
    overall_score: int
    issues: list[PerformanceIssue] = field(default_factory=list)
    recommendations: list[PerformanceIssue] = field(default_factory=list)
    optimization_opportunities: list[PerformanceIssue] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


class PerformanceAnalyzer:
    """Analyzes backend code for performance issues."""

    # Database performance patterns
    DB_PATTERNS = [
        (r'SELECT\s+\*\s+FROM', "SELECT * query", PerformanceCategory.DATABASE, Severity.MEDIUM),
        (r'\.all\(\).*\.all\(\)', "Multiple .all() in sequence", PerformanceCategory.DATABASE, Severity.HIGH),
        (r'for\s+\w+\s+in\s+.*\.all\(\):', "Iterating over .all() in loop", PerformanceCategory.DATABASE, Severity.MEDIUM),
        (r'LIKE\s+[\'"]%', "Leading wildcard LIKE", PerformanceCategory.DATABASE, Severity.HIGH),
        (r'ORDER\s+BY\s+RAND\(\)', "ORDER BY RAND()", PerformanceCategory.DATABASE, Severity.HIGH),
        (r'SELECT.*(?:COUNT|SUM|AVG).*GROUP\s+BY', "Aggregation without index hint", PerformanceCategory.DATABASE, Severity.MEDIUM),
    ]

    # Algorithm complexity patterns
    ALGORITHM_PATTERNS = [
        (r'for\s+\w+\s+in.*:\s*\n\s+for\s+\w+\s+in', "Nested loops (O(n^2))", PerformanceCategory.ALGORITHM, Severity.MEDIUM),
        (r'for.*for.*for', "Triple nested loops (O(n^3))", PerformanceCategory.ALGORITHM, Severity.HIGH),
        (r'\.sort\(\).*for', "Sort in loop", PerformanceCategory.ALGORITHM, Severity.HIGH),
        (r'in\s+\[\s*.*\s*\]', "List membership check (use set)", PerformanceCategory.ALGORITHM, Severity.LOW),
        (r'\.index\(.*\)\s+in\s+.*for', "index() in loop", PerformanceCategory.ALGORITHM, Severity.MEDIUM),
    ]

    # Memory patterns
    MEMORY_PATTERNS = [
        (r'\.read\(\)', "Full file read into memory", PerformanceCategory.MEMORY, Severity.MEDIUM),
        (r'list\(.*\.all\(\)', "Loading all DB records to list", PerformanceCategory.MEMORY, Severity.HIGH),
        (r'\+=\s*[\'"]', "String concatenation in loop", PerformanceCategory.MEMORY, Severity.MEDIUM),
        (r'global\s+\w+\s*=\s*\[\]', "Global mutable list", PerformanceCategory.MEMORY, Severity.LOW),
        (r'\.append\(.*\)\s*$(?=.*for)', "Append in loop (consider list comprehension)", PerformanceCategory.MEMORY, Severity.LOW),
    ]

    # I/O patterns
    IO_PATTERNS = [
        (r'open\(.*\)(?!.*with)', "File open without context manager", PerformanceCategory.IO, Severity.MEDIUM),
        (r'for.*requests\.(get|post)', "HTTP request in loop", PerformanceCategory.IO, Severity.HIGH),
        (r'\.write\(.*\).*for', "Write in loop", PerformanceCategory.IO, Severity.MEDIUM),
        (r'time\.sleep\(', "Blocking sleep", PerformanceCategory.IO, Severity.LOW),
    ]

    # Concurrency patterns
    CONCURRENCY_PATTERNS = [
        (r'threading\.Thread\(', "Manual threading (consider ThreadPool)", PerformanceCategory.CONCURRENCY, Severity.LOW),
        (r'await\s+\w+\(\).*\n.*await\s+\w+\(\)', "Sequential awaits (consider gather)", PerformanceCategory.CONCURRENCY, Severity.MEDIUM),
        (r'for.*await', "Await in loop (consider asyncio.gather)", PerformanceCategory.CONCURRENCY, Severity.MEDIUM),
    ]

    # Caching opportunities
    CACHING_PATTERNS = [
        (r'def\s+get_\w+\(.*\):\s*\n\s+.*query', "Getter without caching", PerformanceCategory.CACHING, Severity.INFO),
        (r'\.find\(.*\).*\n.*\.find\(', "Repeated find operations", PerformanceCategory.CACHING, Severity.MEDIUM),
        (r'requests\.get\(.*\)(?!.*cache)', "HTTP GET without caching", PerformanceCategory.CACHING, Severity.LOW),
    ]

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.analysis_result = None

    def analyze(self, codebase_path: str) -> PerformanceAnalysisResult:
        """Perform complete performance analysis."""
        path = Path(codebase_path)
        if not path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")

        self.analysis_result = PerformanceAnalysisResult(overall_score=100)

        # Collect source files
        python_files = list(path.rglob("*.py"))
        js_files = list(path.rglob("*.js")) + list(path.rglob("*.ts"))
        all_files = python_files + js_files

        # Run pattern-based analysis
        self._analyze_patterns(all_files)

        # Run AST-based analysis for Python
        self._analyze_python_ast(python_files)

        # Check for missing optimizations
        self._check_missing_optimizations(all_files)

        # Analyze async patterns
        self._analyze_async_patterns(all_files)

        # Calculate scores
        self._calculate_scores()

        # Generate recommendations
        self._generate_recommendations()

        return self.analysis_result

    def _analyze_patterns(self, files: list[Path]) -> None:
        """Analyze files for performance anti-patterns."""
        all_patterns = (
            self.DB_PATTERNS +
            self.ALGORITHM_PATTERNS +
            self.MEMORY_PATTERNS +
            self.IO_PATTERNS +
            self.CONCURRENCY_PATTERNS +
            self.CACHING_PATTERNS
        )

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern, description, category, severity in all_patterns:
                for match in re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE):
                    line_num = content[:match.start()].count('\n') + 1

                    issue = PerformanceIssue(
                        severity=severity,
                        category=category,
                        title=description,
                        description=f"Pattern detected: {description}",
                        file_path=str(file_path),
                        line_number=line_num,
                        code_pattern=pattern,
                        recommendation=self._get_recommendation(category, description)
                    )
                    self.analysis_result.issues.append(issue)

    def _analyze_python_ast(self, files: list[Path]) -> None:
        """Perform AST-based analysis on Python files."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content)
            except (OSError, UnicodeDecodeError, SyntaxError):
                continue

            # Check for complexity issues
            self._check_function_complexity(tree, file_path)

            # Check for inefficient patterns
            self._check_inefficient_constructs(tree, file_path, content)

    def _check_function_complexity(self, tree: ast.AST, file_path: Path) -> None:
        """Check function complexity."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count lines
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    lines = node.end_lineno - node.lineno
                    if lines > 100:
                        self.analysis_result.issues.append(PerformanceIssue(
                            severity=Severity.MEDIUM,
                            category=PerformanceCategory.ALGORITHM,
                            title="Long function",
                            description=f"Function '{node.name}' is {lines} lines",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            recommendation="Consider breaking into smaller functions for maintainability"
                        ))

                # Count nested loops
                nested_depth = self._count_nested_loops(node)
                if nested_depth >= 3:
                    self.analysis_result.issues.append(PerformanceIssue(
                        severity=Severity.HIGH,
                        category=PerformanceCategory.ALGORITHM,
                        title=f"Deep loop nesting ({nested_depth} levels)",
                        description=f"Function '{node.name}' has {nested_depth} levels of nested loops",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        recommendation="Consider flattening loops or using more efficient algorithms"
                    ))

    def _count_nested_loops(self, node: ast.AST, depth: int = 0) -> int:
        """Count maximum nested loop depth."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                child_depth = self._count_nested_loops(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._count_nested_loops(child, depth)
                max_depth = max(max_depth, child_depth)
        return max_depth

    def _check_inefficient_constructs(self, tree: ast.AST, file_path: Path, content: str) -> None:
        """Check for inefficient Python constructs."""
        for node in ast.walk(tree):
            # Check for list concatenation in loop
            if isinstance(node, ast.AugAssign):
                if isinstance(node.op, ast.Add) and isinstance(node.target, ast.Name):
                    # Check if inside a loop
                    parent_nodes = [n for n in ast.walk(tree)]
                    in_loop = any(isinstance(p, (ast.For, ast.While)) for p in parent_nodes)
                    if in_loop:
                        self.analysis_result.optimization_opportunities.append(PerformanceIssue(
                            severity=Severity.LOW,
                            category=PerformanceCategory.MEMORY,
                            title="List/string += in loop",
                            description="Concatenation in loop can be inefficient",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            recommendation="Use list comprehension or join() for strings"
                        ))

            # Check for repeated attribute access
            if isinstance(node, ast.Attribute):
                # Multiple dots suggest repeated access
                pass  # Complex to detect reliably

    def _check_missing_optimizations(self, files: list[Path]) -> None:
        """Check for missing common optimizations."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            # Check for missing __slots__ in data classes
            if "class " in content and "@dataclass" in content:
                if "__slots__" not in content:
                    self.analysis_result.optimization_opportunities.append(PerformanceIssue(
                        severity=Severity.INFO,
                        category=PerformanceCategory.MEMORY,
                        title="Dataclass without __slots__",
                        description="Dataclass could benefit from __slots__ for memory efficiency",
                        file_path=str(file_path),
                        recommendation="Add slots=True to @dataclass decorator"
                    ))

            # Check for sync HTTP calls in async context
            if "async def" in content and "requests." in content:
                self.analysis_result.issues.append(PerformanceIssue(
                    severity=Severity.HIGH,
                    category=PerformanceCategory.IO,
                    title="Sync HTTP in async function",
                    description="Using synchronous requests in async context",
                    file_path=str(file_path),
                    recommendation="Use aiohttp or httpx for async HTTP calls"
                ))

    def _analyze_async_patterns(self, files: list[Path]) -> None:
        """Analyze async/await patterns for inefficiencies."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            # Check for sequential awaits that could be parallel
            sequential_await_pattern = r'await\s+\w+\([^)]*\)\s*\n\s*await\s+\w+\('
            for match in re.finditer(sequential_await_pattern, content):
                line_num = content[:match.start()].count('\n') + 1

                # Check if these awaits are independent (simple heuristic)
                matched_text = match.group(0)
                if not re.search(r'=.*await', matched_text):
                    self.analysis_result.optimization_opportunities.append(PerformanceIssue(
                        severity=Severity.MEDIUM,
                        category=PerformanceCategory.CONCURRENCY,
                        title="Sequential awaits",
                        description="Consecutive awaits might run in parallel",
                        file_path=str(file_path),
                        line_number=line_num,
                        recommendation="Use asyncio.gather() for independent async operations"
                    ))

    def _calculate_scores(self) -> None:
        """Calculate performance score."""
        score = 100

        severity_weights = {
            Severity.CRITICAL: 20,
            Severity.HIGH: 12,
            Severity.MEDIUM: 6,
            Severity.LOW: 2,
            Severity.INFO: 0
        }

        for issue in self.analysis_result.issues:
            score -= severity_weights.get(issue.severity, 0)

        self.analysis_result.overall_score = max(0, min(100, score))

        # Calculate stats by category
        category_counts: dict[str, int] = {}
        for issue in self.analysis_result.issues:
            cat = issue.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        self.analysis_result.stats = {
            "total_issues": len(self.analysis_result.issues),
            "optimization_opportunities": len(self.analysis_result.optimization_opportunities),
            "by_category": category_counts,
            "by_severity": {
                "critical": sum(1 for i in self.analysis_result.issues if i.severity == Severity.CRITICAL),
                "high": sum(1 for i in self.analysis_result.issues if i.severity == Severity.HIGH),
                "medium": sum(1 for i in self.analysis_result.issues if i.severity == Severity.MEDIUM),
                "low": sum(1 for i in self.analysis_result.issues if i.severity == Severity.LOW)
            }
        }

    def _generate_recommendations(self) -> None:
        """Generate performance recommendations."""
        stats = self.analysis_result.stats.get("by_category", {})

        if stats.get("database", 0) > 3:
            self.analysis_result.recommendations.append(PerformanceIssue(
                severity=Severity.HIGH,
                category=PerformanceCategory.DATABASE,
                title="Database Query Optimization Needed",
                description="Multiple database performance issues detected",
                file_path="",
                recommendation="Review database queries, add indexes, and implement query optimization"
            ))

        if stats.get("algorithm", 0) > 2:
            self.analysis_result.recommendations.append(PerformanceIssue(
                severity=Severity.MEDIUM,
                category=PerformanceCategory.ALGORITHM,
                title="Algorithm Review Recommended",
                description="Multiple algorithmic inefficiencies detected",
                file_path="",
                recommendation="Review time complexity of critical paths"
            ))

        if stats.get("io", 0) > 2:
            self.analysis_result.recommendations.append(PerformanceIssue(
                severity=Severity.MEDIUM,
                category=PerformanceCategory.IO,
                title="I/O Optimization Needed",
                description="Multiple I/O inefficiencies detected",
                file_path="",
                recommendation="Consider async I/O, connection pooling, and batching"
            ))

    def _get_recommendation(self, category: PerformanceCategory, description: str) -> str:
        """Get recommendation based on category and description."""
        recommendations = {
            PerformanceCategory.DATABASE: {
                "SELECT *": "Select only needed columns",
                "LIKE": "Use full-text search or redesign query",
                "RAND": "Use application-side randomization with LIMIT",
                "default": "Add appropriate indexes and optimize query"
            },
            PerformanceCategory.ALGORITHM: {
                "Nested loops": "Consider using hash maps or sets for O(1) lookups",
                "Sort in loop": "Sort once outside the loop",
                "default": "Review algorithm complexity"
            },
            PerformanceCategory.MEMORY: {
                "read()": "Use chunked reading or streaming",
                "list()": "Use iterators or pagination",
                "concatenation": "Use join() for strings, list comprehensions for lists",
                "default": "Review memory allocation patterns"
            },
            PerformanceCategory.IO: {
                "context manager": "Always use 'with' statement for file operations",
                "HTTP request in loop": "Use connection pooling or batch requests",
                "default": "Consider async I/O or batching"
            },
            PerformanceCategory.CONCURRENCY: {
                "threading": "Use ThreadPoolExecutor or ProcessPoolExecutor",
                "Sequential awaits": "Use asyncio.gather() for parallel execution",
                "default": "Review concurrency patterns"
            },
            PerformanceCategory.CACHING: {
                "default": "Implement caching with appropriate TTL"
            }
        }

        cat_recs = recommendations.get(category, {})
        for key, rec in cat_recs.items():
            if key != "default" and key.lower() in description.lower():
                return rec
        return cat_recs.get("default", "Review and optimize")

    def get_summary(self) -> dict:
        """Get performance analysis summary."""
        if not self.analysis_result:
            return {}

        return {
            "overall_score": self.analysis_result.overall_score,
            "stats": self.analysis_result.stats,
            "top_issues": [
                {
                    "title": i.title,
                    "category": i.category.value,
                    "severity": i.severity.value,
                    "file": i.file_path
                }
                for i in sorted(
                    self.analysis_result.issues,
                    key=lambda x: list(Severity).index(x.severity)
                )[:5]
            ],
            "recommendations_count": len(self.analysis_result.recommendations)
        }


def analyze_performance(codebase_path: str, config: Optional[dict] = None) -> dict:
    """Convenience function to analyze performance and return summary."""
    analyzer = PerformanceAnalyzer(config)
    result = analyzer.analyze(codebase_path)
    return {
        "result": result,
        "summary": analyzer.get_summary()
    }
