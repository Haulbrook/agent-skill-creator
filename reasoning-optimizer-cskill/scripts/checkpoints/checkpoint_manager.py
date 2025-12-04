"""
Checkpoint Manager

Manages reasoning checkpoints throughout the development lifecycle.

Requirements:
- Create pre/mid/post/release checkpoints
- Validate code against checkpoint requirements
- Track checkpoint history
- Generate checkpoint reports
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Checkpoint:
    """
    Represents a development checkpoint.

    Attributes:
        checkpoint_type: Type of checkpoint (pre/mid/post/release)
        timestamp: When checkpoint was created
        project_path: Path to project being checkpointed
        status: Current status (pending/passed/failed)
        reasoning_score: Overall reasoning score
        phase_scores: Individual phase scores
        issues: List of identified issues
        verification_results: Results of verification checks
        metadata: Additional checkpoint metadata
    """
    checkpoint_type: str
    timestamp: str
    project_path: str
    status: str
    reasoning_score: Optional[int] = None
    phase_scores: Optional[Dict[str, int]] = None
    issues: Optional[List[Dict]] = None
    verification_results: Optional[Dict] = None
    metadata: Optional[Dict] = None


class CheckpointManager:
    """
    Manages reasoning checkpoints for development quality assurance.

    Provides:
    - Pre-development checkpoints (requirements validation)
    - Mid-development checkpoints (progress validation)
    - Post-development checkpoints (quality validation)
    - Release checkpoints (final verification)

    Example:
        >>> manager = CheckpointManager()
        >>> checkpoint = manager.create_checkpoint("post", "/path/to/project")
        >>> print(f"Status: {checkpoint['status']}")
    """

    # Minimum scores required for each checkpoint type
    SCORE_THRESHOLDS = {
        "pre": 0,      # No code yet
        "mid": 50,     # In progress
        "post": 70,    # Development complete
        "release": 85  # Ready for release
    }

    # Verification checks for each checkpoint type
    VERIFICATION_CHECKS = {
        "pre": [
            ("requirements_documented", "Requirements are documented"),
            ("constraints_identified", "Constraints are identified"),
            ("approach_selected", "Approach is selected and documented"),
        ],
        "mid": [
            ("following_plan", "Following the execution plan"),
            ("code_compiles", "Code compiles without errors"),
            ("basic_tests_pass", "Basic tests are passing"),
        ],
        "post": [
            ("all_requirements_met", "All requirements are implemented"),
            ("edge_cases_handled", "Edge cases are handled"),
            ("documentation_complete", "Documentation is complete"),
            ("tests_passing", "All tests are passing"),
        ],
        "release": [
            ("code_review_complete", "Code review is complete"),
            ("security_review_done", "Security review is complete"),
            ("performance_acceptable", "Performance meets requirements"),
            ("documentation_current", "Documentation is up to date"),
        ]
    }

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Checkpoint Manager.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.checkpoints: List[Checkpoint] = []

    def create_checkpoint(
        self,
        checkpoint_type: str,
        project_path: Optional[str] = None,
        code_path: Optional[str] = None,
        analyzer: Optional[Any] = None
    ) -> Dict:
        """
        Create a new checkpoint.

        Args:
            checkpoint_type: "pre", "mid", "post", or "release"
            project_path: Path to the project
            code_path: Optional specific code file to analyze
            analyzer: Optional ReasoningOptimizer instance

        Returns:
            Checkpoint dictionary with all verification results
        """
        if checkpoint_type not in self.SCORE_THRESHOLDS:
            raise ValueError(
                f"Invalid checkpoint type: {checkpoint_type}. "
                f"Must be one of: {list(self.SCORE_THRESHOLDS.keys())}"
            )

        # Initialize checkpoint
        checkpoint = Checkpoint(
            checkpoint_type=checkpoint_type,
            timestamp=datetime.now().isoformat(),
            project_path=project_path or ".",
            status="pending"
        )

        # Perform verification checks
        verification_results = self._perform_verification(
            checkpoint_type,
            project_path,
            code_path
        )
        checkpoint.verification_results = verification_results

        # Analyze code if analyzer provided and code path given
        if analyzer and code_path:
            analysis = self._analyze_code(analyzer, code_path)
            checkpoint.reasoning_score = analysis.get("score")
            checkpoint.phase_scores = analysis.get("phases")
            checkpoint.issues = analysis.get("issues")

        # Determine checkpoint status
        checkpoint.status = self._determine_status(
            checkpoint_type,
            checkpoint.reasoning_score,
            verification_results
        )

        # Add metadata
        checkpoint.metadata = {
            "threshold": self.SCORE_THRESHOLDS[checkpoint_type],
            "checks_performed": len(self.VERIFICATION_CHECKS[checkpoint_type]),
            "checks_passed": sum(
                1 for v in verification_results.values() if v["passed"]
            )
        }

        # Store checkpoint
        self.checkpoints.append(checkpoint)

        return asdict(checkpoint)

    def validate_checkpoint(
        self,
        checkpoint: Dict,
        strict: bool = False
    ) -> Dict:
        """
        Validate a checkpoint against requirements.

        Args:
            checkpoint: Checkpoint dictionary to validate
            strict: If True, all checks must pass

        Returns:
            Validation result dictionary
        """
        checkpoint_type = checkpoint.get("checkpoint_type", "post")
        threshold = self.SCORE_THRESHOLDS.get(checkpoint_type, 70)

        # Check score
        score = checkpoint.get("reasoning_score", 0)
        score_passed = score >= threshold if score else True

        # Check verifications
        verifications = checkpoint.get("verification_results", {})
        checks_passed = sum(1 for v in verifications.values() if v.get("passed"))
        total_checks = len(verifications)

        if strict:
            verification_passed = checks_passed == total_checks
        else:
            verification_passed = checks_passed >= (total_checks * 0.7)

        # Overall result
        passed = score_passed and verification_passed

        return {
            "passed": passed,
            "score_validation": {
                "passed": score_passed,
                "score": score,
                "threshold": threshold
            },
            "verification_validation": {
                "passed": verification_passed,
                "checks_passed": checks_passed,
                "total_checks": total_checks
            },
            "recommendations": self._generate_recommendations(checkpoint)
        }

    def get_checkpoint_report(
        self,
        checkpoint: Dict,
        format: str = "markdown"
    ) -> str:
        """
        Generate a formatted checkpoint report.

        Args:
            checkpoint: Checkpoint dictionary
            format: Output format ("markdown", "json", "text")

        Returns:
            Formatted report string
        """
        if format == "json":
            return json.dumps(checkpoint, indent=2)
        elif format == "text":
            return self._generate_text_report(checkpoint)
        else:
            return self._generate_markdown_report(checkpoint)

    def get_checkpoint_history(self, project_path: Optional[str] = None) -> List[Dict]:
        """
        Get checkpoint history for a project.

        Args:
            project_path: Optional project path to filter by

        Returns:
            List of checkpoint dictionaries
        """
        if project_path:
            return [
                asdict(cp) for cp in self.checkpoints
                if cp.project_path == project_path
            ]
        return [asdict(cp) for cp in self.checkpoints]

    def compare_checkpoints(
        self,
        checkpoint1: Dict,
        checkpoint2: Dict
    ) -> Dict:
        """
        Compare two checkpoints to track progress.

        Args:
            checkpoint1: Earlier checkpoint
            checkpoint2: Later checkpoint

        Returns:
            Comparison results dictionary
        """
        score1 = checkpoint1.get("reasoning_score", 0) or 0
        score2 = checkpoint2.get("reasoning_score", 0) or 0

        phases1 = checkpoint1.get("phase_scores", {}) or {}
        phases2 = checkpoint2.get("phase_scores", {}) or {}

        phase_changes = {}
        for phase in set(phases1.keys()) | set(phases2.keys()):
            old_score = phases1.get(phase, 0)
            new_score = phases2.get(phase, 0)
            phase_changes[phase] = {
                "old": old_score,
                "new": new_score,
                "change": new_score - old_score
            }

        return {
            "score_change": score2 - score1,
            "score_percentage_change": (
                ((score2 - score1) / max(score1, 1)) * 100
                if score1 > 0 else 0
            ),
            "phase_changes": phase_changes,
            "improvement": score2 > score1,
            "summary": self._generate_comparison_summary(
                score1, score2, phase_changes
            )
        }

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _perform_verification(
        self,
        checkpoint_type: str,
        project_path: Optional[str],
        code_path: Optional[str]
    ) -> Dict[str, Dict]:
        """Perform verification checks for checkpoint type."""
        checks = self.VERIFICATION_CHECKS.get(checkpoint_type, [])
        results = {}

        for check_id, description in checks:
            # Perform check (simplified - would be more sophisticated in practice)
            passed = self._run_check(check_id, project_path, code_path)

            results[check_id] = {
                "description": description,
                "passed": passed,
                "timestamp": datetime.now().isoformat()
            }

        return results

    def _run_check(
        self,
        check_id: str,
        project_path: Optional[str],
        code_path: Optional[str]
    ) -> bool:
        """
        Run a specific verification check.

        In a full implementation, this would perform actual verification.
        Here we return True as a placeholder - actual checks would be
        implemented based on the check_id.
        """
        # Placeholder implementation
        # In practice, each check would have specific logic

        if project_path and Path(project_path).exists():
            # Check for documentation files
            if check_id == "requirements_documented":
                return any(
                    Path(project_path).glob("**/README*")
                ) or any(
                    Path(project_path).glob("**/REQUIREMENTS*")
                )

            if check_id == "documentation_complete":
                return any(Path(project_path).glob("**/README*"))

        # Default to True for checks we can't verify automatically
        return True

    def _analyze_code(self, analyzer: Any, code_path: str) -> Dict:
        """Analyze code using provided analyzer."""
        try:
            path = Path(code_path)
            if path.exists():
                result = analyzer.analyze_file(code_path)
                return {
                    "score": result.overall_score,
                    "phases": result.phase_scores,
                    "issues": result.issues
                }
        except Exception as e:
            return {
                "score": None,
                "phases": None,
                "issues": [{"error": str(e)}]
            }

        return {"score": None, "phases": None, "issues": []}

    def _determine_status(
        self,
        checkpoint_type: str,
        score: Optional[int],
        verifications: Dict
    ) -> str:
        """Determine checkpoint status."""
        threshold = self.SCORE_THRESHOLDS[checkpoint_type]

        # Check score if available
        if score is not None and score < threshold:
            return "failed"

        # Check verification results
        if verifications:
            passed_count = sum(1 for v in verifications.values() if v["passed"])
            total_count = len(verifications)

            if passed_count < total_count * 0.7:  # 70% must pass
                return "failed"

        return "passed"

    def _generate_recommendations(self, checkpoint: Dict) -> List[str]:
        """Generate recommendations based on checkpoint results."""
        recommendations = []

        # Score-based recommendations
        score = checkpoint.get("reasoning_score")
        if score is not None:
            if score < 50:
                recommendations.append(
                    "Focus on improving documentation and comprehension"
                )
            elif score < 70:
                recommendations.append(
                    "Add edge case handling and input validation"
                )
            elif score < 85:
                recommendations.append(
                    "Polish code and address remaining TODOs"
                )

        # Verification-based recommendations
        verifications = checkpoint.get("verification_results", {})
        for check_id, result in verifications.items():
            if not result.get("passed"):
                recommendations.append(f"Address: {result.get('description')}")

        # Phase-based recommendations
        phase_scores = checkpoint.get("phase_scores", {})
        if phase_scores:
            weakest = min(phase_scores.items(), key=lambda x: x[1])
            if weakest[1] < 14:  # Less than 70% of 20
                recommendations.append(
                    f"Improve {weakest[0]} phase (score: {weakest[1]}/20)"
                )

        return recommendations[:5]  # Top 5 recommendations

    def _generate_markdown_report(self, checkpoint: Dict) -> str:
        """Generate markdown checkpoint report."""
        cp_type = checkpoint.get("checkpoint_type", "unknown").title()
        status = checkpoint.get("status", "unknown").upper()
        score = checkpoint.get("reasoning_score")

        report = f"## {cp_type} Checkpoint Report\n\n"
        report += f"**Date**: {checkpoint.get('timestamp', 'N/A')}\n"
        report += f"**Project**: {checkpoint.get('project_path', 'N/A')}\n"
        report += f"**Status**: {status}\n\n"

        if score is not None:
            report += f"### Reasoning Score: {score}/100\n\n"

            phase_scores = checkpoint.get("phase_scores", {})
            if phase_scores:
                report += "| Phase | Score | Status |\n"
                report += "|-------|-------|--------|\n"
                for phase, ps in phase_scores.items():
                    status_icon = "PASS" if ps >= 14 else "WARN"
                    report += f"| {phase.title()} | {ps}/20 | {status_icon} |\n"
                report += "\n"

        # Verification results
        verifications = checkpoint.get("verification_results", {})
        if verifications:
            report += "### Verification Checks\n\n"
            for check_id, result in verifications.items():
                icon = "PASS" if result["passed"] else "FAIL"
                report += f"- [{icon}] {result['description']}\n"
            report += "\n"

        # Issues
        issues = checkpoint.get("issues", [])
        if issues:
            report += "### Issues Found\n\n"
            for issue in issues[:5]:
                if isinstance(issue, dict):
                    report += f"- **{issue.get('phase', 'General')}**: {issue.get('issue', 'Unknown issue')}\n"
                else:
                    report += f"- {issue}\n"
            report += "\n"

        # Metadata
        metadata = checkpoint.get("metadata", {})
        if metadata:
            threshold = metadata.get("threshold", "N/A")
            passed = metadata.get("checks_passed", 0)
            total = metadata.get("checks_performed", 0)
            report += f"---\n"
            report += f"*Threshold: {threshold} | Checks: {passed}/{total} passed*\n"

        return report

    def _generate_text_report(self, checkpoint: Dict) -> str:
        """Generate plain text checkpoint report."""
        lines = []
        lines.append(f"{'=' * 50}")
        lines.append(f"{checkpoint.get('checkpoint_type', '').upper()} CHECKPOINT")
        lines.append(f"{'=' * 50}")
        lines.append(f"Date: {checkpoint.get('timestamp', 'N/A')}")
        lines.append(f"Status: {checkpoint.get('status', 'N/A').upper()}")

        score = checkpoint.get("reasoning_score")
        if score is not None:
            lines.append(f"Reasoning Score: {score}/100")

        lines.append(f"{'=' * 50}")
        return "\n".join(lines)

    def _generate_comparison_summary(
        self,
        score1: int,
        score2: int,
        phase_changes: Dict
    ) -> str:
        """Generate summary of checkpoint comparison."""
        if score2 > score1:
            summary = f"Improved from {score1} to {score2} (+{score2 - score1} points). "
        elif score2 < score1:
            summary = f"Declined from {score1} to {score2} ({score2 - score1} points). "
        else:
            summary = f"Score unchanged at {score1}. "

        # Find biggest improvements/declines
        improvements = [
            (phase, change["change"])
            for phase, change in phase_changes.items()
            if change["change"] > 0
        ]
        declines = [
            (phase, change["change"])
            for phase, change in phase_changes.items()
            if change["change"] < 0
        ]

        if improvements:
            best = max(improvements, key=lambda x: x[1])
            summary += f"Biggest improvement: {best[0]} (+{best[1]}). "

        if declines:
            worst = min(declines, key=lambda x: x[1])
            summary += f"Needs attention: {worst[0]} ({worst[1]}). "

        return summary
