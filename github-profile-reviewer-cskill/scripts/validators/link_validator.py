"""
Link Validator - Comprehensive Link Verification

Verifies all links found in GitHub profiles and repositories,
checking for functionality, SSL validity, and professional value.
"""

import re
import ssl
import socket
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class LinkResult:
    """Result of link verification."""
    url: str
    source: str
    context: str
    status: str  # 'working', 'broken', 'redirect', 'timeout', 'error'
    status_code: Optional[int]
    response_time: float
    ssl_valid: bool
    redirect_url: Optional[str]
    issues: List[str]
    professional_value: str  # 'high', 'medium', 'low'
    recommendation: str


class LinkValidator:
    """
    Comprehensive link verification for GitHub profiles.

    Checks:
    1. HTTP status (200, 301, 404, etc.)
    2. SSL certificate validity
    3. Response time
    4. Redirect chains
    5. Content validation
    6. Professional value assessment
    """

    # Known low-value or unprofessional link patterns
    LOW_VALUE_PATTERNS = [
        r'localhost',
        r'127\.0\.0\.1',
        r'192\.168\.',
        r'example\.com',
        r'test\.',
        r'placeholder',
    ]

    # High-value professional domains
    HIGH_VALUE_DOMAINS = [
        'linkedin.com',
        'twitter.com',
        'github.io',
        'vercel.app',
        'netlify.app',
        'heroku.com',
        'medium.com',
        'dev.to',
        'stackoverflow.com',
        'youtube.com',
        'npmjs.com',
        'pypi.org',
    ]

    # Suspicious or spammy patterns
    SUSPICIOUS_PATTERNS = [
        r'bit\.ly',
        r'tinyurl',
        r'shorturl',
        r't\.co',
        r'goo\.gl',
    ]

    def __init__(self, timeout: int = 10, max_workers: int = 5):
        """
        Initialize link validator.

        Args:
            timeout: Request timeout in seconds
            max_workers: Max parallel link checks
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = None

        if REQUESTS_AVAILABLE:
            self.session = self._create_session()

    def _create_session(self) -> 'requests.Session':
        """Create a requests session with retry logic."""
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # Set headers to appear as browser
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GitHubProfileReviewer/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })

        return session

    def verify_links(self, links: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Verify multiple links in parallel.

        Args:
            links: List of link dicts with 'url', 'source', 'context'

        Returns:
            Dict with 'working', 'broken', 'redirects', 'warnings' lists
        """
        if not REQUESTS_AVAILABLE:
            return {
                'error': 'requests library not available',
                'links_checked': 0
            }

        results = {
            'working': [],
            'broken': [],
            'redirects': [],
            'warnings': [],
            'errors': [],
            'links_checked': len(links),
            'summary': {}
        }

        # Deduplicate URLs
        unique_links = {}
        for link in links:
            url = link.get('url', '')
            if url and url not in unique_links:
                unique_links[url] = link

        # Verify in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._verify_single_link, link): link
                for link in unique_links.values()
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    self._categorize_result(result, results)
                except Exception as e:
                    link = futures[future]
                    results['errors'].append({
                        'url': link.get('url'),
                        'error': str(e)
                    })

        # Generate summary
        results['summary'] = {
            'total': len(links),
            'unique': len(unique_links),
            'working': len(results['working']),
            'broken': len(results['broken']),
            'warnings': len(results['warnings'])
        }

        return results

    def _verify_single_link(self, link: Dict[str, str]) -> LinkResult:
        """Verify a single link."""
        url = link.get('url', '')
        source = link.get('source', 'Unknown')
        context = link.get('context', '')

        issues = []
        status = 'unknown'
        status_code = None
        response_time = 0.0
        ssl_valid = True
        redirect_url = None
        professional_value = 'medium'
        recommendation = ''

        # Pre-check URL format
        parsed = urlparse(url)
        if not parsed.scheme:
            url = 'https://' + url
            parsed = urlparse(url)

        if not parsed.netloc:
            return LinkResult(
                url=url,
                source=source,
                context=context,
                status='broken',
                status_code=None,
                response_time=0,
                ssl_valid=False,
                redirect_url=None,
                issues=['Invalid URL format'],
                professional_value='low',
                recommendation='Remove or fix this invalid URL'
            )

        # Check for known low-value patterns
        for pattern in self.LOW_VALUE_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                issues.append(f'URL matches low-value pattern: {pattern}')
                professional_value = 'low'

        # Check for suspicious shorteners
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                issues.append('URL uses URL shortener - consider using full URL')

        # Verify SSL certificate
        ssl_valid = self._check_ssl(parsed.netloc)
        if not ssl_valid:
            issues.append('SSL certificate is invalid or expired')

        # Make HTTP request
        try:
            import time
            start_time = time.time()

            response = self.session.head(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )

            response_time = time.time() - start_time
            status_code = response.status_code

            # Check for redirects
            if response.history:
                redirect_url = response.url
                if self._is_significant_redirect(url, redirect_url):
                    issues.append(f'Redirects to different domain: {redirect_url}')
                    status = 'redirect'

            # Determine status
            if status_code == 200:
                status = 'working'
            elif status_code in [301, 302, 303, 307, 308]:
                status = 'redirect'
            elif status_code == 404:
                status = 'broken'
                issues.append('Page not found (404)')
            elif status_code >= 400:
                status = 'broken'
                issues.append(f'HTTP error: {status_code}')
            elif status_code >= 500:
                status = 'error'
                issues.append(f'Server error: {status_code}')
            else:
                status = 'working'

            # Check response time
            if response_time > 5:
                issues.append(f'Slow response time: {response_time:.1f}s')

        except requests.exceptions.Timeout:
            status = 'timeout'
            issues.append('Request timed out')
        except requests.exceptions.SSLError:
            status = 'error'
            ssl_valid = False
            issues.append('SSL certificate error')
        except requests.exceptions.ConnectionError:
            status = 'broken'
            issues.append('Could not connect to server')
        except Exception as e:
            status = 'error'
            issues.append(f'Error: {str(e)}')

        # Assess professional value
        professional_value = self._assess_professional_value(url, status, issues)

        # Generate recommendation
        recommendation = self._generate_recommendation(status, issues, professional_value)

        return LinkResult(
            url=url,
            source=source,
            context=context,
            status=status,
            status_code=status_code,
            response_time=response_time,
            ssl_valid=ssl_valid,
            redirect_url=redirect_url,
            issues=issues,
            professional_value=professional_value,
            recommendation=recommendation
        )

    def _check_ssl(self, hostname: str) -> bool:
        """Check if SSL certificate is valid."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname):
                    return True
        except:
            return False

    def _is_significant_redirect(self, original: str, final: str) -> bool:
        """Check if redirect is to a significantly different domain."""
        orig_parsed = urlparse(original)
        final_parsed = urlparse(final)

        orig_domain = orig_parsed.netloc.lower().replace('www.', '')
        final_domain = final_parsed.netloc.lower().replace('www.', '')

        return orig_domain != final_domain

    def _assess_professional_value(self, url: str, status: str, issues: List[str]) -> str:
        """Assess the professional value of a link."""
        if status == 'broken':
            return 'low'

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Check high-value domains
        for high_value in self.HIGH_VALUE_DOMAINS:
            if high_value in domain:
                return 'high'

        # Check for personal domain (likely portfolio)
        if domain.endswith('.io') or domain.endswith('.dev') or domain.endswith('.me'):
            return 'high'

        # Default based on issues
        if len(issues) > 2:
            return 'low'
        elif issues:
            return 'medium'

        return 'medium'

    def _generate_recommendation(self, status: str, issues: List[str], value: str) -> str:
        """Generate actionable recommendation."""
        if status == 'broken':
            return 'Remove this broken link or update to working URL'
        elif status == 'timeout':
            return 'Check if this server is still operational'
        elif status == 'error':
            return 'Investigate and fix or remove this problematic link'
        elif status == 'redirect':
            return 'Update to the final destination URL for cleaner presentation'
        elif value == 'low':
            return 'Consider removing this low-value link'
        elif issues:
            return f'Address issues: {"; ".join(issues)}'
        else:
            return 'Link is working - no action needed'

    def _categorize_result(self, result: LinkResult, results: Dict):
        """Categorize a link result into appropriate lists."""
        result_dict = {
            'url': result.url,
            'source': result.source,
            'context': result.context,
            'status_code': result.status_code,
            'response_time': f'{result.response_time:.2f}s',
            'ssl_valid': result.ssl_valid,
            'professional_value': result.professional_value,
            'issues': result.issues,
            'recommendation': result.recommendation
        }

        if result.redirect_url:
            result_dict['redirect_url'] = result.redirect_url

        if result.status == 'working':
            if result.issues or result.professional_value == 'low':
                results['warnings'].append(result_dict)
            else:
                results['working'].append(result_dict)
        elif result.status == 'broken':
            results['broken'].append(result_dict)
        elif result.status == 'redirect':
            results['redirects'].append(result_dict)
        else:
            results['errors'].append(result_dict)


def verify_single_url(url: str) -> Dict[str, Any]:
    """Quick utility to verify a single URL."""
    validator = LinkValidator()
    result = validator._verify_single_link({
        'url': url,
        'source': 'Direct check',
        'context': ''
    })
    return {
        'url': result.url,
        'status': result.status,
        'status_code': result.status_code,
        'ssl_valid': result.ssl_valid,
        'issues': result.issues,
        'recommendation': result.recommendation
    }
