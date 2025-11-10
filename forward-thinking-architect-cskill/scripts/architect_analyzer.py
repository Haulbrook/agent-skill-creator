"""
Forward-Thinking Architect Analyzer
Main orchestrator for architectural analysis and pain point detection
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(Enum):
    """Analysis category types"""
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    QUALITY = "quality"
    EVOLUTION = "evolution"
    SCALABILITY = "scalability"
    SECURITY = "security"


@dataclass
class ArchitecturalIssue:
    """Represents an identified architectural issue"""
    title: str
    severity: Severity
    category: Category
    location: str
    description: str
    impact: str
    effort: str
    priority: int
    recommendation: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            **asdict(self),
            'severity': self.severity.value,
            'category': self.category.value
        }


@dataclass
class ExtensionPoint:
    """Represents an opportunity for extension point"""
    name: str
    location: str
    description: str
    pattern: str
    benefits: List[str]
    implementation_notes: str


@dataclass
class ScalabilityConstraint:
    """Represents a scalability constraint or bottleneck"""
    component: str
    constraint_type: str
    current_capacity: str
    projected_failure_point: str
    scaling_strategy: str
    implementation_complexity: str


class ArchitectAnalyzer:
    """
    Main architectural analyzer that coordinates all analysis dimensions
    """

    def __init__(self, project_path: str):
        """
        Initialize the architectural analyzer

        Args:
            project_path: Root path of the project to analyze
        """
        self.project_path = Path(project_path)
        self.issues: List[ArchitecturalIssue] = []
        self.extension_points: List[ExtensionPoint] = []
        self.scalability_constraints: List[ScalabilityConstraint] = []
        self.metrics: Dict[str, Any] = {}

    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive architectural analysis

        Returns:
            Dict containing all analysis results
        """
        print("🔍 Starting forward-thinking architectural analysis...")

        # Run multi-dimensional analysis
        self._analyze_structure()
        self._analyze_quality()
        self._analyze_scalability()
        self._analyze_extensibility()
        self._analyze_maintainability()

        # Generate report
        report = self._generate_report()

        print("✅ Analysis complete!")
        return report

    def _analyze_structure(self):
        """Analyze structural aspects: components, dependencies, coupling"""
        print("📐 Analyzing structural aspects...")

        # Analyze file organization
        file_count = sum(1 for _ in self.project_path.rglob('*.py'))

        if file_count == 0:
            self.issues.append(ArchitecturalIssue(
                title="No Python files found",
                severity=Severity.MEDIUM,
                category=Category.STRUCTURAL,
                location=str(self.project_path),
                description="The project directory contains no Python files for analysis",
                impact="Cannot perform code-level architectural analysis",
                effort="N/A",
                priority=3,
                recommendation="Ensure the correct project path is provided"
            ))
            return

        self.metrics['total_python_files'] = file_count

        # Check for common structural issues
        self._check_god_classes()
        self._check_circular_dependencies()
        self._check_layer_violations()

    def _check_god_classes(self):
        """Detect God classes (classes that do too much)"""
        # Scan for large files (potential God classes)
        for py_file in self.project_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])

                    if loc > 500:
                        self.issues.append(ArchitecturalIssue(
                            title=f"Potential God Class: {py_file.name}",
                            severity=Severity.HIGH if loc > 1000 else Severity.MEDIUM,
                            category=Category.STRUCTURAL,
                            location=str(py_file.relative_to(self.project_path)),
                            description=f"File contains {loc} lines of code, suggesting too many responsibilities",
                            impact="Difficult to maintain, test, and extend. Changes ripple across multiple concerns.",
                            effort="Medium to High - requires careful refactoring into smaller, focused components",
                            priority=2,
                            recommendation=f"Refactor {py_file.name} into smaller, single-responsibility classes following SRP"
                        ))
            except Exception as e:
                pass  # Skip files that can't be read

    def _check_circular_dependencies(self):
        """Check for circular dependency patterns"""
        # Simplified check for import cycles
        import_graph: Dict[str, List[str]] = {}

        for py_file in self.project_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    imports = []
                    for line in content.split('\n'):
                        if line.strip().startswith(('import ', 'from ')):
                            imports.append(line.strip())

                    if imports:
                        import_graph[str(py_file)] = imports
            except Exception:
                pass

        if len(import_graph) > 10:
            self.issues.append(ArchitecturalIssue(
                title="Complex import structure detected",
                severity=Severity.MEDIUM,
                category=Category.STRUCTURAL,
                location="Project-wide",
                description=f"Found {len(import_graph)} files with import statements, indicating complex dependencies",
                impact="Potential for circular dependencies and tight coupling between modules",
                effort="Medium - requires dependency analysis and potential restructuring",
                priority=3,
                recommendation="Review import structure and consider introducing dependency injection or interfaces to break cycles"
            ))

    def _check_layer_violations(self):
        """Check for architectural layer violations"""
        # Look for common layer violation patterns
        has_layers = any([
            (self.project_path / 'models').exists(),
            (self.project_path / 'views').exists(),
            (self.project_path / 'controllers').exists(),
            (self.project_path / 'services').exists(),
            (self.project_path / 'repositories').exists(),
        ])

        if has_layers:
            self.metrics['layered_architecture'] = True
            # In a real implementation, would check for violations
            # For now, note that layering exists
        else:
            self.issues.append(ArchitecturalIssue(
                title="No clear architectural layers",
                severity=Severity.MEDIUM,
                category=Category.STRUCTURAL,
                location="Project structure",
                description="Project does not follow a clear layered architecture pattern",
                impact="Difficult to maintain separation of concerns and enforce architectural boundaries",
                effort="Medium - requires organizational restructuring",
                priority=4,
                recommendation="Consider organizing code into clear layers: presentation, business logic, data access"
            ))

    def _analyze_quality(self):
        """Analyze code quality metrics"""
        print("📊 Analyzing code quality...")

        # Calculate basic quality metrics
        total_loc = 0
        total_files = 0
        files_without_docstrings = 0

        for py_file in self.project_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
                    total_loc += loc
                    total_files += 1

                    # Check for module docstring
                    if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                        files_without_docstrings += 1
            except Exception:
                pass

        self.metrics['total_loc'] = total_loc
        self.metrics['average_loc_per_file'] = total_loc / total_files if total_files > 0 else 0

        # Report documentation issues
        if files_without_docstrings > total_files * 0.3:
            self.issues.append(ArchitecturalIssue(
                title="Insufficient documentation",
                severity=Severity.MEDIUM,
                category=Category.QUALITY,
                location="Project-wide",
                description=f"{files_without_docstrings} out of {total_files} files lack module docstrings",
                impact="Reduced code maintainability and developer onboarding difficulty",
                effort="Low - add docstrings to modules and key functions",
                priority=5,
                recommendation="Add comprehensive docstrings following PEP 257 conventions"
            ))

    def _analyze_scalability(self):
        """Analyze scalability concerns"""
        print("📈 Analyzing scalability...")

        # Check for common scalability anti-patterns
        self._check_synchronous_bottlenecks()
        self._check_state_management()
        self._check_database_patterns()

    def _check_synchronous_bottlenecks(self):
        """Check for synchronous operations that could become bottlenecks"""
        blocking_patterns = ['time.sleep', 'requests.get', 'requests.post', 'urllib.request']
        found_blocking = False

        for py_file in self.project_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in blocking_patterns:
                        if pattern in content:
                            found_blocking = True
                            break
            except Exception:
                pass

        if found_blocking:
            self.scalability_constraints.append(ScalabilityConstraint(
                component="HTTP/Network Operations",
                constraint_type="Synchronous I/O",
                current_capacity="Limited by thread pool size",
                projected_failure_point="High traffic will exhaust thread pool",
                scaling_strategy="Implement async/await patterns or queue-based processing",
                implementation_complexity="Medium"
            ))

    def _check_state_management(self):
        """Check for stateful patterns that limit scaling"""
        # Look for in-memory state patterns
        state_patterns = ['global ', 'session[', 'cache = {}', 'cache = dict()']
        found_state = False

        for py_file in self.project_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in state_patterns:
                        if pattern in content:
                            found_state = True
                            break
            except Exception:
                pass

        if found_state:
            self.scalability_constraints.append(ScalabilityConstraint(
                component="State Management",
                constraint_type="In-memory state",
                current_capacity="Single server only",
                projected_failure_point="Cannot horizontally scale",
                scaling_strategy="Externalize state to Redis, Memcached, or distributed cache",
                implementation_complexity="Medium to High"
            ))

    def _check_database_patterns(self):
        """Check database usage patterns"""
        db_patterns = ['db.query', 'Session()', 'connection.execute', 'cursor.execute']
        found_db = False

        for py_file in self.project_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in db_patterns:
                        if pattern in content:
                            found_db = True
                            break
            except Exception:
                pass

        if found_db:
            # Check for N+1 query patterns or missing connection pooling
            self.issues.append(ArchitecturalIssue(
                title="Database usage patterns need review",
                severity=Severity.MEDIUM,
                category=Category.SCALABILITY,
                location="Data access layer",
                description="Database operations detected - ensure proper connection pooling and query optimization",
                impact="Database can become bottleneck under load",
                effort="Medium - implement connection pooling and query optimization",
                priority=3,
                recommendation="Review for N+1 queries, implement connection pooling, consider read replicas"
            ))

    def _analyze_extensibility(self):
        """Identify opportunities for extension points"""
        print("🔌 Analyzing extensibility...")

        # Look for hardcoded dependencies that could be plugin points
        self._identify_plugin_opportunities()
        self._check_interface_usage()

    def _identify_plugin_opportunities(self):
        """Identify where plugin systems would be beneficial"""
        # Check for strategy pattern opportunities
        conditional_patterns = 0

        for py_file in self.project_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Count if/elif chains (potential strategy pattern)
                    conditional_patterns += content.count('elif ')
            except Exception:
                pass

        if conditional_patterns > 10:
            self.extension_points.append(ExtensionPoint(
                name="Strategy Pattern Opportunities",
                location="Multiple locations with if/elif chains",
                description=f"Found {conditional_patterns} elif statements that could be refactored to strategy pattern",
                pattern="Strategy Pattern",
                benefits=[
                    "Easy addition of new strategies without modifying existing code",
                    "Better testability through strategy injection",
                    "Plugin-friendly architecture"
                ],
                implementation_notes="Create abstract strategy interface and concrete implementations"
            ))

    def _check_interface_usage(self):
        """Check for interface/abstract class usage"""
        has_abc = False

        for py_file in self.project_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'from abc import' in content or 'import abc' in content:
                        has_abc = True
                        break
            except Exception:
                pass

        if not has_abc:
            self.extension_points.append(ExtensionPoint(
                name="Interface-based Design",
                location="Project-wide",
                description="Project could benefit from interface-based design using abstract base classes",
                pattern="Dependency Inversion Principle",
                benefits=[
                    "Loose coupling between components",
                    "Easy to mock for testing",
                    "Plugin architecture readiness"
                ],
                implementation_notes="Identify key abstractions and define ABC interfaces"
            ))

    def _analyze_maintainability(self):
        """Analyze maintainability concerns"""
        print("🔧 Analyzing maintainability...")

        # Check for test coverage
        has_tests = (self.project_path / 'tests').exists() or \
                    (self.project_path / 'test').exists() or \
                    any(self.project_path.rglob('test_*.py'))

        if not has_tests:
            self.issues.append(ArchitecturalIssue(
                title="No test suite detected",
                severity=Severity.HIGH,
                category=Category.QUALITY,
                location="Project-wide",
                description="No test directory or test files found",
                impact="High risk of regressions, difficult to refactor with confidence",
                effort="High - requires building comprehensive test suite",
                priority=1,
                recommendation="Implement test suite with unit, integration, and end-to-end tests"
            ))

        # Check for requirements/dependencies management
        has_requirements = (self.project_path / 'requirements.txt').exists() or \
                          (self.project_path / 'pyproject.toml').exists() or \
                          (self.project_path / 'Pipfile').exists()

        if not has_requirements:
            self.issues.append(ArchitecturalIssue(
                title="No dependency management",
                severity=Severity.MEDIUM,
                category=Category.QUALITY,
                location="Project root",
                description="No requirements.txt, pyproject.toml, or Pipfile found",
                impact="Difficult to reproduce environment, deployment issues",
                effort="Low - create requirements file",
                priority=4,
                recommendation="Create requirements.txt or pyproject.toml with pinned versions"
            ))

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        # Sort issues by priority
        self.issues.sort(key=lambda x: (x.priority, x.severity.value))

        # Calculate health score
        health_score = self._calculate_health_score()

        return {
            'summary': {
                'health_score': health_score,
                'total_issues': len(self.issues),
                'critical_issues': len([i for i in self.issues if i.severity == Severity.CRITICAL]),
                'high_issues': len([i for i in self.issues if i.severity == Severity.HIGH]),
                'extension_opportunities': len(self.extension_points),
                'scalability_constraints': len(self.scalability_constraints)
            },
            'metrics': self.metrics,
            'issues': [issue.to_dict() for issue in self.issues[:10]],  # Top 10
            'extension_points': [asdict(ep) for ep in self.extension_points],
            'scalability_constraints': [asdict(sc) for sc in self.scalability_constraints],
            'recommendations': self._generate_recommendations()
        }

    def _calculate_health_score(self) -> int:
        """Calculate overall architectural health score (0-100)"""
        score = 100

        for issue in self.issues:
            if issue.severity == Severity.CRITICAL:
                score -= 15
            elif issue.severity == Severity.HIGH:
                score -= 10
            elif issue.severity == Severity.MEDIUM:
                score -= 5
            elif issue.severity == Severity.LOW:
                score -= 2

        return max(0, score)

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Critical issues first
        critical = [i for i in self.issues if i.severity == Severity.CRITICAL]
        if critical:
            recommendations.append({
                'phase': 'Immediate (0-1 month)',
                'focus': 'Critical Issues',
                'action': f"Address {len(critical)} critical architectural issues",
                'items': [i.title for i in critical[:3]]
            })

        # High priority issues
        high = [i for i in self.issues if i.severity == Severity.HIGH]
        if high:
            recommendations.append({
                'phase': 'Short-term (1-3 months)',
                'focus': 'High Priority Issues',
                'action': f"Resolve {len(high)} high-priority concerns",
                'items': [i.title for i in high[:3]]
            })

        # Extension points
        if self.extension_points:
            recommendations.append({
                'phase': 'Medium-term (3-6 months)',
                'focus': 'Extensibility',
                'action': 'Implement extension points for future growth',
                'items': [ep.name for ep in self.extension_points[:3]]
            })

        # Scalability
        if self.scalability_constraints:
            recommendations.append({
                'phase': 'Medium-term (3-6 months)',
                'focus': 'Scalability',
                'action': 'Address scaling constraints',
                'items': [sc.component for sc in self.scalability_constraints]
            })

        return recommendations


def main():
    """Main entry point for command-line usage"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python architect_analyzer.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]

    if not os.path.exists(project_path):
        print(f"Error: Project path '{project_path}' does not exist")
        sys.exit(1)

    analyzer = ArchitectAnalyzer(project_path)
    report = analyzer.analyze()

    # Print summary
    print("\n" + "="*80)
    print("🎯 ARCHITECTURAL ANALYSIS REPORT")
    print("="*80)
    print(f"\n📊 Health Score: {report['summary']['health_score']}/100")
    print(f"🔍 Total Issues: {report['summary']['total_issues']}")
    print(f"⚠️  Critical: {report['summary']['critical_issues']}")
    print(f"🔴 High: {report['summary']['high_issues']}")
    print(f"🔌 Extension Opportunities: {report['summary']['extension_opportunities']}")
    print(f"📈 Scalability Constraints: {report['summary']['scalability_constraints']}")

    # Save full report
    output_file = 'architectural_analysis_report.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Full report saved to: {output_file}")


if __name__ == '__main__':
    main()
