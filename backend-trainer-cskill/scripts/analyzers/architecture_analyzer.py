"""
Architecture Analyzer for Backend Trainer

Analyzes backend code structure, layer separation, dependency flow,
and design pattern compliance.
"""

import os
import re
import ast
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ArchitectureType(Enum):
    LAYERED = "layered"
    HEXAGONAL = "hexagonal"
    CLEAN = "clean"
    MONOLITH = "monolith"
    MICROSERVICE = "microservice"
    MVC = "mvc"
    UNKNOWN = "unknown"


class LayerType(Enum):
    PRESENTATION = "presentation"
    BUSINESS = "business"
    DATA_ACCESS = "data_access"
    DOMAIN = "domain"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"


@dataclass
class Issue:
    severity: str  # critical, high, medium, low
    category: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    recommendation: str = ""
    code_snippet: str = ""


@dataclass
class LayerAnalysis:
    layer_type: LayerType
    files: list[str] = field(default_factory=list)
    score: int = 0
    issues: list[Issue] = field(default_factory=list)
    patterns_found: list[str] = field(default_factory=list)


@dataclass
class ArchitectureAnalysisResult:
    architecture_type: ArchitectureType
    overall_score: int
    layers: dict[str, LayerAnalysis] = field(default_factory=dict)
    patterns_detected: list[str] = field(default_factory=list)
    anti_patterns_detected: list[str] = field(default_factory=list)
    dependency_issues: list[Issue] = field(default_factory=list)
    recommendations: list[Issue] = field(default_factory=list)


