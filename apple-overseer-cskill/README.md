# Apple Overseer - Multi-Level Quality Control for Apple Platforms

**Version:** 1.0.0
**Type:** Claude Skill
**Domain:** Apple Platform Quality Assurance

## Overview

Apple Overseer is a comprehensive quality control checkpoint system for Apple platform development (iOS, macOS, iPadOS, tvOS, watchOS). Like a multi-story building with dedicated floor managers at each level, it validates your project through progressive quality gates, ensuring excellence at every stage.

## The Building Metaphor

```
🎖️  Level 4: Executive Overseer      → Final QA & Stamp of Approval
                ↑
🔗  Level 3: Integration Coordinator  → Cross-Platform Validation
                ↑
📱  Level 2: Platform Overseers       → iOS, macOS, iPadOS Validation
                ↑
🏗️  Level 1: Foundation Inspector    → Code Structure & Quality
```

Each "floor" has a manager (overseer) who validates specific aspects before allowing progression to the next level. Only when all checkpoints pass do you receive the final **Stamp of Approval**.

## Key Features

- **Multi-Level Validation**: Progressive checkpoints ensure comprehensive quality control
- **Platform Intelligence**: Automatically detects and validates iOS, macOS, iPadOS, tvOS, and watchOS
- **Cross-Platform Analysis**: Validates consistency and compatibility across platforms
- **Actionable Feedback**: Clear, specific recommendations for every issue found
- **Stamp of Approval**: Clear pass/fail criteria with final approval workflow
- **Flexible Usage**: Command-line, programmatic, or CI/CD integration
- **Zero Dependencies**: Pure Python, no external packages required

## Quick Start

### Command-Line Usage

```bash
# Basic usage (auto-detect platforms)
python -m apple_overseer_cskill.scripts.main /path/to/your/project

# Specify platforms explicitly
python -m apple_overseer_cskill.scripts.main ./MyApp --platforms ios macos ipados

# Validate specific checkpoint levels
python -m apple_overseer_cskill.scripts.main ./MyApp --start-level 2 --stop-level 3

# Export detailed report
python -m apple_overseer_cskill.scripts.main ./MyApp --export validation_report.json
```

### Programmatic Usage

```python
from apple_overseer_cskill.scripts import AppleOverseer

# Create overseer for your project
overseer = AppleOverseer(
    project_path="./MyApp",
    platforms=["ios", "macos"]  # Optional: auto-detected if not specified
)

# Run full validation
report = overseer.run_validation()

# Check if approved
if report.stamp_of_approval:
    print("✅ Project approved for deployment!")
    print(f"All {len(report.checkpoint_reports)} checkpoints passed")
else:
    print(f"❌ Found {report.total_issues} issues and {report.total_warnings} warnings")

# Export detailed report
overseer.export_report(report, "validation_report.json")
```

## Checkpoint Levels

### Level 1: Foundation Inspector

Validates the fundamental aspects of your project:

- ✓ Project structure (Xcode projects, workspaces, Swift packages)
- ✓ Build configuration (CocoaPods, Carthage, SPM)
- ✓ Swift code quality (syntax, force unwrapping, debug statements)
- ✓ Dependency analysis
- ✓ Info.plist configuration
- ✓ Code organization

**Pass Criteria**: Valid project structure, build configuration, and no critical syntax errors

### Level 2: Platform-Specific Overseers

Validates platform-specific requirements for each target platform:

**iOS Overseer**:
- UIKit/SwiftUI framework usage
- Deployment target validation
- iOS capabilities and entitlements
- App icon and assets

**macOS Overseer**:
- AppKit/Cocoa framework usage
- App Sandbox configuration
- macOS-specific entitlements
- Distribution readiness

**iPadOS Overseer**:
- Scene-based architecture support
- Size class handling
- Split view and multitasking support
- iPad-specific UI patterns

**Pass Criteria**: Platform frameworks properly used, requirements met, valid configuration

### Level 3: Integration Coordinator

Validates cross-platform compatibility (for multi-platform projects):

