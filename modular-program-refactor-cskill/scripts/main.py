#!/usr/bin/env python3
"""
Modular Program Refactor Skill - Main Orchestrator

This orchestrator coordinates the entire modular refactoring process:
1. Analyzes existing codebase architecture
2. Maps dependencies and relationships
3. Identifies modular boundaries
4. Plans reconstruction strategy
5. Executes refactoring (or provides detailed plan)
6. Optionally hands off to Forward Thinker for enhancement
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisDepth(Enum):
    """Depth of architectural analysis"""
    SHALLOW = "shallow"
    MEDIUM = "medium"
    DEEP = "deep"


class TargetArchitecture(Enum):
    """Target architectural patterns"""
    LAYERED = "layered"
    HEXAGONAL = "hexagonal"
    MICROSERVICES = "microservices"
    PLUGIN = "plugin"
    MODULAR_MONOLITH = "modular_monolith"
    EVENT_DRIVEN = "event_driven"


@dataclass
class RefactorConfig:
    """Configuration for the refactoring process"""
    analysis_depth: AnalysisDepth = AnalysisDepth.DEEP
    preserve_comments: bool = True
    strict_equivalence: bool = True
    target_architecture: TargetArchitecture = TargetArchitecture.LAYERED
    language_version: str = "auto"
    forward_thinking_integration: bool = True
    generate_tests: bool = True
    documentation_level: str = "comprehensive"
    output_directory: Optional[Path] = None
    dry_run: bool = False


@dataclass
class ArchitectureAnalysis:
    """Results from architectural analysis"""
    total_files: int
    total_lines: int
    languages_detected: List[str]
    entry_points: List[str]
    dependency_graph: Dict[str, List[str]]
    module_candidates: List[Dict[str, Any]]
    complexity_metrics: Dict[str, Any]
    coupling_score: float
    cohesion_score: float
    patterns_detected: List[str]
    anti_patterns: List[str]
    technical_debt_items: List[str]
    recommendations: List[str]


@dataclass
class ModularDesign:
    """Proposed modular architecture design"""
    central_module: Dict[str, Any]
    modules: List[Dict[str, Any]]
    interfaces: List[Dict[str, Any]]
    layer_hierarchy: List[str]
    migration_phases: List[Dict[str, Any]]
    estimated_effort: str


@dataclass
class RefactoringResult:
    """Complete refactoring result"""
    success: bool
    analysis: ArchitectureAnalysis
    design: ModularDesign
    execution_log: List[str]
    forward_thinking_handoff: Optional[Dict[str, Any]]
    error_message: Optional[str] = None


class ModularRefactorOrchestrator:
    """
    Main orchestrator for the modular refactoring process

    Coordinates analysis, planning, and execution phases
    """

    def __init__(self, config: RefactorConfig):
        """
        Initialize the orchestrator

        Args:
            config: Configuration for refactoring process
        """
        self.config = config
        self.logger = logging.getLogger(__name__ + ".Orchestrator")

        # Import analyzers (lazy loading to avoid circular dependencies)
        self.architecture_analyzer = None
        self.dependency_mapper = None
        self.modular_planner = None
        self.forward_thinker_connector = None

    def run(self, codebase_path: Path) -> RefactoringResult:
        """
        Execute the complete refactoring process

        Args:
            codebase_path: Path to the codebase to refactor

        Returns:
            RefactoringResult with all analysis and execution details
        """
        self.logger.info(f"Starting modular refactoring for: {codebase_path}")
        execution_log = []

        try:
            # Phase 1: Discovery & Analysis
            self.logger.info("Phase 1: Discovery & Analysis")
            execution_log.append("Starting Phase 1: Discovery & Analysis")

            analysis = self._analyze_architecture(codebase_path)
            execution_log.append(f"Analyzed {analysis.total_files} files, {analysis.total_lines} lines")
            execution_log.append(f"Detected languages: {', '.join(analysis.languages_detected)}")
            execution_log.append(f"Coupling score: {analysis.coupling_score:.2f}")
            execution_log.append(f"Cohesion score: {analysis.cohesion_score:.2f}")

            # Phase 2: Architectural Planning
            self.logger.info("Phase 2: Architectural Planning")
            execution_log.append("Starting Phase 2: Architectural Planning")

            design = self._plan_modular_architecture(analysis, codebase_path)
            execution_log.append(f"Designed {len(design.modules)} modules")
            execution_log.append(f"Central module: {design.central_module['name']}")
            execution_log.append(f"Migration phases: {len(design.migration_phases)}")

            # Phase 3: Reconstruction (if not dry-run)
            if not self.config.dry_run:
                self.logger.info("Phase 3: Reconstruction")
                execution_log.append("Starting Phase 3: Reconstruction")

                self._execute_reconstruction(design, codebase_path)
                execution_log.append("Reconstruction completed successfully")
            else:
                execution_log.append("Dry-run mode: Skipping reconstruction execution")

            # Phase 4: Forward-Thinking Integration (if enabled)
            forward_thinking_handoff = None
            if self.config.forward_thinking_integration:
                self.logger.info("Phase 4: Forward-Thinking Integration")
                execution_log.append("Starting Phase 4: Forward-Thinking Integration")

                forward_thinking_handoff = self._prepare_forward_thinking_handoff(
                    analysis, design
                )
                execution_log.append("Prepared handoff package for Forward Thinker Skill")

            # Success!
            return RefactoringResult(
                success=True,
                analysis=analysis,
                design=design,
                execution_log=execution_log,
                forward_thinking_handoff=forward_thinking_handoff
            )

        except Exception as e:
            self.logger.error(f"Refactoring failed: {str(e)}", exc_info=True)
            execution_log.append(f"ERROR: {str(e)}")

            return RefactoringResult(
                success=False,
                analysis=ArchitectureAnalysis(
                    total_files=0, total_lines=0, languages_detected=[],
                    entry_points=[], dependency_graph={}, module_candidates=[],
                    complexity_metrics={}, coupling_score=0.0, cohesion_score=0.0,
                    patterns_detected=[], anti_patterns=[], technical_debt_items=[],
                    recommendations=[]
                ),
                design=ModularDesign(
                    central_module={}, modules=[], interfaces=[], layer_hierarchy=[],
                    migration_phases=[], estimated_effort="Unknown"
                ),
                execution_log=execution_log,
                forward_thinking_handoff=None,
                error_message=str(e)
            )

    def _analyze_architecture(self, codebase_path: Path) -> ArchitectureAnalysis:
        """
        Perform deep architectural analysis

        Args:
            codebase_path: Path to codebase

        Returns:
            ArchitectureAnalysis results
        """
        from analyzers.architecture_analyzer import ArchitectureAnalyzer
        from analyzers.dependency_mapper import DependencyMapper

        self.logger.info("Analyzing codebase architecture...")

        # Initialize analyzers
        arch_analyzer = ArchitectureAnalyzer(self.config.analysis_depth)
        dep_mapper = DependencyMapper()

        # Scan codebase
        files = list(codebase_path.rglob("*.*"))
        source_files = [f for f in files if f.suffix in [
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs',
            '.rb', '.php', '.cpp', '.c', '.h', '.cs', '.kt', '.swift'
        ]]

        self.logger.info(f"Found {len(source_files)} source files")

        # Perform analysis
        languages_detected = arch_analyzer.detect_languages(source_files)
        entry_points = arch_analyzer.find_entry_points(source_files)
        dependency_graph = dep_mapper.build_dependency_graph(source_files)
        module_candidates = arch_analyzer.identify_module_candidates(
            source_files, dependency_graph
        )

        # Calculate metrics
        complexity_metrics = arch_analyzer.calculate_complexity_metrics(source_files)
        coupling_score = arch_analyzer.calculate_coupling(dependency_graph)
        cohesion_score = arch_analyzer.calculate_cohesion(module_candidates)

        # Pattern detection
        patterns_detected = arch_analyzer.detect_patterns(source_files, dependency_graph)
        anti_patterns = arch_analyzer.detect_anti_patterns(
            source_files, dependency_graph, coupling_score
        )

        # Technical debt assessment
        technical_debt = arch_analyzer.assess_technical_debt(
            source_files, anti_patterns, complexity_metrics
        )

        # Generate recommendations
        recommendations = arch_analyzer.generate_recommendations(
            coupling_score, cohesion_score, patterns_detected, anti_patterns
        )

        # Count total lines
        total_lines = sum(
            len(f.read_text(errors='ignore').splitlines())
            for f in source_files
        )

        return ArchitectureAnalysis(
            total_files=len(source_files),
            total_lines=total_lines,
            languages_detected=languages_detected,
            entry_points=entry_points,
            dependency_graph=dependency_graph,
            module_candidates=module_candidates,
            complexity_metrics=complexity_metrics,
            coupling_score=coupling_score,
            cohesion_score=cohesion_score,
            patterns_detected=patterns_detected,
            anti_patterns=anti_patterns,
            technical_debt_items=technical_debt,
            recommendations=recommendations
        )

    def _plan_modular_architecture(
        self, analysis: ArchitectureAnalysis, codebase_path: Path
    ) -> ModularDesign:
        """
        Plan the modular architecture reconstruction

        Args:
            analysis: Results from architecture analysis
            codebase_path: Path to codebase

        Returns:
            ModularDesign specification
        """
        from planners.modular_planner import ModularPlanner

        self.logger.info("Planning modular architecture...")

        planner = ModularPlanner(self.config.target_architecture)

        # Design central nervous system module
        central_module = planner.design_central_module(
            analysis.entry_points, analysis.dependency_graph
        )

        # Design peripheral modules
        modules = planner.design_modules(
            analysis.module_candidates, analysis.dependency_graph
        )

        # Define interfaces
        interfaces = planner.design_interfaces(modules, analysis.dependency_graph)

        # Establish layer hierarchy
        layer_hierarchy = planner.establish_layers(
            modules, self.config.target_architecture
        )

        # Create migration plan
        migration_phases = planner.create_migration_phases(
            modules, interfaces, analysis.dependency_graph
        )

        # Estimate effort
        estimated_effort = planner.estimate_effort(
            analysis.total_lines, len(modules), analysis.complexity_metrics
        )

        return ModularDesign(
            central_module=central_module,
            modules=modules,
            interfaces=interfaces,
            layer_hierarchy=layer_hierarchy,
            migration_phases=migration_phases,
            estimated_effort=estimated_effort
        )

    def _execute_reconstruction(
        self, design: ModularDesign, codebase_path: Path
    ) -> None:
        """
        Execute the modular reconstruction

        Args:
            design: Modular design specification
            codebase_path: Path to codebase
        """
        from planners.reconstruction_executor import ReconstructionExecutor

        self.logger.info("Executing modular reconstruction...")

        executor = ReconstructionExecutor(
            self.config, codebase_path, self.config.output_directory
        )

        # Execute each migration phase
        for phase in design.migration_phases:
            self.logger.info(f"Executing phase: {phase['name']}")
            executor.execute_phase(phase, design)

        # Generate tests if configured
        if self.config.generate_tests:
            self.logger.info("Generating equivalence tests...")
            executor.generate_equivalence_tests(design)

        # Update documentation
        if self.config.documentation_level != "minimal":
            self.logger.info("Updating documentation...")
            executor.update_documentation(design, self.config.documentation_level)

    def _prepare_forward_thinking_handoff(
        self, analysis: ArchitectureAnalysis, design: ModularDesign
    ) -> Dict[str, Any]:
        """
        Prepare handoff package for Forward Thinker Skill

        Args:
            analysis: Architecture analysis results
            design: Modular design specification

        Returns:
            Handoff package dictionary
        """
        self.logger.info("Preparing Forward Thinker handoff package...")

        handoff = {
            "summary": {
                "files_analyzed": analysis.total_files,
                "lines_of_code": analysis.total_lines,
                "languages": analysis.languages_detected,
                "coupling_score": analysis.coupling_score,
                "cohesion_score": analysis.cohesion_score
            },
            "current_architecture": {
                "patterns": analysis.patterns_detected,
                "anti_patterns": analysis.anti_patterns,
                "technical_debt": analysis.technical_debt_items
            },
            "modular_design": {
                "architecture_type": self.config.target_architecture.value,
                "module_count": len(design.modules),
                "modules": [m['name'] for m in design.modules],
                "central_module": design.central_module['name'],
                "layer_hierarchy": design.layer_hierarchy
            },
            "enhancement_opportunities": analysis.recommendations,
            "constraints": {
                "functional_equivalence_required": self.config.strict_equivalence,
                "languages": analysis.languages_detected,
                "existing_patterns": analysis.patterns_detected
            },
            "collaboration_prompt": (
                f"The codebase has been analyzed and restructured into a "
                f"{self.config.target_architecture.value} architecture with "
                f"{len(design.modules)} modules. Based on this foundation, please "
                f"propose innovative enhancements that maintain the core functionality "
                f"while introducing modern patterns and preparing for future growth. "
                f"Key constraints: {', '.join(analysis.languages_detected)} languages, "
                f"functional equivalence required, {analysis.coupling_score:.1f} current "
                f"coupling score (target: < 0.3)."
            )
        }

        return handoff


def main() -> int:
    """
    Main entry point for the skill

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Modular Program Refactor Skill - Analyze and restructure code into modular architecture"
    )

    parser.add_argument(
        "codebase_path",
        type=Path,
        help="Path to the codebase to analyze and refactor"
    )

    parser.add_argument(
        "--analysis-depth",
        type=str,
        choices=["shallow", "medium", "deep"],
        default="deep",
        help="Depth of architectural analysis (default: deep)"
    )

    parser.add_argument(
        "--target-architecture",
        type=str,
        choices=["layered", "hexagonal", "microservices", "plugin", "modular_monolith", "event_driven"],
        default="layered",
        help="Target architectural pattern (default: layered)"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for refactored code (default: <codebase>_refactored)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and plan without executing reconstruction"
    )

    parser.add_argument(
        "--no-forward-thinking",
        action="store_true",
        help="Disable Forward Thinker integration"
    )

    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip generating equivalence tests"
    )

    parser.add_argument(
        "--output-format",
        type=str,
        choices=["json", "text", "markdown"],
        default="markdown",
        help="Output format for results (default: markdown)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate codebase path
    if not args.codebase_path.exists():
        logger.error(f"Codebase path does not exist: {args.codebase_path}")
        return 1

    if not args.codebase_path.is_dir():
        logger.error(f"Codebase path must be a directory: {args.codebase_path}")
        return 1

    # Set default output directory
    output_dir = args.output_dir or (args.codebase_path.parent / f"{args.codebase_path.name}_refactored")

    # Create configuration
    config = RefactorConfig(
        analysis_depth=AnalysisDepth(args.analysis_depth),
        target_architecture=TargetArchitecture(args.target_architecture),
        output_directory=output_dir,
        dry_run=args.dry_run,
        forward_thinking_integration=not args.no_forward_thinking,
        generate_tests=not args.no_tests
    )

    # Run orchestrator
    orchestrator = ModularRefactorOrchestrator(config)
    result = orchestrator.run(args.codebase_path)

    # Output results
    if args.output_format == "json":
        output = {
            "success": result.success,
            "analysis": asdict(result.analysis),
            "design": asdict(result.design),
            "execution_log": result.execution_log,
            "forward_thinking_handoff": result.forward_thinking_handoff,
            "error_message": result.error_message
        }
        print(json.dumps(output, indent=2))

    elif args.output_format == "markdown":
        print("# Modular Program Refactor - Results\n")
        print(f"**Status**: {'✓ Success' if result.success else '✗ Failed'}\n")

        if not result.success:
            print(f"**Error**: {result.error_message}\n")
        else:
            print("## Architecture Analysis\n")
            print(f"- **Files Analyzed**: {result.analysis.total_files}")
            print(f"- **Total Lines**: {result.analysis.total_lines:,}")
            print(f"- **Languages**: {', '.join(result.analysis.languages_detected)}")
            print(f"- **Coupling Score**: {result.analysis.coupling_score:.2f}")
            print(f"- **Cohesion Score**: {result.analysis.cohesion_score:.2f}")
            print(f"- **Patterns Detected**: {', '.join(result.analysis.patterns_detected)}")

            if result.analysis.anti_patterns:
                print(f"- **Anti-Patterns**: {', '.join(result.analysis.anti_patterns)}")

            print("\n## Modular Design\n")
            print(f"- **Architecture**: {config.target_architecture.value}")
            print(f"- **Central Module**: {result.design.central_module['name']}")
            print(f"- **Module Count**: {len(result.design.modules)}")
            print(f"- **Migration Phases**: {len(result.design.migration_phases)}")
            print(f"- **Estimated Effort**: {result.design.estimated_effort}")

            print("\n## Recommendations\n")
            for rec in result.analysis.recommendations:
                print(f"- {rec}")

            if result.forward_thinking_handoff:
                print("\n## Forward Thinker Integration\n")
                print("Ready for handoff to Forward Thinker Skill for enhancement proposals.")

    else:  # text
        print(f"Refactoring {'succeeded' if result.success else 'failed'}")
        if not result.success:
            print(f"Error: {result.error_message}")
        else:
            print(f"Analyzed {result.analysis.total_files} files")
            print(f"Designed {len(result.design.modules)} modules")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