class ArchitectureAnalyzer:
    """Analyzes backend architecture and code organization."""

    LAYER_INDICATORS = {
        LayerType.PRESENTATION: [
            "controller", "route", "router", "endpoint", "view", "api",
            "handler", "resource", "rest", "graphql"
        ],
        LayerType.BUSINESS: [
            "service", "usecase", "use_case", "business", "logic",
            "manager", "processor", "workflow", "orchestrator"
        ],
        LayerType.DATA_ACCESS: [
            "repository", "repo", "dao", "data_access", "store",
            "persistence", "database", "db", "query"
        ],
        LayerType.DOMAIN: [
            "model", "entity", "domain", "aggregate", "value_object",
            "schema", "type", "dto"
        ],
        LayerType.INFRASTRUCTURE: [
            "infrastructure", "infra", "config", "middleware",
            "adapter", "gateway", "client", "external"
        ]
    }

    DESIGN_PATTERNS = {
        "repository": [r"class.*Repository", r"def\s+find_by", r"def\s+save\(", r"def\s+delete\("],
        "factory": [r"class.*Factory", r"def\s+create_", r"@staticmethod.*create"],
        "singleton": [r"_instance\s*=\s*None", r"def\s+get_instance"],
        "dependency_injection": [r"def\s+__init__\(self,\s*\w+:", r"@inject", r"@Inject"],
        "unit_of_work": [r"class.*UnitOfWork", r"def\s+commit\(", r"def\s+rollback\("],
        "strategy": [r"class.*Strategy", r"def\s+execute\(self", r"set_strategy"],
        "observer": [r"def\s+subscribe", r"def\s+notify", r"observers.*=.*\[\]"],
        "decorator": [r"def\s+__call__\(self", r"@wraps", r"functools\.wraps"],
        "cqrs": [r"Command", r"Query", r"CommandHandler", r"QueryHandler"]
    }

    ANTI_PATTERNS = {
        "god_class": {"threshold": 500, "description": "Class with too many methods/lines"},
        "feature_envy": {"pattern": r"self\.\w+\.\w+\.\w+", "description": "Excessive chaining"},
        "data_class": {"pattern": r"class.*:\s*\n\s+\w+:\s*\w+\s*\n", "description": "Class with only data, no behavior"},
        "circular_import": {"description": "Circular dependency between modules"},
        "magic_numbers": {"pattern": r"(?<!['\"])\b\d{2,}\b(?!['\"])", "description": "Hardcoded numeric values"},
        "long_method": {"threshold": 50, "description": "Method with too many lines"},
        "deep_nesting": {"threshold": 4, "description": "Deeply nested conditionals/loops"}
    }

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.analysis_result = None

    def analyze(self, codebase_path: str) -> ArchitectureAnalysisResult:
        """Perform complete architecture analysis."""
        path = Path(codebase_path)
        if not path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")

        # Initialize result
        self.analysis_result = ArchitectureAnalysisResult(
            architecture_type=ArchitectureType.UNKNOWN,
            overall_score=0
        )

        # Collect all Python files
        python_files = list(path.rglob("*.py"))

        # Analyze layers
        self._analyze_layers(python_files)

        # Detect architecture type
        self._detect_architecture_type()

        # Detect design patterns
        self._detect_patterns(python_files)

        # Detect anti-patterns
        self._detect_anti_patterns(python_files)

        # Analyze dependencies
        self._analyze_dependencies(python_files)

        # Calculate overall score
        self._calculate_score()

        # Generate recommendations
        self._generate_recommendations()

        return self.analysis_result

    def _analyze_layers(self, files: list[Path]) -> None:
        """Categorize files into architectural layers."""
        for file_path in files:
            layer = self._identify_layer(file_path)
            layer_name = layer.value

            if layer_name not in self.analysis_result.layers:
                self.analysis_result.layers[layer_name] = LayerAnalysis(layer_type=layer)

            self.analysis_result.layers[layer_name].files.append(str(file_path))

            # Analyze layer-specific issues
            issues = self._check_layer_violations(file_path, layer)
            self.analysis_result.layers[layer_name].issues.extend(issues)

    def _identify_layer(self, file_path: Path) -> LayerType:
        """Identify which architectural layer a file belongs to."""
        path_str = str(file_path).lower()
        file_name = file_path.stem.lower()

        for layer_type, indicators in self.LAYER_INDICATORS.items():
            for indicator in indicators:
                if indicator in path_str or indicator in file_name:
                    return layer_type

        return LayerType.UNKNOWN

    def _check_layer_violations(self, file_path: Path, layer: LayerType) -> list[Issue]:
        """Check for layer-specific violations."""
        issues = []

        try:
            content = file_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return issues

        # Check for business logic in presentation layer
        if layer == LayerType.PRESENTATION:
            if self._contains_database_operations(content):
                issues.append(Issue(
                    severity="high",
                    category="layer_violation",
                    description="Database operations found in presentation layer",
                    file_path=str(file_path),
                    recommendation="Move database operations to data access layer"
                ))

        # Check for direct HTTP handling in business layer
        if layer == LayerType.BUSINESS:
            if self._contains_http_handling(content):
                issues.append(Issue(
                    severity="medium",
                    category="layer_violation",
                    description="HTTP handling found in business layer",
                    file_path=str(file_path),
                    recommendation="Keep HTTP concerns in presentation layer"
                ))

        return issues

    def _contains_database_operations(self, content: str) -> bool:
        """Check if content contains direct database operations."""
        db_patterns = [
            r"\.execute\s*\(",
            r"\.query\s*\(",
            r"SELECT\s+.*\s+FROM",
            r"INSERT\s+INTO",
            r"UPDATE\s+.*\s+SET",
            r"DELETE\s+FROM",
            r"session\.add\(",
            r"session\.commit\("
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in db_patterns)

    def _contains_http_handling(self, content: str) -> bool:
        """Check if content contains HTTP handling code."""
        http_patterns = [
            r"request\.(json|form|args)",
            r"Response\(",
            r"jsonify\(",
            r"@app\.(get|post|put|delete)",
            r"@router\.(get|post|put|delete)"
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in http_patterns)

    def _detect_architecture_type(self) -> None:
        """Detect the overall architecture type based on structure."""
        layers = self.analysis_result.layers

        # Check for hexagonal/ports-and-adapters
        if "infrastructure" in layers and "domain" in layers:
            if self._has_ports_and_adapters_structure(layers):
                self.analysis_result.architecture_type = ArchitectureType.HEXAGONAL
                return

        # Check for clean architecture
        if self._has_clean_architecture_structure(layers):
            self.analysis_result.architecture_type = ArchitectureType.CLEAN
            return

        # Check for MVC
        if "presentation" in layers and "business" in layers:
            self.analysis_result.architecture_type = ArchitectureType.MVC
            return

        # Check for layered
        if len(layers) >= 2:
            self.analysis_result.architecture_type = ArchitectureType.LAYERED
            return

        self.analysis_result.architecture_type = ArchitectureType.MONOLITH

    def _has_ports_and_adapters_structure(self, layers: dict) -> bool:
        """Check for ports and adapters (hexagonal) structure."""
        # Look for port/adapter naming conventions
        infra_files = layers.get("infrastructure", LayerAnalysis(layer_type=LayerType.INFRASTRUCTURE)).files
        return any("adapter" in f.lower() or "port" in f.lower() for f in infra_files)

    def _has_clean_architecture_structure(self, layers: dict) -> bool:
        """Check for clean architecture structure."""
        required_layers = ["domain", "business", "infrastructure"]
        return all(layer in layers for layer in required_layers)

    def _detect_patterns(self, files: list[Path]) -> None:
        """Detect design patterns in use."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern_name, patterns in self.DESIGN_PATTERNS.items():
                if any(re.search(p, content) for p in patterns):
                    if pattern_name not in self.analysis_result.patterns_detected:
                        self.analysis_result.patterns_detected.append(pattern_name)

    def _detect_anti_patterns(self, files: list[Path]) -> None:
        """Detect anti-patterns in the codebase."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content)
            except (OSError, UnicodeDecodeError, SyntaxError):
                continue

            # Check for god class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                    if method_count > 20:
                        if "god_class" not in self.analysis_result.anti_patterns_detected:
                            self.analysis_result.anti_patterns_detected.append("god_class")
                            self.analysis_result.recommendations.append(Issue(
                                severity="medium",
                                category="anti_pattern",
                                description=f"God class detected: {node.name} has {method_count} methods",
                                file_path=str(file_path),
                                line_number=node.lineno,
                                recommendation="Consider splitting into smaller, focused classes"
                            ))

            # Check for long methods
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if hasattr(node, 'end_lineno') and node.end_lineno:
                        method_length = node.end_lineno - node.lineno
                        if method_length > self.ANTI_PATTERNS["long_method"]["threshold"]:
                            if "long_method" not in self.analysis_result.anti_patterns_detected:
                                self.analysis_result.anti_patterns_detected.append("long_method")

    def _analyze_dependencies(self, files: list[Path]) -> None:
        """Analyze import dependencies between modules."""
        imports_map: dict[str, list[str]] = {}

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content)
            except (OSError, UnicodeDecodeError, SyntaxError):
                continue

            module_name = str(file_path)
            imports_map[module_name] = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports_map[module_name].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports_map[module_name].append(node.module)

        # Check for dependency direction violations
        self._check_dependency_direction(imports_map)

    def _check_dependency_direction(self, imports_map: dict[str, list[str]]) -> None:
        """Check that dependencies flow in the correct direction."""
        for module, imports in imports_map.items():
            module_layer = self._identify_layer(Path(module))

            for imported in imports:
                # Presentation layer should not be imported by business layer
                if module_layer == LayerType.BUSINESS:
                    if any(ind in imported.lower() for ind in self.LAYER_INDICATORS[LayerType.PRESENTATION]):
                        self.analysis_result.dependency_issues.append(Issue(
                            severity="high",
                            category="dependency_violation",
                            description="Business layer imports from presentation layer",
                            file_path=module,
                            recommendation="Invert dependency - business layer should not depend on presentation"
                        ))

    def _calculate_score(self) -> int:
        """Calculate overall architecture score."""
        base_score = 100

        # Deduct for anti-patterns
        base_score -= len(self.analysis_result.anti_patterns_detected) * 5

        # Deduct for dependency issues
        base_score -= len(self.analysis_result.dependency_issues) * 10

        # Deduct for layer violations
        for layer_analysis in self.analysis_result.layers.values():
            base_score -= len(layer_analysis.issues) * 3

        # Add points for good patterns
        base_score += len(self.analysis_result.patterns_detected) * 2

        # Ensure score is within bounds
        self.analysis_result.overall_score = max(0, min(100, base_score))

        # Calculate individual layer scores
        for layer_name, layer_analysis in self.analysis_result.layers.items():
            layer_score = 100 - (len(layer_analysis.issues) * 10)
            layer_analysis.score = max(0, min(100, layer_score))

        return self.analysis_result.overall_score

    def _generate_recommendations(self) -> None:
        """Generate actionable recommendations based on analysis."""
        # Add recommendations based on missing patterns
        if "repository" not in self.analysis_result.patterns_detected:
            has_data_layer = "data_access" in self.analysis_result.layers
            if has_data_layer:
                self.analysis_result.recommendations.append(Issue(
                    severity="low",
                    category="pattern_suggestion",
                    description="Consider implementing Repository pattern",
                    file_path="",
                    recommendation="Repository pattern can improve testability and separation of concerns"
                ))

        if "dependency_injection" not in self.analysis_result.patterns_detected:
            self.analysis_result.recommendations.append(Issue(
                severity="medium",
                category="pattern_suggestion",
                description="Consider implementing Dependency Injection",
                file_path="",
                recommendation="DI improves testability and makes dependencies explicit"
            ))

    def get_summary(self) -> dict:
        """Get a summary of the analysis for reporting."""
        if not self.analysis_result:
            return {}

        return {
            "architecture_type": self.analysis_result.architecture_type.value,
            "overall_score": self.analysis_result.overall_score,
            "layers_found": list(self.analysis_result.layers.keys()),
            "patterns_detected": self.analysis_result.patterns_detected,
            "anti_patterns_detected": self.analysis_result.anti_patterns_detected,
            "total_issues": sum(
                len(layer.issues) for layer in self.analysis_result.layers.values()
            ) + len(self.analysis_result.dependency_issues),
            "recommendations_count": len(self.analysis_result.recommendations)
        }


def analyze_architecture(codebase_path: str, config: Optional[dict] = None) -> dict:
    """Convenience function to analyze architecture and return summary."""
    analyzer = ArchitectureAnalyzer(config)
    result = analyzer.analyze(codebase_path)
    return {
        "result": result,
        "summary": analyzer.get_summary()
    }
