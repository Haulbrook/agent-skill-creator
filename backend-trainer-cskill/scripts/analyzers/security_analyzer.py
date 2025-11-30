"""
Security Analyzer for Backend Trainer

Identifies security vulnerabilities, risks, and compliance issues
in backend code following OWASP guidelines.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityCategory(Enum):
    INJECTION = "injection"
    BROKEN_AUTH = "broken_authentication"
    SENSITIVE_DATA = "sensitive_data_exposure"
    XXE = "xml_external_entities"
    BROKEN_ACCESS = "broken_access_control"
    SECURITY_MISCONFIG = "security_misconfiguration"
    XSS = "cross_site_scripting"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    VULNERABLE_COMPONENTS = "vulnerable_components"
    LOGGING = "insufficient_logging"
    CRYPTOGRAPHY = "cryptographic_failures"


@dataclass
class SecurityIssue:
    severity: Severity
    category: VulnerabilityCategory
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    code_snippet: str = ""
    cwe_id: str = ""
    recommendation: str = ""
    owasp_category: str = ""


@dataclass
class SecurityAnalysisResult:
    overall_score: int
    risk_level: str
    issues: list[SecurityIssue] = field(default_factory=list)
    recommendations: list[SecurityIssue] = field(default_factory=list)
    owasp_coverage: dict = field(default_factory=dict)
    stats: dict = field(default_factory=dict)


class SecurityAnalyzer:
    """Analyzes backend code for security vulnerabilities."""

    # SQL Injection patterns
    SQL_INJECTION_PATTERNS = [
        (r'execute\s*\(\s*["\'][^"\']*%s', "String formatting in SQL"),
        (r'execute\s*\(\s*f["\']', "f-string in SQL execute"),
        (r'execute\s*\([^)]*\+\s*\w+', "String concatenation in SQL"),
        (r'\.format\s*\([^)]*\).*execute', "format() in SQL"),
        (r'cursor\.execute\s*\(\s*["\'][^"\']*\'\s*\+', "Concatenation in cursor.execute"),
        (r'\$\{[^}]+\}.*(?:SELECT|INSERT|UPDATE|DELETE)', "Template literal in SQL (JS)"),
    ]

    # Command Injection patterns
    COMMAND_INJECTION_PATTERNS = [
        (r'os\.system\s*\(\s*[^)]*\+', "os.system with concatenation"),
        (r'subprocess\.[^(]+\(\s*["\'][^"\']*\'\s*\+', "subprocess with concatenation"),
        (r'subprocess\..*shell\s*=\s*True', "subprocess with shell=True"),
        (r'exec\s*\(\s*[^)]*\+', "exec with concatenation"),
        (r'eval\s*\(\s*(?![\'"]\s*\))', "eval() usage"),
        (r'child_process\.exec\s*\(\s*[^)]*\+', "child_process.exec with concatenation"),
    ]

    # Authentication issues
    AUTH_PATTERNS = [
        (r'password\s*==\s*["\'][^"\']+["\']', "Hardcoded password comparison"),
        (r'secret\s*=\s*["\'][^"\']{5,}["\']', "Hardcoded secret"),
        (r'api_key\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded API key"),
        (r'jwt\.decode\s*\([^)]*verify\s*=\s*False', "JWT verification disabled"),
        (r'verify\s*=\s*False.*requests\.(get|post)', "SSL verification disabled"),
    ]

    # Sensitive data exposure
    SENSITIVE_DATA_PATTERNS = [
        (r'print\s*\(\s*password', "Password in print statement"),
        (r'log.*password', "Password in log"),
        (r'console\.log.*password', "Password in console.log"),
        (r'\.debug\s*\([^)]*password', "Password in debug log"),
        (r'response.*password.*:', "Password in response"),
    ]

    # Cryptographic issues
    CRYPTO_PATTERNS = [
        (r'md5\s*\(', "MD5 usage (weak hash)"),
        (r'sha1\s*\(', "SHA1 usage (weak hash)"),
        (r'DES\s*\(', "DES encryption (weak)"),
        (r'random\.random\s*\(', "Insecure random for security"),
        (r'Math\.random\s*\(', "Math.random for security (JS)"),
    ]

    # XSS patterns (stored/reflected)
    XSS_PATTERNS = [
        (r'innerHTML\s*=\s*[^"\']+\+', "innerHTML with dynamic content"),
        (r'document\.write\s*\([^)]*\+', "document.write with concatenation"),
        (r'dangerouslySetInnerHTML', "dangerouslySetInnerHTML usage"),
        (r'render_template_string\s*\([^)]*\+', "render_template_string with concatenation"),
    ]

    # Access control issues
    ACCESS_CONTROL_PATTERNS = [
        (r'@app\.route.*\n(?!.*@login_required)', "Route without authentication decorator"),
        (r'def\s+\w+\s*\([^)]*request[^)]*\)(?!.*permission)', "Handler without permission check"),
    ]

    # Security misconfiguration
    MISCONFIG_PATTERNS = [
        (r'DEBUG\s*=\s*True', "Debug mode enabled"),
        (r'CORS\s*\(\s*\*\s*\)', "CORS allow all origins"),
        (r'Access-Control-Allow-Origin.*\*', "CORS wildcard"),
        (r'ALLOWED_HOSTS\s*=\s*\[\s*[\'\"]\*', "Django ALLOWED_HOSTS wildcard"),
        (r'helmet\s*\(\s*\)', "Helmet without configuration (needs hardening)"),
    ]

    # OWASP Top 10 2021 mapping
    OWASP_MAPPING = {
        "A01": "Broken Access Control",
        "A02": "Cryptographic Failures",
        "A03": "Injection",
        "A04": "Insecure Design",
        "A05": "Security Misconfiguration",
        "A06": "Vulnerable Components",
        "A07": "Auth Failures",
        "A08": "Software Integrity Failures",
        "A09": "Logging Failures",
        "A10": "SSRF"
    }

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.analysis_result = None

    def analyze(self, codebase_path: str) -> SecurityAnalysisResult:
        """Perform complete security analysis."""
        path = Path(codebase_path)
        if not path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")

        # Initialize result
        self.analysis_result = SecurityAnalysisResult(
            overall_score=100,
            risk_level="low"
        )

        # Collect source files
        source_files = (
            list(path.rglob("*.py")) +
            list(path.rglob("*.js")) +
            list(path.rglob("*.ts")) +
            list(path.rglob("*.java")) +
            list(path.rglob("*.go"))
        )

        # Config files for misconfigurations
        config_files = (
            list(path.rglob("*.json")) +
            list(path.rglob("*.yaml")) +
            list(path.rglob("*.yml")) +
            list(path.rglob("*.env")) +
            list(path.rglob("*.ini"))
        )

        # Run all security checks
        self._check_sql_injection(source_files)
        self._check_command_injection(source_files)
        self._check_authentication_issues(source_files + config_files)
        self._check_sensitive_data_exposure(source_files)
        self._check_cryptographic_issues(source_files)
        self._check_xss_vulnerabilities(source_files)
        self._check_access_control(source_files)
        self._check_security_misconfigurations(source_files + config_files)
        self._check_dependency_vulnerabilities(path)

        # Calculate scores and risk level
        self._calculate_scores()

        # Generate recommendations
        self._generate_recommendations()

        return self.analysis_result

    def _check_sql_injection(self, files: list[Path]) -> None:
        """Check for SQL injection vulnerabilities."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern, description in self.SQL_INJECTION_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    line_num = content[:match.start()].count('\n') + 1
                    snippet = self._get_code_snippet(content, line_num)

                    self.analysis_result.issues.append(SecurityIssue(
                        severity=Severity.CRITICAL,
                        category=VulnerabilityCategory.INJECTION,
                        title="SQL Injection Vulnerability",
                        description=description,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=snippet,
                        cwe_id="CWE-89",
                        owasp_category="A03",
                        recommendation="Use parameterized queries or prepared statements"
                    ))

    def _check_command_injection(self, files: list[Path]) -> None:
        """Check for command injection vulnerabilities."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern, description in self.COMMAND_INJECTION_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    line_num = content[:match.start()].count('\n') + 1

                    # eval() might be legitimate in some cases
                    severity = Severity.HIGH if "eval" in pattern else Severity.CRITICAL

                    self.analysis_result.issues.append(SecurityIssue(
                        severity=severity,
                        category=VulnerabilityCategory.INJECTION,
                        title="Command Injection Risk",
                        description=description,
                        file_path=str(file_path),
                        line_number=line_num,
                        cwe_id="CWE-78",
                        owasp_category="A03",
                        recommendation="Use subprocess with array arguments, avoid shell=True"
                    ))

    def _check_authentication_issues(self, files: list[Path]) -> None:
        """Check for authentication vulnerabilities."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern, description in self.AUTH_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    line_num = content[:match.start()].count('\n') + 1

                    severity = Severity.CRITICAL if "secret" in description.lower() or "api_key" in description.lower() else Severity.HIGH

                    self.analysis_result.issues.append(SecurityIssue(
                        severity=severity,
                        category=VulnerabilityCategory.BROKEN_AUTH,
                        title="Authentication Vulnerability",
                        description=description,
                        file_path=str(file_path),
                        line_number=line_num,
                        cwe_id="CWE-798",
                        owasp_category="A07",
                        recommendation="Use environment variables for secrets, enable verification"
                    ))

    def _check_sensitive_data_exposure(self, files: list[Path]) -> None:
        """Check for sensitive data exposure."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern, description in self.SENSITIVE_DATA_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    line_num = content[:match.start()].count('\n') + 1

                    self.analysis_result.issues.append(SecurityIssue(
                        severity=Severity.HIGH,
                        category=VulnerabilityCategory.SENSITIVE_DATA,
                        title="Sensitive Data Exposure",
                        description=description,
                        file_path=str(file_path),
                        line_number=line_num,
                        cwe_id="CWE-532",
                        owasp_category="A02",
                        recommendation="Remove sensitive data from logs and responses"
                    ))

    def _check_cryptographic_issues(self, files: list[Path]) -> None:
        """Check for cryptographic vulnerabilities."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern, description in self.CRYPTO_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content[:match.start()].count('\n') + 1

                    # Check context - MD5/SHA1 for checksums is less severe
                    context = content[max(0, match.start()-100):match.end()+100]
                    severity = Severity.MEDIUM if "checksum" in context.lower() or "hash" in context.lower() else Severity.HIGH

                    self.analysis_result.issues.append(SecurityIssue(
                        severity=severity,
                        category=VulnerabilityCategory.CRYPTOGRAPHY,
                        title="Weak Cryptography",
                        description=description,
                        file_path=str(file_path),
                        line_number=line_num,
                        cwe_id="CWE-327",
                        owasp_category="A02",
                        recommendation="Use strong algorithms: SHA-256+, bcrypt/argon2 for passwords"
                    ))

    def _check_xss_vulnerabilities(self, files: list[Path]) -> None:
        """Check for XSS vulnerabilities."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern, description in self.XSS_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content[:match.start()].count('\n') + 1

                    self.analysis_result.issues.append(SecurityIssue(
                        severity=Severity.HIGH,
                        category=VulnerabilityCategory.XSS,
                        title="Cross-Site Scripting Risk",
                        description=description,
                        file_path=str(file_path),
                        line_number=line_num,
                        cwe_id="CWE-79",
                        owasp_category="A03",
                        recommendation="Sanitize and encode user input before rendering"
                    ))

    def _check_access_control(self, files: list[Path]) -> None:
        """Check for access control issues."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            # Check for routes without authentication
            route_pattern = r'@(?:app\.)?(?:route|get|post|put|delete)\s*\(\s*["\'][^"\']+["\']\s*\)'
            auth_decorators = ['login_required', 'authenticated', 'auth_required', 'requires_auth', 'jwt_required']

            for match in re.finditer(route_pattern, content):
                route_line = content[:match.start()].count('\n')
                # Check surrounding lines for auth decorator
                context_start = max(0, match.start() - 200)
                context = content[context_start:match.start()]

                has_auth = any(auth in context for auth in auth_decorators)

                if not has_auth:
                    self.analysis_result.issues.append(SecurityIssue(
                        severity=Severity.MEDIUM,
                        category=VulnerabilityCategory.BROKEN_ACCESS,
                        title="Potentially Unprotected Endpoint",
                        description="Route may lack authentication",
                        file_path=str(file_path),
                        line_number=route_line,
                        cwe_id="CWE-862",
                        owasp_category="A01",
                        recommendation="Verify if endpoint requires authentication"
                    ))

    def _check_security_misconfigurations(self, files: list[Path]) -> None:
        """Check for security misconfigurations."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern, description in self.MISCONFIG_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content[:match.start()].count('\n') + 1

                    # Debug mode in production is critical
                    severity = Severity.HIGH if "DEBUG" in description else Severity.MEDIUM

                    self.analysis_result.issues.append(SecurityIssue(
                        severity=severity,
                        category=VulnerabilityCategory.SECURITY_MISCONFIG,
                        title="Security Misconfiguration",
                        description=description,
                        file_path=str(file_path),
                        line_number=line_num,
                        cwe_id="CWE-16",
                        owasp_category="A05",
                        recommendation="Review and harden security configurations for production"
                    ))

    def _check_dependency_vulnerabilities(self, codebase_path: Path) -> None:
        """Check for known vulnerable dependencies."""
        # Look for dependency files
        dep_files = {
            "requirements.txt": "python",
            "package.json": "javascript",
            "Pipfile": "python",
            "poetry.lock": "python",
            "package-lock.json": "javascript",
            "go.mod": "go"
        }

        for dep_file, lang in dep_files.items():
            dep_path = codebase_path / dep_file
            if dep_path.exists():
                self.analysis_result.recommendations.append(SecurityIssue(
                    severity=Severity.INFO,
                    category=VulnerabilityCategory.VULNERABLE_COMPONENTS,
                    title="Dependency Audit Recommended",
                    description=f"Found {dep_file} - run security audit",
                    file_path=str(dep_path),
                    cwe_id="CWE-1104",
                    owasp_category="A06",
                    recommendation=self._get_audit_command(lang)
                ))

    def _get_audit_command(self, language: str) -> str:
        """Get the appropriate security audit command for a language."""
        commands = {
            "python": "Run 'pip-audit' or 'safety check'",
            "javascript": "Run 'npm audit' or 'yarn audit'",
            "go": "Run 'govulncheck ./...'"
        }
        return commands.get(language, "Run dependency security audit")

    def _get_code_snippet(self, content: str, line_num: int, context: int = 2) -> str:
        """Extract code snippet around a line number."""
        lines = content.split('\n')
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        return '\n'.join(lines[start:end])

    def _calculate_scores(self) -> None:
        """Calculate security scores and risk level."""
        score = 100

        severity_weights = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 8,
            Severity.LOW: 3,
            Severity.INFO: 0
        }

        for issue in self.analysis_result.issues:
            score -= severity_weights.get(issue.severity, 0)

        self.analysis_result.overall_score = max(0, min(100, score))

        # Determine risk level
        critical_count = sum(1 for i in self.analysis_result.issues if i.severity == Severity.CRITICAL)
        high_count = sum(1 for i in self.analysis_result.issues if i.severity == Severity.HIGH)

        if critical_count > 0:
            self.analysis_result.risk_level = "critical"
        elif high_count > 2:
            self.analysis_result.risk_level = "high"
        elif high_count > 0 or score < 70:
            self.analysis_result.risk_level = "medium"
        else:
            self.analysis_result.risk_level = "low"

        # Calculate OWASP coverage
        owasp_issues: dict[str, list] = {}
        for issue in self.analysis_result.issues:
            if issue.owasp_category:
                if issue.owasp_category not in owasp_issues:
                    owasp_issues[issue.owasp_category] = []
                owasp_issues[issue.owasp_category].append(issue)

        for code, name in self.OWASP_MAPPING.items():
            issues_count = len(owasp_issues.get(code, []))
            if issues_count == 0:
                status = "good"
            elif issues_count <= 2:
                status = "needs_attention"
            else:
                status = "critical"
            self.analysis_result.owasp_coverage[code] = {
                "name": name,
                "status": status,
                "issues_count": issues_count
            }

        # Update stats
        self.analysis_result.stats = {
            "total_issues": len(self.analysis_result.issues),
            "critical_issues": critical_count,
            "high_issues": high_count,
            "medium_issues": sum(1 for i in self.analysis_result.issues if i.severity == Severity.MEDIUM),
            "low_issues": sum(1 for i in self.analysis_result.issues if i.severity == Severity.LOW)
        }

    def _generate_recommendations(self) -> None:
        """Generate security recommendations."""
        # Check if certain security measures are missing
        has_rate_limiting = False
        has_logging = False
        has_input_validation = False

        # These would be detected during analysis
        if self.analysis_result.stats.get("total_issues", 0) > 5:
            self.analysis_result.recommendations.append(SecurityIssue(
                severity=Severity.HIGH,
                category=VulnerabilityCategory.SECURITY_MISCONFIG,
                title="Security Review Needed",
                description="Multiple security issues detected - comprehensive review recommended",
                file_path="",
                recommendation="Conduct a thorough security audit and implement security best practices"
            ))

    def get_summary(self) -> dict:
        """Get security analysis summary."""
        if not self.analysis_result:
            return {}

        return {
            "overall_score": self.analysis_result.overall_score,
            "risk_level": self.analysis_result.risk_level,
            "stats": self.analysis_result.stats,
            "owasp_coverage": self.analysis_result.owasp_coverage,
            "recommendations_count": len(self.analysis_result.recommendations)
        }

    def generate_security_report(self) -> str:
        """Generate a formatted security report."""
        if not self.analysis_result:
            return "No analysis performed"

        report = []
        report.append("# Security Analysis Report\n")
        report.append(f"**Overall Score**: {self.analysis_result.overall_score}/100")
        report.append(f"**Risk Level**: {self.analysis_result.risk_level.upper()}\n")

        # Issues by severity
        report.append("## Issues by Severity\n")
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            issues = [i for i in self.analysis_result.issues if i.severity == severity]
            if issues:
                report.append(f"### {severity.value.upper()} ({len(issues)})\n")
                for issue in issues:
                    report.append(f"- **{issue.title}** ({issue.file_path}:{issue.line_number})")
                    report.append(f"  - {issue.description}")
                    report.append(f"  - Recommendation: {issue.recommendation}\n")

        # OWASP Coverage
        report.append("## OWASP Top 10 Coverage\n")
        for code, info in self.analysis_result.owasp_coverage.items():
            status_emoji = {"good": "OK", "needs_attention": "WARN", "critical": "CRIT"}
            report.append(f"- {code}: {info['name']} - [{status_emoji[info['status']]}]")

        return "\n".join(report)


def analyze_security(codebase_path: str, config: Optional[dict] = None) -> dict:
    """Convenience function to analyze security and return summary."""
    analyzer = SecurityAnalyzer(config)
    result = analyzer.analyze(codebase_path)
    return {
        "result": result,
        "summary": analyzer.get_summary(),
        "report": analyzer.generate_security_report()
    }
