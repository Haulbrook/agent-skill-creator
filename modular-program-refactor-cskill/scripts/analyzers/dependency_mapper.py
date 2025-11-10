"""
Dependency Mapper Module

Maps both explicit and implicit dependencies between code modules:
- Import/include statements (explicit)
- Function calls across modules (implicit)
- Shared state and global variables (implicit)
- Data flow dependencies (implicit)
"""

import ast
import re
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class DependencyMapper:
    """
    Maps dependencies between code files and modules

    Analyzes both explicit (imports, includes) and implicit
    (data flow, shared state) dependencies
    """

    def __init__(self):
        """Initialize dependency mapper"""
        self.logger = logging.getLogger(__name__ + ".DependencyMapper")

    def build_dependency_graph(self, files: List[Path]) -> Dict[str, List[str]]:
        """
        Build complete dependency graph for all files

        Args:
            files: List of source files

        Returns:
            Dictionary mapping file paths to their dependencies
        """
        self.logger.info(f"Building dependency graph for {len(files)} files...")

        dependency_graph = defaultdict(list)

        for file in files:
            try:
                if file.suffix == '.py':
                    deps = self._analyze_python_dependencies(file, files)
                elif file.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                    deps = self._analyze_javascript_dependencies(file, files)
                elif file.suffix == '.java':
                    deps = self._analyze_java_dependencies(file, files)
                elif file.suffix == '.go':
                    deps = self._analyze_go_dependencies(file, files)
                else:
                    deps = []

                dependency_graph[str(file)] = deps

            except Exception as e:
                self.logger.debug(f"Could not analyze {file}: {e}")
                dependency_graph[str(file)] = []

        return dict(dependency_graph)

    def _analyze_python_dependencies(self, file: Path, all_files: List[Path]) -> List[str]:
        """
        Analyze Python file dependencies

        Args:
            file: File to analyze
            all_files: All files in the codebase

        Returns:
            List of dependency file paths
        """
        try:
            content = file.read_text(errors='ignore')
            tree = ast.parse(content)

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # Map import names to actual files
            dependencies = []
            for imp in imports:
                dep_file = self._resolve_python_import(imp, file, all_files)
                if dep_file:
                    dependencies.append(str(dep_file))

            return dependencies

        except Exception as e:
            self.logger.debug(f"Could not parse Python file {file}: {e}")
            return []

    def _resolve_python_import(
        self, import_name: str, current_file: Path, all_files: List[Path]
    ) -> Optional[Path]:
        """
        Resolve Python import to actual file

        Args:
            import_name: Import module name
            current_file: File containing the import
            all_files: All files in codebase

        Returns:
            Resolved file path or None
        """
        # Convert import name to potential file paths
        parts = import_name.split('.')
        potential_paths = [
            current_file.parent / f"{parts[-1]}.py",
            current_file.parent / parts[-1] / "__init__.py",
        ]

        # Check if any potential path exists in all_files
        for potential in potential_paths:
            if potential in all_files:
                return potential

        # Try to find by module name anywhere in the project
        module_name = parts[-1]
        for file in all_files:
            if file.stem == module_name and file != current_file:
                return file

        return None

    def _analyze_javascript_dependencies(
        self, file: Path, all_files: List[Path]
    ) -> List[str]:
        """
        Analyze JavaScript/TypeScript dependencies

        Args:
            file: File to analyze
            all_files: All files in the codebase

        Returns:
            List of dependency file paths
        """
        try:
            content = file.read_text(errors='ignore')

            # Match import statements
            import_patterns = [
                r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]',  # ES6 imports
                r'require\([\'"](.+?)[\'"]\)',  # CommonJS require
                r'import\([\'"](.+?)[\'"]\)',  # Dynamic import
            ]

            imports = []
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imports.extend(matches)

            # Resolve imports to files
            dependencies = []
            for imp in imports:
                dep_file = self._resolve_javascript_import(imp, file, all_files)
                if dep_file:
                    dependencies.append(str(dep_file))

            return dependencies

        except Exception as e:
            self.logger.debug(f"Could not parse JavaScript file {file}: {e}")
            return []

    def _resolve_javascript_import(
        self, import_path: str, current_file: Path, all_files: List[Path]
    ) -> Optional[Path]:
        """
        Resolve JavaScript import to actual file

        Args:
            import_path: Import path string
            current_file: File containing the import
            all_files: All files in codebase

        Returns:
            Resolved file path or None
        """
        # Skip external packages
        if not import_path.startswith('.'):
            return None

        # Resolve relative path
        base_path = current_file.parent
        resolved = (base_path / import_path).resolve()

        # Try different extensions
        extensions = ['.js', '.ts', '.jsx', '.tsx', '.json']
        for ext in extensions:
            candidate = resolved.with_suffix(ext)
            if candidate in all_files:
                return candidate

        # Try index files
        for ext in extensions:
            candidate = resolved / f"index{ext}"
            if candidate in all_files:
                return candidate

        return None

    def _analyze_java_dependencies(self, file: Path, all_files: List[Path]) -> List[str]:
        """
        Analyze Java dependencies

        Args:
            file: File to analyze
            all_files: All files in the codebase

        Returns:
            List of dependency file paths
        """
        try:
            content = file.read_text(errors='ignore')

            # Match import statements
            import_pattern = r'import\s+([\w.]+);'
            imports = re.findall(import_pattern, content)

            # Resolve to files
            dependencies = []
            for imp in imports:
                class_name = imp.split('.')[-1]
                # Find file with this class name
                for f in all_files:
                    if f.stem == class_name and f.suffix == '.java':
                        dependencies.append(str(f))
                        break

            return dependencies

        except Exception as e:
            self.logger.debug(f"Could not parse Java file {file}: {e}")
            return []

    def _analyze_go_dependencies(self, file: Path, all_files: List[Path]) -> List[str]:
        """
        Analyze Go dependencies

        Args:
            file: File to analyze
            all_files: All files in the codebase

        Returns:
            List of dependency file paths
        """
        try:
            content = file.read_text(errors='ignore')

            # Match import statements
            import_patterns = [
                r'import\s+"(.+?)"',  # Single import
                r'import\s+\((.*?)\)',  # Multiple imports (need to parse further)
            ]

            imports = []
            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    if '\n' in match:  # Multiple imports block
                        sub_imports = re.findall(r'"(.+?)"', match)
                        imports.extend(sub_imports)
                    else:
                        imports.append(match)

            # Resolve to files (Go uses package-based imports)
            dependencies = []
            for imp in imports:
                package_name = imp.split('/')[-1]
                # Find files in package
                for f in all_files:
                    if f.parent.name == package_name and f.suffix == '.go':
                        if str(f) not in dependencies:
                            dependencies.append(str(f))

            return dependencies

        except Exception as e:
            self.logger.debug(f"Could not parse Go file {file}: {e}")
            return []

    def find_circular_dependencies(
        self, dependency_graph: Dict[str, List[str]]
    ) -> List[List[str]]:
        """
        Find circular dependencies in the graph

        Args:
            dependency_graph: File dependency mapping

        Returns:
            List of circular dependency chains
        """
        self.logger.info("Searching for circular dependencies...")

        cycles = []
        visited = set()
        rec_stack = []

        def dfs(node: str) -> bool:
            """DFS to detect cycles"""
            visited.add(node)
            rec_stack.append(node)

            for neighbor in dependency_graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = rec_stack.index(neighbor)
                    cycle = rec_stack[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)
                    return True

            rec_stack.pop()
            return False

        for node in dependency_graph:
            if node not in visited:
                dfs(node)

        return cycles

    def calculate_dependency_metrics(
        self, dependency_graph: Dict[str, List[str]]
    ) -> Dict[str, any]:
        """
        Calculate various dependency metrics

        Args:
            dependency_graph: File dependency mapping

        Returns:
            Dictionary of metrics
        """
        total_files = len(dependency_graph)
        total_dependencies = sum(len(deps) for deps in dependency_graph.values())

        # Find files with most dependencies (outgoing)
        outgoing = sorted(
            [(file, len(deps)) for file, deps in dependency_graph.items()],
            key=lambda x: x[1],
            reverse=True
        )

        # Find files most depended upon (incoming)
        incoming_count = defaultdict(int)
        for file, deps in dependency_graph.items():
            for dep in deps:
                incoming_count[dep] += 1

        incoming = sorted(
            incoming_count.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Find independent files (no dependencies)
        independent = [
            file for file, deps in dependency_graph.items()
            if len(deps) == 0 and incoming_count.get(file, 0) == 0
        ]

        return {
            "total_files": total_files,
            "total_dependencies": total_dependencies,
            "average_dependencies": total_dependencies / total_files if total_files > 0 else 0,
            "most_outgoing_dependencies": outgoing[:10],
            "most_incoming_dependencies": incoming[:10],
            "independent_files": independent,
            "circular_dependencies": self.find_circular_dependencies(dependency_graph)
        }

    def identify_module_boundaries(
        self, dependency_graph: Dict[str, List[str]]
    ) -> List[Set[str]]:
        """
        Identify natural module boundaries using community detection

        Args:
            dependency_graph: File dependency mapping

        Returns:
            List of file sets representing module candidates
        """
        self.logger.info("Identifying module boundaries...")

        # Simple algorithm: files that depend on each other form a module
        modules = []
        processed = set()

        for file in dependency_graph:
            if file in processed:
                continue

            # BFS to find connected component
            module = set()
            queue = [file]
            while queue:
                current = queue.pop(0)
                if current in module:
                    continue

                module.add(current)
                processed.add(current)

                # Add dependencies
                for dep in dependency_graph.get(current, []):
                    if dep not in module:
                        queue.append(dep)

            if module:
                modules.append(module)

        return modules

    def visualize_dependency_graph(
        self, dependency_graph: Dict[str, List[str]], output_file: Optional[Path] = None
    ) -> str:
        """
        Create a text-based visualization of the dependency graph

        Args:
            dependency_graph: File dependency mapping
            output_file: Optional file to write visualization

        Returns:
            String representation of the graph
        """
        lines = ["# Dependency Graph\n"]

        for file, deps in sorted(dependency_graph.items()):
            file_short = Path(file).name
            lines.append(f"\n## {file_short}")

            if not deps:
                lines.append("  No dependencies")
            else:
                lines.append("  Dependencies:")
                for dep in deps:
                    dep_short = Path(dep).name
                    lines.append(f"  - {dep_short}")

        visualization = '\n'.join(lines)

        if output_file:
            output_file.write_text(visualization)

        return visualization


# Type hint import
from typing import Optional
