# Security Protocol

## Overview

The GitHub Profile Reviewer operates under a strict security protocol to protect users and their data. This document outlines the security measures, scanning capabilities, and protection guarantees.

## Protection Covenant

```
=================================================================
                    IMMUTABLE PROTECTION RULES
=================================================================

1. NEVER delete, remove, or modify ANY code/files/repos without:
   - Presenting the recommendation with full rationale
   - Receiving explicit written confirmation from the user
   - Asking a SECOND confirmation
   - Only proceeding after BOTH confirmations

2. ALWAYS maintain allegiance to the GitHub user's interests:
   - Protect their intellectual property
   - Guard against accidental exposure
   - Preserve their work history
   - Respect their creative decisions

3. SECURITY FIRST approach:
   - Scan for exposed credentials FIRST
   - Alert on findings IMMEDIATELY
   - Recommend protective actions PROACTIVELY

=================================================================
```

## Data Handling

### What We DO:
- Read public profile information
- Scan public repository contents
- Analyze public commit messages
- Verify public links

### What We NEVER DO:
- Store credentials or tokens beyond the session
- Transmit user data to third parties
- Access private repositories without explicit permission
- Log or record sensitive findings externally
- Execute code from user repositories
- Modify any repository content automatically

## Security Scanning Capabilities

### Credential Detection

We scan for over 15 types of exposed credentials:

| Type | Pattern | Severity |
|------|---------|----------|
| AWS Access Key | `AKIA[0-9A-Z]{16}` | CRITICAL |
| AWS Secret Key | Base64-like 40 chars | CRITICAL |
| GitHub Token | `ghp_`, `gho_` prefixed | CRITICAL |
| Google API Key | `AIza` prefixed | HIGH |
| Stripe Keys | `sk_live_`, `pk_live_` | CRITICAL |
| Slack Tokens | `xox` prefixed | HIGH |
| Private Keys | `-----BEGIN...PRIVATE KEY-----` | CRITICAL |
| JWT Tokens | `eyJ...` format | HIGH |
| Database URLs | Connection strings with credentials | CRITICAL |
| Generic API Keys | Pattern-matched | HIGH |
| SendGrid Keys | `SG.` prefixed | HIGH |
| Twilio Keys | `SK` prefixed | HIGH |
| NPM Tokens | `npm_` prefixed | HIGH |

### Sensitive File Detection

Files that trigger alerts:
- `.env`, `.env.*` - Environment files
- `credentials.json`, `secrets.json` - Credential files
- `id_rsa`, `id_dsa`, `*.pem`, `*.key` - Private keys
- `.npmrc`, `.pypirc` - Package manager credentials
- `wp-config.php`, `database.yml` - Configuration files

### Personal Information Detection

| Type | Severity | Note |
|------|----------|------|
| Social Security Numbers | CRITICAL | Pattern may have false positives |
| Credit Card Numbers | CRITICAL | Validated with checksum |
| Phone Numbers | MEDIUM | Often intentional |
| Email Addresses | LOW | Usually intentional |

## False Positive Handling

### Automatic False Positive Detection

We reduce false positives by checking for:
- Example/documentation context
- Placeholder patterns (`xxx`, `your-`, `sample`)
- Test/dummy indicators
- Known example values

### False Positive Likelihood Ratings

Each finding includes a likelihood assessment:
- **LOW**: High confidence this is a real credential
- **MEDIUM**: Could be real or example code
- **HIGH**: Likely a false positive/example

## Recommended Actions by Severity

### CRITICAL Findings
1. **Immediate Action Required**
2. Rotate/revoke the exposed credential NOW
3. Review git history for exposure duration
4. Consider using BFG Repo-Cleaner to purge history
5. Enable secret scanning on repository

### HIGH Findings
1. **Action Required Soon**
2. Rotate credentials within 24 hours
3. Review access logs for unauthorized use
4. Update to use environment variables

### MEDIUM Findings
1. **Review and Assess**
2. Determine if intentional (contact info)
3. Consider masking if personal data
4. Add to `.gitignore` if configuration

### LOW Findings
1. **Informational**
2. Review during regular maintenance
3. Often acceptable (public emails)

## Git History Considerations

### Important Warning

Even after removing sensitive data from current files:
- **Git history retains all commits**
- Deleted files can be recovered
- Exposed credentials may still be accessible

### Remediation Steps

1. **For recent exposure** (not pushed):
   ```bash
   git reset --soft HEAD~1
   # Remove sensitive data
   git commit
   ```

2. **For pushed commits**:
   - Use BFG Repo-Cleaner
   - Force push to all remotes
   - Notify collaborators
   - Consider repository as compromised

3. **For critical credentials**:
   - Rotate immediately regardless of history cleanup
   - Assume credential was compromised
   - Check for unauthorized access

## Best Practices

### Prevention

1. **Use `.gitignore`**
   ```
   .env
   .env.*
   *.pem
   *.key
   credentials.json
   secrets/
   ```

2. **Use environment variables**
   ```python
   # Good
   api_key = os.environ.get('API_KEY')

   # Bad
   api_key = 'sk_live_abc123...'
   ```

3. **Enable GitHub secret scanning**
   - Repository Settings → Security → Secret scanning

4. **Use GitHub Actions secrets**
   - Never commit CI/CD credentials

### Detection

1. **Pre-commit hooks**
   ```bash
   pip install pre-commit detect-secrets
   detect-secrets scan > .secrets.baseline
   ```

2. **Regular audits**
   - Run this tool periodically
   - Review security alerts from GitHub

## Reporting Security Issues

If you discover a security vulnerability in this tool:
1. Do NOT open a public issue
2. Contact the maintainers directly
3. Provide detailed reproduction steps
4. Allow time for fix before disclosure

## Disclaimer

This tool provides security scanning as a convenience feature. It is NOT a replacement for:
- Professional security audits
- Dedicated secret scanning tools
- Security-focused code review
- Compliance assessments

Always follow your organization's security policies and consult security professionals for critical systems.
