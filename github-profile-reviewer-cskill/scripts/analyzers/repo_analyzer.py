"""
Repository Analyzer - Deep Repository Assessment

Analyzes all repositories in a GitHub profile, evaluating quality,
activity, documentation, naming, and professional value.
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

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
class RepositoryAssessment:
    """Complete repository assessment."""
    name: str
    url: str
    description: Optional[str]
    classification: str
    classification_reason: str
    quality_score: int  # 0-5
    name_clarity_score: int  # 1-5
    naming_issues: List[str]
    suggested_name: Optional[str]
    naming_rationale: str
    has_readme: bool
    readme_quality: int  # 0-5
    last_commit_date: Optional[str]
    days_since_commit: int
    stars: int
    forks: int
    is_fork: bool
    is_archived: bool
    language: Optional[str]
    topics: List[str]
    links: List[Dict[str, str]]
    needs_improvement: bool
    improvements_needed: List[str]


class RepositoryAnalyzer:
    """
    Deep analysis of GitHub repositories.

    Classification Categories:
    - Showcase: Best work, highlight-worthy
    - Active: Currently maintained
    - Archive: Valuable but inactive
    - Learning: Tutorial/course artifacts
    - Experimental: Tests/experiments
    - Duplicate: Same as another repo
    - Abandoned: No activity, no interest
    - Security Risk: Contains sensitive data (flagged separately)
    """

    # Generic/unclear name patterns
    UNCLEAR_NAME_PATTERNS = [
        r'^test\d*$',
        r'^project\d*$',
        r'^untitled',
        r'^my-?app',
        r'^my-?project',
        r'^my-?website',
        r'^my-?portfolio',
        r'^new-?repo',
        r'^sample',
        r'^demo\d*$',
        r'^example\d*$',
        r'^temp',
        r'^tmp',
        r'^foo',
        r'^bar',
        r'^asdf',
        r'^hello-?world',
        r'^first-?repo',
        r'^learning',
    ]

    # Tutorial/course artifact patterns
    TUTORIAL_PATTERNS = [
        r'freecodecamp',
        r'udemy',
        r'coursera',
        r'udacity',
        r'codecademy',
        r'tutorial',
        r'exercise',
        r'homework',
        r'assignment',
        r'bootcamp',
        r'100-?days',
        r'30-?days',
        r'course',
        r'lesson',
        r'practice',
        r'challenge',
    ]

    def __init__(self, github_token: Optional[str] = None):
        """Initialize with optional GitHub token."""
        self.token = github_token
        self.github = None

        if PYGITHUB_AVAILABLE and github_token:
            self.github = Github(github_token)
        elif PYGITHUB_AVAILABLE:
            self.github = Github()

    def analyze_all_repos(self, username: str) -> List[Dict[str, Any]]:
        """
        Analyze all public repositories for a user.

        Args:
            username: GitHub username

        Returns:
            List of repository assessments
        """
        repos = self._fetch_repositories(username)

        if not repos:
            return []

        assessments = []
        repo_names = [r.get('name', '') for r in repos]

        for repo in repos:
            assessment = self._analyze_repository(repo, repo_names)
            assessments.append(assessment)

        # Sort by quality score descending
        assessments.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

        return assessments

    def _fetch_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Fetch all public repositories."""
        if self.github:
            try:
                user = self.github.get_user(username)
                repos = []

                for repo in user.get_repos(type='public', sort='updated'):
                    repos.append(self._repo_to_dict(repo))

                return repos

            except Exception as e:
                print(f"PyGithub error: {e}")
                return self._fetch_repos_via_api(username)
        else:
            return self._fetch_repos_via_api(username)

    def _repo_to_dict(self, repo) -> Dict[str, Any]:
        """Convert PyGithub repo to dict."""
        try:
            readme_content = None
            try:
                readme = repo.get_readme()
                readme_content = readme.decoded_content.decode('utf-8')
            except:
                pass

            return {
                'name': repo.name,
                'full_name': repo.full_name,
                'url': repo.html_url,
                'description': repo.description,
                'language': repo.language,
                'topics': repo.get_topics(),
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'is_fork': repo.fork,
                'is_archived': repo.archived,
                'created_at': repo.created_at.isoformat() if repo.created_at else None,
                'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                'size': repo.size,
                'default_branch': repo.default_branch,
                'has_wiki': repo.has_wiki,
                'has_pages': repo.has_pages,
                'open_issues': repo.open_issues_count,
                'readme_content': readme_content
            }
        except Exception as e:
            return {'name': repo.name, 'error': str(e)}

    def _fetch_repos_via_api(self, username: str) -> List[Dict[str, Any]]:
        """Fallback: fetch via direct API."""
        if not REQUESTS_AVAILABLE:
            return []

        try:
            headers = {}
            if self.token:
                headers['Authorization'] = f'token {self.token}'

            response = requests.get(
                f'https://api.github.com/users/{username}/repos',
                params={'type': 'public', 'sort': 'updated', 'per_page': 100},
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                return response.json()
            return []

        except Exception as e:
            print(f"API request error: {e}")
            return []

    def _analyze_repository(self, repo: Dict, all_repo_names: List[str]) -> Dict[str, Any]:
        """Perform deep analysis of a single repository."""
        name = repo.get('name', '')
        description = repo.get('description', '')

        # Calculate days since last commit
        days_since = self._calculate_days_since_commit(repo.get('pushed_at'))

        # Analyze naming
        name_analysis = self._analyze_name(name, description, repo.get('language'))

        # Classify repository
        classification, reason = self._classify_repository(repo, days_since, all_repo_names)

        # Calculate quality score
        quality_score = self._calculate_quality_score(repo, days_since)

        # Analyze README
        readme_quality = self._analyze_readme_quality(repo.get('readme_content'))

        # Extract links from README
        links = self._extract_links(repo.get('readme_content', '') or '')

        # Identify improvements needed
        improvements = self._identify_improvements(repo, quality_score, readme_quality, name_analysis)

        return {
            'name': name,
            'url': repo.get('url') or repo.get('html_url', ''),
            'description': description,
            'classification': classification,
            'classification_reason': reason,
            'quality_score': quality_score,
            'name_clarity_score': name_analysis['clarity_score'],
            'naming_issues': name_analysis['issues'],
            'suggested_name': name_analysis['suggested_name'],
            'naming_rationale': name_analysis['rationale'],
            'has_readme': bool(repo.get('readme_content')),
            'readme_quality': readme_quality,
            'last_commit_date': repo.get('pushed_at'),
            'days_since_commit': days_since,
            'stars': repo.get('stars', 0) or repo.get('stargazers_count', 0),
            'forks': repo.get('forks', 0) or repo.get('forks_count', 0),
            'is_fork': repo.get('is_fork', False) or repo.get('fork', False),
            'is_archived': repo.get('is_archived', False) or repo.get('archived', False),
            'language': repo.get('language'),
            'topics': repo.get('topics', []),
            'links': links,
            'needs_improvement': len(improvements) > 0,
            'improvements_needed': improvements
        }

    def _calculate_days_since_commit(self, pushed_at: Optional[str]) -> int:
        """Calculate days since last commit."""
        if not pushed_at:
            return 9999  # Very stale

        try:
            pushed = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
            now = datetime.now(pushed.tzinfo) if pushed.tzinfo else datetime.now()
            return (now - pushed).days
        except:
            return 9999

    def _analyze_name(self, name: str, description: str, language: str) -> Dict[str, Any]:
        """Analyze repository name for clarity and professionalism."""
        issues = []
        clarity_score = 5
        suggested_name = None
        rationale = ""

        name_lower = name.lower()

        # Check for unclear patterns
        for pattern in self.UNCLEAR_NAME_PATTERNS:
            if re.match(pattern, name_lower):
                issues.append(f"Generic name pattern: '{name}'")
                clarity_score = max(1, clarity_score - 2)
                break

        # Check for very short names
        if len(name) < 4:
            issues.append("Name is too short to be descriptive")
            clarity_score = max(1, clarity_score - 1)

        # Check for all lowercase without hyphens (hard to read)
        if name.islower() and '-' not in name and '_' not in name and len(name) > 10:
            issues.append("Long name without separators is hard to read")
            clarity_score = max(1, clarity_score - 1)

        # Check for inconsistent casing
        if '_' in name and '-' in name:
            issues.append("Inconsistent separator style (mixing _ and -)")
            clarity_score = max(1, clarity_score - 1)

        # Generate suggested name if issues found
        if clarity_score < 4:
            suggested_name = self._suggest_name(name, description, language)
            rationale = self._generate_naming_rationale(name, suggested_name, issues)

        return {
            'clarity_score': clarity_score,
            'issues': issues,
            'suggested_name': suggested_name,
            'rationale': rationale
        }

    def _suggest_name(self, current: str, description: str, language: str) -> Optional[str]:
        """Generate a suggested repository name."""
        # If description is helpful, try to use it
        if description and len(description) > 10:
            # Extract key words from description
            words = re.findall(r'\b[a-z]+\b', description.lower())
            # Filter common words
            stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'for', 'and', 'or', 'to', 'in', 'on', 'with'}
            key_words = [w for w in words if w not in stop_words and len(w) > 2][:3]

            if key_words:
                suggested = '-'.join(key_words)
                if language:
                    suggested = f"{suggested}-{language.lower()}"
                return suggested

        # Default suggestion based on language
        if language:
            return f"project-{language.lower()}"

        return None

    def _generate_naming_rationale(self, current: str, suggested: str, issues: List[str]) -> str:
        """Generate rationale for name change."""
        if not suggested:
            return "No specific suggestion available"

        rationale_parts = [f"Current name '{current}' has issues: {', '.join(issues)}."]
        rationale_parts.append(f"Suggested '{suggested}' is more descriptive and follows naming conventions.")

        return ' '.join(rationale_parts)

    def _classify_repository(self, repo: Dict, days_since: int, all_names: List[str]) -> tuple:
        """Classify repository into categories."""
        name = repo.get('name', '').lower()
        description = (repo.get('description') or '').lower()
        stars = repo.get('stars', 0) or repo.get('stargazers_count', 0)
        forks = repo.get('forks', 0) or repo.get('forks_count', 0)
        is_fork = repo.get('is_fork', False) or repo.get('fork', False)
        is_archived = repo.get('is_archived', False) or repo.get('archived', False)
        has_readme = bool(repo.get('readme_content'))
        size = repo.get('size', 0)

        # Check for duplicates (similar names)
        similar = self._find_similar_names(repo.get('name', ''), all_names)
        if similar:
            return 'Duplicate', f"Similar to: {', '.join(similar)}"

        # Fork with no modifications
        if is_fork and days_since > 365 and stars == 0:
            return 'Abandoned', 'Unmodified fork with no activity'

        # Already archived
        if is_archived:
            return 'Archive', 'Repository is archived'

        # Tutorial/learning artifact
        for pattern in self.TUTORIAL_PATTERNS:
            if re.search(pattern, name) or re.search(pattern, description):
                return 'Learning', 'Appears to be tutorial/course work'

        # Abandoned: no activity, no interest
        if days_since > 730 and stars == 0 and forks == 0:
            return 'Abandoned', 'No activity for 2+ years, no stars/forks'

        # Experimental/test
        if any(re.match(p, name) for p in [r'^test', r'^experiment', r'^try', r'^scratch']):
            return 'Experimental', 'Name suggests experimental/test project'

        # Empty or near-empty
        if size < 10 and not has_readme:
            return 'Experimental', 'Very small repository with no documentation'

        # Showcase: high quality, has engagement
        if stars >= 5 or forks >= 2:
            if has_readme and days_since < 365:
                return 'Showcase', 'Has community engagement and is maintained'

        # Active: recent activity
        if days_since < 180:
            return 'Active', 'Recent activity within 6 months'

        # Archive candidate: inactive but potentially valuable
        if days_since >= 180 and days_since < 730:
            if has_readme or stars > 0:
                return 'Archive', 'Inactive but has documentation/engagement'

        # Default to active if nothing else matches
        return 'Active', 'Regular repository'

    def _find_similar_names(self, name: str, all_names: List[str]) -> List[str]:
        """Find potentially duplicate repository names."""
        similar = []
        name_lower = name.lower()

        # Remove common suffixes for comparison
        base_name = re.sub(r'[-_]?(v\d+|old|new|backup|copy|2|final)$', '', name_lower)

        for other in all_names:
            if other.lower() == name_lower:
                continue

            other_base = re.sub(r'[-_]?(v\d+|old|new|backup|copy|2|final)$', '', other.lower())

            # Check similarity
            if base_name == other_base:
                similar.append(other)
            elif base_name in other.lower() or other.lower() in base_name:
                if abs(len(base_name) - len(other.lower())) < 5:
                    similar.append(other)

        return similar

    def _calculate_quality_score(self, repo: Dict, days_since: int) -> int:
        """Calculate overall quality score (0-5)."""
        score = 3  # Base score

        has_readme = bool(repo.get('readme_content'))
        description = repo.get('description')
        stars = repo.get('stars', 0) or repo.get('stargazers_count', 0)
        forks = repo.get('forks', 0) or repo.get('forks_count', 0)
        topics = repo.get('topics', [])
        is_fork = repo.get('is_fork', False) or repo.get('fork', False)

        # README presence
        if has_readme:
            score += 0.5

        # Description
        if description and len(description) > 20:
            score += 0.5

        # Topics/tags
        if topics and len(topics) >= 3:
            score += 0.5

        # Community engagement
        if stars >= 10:
            score += 0.5
        if forks >= 5:
            score += 0.5

        # Recent activity
        if days_since < 90:
            score += 0.5
        elif days_since > 365:
            score -= 0.5

        # Fork penalty (if unmodified)
        if is_fork:
            score -= 0.5

        return max(0, min(5, int(score)))

    def _analyze_readme_quality(self, content: Optional[str]) -> int:
        """Analyze README quality (0-5)."""
        if not content:
            return 0

        score = 1  # Base for having README

        # Length check
        if len(content) > 500:
            score += 1
        if len(content) > 2000:
            score += 1

        # Check for key sections
        sections = ['installation', 'install', 'usage', 'getting started',
                   'features', 'api', 'documentation', 'license', 'contributing']
        found_sections = sum(1 for s in sections if s.lower() in content.lower())

        if found_sections >= 2:
            score += 1
        if found_sections >= 4:
            score += 1

        return min(5, score)

    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract links from README content."""
        links = []

        if not content:
            return links

        # Markdown link pattern: [text](url)
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, url in md_links:
            if url.startswith('http'):
                links.append({
                    'url': url,
                    'text': text,
                    'context': 'README link'
                })

        # Raw URL pattern
        raw_urls = re.findall(r'(?<!\()https?://[^\s\)>\]]+', content)
        for url in raw_urls:
            # Avoid duplicates
            if not any(l['url'] == url for l in links):
                links.append({
                    'url': url,
                    'text': url,
                    'context': 'README raw URL'
                })

        return links

    def _identify_improvements(self, repo: Dict, quality: int, readme_quality: int, naming: Dict) -> List[str]:
        """Identify specific improvements needed."""
        improvements = []

        if not repo.get('description'):
            improvements.append("Add a repository description")

        if not repo.get('readme_content'):
            improvements.append("Add a README.md file")
        elif readme_quality < 3:
            improvements.append("Expand README with installation/usage instructions")

        if not repo.get('topics'):
            improvements.append("Add topic tags for discoverability")

        if naming['clarity_score'] < 4:
            improvements.append(f"Consider renaming: {naming['issues']}")

        if repo.get('is_fork') and not repo.get('description'):
            improvements.append("Add description explaining your modifications to this fork")

        return improvements
