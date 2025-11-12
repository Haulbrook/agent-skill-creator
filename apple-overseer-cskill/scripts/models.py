"""
Data models for Apple Overseer checkpoint system.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class CheckpointStatus(Enum):
    """Status of a checkpoint validation."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    PENDING = "PENDING"
    SKIPPED = "SKIPPED"


class CheckpointLevel(Enum):
    """Multi-level checkpoint hierarchy."""
    FOUNDATION = 1
    PLATFORM_SPECIFIC = 2
    INTEGRATION = 3
    EXECUTIVE = 4


class Platform(Enum):
    """Supported Apple platforms."""
    IOS = "iOS"
    MACOS = "macOS"
    IPADOS = "iPadOS"
    TVOS = "tvOS"
    WATCHOS = "watchOS"


@dataclass
class Issue:
    """Represents a single validation issue."""
    severity: str  # "error", "warning", "info"
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    category: str = "general"


@dataclass
class CheckpointReport:
    """Report from a single checkpoint validation."""
    level: CheckpointLevel
    checkpoint_name: str
    status: CheckpointStatus
    timestamp: str
    duration_seconds: float

    issues: List[Issue] = field(default_factory=list)
    warnings: List[Issue] = field(default_factory=list)
    info: List[Issue] = field(default_factory=list)

    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    skipped_checks: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if checkpoint has any errors."""
        return len(self.issues) > 0 or self.status == CheckpointStatus.FAILED

    @property
    def can_proceed(self) -> bool:
        """Check if can proceed to next checkpoint."""
        return self.status in [CheckpointStatus.PASSED, CheckpointStatus.WARNING]

    @property
    def total_checks(self) -> int:
        """Total number of checks performed."""
        return len(self.passed_checks) + len(self.failed_checks) + len(self.skipped_checks)

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_checks == 0:
            return 0.0
        return (len(self.passed_checks) / self.total_checks) * 100


@dataclass
class PlatformValidationResult:
    """Result of platform-specific validation."""
    platform: Platform
    status: CheckpointStatus
    checks_performed: List[str]
    issues: List[Issue]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OverseerReport:
    """Complete overseer validation report."""
    project_path: str
    platforms: List[Platform]
    start_time: str
    end_time: str
    total_duration_seconds: float

    checkpoint_reports: List[CheckpointReport] = field(default_factory=list)

    final_status: CheckpointStatus = CheckpointStatus.PENDING
    stamp_of_approval: bool = False

    summary: Dict[str, Any] = field(default_factory=dict)

    @property
    def all_passed(self) -> bool:
        """Check if all checkpoints passed."""
        return all(report.can_proceed for report in self.checkpoint_reports)

    @property
    def highest_level_reached(self) -> CheckpointLevel:
        """Get the highest checkpoint level reached."""
        if not self.checkpoint_reports:
            return CheckpointLevel.FOUNDATION
        return max(report.level for report in self.checkpoint_reports)

    @property
    def total_issues(self) -> int:
        """Total issues across all checkpoints."""
        return sum(len(report.issues) for report in self.checkpoint_reports)

    @property
    def total_warnings(self) -> int:
        """Total warnings across all checkpoints."""
        return sum(len(report.warnings) for report in self.checkpoint_reports)

    def get_checkpoint_by_level(self, level: CheckpointLevel) -> Optional[CheckpointReport]:
        """Get checkpoint report by level."""
        for report in self.checkpoint_reports:
            if report.level == level:
                return report
        return None

    def generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary."""
        return {
            "total_checkpoints": len(self.checkpoint_reports),
            "passed_checkpoints": sum(1 for r in self.checkpoint_reports if r.status == CheckpointStatus.PASSED),
            "failed_checkpoints": sum(1 for r in self.checkpoint_reports if r.status == CheckpointStatus.FAILED),
            "total_issues": self.total_issues,
            "total_warnings": self.total_warnings,
            "stamp_of_approval": self.stamp_of_approval,
            "final_status": self.final_status.value,
            "highest_level_reached": self.highest_level_reached.value,
            "platforms_validated": [p.value for p in self.platforms]
        }
