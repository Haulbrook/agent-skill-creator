# GitHub Profile Reviewer

> Professional GitHub profile audit through the lens of recruiters and hiring managers

## Overview

GitHub Profile Reviewer is a comprehensive skill that analyzes GitHub profiles from a professional perspective. It helps developers optimize their GitHub presence by evaluating profiles the way hiring managers and technical recruiters would.

## Key Features

-  **Security First** - Scans for exposed credentials before any other analysis
-  **Professional Lens** - Every recommendation considers how it appears to employers
-  **Link Verification** - Tests all links for functionality and professional value
-  **Cleanup Recommendations** - Identifies repos to remove, archive, or improve
-  **Naming Analysis** - Suggests clearer, more professional repository names
-  **Non-Destructive** - NEVER modifies anything without explicit dual confirmation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run a profile review
python scripts/main.py your-github-username

# Save report to file
python scripts/main.py your-github-username --output report.md
```

## What Gets Reviewed

### Profile Elements
- Profile photo
- Display name
- Bio (keywords, length, professionalism)
- Location
- Company/organization
- Website URL
- Profile README

### Repositories
- Quality and documentation
- Activity and maintenance
- Naming clarity
- Classification (Showcase, Active, Archive, Learning, etc.)

### Security
- Exposed API keys and tokens
- Sensitive files (.env, credentials, private keys)
- Personal data exposure

### Links
- HTTP status verification
- SSL certificate validity
- Redirect detection
- Professional value assessment

## Protection Guarantees

```
This skill operates under an IMMUTABLE protection protocol:

1. NEVER deletes without DUAL confirmation
2. ALWAYS maintains allegiance to your interests
3. SECURITY scans run FIRST
4. NO data is stored or transmitted
```

## Output Formats

- **Markdown** (default) - Human-readable reports
- **JSON** - Machine-readable for integrations
- **HTML** - Web-ready presentation

## Documentation

- [Usage Guide](references/USAGE_GUIDE.md) - Detailed usage instructions
- [Security Protocol](references/SECURITY_PROTOCOL.md) - Security measures and scanning
- [SKILL.md](SKILL.md) - Complete skill specification

## Requirements

- Python 3.8+
- GitHub account (token recommended for higher rate limits)
- See [requirements.txt](requirements.txt) for dependencies

## Example Report

```
# GitHub Profile Professional Assessment
## octocat - 2024-01-15

**Overall Professional Score: 78/100**

| Category | Assessment |
|----------|------------|
| First Impression | 32/40 |
| Repository Quality | 4.2/5 |
| Security Posture | No Issues |
| Link Health | All Working |

### Priority Actions
- [HIGH] Add profile README for differentiation
- [MEDIUM] Review 3 repos for potential removal
- [LOW] Consider renaming 2 repos for clarity
```

## License

MIT

---

*Your GitHub profile is YOUR professional identity. This skill exists to PROTECT and ENHANCE it.*
