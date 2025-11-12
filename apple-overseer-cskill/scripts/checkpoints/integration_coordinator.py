"""
Level 3: Integration Coordinator
Validates cross-platform compatibility and integration.
"""
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime
import re

from ..models import (
    CheckpointReport, CheckpointStatus, CheckpointLevel,
    Issue, Platform
)


class IntegrationCoordinator:
    """
    Level 3 Checkpoint: Integration and Cross-Platform Coordinator

    Validates:
    - Cross-platform code compatibility
    - Shared code and resources
    - Platform-specific conditional compilation
    - Consistent API usage across platforms
    - Resource sharing and optimization
    """

    def __init__(self, project_path: str, platforms: List[Platform]):
        self.project_path = Path(project_path)
        self.platforms = platforms
        self.issues: List[Issue] = []
        self.warnings: List[Issue] = []
        self.info: List[Issue] = []
        self.passed_checks: List[str] = []
        self.failed_checks: List[str] = []

    def validate(self) -> CheckpointReport:
        """
        Run integration validation checks.

        Returns:
            CheckpointReport with validation results
        """
        start_time = datetime.now()

        # Only run integration checks if multiple platforms
        if len(self.platforms) > 1:
            self._check_conditional_compilation()
            self._check_shared_code()
            self._check_platform_specific_apis()
            self._check_resource_sharing()
            self._check_architecture_consistency()
        else:
            self.info.append(Issue(
                severity="info",
                message="Single platform project - integration checks not applicable",
                category="integration"
            ))
            self.passed_checks.append("Integration: Single Platform (N/A)")

        duration = (datetime.now() - start_time).total_seconds()

        # Determine overall status
        status = self._determine_status()

        return CheckpointReport(
            level=CheckpointLevel.INTEGRATION,
            checkpoint_name="Integration Coordinator",
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
                "integration_scope": "multi-platform" if len(self.platforms) > 1 else "single-platform"
            },
            recommendations=self._generate_recommendations()
        )

    def _check_conditional_compilation(self):
        """Check proper use of conditional compilation for platform-specific code."""
        check_name = "Conditional Compilation"

        swift_files = list(self.project_path.rglob("*.swift"))

        # Platform compilation conditions
        compilation_conditions = {
            "iOS": r"#if\s+(?:os\(iOS\)|canImport\(UIKit\))",
            "macOS": r"#if\s+(?:os\(macOS\)|canImport\(AppKit\))",
            "iPadOS": r"#if\s+(?:os\(iOS\)|canImport\(UIKit\))",  # iPadOS shares iOS condition
            "tvOS": r"#if\s+(?:os\(tvOS\))",
            "watchOS": r"#if\s+(?:os\(watchOS\))"
        }

        files_with_conditions = 0
        improper_conditions = []

        for swift_file in swift_files:
            try:
                content = swift_file.read_text()

                # Check for any conditional compilation
                if "#if" in content:
                    files_with_conditions += 1

                    # Check for proper closure
                    if_count = content.count("#if")
                    endif_count = content.count("#endif")

                    if if_count != endif_count:
                        improper_conditions.append(swift_file)
                        self.issues.append(Issue(
                            severity="error",
                            message="Mismatched #if/#endif directives",
                            file_path=str(swift_file),
                            category="integration",
                            suggestion="Ensure all #if blocks have corresponding #endif"
                        ))

            except Exception as e:
                self.warnings.append(Issue(
                    severity="warning",
                    message=f"Could not analyze {swift_file.name}: {str(e)}",
                    category="integration"
                ))

        if improper_conditions:
            self.failed_checks.append(check_name)
        elif files_with_conditions > 0:
            self.passed_checks.append(check_name)
            self.info.append(Issue(
                severity="info",
                message=f"Found {files_with_conditions} files using conditional compilation",
                category="integration"
            ))
        else:
            self.info.append(Issue(
                severity="info",
                message="No conditional compilation detected (may use separate targets)",
                category="integration"
            ))

    def _check_shared_code(self):
        """Check for properly shared code across platforms."""
        check_name = "Shared Code Architecture"

        # Look for common shared code patterns
        shared_indicators = [
            "Shared",
            "Common",
            "Core",
            "Models",
            "Utilities",
            "Services"
        ]

        shared_dirs = []
        for indicator in shared_indicators:
            found = list(self.project_path.rglob(f"**/{indicator}"))
            if found:
                shared_dirs.extend(found)

        if shared_dirs:
            self.passed_checks.append(check_name)
            self.info.append(Issue(
                severity="info",
                message=f"Found {len(set(shared_dirs))} shared code directories",
                category="integration"
            ))
        else:
            if len(self.platforms) > 1:
                self.warnings.append(Issue(
                    severity="warning",
                    message="No obvious shared code structure detected for multi-platform project",
                    category="integration",
                    suggestion="Consider organizing shared code in Common/Shared directories"
                ))

    def _check_platform_specific_apis(self):
        """Check for platform-specific API usage and proper isolation."""
        check_name = "Platform API Isolation"

        swift_files = list(self.project_path.rglob("*.swift"))

        # Platform-specific APIs to watch for
        ios_apis = ["UIKit", "UIViewController", "UIView", "UIApplication"]
        macos_apis = ["AppKit", "NSViewController", "NSView", "NSApplication"]

        mixed_usage_files = []

        for swift_file in swift_files:
            try:
                content = swift_file.read_text()

                has_ios = any(api in content for api in ios_apis)
                has_macos = any(api in content for api in macos_apis)

                # Flag files mixing platform APIs without conditional compilation
                if has_ios and has_macos and "#if" not in content:
                    mixed_usage_files.append(swift_file)
                    self.warnings.append(Issue(
                        severity="warning",
                        message="File contains both iOS and macOS APIs without conditional compilation",
                        file_path=str(swift_file),
                        category="integration",
                        suggestion="Use #if os(iOS) / #if os(macOS) to separate platform-specific code"
                    ))

            except:
                pass

        if not mixed_usage_files:
            self.passed_checks.append(check_name)
        else:
            self.failed_checks.append(check_name)

    def _check_resource_sharing(self):
        """Check for shared resources and assets."""
        check_name = "Resource Sharing"

        # Look for asset catalogs
        asset_catalogs = list(self.project_path.rglob("*.xcassets"))

        if len(asset_catalogs) == 1 and len(self.platforms) > 1:
            self.passed_checks.append(f"{check_name}: Single Asset Catalog")
            self.info.append(Issue(
                severity="info",
                message="Using single asset catalog for all platforms (good for consistency)",
                category="integration"
            ))
        elif len(asset_catalogs) > 1:
            self.info.append(Issue(
                severity="info",
                message=f"Found {len(asset_catalogs)} asset catalogs (platform-specific assets)",
                category="integration"
            ))

        # Check for localization
        lproj_dirs = list(self.project_path.rglob("*.lproj"))
        if lproj_dirs:
            self.passed_checks.append(f"{check_name}: Localization")
            self.info.append(Issue(
                severity="info",
                message=f"Found {len(lproj_dirs)} localization directories",
                category="integration"
            ))

    def _check_architecture_consistency(self):
        """Check for consistent architecture patterns across platforms."""
        check_name = "Architecture Consistency"

        swift_files = list(self.project_path.rglob("*.swift"))

        # Look for architecture patterns
        mvvm_indicators = ["ViewModel", "viewModel"]
        mvc_indicators = ["Controller", "ViewController"]
        viper_indicators = ["Presenter", "Interactor", "Router"]

        mvvm_count = 0
        mvc_count = 0
        viper_count = 0

        for swift_file in swift_files:
            try:
                content = swift_file.read_text()

                if any(ind in content for ind in mvvm_indicators):
                    mvvm_count += 1
                if any(ind in content for ind in mvc_indicators):
                    mvc_count += 1
                if any(ind in content for ind in viper_indicators):
                    viper_count += 1

            except:
                pass

        # Report architecture patterns
        patterns_found = []
        if mvvm_count > 0:
            patterns_found.append(f"MVVM ({mvvm_count} files)")
        if mvc_count > 0:
            patterns_found.append(f"MVC ({mvc_count} files)")
        if viper_count > 0:
            patterns_found.append(f"VIPER ({viper_count} files)")

        if patterns_found:
            self.passed_checks.append(check_name)
            self.info.append(Issue(
                severity="info",
                message=f"Architecture patterns detected: {', '.join(patterns_found)}",
                category="integration"
            ))

            # Warn if mixing multiple patterns heavily
            if len(patterns_found) > 2:
                self.warnings.append(Issue(
                    severity="warning",
                    message="Multiple architecture patterns detected",
                    category="integration",
                    suggestion="Consider standardizing on one architecture pattern for consistency"
                ))

    def _determine_status(self) -> CheckpointStatus:
        """Determine overall checkpoint status."""
        if self.issues:
            return CheckpointStatus.FAILED
        elif self.warnings:
            return CheckpointStatus.WARNING
        elif self.passed_checks or len(self.platforms) == 1:
            return CheckpointStatus.PASSED
        else:
            return CheckpointStatus.PENDING

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []

        if len(self.platforms) > 1:
            if self.issues:
                recommendations.append("Fix platform integration issues before final validation")

            if any("Architecture Consistency" in check for check in self.failed_checks):
                recommendations.append("Standardize architecture patterns across platforms")

            if any("mixed usage" in str(i.message) for i in self.warnings):
                recommendations.append("Properly isolate platform-specific APIs with conditional compilation")

            recommendations.append("Proceed to Executive Overseer for final quality assurance")
        else:
            recommendations.append("Single platform - ready for final executive validation")

        return recommendations
