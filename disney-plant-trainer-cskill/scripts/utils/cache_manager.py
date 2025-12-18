"""
Cache Manager for Disney Plant Trainer

Provides persistent caching for:
- Downloaded images (file-based)
- API responses (JSON-based)
- Scraped metadata (SQLite-based)
- Model checkpoints
"""

import hashlib
import json
import os
import shutil
import sqlite3
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached item with metadata."""
    key: str
    value_type: str
    file_path: Optional[str]
    created_at: float
    expires_at: Optional[float]
    metadata: Dict[str, Any]
    hit_count: int = 0
    last_accessed: Optional[float] = None


class CacheManager:
    """
    Multi-tier caching system for image datasets and metadata.

    Features:
    - File-based image caching with deduplication
    - SQLite metadata storage for fast lookups
    - TTL-based expiration
    - LRU eviction when cache exceeds size limits
    - Cache statistics and health monitoring
    """

    DEFAULT_TTL_DAYS = 30
    DEFAULT_MAX_SIZE_GB = 10

    def __init__(
        self,
        cache_dir: Union[str, Path],
        max_size_gb: float = DEFAULT_MAX_SIZE_GB,
        default_ttl_days: int = DEFAULT_TTL_DAYS
    ):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Base directory for cache storage
            max_size_gb: Maximum cache size in gigabytes
            default_ttl_days: Default time-to-live for cached items
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
        self.default_ttl_seconds = default_ttl_days * 24 * 60 * 60

        self._setup_directories()
        self._init_database()

        logger.info(f"Cache initialized at {self.cache_dir} (max {max_size_gb}GB)")

    def _setup_directories(self) -> None:
        """Create cache directory structure."""
        self.images_dir = self.cache_dir / "images"
        self.responses_dir = self.cache_dir / "responses"
        self.models_dir = self.cache_dir / "models"
        self.db_path = self.cache_dir / "cache_index.db"

        for directory in [self.images_dir, self.responses_dir, self.models_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _init_database(self) -> None:
        """Initialize SQLite database for cache index."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value_type TEXT NOT NULL,
                    file_path TEXT,
                    created_at REAL NOT NULL,
                    expires_at REAL,
                    metadata TEXT,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed REAL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON cache_entries(expires_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_value_type
                ON cache_entries(value_type)
            """)
            conn.commit()

    def _generate_key(self, identifier: str, prefix: str = "") -> str:
        """Generate a unique cache key from an identifier."""
        hash_input = f"{prefix}:{identifier}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()[:32]

    def _get_image_path(self, key: str, extension: str = ".jpg") -> Path:
        """Get the file path for a cached image using sharding."""
        shard = key[:2]
        shard_dir = self.images_dir / shard
        shard_dir.mkdir(exist_ok=True)
        return shard_dir / f"{key}{extension}"

    def cache_image(
        self,
        url: str,
        image_data: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_days: Optional[int] = None
    ) -> str:
        """
        Cache an image with its metadata.

        Args:
            url: Source URL of the image
            image_data: Raw image bytes
            metadata: Additional metadata to store
            ttl_days: Time-to-live in days (None for default)

        Returns:
            Cache key for the stored image
        """
        key = self._generate_key(url, prefix="image")
        extension = self._detect_image_extension(image_data)
        file_path = self._get_image_path(key, extension)

        file_path.write_bytes(image_data)

        ttl_seconds = (ttl_days or self.default_ttl_days) * 24 * 60 * 60
        now = time.time()

        entry = CacheEntry(
            key=key,
            value_type="image",
            file_path=str(file_path),
            created_at=now,
            expires_at=now + ttl_seconds if ttl_seconds else None,
            metadata=metadata or {}
        )

        self._store_entry(entry)
        logger.debug(f"Cached image: {key} from {url}")

        return key

    def _detect_image_extension(self, image_data: bytes) -> str:
        """Detect image format from magic bytes."""
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            return ".png"
        elif image_data[:2] == b'\xff\xd8':
            return ".jpg"
        elif image_data[:6] in (b'GIF87a', b'GIF89a'):
            return ".gif"
        elif image_data[:4] == b'RIFF' and image_data[8:12] == b'WEBP':
            return ".webp"
        return ".jpg"

    def get_image(self, url: str) -> Optional[bytes]:
        """
        Retrieve a cached image by its source URL.

        Args:
            url: Original source URL

        Returns:
            Image bytes if cached and valid, None otherwise
        """
        key = self._generate_key(url, prefix="image")
        entry = self._get_entry(key)

        if entry is None:
            return None

        if entry.expires_at and time.time() > entry.expires_at:
            self.invalidate(key)
            return None

        if entry.file_path and Path(entry.file_path).exists():
            self._update_access(key)
            return Path(entry.file_path).read_bytes()

        return None

    def cache_response(
        self,
        url: str,
        response_data: Dict[str, Any],
        ttl_hours: int = 24
    ) -> str:
        """
        Cache an API response.

        Args:
            url: API endpoint URL
            response_data: Response data to cache
            ttl_hours: Time-to-live in hours

        Returns:
            Cache key
        """
        key = self._generate_key(url, prefix="response")
        file_path = self.responses_dir / f"{key}.json"

        file_path.write_text(json.dumps(response_data, indent=2))

        now = time.time()
        ttl_seconds = ttl_hours * 60 * 60

        entry = CacheEntry(
            key=key,
            value_type="response",
            file_path=str(file_path),
            created_at=now,
            expires_at=now + ttl_seconds,
            metadata={"url": url}
        )

        self._store_entry(entry)
        return key

    def get_response(self, url: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached API response."""
        key = self._generate_key(url, prefix="response")
        entry = self._get_entry(key)

        if entry is None:
            return None

        if entry.expires_at and time.time() > entry.expires_at:
            self.invalidate(key)
            return None

        if entry.file_path and Path(entry.file_path).exists():
            self._update_access(key)
            return json.loads(Path(entry.file_path).read_text())

        return None

    def cache_metadata(
        self,
        identifier: str,
        metadata: Dict[str, Any],
        category: str = "general"
    ) -> str:
        """
        Cache arbitrary metadata without a file.

        Args:
            identifier: Unique identifier for the metadata
            metadata: Metadata dictionary to store
            category: Category for organization

        Returns:
            Cache key
        """
        key = self._generate_key(identifier, prefix=f"meta:{category}")
        now = time.time()

        entry = CacheEntry(
            key=key,
            value_type=f"metadata:{category}",
            file_path=None,
            created_at=now,
            expires_at=None,
            metadata=metadata
        )

        self._store_entry(entry)
        return key

    def get_metadata(self, identifier: str, category: str = "general") -> Optional[Dict[str, Any]]:
        """Retrieve cached metadata."""
        key = self._generate_key(identifier, prefix=f"meta:{category}")
        entry = self._get_entry(key)

        if entry:
            self._update_access(key)
            return entry.metadata
        return None

    def _store_entry(self, entry: CacheEntry) -> None:
        """Store a cache entry in the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache_entries
                (key, value_type, file_path, created_at, expires_at, metadata, hit_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.key,
                entry.value_type,
                entry.file_path,
                entry.created_at,
                entry.expires_at,
                json.dumps(entry.metadata),
                entry.hit_count,
                entry.last_accessed
            ))
            conn.commit()

    def _get_entry(self, key: str) -> Optional[CacheEntry]:
        """Retrieve a cache entry from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM cache_entries WHERE key = ?", (key,)
            )
            row = cursor.fetchone()

            if row:
                return CacheEntry(
                    key=row[0],
                    value_type=row[1],
                    file_path=row[2],
                    created_at=row[3],
                    expires_at=row[4],
                    metadata=json.loads(row[5]) if row[5] else {},
                    hit_count=row[6],
                    last_accessed=row[7]
                )
        return None

    def _update_access(self, key: str) -> None:
        """Update access statistics for a cache entry."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE cache_entries
                SET hit_count = hit_count + 1, last_accessed = ?
                WHERE key = ?
            """, (time.time(), key))
            conn.commit()

    def invalidate(self, key: str) -> bool:
        """
        Invalidate a cache entry.

        Args:
            key: Cache key to invalidate

        Returns:
            True if entry was found and removed
        """
        entry = self._get_entry(key)
        if entry is None:
            return False

        if entry.file_path:
            file_path = Path(entry.file_path)
            if file_path.exists():
                file_path.unlink()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            conn.commit()

        logger.debug(f"Invalidated cache entry: {key}")
        return True

    def cleanup_expired(self) -> int:
        """
        Remove all expired cache entries.

        Returns:
            Number of entries removed
        """
        now = time.time()
        removed = 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT key, file_path FROM cache_entries WHERE expires_at IS NOT NULL AND expires_at < ?",
                (now,)
            )

            for row in cursor.fetchall():
                key, file_path = row
                if file_path and Path(file_path).exists():
                    Path(file_path).unlink()
                removed += 1

            conn.execute(
                "DELETE FROM cache_entries WHERE expires_at IS NOT NULL AND expires_at < ?",
                (now,)
            )
            conn.commit()

        logger.info(f"Cleaned up {removed} expired cache entries")
        return removed

    def evict_lru(self, target_size_bytes: Optional[int] = None) -> int:
        """
        Evict least recently used entries until under size limit.

        Args:
            target_size_bytes: Target size (defaults to max_size_bytes)

        Returns:
            Number of entries evicted
        """
        target = target_size_bytes or self.max_size_bytes
        current_size = self.get_cache_size()

        if current_size <= target:
            return 0

        evicted = 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key, file_path FROM cache_entries
                ORDER BY COALESCE(last_accessed, created_at) ASC
            """)

            for row in cursor.fetchall():
                if current_size <= target:
                    break

                key, file_path = row
                if file_path:
                    file_path = Path(file_path)
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        current_size -= file_size

                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                evicted += 1

            conn.commit()

        logger.info(f"Evicted {evicted} LRU cache entries")
        return evicted

    def get_cache_size(self) -> int:
        """Get total size of cached files in bytes."""
        total = 0
        for directory in [self.images_dir, self.responses_dir, self.models_dir]:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total += file_path.stat().st_size
        return total

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            total_entries = conn.execute(
                "SELECT COUNT(*) FROM cache_entries"
            ).fetchone()[0]

            by_type = dict(conn.execute(
                "SELECT value_type, COUNT(*) FROM cache_entries GROUP BY value_type"
            ).fetchall())

            total_hits = conn.execute(
                "SELECT SUM(hit_count) FROM cache_entries"
            ).fetchone()[0] or 0

        size_bytes = self.get_cache_size()

        return {
            "total_entries": total_entries,
            "entries_by_type": by_type,
            "total_hits": total_hits,
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "max_size_gb": self.max_size_bytes / (1024 * 1024 * 1024),
            "utilization_percent": round(size_bytes / self.max_size_bytes * 100, 2)
        }

    def clear(self, value_type: Optional[str] = None) -> int:
        """
        Clear cache entries.

        Args:
            value_type: If specified, only clear entries of this type

        Returns:
            Number of entries cleared
        """
        with sqlite3.connect(self.db_path) as conn:
            if value_type:
                cursor = conn.execute(
                    "SELECT key, file_path FROM cache_entries WHERE value_type = ?",
                    (value_type,)
                )
            else:
                cursor = conn.execute("SELECT key, file_path FROM cache_entries")

            cleared = 0
            for row in cursor.fetchall():
                key, file_path = row
                if file_path and Path(file_path).exists():
                    Path(file_path).unlink()
                cleared += 1

            if value_type:
                conn.execute(
                    "DELETE FROM cache_entries WHERE value_type = ?",
                    (value_type,)
                )
            else:
                conn.execute("DELETE FROM cache_entries")

            conn.commit()

        logger.info(f"Cleared {cleared} cache entries" +
                   (f" of type {value_type}" if value_type else ""))
        return cleared

    def list_entries(
        self,
        value_type: Optional[str] = None,
        limit: int = 100
    ) -> List[CacheEntry]:
        """
        List cache entries.

        Args:
            value_type: Filter by type
            limit: Maximum entries to return

        Returns:
            List of cache entries
        """
        with sqlite3.connect(self.db_path) as conn:
            if value_type:
                cursor = conn.execute(
                    "SELECT * FROM cache_entries WHERE value_type = ? ORDER BY created_at DESC LIMIT ?",
                    (value_type, limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM cache_entries ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )

            entries = []
            for row in cursor.fetchall():
                entries.append(CacheEntry(
                    key=row[0],
                    value_type=row[1],
                    file_path=row[2],
                    created_at=row[3],
                    expires_at=row[4],
                    metadata=json.loads(row[5]) if row[5] else {},
                    hit_count=row[6],
                    last_accessed=row[7]
                ))

            return entries
