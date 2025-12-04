"""
Code Rebuilder

Reconstructs code using the 5-Phase Reasoning Model methodology.

Requirements:
- Extract intent from existing code
- Apply comprehension phase documentation
- Apply strategy phase planning
- Rebuild execution with proper structure
- Add review phase verification
- Apply refinement phase optimization
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Intent:
    """Represents extracted intent from code."""
    purpose: str
    inputs: List[Dict]
    outputs: Dict
    constraints: List[str]
    inferred_requirements: List[str]


class CodeRebuilder:
    """
    Rebuilds code following the 5-Phase Reasoning Model.

    Process:
    1. Extract original intent
    2. Re-apply Comprehension (documentation)
    3. Re-apply Strategy (approach documentation)
    4. Re-apply Execution (structured implementation)
    5. Re-apply Review (validation)
    6. Re-apply Refinement (optimization)

    Example:
        >>> rebuilder = CodeRebuilder()
        >>> intent = rebuilder.extract_intent(code)
        >>> result = rebuilder.rebuild(code, "python", intent, issues)
    """

    # Templates for reasoning documentation
    MODULE_DOC_TEMPLATE = '''"""
{module_name}

{purpose}

Requirements:
{requirements}

Constraints:
{constraints}

Approach: {approach}
Selected because: {rationale}
"""

'''

    FUNCTION_DOC_TEMPLATE = '''"""
    {description}

    Args:
{args_doc}

    Returns:
        {return_doc}

    Raises:
{raises_doc}

    Edge Cases:
{edge_cases}
    """'''

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Code Rebuilder.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    def extract_intent(self, code: str, language: str = "python") -> Intent:
        """
        Extract the original intent from existing code.

        Analyzes the code to understand:
        - What it's trying to accomplish
        - Input/output specifications
        - Implicit requirements
        - Constraints

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Intent object with extracted information
        """
        # Extract purpose from any existing documentation
        purpose = self._extract_purpose(code, language)

        # Analyze function signatures for inputs
        inputs = self._extract_inputs(code, language)

        # Analyze return statements for outputs
        outputs = self._extract_outputs(code, language)

        # Infer constraints from code patterns
        constraints = self._infer_constraints(code, language)

        # Infer requirements from behavior
        requirements = self._infer_requirements(code, language)

        return Intent(
            purpose=purpose,
            inputs=inputs,
            outputs=outputs,
            constraints=constraints,
            inferred_requirements=requirements
        )

    def rebuild(
        self,
        code: str,
        language: str,
        intent: Intent,
        issues: List[Dict]
    ) -> Dict:
        """
        Rebuild code with proper reasoning methodology.

        Args:
            code: Original code
            language: Programming language
            intent: Extracted intent
            issues: List of identified issues to address

        Returns:
            Dictionary with reconstructed code, documentation, and changes
        """
        changes = []

        # Phase 1: Apply Comprehension (documentation)
        documented_code, doc_changes = self._apply_comprehension(
            code, language, intent
        )
        changes.extend(doc_changes)

        # Phase 2: Apply Strategy (approach documentation)
        strategized_code, strat_changes = self._apply_strategy(
            documented_code, language, intent
        )
        changes.extend(strat_changes)

        # Phase 3: Apply Execution (structured implementation)
        executed_code, exec_changes = self._apply_execution(
            strategized_code, language
        )
        changes.extend(exec_changes)

        # Phase 4: Apply Review (validation)
        reviewed_code, review_changes = self._apply_review(
            executed_code, language, issues
        )
        changes.extend(review_changes)

        # Phase 5: Apply Refinement (optimization)
        refined_code, refine_changes = self._apply_refinement(
            reviewed_code, language
        )
        changes.extend(refine_changes)

        # Generate documentation
        documentation = self._generate_documentation(intent, changes)

        return {
            "code": refined_code,
            "documentation": documentation,
            "changes": changes
        }

    def generate_reasoning_skeleton(
        self,
        intent: Intent,
        language: str = "python"
    ) -> str:
        """
        Generate a code skeleton with reasoning structure.

        Creates a template with proper reasoning phases
        built into the structure.

        Args:
            intent: The extracted or defined intent
            language: Programming language

        Returns:
            Code skeleton string
        """
        module_name = "module"  # Could be extracted from context

        # Build requirements list
        requirements_str = "\n".join(
            f"- {req}" for req in intent.inferred_requirements
        ) or "- [Define requirements]"

        # Build constraints list
        constraints_str = "\n".join(
            f"- {con}" for con in intent.constraints
        ) or "- [Define constraints]"

        skeleton = self.MODULE_DOC_TEMPLATE.format(
            module_name=module_name,
            purpose=intent.purpose or "[Describe purpose]",
            requirements=requirements_str,
            constraints=constraints_str,
            approach="[Describe chosen approach]",
            rationale="[Explain why this approach was selected]"
        )

        # Add imports section
        skeleton += "# =============================================================================\n"
        skeleton += "# IMPORTS\n"
        skeleton += "# =============================================================================\n\n"
        skeleton += "from typing import Dict, List, Optional\n\n"

        # Add constants section
        skeleton += "# =============================================================================\n"
        skeleton += "# CONSTANTS\n"
        skeleton += "# =============================================================================\n\n"
        skeleton += "# DECISION: Define constants here instead of magic values\n\n"

        # Add main implementation section
        skeleton += "# =============================================================================\n"
        skeleton += "# IMPLEMENTATION\n"
        skeleton += "# Plan Step: [Reference plan step]\n"
        skeleton += "# =============================================================================\n\n"

        # Add function skeleton
        if intent.inputs:
            params = ", ".join(
                f"{inp['name']}: {inp.get('type', 'Any')}"
                for inp in intent.inputs
            )
        else:
            params = ""

        return_type = intent.outputs.get("type", "None") if intent.outputs else "None"

        skeleton += f"def main_function({params}) -> {return_type}:\n"
        skeleton += '    """\n'
        skeleton += f"    {intent.purpose or '[Description]'}\n"
        skeleton += "\n"
        skeleton += "    Args:\n"
        for inp in intent.inputs:
            skeleton += f"        {inp['name']}: [Description]\n"
        skeleton += "\n"
        skeleton += "    Returns:\n"
        skeleton += "        [Description]\n"
        skeleton += "\n"
        skeleton += "    Edge Cases:\n"
        skeleton += "        - [Edge case 1]: [How handled]\n"
        skeleton += '    """\n'
        skeleton += "    # Step 1: Input validation\n"
        skeleton += "    # ...\n\n"
        skeleton += "    # Step 2: Main logic\n"
        skeleton += "    # ...\n\n"
        skeleton += "    # Step 3: Return result\n"
        skeleton += "    pass\n"

        return skeleton

    # =========================================================================
    # Private Methods - Intent Extraction
    # =========================================================================

    def _extract_purpose(self, code: str, language: str) -> str:
        """Extract purpose from existing documentation."""
        # Try to find module docstring
        if language == "python":
            doc_match = re.search(r'^(?:\s*#[^\n]*\n)*\s*"""([\s\S]*?)"""', code)
            if doc_match:
                doc = doc_match.group(1).strip()
                # Get first sentence or paragraph
                first_para = doc.split("\n\n")[0]
                return first_para.strip()

        # Try to infer from function names
        func_names = re.findall(r"def\s+(\w+)", code)
        if func_names:
            main_func = func_names[0]
            # Convert function name to description
            words = re.findall(r"[A-Z][a-z]*|[a-z]+", main_func)
            return f"Function to {' '.join(words).lower()}"

        return "Purpose not clearly defined in original code"

    def _extract_inputs(self, code: str, language: str) -> List[Dict]:
        """Extract input specifications from code."""
        inputs = []

        # Find function parameters
        if language == "python":
            func_match = re.search(
                r"def\s+\w+\s*\(([^)]*)\)",
                code
            )
            if func_match:
                params_str = func_match.group(1)
                if params_str.strip():
                    for param in params_str.split(","):
                        param = param.strip()
                        if param and param != "self":
                            # Parse parameter
                            if ":" in param:
                                name, type_hint = param.split(":", 1)
                                type_hint = type_hint.split("=")[0].strip()
                            else:
                                name = param.split("=")[0].strip()
                                type_hint = "Any"

                            inputs.append({
                                "name": name.strip(),
                                "type": type_hint,
                                "description": f"Parameter {name}"
                            })

        return inputs

    def _extract_outputs(self, code: str, language: str) -> Dict:
        """Extract output specifications from code."""
        output = {"type": "None", "description": ""}

        # Find return type annotation
        if language == "python":
            return_match = re.search(r"->\s*([^:]+):", code)
            if return_match:
                output["type"] = return_match.group(1).strip()

        # Analyze return statements
        returns = re.findall(r"return\s+(.+)", code)
        if returns:
            # Infer type from return values
            return_values = [r.strip() for r in returns]
            output["description"] = f"Returns: {return_values[0][:50]}"

        return output

    def _infer_constraints(self, code: str, language: str) -> List[str]:
        """Infer constraints from code patterns."""
        constraints = []

        # Check for error handling
        if not re.search(r"\btry\b", code):
            constraints.append("No explicit error handling required")

        # Check for type constraints
        if re.search(r"isinstance\s*\(", code):
            constraints.append("Type checking is performed")

        # Check for size/limit constraints
        limit_patterns = [
            (r"len\([^)]+\)\s*[<>]", "Size limits present"),
            (r"\bmax\b|\bmin\b", "Value bounds present"),
            (r"range\s*\(\s*\d+", "Iteration limits present"),
        ]
        for pattern, description in limit_patterns:
            if re.search(pattern, code):
                constraints.append(description)

        return constraints

    def _infer_requirements(self, code: str, language: str) -> List[str]:
        """Infer requirements from code behavior."""
        requirements = []

        # Analyze control flow for implicit requirements
        if re.search(r"\bif\b.*\bnone\b|\bnull\b", code, re.IGNORECASE):
            requirements.append("Handle null/None values")

        if re.search(r"\bfor\b|\bwhile\b", code):
            requirements.append("Process collections/sequences")

        if re.search(r"\bopen\s*\(", code):
            requirements.append("File I/O operations")

        if re.search(r"\brequests\b|\bhttp\b|\burl\b", code, re.IGNORECASE):
            requirements.append("Network/HTTP operations")

        if re.search(r"def\s+test_|assert\s+", code):
            requirements.append("Testing/validation")

        # Check for data transformations
        if re.search(r"\[.*for.*in.*\]", code):  # List comprehension
            requirements.append("Data transformation")

        return requirements if requirements else ["Core functionality implementation"]

    # =========================================================================
    # Private Methods - Phase Application
    # =========================================================================

    def _apply_comprehension(
        self,
        code: str,
        language: str,
        intent: Intent
    ) -> Tuple[str, List[str]]:
        """Apply Phase 1: Comprehension documentation."""
        changes = []

        # Check if module doc exists
        if language == "python":
            has_module_doc = re.match(
                r'^(?:\s*#[^\n]*\n)*\s*"""',
                code
            )
        else:
            has_module_doc = code.strip().startswith("/**")

        if not has_module_doc:
            # Generate module documentation
            requirements_str = "\n".join(
                f"- {req}" for req in intent.inferred_requirements
            )
            constraints_str = "\n".join(
                f"- {con}" for con in intent.constraints
            ) or "- None specified"

            module_doc = self.MODULE_DOC_TEMPLATE.format(
                module_name="Module",
                purpose=intent.purpose,
                requirements=requirements_str,
                constraints=constraints_str,
                approach="[Approach from original implementation]",
                rationale="[Preserved original approach]"
            )

            code = module_doc + code
            changes.append("Added module documentation with requirements")

        # Add function documentation where missing
        code, func_changes = self._add_function_docs(code, language, intent)
        changes.extend(func_changes)

        return code, changes

    def _apply_strategy(
        self,
        code: str,
        language: str,
        intent: Intent
    ) -> Tuple[str, List[str]]:
        """Apply Phase 2: Strategy documentation."""
        changes = []

        # Add approach comments if missing
        if not re.search(r"#.*approach|#.*strategy", code, re.IGNORECASE):
            # Find first function and add strategy comment before it
            func_match = re.search(r"(\ndef\s+)", code)
            if func_match:
                strategy_comment = "\n# APPROACH: [Document the chosen strategy here]\n"
                strategy_comment += "# ALTERNATIVES CONSIDERED: [List alternatives]\n"
                strategy_comment += "# SELECTED BECAUSE: [Rationale]\n"

                insert_pos = func_match.start()
                code = code[:insert_pos] + strategy_comment + code[insert_pos:]
                changes.append("Added strategy documentation section")

        # Add decision comments for complex logic
        # Find if-else chains without decision comments
        if_blocks = re.finditer(r"(\n\s*)(if\s+[^:]+:)", code)
        for match in if_blocks:
            # Check if there's a decision comment nearby
            start = max(0, match.start() - 100)
            context = code[start:match.start()]
            if "DECISION:" not in context and "decision" not in context.lower():
                # This is a candidate for decision documentation
                # We'll note it but not auto-add to avoid noise
                pass

        return code, changes

    def _apply_execution(
        self,
        code: str,
        language: str
    ) -> Tuple[str, List[str]]:
        """Apply Phase 3: Execution structure."""
        changes = []

        # Add step markers if functions are long and unmarked
        lines = code.split("\n")

        # Find function bodies
        in_function = False
        function_start = 0
        function_lines = 0
        modified_lines = []

        for i, line in enumerate(lines):
            if re.match(r"\s*def\s+", line):
                in_function = True
                function_start = i
                function_lines = 0

            if in_function:
                function_lines += 1

                # If function is getting long and no step markers
                if function_lines == 10 and not any(
                    "step" in lines[j].lower()
                    for j in range(function_start, min(i, function_start + 15))
                ):
                    # Add a note (don't modify automatically to avoid breaking code)
                    changes.append(
                        f"Consider adding step markers in function starting at line {function_start + 1}"
                    )

            # Track function end (simple heuristic)
            if in_function and line and not line[0].isspace() and i > function_start:
                in_function = False

            modified_lines.append(line)

        return "\n".join(modified_lines), changes

    def _apply_review(
        self,
        code: str,
        language: str,
        issues: List[Dict]
    ) -> Tuple[str, List[str]]:
        """Apply Phase 4: Review (validation)."""
        changes = []

        # Check for input validation
        has_validation = re.search(
            r"if\s+(?:not\s+)?\w+:|isinstance|assert\s+",
            code
        )

        if not has_validation:
            changes.append("Consider adding input validation")

        # Check for edge case handling
        edge_patterns = [
            (r"if.*(?:is\s+)?None", "null check"),
            (r"if.*len.*[<>=]+\s*0", "empty check"),
            (r"if.*[<>=]+\s*0", "zero/negative check"),
        ]

        missing_edge_cases = []
        for pattern, name in edge_patterns:
            if not re.search(pattern, code):
                missing_edge_cases.append(name)

        if missing_edge_cases:
            changes.append(
                f"Consider adding edge case handling: {', '.join(missing_edge_cases)}"
            )

        # Check for error handling based on issues
        review_issues = [i for i in issues if i.get("phase") == "review"]
        for issue in review_issues:
            changes.append(f"Address: {issue.get('issue', 'review issue')}")

        return code, changes

    def _apply_refinement(
        self,
        code: str,
        language: str
    ) -> Tuple[str, List[str]]:
        """Apply Phase 5: Refinement."""
        changes = []

        # Check for TODOs that should be addressed
        todos = re.findall(r"#\s*(TODO|FIXME|HACK|XXX)[:\s]*([^\n]*)", code)
        if todos:
            for todo_type, todo_text in todos[:3]:
                changes.append(f"Address {todo_type}: {todo_text.strip()[:50]}")

        # Check for obvious code duplication
        lines = [l.strip() for l in code.split("\n") if l.strip()]
        from collections import Counter
        line_counts = Counter(lines)
        duplicates = [
            line for line, count in line_counts.items()
            if count > 2 and len(line) > 20 and not line.startswith("#")
        ]

        if duplicates:
            changes.append(
                f"Consider extracting duplicated code ({len(duplicates)} patterns)"
            )

        return code, changes

    def _add_function_docs(
        self,
        code: str,
        language: str,
        intent: Intent
    ) -> Tuple[str, List[str]]:
        """Add documentation to undocumented functions."""
        changes = []

        # Find functions without docstrings
        pattern = r"(def\s+(\w+)\s*\([^)]*\)[^:]*:)\s*\n(\s*)(?!""")"

        def add_docstring(match):
            func_def = match.group(1)
            func_name = match.group(2)
            indent = match.group(3) or "    "

            # Generate simple docstring
            docstring = f'{indent}"""\n'
            docstring += f"{indent}[Description of {func_name}]\n"
            docstring += f'{indent}"""\n'

            changes.append(f"Added docstring to function '{func_name}'")
            return f"{func_def}\n{docstring}{indent}"

        # Only add to first few undocumented functions to avoid noise
        modified_code = code
        for i in range(3):  # Limit to 3 additions
            new_code = re.sub(pattern, add_docstring, modified_code, count=1)
            if new_code == modified_code:
                break
            modified_code = new_code

        return modified_code, changes

    def _generate_documentation(
        self,
        intent: Intent,
        changes: List[str]
    ) -> str:
        """Generate reconstruction documentation."""
        doc = "## Reconstruction Report\n\n"

        doc += "### Extracted Intent\n"
        doc += f"**Purpose**: {intent.purpose}\n\n"

        if intent.inputs:
            doc += "**Inputs**:\n"
            for inp in intent.inputs:
                doc += f"- `{inp['name']}`: {inp.get('type', 'Any')}\n"
            doc += "\n"

        if intent.outputs:
            doc += f"**Output**: {intent.outputs.get('type', 'Unknown')}\n\n"

        if intent.inferred_requirements:
            doc += "**Inferred Requirements**:\n"
            for req in intent.inferred_requirements:
                doc += f"- {req}\n"
            doc += "\n"

        doc += "### Changes Applied\n"
        for i, change in enumerate(changes, 1):
            doc += f"{i}. {change}\n"

        return doc
