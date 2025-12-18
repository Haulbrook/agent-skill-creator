"""
Rate Limiter for Disney Plant Trainer

Implements polite web scraping with:
- Per-domain request throttling
- Exponential backoff on errors
- Concurrent request limiting
- robots.txt compliance checking
"""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

logger = logging.getLogger(__name__)


@dataclass
class DomainState:
    """Tracks rate limiting state for a domain."""
    last_request: float = 0.0
    request_count: int = 0
    error_count: int = 0
    backoff_until: float = 0.0
    crawl_delay: float = 1.0
    allowed_paths: List[str] = field(default_factory=list)
    disallowed_paths: List[str] = field(default_factory=list)
    robots_checked: bool = False


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting behavior."""
    requests_per_second: float = 1.0
    min_delay_seconds: float = 0.5
    max_delay_seconds: float = 10.0
    max_concurrent_requests: int = 5
    backoff_multiplier: float = 2.0
    max_backoff_seconds: float = 300.0
    respect_robots_txt: bool = True
    user_agent: str = "DisneyPlantTrainer/1.0 (Educational Bot)"


class RateLimiter:
    """
    Intelligent rate limiter for web scraping.

    Features:
    - Per-domain request tracking
    - Automatic robots.txt parsing
    - Exponential backoff on failures
    - Thread-safe operation
    - Rate limit statistics
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize the rate limiter.

        Args:
            config: Rate limiting configuration
        """
        self.config = config or RateLimitConfig()
        self.domain_states: Dict[str, DomainState] = defaultdict(DomainState)
        self._lock = Lock()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        self._request_history: List[Tuple[str, float, bool]] = []

        logger.info(f"Rate limiter initialized: {self.config.requests_per_second} req/s")

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc.lower()

    def _get_robots_parser(self, domain: str) -> Optional[RobotFileParser]:
        """Get and cache robots.txt parser for a domain."""
        if not self.config.respect_robots_txt:
            return None

        robots_url = f"https://{domain}/robots.txt"
        try:
            parser = RobotFileParser()
            parser.set_url(robots_url)
            parser.read()
            return parser
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt for {domain}: {e}")
            return None

    def _check_robots_txt(self, url: str) -> Tuple[bool, float]:
        """
        Check if URL is allowed by robots.txt.

        Args:
            url: URL to check

        Returns:
            Tuple of (is_allowed, crawl_delay)
        """
        domain = self._extract_domain(url)
        state = self.domain_states[domain]

        if state.robots_checked:
            parsed = urlparse(url)
            path = parsed.path or "/"

            for disallowed in state.disallowed_paths:
                if path.startswith(disallowed):
                    return False, state.crawl_delay

            return True, state.crawl_delay

        parser = self._get_robots_parser(domain)
        state.robots_checked = True

        if parser is None:
            return True, self.config.min_delay_seconds

        is_allowed = parser.can_fetch(self.config.user_agent, url)
        crawl_delay = parser.crawl_delay(self.config.user_agent)

        if crawl_delay:
            state.crawl_delay = max(crawl_delay, self.config.min_delay_seconds)
        else:
            state.crawl_delay = 1.0 / self.config.requests_per_second

        return is_allowed, state.crawl_delay

    def can_request(self, url: str) -> Tuple[bool, float, str]:
        """
        Check if a request can be made to a URL.

        Args:
            url: URL to check

        Returns:
            Tuple of (can_request, wait_time, reason)
        """
        domain = self._extract_domain(url)

        with self._lock:
            state = self.domain_states[domain]
            now = time.time()

            if state.backoff_until > now:
                wait_time = state.backoff_until - now
                return False, wait_time, f"Backing off due to errors (wait {wait_time:.1f}s)"

            is_allowed, crawl_delay = self._check_robots_txt(url)
            if not is_allowed:
                return False, 0, "Disallowed by robots.txt"

            time_since_last = now - state.last_request
            required_delay = max(
                crawl_delay,
                1.0 / self.config.requests_per_second,
                self.config.min_delay_seconds
            )

            if time_since_last < required_delay:
                wait_time = required_delay - time_since_last
                return False, wait_time, f"Rate limited (wait {wait_time:.1f}s)"

            return True, 0, "OK"

    def wait_if_needed(self, url: str) -> bool:
        """
        Wait if necessary before making a request.

        Args:
            url: URL to request

        Returns:
            True if request can proceed, False if blocked
        """
        can_request, wait_time, reason = self.can_request(url)

        if "robots.txt" in reason:
            logger.warning(f"Blocked by robots.txt: {url}")
            return False

        if not can_request and wait_time > 0:
            if wait_time <= self.config.max_delay_seconds:
                logger.debug(f"Rate limiting: waiting {wait_time:.1f}s for {url}")
                time.sleep(wait_time)
                return True
            else:
                logger.warning(f"Wait time too long ({wait_time:.1f}s) for {url}")
                return False

        return True

    def record_request(self, url: str, success: bool = True) -> None:
        """
        Record that a request was made.

        Args:
            url: URL that was requested
            success: Whether the request succeeded
        """
        domain = self._extract_domain(url)

        with self._lock:
            state = self.domain_states[domain]
            now = time.time()

            state.last_request = now
            state.request_count += 1

            if success:
                state.error_count = 0
            else:
                state.error_count += 1
                backoff = min(
                    self.config.min_delay_seconds * (
                        self.config.backoff_multiplier ** state.error_count
                    ),
                    self.config.max_backoff_seconds
                )
                state.backoff_until = now + backoff
                logger.warning(
                    f"Request failed for {domain}, backing off for {backoff:.1f}s "
                    f"(error count: {state.error_count})"
                )

            self._request_history.append((domain, now, success))

            if len(self._request_history) > 10000:
                self._request_history = self._request_history[-5000:]

    def record_error(self, url: str, error_code: Optional[int] = None) -> None:
        """
        Record a request error with optional HTTP status code.

        Args:
            url: URL that failed
            error_code: HTTP status code if available
        """
        domain = self._extract_domain(url)

        with self._lock:
            state = self.domain_states[domain]
            state.error_count += 1
            now = time.time()

            if error_code == 429:
                backoff = self.config.max_backoff_seconds
                logger.warning(f"Rate limit (429) from {domain}, max backoff applied")
            elif error_code and error_code >= 500:
                backoff = min(
                    30 * (self.config.backoff_multiplier ** (state.error_count - 1)),
                    self.config.max_backoff_seconds
                )
            else:
                backoff = min(
                    self.config.min_delay_seconds * (
                        self.config.backoff_multiplier ** state.error_count
                    ),
                    self.config.max_backoff_seconds
                )

            state.backoff_until = now + backoff
            logger.warning(
                f"Error {error_code or 'unknown'} for {domain}, "
                f"backing off for {backoff:.1f}s"
            )

    async def acquire(self, url: str) -> bool:
        """
        Async context manager for rate-limited requests.

        Args:
            url: URL to request

        Returns:
            True if request can proceed
        """
        async with self._semaphore:
            can_request, wait_time, reason = self.can_request(url)

            if "robots.txt" in reason:
                return False

            if wait_time > 0:
                if wait_time <= self.config.max_delay_seconds:
                    await asyncio.sleep(wait_time)
                else:
                    return False

            return True

    def get_domain_stats(self, domain: str) -> Dict[str, Any]:
        """
        Get statistics for a specific domain.

        Args:
            domain: Domain to get stats for

        Returns:
            Dictionary with domain statistics
        """
        with self._lock:
            state = self.domain_states[domain]
            now = time.time()

            return {
                "domain": domain,
                "request_count": state.request_count,
                "error_count": state.error_count,
                "crawl_delay": state.crawl_delay,
                "last_request_ago": now - state.last_request if state.last_request else None,
                "backoff_remaining": max(0, state.backoff_until - now),
                "robots_checked": state.robots_checked
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get overall rate limiter statistics.

        Returns:
            Dictionary with statistics
        """
        with self._lock:
            now = time.time()
            recent_requests = [r for r in self._request_history if now - r[1] < 60]
            recent_errors = [r for r in recent_requests if not r[2]]

            total_requests = sum(s.request_count for s in self.domain_states.values())
            total_errors = sum(s.error_count for s in self.domain_states.values())

            return {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "domains_tracked": len(self.domain_states),
                "requests_last_minute": len(recent_requests),
                "errors_last_minute": len(recent_errors),
                "avg_requests_per_second": len(recent_requests) / 60 if recent_requests else 0,
                "config": {
                    "requests_per_second": self.config.requests_per_second,
                    "max_concurrent": self.config.max_concurrent_requests,
                    "respect_robots_txt": self.config.respect_robots_txt
                }
            }

    def reset_domain(self, domain: str) -> None:
        """Reset rate limiting state for a domain."""
        with self._lock:
            if domain in self.domain_states:
                del self.domain_states[domain]
                logger.info(f"Reset rate limiting state for {domain}")

    def reset_all(self) -> None:
        """Reset all rate limiting state."""
        with self._lock:
            self.domain_states.clear()
            self._request_history.clear()
            logger.info("Reset all rate limiting state")


