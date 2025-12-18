"""
Plant Image Scraper for Disney Plant Trainer

Scrapes royalty-free plant images from:
- Unsplash (via API)
- Pexels (via API)
- Pixabay (via API)
- Custom botanical websites
"""

import json
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Set
from urllib.parse import urljoin, urlparse, quote_plus

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from ..utils.rate_limiter import RateLimiter, RateLimitConfig
from ..utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class ScrapedImage:
    """Represents a scraped image with metadata."""
    url: str
    thumbnail_url: Optional[str] = None
    source: str = ""
    source_page: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    photographer: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    width: Optional[int] = None
    height: Optional[int] = None
    license: str = "royalty-free"
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ScrapingConfig:
    """Configuration for scraping behavior."""
    max_images_per_query: int = 100
    max_pages: int = 10
    images_per_page: int = 30
    min_width: int = 800
    min_height: int = 600
    preferred_orientation: Optional[str] = None
    color_filter: Optional[str] = None
    safe_search: bool = True


class ImageSourceBase(ABC):
    """Base class for image sources."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None,
        config: Optional[ScrapingConfig] = None
    ):
        self.api_key = api_key
        self.rate_limiter = rate_limiter or RateLimiter()
        self.config = config or ScrapingConfig()
        self.session = requests.Session() if HAS_REQUESTS else None

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the image source."""
        pass

    @abstractmethod
    def search(self, query: str, page: int = 1) -> List[ScrapedImage]:
        """Search for images matching query."""
        pass

    def _make_request(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make a rate-limited API request."""
        if not HAS_REQUESTS:
            logger.error("requests library not available")
            return None

        if not self.rate_limiter.wait_if_needed(url):
            return None

        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers or {},
                timeout=30
            )
            self.rate_limiter.record_request(url, success=True)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                self.rate_limiter.record_error(url, 429)
                logger.warning(f"Rate limited by {self.source_name}")
            else:
                logger.warning(f"{self.source_name} returned {response.status_code}")
                self.rate_limiter.record_request(url, success=False)

        except Exception as e:
            logger.error(f"Request failed: {e}")
            self.rate_limiter.record_request(url, success=False)

        return None


class UnsplashSource(ImageSourceBase):
    """Scraper for Unsplash API."""

    BASE_URL = "https://api.unsplash.com"

    @property
    def source_name(self) -> str:
        return "unsplash"

    def search(self, query: str, page: int = 1) -> List[ScrapedImage]:
        """Search Unsplash for images."""
        if not self.api_key:
            logger.warning("Unsplash API key not configured")
            return []

        url = f"{self.BASE_URL}/search/photos"
        params = {
            "query": query,
            "page": page,
            "per_page": self.config.images_per_page,
            "content_filter": "high" if self.config.safe_search else "low"
        }

        if self.config.preferred_orientation:
            params["orientation"] = self.config.preferred_orientation

        if self.config.color_filter:
            params["color"] = self.config.color_filter

        headers = {"Authorization": f"Client-ID {self.api_key}"}

        data = self._make_request(url, params=params, headers=headers)
        if not data:
            return []

        images = []
        for result in data.get("results", []):
            width = result.get("width", 0)
            height = result.get("height", 0)

            if width < self.config.min_width or height < self.config.min_height:
                continue

            urls = result.get("urls", {})
            user = result.get("user", {})

            image = ScrapedImage(
                url=urls.get("regular") or urls.get("full"),
                thumbnail_url=urls.get("thumb"),
                source="unsplash",
                source_page=result.get("links", {}).get("html"),
                title=result.get("alt_description") or result.get("description"),
                description=result.get("description"),
                photographer=user.get("name"),
                tags=[tag.get("title") for tag in result.get("tags", [])],
                width=width,
                height=height,
                license="unsplash"
            )
            images.append(image)

        logger.info(f"Unsplash: Found {len(images)} images for '{query}' (page {page})")
        return images


class PexelsSource(ImageSourceBase):
    """Scraper for Pexels API."""

    BASE_URL = "https://api.pexels.com/v1"

    @property
    def source_name(self) -> str:
        return "pexels"

    def search(self, query: str, page: int = 1) -> List[ScrapedImage]:
        """Search Pexels for images."""
        if not self.api_key:
            logger.warning("Pexels API key not configured")
            return []

        url = f"{self.BASE_URL}/search"
        params = {
            "query": query,
            "page": page,
            "per_page": self.config.images_per_page,
        }

        if self.config.preferred_orientation:
            params["orientation"] = self.config.preferred_orientation

        if self.config.color_filter:
            params["color"] = self.config.color_filter

        headers = {"Authorization": self.api_key}

        data = self._make_request(url, params=params, headers=headers)
        if not data:
            return []

        images = []
        for photo in data.get("photos", []):
            width = photo.get("width", 0)
            height = photo.get("height", 0)

            if width < self.config.min_width or height < self.config.min_height:
                continue

            src = photo.get("src", {})

            image = ScrapedImage(
                url=src.get("large2x") or src.get("original"),
                thumbnail_url=src.get("medium"),
                source="pexels",
                source_page=photo.get("url"),
                title=photo.get("alt"),
                photographer=photo.get("photographer"),
                tags=[],
                width=width,
                height=height,
                license="pexels"
            )
            images.append(image)

        logger.info(f"Pexels: Found {len(images)} images for '{query}' (page {page})")
        return images


class PixabaySource(ImageSourceBase):
    """Scraper for Pixabay API."""

    BASE_URL = "https://pixabay.com/api"

    @property
    def source_name(self) -> str:
        return "pixabay"

    def search(self, query: str, page: int = 1) -> List[ScrapedImage]:
        """Search Pixabay for images."""
        if not self.api_key:
            logger.warning("Pixabay API key not configured")
            return []

        params = {
            "key": self.api_key,
            "q": query,
            "page": page,
            "per_page": min(self.config.images_per_page, 200),
            "image_type": "photo",
            "safesearch": str(self.config.safe_search).lower(),
            "min_width": self.config.min_width,
            "min_height": self.config.min_height
        }

        if self.config.preferred_orientation:
            params["orientation"] = self.config.preferred_orientation

        if self.config.color_filter:
            params["colors"] = self.config.color_filter

        data = self._make_request(self.BASE_URL, params=params)
        if not data:
            return []

        images = []
        for hit in data.get("hits", []):
            image = ScrapedImage(
                url=hit.get("largeImageURL") or hit.get("webformatURL"),
                thumbnail_url=hit.get("previewURL"),
                source="pixabay",
                source_page=hit.get("pageURL"),
                title=None,
                tags=hit.get("tags", "").split(", ") if hit.get("tags") else [],
                width=hit.get("imageWidth"),
                height=hit.get("imageHeight"),
                photographer=hit.get("user"),
                license="pixabay"
            )
            images.append(image)

        logger.info(f"Pixabay: Found {len(images)} images for '{query}' (page {page})")
        return images


class CustomWebSource(ImageSourceBase):
    """Scraper for custom botanical websites."""

    @property
    def source_name(self) -> str:
        return "custom"

    def __init__(
        self,
        base_url: str,
        selectors: Dict[str, str],
        **kwargs
    ):
        """
        Initialize custom web scraper.

        Args:
            base_url: Base URL of the website
            selectors: CSS selectors for extracting content
                - container: Main image container
                - image: Image element
                - title: Title element
                - link: Link to full image
        """
        super().__init__(**kwargs)
        self.base_url = base_url
        self.selectors = selectors

    def search(self, query: str, page: int = 1) -> List[ScrapedImage]:
        """Scrape images from custom website."""
        if not HAS_REQUESTS:
            return []

        search_url = self._build_search_url(query, page)

        if not self.rate_limiter.wait_if_needed(search_url):
            return []

        try:
            response = self.session.get(search_url, timeout=30)
            self.rate_limiter.record_request(search_url, success=True)

            if response.status_code != 200:
                logger.warning(f"Custom scraper returned {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            return self._parse_results(soup, search_url)

        except Exception as e:
            logger.error(f"Custom scraper failed: {e}")
            self.rate_limiter.record_request(search_url, success=False)
            return []

    def _build_search_url(self, query: str, page: int) -> str:
        """Build search URL for the website."""
        encoded_query = quote_plus(query)
        return f"{self.base_url}/search?q={encoded_query}&page={page}"

    def _parse_results(self, soup: BeautifulSoup, source_url: str) -> List[ScrapedImage]:
        """Parse image results from HTML."""
        images = []

        containers = soup.select(self.selectors.get("container", "img"))

        for container in containers:
            try:
                img_elem = container
                if self.selectors.get("image"):
                    img_elem = container.select_one(self.selectors["image"])

                if not img_elem:
                    continue

                src = img_elem.get("src") or img_elem.get("data-src")
                if not src:
                    continue

                image_url = urljoin(self.base_url, src)

                title = None
                if self.selectors.get("title"):
                    title_elem = container.select_one(self.selectors["title"])
                    if title_elem:
                        title = title_elem.get_text(strip=True)

                link_url = None
                if self.selectors.get("link"):
                    link_elem = container.select_one(self.selectors["link"])
                    if link_elem:
                        href = link_elem.get("href")
                        if href:
                            link_url = urljoin(self.base_url, href)

                image = ScrapedImage(
                    url=image_url,
                    source="custom",
                    source_page=link_url or source_url,
                    title=title or img_elem.get("alt"),
                    tags=self._extract_tags(container),
                    license="check-source"
                )
                images.append(image)

            except Exception as e:
                logger.debug(f"Failed to parse image element: {e}")
                continue

        return images

    def _extract_tags(self, element) -> List[str]:
        """Extract tags from element attributes and text."""
        tags = []

        alt = element.get("alt", "")
        if alt:
            tags.extend(re.findall(r'\w+', alt.lower()))

        title = element.get("title", "")
        if title:
            tags.extend(re.findall(r'\w+', title.lower()))

        return list(set(tags))[:10]


class PlantImageScraper:
    """
    Main scraper orchestrating multiple image sources.

    Features:
    - Multi-source aggregation
    - Deduplication
    - Query expansion for plant species
    - Progress tracking
    """

    PLANT_QUERY_EXPANSIONS = {
        "rose": ["rose flower", "rose bush", "rose garden", "climbing rose"],
        "tulip": ["tulip flower", "tulip bed", "tulip garden", "dutch tulip"],
        "palm": ["palm tree", "tropical palm", "palm landscape"],
        "hedge": ["hedge row", "boxwood hedge", "garden hedge", "topiary"],
        "flower bed": ["flower bed design", "annual flower bed", "perennial border"],
        "shrub": ["ornamental shrub", "flowering shrub", "landscape shrub"],
        "ground cover": ["ground cover plants", "creeping plants", "low growing plants"],
    }

    def __init__(
        self,
        api_keys: Optional[Dict[str, str]] = None,
        cache: Optional[CacheManager] = None,
        config: Optional[ScrapingConfig] = None
    ):
        """
        Initialize the plant image scraper.

        Args:
            api_keys: Dictionary of API keys for each source
            cache: Cache manager for storing results
            config: Scraping configuration
        """
        self.api_keys = api_keys or {}
        self.cache = cache
        self.config = config or ScrapingConfig()

        rate_config = RateLimitConfig(
            requests_per_second=0.5,
            min_delay_seconds=1.0,
            respect_robots_txt=True
        )
        self.rate_limiter = RateLimiter(rate_config)

        self.sources: List[ImageSourceBase] = []
        self._setup_sources()

        self._seen_urls: Set[str] = set()

        logger.info(f"Plant scraper initialized with {len(self.sources)} sources")

    def _setup_sources(self) -> None:
        """Configure image sources based on available API keys."""
        if self.api_keys.get("unsplash"):
            self.sources.append(UnsplashSource(
                api_key=self.api_keys["unsplash"],
                rate_limiter=self.rate_limiter,
                config=self.config
            ))

        if self.api_keys.get("pexels"):
            self.sources.append(PexelsSource(
                api_key=self.api_keys["pexels"],
                rate_limiter=self.rate_limiter,
                config=self.config
            ))

        if self.api_keys.get("pixabay"):
            self.sources.append(PixabaySource(
                api_key=self.api_keys["pixabay"],
                rate_limiter=self.rate_limiter,
                config=self.config
            ))

    def add_custom_source(
        self,
        base_url: str,
        selectors: Dict[str, str],
        name: Optional[str] = None
    ) -> None:
        """
        Add a custom website source.

        Args:
            base_url: Base URL of the website
            selectors: CSS selectors for content extraction
            name: Optional name for the source
        """
        source = CustomWebSource(
            base_url=base_url,
            selectors=selectors,
            rate_limiter=self.rate_limiter,
            config=self.config
        )
        self.sources.append(source)
        logger.info(f"Added custom source: {base_url}")

    def scrape(
        self,
        queries: List[str],
        expand_queries: bool = True,
        max_total: Optional[int] = None
    ) -> Generator[ScrapedImage, None, None]:
        """
        Scrape images for given queries from all sources.

        Args:
            queries: Search queries (plant names, descriptions)
            expand_queries: Whether to expand queries with variations
            max_total: Maximum total images to return

        Yields:
            ScrapedImage objects
        """
        if not self.sources:
            logger.warning("No image sources configured")
            return

        all_queries = set(queries)
        if expand_queries:
            for query in queries:
                query_lower = query.lower()
                for key, expansions in self.PLANT_QUERY_EXPANSIONS.items():
                    if key in query_lower:
                        all_queries.update(expansions)

        total_scraped = 0
        max_total = max_total or self.config.max_images_per_query * len(all_queries)

        for query in all_queries:
            if total_scraped >= max_total:
                break

            logger.info(f"Scraping images for: {query}")

            for page in range(1, self.config.max_pages + 1):
                if total_scraped >= max_total:
                    break

                page_images = []

                for source in self.sources:
                    if total_scraped >= max_total:
                        break

                    try:
                        images = source.search(query, page)

                        for img in images:
                            if img.url in self._seen_urls:
                                continue

                            self._seen_urls.add(img.url)
                            page_images.append(img)

                    except Exception as e:
                        logger.error(f"Source {source.source_name} failed: {e}")

                if not page_images:
                    break

                for img in page_images:
                    if total_scraped >= max_total:
                        break

                    if self.cache:
                        self.cache.cache_metadata(
                            img.url,
                            {
                                "source": img.source,
                                "title": img.title,
                                "tags": img.tags,
                                "scraped_at": img.scraped_at
                            },
                            category="scraped_images"
                        )

                    yield img
                    total_scraped += 1

        logger.info(f"Scraping complete: {total_scraped} unique images")

    def scrape_species_dataset(
        self,
        species_list: List[str],
        images_per_species: int = 50
    ) -> Dict[str, List[ScrapedImage]]:
        """
        Build a dataset organized by plant species.

        Args:
            species_list: List of plant species names
            images_per_species: Target images per species

        Returns:
            Dictionary mapping species to scraped images
        """
        dataset = {}

        for species in species_list:
            logger.info(f"Scraping {images_per_species} images for: {species}")

            species_images = list(self.scrape(
                queries=[species],
                expand_queries=True,
                max_total=images_per_species
            ))

            dataset[species] = species_images
            logger.info(f"Collected {len(species_images)} images for {species}")

        return dataset

    def scrape_arrangement_dataset(
        self,
        arrangement_types: List[str],
        images_per_type: int = 100
    ) -> Dict[str, List[ScrapedImage]]:
        """
        Build a dataset organized by arrangement type.

        Args:
            arrangement_types: Types like "flower bed", "hedge row", etc.
            images_per_type: Target images per type

        Returns:
            Dictionary mapping arrangement types to images
        """
        arrangement_queries = {
            "flower_bed": [
                "flower bed garden", "annual flower bed",
                "perennial flower border", "mixed flower bed"
            ],
            "hedge_row": [
                "formal hedge", "boxwood hedge", "hedge garden",
                "trimmed hedge row", "garden hedge border"
            ],
            "tree_cluster": [
                "tree grouping landscape", "specimen tree garden",
                "ornamental tree cluster", "shade tree landscape"
            ],
            "ground_cover": [
                "ground cover garden", "low growing plants",
                "creeping plants landscape", "lawn alternative plants"
            ],
            "layered_planting": [
                "layered garden design", "tiered planting",
                "mixed border garden", "cottage garden layers"
            ],
            "focal_point": [
                "garden focal point", "specimen plant",
                "feature tree", "ornamental centerpiece"
            ],
            "disney_style": [
                "Disney garden", "theme park landscaping",
                "formal garden design", "immersive landscape",
                "manicured garden", "fantasy garden"
            ]
        }

        dataset = {}

        for arr_type in arrangement_types:
            queries = arrangement_queries.get(
                arr_type,
                [arr_type, f"{arr_type} garden", f"{arr_type} landscape"]
            )

            logger.info(f"Scraping images for arrangement: {arr_type}")

            arr_images = list(self.scrape(
                queries=queries,
                expand_queries=False,
                max_total=images_per_type
            ))

            dataset[arr_type] = arr_images

        return dataset

    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics."""
        return {
            "sources_configured": len(self.sources),
            "source_names": [s.source_name for s in self.sources],
            "unique_urls_seen": len(self._seen_urls),
            "rate_limiter": self.rate_limiter.get_stats(),
            "config": {
                "max_images_per_query": self.config.max_images_per_query,
                "max_pages": self.config.max_pages,
                "min_dimensions": f"{self.config.min_width}x{self.config.min_height}"
            }
        }

    def reset(self) -> None:
        """Reset scraper state."""
        self._seen_urls.clear()
        self.rate_limiter.reset_all()
        logger.info("Scraper state reset")
