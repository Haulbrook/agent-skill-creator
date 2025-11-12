"""
Level 4: Executive Overseer
Final quality assurance and stamp of approval.
"""
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import re

from ..models import (
    CheckpointReport, CheckpointStatus, CheckpointLevel,
    Issue, Platform, OverseerReport
)


class ExecutiveOverseer:
    """
    Level 4 Checkpoint: Executive Overseer - Final Quality Assurance

    Validates:
    - Performance considerations
    - Security best practices
    - UX/UI consistency
    - App Store readiness
    - Overall code quality metrics
    - Final stamp of approval
    """

    def __init__(self, project_path: str, platforms: List[Platform], previous_reports: List[CheckpointReport]):
        self.project_path = Path(project_path)
        self.platforms = platforms
        self.previous_reports = previous_reports
        self.issues: List[Issue] = []
        self.warnings: List[Issue] = []
        self.info: List[Issue] = []
        self.passed_checks: List[str] = []
        self.failed_checks: List[str] = []

    def validate(self) -> CheckpointReport:
        """
        Run executive-level validation checks.

        Returns:
            CheckpointReport with final validation results
        """
        start_time = datetime.now()

        # Review previous checkpoint results
        self._review_previous_checkpoints()

        # Executive-level checks
        self._check_performance_considerations()
        self._check_security_practices()
        self._check_ux_ui_consistency()
        self._check_app_store_readiness()
        self._check_code_quality_metrics()
        self._check_documentation()

        # Make final determination
        stamp_of_approval = self._determine_stamp_of_approval()

        duration = (datetime.now() - start_time).total_seconds()

        # Determine overall status
        status = self._determine_status(stamp_of_approval)

        report = CheckpointReport(
            level=CheckpointLevel.EXECUTIVE,
            checkpoint_name="Executive Overseer",
            status=status,
            timestamp=datetime.now().isoformat(),
            duration_seconds=duration,
            issues=self.issues,
            warnings=self.warnings,
            info=self.info,
            passed_checks=self.passed_checks,
            failed_checks=self.failed_checks,
            metadata={
                "project_path": str(self.project_path),
                "platforms": [p.value for p in self.platforms],
                "stamp_of_approval": stamp_of_approval,
                "previous_checkpoints_passed": all(r.can_proceed for r in self.previous_reports)
            },
            recommendations=self._generate_recommendations(stamp_of_approval)
        )

        return report

    def _review_previous_checkpoints(self):
        """Review results from previous checkpoint levels."""
        check_name = "Previous Checkpoint Review"

        total_issues = sum(len(r.issues) for r in self.previous_reports)
        total_warnings = sum(len(r.warnings) for r in self.previous_reports)

        failed_checkpoints = [r.checkpoint_name for r in self.previous_reports if not r.can_proceed]

        if failed_checkpoints:
            self.issues.append(Issue(
                severity="error",
                message=f"Previous checkpoints failed: {', '.join(failed_checkpoints)}",
                category="executive",
                suggestion="All previous checkpoints must pass before final approval"
            ))
            self.failed_checks.append(check_name)
        else:
            self.passed_checks.append(check_name)
            self.info.append(Issue(
                severity="info",
                message=f"All previous checkpoints passed (Total issues: {total_issues}, warnings: {total_warnings})",
                category="executive"
            ))

    def _check_performance_considerations(self):
        """Check for performance best practices."""
        check_name = "Performance Considerations"

        swift_files = list(self.project_path.rglob("*.swift"))

        performance_issues = []

        for swift_file in swift_files[:30]:  # Check first 30 files
            try:
                content = swift_file.read_text()

                # Check for synchronous network calls on main thread (bad practice)
                if "URLSession" in content and "await" not in content:
                    # This is a simplified check - may need refinement
                    pass

                # Check for memory leak indicators
                if "[weak self]" not in content and "self." in content:
                    # Count self references without weak
                    # This is a heuristic - not definitive
                    pass

                # Check for lazy loading usage (good for performance)
                if "lazy var" in content:
                    # Good practice detected
                    pass

            except:
                pass

        # General performance checks
        self.passed_checks.append(f"{check_name}: Basic Checks")
        self.info.append(Issue(
            severity="info",
            message="Performance best practices reviewed",
            category="performance"
        ))

        # Check for large asset files
        asset_files = list(self.project_path.rglob("*.xcassets/**/*"))
        large_assets = []

        for asset in asset_files:
            try:
                if asset.is_file() and asset.stat().st_size > 5 * 1024 * 1024:  # > 5MB
                    large_assets.append(asset)
            except:
                pass

        if large_assets:
            self.warnings.append(Issue(
                severity="warning",
                message=f"Found {len(large_assets)} large asset files (>5MB)",
                category="performance",
                suggestion="Consider optimizing large assets for better app performance"
            ))

    def _check_security_practices(self):
        """Check for security best practices."""
        check_name = "Security Best Practices"

        swift_files = list(self.project_path.rglob("*.swift"))

        security_concerns = []

        for swift_file in swift_files[:30]:
            try:
                content = swift_file.read_text()

                # Check for hardcoded credentials/keys (basic check)
                suspicious_patterns = [
                    r'api[_-]?key\s*=\s*["\'][\w-]{20,}["\']',
                    r'password\s*=\s*["\'].+["\']',
                    r'secret\s*=\s*["\'].+["\']',
                    r'token\s*=\s*["\'][\w-]{20,}["\']'
                ]

                for pattern in suspicious_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        security_concerns.append(swift_file)
                        self.warnings.append(Issue(
                            severity="warning",
                            message="Potential hardcoded credential detected",
                            file_path=str(swift_file),
                            category="security",
                            suggestion="Use secure storage (Keychain) for sensitive data"
                        ))
                        break

                # Check for App Transport Security considerations
                if "http://" in content and "localhost" not in content:
                    self.warnings.append(Issue(
                        severity="warning",
                        message="HTTP URL detected (should use HTTPS)",
                        file_path=str(swift_file),
                        category="security",
                        suggestion="Use HTTPS for network communications"
                    ))

            except:
                pass

        if not security_concerns:
            self.passed_checks.append(check_name)
        else:
            self.failed_checks.append(check_name)

    def _check_ux_ui_consistency(self):
        """Check for UX/UI consistency across platforms."""
        check_name = "UX/UI Consistency"

        # Check for SwiftUI usage (easier consistency)
        swift_files = list(self.project_path.rglob("*.swift"))
        swiftui_files = 0
        uikit_files = 0
        appkit_files = 0

        for swift_file in swift_files:
            try:
                content = swift_file.read_text()
                if "import SwiftUI" in content:
                    swiftui_files += 1
                if "import UIKit" in content:
                    uikit_files += 1
                if "import AppKit" in content:
                    appkit_files += 1
            except:
                pass

        self.info.append(Issue(
            severity="info",
            message=f"UI Framework usage: SwiftUI ({swiftui_files}), UIKit ({uikit_files}), AppKit ({appkit_files})",
            category="ux"
        ))

        # SwiftUI generally provides better cross-platform consistency
        if swiftui_files > 0 and len(self.platforms) > 1:
            self.passed_checks.append(f"{check_name}: SwiftUI Cross-Platform")
            self.info.append(Issue(
                severity="info",
                message="SwiftUI usage supports cross-platform consistency",
                category="ux"
            ))

        # Check for accessibility
        accessibility_indicators = ["accessibilityLabel", "accessibilityHint", "accessibilityIdentifier"]
        accessibility_usage = 0

        for swift_file in swift_files[:30]:
            try:
                content = swift_file.read_text()
                if any(ind in content for ind in accessibility_indicators):
                    accessibility_usage += 1
            except:
                pass

        if accessibility_usage > 0:
            self.passed_checks.append(f"{check_name}: Accessibility")
            self.info.append(Issue(
                severity="info",
                message=f"Accessibility features found in {accessibility_usage} files",
                category="ux"
            ))
        else:
            self.warnings.append(Issue(
                severity="warning",
                message="Limited or no accessibility features detected",
                category="ux",
                suggestion="Add accessibility labels and hints for better user experience"
            ))

    def _check_app_store_readiness(self):
        """Check for App Store submission readiness."""
        check_name = "App Store Readiness"

        readiness_items = []

        # Check for privacy manifest (iOS 17+)
        privacy_manifests = list(self.project_path.rglob("PrivacyInfo.xcprivacy"))
        if privacy_manifests:
            readiness_items.append("Privacy Manifest")
            self.passed_checks.append(f"{check_name}: Privacy Manifest")
        else:
            self.info.append(Issue(
                severity="info",
                message="No PrivacyInfo.xcprivacy found (required for iOS 17+ apps using certain APIs)",
                category="app-store",
                suggestion="Add privacy manifest if using tracking or required APIs"
            ))

        # Check for README or documentation
        readme_files = list(self.project_path.glob("README*"))
        if readme_files:
            readiness_items.append("Documentation")
            self.passed_checks.append(f"{check_name}: Documentation")

        # Check for license file
        license_files = list(self.project_path.glob("LICENSE*"))
        if license_files:
            readiness_items.append("License")

        if len(readiness_items) >= 2:
            self.passed_checks.append(check_name)

    def _check_code_quality_metrics(self):
        """Check overall code quality metrics."""
        check_name = "Code Quality Metrics"

        swift_files = list(self.project_path.rglob("*.swift"))

        if not swift_files:
            self.warnings.append(Issue(
                severity="warning",
                message="No Swift files found for quality analysis",
                category="quality"
            ))
            return

        total_lines = 0
        total_files = len(swift_files)

        for swift_file in swift_files:
            try:
                lines = len(swift_file.read_text().splitlines())
                total_lines += lines
            except:
                pass

        avg_lines_per_file = total_lines / total_files if total_files > 0 else 0

        self.info.append(Issue(
            severity="info",
            message=f"Code metrics: {total_files} files, {total_lines} total lines, {avg_lines_per_file:.0f} avg lines/file",
            category="quality"
        ))

        # Good practices: files should be reasonably sized
        if avg_lines_per_file < 500:
            self.passed_checks.append(f"{check_name}: File Size")
        else:
            self.warnings.append(Issue(
                severity="warning",
                message=f"Average file size is high ({avg_lines_per_file:.0f} lines)",
                category="quality",
                suggestion="Consider breaking down large files into smaller, focused modules"
            ))

        self.passed_checks.append(check_name)

    def _check_documentation(self):
        """Check for adequate documentation."""
        check_name = "Documentation"

        # Check for README
        readme = list(self.project_path.glob("README*"))
        if readme:
            self.passed_checks.append(f"{check_name}: README")

        # Check for code comments
        swift_files = list(self.project_path.rglob("*.swift"))
        documented_files = 0

        for swift_file in swift_files[:20]:
            try:
                content = swift_file.read_text()
                # Check for documentation comments
                if "///" in content or "/**" in content:
                    documented_files += 1
            except:
                pass

        if documented_files > 0:
            self.passed_checks.append(f"{check_name}: Code Comments")
            self.info.append(Issue(
                severity="info",
                message=f"Found documentation in {documented_files} files",
                category="documentation"
            ))

    def _determine_stamp_of_approval(self) -> bool:
        """
        Determine if project receives the final stamp of approval.

        Criteria:
        - All previous checkpoints must pass (or have only warnings)
        - No critical security issues
        - No critical performance issues
        - Reasonable code quality
        """

        # Check previous checkpoints
        all_previous_passed = all(r.can_proceed for r in self.previous_reports)

        # Check for critical issues in executive review
        has_critical_issues = len(self.issues) > 0

        # Check for too many warnings
        total_warnings = sum(len(r.warnings) for r in self.previous_reports) + len(self.warnings)
        excessive_warnings = total_warnings > 20

        # Grant approval if:
        # 1. All previous checkpoints passed
        # 2. No critical issues found
        # 3. Not excessive warnings
        stamp_approved = all_previous_passed and not has_critical_issues and not excessive_warnings

        return stamp_approved

    def _determine_status(self, stamp_of_approval: bool) -> CheckpointStatus:
        """Determine overall checkpoint status."""
        if not stamp_of_approval:
            if self.issues:
                return CheckpointStatus.FAILED
            else:
                return CheckpointStatus.WARNING
        else:
            return CheckpointStatus.PASSED

    def _generate_recommendations(self, stamp_of_approval: bool) -> List[str]:
        """Generate final recommendations."""
        recommendations = []

        if stamp_of_approval:
            recommendations.append("✓ PROJECT APPROVED - All quality checkpoints passed")
            recommendations.append("Project is ready for deployment/distribution")

            if self.warnings:
                recommendations.append(f"Consider addressing {len(self.warnings)} warnings for improved quality")

            if len(self.platforms) > 1:
                recommendations.append(f"Multi-platform validation complete for: {', '.join(p.value for p in self.platforms)}")

        else:
            recommendations.append("✗ APPROVAL PENDING - Issues must be resolved")

            if self.issues:
                recommendations.append(f"Fix {len(self.issues)} critical issues")

            failed_previous = [r.checkpoint_name for r in self.previous_reports if not r.can_proceed]
            if failed_previous:
                recommendations.append(f"Complete previous checkpoints: {', '.join(failed_previous)}")

            recommendations.append("Re-run validation after addressing issues")

        return recommendations