class RateLimitedSession:
    """
    Requests session with built-in rate limiting.

    Usage:
        session = RateLimitedSession()
        response = session.get("https://example.com/image.jpg")
    """

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize rate-limited session.

        Args:
            rate_limiter: Rate limiter instance (creates default if None)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.rate_limiter = rate_limiter or RateLimiter()
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.rate_limiter.config.user_agent
        })

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make a rate-limited GET request.

        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.get

        Returns:
            Response object or None if failed
        """
        return self._request("GET", url, **kwargs)

    def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Optional[requests.Response]:
        """Make a rate-limited request with retries."""
        kwargs.setdefault("timeout", self.timeout)

        for attempt in range(1, self.max_retries + 1):
            if not self.rate_limiter.wait_if_needed(url):
                logger.warning(f"Request blocked by rate limiter: {url}")
                return None

            try:
                response = self.session.request(method, url, **kwargs)
                self.rate_limiter.record_request(url, success=True)

                if response.status_code == 429:
                    self.rate_limiter.record_error(url, 429)
                    if attempt < self.max_retries:
                        continue
                    return None

                return response

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt}/{self.max_retries}: {url}")
                self.rate_limiter.record_request(url, success=False)

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt}: {e}")
                self.rate_limiter.record_request(url, success=False)

            except Exception as e:
                logger.error(f"Request failed: {e}")
                self.rate_limiter.record_request(url, success=False)
                return None

        logger.error(f"Max retries exceeded for {url}")
        return None

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
