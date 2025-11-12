---
name: apple-overseer
description: Multi-level quality control checkpoint system for Apple platform development (iOS, macOS, iPadOS)
version: 1.0.0
type: Simple Skill
domain: Apple Platform Quality Assurance
---

# Apple Overseer Skill - Technical Specification

**Version:** 1.0.0
**Type:** Simple Skill
**Domain:** Apple Platform Quality Assurance and Validation
**Created:** 2025-11-12
**Author:** Apple Overseer Team

## Table of Contents

1. [Overview](#overview)
2. [Core Concept: The Building Metaphor](#core-concept-the-building-metaphor)
3. [Architecture](#architecture)
4. [Checkpoint Levels](#checkpoint-levels)
5. [Detailed Component Specifications](#detailed-component-specifications)
6. [Validation Pipeline](#validation-pipeline)
7. [Platform Support](#platform-support)
8. [Usage Guide](#usage-guide)
9. [Quality Standards](#quality-standards)
10. [Integration Points](#integration-points)
11. [Error Handling & Recovery](#error-handling--recovery)
12. [Extension Points](#extension-points)
13. [Testing Strategy](#testing-strategy)
14. [Deployment & Installation](#deployment--installation)

---

## Overview

### Purpose

The Apple Overseer skill is a comprehensive, multi-level quality control checkpoint system designed specifically for Apple platform development. It provides systematic validation of iOS, macOS, iPadOS, tvOS, and watchOS projects through progressive quality gates, ensuring code quality, platform compliance, and cross-platform compatibility.

### Problem Statement

Developing applications for Apple platforms presents unique challenges:

1. **Multiple Platform Requirements**: Each Apple platform (iOS, macOS, iPadOS, tvOS, watchOS) has specific requirements, APIs, and best practices
2. **Cross-Platform Complexity**: Applications targeting multiple platforms must maintain consistency while respecting platform differences
3. **Quality Assurance Gaps**: Traditional testing may miss platform-specific issues, configuration problems, or integration challenges
4. **App Store Compliance**: Applications must meet Apple's strict guidelines for submission and distribution
5. **Manual Review Overhead**: Manual quality checks are time-consuming, error-prone, and inconsistent

### Solution

The Apple Overseer skill implements a multi-level checkpoint system inspired by a multi-story building with dedicated floor managers. Each level validates specific aspects of the project before allowing progression to the next level, ensuring comprehensive quality control:

**Level 1: Foundation Inspector** - Validates code structure, syntax, and dependencies
**Level 2: Platform-Specific Overseers** - Validates platform requirements and APIs
**Level 3: Integration Coordinator** - Validates cross-platform compatibility
**Level 4: Executive Overseer** - Final QA and stamp of approval

Only when all checkpoints pass does the project receive the final "Stamp of Approval," indicating readiness for deployment or App Store submission.

### Key Features

- **Progressive Validation**: Multi-level checkpoint system ensures thorough quality control
- **Platform Intelligence**: Automatically detects target platforms and validates platform-specific requirements
- **Cross-Platform Analysis**: Validates consistency and compatibility across iOS, macOS, iPadOS, and other Apple platforms
- **Comprehensive Reporting**: Detailed reports at each checkpoint with actionable recommendations
- **Approval Workflow**: Clear pass/fail criteria with final stamp of approval
- **Extensible Architecture**: Easy to add new checkpoints or customize validation rules
- **Developer-Friendly**: Clear, actionable feedback with specific file locations and suggestions

---

## Core Concept: The Building Metaphor

### The Multi-Story Building Analogy

The Apple Overseer skill is structured like a multi-story building under construction, where each floor has a dedicated floor manager responsible for quality control at that specific stage:

```
┌─────────────────────────────────────────────────────────┐
│  🎖️  EXECUTIVE OVERSEER (Level 4)                      │
│  Final QA, Stamp of Approval                            │
│  ✓ Performance ✓ Security ✓ UX/UI ✓ App Store Ready   │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │ Pass
                         │
┌─────────────────────────────────────────────────────────┐
│  🔗  INTEGRATION COORDINATOR (Level 3)                  │
│  Cross-Platform Validation                              │
│  ✓ Shared Code ✓ Platform APIs ✓ Consistency          │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │ Pass
                         │
┌─────────────────────────────────────────────────────────┐
│  📱  PLATFORM OVERSEERS (Level 2)                       │
│  iOS Overseer | macOS Overseer | iPadOS Overseer        │
│  ✓ Platform Requirements ✓ APIs ✓ Capabilities         │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │ Pass
                         │
┌─────────────────────────────────────────────────────────┐
│  🏗️  FOUNDATION INSPECTOR (Level 1)                    │
│  Ground Floor - Basic Quality Control                   │
│  ✓ Structure ✓ Syntax ✓ Dependencies ✓ Configuration  │
└─────────────────────────────────────────────────────────┘
```

### Workflow Progression

1. **Entry Point**: Project enters at the Foundation level
2. **Checkpoint Validation**: Each level performs its specific checks
3. **Pass/Fail Decision**: Must pass (or have acceptable warnings) to proceed
4. **Progressive Advancement**: Successfully validated projects move to the next level
5. **Final Approval**: Top-level executive overseer grants stamp of approval
6. **Rejection Handling**: Failures at any level prevent progression and provide detailed feedback

This approach ensures that fundamental issues are caught early (at the foundation) before investing time in higher-level validations, while comprehensive issues are only addressed when the basics are solid.

---

## Architecture

### System Architecture

```
AppleOverseer (Main Orchestrator)
    │
    ├── Models (Data Structures)
    │   ├── CheckpointReport
    │   ├── OverseerReport
    │   ├── Issue
    │   ├── Platform
    │   └── CheckpointStatus
    │
    ├── Checkpoints (Validation Modules)
    │   ├── FoundationInspector (Level 1)
    │   ├── PlatformOverseer (Level 2)
    │   │   ├── iOS Validator
    │   │   ├── macOS Validator
    │   │   ├── iPadOS Validator
    │   │   ├── tvOS Validator
    │   │   └── watchOS Validator
    │   ├── IntegrationCoordinator (Level 3)
    │   └── ExecutiveOverseer (Level 4)
    │
    └── Reporting
        ├── Console Output (formatted)
        └── JSON Export
```

### Design Principles

1. **Separation of Concerns**: Each checkpoint level is independent and focused
2. **Progressive Validation**: Build complexity incrementally
3. **Fail-Fast Philosophy**: Catch fundamental issues early
4. **Actionable Feedback**: Every issue includes suggestions for resolution
5. **Platform Awareness**: Understand and respect platform differences
6. **Extensibility**: Easy to add new checkpoints or validators

### Technology Stack

- **Language**: Python 3.8+
- **Architecture Pattern**: Orchestrator + Modular Validators
- **Data Models**: Dataclasses for type safety and clarity
- **Reporting**: Structured console output + JSON export

---

## Checkpoint Levels

### Level 1: Foundation Inspector

**Role**: Ground Floor Manager - Basic Quality Control

The Foundation Inspector is the first checkpoint and validates the fundamental aspects of the project that are common across all platforms.

**Responsibilities**:

1. **Project Structure Validation**
   - Verify project directory exists and is accessible
   - Detect Xcode projects (.xcodeproj)
   - Detect Xcode workspaces (.xcworkspace)
   - Detect Swift Package Manager projects (Package.swift)

2. **Build Configuration**
   - Validate CocoaPods configuration (Podfile, Podfile.lock)
   - Validate Carthage configuration (Cartfile)
   - Validate Swift Package Manager dependencies
   - Check dependency version constraints

3. **Swift Code Quality**
   - Basic syntax validation
   - Detect excessive force unwrapping (safety concern)
   - Identify debug print statements in production code
   - Count Swift files and provide metrics

4. **Dependency Analysis**
   - Verify dependency declarations
   - Check for version pinning and constraints
   - Count and report package dependencies

5. **Configuration Files**
   - Validate Info.plist files
   - Check for required configuration keys
   - Verify bundle identifiers

6. **Code Organization**
   - Detect common organizational patterns (MVC, MVVM)
   - Identify structured directories (Models, Views, Controllers)
   - Report on project organization quality

**Pass Criteria**:
- Project structure is valid
- Build configuration is present and valid
- No critical syntax errors
- Dependencies are properly declared

**Failure Scenarios**:
- Project path does not exist
- No valid Xcode project or Swift Package found
- Critical build configuration errors
- Severe code quality issues

### Level 2: Platform-Specific Overseers

**Role**: Platform Floor Managers - Platform Requirements Validation

Each platform overseer validates platform-specific requirements, APIs, and best practices for its respective platform.

#### iOS Overseer

**Responsibilities**:

1. **Framework Detection**
   - Verify UIKit or SwiftUI usage
   - Count framework imports across project
   - Report UI framework distribution

2. **Deployment Target**
   - Check iOS deployment target specification
   - Verify target version compatibility

3. **iOS Capabilities**
   - Check for entitlements configuration
   - Validate capability declarations

4. **Assets**
   - Verify asset catalog presence
   - Check for app icon configuration
   - Validate asset organization

**iOS-Specific Validations**:
- UIKit/SwiftUI proper usage
- iOS SDK API compatibility
- App lifecycle implementation
- iOS Human Interface Guidelines compliance

#### macOS Overseer

**Responsibilities**:

1. **Framework Detection**
   - Verify AppKit/Cocoa or SwiftUI usage
   - Validate macOS-specific frameworks

2. **Deployment Target**
   - Check macOS deployment target
   - Verify version compatibility

3. **Sandboxing**
   - Check for App Sandbox entitlement
   - Validate sandbox permissions
   - Review entitlements configuration

4. **Assets**
   - Verify macOS app icon
   - Check asset catalog organization

**macOS-Specific Validations**:
- AppKit/Cocoa proper usage
- macOS SDK API compatibility
- Menu bar and window management
- Sandboxing compliance for distribution

#### iPadOS Overseer

**Responsibilities**:

1. **Scene Architecture**
   - Check for UISceneConfiguration
   - Validate multi-window support
   - Verify scene-based architecture

2. **Size Class Handling**
   - Check for trait collection usage
   - Validate adaptive layouts
   - Verify size class responsiveness

3. **iPad UI Patterns**
   - Check for split view controller usage
   - Validate iPad-specific UI patterns
   - Verify multitasking support

**iPadOS-Specific Validations**:
- Scene-based architecture support
- Size class adaptivity
- iPad-specific UI components
- Multitasking capabilities

#### tvOS Overseer

**Responsibilities**:
- TVUIKit framework usage
- Focus-based navigation
- Apple TV remote support
- tvOS-specific UI patterns

#### watchOS Overseer

**Responsibilities**:
- WatchKit framework usage
- Complication support
- Watch-specific UI constraints
- Health and fitness integration

**Platform Overseer Pass Criteria**:
- Platform frameworks properly imported and used
- Platform-specific requirements met
- Assets and configurations valid
- No platform API misuse

### Level 3: Integration Coordinator

**Role**: Integration Floor Manager - Cross-Platform Compatibility

The Integration Coordinator validates that multi-platform projects maintain consistency and proper isolation between platforms.

**Responsibilities**:

1. **Conditional Compilation**
   - Detect platform-specific compilation directives (#if os(iOS), etc.)
   - Verify proper #if/#endif matching
   - Check for platform isolation patterns

2. **Shared Code Architecture**
   - Identify shared code directories (Shared, Common, Core)
   - Validate shared code organization
   - Check for proper code reuse patterns

3. **Platform API Isolation**
   - Detect mixed platform API usage
   - Verify conditional compilation for platform-specific code
   - Flag files mixing iOS/macOS APIs without guards

4. **Resource Sharing**
   - Validate asset catalog strategy
   - Check for localization consistency
   - Verify resource organization

5. **Architecture Consistency**
   - Detect architecture patterns (MVVM, MVC, VIPER)
   - Check for consistent patterns across platforms
   - Flag mixed architecture approaches

**Pass Criteria**:
- Platform-specific code is properly isolated
- Shared code is well-organized
- No platform API conflicts
- Consistent architecture patterns

**Note**: Single-platform projects automatically pass this level

### Level 4: Executive Overseer

**Role**: Top Floor Executive - Final Quality Assurance

The Executive Overseer performs final validation and determines whether the project receives the stamp of approval.

**Responsibilities**:

1. **Previous Checkpoint Review**
   - Verify all previous checkpoints passed
   - Aggregate issues and warnings
   - Ensure no blocking issues remain

2. **Performance Considerations**
   - Check for performance best practices
   - Identify large asset files
   - Validate resource optimization
   - Review memory management patterns

3. **Security Best Practices**
   - Detect potential hardcoded credentials
   - Check for HTTPS usage
   - Validate secure data storage patterns
   - Review App Transport Security compliance

4. **UX/UI Consistency**
   - Verify UI framework consistency
   - Check accessibility implementation
   - Validate cross-platform UI patterns
   - Review SwiftUI vs UIKit/AppKit usage

5. **App Store Readiness**
   - Check for privacy manifest (iOS 17+)
   - Verify documentation presence
   - Check for license files
   - Validate submission requirements

6. **Code Quality Metrics**
   - Calculate total lines of code
   - Determine average file size
   - Assess code distribution
   - Evaluate documentation coverage

7. **Stamp of Approval Decision**
   - All previous checkpoints must pass
   - No critical security issues
   - No critical performance issues
   - Reasonable code quality
   - Limited warnings (< 20 total)

**Pass Criteria**:
- All previous checkpoints passed
- No critical issues found
- Security best practices followed
- Reasonable code quality
- Total warnings acceptable (< 20)

**Stamp of Approval Granted When**:
- ✓ All checkpoints passed
- ✓ No blocking issues
- ✓ Security validated
- ✓ Performance acceptable
- ✓ Quality standards met

---

## Detailed Component Specifications

### Data Models

#### CheckpointStatus Enum

```python
class CheckpointStatus(Enum):
    PASSED = "PASSED"      # Checkpoint passed all checks
    FAILED = "FAILED"      # Checkpoint failed with errors
    WARNING = "WARNING"    # Checkpoint passed but has warnings
    PENDING = "PENDING"    # Checkpoint not yet run
    SKIPPED = "SKIPPED"    # Checkpoint skipped (e.g., single platform)
```

#### CheckpointLevel Enum

```python
class CheckpointLevel(Enum):
    FOUNDATION = 1          # Level 1: Foundation Inspector
    PLATFORM_SPECIFIC = 2   # Level 2: Platform Overseers
    INTEGRATION = 3         # Level 3: Integration Coordinator
    EXECUTIVE = 4           # Level 4: Executive Overseer
```

#### Platform Enum

```python
class Platform(Enum):
    IOS = "iOS"
    MACOS = "macOS"
    IPADOS = "iPadOS"
    TVOS = "tvOS"
    WATCHOS = "watchOS"
```

#### Issue Dataclass

```python
@dataclass
class Issue:
    severity: str           # "error", "warning", "info"
    message: str           # Human-readable issue description
    file_path: Optional[str]       # Affected file (if applicable)
    line_number: Optional[int]     # Line number (if applicable)
    suggestion: Optional[str]      # Actionable suggestion
    category: str          # Issue category for grouping
```

#### CheckpointReport Dataclass

```python
@dataclass
class CheckpointReport:
    level: CheckpointLevel
    checkpoint_name: str
    status: CheckpointStatus
    timestamp: str
    duration_seconds: float

    issues: List[Issue]            # Critical errors
    warnings: List[Issue]          # Warnings
    info: List[Issue]             # Informational messages

    passed_checks: List[str]       # Checks that passed
    failed_checks: List[str]       # Checks that failed
    skipped_checks: List[str]      # Checks that were skipped

    metadata: Dict[str, Any]       # Additional metadata
    recommendations: List[str]     # Actionable recommendations

    # Computed properties
    @property
    def has_errors(self) -> bool

    @property
    def can_proceed(self) -> bool

    @property
    def success_rate(self) -> float
```

#### OverseerReport Dataclass

```python
@dataclass
class OverseerReport:
    project_path: str
    platforms: List[Platform]
    start_time: str
    end_time: str
    total_duration_seconds: float

    checkpoint_reports: List[CheckpointReport]

    final_status: CheckpointStatus
    stamp_of_approval: bool

    summary: Dict[str, Any]

    # Computed properties
    @property
    def all_passed(self) -> bool

    @property
    def highest_level_reached(self) -> CheckpointLevel

    @property
    def total_issues(self) -> int

    def generate_summary(self) -> Dict[str, Any]
```

### Orchestrator: AppleOverseer

The main orchestrator coordinates the entire validation process.

**Key Methods**:

```python
class AppleOverseer:
    def __init__(self, project_path: str, platforms: Optional[List[str]] = None)

    def run_validation(self, start_level: int = 1, stop_level: int = 4) -> OverseerReport

    def _detect_platforms(self) -> List[Platform]

    def export_report(self, report: OverseerReport, output_path: str)
```

**Workflow**:

1. Initialize with project path and platforms
2. Auto-detect platforms if not specified
3. Run checkpoints sequentially (Level 1 → Level 4)
4. Stop at first failure (fail-fast)
5. Generate comprehensive final report
6. Optionally export report to JSON

---

## Validation Pipeline

### Sequential Validation Flow

```
┌─────────────────────────────────────────┐
│  Start Validation                        │
│  - Parse project path                    │
│  - Detect/parse platforms                │
│  - Initialize orchestrator               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Level 1: Foundation Inspector           │
│  - Validate project structure            │
│  - Check build configuration             │
│  - Analyze code quality                  │
│  - Verify dependencies                   │
└──────────────┬──────────────────────────┘
               │
               ├─► [FAILED] ──► Stop, Report Issues
               │
               ▼ [PASSED/WARNING]
┌─────────────────────────────────────────┐
│  Level 2: Platform Overseers             │
│  For each platform:                      │
│    - Validate platform frameworks        │
│    - Check platform requirements         │
│    - Verify platform-specific config     │
│    - Validate assets                     │
└──────────────┬──────────────────────────┘
               │
               ├─► [FAILED] ──► Stop, Report Issues
               │
               ▼ [PASSED/WARNING]
┌─────────────────────────────────────────┐
│  Level 3: Integration Coordinator        │
│  - Check conditional compilation         │
│  - Validate shared code architecture     │
│  - Verify platform API isolation         │
│  - Check resource sharing                │
└──────────────┬──────────────────────────┘
               │
               ├─► [FAILED] ──► Stop, Report Issues
               │
               ▼ [PASSED/WARNING]
┌─────────────────────────────────────────┐
│  Level 4: Executive Overseer             │
│  - Review previous checkpoints           │
│  - Validate performance considerations   │
│  - Check security practices              │
│  - Verify UX/UI consistency              │
│  - Assess App Store readiness            │
│  - Calculate code quality metrics        │
│  - DECISION: Grant/Deny Stamp            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Generate Final Report                   │
│  - Aggregate all checkpoint results      │
│  - Calculate summary statistics          │
│  - Determine final status                │
│  - Print formatted output                │
│  - Optionally export JSON                │
└──────────────┬──────────────────────────┘
               │
               ▼
        [STAMP OF APPROVAL]
        ✅ Granted / ❌ Denied
```

### Partial Validation

The system supports partial validation by specifying start and stop levels:

```python
# Run only foundation check
overseer.run_validation(start_level=1, stop_level=1)

# Run platform and integration only
overseer.run_validation(start_level=2, stop_level=3)

# Full validation (default)
overseer.run_validation(start_level=1, stop_level=4)
```

---

## Platform Support

### Supported Platforms

| Platform | Status | Primary Framework | Validation Focus |
|----------|--------|-------------------|------------------|
| **iOS** | Full Support | UIKit / SwiftUI | Mobile-specific APIs, UI patterns |
| **macOS** | Full Support | AppKit / SwiftUI | Desktop patterns, sandboxing |
| **iPadOS** | Full Support | UIKit / SwiftUI | Multitasking, size classes |
| **tvOS** | Basic Support | TVUIKit | Focus navigation, remote support |
| **watchOS** | Basic Support | WatchKit | Complications, health integration |

### Platform Detection

The system automatically detects target platforms by analyzing:

1. **Framework Imports**: UIKit → iOS/iPadOS, AppKit → macOS, etc.
2. **Project Configuration**: Xcode project settings, Package.swift platforms
3. **Conditional Compilation**: #if os(iOS), #if os(macOS) directives
4. **File Organization**: Platform-specific directories

Manual platform specification is also supported:

```python
overseer = AppleOverseer(
    project_path="./MyApp",
    platforms=["ios", "macos", "ipados"]
)
```

---

## Usage Guide

### Command-Line Interface

```bash
# Basic usage (auto-detect platforms)
python -m apple_overseer_cskill.scripts.main /path/to/project

# Specify platforms
python -m apple_overseer_cskill.scripts.main /path/to/project --platforms ios macos

# Partial validation
python -m apple_overseer_cskill.scripts.main /path/to/project --start-level 2 --stop-level 3

# Export report
python -m apple_overseer_cskill.scripts.main /path/to/project --export report.json
```

### Programmatic Usage

```python
from apple_overseer_cskill.scripts import AppleOverseer

# Create overseer instance
overseer = AppleOverseer(
    project_path="/path/to/MyApp",
    platforms=["ios", "ipados"]
)

# Run full validation
report = overseer.run_validation()

# Check results
if report.stamp_of_approval:
    print("✅ Project approved for deployment!")
else:
    print(f"❌ {report.total_issues} issues found")

# Export detailed report
overseer.export_report(report, "validation_report.json")
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Run Apple Overseer Validation
  run: |
    python -m apple_overseer_cskill.scripts.main ./MyApp --export report.json
  continue-on-error: false

- name: Upload Validation Report
  uses: actions/upload-artifact@v2
  with:
    name: overseer-report
    path: report.json
```

---

## Quality Standards

### Pass/Fail Criteria

#### Foundation Inspector
- **Pass**: Valid project structure, build configuration, dependencies
- **Fail**: Missing project files, invalid configuration, critical syntax errors

#### Platform Overseers
- **Pass**: Platform frameworks detected, requirements met, valid configuration
- **Fail**: Missing platform frameworks, invalid platform configuration

#### Integration Coordinator
- **Pass**: Proper platform isolation, shared code organized, no API conflicts
- **Fail**: Mixed platform APIs without guards, integration errors

#### Executive Overseer
- **Pass**: All checkpoints passed, security validated, quality acceptable
- **Fail**: Previous checkpoints failed, critical security/performance issues

### Warning Threshold

- **Acceptable**: < 20 total warnings across all checkpoints
- **Concerning**: 20-50 warnings (approval may still be granted)
- **Excessive**: > 50 warnings (approval unlikely)

### Stamp of Approval Requirements

All of the following must be true:

1. ✓ Foundation checkpoint passed
2. ✓ All platform checkpoints passed
3. ✓ Integration checkpoint passed
4. ✓ No critical security issues
5. ✓ No critical performance issues
6. ✓ Total warnings < 20
7. ✓ Code quality metrics acceptable

---

## Integration Points

### Xcode Integration

The skill analyzes Xcode projects and workspaces:
- `.xcodeproj` files
- `.xcworkspace` files
- Build configurations
- Project targets and schemes

### Swift Package Manager

Full support for Swift Package Manager projects:
- `Package.swift` validation
- Dependency analysis
- Platform declarations
- Version constraints

### CocoaPods

Validates CocoaPods configuration:
- `Podfile` syntax and dependencies
- `Podfile.lock` presence
- Version specifications

### Carthage

Basic Carthage support:
- `Cartfile` detection
- Dependency declarations

---

## Error Handling & Recovery

### Error Categories

1. **Critical Errors**: Block progression to next checkpoint
2. **Warnings**: Allow progression but require attention
3. **Info**: Informational messages for awareness

### Graceful Degradation

- If file cannot be read, skip and log warning
- If platform detection fails, default to iOS
- If checkpoint throws exception, report error and continue

### User Feedback

Every issue includes:
- **Severity**: error / warning / info
- **Message**: Clear description of the issue
- **File Path**: Exact location (when applicable)
- **Line Number**: Specific line (when applicable)
- **Suggestion**: Actionable fix recommendation
- **Category**: Issue category for grouping

Example:
```
⚠️ Warning: Excessive force unwrapping (12 instances)
   File: /path/to/MyViewController.swift
   💡 Suggestion: Consider using optional binding (if let, guard let) instead
```

---

## Extension Points

### Adding New Checkpoints

To add a new checkpoint level:

1. Create new checkpoint class inheriting base pattern
2. Implement `validate()` method returning `CheckpointReport`
3. Add to orchestrator's validation sequence
4. Update checkpoint level enum

### Custom Platform Validators

To add validation for a new platform:

1. Add platform to `Platform` enum
2. Create `_validate_<platform>()` method in `PlatformOverseer`
3. Define platform-specific checks
4. Return `PlatformValidationResult`

### Custom Validation Rules

Extend existing checkpoints by:

1. Adding new check methods to checkpoint classes
2. Calling from main `validate()` method
3. Updating pass/fail criteria

---

## Testing Strategy

### Unit Testing

Each checkpoint should have unit tests covering:
- Valid project scenarios
- Invalid project scenarios
- Edge cases (empty projects, missing files)
- Platform-specific validations

### Integration Testing

Test the full validation pipeline:
- Multi-platform projects
- Single platform projects
- Projects with various issues
- End-to-end approval workflow

### Test Projects

Maintain test projects representing:
- Valid iOS-only project
- Valid macOS-only project
- Valid multi-platform project
- Project with various common issues
- Project with security issues
- Project with performance issues

---

## Deployment & Installation

### Requirements

```
Python 3.8+
No external dependencies (uses standard library only)
```

### Installation

```bash
# Clone the skill
git clone <repository-url>

# Navigate to skill directory
cd apple-overseer-cskill

# Install (optional, for system-wide access)
pip install -e .
```

### Directory Structure

```
apple-overseer-cskill/
├── .claude-plugin/
│   └── marketplace.json          # Skill configuration
├── scripts/
│   ├── __init__.py
│   ├── main.py                   # Main orchestrator
│   ├── models.py                 # Data models
│   └── checkpoints/
│       ├── __init__.py
│       ├── foundation_inspector.py
│       ├── platform_overseers.py
│       ├── integration_coordinator.py
│       └── executive_overseer.py
├── assets/
│   └── examples/
│       └── sample_project_structure.md
├── SKILL.md                      # This file
├── README.md                     # User documentation
└── requirements.txt              # Python dependencies (none)
```

---

## Advanced Features

### Checkpoint Resumption

Resume validation from a specific level:

```python
# Skip foundation, start from platform validation
report = overseer.run_validation(start_level=2)
```

### Selective Platform Validation

Validate only specific platforms:

```python
overseer = AppleOverseer(
    project_path="./MyApp",
    platforms=["ios"]  # Only validate iOS
)
```

### JSON Report Export

Export detailed reports for analysis:

```python
overseer.export_report(report, "validation_report.json")
```

Report structure:
```json
{
  "project_path": "/path/to/project",
  "platforms": ["iOS", "macOS"],
  "final_status": "PASSED",
  "stamp_of_approval": true,
  "summary": {
    "total_checkpoints": 4,
    "passed_checkpoints": 4,
    "total_issues": 0,
    "total_warnings": 3
  },
  "checkpoints": [...]
}
```

---

## Best Practices

### For Users

1. **Run Early and Often**: Run validation throughout development, not just before release
2. **Address Warnings**: Don't ignore warnings; they indicate potential issues
3. **Understand Failures**: Read error messages and suggestions carefully
4. **Use Partial Validation**: During development, focus on specific checkpoints
5. **Export Reports**: Keep validation reports for historical tracking

### For Developers

1. **Write Clean Code**: Follow Apple's Swift style guidelines
2. **Organize Code**: Use clear directory structures (Models, Views, Controllers)
3. **Platform Isolation**: Use conditional compilation for platform-specific code
4. **Document Code**: Add comments and documentation
5. **Security First**: Never hardcode credentials or use HTTP
6. **Accessibility**: Implement accessibility features from the start

---

## Troubleshooting

### Common Issues

**Issue**: "No Xcode project found"
- **Solution**: Ensure you're pointing to a directory containing .xcodeproj, .xcworkspace, or Package.swift

**Issue**: "Platform detection failed"
- **Solution**: Manually specify platforms using `--platforms` flag

**Issue**: "Excessive warnings"
- **Solution**: Review and address warnings; aim for < 20 total

**Issue**: "Stamp of approval denied"
- **Solution**: Review checkpoint reports, fix critical issues, re-run validation

---

## Performance Characteristics

### Validation Speed

- **Small projects** (< 50 files): < 5 seconds
- **Medium projects** (50-200 files): 5-15 seconds
- **Large projects** (200+ files): 15-60 seconds

### Resource Usage

- **Memory**: Minimal (< 50MB for most projects)
- **CPU**: Single-threaded, low intensity
- **Disk**: Read-only access to project files

---

## Future Enhancements

### Planned Features

1. **Parallel Checkpoint Execution**: Run independent checks in parallel
2. **Custom Rule Engine**: Allow users to define custom validation rules
3. **IDE Integration**: Xcode extension for in-editor validation
4. **Continuous Monitoring**: Watch mode for real-time validation
5. **Historical Tracking**: Track quality metrics over time
6. **Team Dashboards**: Aggregate reports across multiple projects
7. **AI-Powered Suggestions**: Use ML to suggest improvements
8. **Performance Profiling**: Detect performance bottlenecks in code

### Community Contributions

Contributions welcome for:
- Additional platform validators
- Custom checkpoint implementations
- Enhanced reporting formats
- Integration with other tools

---

## Conclusion

The Apple Overseer skill provides comprehensive, multi-level quality control for Apple platform development. By implementing a progressive checkpoint system inspired by the building floor manager metaphor, it ensures that projects meet quality standards at every stage of development, from foundation to final approval.

The skill's modular architecture, clear feedback, and actionable recommendations make it an essential tool for maintaining high-quality Apple platform applications across iOS, macOS, iPadOS, and other platforms.

**Ready to start validating your Apple projects? Run the Apple Overseer and get your stamp of approval today!**

---

## Version History

- **v1.0.0** (2025-11-12): Initial release
  - Multi-level checkpoint system
  - Support for iOS, macOS, iPadOS, tvOS, watchOS
  - Foundation, Platform, Integration, and Executive validation
  - JSON report export
  - Command-line and programmatic interfaces

---

## License & Support

**License**: [Specify license]
**Support**: [Support contact information]
**Documentation**: This document (SKILL.md)
**Repository**: [Repository URL]

---

**End of Technical Specification**

*This skill was designed and implemented following the Claude Skills Architecture specification for creating modular, reusable, and maintainable skills for Claude Code.*