- ✓ Conditional compilation (#if os(iOS), etc.)
- ✓ Shared code architecture
- ✓ Platform API isolation
- ✓ Resource sharing and consistency
- ✓ Architecture pattern consistency

**Pass Criteria**: Proper platform isolation, organized shared code, no API conflicts

*Note: Single-platform projects automatically pass this level*

### Level 4: Executive Overseer

Final quality assurance and approval decision:

- ✓ Previous checkpoint review
- ✓ Performance best practices
- ✓ Security validation (no hardcoded credentials, HTTPS usage)
- ✓ UX/UI consistency
- ✓ App Store readiness (privacy manifest, documentation)
- ✓ Code quality metrics
- ✓ **Stamp of Approval decision**

**Pass Criteria**: All checkpoints passed, no critical issues, acceptable warnings (< 20)

## Installation

### Requirements

- Python 3.8 or higher
- No external dependencies

### Setup

```bash
# Clone or download the skill
cd apple-overseer-cskill

# Optional: Install for system-wide access
pip install -e .
```

## Supported Platforms

| Platform | Support Level | Primary Frameworks |
|----------|---------------|-------------------|
| iOS | Full | UIKit, SwiftUI |
| macOS | Full | AppKit, Cocoa, SwiftUI |
| iPadOS | Full | UIKit, SwiftUI |
| tvOS | Basic | TVUIKit |
| watchOS | Basic | WatchKit |

## CI/CD Integration

### GitHub Actions

```yaml
name: Quality Control

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      - name: Run Apple Overseer
        run: |
          python -m apple_overseer_cskill.scripts.main . --export report.json

      - name: Upload Report
        uses: actions/upload-artifact@v2
        if: always()
        with:
          name: validation-report
          path: report.json
```

## Example Output

```
======================================================================
🏢 APPLE OVERSEER - MULTI-LEVEL QUALITY CONTROL
======================================================================
📁 Project: /Users/dev/MyAwesomeApp
🎯 Platforms: iOS, macOS, iPadOS
📊 Checkpoints: Level 1 → Level 4
======================================================================

┌─────────────────────────────────────────────────────────────────┐
│ LEVEL 1: FOUNDATION INSPECTOR                                   │
│ Validating code structure, syntax, and dependencies            │
└─────────────────────────────────────────────────────────────────┘

✅ Status: PASSED
⏱️  Duration: 1.23s
✓  Passed: 8
✗  Failed: 0
⚠  Warnings: 2
📊 Success Rate: 100.0%

💡 Recommendations:
   • Proceed to platform-specific validation

[... additional checkpoint output ...]

======================================================================
📋 FINAL VALIDATION SUMMARY
======================================================================
Project: /Users/dev/MyAwesomeApp
Platforms: iOS, macOS, iPadOS
Duration: 4.56s

Checkpoints Completed: 4
✅ Passed: 4
❌ Failed: 0
🔴 Total Issues: 0
⚠️  Total Warnings: 5

Final Status: PASSED

🎖️  STAMP OF APPROVAL: ✅ GRANTED
======================================================================
```

## What Gets Validated?

### Code Quality
- Swift syntax and best practices
- Force unwrapping usage
- Debug statements in production code
- Code organization and structure
- File size and complexity

### Platform Compliance
- Correct framework usage per platform
- Platform-specific API usage
- Deployment target configuration
- Entitlements and capabilities
- Asset configuration

### Security
- Hardcoded credentials detection
- HTTPS usage validation
- Secure storage patterns
- App Transport Security compliance

### Performance
- Large asset detection
- Memory management patterns
- Resource optimization

### App Store Readiness
- Privacy manifest (iOS 17+)
- Documentation presence
- License files
- Submission requirements

## Interpreting Results

### Status Types

- **✅ PASSED**: Checkpoint completed successfully, no issues
- **⚠️ WARNING**: Checkpoint passed but has warnings requiring attention
- **❌ FAILED**: Checkpoint failed with blocking issues
- **⏳ PENDING**: Checkpoint not yet executed
- **⏭️ SKIPPED**: Checkpoint not applicable (e.g., integration for single-platform)

### Issue Severity

- **🔴 Error**: Critical issue blocking approval
- **⚠️ Warning**: Important issue that should be addressed
- **ℹ️ Info**: Informational message for awareness

### Stamp of Approval

The final stamp of approval is granted when:

1. All checkpoint levels pass (or have acceptable warnings)
2. No critical security issues detected
3. No critical performance issues detected
4. Total warnings < 20 across all checkpoints
5. Code quality metrics are acceptable

## Configuration

### Platform Detection

The skill automatically detects platforms by analyzing:

- Framework imports (UIKit → iOS, AppKit → macOS)
- Package.swift platform declarations
- Conditional compilation directives

To override auto-detection, specify platforms explicitly:

```bash
python -m apple_overseer_cskill.scripts.main ./MyApp --platforms ios macos
```

### Partial Validation

Run specific checkpoint levels:

```bash
# Only foundation check
python -m apple_overseer_cskill.scripts.main ./MyApp --start-level 1 --stop-level 1

# Platform and integration only
python -m apple_overseer_cskill.scripts.main ./MyApp --start-level 2 --stop-level 3
```

## Troubleshooting

### "No Xcode project found"

Ensure you're in a directory containing:
- `.xcodeproj` (Xcode project)
- `.xcworkspace` (Xcode workspace)
- `Package.swift` (Swift Package Manager)

### "Platform detection failed"

Manually specify platforms:
```bash
python -m apple_overseer_cskill.scripts.main ./MyApp --platforms ios
```

### "Stamp of approval denied"

Review the checkpoint reports to identify issues:
1. Check which checkpoint failed
2. Review specific errors and warnings
3. Follow the provided suggestions
4. Re-run validation after fixes

## Best Practices

1. **Run Early**: Validate throughout development, not just before release
2. **Address Warnings**: Don't ignore warnings; they indicate potential issues
3. **Use in CI/CD**: Automate validation in your continuous integration pipeline
4. **Track Reports**: Export and keep validation reports for historical tracking
5. **Educate Team**: Ensure all developers understand the validation criteria

## Advanced Usage

### Programmatic Integration

```python
from apple_overseer_cskill.scripts import AppleOverseer, CheckpointStatus

overseer = AppleOverseer("./MyApp", platforms=["ios", "macos"])
report = overseer.run_validation()

# Access specific checkpoint results
foundation_report = report.get_checkpoint_by_level(CheckpointLevel.FOUNDATION)
print(f"Foundation success rate: {foundation_report.success_rate}%")

# Check specific platforms
for platform_result in report.metadata.get('platform_results', []):
    print(f"{platform_result['platform']}: {platform_result['status']}")

# Export for analysis
overseer.export_report(report, "detailed_report.json")
```

## Contributing

We welcome contributions! Areas for enhancement:

- Additional platform validators
- Custom validation rules
- Enhanced reporting formats
- Integration with other tools
- Performance optimizations

## Documentation

- **SKILL.md**: Comprehensive technical specification (5000+ words)
- **README.md**: This file - user-friendly overview
- **marketplace.json**: Skill activation configuration

## Support & Feedback

- **Issues**: Report bugs or request features
- **Documentation**: See SKILL.md for detailed technical information
- **Examples**: Check `assets/examples/` for sample usage

## License

[Specify license]

---

**Ready to validate your Apple platform project? Get your Stamp of Approval today!**

```bash
python -m apple_overseer_cskill.scripts.main /path/to/your/project
```
