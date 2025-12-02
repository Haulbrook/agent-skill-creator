#!/usr/bin/env python3
"""
GitHub Profile Reviewer - Main Entry Point

Professional GitHub profile audit through the lens of recruiters and hiring managers.
This tool reviews profiles, repositories, links, security, and provides cleanup recommendations.

CRITICAL: This tool maintains strict user protection protocols:
- NEVER deletes without explicit dual confirmation
- Prioritizes security scanning first
- Maintains allegiance to user's interests
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.profile_analyzer import ProfileAnalyzer
from analyzers.repo_analyzer import RepositoryAnalyzer
from validators.link_validator import LinkValidator
from validators.security_scanner import SecurityScanner
from reporters.report_generator import ReportGenerator


@dataclass
class ReviewConfig:
    """Configuration for the profile review."""
    username: str
    include_security_scan: bool = True
    include_link_verification: bool = True
    include_cleanup_recommendations: bool = True
    include_naming_review: bool = True
    verbose: bool = False
    output_format: str = "markdown"  # markdown, json, html
    output_file: Optional[str] = None
    github_token: Optional[str] = None  # For higher rate limits


@dataclass
class ReviewResults:
    """Container for all review results."""
    username: str
    review_date: str
    profile_assessment: Dict[str, Any] = field(default_factory=dict)
    repository_analysis: List[Dict[str, Any]] = field(default_factory=list)
    security_findings: Dict[str, Any] = field(default_factory=dict)
    link_audit: Dict[str, Any] = field(default_factory=dict)
    cleanup_recommendations: Dict[str, Any] = field(default_factory=dict)
    naming_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    overall_score: int = 0
    priority_actions: List[str] = field(default_factory=list)


class GitHubProfileReviewer:
    """
    Main orchestrator for GitHub profile reviews.

    This class coordinates all analysis components and ensures
    the protection protocol is followed throughout the review.
    """

    def __init__(self, config: ReviewConfig):
        self.config = config
        self.results = ReviewResults(
            username=config.username,
            review_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Initialize analyzers
        self.profile_analyzer = ProfileAnalyzer(config.github_token)
        self.repo_analyzer = RepositoryAnalyzer(config.github_token)
        self.link_validator = LinkValidator()
        self.security_scanner = SecurityScanner(config.github_token)
        self.report_generator = ReportGenerator()

    def run_review(self) -> ReviewResults:
        """
        Execute the full profile review.

        Order of operations:
        1. Security scan FIRST (critical priority)
        2. Profile overview analysis
        3. Repository deep dive
        4. Link verification
        5. Cleanup recommendations
        6. Report generation
        """
        print(f"\n{'='*60}")
        print(f"  GitHub Profile Review: {self.config.username}")
        print(f"  Started: {self.results.review_date}")
        print(f"{'='*60}\n")

        # Phase 1: Security Scan (ALWAYS FIRST)
        if self.config.include_security_scan:
            self._run_security_scan()

        # Phase 2: Profile Analysis
        self._run_profile_analysis()

        # Phase 3: Repository Analysis
        self._run_repository_analysis()

        # Phase 4: Link Verification
        if self.config.include_link_verification:
            self._run_link_verification()

        # Phase 5: Cleanup Recommendations
        if self.config.include_cleanup_recommendations:
            self._generate_cleanup_recommendations()

        # Phase 6: Naming Review
        if self.config.include_naming_review:
            self._run_naming_review()

        # Calculate overall score
        self._calculate_overall_score()

        # Generate priority actions
        self._generate_priority_actions()

        return self.results

    def _run_security_scan(self):
        """
        Run security scan FIRST - highest priority.

        This scans for:
        - Exposed credentials
        - API keys and tokens
        - Sensitive data
        - Vulnerable dependencies
        """
        print("[1/6] Running Security Scan (PRIORITY)...")
        print("      Scanning for exposed credentials and sensitive data...")

        try:
            findings = self.security_scanner.scan_profile(self.config.username)
            self.results.security_findings = findings

            # Alert immediately if critical findings
            if findings.get('critical_findings'):
                self._alert_security_issues(findings['critical_findings'])

            print(f"      Security scan complete.")
            if findings.get('issues_found', 0) > 0:
                print(f"      !! {findings['issues_found']} potential issues found")
            else:
                print(f"      No security issues detected")

        except Exception as e:
            print(f"      Error during security scan: {e}")
            self.results.security_findings = {'error': str(e)}

    def _alert_security_issues(self, findings: List[Dict]):
        """Display immediate security alerts."""
        print("\n" + "="*60)
        print("!!!  SECURITY ALERT - IMMEDIATE ACTION REQUIRED  !!!")
        print("="*60)

        for finding in findings:
            print(f"\nTYPE: {finding.get('type', 'Unknown')}")
            print(f"SEVERITY: {finding.get('severity', 'Unknown')}")
            print(f"LOCATION: {finding.get('location', 'Unknown')}")
            print(f"DESCRIPTION: {finding.get('description', 'No description')}")
            print(f"RECOMMENDATION: {finding.get('recommendation', 'Review immediately')}")

        print("\n" + "="*60)
        print("Please address these issues before continuing.")
        print("="*60 + "\n")

    def _run_profile_analysis(self):
        """Analyze the GitHub profile overview."""
        print("\n[2/6] Analyzing Profile Overview...")

        try:
            assessment = self.profile_analyzer.analyze(self.config.username)
            self.results.profile_assessment = assessment
            print(f"      Profile analysis complete.")
            print(f"      First Impression Score: {assessment.get('first_impression_score', 'N/A')}/40")

        except Exception as e:
            print(f"      Error during profile analysis: {e}")
            self.results.profile_assessment = {'error': str(e)}

    def _run_repository_analysis(self):
        """Deep dive into each repository."""
        print("\n[3/6] Analyzing Repositories...")

        try:
            repos = self.repo_analyzer.analyze_all_repos(self.config.username)
            self.results.repository_analysis = repos
            print(f"      Analyzed {len(repos)} repositories.")

            # Summary statistics
            categories = {}
            for repo in repos:
                cat = repo.get('classification', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1

            print(f"      Categories: {categories}")

        except Exception as e:
            print(f"      Error during repository analysis: {e}")
            self.results.repository_analysis = []

    def _run_link_verification(self):
        """Verify all links in profile and repositories."""
        print("\n[4/6] Verifying Links...")

        try:
            # Collect all links from profile and repos
            all_links = self._collect_all_links()

            if all_links:
                audit_results = self.link_validator.verify_links(all_links)
                self.results.link_audit = audit_results

                working = audit_results.get('working', [])
                broken = audit_results.get('broken', [])
                print(f"      Verified {len(all_links)} links.")
                print(f"      Working: {len(working)}, Broken: {len(broken)}")
            else:
                print(f"      No links found to verify.")
                self.results.link_audit = {'links_checked': 0}

        except Exception as e:
            print(f"      Error during link verification: {e}")
            self.results.link_audit = {'error': str(e)}

    def _collect_all_links(self) -> List[Dict[str, str]]:
        """Collect all links from profile and repositories."""
        links = []

        # Profile links
        profile = self.results.profile_assessment
        if profile.get('website_url'):
            links.append({
                'url': profile['website_url'],
                'source': 'Profile',
                'context': 'Website URL'
            })

        # Repository links
        for repo in self.results.repository_analysis:
            repo_links = repo.get('links', [])
            for link in repo_links:
                link['source'] = f"Repository: {repo.get('name', 'Unknown')}"
                links.append(link)

        return links

    def _generate_cleanup_recommendations(self):
        """Generate cleanup recommendations based on analysis."""
        print("\n[5/6] Generating Cleanup Recommendations...")

        recommendations = {
            'removal_candidates': [],
            'privatization_candidates': [],
            'archive_candidates': [],
            'improvement_candidates': []
        }

        for repo in self.results.repository_analysis:
            classification = repo.get('classification', '')
            repo_info = {
                'name': repo.get('name'),
                'reason': repo.get('classification_reason', ''),
                'last_activity': repo.get('last_commit_date', 'Unknown'),
                'stars': repo.get('stars', 0),
                'forks': repo.get('forks', 0)
            }

            if classification in ['Abandoned', 'Duplicate', 'Learning']:
                recommendations['removal_candidates'].append(repo_info)
            elif classification == 'Experimental':
                recommendations['privatization_candidates'].append(repo_info)
            elif classification == 'Archive':
                recommendations['archive_candidates'].append(repo_info)
            elif classification == 'Active' and repo.get('needs_improvement'):
                repo_info['improvements_needed'] = repo.get('improvements_needed', [])
                recommendations['improvement_candidates'].append(repo_info)

        self.results.cleanup_recommendations = recommendations

        total = sum(len(v) for v in recommendations.values())
        print(f"      Generated {total} recommendations.")
        print(f"      - Removal candidates: {len(recommendations['removal_candidates'])}")
        print(f"      - Privatization candidates: {len(recommendations['privatization_candidates'])}")
        print(f"      - Archive candidates: {len(recommendations['archive_candidates'])}")
        print(f"      - Improvement candidates: {len(recommendations['improvement_candidates'])}")

    def _run_naming_review(self):
        """Review repository naming for clarity."""
        print("\n[6/6] Reviewing Repository Names...")

        naming_suggestions = []

        for repo in self.results.repository_analysis:
            name = repo.get('name', '')
            clarity_score = repo.get('name_clarity_score', 5)

            if clarity_score < 4:
                suggestion = {
                    'current_name': name,
                    'clarity_score': clarity_score,
                    'issues': repo.get('naming_issues', []),
                    'suggested_name': repo.get('suggested_name'),
                    'rationale': repo.get('naming_rationale', '')
                }
                naming_suggestions.append(suggestion)

        self.results.naming_suggestions = naming_suggestions
        print(f"      Found {len(naming_suggestions)} naming improvements suggested.")

    def _calculate_overall_score(self):
        """Calculate the overall professional score."""
        score = 0

        # Profile completeness (25 points)
        profile = self.results.profile_assessment
        score += profile.get('first_impression_score', 0) * (25/40)  # Scale to 25

        # Repository quality (25 points)
        repos = self.results.repository_analysis
        if repos:
            avg_quality = sum(r.get('quality_score', 0) for r in repos) / len(repos)
            score += avg_quality * 5  # Scale to 25

        # Documentation (20 points)
        if repos:
            docs_score = sum(1 for r in repos if r.get('has_readme', False)) / len(repos)
            score += docs_score * 20

        # Security (15 points)
        security = self.results.security_findings
        if not security.get('issues_found', 0):
            score += 15
        else:
            severity_penalty = security.get('severity_score', 0)
            score += max(0, 15 - severity_penalty)

        # Professional polish (15 points)
        if not self.results.naming_suggestions:
            score += 10
        else:
            score += max(0, 10 - len(self.results.naming_suggestions))

        links = self.results.link_audit
        if links.get('broken', []):
            score -= len(links['broken']) * 0.5
        else:
            score += 5

        self.results.overall_score = max(0, min(100, int(score)))

    def _generate_priority_actions(self):
        """Generate prioritized action list."""
        actions = []

        # Critical: Security issues
        security = self.results.security_findings
        if security.get('critical_findings'):
            for finding in security['critical_findings']:
                actions.append(f"[CRITICAL] Fix security issue: {finding.get('description', 'Unknown')}")

        # High: Broken links
        links = self.results.link_audit
        for broken in links.get('broken', [])[:3]:  # Top 3
            actions.append(f"[HIGH] Fix broken link in {broken.get('source', 'Unknown')}")

        # Medium: Cleanup recommendations
        cleanup = self.results.cleanup_recommendations
        if cleanup.get('removal_candidates'):
            actions.append(f"[MEDIUM] Review {len(cleanup['removal_candidates'])} repos for potential removal")

        # Low: Naming improvements
        if self.results.naming_suggestions:
            actions.append(f"[LOW] Consider renaming {len(self.results.naming_suggestions)} repos for clarity")

        self.results.priority_actions = actions

    def generate_report(self) -> str:
        """Generate the final report."""
        return self.report_generator.generate(
            self.results,
            format=self.config.output_format
        )

    def save_report(self, filepath: str):
        """Save the report to a file."""
        report = self.generate_report()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {filepath}")


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='GitHub Profile Reviewer - Professional Assessment Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py username123
  python main.py username123 --output report.md
  python main.py username123 --format json --verbose
  python main.py username123 --token YOUR_GITHUB_TOKEN
        """
    )

    parser.add_argument('username', help='GitHub username to review')
    parser.add_argument('--token', '-t', help='GitHub personal access token for higher rate limits')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'html'],
                       default='markdown', help='Output format (default: markdown)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-security', action='store_true', help='Skip security scan')
    parser.add_argument('--no-links', action='store_true', help='Skip link verification')
    parser.add_argument('--no-cleanup', action='store_true', help='Skip cleanup recommendations')
    parser.add_argument('--no-naming', action='store_true', help='Skip naming review')

    args = parser.parse_args()

    # Build configuration
    config = ReviewConfig(
        username=args.username,
        include_security_scan=not args.no_security,
        include_link_verification=not args.no_links,
        include_cleanup_recommendations=not args.no_cleanup,
        include_naming_review=not args.no_naming,
        verbose=args.verbose,
        output_format=args.format,
        output_file=args.output,
        github_token=args.token or os.environ.get('GITHUB_TOKEN')
    )

    # Run review
    reviewer = GitHubProfileReviewer(config)
    results = reviewer.run_review()

    # Generate and output report
    report = reviewer.generate_report()

    if args.output:
        reviewer.save_report(args.output)
    else:
        print("\n" + "="*60)
        print("  PROFILE REVIEW REPORT")
        print("="*60 + "\n")
        print(report)

    return results


if __name__ == '__main__':
    main()
