"""
Report Generator - Professional Assessment Reports

Generates comprehensive, actionable reports from profile review results
in various formats (Markdown, JSON, HTML).
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime


class ReportGenerator:
    """
    Generate professional GitHub profile assessment reports.

    Supports multiple output formats:
    - Markdown (default): Human-readable, GitHub-compatible
    - JSON: Machine-readable, API-friendly
    - HTML: Web-ready presentation
    """

    def generate(self, results, format: str = 'markdown') -> str:
        """
        Generate report in specified format.

        Args:
            results: ReviewResults object or dict
            format: Output format ('markdown', 'json', 'html')

        Returns:
            Formatted report string
        """
        # Convert to dict if needed
        if hasattr(results, '__dict__'):
            data = self._results_to_dict(results)
        else:
            data = results

        if format == 'json':
            return self._generate_json(data)
        elif format == 'html':
            return self._generate_html(data)
        else:
            return self._generate_markdown(data)

    def _results_to_dict(self, results) -> Dict[str, Any]:
        """Convert ReviewResults to dictionary."""
        return {
            'username': results.username,
            'review_date': results.review_date,
            'profile_assessment': results.profile_assessment,
            'repository_analysis': results.repository_analysis,
            'security_findings': results.security_findings,
            'link_audit': results.link_audit,
            'cleanup_recommendations': results.cleanup_recommendations,
            'naming_suggestions': results.naming_suggestions,
            'overall_score': results.overall_score,
            'priority_actions': results.priority_actions
        }

    def _generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generate Markdown report."""
        lines = []

        # Header
        lines.append(f"# GitHub Profile Professional Assessment")
        lines.append(f"## {data.get('username', 'Unknown')} - {data.get('review_date', 'N/A')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"**Overall Professional Score: {data.get('overall_score', 0)}/100**")
        lines.append("")

        # Score breakdown
        lines.append("| Category | Assessment |")
        lines.append("|----------|------------|")

        profile = data.get('profile_assessment', {})
        first_impression = profile.get('first_impression_score', 0)
        lines.append(f"| First Impression | {first_impression}/40 |")

        repos = data.get('repository_analysis', [])
        if repos:
            avg_quality = sum(r.get('quality_score', 0) for r in repos) / len(repos)
            lines.append(f"| Repository Quality | {avg_quality:.1f}/5 |")
            lines.append(f"| Total Repositories | {len(repos)} |")

        security = data.get('security_findings', {})
        security_issues = security.get('issues_found', 0)
        security_status = " No Issues" if security_issues == 0 else f" {security_issues} Issues Found"
        lines.append(f"| Security Posture | {security_status} |")

        links = data.get('link_audit', {})
        broken_links = len(links.get('broken', []))
        links_status = " All Working" if broken_links == 0 else f" {broken_links} Broken"
        lines.append(f"| Link Health | {links_status} |")

        lines.append("")

        # Priority Actions
        actions = data.get('priority_actions', [])
        if actions:
            lines.append("### Priority Actions")
            lines.append("")
            for action in actions:
                lines.append(f"- {action}")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Security Section (if issues found)
        if security.get('issues_found', 0) > 0:
            lines.append("## SECURITY ALERTS")
            lines.append("")
            lines.append("> **WARNING**: Security issues detected. Address these immediately.")
            lines.append("")

            for finding in security.get('critical_findings', []):
                lines.append(f"###  CRITICAL: {finding.get('description', 'Unknown')}")
                lines.append(f"- **Location**: {finding.get('location', 'Unknown')}")
                lines.append(f"- **Recommendation**: {finding.get('recommendation', 'Review immediately')}")
                lines.append("")

            for finding in security.get('high_findings', []):
                lines.append(f"###  HIGH: {finding.get('description', 'Unknown')}")
                lines.append(f"- **Location**: {finding.get('location', 'Unknown')}")
                lines.append(f"- **Recommendation**: {finding.get('recommendation', 'Review soon')}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Profile Assessment
        lines.append("## Profile Overview")
        lines.append("")

        if profile:
            elements = profile.get('elements', {})

            lines.append("| Element | Status | Score | Notes |")
            lines.append("|---------|--------|-------|-------|")

            element_order = ['photo', 'name', 'bio', 'website', 'readme', 'location', 'company', 'email']
            for elem_name in element_order:
                elem = elements.get(elem_name)
                if elem:
                    status = "" if elem.present else ""
                    issues = "; ".join(elem.issues) if elem.issues else "Good"
                    lines.append(f"| {elem.name} | {status} | {elem.score}/10 | {issues} |")

            lines.append("")

            # Strengths and weaknesses
            strengths = profile.get('strengths', [])
            if strengths:
                lines.append("### Strengths")
                for s in strengths:
                    lines.append(f"-  {s}")
                lines.append("")

            weaknesses = profile.get('weaknesses', [])
            if weaknesses:
                lines.append("### Areas for Improvement")
                for w in weaknesses:
                    lines.append(f"-  {w}")
                lines.append("")

            # Profile recommendations
            recommendations = profile.get('recommendations', [])
            if recommendations:
                lines.append("### Recommendations")
                for rec in recommendations[:5]:  # Top 5
                    impact = rec.get('impact', 'MEDIUM')
                    icon = "" if impact == 'HIGH' else "" if impact == 'MEDIUM' else ""
                    lines.append(f"- {icon} [{impact}] {rec.get('recommendation', '')}")
                lines.append("")

        lines.append("---")
        lines.append("")

        # Repository Analysis
        lines.append("## Repository Analysis")
        lines.append("")

        if repos:
            # Summary by classification
            classifications = {}
            for repo in repos:
                cls = repo.get('classification', 'Unknown')
                classifications[cls] = classifications.get(cls, 0) + 1

            lines.append("### Repository Classification Summary")
            lines.append("")
            lines.append("| Category | Count |")
            lines.append("|----------|-------|")
            for cls, count in sorted(classifications.items()):
                lines.append(f"| {cls} | {count} |")
            lines.append("")

            # Top repositories (Showcase)
            showcase = [r for r in repos if r.get('classification') == 'Showcase']
            if showcase:
                lines.append("### Showcase Repositories")
                lines.append("")
                for repo in showcase[:5]:
                    lines.append(f"**[{repo.get('name', 'Unknown')}]({repo.get('url', '#')})**")
                    lines.append(f"- {repo.get('description', 'No description')}")
                    lines.append(f"-  {repo.get('stars', 0)} |  {repo.get('forks', 0)} | Quality: {repo.get('quality_score', 0)}/5")
                    lines.append("")

            # Repositories needing attention
            needs_work = [r for r in repos if r.get('needs_improvement')]
            if needs_work:
                lines.append("### Repositories Needing Improvement")
                lines.append("")
                for repo in needs_work[:5]:
                    lines.append(f"**{repo.get('name', 'Unknown')}**")
                    for improvement in repo.get('improvements_needed', []):
                        lines.append(f"  -  {improvement}")
                    lines.append("")

        lines.append("---")
        lines.append("")

        # Link Audit
        lines.append("## Link Audit Results")
        lines.append("")

        if links:
            summary = links.get('summary', {})
            lines.append(f"- Total links checked: {summary.get('total', 0)}")
            lines.append(f"- Working: {summary.get('working', 0)}")
            lines.append(f"- Broken: {summary.get('broken', 0)}")
            lines.append(f"- Warnings: {summary.get('warnings', 0)}")
            lines.append("")

            broken = links.get('broken', [])
            if broken:
                lines.append("### Broken Links (Action Required)")
                lines.append("")
                for link in broken:
                    lines.append(f"- **{link.get('url', 'Unknown')}**")
                    lines.append(f"  - Source: {link.get('source', 'Unknown')}")
                    lines.append(f"  - Issue: {'; '.join(link.get('issues', ['Unknown']))}")
                    lines.append(f"  - Recommendation: {link.get('recommendation', 'Fix or remove')}")
                    lines.append("")

        lines.append("---")
        lines.append("")

        # Cleanup Recommendations
        lines.append("## Cleanup Recommendations")
        lines.append("")
        lines.append("> **IMPORTANT**: No action will be taken without your explicit confirmation.")
        lines.append("> Each cleanup action requires TWO confirmations before proceeding.")
        lines.append("")

        cleanup = data.get('cleanup_recommendations', {})

        removal = cleanup.get('removal_candidates', [])
        if removal:
            lines.append("### Removal Candidates")
            lines.append("")
            for repo in removal:
                lines.append(f"- **{repo.get('name', 'Unknown')}**")
                lines.append(f"  - Reason: {repo.get('reason', 'N/A')}")
                lines.append(f"  - Last activity: {repo.get('last_activity', 'Unknown')}")
                lines.append("")

        privatize = cleanup.get('privatization_candidates', [])
        if privatize:
            lines.append("### Consider Making Private")
            lines.append("")
            for repo in privatize:
                lines.append(f"- **{repo.get('name', 'Unknown')}**: {repo.get('reason', 'N/A')}")
            lines.append("")

        archive = cleanup.get('archive_candidates', [])
        if archive:
            lines.append("### Consider Archiving")
            lines.append("")
            for repo in archive:
                lines.append(f"- **{repo.get('name', 'Unknown')}**: {repo.get('reason', 'N/A')}")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Naming Suggestions
        naming = data.get('naming_suggestions', [])
        if naming:
            lines.append("## Naming Improvements")
            lines.append("")
            lines.append("| Current Name | Suggested Name | Clarity Score | Issues |")
            lines.append("|--------------|----------------|---------------|--------|")
            for suggestion in naming:
                current = suggestion.get('current_name', 'Unknown')
                suggested = suggestion.get('suggested_name', 'N/A')
                score = suggestion.get('clarity_score', 0)
                issues = "; ".join(suggestion.get('issues', []))
                lines.append(f"| {current} | {suggested} | {score}/5 | {issues} |")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Footer
        lines.append("## Next Steps")
        lines.append("")
        lines.append("1. Address any security issues immediately")
        lines.append("2. Fix broken links")
        lines.append("3. Review cleanup recommendations")
        lines.append("4. Improve profile elements as suggested")
        lines.append("5. Consider renaming repositories for clarity")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by GitHub Profile Reviewer*")
        lines.append(f"*Your data security is our priority - no changes were made without your consent.*")

        return "\n".join(lines)

    def _generate_json(self, data: Dict[str, Any]) -> str:
        """Generate JSON report."""
        # Clean up non-serializable objects
        clean_data = self._clean_for_json(data)
        return json.dumps(clean_data, indent=2, default=str)

    def _clean_for_json(self, obj):
        """Recursively clean object for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_for_json(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._clean_for_json(obj.__dict__)
        else:
            return obj

    def _generate_html(self, data: Dict[str, Any]) -> str:
        """Generate HTML report."""
        # Convert markdown to basic HTML
        md_report = self._generate_markdown(data)

        html_lines = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "  <meta charset='UTF-8'>",
            "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"  <title>GitHub Profile Review - {data.get('username', 'Unknown')}</title>",
            "  <style>",
            "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; }",
            "    h1, h2, h3 { color: #24292e; }",
            "    table { border-collapse: collapse; width: 100%; margin: 1em 0; }",
            "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "    th { background-color: #f6f8fa; }",
            "    blockquote { border-left: 4px solid #0366d6; padding-left: 1em; color: #586069; }",
            "    code { background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; }",
            "    .critical { color: #cb2431; font-weight: bold; }",
            "    .high { color: #e36209; }",
            "    .score { font-size: 2em; color: #0366d6; }",
            "  </style>",
            "</head>",
            "<body>",
        ]

        # Simple markdown to HTML conversion
        in_table = False
        in_list = False

        for line in md_report.split('\n'):
            # Headers
            if line.startswith('# '):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith('## '):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith('### '):
                html_lines.append(f"<h3>{line[4:]}</h3>")
            # Horizontal rule
            elif line == '---':
                html_lines.append("<hr>")
            # Blockquote
            elif line.startswith('> '):
                html_lines.append(f"<blockquote>{line[2:]}</blockquote>")
            # Table
            elif line.startswith('|'):
                if not in_table:
                    html_lines.append("<table>")
                    in_table = True
                if '|---|' in line or '|---|' in line.replace(' ', ''):
                    continue
                cells = [c.strip() for c in line.split('|')[1:-1]]
                tag = 'th' if html_lines[-1] == "<table>" else 'td'
                html_lines.append(f"<tr>{''.join(f'<{tag}>{c}</{tag}>' for c in cells)}</tr>")
            elif in_table:
                html_lines.append("</table>")
                in_table = False
            # List
            elif line.startswith('- '):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                html_lines.append(f"<li>{line[2:]}</li>")
            elif in_list and not line.startswith('- ') and not line.startswith('  -'):
                html_lines.append("</ul>")
                in_list = False
                if line.strip():
                    html_lines.append(f"<p>{line}</p>")
            # Bold
            elif '**' in line:
                line = line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
                html_lines.append(f"<p>{line}</p>")
            # Regular paragraph
            elif line.strip():
                html_lines.append(f"<p>{line}</p>")

        if in_table:
            html_lines.append("</table>")
        if in_list:
            html_lines.append("</ul>")

        html_lines.extend([
            "</body>",
            "</html>"
        ])

        return "\n".join(html_lines)
