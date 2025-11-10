"""
Modular Planner Module

Plans the modular architecture reconstruction:
- Designs central nervous system module
- Defines peripheral modules
- Establishes interfaces
- Creates migration phases
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class ModularPlanner:
    """
    Plans modular architecture reconstruction

    Takes analysis results and designs a clean modular structure
    with central orchestration and well-defined boundaries
    """

    def __init__(self, target_architecture: str):
        """
        Initialize planner

        Args:
            target_architecture: Target architecture pattern
        """
        self.target_architecture = target_architecture
        self.logger = logging.getLogger(__name__ + ".ModularPlanner")

    def design_central_module(
        self, entry_points: List[str], dependency_graph: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Design the central nervous system module

        This is the orchestrator that coordinates all other modules

        Args:
            entry_points: Application entry points
            dependency_graph: File dependencies

        Returns:
            Central module specification
        """
        self.logger.info("Designing central module...")

        return {
            "name": "core",
            "purpose": "Central orchestration and coordination",
            "responsibilities": [
                "Application initialization and startup",
                "Module lifecycle management",
                "Dependency injection and wiring",
                "Configuration management",
                "Cross-cutting concerns coordination"
            ],
            "contains": [
                "Application entry point",
                "Module registry",
                "Dependency container",
                "Configuration loader",
                "Logging setup"
            ],
            "interfaces": {
                "IModule": "Interface all modules must implement",
                "IConfiguration": "Configuration access interface",
                "IServiceLocator": "Service discovery interface"
            },
            "entry_points": entry_points
        }

    def design_modules(
        self, module_candidates: List[Dict[str, Any]], dependency_graph: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Design peripheral modules based on analysis

        Args:
            module_candidates: Identified module candidates
            dependency_graph: File dependencies

        Returns:
            List of module specifications
        """
        self.logger.info("Designing peripheral modules...")

        modules = []

        # Use module candidates as starting point
        for candidate in module_candidates:
            # Skip if too small
            if candidate['file_count'] < 2:
                continue

            module = {
                "name": self._sanitize_module_name(candidate['name']),
                "purpose": candidate['purpose'],
                "cohesion": candidate['cohesion'],
                "files": candidate['files'],
                "responsibilities": self._infer_responsibilities(candidate),
                "public_interface": self._design_module_interface(candidate),
                "internal_components": self._identify_internal_components(candidate),
                "dependencies": self._extract_module_dependencies(
                    candidate, dependency_graph
                )
            }

            modules.append(module)

        # Add standard modules if not present
        modules = self._ensure_standard_modules(modules)

        return modules

    def _sanitize_module_name(self, name: str) -> str:
        """Convert directory name to clean module name"""
        # Remove special characters and convert to snake_case
        clean = name.replace('-', '_').replace(' ', '_')
        clean = ''.join(c for c in clean if c.isalnum() or c == '_')
        return clean.lower()

    def _infer_responsibilities(self, candidate: Dict[str, Any]) -> List[str]:
        """Infer module responsibilities from structure"""
        purpose = candidate['purpose'].lower()

        responsibility_map = {
            "authentication": [
                "User authentication and authorization",
                "Session management",
                "Token generation and validation",
                "Permission checking"
            ],
            "database": [
                "Database connection management",
                "Query execution",
                "Transaction handling",
                "Data persistence"
            ],
            "api": [
                "HTTP request handling",
                "Route registration",
                "Request validation",
                "Response formatting"
            ],
            "model": [
                "Data structure definitions",
                "Data validation",
                "Business rules enforcement",
                "Data transformations"
            ],
            "service": [
                "Business logic execution",
                "Orchestration of domain operations",
                "External service integration",
                "Complex operation coordination"
            ]
        }

        # Match purpose to responsibility template
        for keyword, responsibilities in responsibility_map.items():
            if keyword in purpose:
                return responsibilities

        # Default responsibilities
        return [
            f"{candidate['purpose']} operations",
            "Internal state management",
            "Error handling for module domain"
        ]

    def _design_module_interface(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Design public interface for module"""
        name = self._sanitize_module_name(candidate['name'])

        return {
            "interface_name": f"I{name.title().replace('_', '')}",
            "methods": [
                {
                    "name": "initialize",
                    "purpose": "Initialize module resources",
                    "parameters": ["config: IConfiguration"],
                    "returns": "bool"
                },
                {
                    "name": "shutdown",
                    "purpose": "Clean up module resources",
                    "parameters": [],
                    "returns": "void"
                }
            ],
            "events": [
                f"{name}_initialized",
                f"{name}_error"
            ]
        }

    def _identify_internal_components(self, candidate: Dict[str, Any]) -> List[str]:
        """Identify internal components within module"""
        components = []

        # Analyze files to identify component types
        for file_path in candidate['files']:
            file_name = Path(file_path).stem.lower()

            if 'controller' in file_name:
                components.append(f"{file_name}: Request handler")
            elif 'service' in file_name:
                components.append(f"{file_name}: Business logic")
            elif 'model' in file_name:
                components.append(f"{file_name}: Data model")
            elif 'repository' in file_name:
                components.append(f"{file_name}: Data access")
            elif 'util' in file_name or 'helper' in file_name:
                components.append(f"{file_name}: Utility functions")
            else:
                components.append(f"{file_name}: Module component")

        return components

    def _extract_module_dependencies(
        self, candidate: Dict[str, Any], dependency_graph: Dict[str, List[str]]
    ) -> List[str]:
        """Extract module-level dependencies"""
        module_files = set(candidate['files'])
        external_deps = set()

        for file in candidate['files']:
            file_deps = dependency_graph.get(file, [])
            for dep in file_deps:
                if dep not in module_files:
                    # This is an external dependency
                    dep_module = self._file_to_module_name(dep)
                    external_deps.add(dep_module)

        return sorted(list(external_deps))

    def _file_to_module_name(self, file_path: str) -> str:
        """Convert file path to module name"""
        path = Path(file_path)
        # Use parent directory as module name
        return self._sanitize_module_name(path.parent.name)

    def _ensure_standard_modules(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure standard modules are present"""
        module_names = {m['name'] for m in modules}

        # Standard modules that should exist
        standard = {
            'config': {
                'name': 'config',
                'purpose': 'Configuration management',
                'responsibilities': ['Load configuration', 'Validate settings', 'Provide config access'],
                'public_interface': {'interface_name': 'IConfiguration', 'methods': [], 'events': []},
                'files': [],
                'internal_components': [],
                'dependencies': [],
                'cohesion': 1.0
            },
            'logging': {
                'name': 'logging',
                'purpose': 'Logging and monitoring',
                'responsibilities': ['Log events', 'Error tracking', 'Performance monitoring'],
                'public_interface': {'interface_name': 'ILogger', 'methods': [], 'events': []},
                'files': [],
                'internal_components': [],
                'dependencies': [],
                'cohesion': 1.0
            }
        }

        # Add missing standard modules
        for name, spec in standard.items():
            if name not in module_names:
                modules.append(spec)

        return modules

    def design_interfaces(
        self, modules: List[Dict[str, Any]], dependency_graph: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Design interfaces between modules

        Args:
            modules: Module specifications
            dependency_graph: File dependencies

        Returns:
            List of interface specifications
        """
        self.logger.info("Designing module interfaces...")

        interfaces = []

        for module in modules:
            interface = {
                "module": module['name'],
                "interface_name": module['public_interface']['interface_name'],
                "description": f"Public interface for {module['name']} module",
                "methods": module['public_interface']['methods'],
                "events": module['public_interface']['events'],
                "consumers": self._identify_consumers(module, modules)
            }

            interfaces.append(interface)

        return interfaces

    def _identify_consumers(
        self, module: Dict[str, Any], all_modules: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify which modules consume this module's interface"""
        consumers = []

        for other_module in all_modules:
            if other_module['name'] == module['name']:
                continue

            # Check if this module is in dependencies
            if module['name'] in other_module.get('dependencies', []):
                consumers.append(other_module['name'])

        return consumers

    def establish_layers(
        self, modules: List[Dict[str, Any]], target_architecture: str
    ) -> List[str]:
        """
        Establish layer hierarchy based on target architecture

        Args:
            modules: Module specifications
            target_architecture: Target pattern

        Returns:
            Ordered list of layer names (top to bottom)
        """
        self.logger.info(f"Establishing {target_architecture} layer hierarchy...")

        architecture_layers = {
            "layered": [
                "presentation",
                "application",
                "domain",
                "infrastructure"
            ],
            "hexagonal": [
                "adapters",
                "ports",
                "application",
                "domain"
            ],
            "microservices": [
                "api_gateway",
                "services",
                "shared"
            ],
            "plugin": [
                "core",
                "plugin_interface",
                "plugins",
                "shared"
            ],
            "modular_monolith": [
                "presentation",
                "modules",
                "shared_kernel"
            ],
            "event_driven": [
                "producers",
                "event_bus",
                "consumers",
                "shared"
            ]
        }

        return architecture_layers.get(target_architecture, ["core", "modules", "shared"])

    def create_migration_phases(
        self, modules: List[Dict[str, Any]], interfaces: List[Dict[str, Any]],
        dependency_graph: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Create phased migration plan

        Args:
            modules: Module specifications
            interfaces: Interface specifications
            dependency_graph: File dependencies

        Returns:
            List of migration phases
        """
        self.logger.info("Creating migration phases...")

        phases = []

        # Phase 1: Setup infrastructure
        phases.append({
            "name": "Phase 1: Infrastructure Setup",
            "description": "Create directory structure and central module",
            "tasks": [
                "Create module directory structure",
                "Implement central core module",
                "Setup configuration system",
                "Initialize logging infrastructure"
            ],
            "deliverables": [
                "Module skeleton",
                "Core orchestrator",
                "Configuration loader"
            ]
        })

        # Phase 2: Define interfaces
        phases.append({
            "name": "Phase 2: Interface Definition",
            "description": "Define all module interfaces and contracts",
            "tasks": [
                f"Define {interface['interface_name']}" for interface in interfaces[:5]
            ] + ["Define remaining interfaces..."],
            "deliverables": [
                "Interface specifications",
                "Contract documentation"
            ]
        })

        # Phase 3: Migrate independent modules first
        independent_modules = [
            m for m in modules if not m.get('dependencies', [])
        ]

        if independent_modules:
            phases.append({
                "name": "Phase 3: Migrate Independent Modules",
                "description": "Migrate modules with no dependencies",
                "tasks": [
                    f"Migrate {m['name']} module" for m in independent_modules[:5]
                ],
                "deliverables": [
                    f"{m['name']} module" for m in independent_modules[:5]
                ]
            })

        # Phase 4: Migrate dependent modules
        dependent_modules = [
            m for m in modules if m.get('dependencies', [])
        ]

        if dependent_modules:
            phases.append({
                "name": "Phase 4: Migrate Dependent Modules",
                "description": "Migrate modules with dependencies in order",
                "tasks": [
                    f"Migrate {m['name']} module" for m in dependent_modules[:5]
                ],
                "deliverables": [
                    f"{m['name']} module" for m in dependent_modules[:5]
                ]
            })

        # Phase 5: Integration and testing
        phases.append({
            "name": "Phase 5: Integration & Testing",
            "description": "Wire modules together and validate",
            "tasks": [
                "Wire module dependencies",
                "Implement dependency injection",
                "Run integration tests",
                "Validate functional equivalence",
                "Performance testing"
            ],
            "deliverables": [
                "Integrated system",
                "Test results",
                "Performance report"
            ]
        })

        # Phase 6: Documentation and cleanup
        phases.append({
            "name": "Phase 6: Documentation & Cleanup",
            "description": "Finalize documentation and cleanup",
            "tasks": [
                "Update architecture documentation",
                "Create module READMEs",
                "Generate API documentation",
                "Remove deprecated code",
                "Final code review"
            ],
            "deliverables": [
                "Architecture documentation",
                "API documentation",
                "Migration report"
            ]
        })

        return phases

    def estimate_effort(
        self, total_lines: int, module_count: int, complexity_metrics: Dict[str, Any]
    ) -> str:
        """
        Estimate refactoring effort

        Args:
            total_lines: Total lines of code
            module_count: Number of modules
            complexity_metrics: Complexity metrics

        Returns:
            Effort estimate string
        """
        # Simple heuristic-based estimation
        base_hours = total_lines / 500  # Assume 500 lines per hour
        module_overhead = module_count * 2  # 2 hours per module setup

        complexity_factor = 1.0
        avg_complexity = complexity_metrics.get('average_file_complexity', 0)
        if avg_complexity > 15:
            complexity_factor = 2.0
        elif avg_complexity > 10:
            complexity_factor = 1.5
        elif avg_complexity > 5:
            complexity_factor = 1.2

        total_hours = (base_hours + module_overhead) * complexity_factor

        # Convert to days (8 hours per day)
        total_days = total_hours / 8

        if total_days < 1:
            return f"{total_hours:.1f} hours"
        elif total_days < 5:
            return f"{total_days:.1f} days"
        elif total_days < 20:
            return f"{total_days / 5:.1f} weeks"
        else:
            return f"{total_days / 20:.1f} months"
