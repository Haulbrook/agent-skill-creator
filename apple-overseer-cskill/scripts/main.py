"""
Apple Overseer - Main Orchestrator

Coordinates multi-level quality control checkpoints for Apple platform projects.
"""
import sys
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .models import (
    OverseerReport, CheckpointReport, CheckpointStatus,
    Platform, CheckpointLevel
)
from .checkpoints import (
    FoundationInspector,
    PlatformOverseer,
    IntegrationCoordinator,
    ExecutiveOverseer
)


class AppleOverseer:
    """
    Apple Overseer - Multi-Level Quality Control System

    Like a multi-story building with floor managers, this system validates
    Apple platform projects through progressive checkpoints:

    Level 1: Foundation Inspector - Code structure, syntax, dependencies
    Level 2: Platform Overseers - iOS, macOS, iPadOS specific validation
    Level 3: Integration Coordinator - Cross-platform compatibility
    Level 4: Executive Overseer - Final QA and approval stamp

    Each level must pass (or have acceptable warnings) before proceeding to the next.
    """

    def __init__(self, project_path: str, platforms: Optional[List[str]] = None):
        """
        Initialize Apple Overseer.

        Args:
            project_path: Path to the Apple platform project
            platforms: List of platforms to validate (default: detect from project)
        """
        self.project_path = Path(project_path)

        # Parse platforms
        if platforms:
            self.platforms = self._parse_platforms(platforms)
        else:
            self.platforms = self._detect_platforms()

        self.checkpoint_reports: List[CheckpointReport] = []

    def run_validation(self, start_level: int = 1, stop_level: int = 4) -> OverseerReport:
        """
        Run the multi-level validation process.

        Args:
            start_level: Checkpoint level to start from (1-4)
            stop_level: Checkpoint level to stop at (1-4)

        Returns:
            OverseerReport with complete validation results
        """
        start_time = datetime.now()

        print("=" * 70)
        print("🏢 APPLE OVERSEER - MULTI-LEVEL QUALITY CONTROL")
        print("=" * 70)
        print(f"📁 Project: {self.project_path}")
        print(f"🎯 Platforms: {', '.join(p.value for p in self.platforms)}")
        print(f"📊 Checkpoints: Level {start_level} → Level {stop_level}")
        print("=" * 70)
        print()

        # Level 1: Foundation Inspector
        if start_level <= 1 <= stop_level:
            foundation_report = self._run_foundation_checkpoint()
            self.checkpoint_reports.append(foundation_report)

            if not foundation_report.can_proceed:
                print("\n❌ Foundation checkpoint failed. Cannot proceed to next level.")
                return self._generate_final_report(start_time)

        # Level 2: Platform-Specific Overseers
        if start_level <= 2 <= stop_level:
            platform_report = self._run_platform_checkpoint()
            self.checkpoint_reports.append(platform_report)

            if not platform_report.can_proceed:
                print("\n❌ Platform checkpoint failed. Cannot proceed to next level.")
                return self._generate_final_report(start_time)

        # Level 3: Integration Coordinator
        if start_level <= 3 <= stop_level:
            integration_report = self._run_integration_checkpoint()
            self.checkpoint_reports.append(integration_report)

            if not integration_report.can_proceed:
                print("\n❌ Integration checkpoint failed. Cannot proceed to next level.")
                return self._generate_final_report(start_time)

        # Level 4: Executive Overseer
        if start_level <= 4 <= stop_level:
            executive_report = self._run_executive_checkpoint()
            self.checkpoint_reports.append(executive_report)

        # Generate final report
        return self._generate_final_report(start_time)

    def _run_foundation_checkpoint(self) -> CheckpointReport:
        """Run Level 1: Foundation Inspector."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│ LEVEL 1: FOUNDATION INSPECTOR                                   │")
        print("│ Validating code structure, syntax, and dependencies            │")
        print("└─────────────────────────────────────────────────────────────────┘")

        inspector = FoundationInspector(str(self.project_path))
        report = inspector.validate()

        self._print_checkpoint_results(report)
        return report

    def _run_platform_checkpoint(self) -> CheckpointReport:
        """Run Level 2: Platform-Specific Overseers."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│ LEVEL 2: PLATFORM-SPECIFIC OVERSEERS                           │")
        print("│ Validating platform requirements and APIs                      │")
        print("└─────────────────────────────────────────────────────────────────┘")

        overseer = PlatformOverseer(str(self.project_path), self.platforms)
        report = overseer.validate()

        self._print_checkpoint_results(report)
        return report

    def _run_integration_checkpoint(self) -> CheckpointReport:
        """Run Level 3: Integration Coordinator."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│ LEVEL 3: INTEGRATION COORDINATOR                                │")
        print("│ Validating cross-platform compatibility                         │")
        print("└─────────────────────────────────────────────────────────────────┘")

        coordinator = IntegrationCoordinator(str(self.project_path), self.platforms)
        report = coordinator.validate()

        self._print_checkpoint_results(report)
        return report

    def _run_executive_checkpoint(self) -> CheckpointReport:
        """Run Level 4: Executive Overseer."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│ LEVEL 4: EXECUTIVE OVERSEER                                     │")
        print("│ Final quality assurance and approval                            │")
        print("└─────────────────────────────────────────────────────────────────┘")

        overseer = ExecutiveOverseer(
            str(self.project_path),
            self.platforms,
            self.checkpoint_reports
        )
        report = overseer.validate()

        self._print_checkpoint_results(report)

        # Display stamp of approval
        if report.metadata.get("stamp_of_approval"):
            print("\n" + "=" * 70)
            print("🎉 STAMP OF APPROVAL GRANTED 🎉")
            print("=" * 70)
            print("All quality checkpoints passed successfully!")
            print("Project is ready for deployment/distribution.")
            print("=" * 70)

        return report

    def _print_checkpoint_results(self, report: CheckpointReport):
        """Print checkpoint results in a formatted way."""
        status_symbol = {
            CheckpointStatus.PASSED: "✅",
            CheckpointStatus.WARNING: "⚠️",
            CheckpointStatus.FAILED: "❌",
            CheckpointStatus.PENDING: "⏳",
            CheckpointStatus.SKIPPED: "⏭️"
        }

        print(f"\n{status_symbol.get(report.status, '❓')} Status: {report.status.value}")
        print(f"⏱️  Duration: {report.duration_seconds:.2f}s")
        print(f"✓  Passed: {len(report.passed_checks)}")
        print(f"✗  Failed: {len(report.failed_checks)}")
        print(f"⚠  Warnings: {len(report.warnings)}")
        print(f"🔴 Issues: {len(report.issues)}")

        if report.success_rate > 0:
            print(f"📊 Success Rate: {report.success_rate:.1f}%")

        # Print issues
        if report.issues:
            print("\n🔴 Critical Issues:")
            for issue in report.issues[:5]:  # Show first 5
                print(f"   • {issue.message}")
                if issue.file_path:
                    print(f"     File: {issue.file_path}")
                if issue.suggestion:
                    print(f"     💡 {issue.suggestion}")

        # Print warnings
        if report.warnings and len(report.warnings) <= 3:
            print("\n⚠️  Warnings:")
            for warning in report.warnings:
                print(f"   • {warning.message}")

        # Print recommendations
        if report.recommendations:
            print("\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"   • {rec}")

    def _generate_final_report(self, start_time: datetime) -> OverseerReport:
        """Generate final overseer report."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Determine final status
        if all(r.status == CheckpointStatus.PASSED for r in self.checkpoint_reports):
            final_status = CheckpointStatus.PASSED
            stamp_of_approval = True
        elif any(r.status == CheckpointStatus.FAILED for r in self.checkpoint_reports):
            final_status = CheckpointStatus.FAILED
            stamp_of_approval = False
        elif any(r.status == CheckpointStatus.WARNING for r in self.checkpoint_reports):
            final_status = CheckpointStatus.WARNING
            stamp_of_approval = False
        else:
            final_status = CheckpointStatus.PENDING
            stamp_of_approval = False

        # Check executive approval
        executive_report = next(
            (r for r in self.checkpoint_reports if r.level == CheckpointLevel.EXECUTIVE),
            None
        )
        if executive_report:
            stamp_of_approval = executive_report.metadata.get("stamp_of_approval", False)

        report = OverseerReport(
            project_path=str(self.project_path),
            platforms=self.platforms,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_duration_seconds=duration,
            checkpoint_reports=self.checkpoint_reports,
            final_status=final_status,
            stamp_of_approval=stamp_of_approval
        )

        report.summary = report.generate_summary()

        # Print final summary
        self._print_final_summary(report)

        return report

    def _print_final_summary(self, report: OverseerReport):
        """Print final validation summary."""
        print("\n")
        print("=" * 70)
        print("📋 FINAL VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Project: {report.project_path}")
        print(f"Platforms: {', '.join(p.value for p in report.platforms)}")
        print(f"Duration: {report.total_duration_seconds:.2f}s")
        print()
        print(f"Checkpoints Completed: {report.summary['total_checkpoints']}")
        print(f"✅ Passed: {report.summary['passed_checkpoints']}")
        print(f"❌ Failed: {report.summary['failed_checkpoints']}")
        print(f"🔴 Total Issues: {report.summary['total_issues']}")
        print(f"⚠️  Total Warnings: {report.summary['total_warnings']}")
        print()
        print(f"Final Status: {report.final_status.value}")

        if report.stamp_of_approval:
            print("\n🎖️  STAMP OF APPROVAL: ✅ GRANTED")
        else:
            print("\n🎖️  STAMP OF APPROVAL: ❌ NOT GRANTED")

        print("=" * 70)

    def _parse_platforms(self, platform_list: List[str]) -> List[Platform]:
        """Parse platform strings to Platform enums."""
        platforms = []
        platform_map = {
            "ios": Platform.IOS,
            "macos": Platform.MACOS,
            "ipados": Platform.IPADOS,
            "tvos": Platform.TVOS,
            "watchos": Platform.WATCHOS
        }

        for p in platform_list:
            platform = platform_map.get(p.lower())
            if platform:
                platforms.append(platform)
            else:
                print(f"⚠️  Unknown platform: {p}")

        return platforms if platforms else [Platform.IOS]  # Default to iOS

    def _detect_platforms(self) -> List[Platform]:
        """Auto-detect platforms from project."""
        platforms = []

        # Look for platform indicators in project files
        swift_files = list(self.project_path.rglob("*.swift"))

        has_uikit = False
        has_appkit = False
        has_watchkit = False

        for swift_file in swift_files[:50]:  # Check first 50 files
            try:
                content = swift_file.read_text()
                if "import UIKit" in content:
                    has_uikit = True
                if "import AppKit" in content or "import Cocoa" in content:
                    has_appkit = True
                if "import WatchKit" in content:
                    has_watchkit = True
            except:
                pass

        # Determine platforms
        if has_uikit:
            platforms.append(Platform.IOS)
            # iOS includes iPadOS
            platforms.append(Platform.IPADOS)
        if has_appkit:
            platforms.append(Platform.MACOS)
        if has_watchkit:
            platforms.append(Platform.WATCHOS)

        # Default to iOS if nothing detected
        if not platforms:
            print("⚠️  Could not detect platforms, defaulting to iOS")
            platforms.append(Platform.IOS)

        return platforms

    def export_report(self, report: OverseerReport, output_path: str):
        """Export report to JSON file."""
        report_data = {
            "project_path": report.project_path,
            "platforms": [p.value for p in report.platforms],
            "start_time": report.start_time,
            "end_time": report.end_time,
            "total_duration_seconds": report.total_duration_seconds,
            "final_status": report.final_status.value,
            "stamp_of_approval": report.stamp_of_approval,
            "summary": report.summary,
            "checkpoints": [
                {
                    "level": r.level.value,
                    "name": r.checkpoint_name,
                    "status": r.status.value,
                    "duration": r.duration_seconds,
                    "passed_checks": len(r.passed_checks),
                    "failed_checks": len(r.failed_checks),
                    "issues": len(r.issues),
                    "warnings": len(r.warnings)
                }
                for r in report.checkpoint_reports
            ]
        }

        output_file = Path(output_path)
        output_file.write_text(json.dumps(report_data, indent=2))
        print(f"\n📄 Report exported to: {output_path}")


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Apple Overseer - Multi-Level Quality Control for Apple Platform Projects"
    )
    parser.add_argument("project_path", help="Path to Apple platform project")
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["ios", "macos", "ipados", "tvos", "watchos"],
        help="Platforms to validate (default: auto-detect)"
    )
    parser.add_argument(
        "--start-level",
        type=int,
        default=1,
        choices=[1, 2, 3, 4],
        help="Checkpoint level to start from (default: 1)"
    )
    parser.add_argument(
        "--stop-level",
        type=int,
        default=4,
        choices=[1, 2, 3, 4],
        help="Checkpoint level to stop at (default: 4)"
    )
    parser.add_argument(
        "--export",
        help="Export report to JSON file"
    )

    args = parser.parse_args()

    # Run validation
    overseer = AppleOverseer(args.project_path, args.platforms)
    report = overseer.run_validation(args.start_level, args.stop_level)

    # Export if requested
    if args.export:
        overseer.export_report(report, args.export)

    # Exit with appropriate code
    if report.stamp_of_approval:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
