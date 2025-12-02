"""
Profile Analyzer - GitHub Profile Overview Assessment

Analyzes GitHub profiles from a professional/recruiter perspective,
evaluating first impressions, completeness, and professional appeal.
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

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
class ProfileElement:
    """Individual profile element assessment."""
    name: str
    present: bool
    value: Optional[str]
    score: int  # 0-10
    issues: List[str]
    recommendations: List[str]


class ProfileAnalyzer:
    """
    Analyzes GitHub profile through professional lens.

    Evaluation Criteria (Recruiter Perspective):
    - Profile photo: Professional, clear, appropriate
    - Display name: Real name clarity
    - Bio: Concise, keyword-rich, current
    - Location: Timezone indicator for remote work
    - Company: Employment status
    - Website: Portfolio access
    - Social links: Network presence
    - README: Differentiation
    """

    def __init__(self, github_token: Optional[str] = None):
        """Initialize with optional GitHub token for higher rate limits."""
        self.token = github_token
        self.github = None

        if PYGITHUB_AVAILABLE and github_token:
            self.github = Github(github_token)
        elif PYGITHUB_AVAILABLE:
            self.github = Github()

    def analyze(self, username: str) -> Dict[str, Any]:
        """
        Perform complete profile analysis.

        Args:
            username: GitHub username to analyze

        Returns:
            Dict containing profile assessment with scores and recommendations
        """
        profile_data = self._fetch_profile_data(username)

        if not profile_data:
            return {
                'error': f'Could not fetch profile for {username}',
                'username': username
            }

        assessment = {
            'username': username,
            'analysis_date': datetime.now().isoformat(),
            'profile_url': f'https://github.com/{username}',
            'raw_data': profile_data,
            'elements': {},
            'first_impression_score': 0,
            'category_scores': {},
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }

        # Analyze each profile element
        assessment['elements']['photo'] = self._analyze_photo(profile_data)
        assessment['elements']['name'] = self._analyze_name(profile_data)
        assessment['elements']['bio'] = self._analyze_bio(profile_data)
        assessment['elements']['location'] = self._analyze_location(profile_data)
        assessment['elements']['company'] = self._analyze_company(profile_data)
        assessment['elements']['website'] = self._analyze_website(profile_data)
        assessment['elements']['email'] = self._analyze_email(profile_data)
        assessment['elements']['readme'] = self._analyze_readme(username)

        # Calculate scores
        assessment['first_impression_score'] = self._calculate_first_impression(assessment)
        assessment['category_scores'] = self._calculate_category_scores(assessment)

        # Generate insights
        assessment['strengths'] = self._identify_strengths(assessment)
        assessment['weaknesses'] = self._identify_weaknesses(assessment)
        assessment['recommendations'] = self._generate_recommendations(assessment)

        # Add statistics
        assessment['statistics'] = self._get_profile_statistics(profile_data)

        return assessment

    def _fetch_profile_data(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch profile data from GitHub API."""
        if self.github:
            try:
                user = self.github.get_user(username)
                return {
                    'login': user.login,
                    'name': user.name,
                    'avatar_url': user.avatar_url,
                    'bio': user.bio,
                    'location': user.location,
                    'company': user.company,
                    'blog': user.blog,
                    'email': user.email,
                    'twitter_username': user.twitter_username,
                    'public_repos': user.public_repos,
                    'public_gists': user.public_gists,
                    'followers': user.followers,
                    'following': user.following,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                    'hireable': user.hireable
                }
            except Exception as e:
                print(f"PyGithub error: {e}")
                return self._fetch_profile_via_api(username)
        else:
            return self._fetch_profile_via_api(username)

    def _fetch_profile_via_api(self, username: str) -> Optional[Dict[str, Any]]:
        """Fallback: fetch via direct API call."""
        if not REQUESTS_AVAILABLE:
            return None

        try:
            headers = {}
            if self.token:
                headers['Authorization'] = f'token {self.token}'

            response = requests.get(
                f'https://api.github.com/users/{username}',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"API request error: {e}")
            return None

    def _analyze_photo(self, data: Dict) -> ProfileElement:
        """Analyze profile photo."""
        avatar_url = data.get('avatar_url', '')
        has_custom = avatar_url and 'identicon' not in avatar_url.lower()

        issues = []
        recommendations = []

        if not has_custom:
            issues.append("Using default GitHub avatar")
            recommendations.append("Add a professional photo or custom avatar")

        score = 10 if has_custom else 3

        return ProfileElement(
            name='Profile Photo',
            present=has_custom,
            value=avatar_url if has_custom else None,
            score=score,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_name(self, data: Dict) -> ProfileElement:
        """Analyze display name."""
        name = data.get('name', '')
        login = data.get('login', '')

        issues = []
        recommendations = []
        score = 0

        if name:
            # Check if it looks like a real name
            if len(name.split()) >= 2:
                score = 10  # Full name present
            elif len(name.split()) == 1:
                score = 7
                recommendations.append("Consider using full name for professional appearance")
            else:
                score = 5
        else:
            issues.append("No display name set - only username visible")
            recommendations.append("Add your real name for better professional presence")
            score = 2

        return ProfileElement(
            name='Display Name',
            present=bool(name),
            value=name or login,
            score=score,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_bio(self, data: Dict) -> ProfileElement:
        """Analyze profile bio."""
        bio = data.get('bio', '')

        issues = []
        recommendations = []
        score = 0

        if bio:
            # Length analysis
            if len(bio) < 20:
                issues.append("Bio is too short")
                recommendations.append("Expand bio to include skills and interests")
                score = 4
            elif len(bio) > 150:
                score = 9
            else:
                score = 7

            # Keyword analysis
            tech_keywords = ['developer', 'engineer', 'software', 'full-stack', 'frontend',
                           'backend', 'devops', 'data', 'machine learning', 'ai', 'python',
                           'javascript', 'react', 'node', 'cloud', 'aws', 'open source']

            keywords_found = sum(1 for kw in tech_keywords if kw.lower() in bio.lower())
            if keywords_found == 0:
                recommendations.append("Add relevant technical keywords to improve discoverability")

            # Check for emoji overuse
            emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
            emoji_count = len(emoji_pattern.findall(bio))
            if emoji_count > 5:
                issues.append("Excessive emoji use may appear unprofessional")
                recommendations.append("Consider reducing emojis for a cleaner look")
                score = max(score - 2, 0)

        else:
            issues.append("No bio provided")
            recommendations.append("Add a compelling bio that highlights your expertise and interests")
            score = 0

        return ProfileElement(
            name='Bio',
            present=bool(bio),
            value=bio,
            score=score,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_location(self, data: Dict) -> ProfileElement:
        """Analyze location field."""
        location = data.get('location', '')

        issues = []
        recommendations = []
        score = 0

        if location:
            score = 8

            # Check if timezone-friendly
            timezone_indicators = ['UTC', 'EST', 'PST', 'GMT', 'CET', 'timezone', 'remote']
            has_timezone = any(tz.lower() in location.lower() for tz in timezone_indicators)

            if not has_timezone and len(location) < 15:
                recommendations.append("Consider adding timezone for remote work visibility")
        else:
            issues.append("No location specified")
            recommendations.append("Add location to help recruiters assess timezone fit")
            score = 0

        return ProfileElement(
            name='Location',
            present=bool(location),
            value=location,
            score=score,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_company(self, data: Dict) -> ProfileElement:
        """Analyze company/organization field."""
        company = data.get('company', '')

        issues = []
        recommendations = []
        score = 0

        if company:
            score = 8

            # Check for @ mention format (links to GitHub org)
            if company.startswith('@'):
                score = 10  # Linked to actual GitHub org
        else:
            # Not having company is not necessarily bad
            recommendations.append("Consider adding current company or 'Open to opportunities'")
            score = 5  # Neutral score

        return ProfileElement(
            name='Company',
            present=bool(company),
            value=company,
            score=score,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_website(self, data: Dict) -> ProfileElement:
        """Analyze website/blog URL."""
        website = data.get('blog', '')

        issues = []
        recommendations = []
        score = 0

        if website:
            score = 9

            # Basic URL validation
            if not website.startswith(('http://', 'https://')):
                issues.append("Website URL should include protocol (https://)")
                recommendations.append("Update URL to include https://")
                score = 6
        else:
            issues.append("No website/portfolio link")
            recommendations.append("Add a portfolio site, LinkedIn, or personal website")
            score = 0

        return ProfileElement(
            name='Website',
            present=bool(website),
            value=website,
            score=score,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_email(self, data: Dict) -> ProfileElement:
        """Analyze public email."""
        email = data.get('email', '')

        issues = []
        recommendations = []
        score = 0

        if email:
            score = 7

            # Check email domain professionalism
            unprofessional_domains = ['hotmail', 'yahoo', 'aol']
            if any(domain in email.lower() for domain in unprofessional_domains):
                recommendations.append("Consider using a more professional email domain")
                score = 5
        else:
            # Not having public email is fine for privacy
            score = 5  # Neutral

        return ProfileElement(
            name='Email',
            present=bool(email),
            value=email if email else '[Private]',
            score=score,
            issues=issues,
            recommendations=recommendations
        )

    def _analyze_readme(self, username: str) -> ProfileElement:
        """Analyze profile README (username/username repo)."""
        issues = []
        recommendations = []
        readme_content = None
        score = 0

        try:
            if self.github:
                try:
                    repo = self.github.get_repo(f"{username}/{username}")
                    readme = repo.get_readme()
                    readme_content = readme.decoded_content.decode('utf-8')
                except:
                    pass

            if readme_content:
                score = 8

                # Analyze content quality
                if len(readme_content) < 100:
                    issues.append("Profile README is very short")
                    recommendations.append("Expand README with skills, projects, and contact info")
                    score = 5
                elif len(readme_content) > 2000:
                    score = 10

                # Check for key sections
                key_elements = ['about', 'skills', 'projects', 'contact', 'connect']
                found_elements = sum(1 for el in key_elements if el.lower() in readme_content.lower())

                if found_elements < 2:
                    recommendations.append("Add sections for About, Skills, Projects, or Contact")
            else:
                issues.append("No profile README")
                recommendations.append("Create a README.md in a repo named after your username to stand out")
                score = 0

        except Exception as e:
            issues.append(f"Could not analyze README: {e}")
            score = 0

        return ProfileElement(
            name='Profile README',
            present=bool(readme_content),
            value='Present' if readme_content else None,
            score=score,
            issues=issues,
            recommendations=recommendations
        )

    def _calculate_first_impression(self, assessment: Dict) -> int:
        """Calculate first impression score (0-40)."""
        elements = assessment.get('elements', {})

        # Weight different elements
        weights = {
            'photo': 6,       # HIGH impact
            'name': 6,        # HIGH impact
            'bio': 8,         # HIGH impact
            'website': 6,     # HIGH impact
            'readme': 6,      # HIGH impact
            'location': 4,    # MEDIUM impact
            'company': 2,     # MEDIUM impact
            'email': 2        # LOW impact
        }

        total_score = 0
        for element_name, weight in weights.items():
            element = elements.get(element_name)
            if element:
                # Scale element score (0-10) by weight
                total_score += (element.score / 10) * weight

        return int(total_score)

    def _calculate_category_scores(self, assessment: Dict) -> Dict[str, int]:
        """Calculate scores by category."""
        elements = assessment.get('elements', {})

        categories = {
            'identity': ['photo', 'name'],
            'professional_presence': ['bio', 'website', 'company'],
            'accessibility': ['location', 'email'],
            'differentiation': ['readme']
        }

        scores = {}
        for category, element_names in categories.items():
            category_elements = [elements.get(name) for name in element_names if elements.get(name)]
            if category_elements:
                avg_score = sum(el.score for el in category_elements) / len(category_elements)
                scores[category] = int(avg_score)
            else:
                scores[category] = 0

        return scores

    def _identify_strengths(self, assessment: Dict) -> List[str]:
        """Identify profile strengths."""
        strengths = []
        elements = assessment.get('elements', {})

        for name, element in elements.items():
            if element.score >= 8:
                if name == 'photo' and element.present:
                    strengths.append("Professional profile photo present")
                elif name == 'name' and element.present:
                    strengths.append("Clear professional name displayed")
                elif name == 'bio' and element.present:
                    strengths.append("Informative bio that showcases expertise")
                elif name == 'website' and element.present:
                    strengths.append("Portfolio/website link available for deeper review")
                elif name == 'readme' and element.present:
                    strengths.append("Profile README provides differentiation")

        return strengths

    def _identify_weaknesses(self, assessment: Dict) -> List[str]:
        """Identify profile weaknesses."""
        weaknesses = []
        elements = assessment.get('elements', {})

        for name, element in elements.items():
            if element.score < 5:
                weaknesses.extend(element.issues)

        return weaknesses

    def _generate_recommendations(self, assessment: Dict) -> List[Dict[str, str]]:
        """Generate prioritized recommendations."""
        recommendations = []
        elements = assessment.get('elements', {})

        # Priority order
        priority_order = ['readme', 'bio', 'photo', 'name', 'website', 'location', 'company', 'email']

        for element_name in priority_order:
            element = elements.get(element_name)
            if element and element.recommendations:
                for rec in element.recommendations:
                    recommendations.append({
                        'element': element_name,
                        'recommendation': rec,
                        'impact': 'HIGH' if element.score < 3 else 'MEDIUM' if element.score < 6 else 'LOW'
                    })

        return recommendations

    def _get_profile_statistics(self, data: Dict) -> Dict[str, Any]:
        """Extract profile statistics."""
        return {
            'public_repos': data.get('public_repos', 0),
            'public_gists': data.get('public_gists', 0),
            'followers': data.get('followers', 0),
            'following': data.get('following', 0),
            'account_age_days': self._calculate_account_age(data.get('created_at')),
            'hireable': data.get('hireable', False)
        }

    def _calculate_account_age(self, created_at: Optional[str]) -> int:
        """Calculate account age in days."""
        if not created_at:
            return 0

        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.now(created.tzinfo) - created
            return age.days
        except:
            return 0
