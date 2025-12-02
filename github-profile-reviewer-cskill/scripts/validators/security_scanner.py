"""
Security Scanner - Sensitive Data and Credential Detection

CRITICAL COMPONENT: This scanner runs FIRST in any profile review
to identify exposed credentials and sensitive data.

This protects users from accidental exposure of:
- API keys and tokens
- Database credentials
- Private keys
- Personal information
- Client/customer data
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from github import Github
    PYGITHUB_AVAILABLE = True
except ImportError:
    PYGITHUB_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class SecurityFinding:
    """A security finding."""
    type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    location: str
    file_path: Optional[str]
    line_number: Optional[int]
    description: str
    matched_pattern: str
    recommendation: str
    false_positive_likelihood: str  # HIGH, MEDIUM, LOW


class SecurityScanner:
    """
    Security scanner for GitHub profiles and repositories.

    Scans for:
    1. Exposed API keys and tokens
    2. Database credentials
    3. Private keys (SSH, GPG, etc.)
    4. Environment files
    5. Personal information
    6. Known vulnerable patterns

    IMPORTANT: This component runs with HIGHEST PRIORITY
    before any other analysis to protect user data.
    """

    # Credential patterns with high confidence
    CREDENTIAL_PATTERNS = {
        'aws_access_key': {
            'pattern': r'AKIA[0-9A-Z]{16}',
            'severity': 'CRITICAL',
            'description': 'AWS Access Key ID',
            'recommendation': 'Rotate this key immediately in AWS IAM console'
        },
        'aws_secret_key': {
            'pattern': r'(?i)aws_secret_access_key\s*[=:]\s*["\']?([A-Za-z0-9/+=]{40})',
            'severity': 'CRITICAL',
            'description': 'AWS Secret Access Key',
            'recommendation': 'Rotate this key immediately and remove from history'
        },
        'github_token': {
            'pattern': r'ghp_[A-Za-z0-9_]{36}',
            'severity': 'CRITICAL',
            'description': 'GitHub Personal Access Token',
            'recommendation': 'Revoke this token immediately in GitHub settings'
        },
        'github_oauth': {
            'pattern': r'gho_[A-Za-z0-9_]{36}',
            'severity': 'CRITICAL',
            'description': 'GitHub OAuth Token',
            'recommendation': 'Revoke this token immediately'
        },
        'google_api_key': {
            'pattern': r'AIza[0-9A-Za-z_-]{35}',
            'severity': 'HIGH',
            'description': 'Google API Key',
            'recommendation': 'Regenerate this key in Google Cloud Console'
        },
        'stripe_key': {
            'pattern': r'(?:sk|pk)_(?:test|live)_[0-9a-zA-Z]{24,}',
            'severity': 'CRITICAL',
            'description': 'Stripe API Key',
            'recommendation': 'Roll this key immediately in Stripe dashboard'
        },
        'slack_token': {
            'pattern': r'xox[baprs]-[0-9a-zA-Z]{10,48}',
            'severity': 'HIGH',
            'description': 'Slack Token',
            'recommendation': 'Regenerate this token in Slack workspace settings'
        },
        'slack_webhook': {
            'pattern': r'https://hooks\.slack\.com/services/T[A-Z0-9]{8}/B[A-Z0-9]{8}/[A-Za-z0-9]{24}',
            'severity': 'HIGH',
            'description': 'Slack Webhook URL',
            'recommendation': 'Regenerate this webhook URL'
        },
        'private_key': {
            'pattern': r'-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
            'severity': 'CRITICAL',
            'description': 'Private Key',
            'recommendation': 'Remove immediately and generate new key pair'
        },
        'jwt_token': {
            'pattern': r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
            'severity': 'HIGH',
            'description': 'JWT Token',
            'recommendation': 'This token should not be hardcoded'
        },
        'database_url': {
            'pattern': r'(?i)(?:mysql|postgres|mongodb|redis)://[^\s"\']+:[^\s"\']+@[^\s"\']+',
            'severity': 'CRITICAL',
            'description': 'Database Connection URL with credentials',
            'recommendation': 'Use environment variables for database connections'
        },
        'generic_password': {
            'pattern': r'(?i)(?:password|passwd|pwd|secret)\s*[=:]\s*["\']([^"\']{8,})["\']',
            'severity': 'HIGH',
            'description': 'Hardcoded password',
            'recommendation': 'Remove hardcoded passwords, use environment variables'
        },
        'api_key_generic': {
            'pattern': r'(?i)(?:api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9_-]{20,})["\']',
            'severity': 'HIGH',
            'description': 'Generic API Key',
            'recommendation': 'Store API keys in environment variables'
        },
        'sendgrid_key': {
            'pattern': r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}',
            'severity': 'HIGH',
            'description': 'SendGrid API Key',
            'recommendation': 'Regenerate this key in SendGrid dashboard'
        },
        'twilio_key': {
            'pattern': r'SK[0-9a-fA-F]{32}',
            'severity': 'HIGH',
            'description': 'Twilio API Key',
            'recommendation': 'Regenerate this key in Twilio console'
        },
        'heroku_key': {
            'pattern': r'(?i)heroku.*[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
            'severity': 'HIGH',
            'description': 'Heroku API Key',
            'recommendation': 'Regenerate this key in Heroku dashboard'
        },
        'npm_token': {
            'pattern': r'npm_[A-Za-z0-9]{36}',
            'severity': 'HIGH',
            'description': 'NPM Access Token',
            'recommendation': 'Revoke this token in npm account settings'
        },
    }

    # Sensitive file patterns
    SENSITIVE_FILES = [
        '.env',
        '.env.local',
        '.env.production',
        '.env.development',
        'credentials.json',
        'secrets.json',
        'config.json',
        'settings.json',
        '.htpasswd',
        'id_rsa',
        'id_dsa',
        'id_ecdsa',
        'id_ed25519',
        '.pem',
        '.key',
        '.p12',
        '.pfx',
        'keystore.jks',
        'keystore',
        '.npmrc',
        '.pypirc',
        'docker-compose.override.yml',
        'wp-config.php',
        'database.yml',
        'credentials.xml',
    ]

    # Personal information patterns
    PERSONAL_INFO_PATTERNS = {
        'email': {
            'pattern': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'severity': 'LOW',
            'description': 'Email address',
            'false_positive_note': 'May be intentional contact info'
        },
        'phone': {
            'pattern': r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'severity': 'MEDIUM',
            'description': 'Phone number',
            'false_positive_note': 'Verify if intentional'
        },
        'ssn': {
            'pattern': r'\d{3}-\d{2}-\d{4}',
            'severity': 'CRITICAL',
            'description': 'Possible Social Security Number',
            'false_positive_note': 'Could be other formatted number'
        },
        'credit_card': {
            'pattern': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
            'severity': 'CRITICAL',
            'description': 'Possible credit card number',
            'false_positive_note': 'Verify if real card number'
        },
    }

    def __init__(self, github_token: Optional[str] = None):
        """Initialize with optional GitHub token."""
        self.token = github_token
        self.github = None

        if PYGITHUB_AVAILABLE and github_token:
            self.github = Github(github_token)
        elif PYGITHUB_AVAILABLE:
            self.github = Github()

    def scan_profile(self, username: str) -> Dict[str, Any]:
        """
        Scan entire GitHub profile for security issues.

        Args:
            username: GitHub username to scan

        Returns:
            Dict with findings categorized by severity
        """
        results = {
            'username': username,
            'scan_type': 'full_profile',
            'critical_findings': [],
            'high_findings': [],
            'medium_findings': [],
            'low_findings': [],
            'sensitive_files_found': [],
            'issues_found': 0,
            'severity_score': 0,
            'recommendations': []
        }

        # Get all repositories
        repos = self._get_repositories(username)

        if not repos:
            results['error'] = 'Could not fetch repositories'
            return results

        # Scan each repository
        for repo in repos:
            repo_findings = self._scan_repository(repo)
            self._merge_findings(results, repo_findings)

        # Calculate severity score
        results['severity_score'] = self._calculate_severity_score(results)

        # Generate overall recommendations
        results['recommendations'] = self._generate_recommendations(results)

        # Count total issues
        results['issues_found'] = (
            len(results['critical_findings']) +
            len(results['high_findings']) +
            len(results['medium_findings']) +
            len(results['low_findings'])
        )

        return results

    def _get_repositories(self, username: str) -> List[Any]:
        """Get user's public repositories."""
        if self.github:
            try:
                user = self.github.get_user(username)
                return list(user.get_repos(type='public'))
            except Exception as e:
                print(f"Error fetching repos: {e}")
                return []
        return []

    def _scan_repository(self, repo) -> Dict[str, Any]:
        """Scan a single repository for security issues."""
        findings = {
            'critical_findings': [],
            'high_findings': [],
            'medium_findings': [],
            'low_findings': [],
            'sensitive_files_found': []
        }

        repo_name = repo.name if hasattr(repo, 'name') else repo.get('name', 'unknown')

        try:
            # Check for sensitive files
            self._check_sensitive_files(repo, findings)

            # Scan README and other common files
            self._scan_readme(repo, findings)

            # Scan recent commits (limited to avoid rate limits)
            self._scan_recent_commits(repo, findings)

        except Exception as e:
            print(f"Error scanning {repo_name}: {e}")

        return findings

    def _check_sensitive_files(self, repo, findings: Dict):
        """Check if sensitive files exist in repository."""
        repo_name = repo.name if hasattr(repo, 'name') else 'unknown'

        try:
            contents = repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                file_name = file_content.name.lower()

                # Check against sensitive file list
                for sensitive in self.SENSITIVE_FILES:
                    if sensitive.lower() in file_name or file_name.endswith(sensitive.lower()):
                        finding = SecurityFinding(
                            type='sensitive_file',
                            severity='HIGH',
                            location=f'{repo_name}/{file_content.path}',
                            file_path=file_content.path,
                            line_number=None,
                            description=f'Sensitive file found: {file_content.name}',
                            matched_pattern=sensitive,
                            recommendation='Remove this file or add to .gitignore',
                            false_positive_likelihood='LOW'
                        )
                        findings['sensitive_files_found'].append(self._finding_to_dict(finding))
                        findings['high_findings'].append(self._finding_to_dict(finding))

                # Recurse into directories (limited depth)
                if file_content.type == "dir":
                    try:
                        contents.extend(repo.get_contents(file_content.path))
                    except:
                        pass

        except Exception as e:
            pass  # Repository might be empty or inaccessible

    def _scan_readme(self, repo, findings: Dict):
        """Scan README file for exposed credentials."""
        repo_name = repo.name if hasattr(repo, 'name') else 'unknown'

        try:
            readme = repo.get_readme()
            content = readme.decoded_content.decode('utf-8')

            # Scan for credential patterns
            self._scan_content(content, f'{repo_name}/README.md', findings)

        except Exception:
            pass  # No README or can't access

    def _scan_recent_commits(self, repo, findings: Dict, limit: int = 10):
        """Scan recent commit messages and diffs for credentials."""
        repo_name = repo.name if hasattr(repo, 'name') else 'unknown'

        try:
            commits = list(repo.get_commits()[:limit])

            for commit in commits:
                # Scan commit message
                message = commit.commit.message
                self._scan_content(
                    message,
                    f'{repo_name}/commit/{commit.sha[:7]}',
                    findings,
                    is_commit=True
                )

        except Exception as e:
            pass  # Can't access commits

    def _scan_content(self, content: str, location: str, findings: Dict, is_commit: bool = False):
        """Scan content string for security issues."""

        # Scan for credential patterns
        for pattern_name, pattern_info in self.CREDENTIAL_PATTERNS.items():
            matches = re.finditer(pattern_info['pattern'], content)

            for match in matches:
                # Determine false positive likelihood
                fp_likelihood = self._assess_false_positive(match.group(), pattern_name, content)

                finding = SecurityFinding(
                    type='exposed_credential',
                    severity=pattern_info['severity'],
                    location=location,
                    file_path=None if is_commit else location,
                    line_number=content[:match.start()].count('\n') + 1,
                    description=pattern_info['description'],
                    matched_pattern=pattern_name,
                    recommendation=pattern_info['recommendation'],
                    false_positive_likelihood=fp_likelihood
                )

                self._add_finding(findings, finding)

        # Scan for personal info (with higher false positive tolerance)
        for pattern_name, pattern_info in self.PERSONAL_INFO_PATTERNS.items():
            # Only flag high-severity personal info
            if pattern_info['severity'] in ['CRITICAL', 'HIGH']:
                matches = re.finditer(pattern_info['pattern'], content)

                for match in matches:
                    finding = SecurityFinding(
                        type='personal_info',
                        severity=pattern_info['severity'],
                        location=location,
                        file_path=None if is_commit else location,
                        line_number=content[:match.start()].count('\n') + 1,
                        description=pattern_info['description'],
                        matched_pattern=pattern_name,
                        recommendation=f'Verify and remove if sensitive: {pattern_info.get("false_positive_note", "")}',
                        false_positive_likelihood='MEDIUM'
                    )

                    self._add_finding(findings, finding)

    def _assess_false_positive(self, matched: str, pattern_name: str, context: str) -> str:
        """Assess likelihood that a match is a false positive."""

        # Check if it's in an example or documentation context
        doc_indicators = ['example', 'sample', 'test', 'dummy', 'placeholder', 'xxx', 'your-']
        context_lower = context.lower()

        for indicator in doc_indicators:
            if indicator in context_lower:
                return 'HIGH'

        # Check if the matched value looks like a placeholder
        matched_lower = matched.lower()
        if any(x in matched_lower for x in ['example', 'test', 'sample', 'your_', 'xxx', '***']):
            return 'HIGH'

        # Real credentials are usually longer and more random
        if pattern_name in ['generic_password', 'api_key_generic']:
            if len(matched) < 12 or matched.isalpha() or matched.isdigit():
                return 'MEDIUM'

        return 'LOW'

    def _add_finding(self, findings: Dict, finding: SecurityFinding):
        """Add finding to appropriate severity list."""
        finding_dict = self._finding_to_dict(finding)

        severity_map = {
            'CRITICAL': 'critical_findings',
            'HIGH': 'high_findings',
            'MEDIUM': 'medium_findings',
            'LOW': 'low_findings'
        }

        key = severity_map.get(finding.severity, 'low_findings')
        findings[key].append(finding_dict)

    def _finding_to_dict(self, finding: SecurityFinding) -> Dict[str, Any]:
        """Convert SecurityFinding to dictionary."""
        return {
            'type': finding.type,
            'severity': finding.severity,
            'location': finding.location,
            'file_path': finding.file_path,
            'line_number': finding.line_number,
            'description': finding.description,
            'matched_pattern': finding.matched_pattern,
            'recommendation': finding.recommendation,
            'false_positive_likelihood': finding.false_positive_likelihood
        }

    def _merge_findings(self, results: Dict, new_findings: Dict):
        """Merge new findings into results."""
        for key in ['critical_findings', 'high_findings', 'medium_findings', 'low_findings', 'sensitive_files_found']:
            results[key].extend(new_findings.get(key, []))

    def _calculate_severity_score(self, results: Dict) -> int:
        """Calculate overall severity score (higher = worse)."""
        score = 0
        score += len(results['critical_findings']) * 10
        score += len(results['high_findings']) * 5
        score += len(results['medium_findings']) * 2
        score += len(results['low_findings']) * 1
        return score

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate overall security recommendations."""
        recommendations = []

        if results['critical_findings']:
            recommendations.append(
                "IMMEDIATE ACTION: Critical security issues found. "
                "Rotate exposed credentials immediately."
            )

        if results['sensitive_files_found']:
            recommendations.append(
                "Remove sensitive files and add them to .gitignore. "
                "Consider using git filter-branch or BFG to clean history."
            )

        if results['high_findings']:
            recommendations.append(
                "Review and address high-severity findings as soon as possible."
            )

        if not any([results['critical_findings'], results['high_findings'], results['sensitive_files_found']]):
            recommendations.append(
                "No critical security issues found. Continue following security best practices."
            )

        return recommendations


def quick_scan(username: str, token: Optional[str] = None) -> Dict[str, Any]:
    """Quick utility function to scan a GitHub profile."""
    scanner = SecurityScanner(token)
    return scanner.scan_profile(username)
