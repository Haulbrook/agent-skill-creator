# GitHub Profile Reviewer - Usage Guide

## Quick Start

### Basic Usage

```bash
# Review a GitHub profile
python scripts/main.py username123

# Save report to file
python scripts/main.py username123 --output report.md

# Use JSON format
python scripts/main.py username123 --format json --output report.json
```

### With GitHub Token (Recommended)

For higher API rate limits:

```bash
# Set token as environment variable
export GITHUB_TOKEN=your_token_here
python scripts/main.py username123

# Or pass directly
python scripts/main.py username123 --token your_token_here
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--token` | `-t` | GitHub personal access token |
| `--output` | `-o` | Output file path |
| `--format` | `-f` | Output format: markdown, json, html |
| `--verbose` | `-v` | Verbose output |
| `--no-security` | | Skip security scan |
| `--no-links` | | Skip link verification |
| `--no-cleanup` | | Skip cleanup recommendations |
| `--no-naming` | | Skip naming review |

## Review Phases

### Phase 1: Security Scan (ALWAYS FIRST)
- Scans for exposed credentials
- Checks for sensitive files
- Identifies personal data exposure
- **Runs automatically unless `--no-security` specified**

### Phase 2: Profile Overview
- Evaluates profile photo, name, bio
- Checks website and social links
- Assesses profile README
- Calculates first impression score

### Phase 3: Repository Analysis
- Classifies all repositories
- Evaluates quality and documentation
- Analyzes naming clarity
- Identifies improvement opportunities

### Phase 4: Link Verification
- Tests all links for functionality
- Validates SSL certificates
- Checks for redirects
- Assesses professional value

### Phase 5: Cleanup Recommendations
- Identifies removal candidates
- Suggests privatization options
- Recommends archiving
- Lists improvement actions

### Phase 6: Naming Review
- Scores naming clarity
- Suggests better names
- Provides rationale

## Understanding the Report

### Score Categories

| Category | Description | Weight |
|----------|-------------|--------|
| First Impression | Profile completeness and appeal | 25% |
| Repository Quality | Code quality and documentation | 25% |
| Documentation | README presence and quality | 20% |
| Security Posture | No exposed credentials | 15% |
| Professional Polish | Naming, links, presentation | 15% |

### Repository Classifications

| Classification | Description | Typical Action |
|---------------|-------------|----------------|
| **Showcase** | Best work, highlight-worthy | Feature prominently |
| **Active** | Currently maintained | Keep, ensure quality |
| **Archive** | Valuable but inactive | Archive with note |
| **Learning** | Tutorial/course artifacts | Make private or remove |
| **Experimental** | Tests/experiments | Make private or remove |
| **Duplicate** | Same as another repo | Consolidate or remove |
| **Abandoned** | No activity, no interest | Consider removal |

## Safety Features

### Double Confirmation Protocol

This skill NEVER performs destructive actions without explicit confirmation:

1. Recommendation is presented with full rationale
2. User must confirm: "I confirm I want to [action]"
3. User must confirm again: "YES, I am sure"
4. Only then is action executed

### Security First

- Security scan runs FIRST before any other analysis
- Critical findings are alerted immediately
- No credentials are stored or transmitted
- Private repositories require explicit permission

## Examples

### Full Review with All Features

```bash
python scripts/main.py octocat --output octocat-review.md
```

### Quick Security Check Only

```bash
python scripts/main.py octocat --no-links --no-cleanup --no-naming
```

### Generate JSON for API Integration

```bash
python scripts/main.py octocat --format json --output review.json
```

### Verbose Output for Debugging

```bash
python scripts/main.py octocat --verbose
```

## Integration

### As a Python Module

```python
from scripts.main import GitHubProfileReviewer, ReviewConfig

config = ReviewConfig(
    username='octocat',
    github_token='your_token',
    include_security_scan=True,
    include_link_verification=True
)

reviewer = GitHubProfileReviewer(config)
results = reviewer.run_review()
report = reviewer.generate_report()
```

### Individual Components

```python
# Security scan only
from scripts.validators.security_scanner import SecurityScanner
scanner = SecurityScanner(token='your_token')
findings = scanner.scan_profile('octocat')

# Link verification only
from scripts.validators.link_validator import LinkValidator
validator = LinkValidator()
results = validator.verify_links([{'url': 'https://example.com', 'source': 'test'}])
```

## Troubleshooting

### Rate Limiting

If you hit GitHub API rate limits:
1. Use a personal access token (`--token`)
2. Wait for rate limit reset (shown in error message)
3. Run with `--no-links` to reduce API calls

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### Permission Errors

- Ensure token has `public_repo` scope
- Private repos require additional permissions
- Some organizations may restrict API access

## Support

For issues or feature requests, please open an issue in the repository.
