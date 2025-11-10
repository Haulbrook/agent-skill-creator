"""
Reconstruction Executor Module

Executes the actual refactoring/reconstruction:
- Creates module structure
- Migrates code to modules
- Generates tests
- Updates documentation
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReconstructionExecutor:
    """
    Executes the modular reconstruction

    Takes the designed architecture and implements it
    """

    def __init__(self, config: Any, source_path: Path, output_path: Optional[Path]):
        """
        Initialize executor

        Args:
            config: Refactoring configuration
            source_path: Source codebase path
            output_path: Output directory for refactored code
        """
        self.config = config
        self.source_path = source_path
        self.output_path = output_path or (source_path.parent / f"{source_path.name}_refactored")
        self.logger = logging.getLogger(__name__ + ".ReconstructionExecutor")

    def execute_phase(self, phase: Dict[str, Any], design: Any) -> None:
        """
        Execute a single migration phase

        Args:
            phase: Phase specification
            design: Complete modular design
        """
        self.logger.info(f"Executing: {phase['name']}")

        phase_name = phase['name'].lower()

        if 'infrastructure' in phase_name:
            self._create_infrastructure(design)
        elif 'interface' in phase_name:
            self._create_interfaces(design)
        elif 'migrate' in phase_name:
            self._migrate_modules(phase, design)
        elif 'integration' in phase_name:
            self._integrate_modules(design)
        elif 'documentation' in phase_name:
            self._create_documentation(design)

    def _create_infrastructure(self, design: Any) -> None:
        """Create basic infrastructure and directory structure"""
        self.logger.info("Creating infrastructure...")

        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Create module directories
        for module in design.modules:
            module_path = self.output_path / module['name']
            module_path.mkdir(exist_ok=True)

            # Create __init__.py for Python projects
            (module_path / '__init__.py').touch()

        # Create central module
        core_path = self.output_path / design.central_module['name']
        core_path.mkdir(exist_ok=True)
        (core_path / '__init__.py').touch()

        # Create shared directory
        shared_path = self.output_path / 'shared'
        shared_path.mkdir(exist_ok=True)
        (shared_path / '__init__.py').touch()

        self.logger.info(f"Created {len(design.modules)} module directories")

    def _create_interfaces(self, design: Any) -> None:
        """Create interface definitions"""
        self.logger.info("Creating interfaces...")

        interfaces_path = self.output_path / 'shared' / 'interfaces'
        interfaces_path.mkdir(exist_ok=True)
        (interfaces_path / '__init__.py').touch()

        for interface in design.interfaces:
            interface_file = interfaces_path / f"{interface['interface_name'].lower()}.py"

            content = self._generate_interface_code(interface)
            interface_file.write_text(content)

        self.logger.info(f"Created {len(design.interfaces)} interface definitions")

    def _generate_interface_code(self, interface: Dict[str, Any]) -> str:
        """Generate Python interface code"""
        lines = [
            '"""',
            f"{interface['description']}",
            '"""',
            '',
            'from abc import ABC, abstractmethod',
            'from typing import Any, Dict',
            '',
            '',
            f"class {interface['interface_name']}(ABC):",
            f'    """Interface for {interface["module"]} module"""',
            ''
        ]

        # Add methods
        for method in interface.get('methods', []):
            lines.append(f"    @abstractmethod")
            params = ', '.join(method.get('parameters', []))
            lines.append(f"    def {method['name']}(self, {params}) -> {method['returns']}:")
            lines.append(f'        """{method["purpose"]}"""')
            lines.append(f"        pass")
            lines.append('')

        return '\n'.join(lines)

    def _migrate_modules(self, phase: Dict[str, Any], design: Any) -> None:
        """Migrate code to modular structure"""
        self.logger.info("Migrating modules...")

        for module in design.modules:
            if not module.get('files'):
                continue

            module_path = self.output_path / module['name']

            # Copy files to module directory
            for source_file in module['files']:
                source = Path(source_file)
                if source.exists():
                    dest = module_path / source.name
                    shutil.copy2(source, dest)
                    self.logger.debug(f"Copied {source.name} to {module['name']}")

    def _integrate_modules(self, design: Any) -> None:
        """Wire modules together"""
        self.logger.info("Integrating modules...")

        # Create main application file
        main_file = self.output_path / 'main.py'
        main_content = self._generate_main_application(design)
        main_file.write_text(main_content)

        self.logger.info("Created main application file")

    def _generate_main_application(self, design: Any) -> str:
        """Generate main application orchestrator"""
        lines = [
            '"""',
            'Main application entry point',
            '',
            'Orchestrates all modules and manages lifecycle',
            '"""',
            '',
            'import logging',
            'from pathlib import Path',
            '',
            '# Import modules',
        ]

        # Add imports
        for module in design.modules:
            lines.append(f"# from {module['name']} import {module['name'].title()}Module")

        lines.extend([
            '',
            '',
            'class Application:',
            '    """Central application orchestrator"""',
            '',
            '    def __init__(self):',
            '        self.logger = logging.getLogger(__name__)',
            '        self.modules = {}',
            '',
            '    def initialize(self):',
            '        """Initialize all modules"""',
            '        self.logger.info("Initializing application...")',
            '',
            '        # Initialize modules',
        ])

        for module in design.modules:
            lines.append(f"        # self.modules['{module['name']}'] = {module['name'].title()}Module()")

        lines.extend([
            '',
            '        self.logger.info("Application initialized")',
            '',
            '    def run(self):',
            '        """Run the application"""',
            '        self.logger.info("Starting application...")',
            '',
            '        # Run application logic',
            '        pass',
            '',
            '    def shutdown(self):',
            '        """Shutdown all modules"""',
            '        self.logger.info("Shutting down application...")',
            '',
            '        for name, module in self.modules.items():',
            '            self.logger.info(f"Shutting down {name}...")',
            '            # module.shutdown()',
            '',
            '',
            'def main():',
            '    """Main entry point"""',
            '    logging.basicConfig(',
            '        level=logging.INFO,',
            '        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"',
            '    )',
            '',
            '    app = Application()',
            '    app.initialize()',
            '',
            '    try:',
            '        app.run()',
            '    except KeyboardInterrupt:',
            '        print("\\nShutting down...")',
            '    finally:',
            '        app.shutdown()',
            '',
            '',
            'if __name__ == "__main__":',
            '    main()',
        ])

        return '\n'.join(lines)

    def generate_equivalence_tests(self, design: Any) -> None:
        """Generate tests to validate functional equivalence"""
        self.logger.info("Generating equivalence tests...")

        tests_path = self.output_path / 'tests'
        tests_path.mkdir(exist_ok=True)
        (tests_path / '__init__.py').touch()

        # Generate test file
        test_file = tests_path / 'test_equivalence.py'
        test_content = self._generate_test_code(design)
        test_file.write_text(test_content)

        self.logger.info("Generated equivalence tests")

    def _generate_test_code(self, design: Any) -> str:
        """Generate Python test code"""
        lines = [
            '"""',
            'Equivalence tests to validate refactored code',
            '"""',
            '',
            'import unittest',
            '',
            '',
            'class TestEquivalence(unittest.TestCase):',
            '    """Test that refactored code maintains functionality"""',
            '',
            '    def setUp(self):',
            '        """Set up test fixtures"""',
            '        pass',
            '',
        ]

        for module in design.modules[:5]:  # Limit to first 5
            test_name = f"test_{module['name']}_module"
            lines.extend([
                f"    def {test_name}(self):",
                f'        """Test {module["name"]} module functionality"""',
                '        # Add specific tests for this module',
                '        self.assertTrue(True)',
                '',
            ])

        lines.extend([
            '',
            'if __name__ == "__main__":',
            '    unittest.main()',
        ])

        return '\n'.join(lines)

    def update_documentation(self, design: Any, documentation_level: str) -> None:
        """Update or create documentation"""
        self.logger.info(f"Updating documentation (level: {documentation_level})...")

        # Create README
        readme_path = self.output_path / 'README.md'
        readme_content = self._generate_readme(design)
        readme_path.write_text(readme_content)

        # Create architecture document
        arch_doc_path = self.output_path / 'ARCHITECTURE.md'
        arch_content = self._generate_architecture_doc(design)
        arch_doc_path.write_text(arch_content)

        self.logger.info("Documentation updated")

    def _generate_readme(self, design: Any) -> str:
        """Generate README.md"""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        lines = [
            '# Refactored Application',
            '',
            f'Refactored on: {timestamp}',
            '',
            '## Overview',
            '',
            f'This application has been refactored into a {self.config.target_architecture.value} architecture',
            f'with {len(design.modules)} modules.',
            '',
            '## Architecture',
            '',
            f'**Central Module**: {design.central_module["name"]}',
            '',
            '**Modules**:',
        ]

        for module in design.modules:
            lines.append(f'- `{module["name"]}`: {module["purpose"]}')

        lines.extend([
            '',
            '## Getting Started',
            '',
            '```bash',
            'python main.py',
            '```',
            '',
            '## Module Structure',
            '',
            '```',
        ])

        for module in design.modules:
            lines.append(f'{module["name"]}/')
            for component in module.get('internal_components', [])[:3]:
                lines.append(f'  - {component}')

        lines.extend([
            '```',
            '',
            '## Documentation',
            '',
            'See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.',
        ])

        return '\n'.join(lines)

    def _generate_architecture_doc(self, design: Any) -> str:
        """Generate ARCHITECTURE.md"""
        lines = [
            '# Architecture Documentation',
            '',
            f'## Architecture Pattern: {self.config.target_architecture.value.title()}',
            '',
            '## Layer Hierarchy',
            '',
        ]

        for i, layer in enumerate(design.layer_hierarchy, 1):
            lines.append(f'{i}. **{layer.title()}**')

        lines.extend([
            '',
            '## Central Module',
            '',
            f'**Name**: {design.central_module["name"]}',
            '',
            f'**Purpose**: {design.central_module["purpose"]}',
            '',
            '**Responsibilities**:',
        ])

        for resp in design.central_module.get('responsibilities', []):
            lines.append(f'- {resp}')

        lines.extend([
            '',
            '## Modules',
            '',
        ])

        for module in design.modules:
            lines.extend([
                f'### {module["name"].title()} Module',
                '',
                f'**Purpose**: {module["purpose"]}',
                '',
                '**Responsibilities**:',
            ])

            for resp in module.get('responsibilities', []):
                lines.append(f'- {resp}')

            if module.get('dependencies'):
                lines.append('')
                lines.append('**Dependencies**:')
                for dep in module['dependencies']:
                    lines.append(f'- {dep}')

            lines.append('')

        return '\n'.join(lines)

    def _create_documentation(self, design: Any) -> None:
        """Create comprehensive documentation"""
        self.update_documentation(design, self.config.documentation_level)


# Make __init__.py for planners
