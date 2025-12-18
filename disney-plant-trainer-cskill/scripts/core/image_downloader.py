"""
Image Downloader for Disney Plant Trainer

Robust image downloading with:
- Retry logic and exponential backoff
- Progress tracking
- Concurrent downloads
- Integrity verification
"""

import asyncio
import hashlib
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

from .scraper import ScrapedImage
from ..utils.rate_limiter import RateLimiter, RateLimitConfig
from ..utils.cache_manager import CacheManager
from ..utils.image_validator import ImageValidator, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    """Result of an image download attempt."""
    url: str
    success: bool
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    hash_value: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 1
    download_time: float = 0.0
    validation_result: Optional[str] = None


@dataclass
class DownloadConfig:
    """Configuration for image downloads."""
    max_concurrent: int = 5
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_multiplier: float = 2.0
    max_file_size_mb: float = 50.0
    verify_integrity: bool = True
    validate_images: bool = True
    chunk_size: int = 8192
    user_agent: str = "DisneyPlantTrainer/1.0"


@dataclass
class DownloadProgress:
    """Progress tracking for batch downloads."""
    total: int = 0
    completed: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    bytes_downloaded: int = 0
    start_time: float = field(default_factory=time.time)
    current_url: Optional[str] = None

    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    @property
    def progress_percent(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100

    @property
    def success_rate(self) -> float:
        if self.completed == 0:
            return 0.0
        return (self.successful / self.completed) * 100


class ImageDownloader:
    """
    Robust image downloader with concurrent support.

    Features:
    - Synchronous and asynchronous download modes
    - Retry logic with exponential backoff
    - Progress callbacks
    - Image validation after download
    - Caching to avoid re-downloads
    """

    def __init__(
        self,
        output_dir: Union[str, Path],
        config: Optional[DownloadConfig] = None,
        cache: Optional[CacheManager] = None,
        rate_limiter: Optional[RateLimiter] = None,
        validator: Optional[ImageValidator] = None
    ):
        """
        Initialize the image downloader.

        Args:
            output_dir: Directory to save downloaded images
            config: Download configuration
            cache: Cache manager for avoiding re-downloads
            rate_limiter: Rate limiter for polite downloading
            validator: Image validator for quality checks
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.config = config or DownloadConfig()
        self.cache = cache
        self.rate_limiter = rate_limiter or RateLimiter(RateLimitConfig(
            requests_per_second=2.0,
            max_concurrent_requests=self.config.max_concurrent
        ))
        self.validator = validator or ImageValidator()

        self._session: Optional[requests.Session] = None
        self._progress = DownloadProgress()

        logger.info(f"Image downloader initialized: {self.output_dir}")

    def _get_session(self) -> requests.Session:
        """Get or create requests session with retry configuration."""
        if self._session is None:
            self._session = requests.Session()

            retry_strategy = Retry(
                total=self.config.max_retries,
                backoff_factor=self.config.retry_delay,
                status_forcelist=[429, 500, 502, 503, 504]
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)

            self._session.headers.update({
                "User-Agent": self.config.user_agent,
                "Accept": "image/*,*/*;q=0.8"
            })

        return self._session

    def _generate_filename(self, url: str, content_type: Optional[str] = None) -> str:
        """Generate a unique filename for a URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]

        parsed = urlparse(url)
        path = parsed.path

        ext = ""
        if "." in path:
            ext = Path(path).suffix.lower()

        if not ext or ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            if content_type:
                ext_map = {
                    "image/jpeg": ".jpg",
                    "image/png": ".png",
                    "image/gif": ".gif",
                    "image/webp": ".webp"
                }
                ext = ext_map.get(content_type.split(";")[0], ".jpg")
            else:
                ext = ".jpg"

        return f"{url_hash}{ext}"

    def download_one(
        self,
        url: str,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DownloadResult:
        """
        Download a single image.

        Args:
            url: Image URL to download
            filename: Optional filename (auto-generated if not provided)
            metadata: Additional metadata to store

        Returns:
            DownloadResult with success status and details
        """
        start_time = time.time()
        self._progress.current_url = url

        if self.cache:
            cached = self.cache.get_image(url)
            if cached:
                logger.debug(f"Cache hit for {url}")
                return DownloadResult(
                    url=url,
                    success=True,
                    file_path="(cached)",
                    file_size=len(cached),
                    validation_result="cached"
                )

        if not self.rate_limiter.wait_if_needed(url):
            return DownloadResult(
                url=url,
                success=False,
                error="Blocked by rate limiter"
            )

        session = self._get_session()
        attempts = 0
        last_error = None

        while attempts < self.config.max_retries:
            attempts += 1

            try:
                response = session.get(
                    url,
                    timeout=self.config.timeout_seconds,
                    stream=True
                )

                self.rate_limiter.record_request(url, success=True)

                if response.status_code == 429:
                    self.rate_limiter.record_error(url, 429)
                    delay = self.config.retry_delay * (self.config.backoff_multiplier ** attempts)
                    time.sleep(delay)
                    continue

                if response.status_code != 200:
                    last_error = f"HTTP {response.status_code}"
                    continue

                content_length = response.headers.get("Content-Length")
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    if size_mb > self.config.max_file_size_mb:
                        return DownloadResult(
                            url=url,
                            success=False,
                            error=f"File too large: {size_mb:.1f}MB",
                            attempts=attempts
                        )

                chunks = []
                downloaded = 0
                for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                    chunks.append(chunk)
                    downloaded += len(chunk)

                    if downloaded > self.config.max_file_size_mb * 1024 * 1024:
                        return DownloadResult(
                            url=url,
                            success=False,
                            error="File exceeded max size during download",
                            attempts=attempts
                        )

                image_data = b"".join(chunks)

                if self.config.validate_images:
                    validation = self.validator.validate(image_data)
                    if not validation.is_valid:
                        return DownloadResult(
                            url=url,
                            success=False,
                            error=f"Validation failed: {validation.result.value}",
                            attempts=attempts,
                            validation_result=validation.result.value
                        )

                if not filename:
                    content_type = response.headers.get("Content-Type")
                    filename = self._generate_filename(url, content_type)

                file_path = self.output_dir / filename
                file_path.write_bytes(image_data)

                hash_value = hashlib.md5(image_data).hexdigest()

                if self.cache:
                    self.cache.cache_image(url, image_data, metadata=metadata)

                download_time = time.time() - start_time

                return DownloadResult(
                    url=url,
                    success=True,
                    file_path=str(file_path),
                    file_size=len(image_data),
                    hash_value=hash_value,
                    attempts=attempts,
                    download_time=download_time,
                    validation_result="valid"
                )

            except requests.exceptions.Timeout:
                last_error = "Timeout"
                self.rate_limiter.record_request(url, success=False)

            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {e}"
                self.rate_limiter.record_request(url, success=False)

            except Exception as e:
                last_error = str(e)
                logger.error(f"Download error for {url}: {e}")

            if attempts < self.config.max_retries:
                delay = self.config.retry_delay * (self.config.backoff_multiplier ** (attempts - 1))
                time.sleep(delay)

        return DownloadResult(
            url=url,
            success=False,
            error=last_error,
            attempts=attempts,
            download_time=time.time() - start_time
        )

    def download_batch(
        self,
        images: List[Union[str, ScrapedImage]],
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> List[DownloadResult]:
        """
        Download multiple images concurrently.

        Args:
            images: List of URLs or ScrapedImage objects
            progress_callback: Callback for progress updates

        Returns:
            List of DownloadResult objects
        """
        urls = []
        metadata_map = {}

        for item in images:
            if isinstance(item, str):
                urls.append(item)
            else:
                urls.append(item.url)
                metadata_map[item.url] = {
                    "source": item.source,
                    "title": item.title,
                    "tags": item.tags
                }

        self._progress = DownloadProgress(total=len(urls))
        results = []

        with ThreadPoolExecutor(max_workers=self.config.max_concurrent) as executor:
            futures = {
                executor.submit(
                    self.download_one,
                    url,
                    metadata=metadata_map.get(url)
                ): url
                for url in urls
            }

            for future in as_completed(futures):
                url = futures[future]

                try:
                    result = future.result()
                except Exception as e:
                    result = DownloadResult(
                        url=url,
                        success=False,
                        error=str(e)
                    )

                results.append(result)

                self._progress.completed += 1
                if result.success:
                    self._progress.successful += 1
                    if result.file_size:
                        self._progress.bytes_downloaded += result.file_size
                else:
                    self._progress.failed += 1

                if progress_callback:
                    progress_callback(self._progress)

        return results

    async def download_batch_async(
        self,
        images: List[Union[str, ScrapedImage]],
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> List[DownloadResult]:
        """
        Download multiple images asynchronously.

        Args:
            images: List of URLs or ScrapedImage objects
            progress_callback: Callback for progress updates

        Returns:
            List of DownloadResult objects
        """
        if not HAS_AIOHTTP:
            logger.warning("aiohttp not available, falling back to sync download")
            return self.download_batch(images, progress_callback)

        urls = []
        metadata_map = {}

        for item in images:
            if isinstance(item, str):
                urls.append(item)
            else:
                urls.append(item.url)
                metadata_map[item.url] = {
                    "source": item.source,
                    "title": item.title,
                    "tags": item.tags
                }

        self._progress = DownloadProgress(total=len(urls))

        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async def download_with_semaphore(url: str) -> DownloadResult:
            async with semaphore:
                return await self._async_download_one(url, metadata_map.get(url))

        async with aiohttp.ClientSession(
            headers={"User-Agent": self.config.user_agent}
        ) as session:
            tasks = [download_with_semaphore(url) for url in urls]
            results = []

            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)

                self._progress.completed += 1
                if result.success:
                    self._progress.successful += 1
                    if result.file_size:
                        self._progress.bytes_downloaded += result.file_size
                else:
                    self._progress.failed += 1

                if progress_callback:
                    progress_callback(self._progress)

        return results

    async def _async_download_one(
        self,
        url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DownloadResult:
        """Async download implementation."""
        if not HAS_AIOHTTP:
            return self.download_one(url, metadata=metadata)

        start_time = time.time()

        can_request, wait_time, _ = self.rate_limiter.can_request(url)
        if not can_request:
            if wait_time > 0 and wait_time <= self.config.timeout_seconds:
                await asyncio.sleep(wait_time)
            else:
                return DownloadResult(
                    url=url,
                    success=False,
                    error="Rate limited"
                )

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
                ) as response:
                    if response.status != 200:
                        return DownloadResult(
                            url=url,
                            success=False,
                            error=f"HTTP {response.status}"
                        )

                    image_data = await response.read()

                    if self.config.validate_images:
                        validation = self.validator.validate(image_data)
                        if not validation.is_valid:
                            return DownloadResult(
                                url=url,
                                success=False,
                                error=f"Validation failed: {validation.result.value}",
                                validation_result=validation.result.value
                            )

                    content_type = response.headers.get("Content-Type")
                    filename = self._generate_filename(url, content_type)
                    file_path = self.output_dir / filename

                    file_path.write_bytes(image_data)

                    return DownloadResult(
                        url=url,
                        success=True,
                        file_path=str(file_path),
                        file_size=len(image_data),
                        hash_value=hashlib.md5(image_data).hexdigest(),
                        download_time=time.time() - start_time,
                        validation_result="valid"
                    )

            except asyncio.TimeoutError:
                return DownloadResult(url=url, success=False, error="Timeout")
            except Exception as e:
                return DownloadResult(url=url, success=False, error=str(e))

    def download_from_scraper(
        self,
        scraped_images: List[ScrapedImage],
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> Tuple[List[DownloadResult], Dict[str, Any]]:
        """
        Download images from scraper results.

        Args:
            scraped_images: List of ScrapedImage objects
            progress_callback: Progress callback

        Returns:
            Tuple of (results list, summary statistics)
        """
        results = self.download_batch(scraped_images, progress_callback)

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        summary = {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) * 100 if results else 0,
            "total_bytes": sum(r.file_size or 0 for r in successful),
            "total_time": self._progress.elapsed_seconds,
            "by_source": {},
            "failure_reasons": {}
        }

        for img in scraped_images:
            source = img.source
            if source not in summary["by_source"]:
                summary["by_source"][source] = {"total": 0, "success": 0}
            summary["by_source"][source]["total"] += 1

        for result in successful:
            for img in scraped_images:
                if img.url == result.url:
                    summary["by_source"][img.source]["success"] += 1
                    break

        for result in failed:
            reason = result.error or "unknown"
            summary["failure_reasons"][reason] = summary["failure_reasons"].get(reason, 0) + 1

        return results, summary

    def get_progress(self) -> DownloadProgress:
        """Get current download progress."""
        return self._progress

    def close(self) -> None:
        """Close the downloader and release resources."""
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
