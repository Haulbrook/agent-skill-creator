"""
Level 2: Platform-Specific Overseers
Validates iOS, macOS, and iPadOS specific requirements and APIs.
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models import (
    CheckpointReport, CheckpointStatus, CheckpointLevel,
    Issue, Platform, PlatformValidationResult
)


class PlatformOverseer:
    """
    Level 2 Checkpoint: Platform-Specific Validation

    Validates platform-specific requirements, APIs, and configurations
    for iOS, macOS, and iPadOS.
    """

    def __init__(self, project_path: str, platforms: List[Platform]):
        self.project_path = Path(project_path)
        self.platforms = platforms
        self.issues: List[Issue] = []
        self.warnings: List[Issue] = []
        self.info: List[Issue] = []
        self.passed_checks: List[str] = []
        self.failed_checks: List[str] = []
        self.platform_results: List[PlatformValidationResult] = []

    def validate(self) -> CheckpointReport:
        """
        Run platform-specific validation checks.

        Returns:
            CheckpointReport with validation results
        """
        start_time = datetime.now()

        # Validate each platform
        for platform in self.platforms:
            result = self._validate_platform(platform)
            self.platform_results.append(result)

        duration = (datetime.now() - start_time).total_seconds()

        # Determine overall status
        status = self._determine_status()

        return CheckpointReport(
            level=CheckpointLevel.PLATFORM_SPECIFIC,
            checkpoint_name="Platform-Specific Overseers",
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
                "platforms_validated": [p.value for p in self.platforms],
                "platform_results": [
                    {
                        "platform": r.platform.value,
                        "status": r.status.value,
                        "checks": r.checks_performed
                    }
                    for r in self.platform_results
                ]
            },
            recommendations=self._generate_recommendations()
        )

    def _validate_platform(self, platform: Platform) -> PlatformValidationResult:
        """Validate a specific platform."""
        if platform == Platform.IOS:
            return self._validate_ios()
        elif platform == Platform.MACOS:
            return self._validate_macos()
        elif platform == Platform.IPADOS:
            return self._validate_ipados()
        elif platform == Platform.TVOS:
            return self._validate_tvos()
        elif platform == Platform.WATCHOS:
            return self._validate_watchos()
        else:
            return PlatformValidationResult(
                platform=platform,
                status=CheckpointStatus.SKIPPED,
                checks_performed=[],
                issues=[]
            )

    def _validate_ios(self) -> PlatformValidationResult:
        """iOS-specific validation."""
        checks_performed = []
        platform_issues = []

        # Check for UIKit usage
        swift_files = list(self.project_path.rglob("*.swift"))
        uikit_imports = 0
        swiftui_imports = 0

        for swift_file in swift_files:
            try:
                content = swift_file.read_text()
                if "import UIKit" in content:
                    uikit_imports += 1
                if "import SwiftUI" in content:
                    swiftui_imports += 1
            except:
                pass

        checks_performed.append("UIKit/SwiftUI detection")

        if uikit_imports > 0 or swiftui_imports > 0:
            self.passed_checks.append("iOS: UI Framework Detection")
            self.info.append(Issue(
                severity="info",
                message=f"iOS project using: UIKit ({uikit_imports} files), SwiftUI ({swiftui_imports} files)",
                category="ios"
            ))
        else:
            self.warnings.append(Issue(
                severity="warning",
                message="No UIKit or SwiftUI imports detected",
                category="ios",
                suggestion="Ensure iOS UI framework is properly imported"
            ))
            platform_issues.append(Issue(
                severity="warning",
                message="No UIKit or SwiftUI imports detected",
                category="ios"
            ))

        # Check for iOS deployment target
        checks_performed.append("Deployment target check")
        self._check_deployment_target("iOS", platform_issues)

        # Check for iOS-specific capabilities
        checks_performed.append("iOS capabilities check")
        self._check_ios_capabilities(platform_issues)

        # Check for App Icon
        checks_performed.append("App Icon presence")
        self._check_app_assets("iOS", platform_issues)

        # Determine platform status
        status = CheckpointStatus.FAILED if any(i.severity == "error" for i in platform_issues) else \
                 CheckpointStatus.WARNING if platform_issues else \
                 CheckpointStatus.PASSED

        return PlatformValidationResult(
            platform=Platform.IOS,
            status=status,
            checks_performed=checks_performed,
            issues=platform_issues
        )

    def _validate_macos(self) -> PlatformValidationResult:
        """macOS-specific validation."""
        checks_performed = []
        platform_issues = []

        # Check for AppKit usage
        swift_files = list(self.project_path.rglob("*.swift"))
        appkit_imports = 0
        swiftui_imports = 0

        for swift_file in swift_files:
            try:
                content = swift_file.read_text()
                if "import AppKit" in content or "import Cocoa" in content:
                    appkit_imports += 1
                if "import SwiftUI" in content:
                    swiftui_imports += 1
            except:
                pass

        checks_performed.append("AppKit/SwiftUI detection")

        if appkit_imports > 0 or swiftui_imports > 0:
            self.passed_checks.append("macOS: UI Framework Detection")
            self.info.append(Issue(
                severity="info",
                message=f"macOS project using: AppKit/Cocoa ({appkit_imports} files), SwiftUI ({swiftui_imports} files)",
                category="macos"
            ))
        else:
            self.warnings.append(Issue(
                severity="warning",
                message="No AppKit/Cocoa or SwiftUI imports detected",
                category="macos",
                suggestion="Ensure macOS UI framework is properly imported"
            ))
            platform_issues.append(Issue(
                severity="warning",
                message="No AppKit/Cocoa or SwiftUI imports detected",
                category="macos"
            ))

        # Check for macOS deployment target
        checks_performed.append("Deployment target check")
        self._check_deployment_target("macOS", platform_issues)

        # Check for macOS-specific entitlements
        checks_performed.append("Entitlements check")
        self._check_macos_entitlements(platform_issues)

        # Check for macOS app icon
        checks_performed.append("App Icon presence")
        self._check_app_assets("macOS", platform_issues)

        # Determine platform status
        status = CheckpointStatus.FAILED if any(i.severity == "error" for i in platform_issues) else \
                 CheckpointStatus.WARNING if platform_issues else \
                 CheckpointStatus.PASSED

        return PlatformValidationResult(
            platform=Platform.MACOS,
            status=status,
            checks_performed=checks_performed,
            issues=platform_issues
        )

    def _validate_ipados(self) -> PlatformValidationResult:
        """iPadOS-specific validation."""
        checks_performed = []
        platform_issues = []

        # iPadOS shares most characteristics with iOS
        # Check for iPad-specific features
        swift_files = list(self.project_path.rglob("*.swift"))

        # Check for multitasking/scene support
        scene_support = False
        for swift_file in swift_files:
            try:
                content = swift_file.read_text()
                if "UISceneConfiguration" in content or "UIWindowScene" in content:
                    scene_support = True
                    break
            except:
                pass

        checks_performed.append("Scene-based architecture check")

        if scene_support:
            self.passed_checks.append("iPadOS: Scene Support")
            self.info.append(Issue(
                severity="info",
                message="Project supports iPadOS scene-based architecture",
                category="ipados"
            ))
        else:
            self.info.append(Issue(
                severity="info",
                message="No explicit scene support detected (may be using traditional app delegate)",
                category="ipados"
            ))

        # Check for size class handling
        checks_performed.append("Size class handling")
        self._check_size_class_support(platform_issues)

        # Check for iPad-specific UI considerations
        checks_performed.append("iPad UI patterns")
        self._check_ipad_ui_patterns(platform_issues)

        # Determine platform status
        status = CheckpointStatus.FAILED if any(i.severity == "error" for i in platform_issues) else \
                 CheckpointStatus.WARNING if platform_issues else \
                 CheckpointStatus.PASSED

        return PlatformValidationResult(
            platform=Platform.IPADOS,
            status=status,
            checks_performed=checks_performed,
            issues=platform_issues
        )

    def _validate_tvos(self) -> PlatformValidationResult:
        """tvOS-specific validation."""
        checks_performed = []
        platform_issues = []

        # Check for TVUIKit usage
        swift_files = list(self.project_path.rglob("*.swift"))
        tvuikit_imports = 0

        for swift_file in swift_files:
            try:
                content = swift_file.read_text()
                if "import TVUIKit" in content:
                    tvuikit_imports += 1
            except:
                pass

        checks_performed.append("tvOS framework detection")

        if tvuikit_imports > 0:
            self.passed_checks.append("tvOS: Framework Detection")
            self.info.append(Issue(
                severity="info",
                message=f"tvOS project detected with TVUIKit usage",
                category="tvos"
            ))

        return PlatformValidationResult(
            platform=Platform.TVOS,
            status=CheckpointStatus.PASSED,
            checks_performed=checks_performed,
            issues=platform_issues
        )

    def _validate_watchos(self) -> PlatformValidationResult:
        """watchOS-specific validation."""
        checks_performed = []
        platform_issues = []

        # Check for WatchKit usage
        swift_files = list(self.project_path.rglob("*.swift"))
        watchkit_imports = 0

        for swift_file in swift_files:
            try:
                content = swift_file.read_text()
                if "import WatchKit" in content:
                    watchkit_imports += 1
            except:
                pass

        checks_performed.append("watchOS framework detection")

        if watchkit_imports > 0:
            self.passed_checks.append("watchOS: Framework Detection")
            self.info.append(Issue(
                severity="info",
                message=f"watchOS project detected with WatchKit usage",
                category="watchos"
            ))

        return PlatformValidationResult(
            platform=Platform.WATCHOS,
            status=CheckpointStatus.PASSED,
            checks_performed=checks_performed,
            issues=platform_issues
        )

    def _check_deployment_target(self, platform_name: str, issues: List[Issue]):
        """Check deployment target in project files."""
        # Look for deployment target in Package.swift
        package_swift = self.project_path / "Package.swift"
        if package_swift.exists():
            try:
                content = package_swift.read_text()
                if "platforms:" in content:
                    self.passed_checks.append(f"{platform_name}: Deployment Target Specified")
                else:
                    self.info.append(Issue(
                        severity="info",
                        message=f"{platform_name} deployment target not explicitly specified",
                        category=platform_name.lower()
                    ))
            except:
                pass

    def _check_ios_capabilities(self, issues: List[Issue]):
        """Check for iOS-specific capabilities."""
        # Look for entitlements file
        entitlements = list(self.project_path.rglob("*.entitlements"))
        if entitlements:
            self.passed_checks.append("iOS: Entitlements Configuration")
            self.info.append(Issue(
                severity="info",
                message=f"Found {len(entitlements)} entitlements file(s)",
                category="ios"
            ))

    def _check_macos_entitlements(self, issues: List[Issue]):
        """Check macOS entitlements."""
        entitlements = list(self.project_path.rglob("*.entitlements"))

        for ent_file in entitlements:
            try:
                content = ent_file.read_text()

                # Check for sandboxing
                if "com.apple.security.app-sandbox" in content:
                    self.passed_checks.append("macOS: App Sandbox Enabled")
                else:
                    self.warnings.append(Issue(
                        severity="warning",
                        message="macOS app may not be sandboxed",
                        file_path=str(ent_file),
                        category="macos",
                        suggestion="Consider enabling App Sandbox for distribution"
                    ))
            except:
                pass

    def _check_app_assets(self, platform_name: str, issues: List[Issue]):
        """Check for app icon and assets."""
        asset_catalogs = list(self.project_path.rglob("*.xcassets"))

        if asset_catalogs:
            self.passed_checks.append(f"{platform_name}: Asset Catalog Present")

            # Check for AppIcon
            for catalog in asset_catalogs:
                appicon_dir = catalog / "AppIcon.appiconset"
                if appicon_dir.exists():
                    self.passed_checks.append(f"{platform_name}: App Icon Configured")
                    break
        else:
            self.warnings.append(Issue(
                severity="warning",
                message=f"No asset catalog (.xcassets) found for {platform_name}",
                category=platform_name.lower(),
                suggestion="Add an asset catalog with app icons"
            ))

    def _check_size_class_support(self, issues: List[Issue]):
        """Check for size class handling (important for iPad)."""
        swift_files = list(self.project_path.rglob("*.swift"))

        size_class_usage = False
        for swift_file in swift_files[:20]:
            try:
                content = swift_file.read_text()
                if "traitCollection" in content or "UIUserInterfaceSizeClass" in content:
                    size_class_usage = True
                    break
            except:
                pass

        if size_class_usage:
            self.passed_checks.append("iPadOS: Size Class Handling")
        else:
            self.info.append(Issue(
                severity="info",
                message="No explicit size class handling detected",
                category="ipados",
                suggestion="Consider handling different size classes for better iPad experience"
            ))

    def _check_ipad_ui_patterns(self, issues: List[Issue]):
        """Check for iPad-specific UI patterns."""
        swift_files = list(self.project_path.rglob("*.swift"))

        split_view = False
        for swift_file in swift_files[:20]:
            try:
                content = swift_file.read_text()
                if "UISplitViewController" in content or "splitView" in content:
                    split_view = True
                    break
            except:
                pass

        if split_view:
            self.passed_checks.append("iPadOS: Split View Support")
            self.info.append(Issue(
                severity="info",
                message="Project includes split view support",
                category="ipados"
            ))

    def _determine_status(self) -> CheckpointStatus:
        """Determine overall checkpoint status."""
        # Check if any platform failed
        if any(r.status == CheckpointStatus.FAILED for r in self.platform_results):
            return CheckpointStatus.FAILED

        # Check if any platform has warnings
        if any(r.status == CheckpointStatus.WARNING for r in self.platform_results):
            return CheckpointStatus.WARNING

        # All platforms passed
        if all(r.status == CheckpointStatus.PASSED for r in self.platform_results):
            return CheckpointStatus.PASSED

        return CheckpointStatus.PENDING

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []

        failed_platforms = [r.platform.value for r in self.platform_results if r.status == CheckpointStatus.FAILED]
        if failed_platforms:
            recommendations.append(f"Fix critical issues in: {', '.join(failed_platforms)}")

        warning_platforms = [r.platform.value for r in self.platform_results if r.status == CheckpointStatus.WARNING]
        if warning_platforms:
            recommendations.append(f"Review warnings for: {', '.join(warning_platforms)}")

        if len(self.platforms) > 1:
            recommendations.append("Proceed to integration testing to ensure cross-platform compatibility")

        return recommendations
