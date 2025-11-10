"""
Architecture Analyzer Module

Performs deep analysis of codebase architecture including:
- Language detection
- Entry point identification
- Pattern recognition
- Complexity metrics
- Technical debt assessment
"""

import ast
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict, Counter
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FileAnalysis:
    """Analysis results for a single file"""
    path: Path
    language: str
    lines_of_code: int
    complexity: int
    imports: List[str]
    exports: List[str]
    classes: List[str]
    functions: List[str]
    patterns: List[str]


class ArchitectureAnalyzer:
    """
    Analyzes codebase architecture to understand structure and quality

    Performs static analysis to detect patterns, anti-patterns, and
    architectural characteristics
    """

    def __init__(self, analysis_depth: str = "deep"):
        """
        Initialize analyzer

        Args:
            analysis_depth: Level of analysis ("shallow", "medium", "deep")
        """
        self.analysis_depth = analysis_depth
        self.logger = logging.getLogger(__name__ + ".ArchitectureAnalyzer")

        # Pattern definitions
        self.design_patterns = {
            "singleton": [r"class\s+\w+.*:\s+_instance\s*=\s*None", r"getInstance"],
            "factory": [r"create\w+", r"build\w+", r"Factory"],
            "observer": [r"subscribe", r"notify", r"addEventListener"],
            "strategy": [r"Strategy", r"setStrategy"],
            "decorator": [r"@\w+", r"wrapper"],
            "repository": [r"Repository", r"findBy", r"save"],
            "service": [r"Service", r"execute", r"process"],
            "mvc": [r"Controller", r"Model", r"View"],
            "mvvm": [r"ViewModel", r"Model", r"View"]
        }

        self.anti_patterns = {
            "god_object": "Class/module doing too much",
            "spaghetti_code": "Complex tangled control flow",
            "circular_dependency": "Modules depend on each other",
            "magic_numbers": "Unexplained numeric literals",
            "tight_coupling": "High interdependency between modules"
        }

    def detect_languages(self, files: List[Path]) -> List[str]:
        """
        Detect programming languages in the codebase

        Args:
            files: List of file paths

        Returns:
            List of detected language names
        """
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript React',
            '.tsx': 'TypeScript React',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.cs': 'C#',
            '.kt': 'Kotlin',
            '.swift': 'Swift'
        }

        detected = set()
        for file in files:
            lang = language_map.get(file.suffix)
            if lang:
                detected.add(lang)

        return sorted(list(detected))

    def find_entry_points(self, files: List[Path]) -> List[str]:
        """
        Identify entry points in the codebase

        Args:
            files: List of source files

        Returns:
            List of entry point file paths
        """
        entry_points = []
        entry_indicators = [
            'main.py', '__main__.py', 'app.py', 'index.js', 'main.js',
            'index.ts', 'main.ts', 'server.js', 'server.ts', 'Main.java',
            'main.go', 'main.rs', 'application.py', 'run.py'
        ]

        for file in files:
            # Check by filename
            if file.name in entry_indicators:
                entry_points.append(str(file))
                continue

            # Check for main function/block
            try:
                content = file.read_text(errors='ignore')
                if self._has_main_function(content, file.suffix):
                    entry_points.append(str(file))
            except Exception as e:
                self.logger.debug(f"Could not read {file}: {e}")

        return entry_points

    def _has_main_function(self, content: str, extension: str) -> bool:
        """Check if file contains a main function/entry point"""
        if extension == '.py':
            return 'if __name__ == "__main__"' in content or 'if __name__ == \'__main__\'' in content
        elif extension in ['.js', '.ts']:
            return bool(re.search(r'function\s+main\s*\(', content))
        elif extension == '.java':
            return bool(re.search(r'public\s+static\s+void\s+main', content))
        elif extension == '.go':
            return bool(re.search(r'func\s+main\s*\(', content))
        elif extension == '.rs':
            return bool(re.search(r'fn\s+main\s*\(', content))
        return False

    def identify_module_candidates(
        self, files: List[Path], dependency_graph: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Identify potential module boundaries

        Args:
            files: Source files
            dependency_graph: File dependency relationships

        Returns:
            List of module candidate specifications
        """
        self.logger.info("Identifying module candidates...")

        # Group files by directory
        dir_groups = defaultdict(list)
        for file in files:
            dir_groups[file.parent].append(file)

        # Analyze each directory as potential module
        candidates = []
        for directory, dir_files in dir_groups.items():
            # Skip if too few files
            if len(dir_files) < 2:
                continue

            # Analyze directory cohesion
            internal_deps = 0
            external_deps = 0

            for file in dir_files:
                file_deps = dependency_graph.get(str(file), [])
                for dep in file_deps:
                    if Path(dep).parent == directory:
                        internal_deps += 1
                    else:
                        external_deps += 1

            # Calculate cohesion score
            total_deps = internal_deps + external_deps
            cohesion = internal_deps / total_deps if total_deps > 0 else 0

            # Identify module purpose from names
            purpose = self._infer_module_purpose(directory, dir_files)

            candidates.append({
                "path": str(directory),
                "name": directory.name,
                "file_count": len(dir_files),
                "cohesion": cohesion,
                "internal_dependencies": internal_deps,
                "external_dependencies": external_deps,
                "purpose": purpose,
                "files": [str(f) for f in dir_files]
            })

        # Sort by cohesion (higher is better)
        candidates.sort(key=lambda x: x['cohesion'], reverse=True)

        return candidates

    def _infer_module_purpose(self, directory: Path, files: List[Path]) -> str:
        """Infer the purpose of a module from its structure"""
        dir_name = directory.name.lower()

        purpose_keywords = {
            "auth": "Authentication and authorization",
            "api": "API endpoints and routes",
            "db": "Database access layer",
            "database": "Database access layer",
            "model": "Data models and schemas",
            "view": "View/presentation layer",
            "controller": "Business logic controllers",
            "service": "Business logic services",
            "util": "Utility functions",
            "helper": "Helper functions",
            "config": "Configuration management",
            "test": "Test suite",
            "core": "Core functionality",
            "common": "Shared/common code",
            "lib": "Library functions",
            "component": "UI components",
            "middleware": "Middleware functions",
            "handler": "Request/event handlers",
            "repository": "Data repository pattern",
            "domain": "Domain models and logic"
        }

        for keyword, purpose in purpose_keywords.items():
            if keyword in dir_name:
                return purpose

        return "General module"

    def calculate_complexity_metrics(self, files: List[Path]) -> Dict[str, Any]:
        """
        Calculate various complexity metrics

        Args:
            files: Source files to analyze

        Returns:
            Dictionary of complexity metrics
        """
        self.logger.info("Calculating complexity metrics...")

        total_complexity = 0
        file_complexities = []
        function_complexities = []

        for file in files:
            try:
                if file.suffix == '.py':
                    complexity = self._analyze_python_complexity(file)
                    total_complexity += complexity['file_complexity']
                    file_complexities.append({
                        "file": str(file),
                        "complexity": complexity['file_complexity']
                    })
                    function_complexities.extend(complexity['functions'])
            except Exception as e:
                self.logger.debug(f"Could not analyze {file}: {e}")

        avg_file_complexity = (
            sum(fc['complexity'] for fc in file_complexities) / len(file_complexities)
            if file_complexities else 0
        )

        avg_function_complexity = (
            sum(fc['complexity'] for fc in function_complexities) / len(function_complexities)
            if function_complexities else 0
        )

        return {
            "total_complexity": total_complexity,
            "average_file_complexity": avg_file_complexity,
            "average_function_complexity": avg_function_complexity,
            "complex_files": sorted(
                file_complexities, key=lambda x: x['complexity'], reverse=True
            )[:10],
            "complex_functions": sorted(
                function_complexities, key=lambda x: x['complexity'], reverse=True
            )[:10]
        }

    def _analyze_python_complexity(self, file: Path) -> Dict[str, Any]:
        """Calculate cyclomatic complexity for Python file"""
        try:
            content = file.read_text(errors='ignore')
            tree = ast.parse(content)

            file_complexity = 0
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_complexity = self._calculate_cyclomatic_complexity(node)
                    file_complexity += func_complexity
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "complexity": func_complexity
                    })

            return {
                "file_complexity": file_complexity,
                "functions": functions
            }
        except Exception:
            return {"file_complexity": 0, "functions": []}

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for an AST node"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def calculate_coupling(self, dependency_graph: Dict[str, List[str]]) -> float:
        """
        Calculate coupling score (0-1, lower is better)

        Args:
            dependency_graph: File dependencies

        Returns:
            Coupling score
        """
        if not dependency_graph:
            return 0.0

        total_files = len(dependency_graph)
        total_dependencies = sum(len(deps) for deps in dependency_graph.values())

        # Maximum possible dependencies (complete graph)
        max_dependencies = total_files * (total_files - 1)

        if max_dependencies == 0:
            return 0.0

        coupling = total_dependencies / max_dependencies
        return min(coupling, 1.0)

    def calculate_cohesion(self, module_candidates: List[Dict[str, Any]]) -> float:
        """
        Calculate average cohesion score (0-1, higher is better)

        Args:
            module_candidates: Identified module candidates

        Returns:
            Average cohesion score
        """
        if not module_candidates:
            return 0.0

        cohesion_scores = [m['cohesion'] for m in module_candidates]
        return sum(cohesion_scores) / len(cohesion_scores)

    def detect_patterns(
        self, files: List[Path], dependency_graph: Dict[str, List[str]]
    ) -> List[str]:
        """
        Detect design patterns in the codebase

        Args:
            files: Source files
            dependency_graph: Dependencies

        Returns:
            List of detected patterns
        """
        detected = set()

        for file in files:
            try:
                content = file.read_text(errors='ignore')

                for pattern_name, pattern_regexes in self.design_patterns.items():
                    for regex in pattern_regexes:
                        if re.search(regex, content, re.IGNORECASE):
                            detected.add(pattern_name.title())
                            break
            except Exception as e:
                self.logger.debug(f"Could not analyze {file}: {e}")

        return sorted(list(detected))

    def detect_anti_patterns(
        self, files: List[Path], dependency_graph: Dict[str, List[str]], coupling_score: float
    ) -> List[str]:
        """
        Detect anti-patterns and code smells

        Args:
            files: Source files
            dependency_graph: Dependencies
            coupling_score: Calculated coupling score

        Returns:
            List of detected anti-patterns
        """
        detected = []

        # Check for tight coupling
        if coupling_score > 0.5:
            detected.append("Tight Coupling")

        # Check for circular dependencies
        if self._has_circular_dependencies(dependency_graph):
            detected.append("Circular Dependencies")

        # Check for god objects (very large files)
        for file in files:
            try:
                lines = len(file.read_text(errors='ignore').splitlines())
                if lines > 1000:
                    detected.append(f"God Object ({file.name})")
            except Exception:
                pass

        return detected

    def _has_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> bool:
        """Check if dependency graph has cycles"""
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in dependency_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in dependency_graph:
            if node not in visited:
                if has_cycle(node):
                    return True

        return False

    def assess_technical_debt(
        self, files: List[Path], anti_patterns: List[str], complexity_metrics: Dict[str, Any]
    ) -> List[str]:
        """
        Assess technical debt items

        Args:
            files: Source files
            anti_patterns: Detected anti-patterns
            complexity_metrics: Complexity metrics

        Returns:
            List of technical debt items
        """
        debt_items = []

        # Anti-patterns are technical debt
        for pattern in anti_patterns:
            debt_items.append(f"Anti-pattern detected: {pattern}")

        # High complexity is debt
        avg_complexity = complexity_metrics.get('average_file_complexity', 0)
        if avg_complexity > 10:
            debt_items.append(f"High average complexity: {avg_complexity:.1f}")

        # TODO comments indicate debt
        todo_count = 0
        for file in files:
            try:
                content = file.read_text(errors='ignore')
                todo_count += len(re.findall(r'#\s*TODO|//\s*TODO|/\*\s*TODO', content, re.IGNORECASE))
            except Exception:
                pass

        if todo_count > 0:
            debt_items.append(f"Found {todo_count} TODO comments")

        return debt_items

    def generate_recommendations(
        self, coupling_score: float, cohesion_score: float,
        patterns_detected: List[str], anti_patterns: List[str]
    ) -> List[str]:
        """
        Generate architectural recommendations

        Args:
            coupling_score: Coupling metric
            cohesion_score: Cohesion metric
            patterns_detected: Existing patterns
            anti_patterns: Detected anti-patterns

        Returns:
            List of recommendations
        """
        recommendations = []

        # Coupling recommendations
        if coupling_score > 0.5:
            recommendations.append(
                "High coupling detected. Consider applying dependency inversion "
                "and interface segregation principles."
            )
        elif coupling_score > 0.3:
            recommendations.append(
                "Moderate coupling. Look for opportunities to decouple through "
                "event-driven patterns or message passing."
            )

        # Cohesion recommendations
        if cohesion_score < 0.3:
            recommendations.append(
                "Low cohesion detected. Group related functionality together "
                "and separate unrelated concerns."
            )

        # Pattern recommendations
        if "Repository" not in patterns_detected:
            recommendations.append(
                "Consider implementing Repository pattern for data access abstraction."
            )

        if "Service" not in patterns_detected:
            recommendations.append(
                "Consider extracting business logic into Service layer."
            )

        # Anti-pattern remediation
        if "Circular Dependencies" in anti_patterns:
            recommendations.append(
                "Break circular dependencies using dependency inversion or mediator pattern."
            )

        if any("God Object" in ap for ap in anti_patterns):
            recommendations.append(
                "Refactor large classes/files using Single Responsibility Principle."
            )

        return recommendations
