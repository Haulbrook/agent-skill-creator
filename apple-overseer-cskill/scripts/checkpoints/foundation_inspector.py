"""
Level 1: Foundation Inspector
Validates code syntax, structure, dependencies, and build configuration.
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from ..models import (
    CheckpointReport, CheckpointStatus, CheckpointLevel,
    Issue, Platform
)


class FoundationInspector:
    """
    Level 1 Checkpoint: Foundation Quality Inspector

    Validates:
    - Project structure and organization
    - Build configuration files (Xcode project, Package.swift, etc.)
    - Swift/Objective-C syntax basics
    - Dependency declarations
    - Common code quality issues
    """

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.issues: List[Issue] = []
        self.warnings: List[Issue] = []
        self.info: List[Issue] = []
        self.passed_checks: List[str] = []
        self.failed_checks: List[str] = []

    def validate(self) -> CheckpointReport:
        """
        Run foundation validation checks.

        Returns:
            CheckpointReport with validation results
        """
        start_time = datetime.now()

        # Run all foundation checks
        self._check_project_structure()
        self._check_build_configuration()
        self._check_swift_files()
        self._check_dependencies()
        self._check_info_plist()
        self._check_code_organization()

        duration = (datetime.now() - start_time).total_seconds()

        # Determine overall status
        status = self._determine_status()

        return CheckpointReport(
            level=CheckpointLevel.FOUNDATION,
            checkpoint_name="Foundation Inspector",
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
                "inspector_version": "1.0.0"
            },
            recommendations=self._generate_recommendations()
        )

    def _check_project_structure(self):
        """Validate basic project structure."""
        check_name = "Project Structure Validation"

        if not self.project_path.exists():
            self.issues.append(Issue(
                severity="error",
                message=f"Project path does not exist: {self.project_path}",
                category="structure"
            ))
            self.failed_checks.append(check_name)
            return

        # Look for common Apple project indicators
        has_xcodeproj = any(self.project_path.glob("*.xcodeproj"))
        has_xcworkspace = any(self.project_path.glob("*.xcworkspace"))
        has_package_swift = (self.project_path / "Package.swift").exists()

        if not (has_xcodeproj or has_xcworkspace or has_package_swift):
            self.issues.append(Issue(
                severity="error",
                message="No Xcode project (.xcodeproj), workspace (.xcworkspace), or Swift Package (Package.swift) found",
                category="structure",
                suggestion="Ensure this is a valid Apple platform project"
            ))
            self.failed_checks.append(check_name)
        else:
            self.passed_checks.append(check_name)
            self.info.append(Issue(
                severity="info",
                message=f"Found valid project structure: "
                        f"{'Xcode Project' if has_xcodeproj else ''} "
                        f"{'Workspace' if has_xcworkspace else ''} "
                        f"{'Swift Package' if has_package_swift else ''}",
                category="structure"
            ))

    def _check_build_configuration(self):
        """Check build configuration files."""
        check_name = "Build Configuration"

        # Check for Podfile (CocoaPods)
        podfile = self.project_path / "Podfile"
        if podfile.exists():
            self.passed_checks.append(f"{check_name}: Podfile")
            # Check if Podfile.lock exists
            if not (self.project_path / "Podfile.lock").exists():
                self.warnings.append(Issue(
                    severity="warning",
                    message="Podfile exists but Podfile.lock not found",
                    file_path=str(podfile),
                    category="dependencies",
                    suggestion="Run 'pod install' to generate Podfile.lock"
                ))

        # Check for Cartfile (Carthage)
        cartfile = self.project_path / "Cartfile"
        if cartfile.exists():
            self.passed_checks.append(f"{check_name}: Cartfile")

        # Check for Package.swift (Swift Package Manager)
        package_swift = self.project_path / "Package.swift"
        if package_swift.exists():
            self.passed_checks.append(f"{check_name}: Package.swift")
            self._validate_package_swift(package_swift)

        if not any([podfile.exists(), cartfile.exists(), package_swift.exists()]):
            self.info.append(Issue(
                severity="info",
                message="No dependency manager configuration found (Podfile, Cartfile, Package.swift)",
                category="dependencies"
            ))

    def _validate_package_swift(self, package_path: Path):
        """Validate Package.swift syntax."""
        try:
            content = package_path.read_text()

            # Basic syntax checks
            if "import PackageDescription" not in content:
                self.warnings.append(Issue(
                    severity="warning",
                    message="Package.swift missing 'import PackageDescription'",
                    file_path=str(package_path),
                    category="build"
                ))

            if "let package = Package(" not in content:
                self.issues.append(Issue(
                    severity="error",
                    message="Package.swift missing Package declaration",
                    file_path=str(package_path),
                    category="build"
                ))

        except Exception as e:
            self.issues.append(Issue(
                severity="error",
                message=f"Failed to read Package.swift: {str(e)}",
                file_path=str(package_path),
                category="build"
            ))

    def _check_swift_files(self):
        """Perform basic Swift syntax and quality checks."""
        check_name = "Swift Code Quality"

        swift_files = list(self.project_path.rglob("*.swift"))

        if not swift_files:
            self.warnings.append(Issue(
                severity="warning",
                message="No Swift files found in project",
                category="code"
            ))
            return

        self.info.append(Issue(
            severity="info",
            message=f"Found {len(swift_files)} Swift files",
            category="code"
        ))

        issues_found = False
        for swift_file in swift_files[:20]:  # Check first 20 files
            try:
                content = swift_file.read_text()

                # Check for common issues
                if "import Foundation" not in content and "import UIKit" not in content and "import AppKit" not in content:
                    # File might not need imports, just note it
                    pass

                # Check for force unwrapping (potential crashes)
                force_unwraps = re.findall(r'!\s*(?![=])', content)
                if len(force_unwraps) > 5:
                    self.warnings.append(Issue(
                        severity="warning",
                        message=f"Excessive force unwrapping ({len(force_unwraps)} instances)",
                        file_path=str(swift_file),
                        category="code-quality",
                        suggestion="Consider using optional binding (if let, guard let) instead"
                    ))
                    issues_found = True

                # Check for print statements (should use proper logging)
                print_statements = re.findall(r'\bprint\s*\(', content)
                if len(print_statements) > 3:
                    self.warnings.append(Issue(
                        severity="warning",
                        message=f"Multiple print statements ({len(print_statements)} found)",
                        file_path=str(swift_file),
                        category="code-quality",
                        suggestion="Consider using os.log or Logger for production code"
                    ))

            except Exception as e:
                self.warnings.append(Issue(
                    severity="warning",
                    message=f"Could not analyze {swift_file.name}: {str(e)}",
                    file_path=str(swift_file),
                    category="code"
                ))

        if not issues_found:
            self.passed_checks.append(check_name)
        else:
            self.failed_checks.append(check_name)

    def _check_dependencies(self):
        """Check dependency declarations and potential issues."""
        check_name = "Dependency Analysis"

        # Check Package.swift dependencies
        package_swift = self.project_path / "Package.swift"
        if package_swift.exists():
            try:
                content = package_swift.read_text()

                # Count dependencies
                dep_count = content.count(".package(")
                self.info.append(Issue(
                    severity="info",
                    message=f"Found {dep_count} package dependencies in Package.swift",
                    category="dependencies"
                ))

                # Check for version pinning
                if ".upToNextMajor" in content or ".upToNextMinor" in content:
                    self.passed_checks.append(f"{check_name}: Version Constraints")
                else:
                    self.warnings.append(Issue(
                        severity="warning",
                        message="Dependencies may not have version constraints",
                        file_path=str(package_swift),
                        category="dependencies",
                        suggestion="Consider using .upToNextMajor or .upToNextMinor for stability"
                    ))

            except Exception as e:
                self.warnings.append(Issue(
                    severity="warning",
                    message=f"Could not analyze dependencies: {str(e)}",
                    category="dependencies"
                ))

    def _check_info_plist(self):
        """Check for Info.plist files and basic configurations."""
        check_name = "Info.plist Configuration"

        info_plists = list(self.project_path.rglob("Info.plist"))

        if not info_plists:
            self.info.append(Issue(
                severity="info",
                message="No Info.plist files found (may be using Info.plist-less approach)",
                category="configuration"
            ))
            return

        for plist in info_plists:
            self.passed_checks.append(f"{check_name}: {plist.name}")

            # Basic validation
            try:
                content = plist.read_text()

                # Check for required keys (basic check)
                if "CFBundleIdentifier" not in content:
                    self.warnings.append(Issue(
                        severity="warning",
                        message="Info.plist may be missing CFBundleIdentifier",
                        file_path=str(plist),
                        category="configuration"
                    ))

            except Exception as e:
                self.warnings.append(Issue(
                    severity="warning",
                    message=f"Could not read Info.plist: {str(e)}",
                    file_path=str(plist),
                    category="configuration"
                ))

    def _check_code_organization(self):
        """Check code organization and file structure."""
        check_name = "Code Organization"

        # Check for common directories
        common_dirs = ["Models", "Views", "Controllers", "ViewModels", "Services", "Utilities"]
        found_dirs = []

        for dir_name in common_dirs:
            if any(self.project_path.rglob(dir_name)):
                found_dirs.append(dir_name)

        if found_dirs:
            self.passed_checks.append(f"{check_name}: Structured Organization")
            self.info.append(Issue(
                severity="info",
                message=f"Found organized directories: {', '.join(found_dirs)}",
                category="organization"
            ))
        else:
            self.info.append(Issue(
                severity="info",
                message="No standard organization pattern detected",
                category="organization"
            ))

    def _determine_status(self) -> CheckpointStatus:
        """Determine overall checkpoint status."""
        if self.issues:
            return CheckpointStatus.FAILED
        elif self.warnings:
            return CheckpointStatus.WARNING
        elif self.passed_checks:
            return CheckpointStatus.PASSED
        else:
            return CheckpointStatus.PENDING

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []

        if self.issues:
            recommendations.append("Fix critical issues before proceeding to platform-specific validation")

        if len(self.warnings) > 5:
            recommendations.append("Address warnings to improve code quality")

        if not any("Swift Code Quality" in check for check in self.passed_checks):
            recommendations.append("Review Swift code for quality and best practices")

        if not self.passed_checks:
            recommendations.append("Ensure project has valid structure and configuration")

        return recommendations
