"""
Image Validator for Disney Plant Trainer

Validates downloaded images for:
- File integrity and format
- Minimum quality requirements
- Plant content detection
- Duplicate detection
"""

import hashlib
import io
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

try:
    from PIL import Image, ImageStat
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import imagehash
    HAS_IMAGEHASH = True
except ImportError:
    HAS_IMAGEHASH = False

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Result codes for image validation."""
    VALID = "valid"
    INVALID_FORMAT = "invalid_format"
    TOO_SMALL = "too_small"
    TOO_LARGE = "too_large"
    CORRUPT = "corrupt"
    LOW_QUALITY = "low_quality"
    DUPLICATE = "duplicate"
    NOT_PLANT = "not_plant"
    GRAYSCALE = "grayscale"
    ASPECT_RATIO = "bad_aspect_ratio"


@dataclass
class ValidationReport:
    """Detailed validation report for an image."""
    result: ValidationResult
    is_valid: bool
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    file_size: Optional[int] = None
    hash_value: Optional[str] = None
    perceptual_hash: Optional[str] = None
    quality_score: Optional[float] = None
    color_stats: Optional[Dict[str, Any]] = None
    warnings: List[str] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []


@dataclass
class ValidationConfig:
    """Configuration for image validation."""
    min_width: int = 256
    min_height: int = 256
    max_width: int = 8192
    max_height: int = 8192
    max_file_size_mb: float = 50.0
    min_aspect_ratio: float = 0.25
    max_aspect_ratio: float = 4.0
    min_quality_score: float = 0.3
    allowed_formats: Set[str] = None
    require_color: bool = True
    check_duplicates: bool = True

    def __post_init__(self):
        if self.allowed_formats is None:
            self.allowed_formats = {"JPEG", "PNG", "WEBP", "GIF"}


class ImageValidator:
    """
    Comprehensive image validation for plant training datasets.

    Features:
    - Format and integrity checking
    - Quality assessment
    - Duplicate detection via perceptual hashing
    - Color analysis for plant content hints
    - Batch validation with reporting
    """

    def __init__(self, config: Optional[ValidationConfig] = None):
        """
        Initialize the image validator.

        Args:
            config: Validation configuration
        """
        self.config = config or ValidationConfig()
        self._seen_hashes: Set[str] = set()
        self._seen_perceptual_hashes: Dict[str, str] = {}

        if not HAS_PIL:
            logger.warning("PIL not available - limited validation")

        if not HAS_IMAGEHASH:
            logger.warning("imagehash not available - no perceptual duplicate detection")

    def validate(
        self,
        image_data: Union[bytes, Path, str],
        check_content: bool = True
    ) -> ValidationReport:
        """
        Validate an image.

        Args:
            image_data: Image bytes, file path, or URL
            check_content: Whether to perform content analysis

        Returns:
            ValidationReport with results
        """
        if not HAS_PIL:
            return self._basic_validation(image_data)

        try:
            if isinstance(image_data, (str, Path)):
                path = Path(image_data)
                if not path.exists():
                    return ValidationReport(
                        result=ValidationResult.CORRUPT,
                        is_valid=False,
                        errors=["File not found"]
                    )
                raw_bytes = path.read_bytes()
            else:
                raw_bytes = image_data

            return self._full_validation(raw_bytes, check_content)

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationReport(
                result=ValidationResult.CORRUPT,
                is_valid=False,
                errors=[str(e)]
            )

    def _basic_validation(self, image_data: Union[bytes, Path]) -> ValidationReport:
        """Basic validation without PIL."""
        if isinstance(image_data, (str, Path)):
            raw_bytes = Path(image_data).read_bytes()
        else:
            raw_bytes = image_data

        file_size = len(raw_bytes)
        max_bytes = int(self.config.max_file_size_mb * 1024 * 1024)

        if file_size > max_bytes:
            return ValidationReport(
                result=ValidationResult.TOO_LARGE,
                is_valid=False,
                file_size=file_size,
                errors=[f"File too large: {file_size / (1024*1024):.1f}MB"]
            )

        fmt = self._detect_format_from_bytes(raw_bytes)
        hash_value = hashlib.md5(raw_bytes).hexdigest()

        if self.config.check_duplicates and hash_value in self._seen_hashes:
            return ValidationReport(
                result=ValidationResult.DUPLICATE,
                is_valid=False,
                file_size=file_size,
                format=fmt,
                hash_value=hash_value,
                errors=["Duplicate image (exact match)"]
            )

        self._seen_hashes.add(hash_value)

        return ValidationReport(
            result=ValidationResult.VALID,
            is_valid=True,
            file_size=file_size,
            format=fmt,
            hash_value=hash_value
        )

    def _full_validation(
        self,
        raw_bytes: bytes,
        check_content: bool
    ) -> ValidationReport:
        """Full validation with PIL."""
        warnings = []
        errors = []
        file_size = len(raw_bytes)

        max_bytes = int(self.config.max_file_size_mb * 1024 * 1024)
        if file_size > max_bytes:
            return ValidationReport(
                result=ValidationResult.TOO_LARGE,
                is_valid=False,
                file_size=file_size,
                errors=[f"File too large: {file_size / (1024*1024):.1f}MB"]
            )

        try:
            img = Image.open(io.BytesIO(raw_bytes))
            img.verify()
            img = Image.open(io.BytesIO(raw_bytes))
        except Exception as e:
            return ValidationReport(
                result=ValidationResult.CORRUPT,
                is_valid=False,
                file_size=file_size,
                errors=[f"Corrupt image: {e}"]
            )

        width, height = img.size
        fmt = img.format

        if fmt not in self.config.allowed_formats:
            return ValidationReport(
                result=ValidationResult.INVALID_FORMAT,
                is_valid=False,
                width=width,
                height=height,
                format=fmt,
                file_size=file_size,
                errors=[f"Format {fmt} not allowed"]
            )

        if width < self.config.min_width or height < self.config.min_height:
            return ValidationReport(
                result=ValidationResult.TOO_SMALL,
                is_valid=False,
                width=width,
                height=height,
                format=fmt,
                file_size=file_size,
                errors=[f"Image too small: {width}x{height}"]
            )

        if width > self.config.max_width or height > self.config.max_height:
            return ValidationReport(
                result=ValidationResult.TOO_LARGE,
                is_valid=False,
                width=width,
                height=height,
                format=fmt,
                file_size=file_size,
                errors=[f"Image too large: {width}x{height}"]
            )

        aspect_ratio = width / height
        if (aspect_ratio < self.config.min_aspect_ratio or
            aspect_ratio > self.config.max_aspect_ratio):
            return ValidationReport(
                result=ValidationResult.ASPECT_RATIO,
                is_valid=False,
                width=width,
                height=height,
                format=fmt,
                file_size=file_size,
                errors=[f"Bad aspect ratio: {aspect_ratio:.2f}"]
            )

        hash_value = hashlib.md5(raw_bytes).hexdigest()

        if self.config.check_duplicates and hash_value in self._seen_hashes:
            return ValidationReport(
                result=ValidationResult.DUPLICATE,
                is_valid=False,
                width=width,
                height=height,
                format=fmt,
                file_size=file_size,
                hash_value=hash_value,
                errors=["Duplicate image (exact match)"]
            )

        perceptual_hash = None
        if HAS_IMAGEHASH and self.config.check_duplicates:
            try:
                phash = imagehash.phash(img)
                perceptual_hash = str(phash)

                for seen_phash, seen_key in self._seen_perceptual_hashes.items():
                    if phash - imagehash.hex_to_hash(seen_phash) < 5:
                        return ValidationReport(
                            result=ValidationResult.DUPLICATE,
                            is_valid=False,
                            width=width,
                            height=height,
                            format=fmt,
                            file_size=file_size,
                            hash_value=hash_value,
                            perceptual_hash=perceptual_hash,
                            errors=[f"Near-duplicate of {seen_key}"]
                        )

                self._seen_perceptual_hashes[perceptual_hash] = hash_value
            except Exception as e:
                warnings.append(f"Could not compute perceptual hash: {e}")

        if self.config.require_color and img.mode in ("L", "1"):
            return ValidationReport(
                result=ValidationResult.GRAYSCALE,
                is_valid=False,
                width=width,
                height=height,
                format=fmt,
                file_size=file_size,
                hash_value=hash_value,
                errors=["Image is grayscale, color required"]
            )

        quality_score = None
        color_stats = None

        if check_content:
            quality_score = self._compute_quality_score(img)
            color_stats = self._analyze_colors(img)

            if quality_score < self.config.min_quality_score:
                return ValidationReport(
                    result=ValidationResult.LOW_QUALITY,
                    is_valid=False,
                    width=width,
                    height=height,
                    format=fmt,
                    file_size=file_size,
                    hash_value=hash_value,
                    perceptual_hash=perceptual_hash,
                    quality_score=quality_score,
                    color_stats=color_stats,
                    errors=[f"Quality score {quality_score:.2f} below threshold"]
                )

            if color_stats.get("green_ratio", 0) < 0.05:
                warnings.append("Low green content - may not contain plants")

        self._seen_hashes.add(hash_value)

        return ValidationReport(
            result=ValidationResult.VALID,
            is_valid=True,
            width=width,
            height=height,
            format=fmt,
            file_size=file_size,
            hash_value=hash_value,
            perceptual_hash=perceptual_hash,
            quality_score=quality_score,
            color_stats=color_stats,
            warnings=warnings
        )

    def _detect_format_from_bytes(self, data: bytes) -> Optional[str]:
        """Detect image format from magic bytes."""
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return "PNG"
        elif data[:2] == b'\xff\xd8':
            return "JPEG"
        elif data[:6] in (b'GIF87a', b'GIF89a'):
            return "GIF"
        elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            return "WEBP"
        return None

    def _compute_quality_score(self, img: Image.Image) -> float:
        """
        Compute a quality score for the image.

        Higher scores indicate:
        - Good contrast
        - Sharp focus
        - Proper exposure
        """
        try:
            if img.mode != "RGB":
                img = img.convert("RGB")

            stat = ImageStat.Stat(img)

            mean_brightness = sum(stat.mean) / 3
            brightness_score = 1 - abs(mean_brightness - 128) / 128

            stddev = sum(stat.stddev) / 3
            contrast_score = min(stddev / 64, 1.0)

            entropy = img.entropy()
            detail_score = min(entropy / 7, 1.0)

            weights = [0.3, 0.4, 0.3]
            quality = (
                weights[0] * brightness_score +
                weights[1] * contrast_score +
                weights[2] * detail_score
            )

            return round(quality, 3)

        except Exception as e:
            logger.warning(f"Quality computation failed: {e}")
            return 0.5

    def _analyze_colors(self, img: Image.Image) -> Dict[str, Any]:
        """
        Analyze color distribution in the image.

        Returns metrics useful for plant detection:
        - Green ratio (higher = likely plants)
        - Color diversity
        - Dominant colors
        """
        try:
            if img.mode != "RGB":
                img = img.convert("RGB")

            small = img.resize((100, 100), Image.Resampling.LANCZOS)
            pixels = list(small.getdata())

            r_total = g_total = b_total = 0
            green_pixels = 0

            for r, g, b in pixels:
                r_total += r
                g_total += g
                b_total += b

                if g > r and g > b and g > 80:
                    green_pixels += 1

            total = len(pixels)
            avg_r = r_total / total
            avg_g = g_total / total
            avg_b = b_total / total

            green_ratio = green_pixels / total

            color_counts = {}
            for pixel in pixels:
                quantized = (pixel[0] // 32, pixel[1] // 32, pixel[2] // 32)
                color_counts[quantized] = color_counts.get(quantized, 0) + 1

            color_diversity = len(color_counts) / 512

            sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])
            dominant = [
                {"rgb": (c[0]*32, c[1]*32, c[2]*32), "ratio": count/total}
                for c, count in sorted_colors[:5]
            ]

            return {
                "average_rgb": (avg_r, avg_g, avg_b),
                "green_ratio": round(green_ratio, 3),
                "color_diversity": round(color_diversity, 3),
                "dominant_colors": dominant
            }

        except Exception as e:
            logger.warning(f"Color analysis failed: {e}")
            return {}

    def validate_batch(
        self,
        images: List[Union[bytes, Path, str]]
    ) -> Tuple[List[ValidationReport], Dict[str, Any]]:
        """
        Validate a batch of images.

        Args:
            images: List of image data/paths

        Returns:
            Tuple of (list of reports, summary statistics)
        """
        reports = []
        stats = {
            "total": len(images),
            "valid": 0,
            "invalid": 0,
            "by_result": {}
        }

        for image in images:
            report = self.validate(image)
            reports.append(report)

            if report.is_valid:
                stats["valid"] += 1
            else:
                stats["invalid"] += 1

            result_name = report.result.value
            stats["by_result"][result_name] = stats["by_result"].get(result_name, 0) + 1

        stats["valid_ratio"] = stats["valid"] / stats["total"] if stats["total"] > 0 else 0

        return reports, stats

    def reset_duplicate_tracking(self) -> None:
        """Reset duplicate detection state."""
        self._seen_hashes.clear()
        self._seen_perceptual_hashes.clear()
        logger.info("Reset duplicate tracking state")

    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics."""
        return {
            "unique_images_seen": len(self._seen_hashes),
            "perceptual_hashes_tracked": len(self._seen_perceptual_hashes),
            "config": {
                "min_dimensions": f"{self.config.min_width}x{self.config.min_height}",
                "max_dimensions": f"{self.config.max_width}x{self.config.max_height}",
                "max_file_size_mb": self.config.max_file_size_mb,
                "min_quality_score": self.config.min_quality_score,
                "require_color": self.config.require_color
            }
        }


def quick_validate(image_data: Union[bytes, Path, str]) -> bool:
    """
    Quick validation check for an image.

    Args:
        image_data: Image to validate

    Returns:
        True if image passes basic validation
    """
    validator = ImageValidator()
    report = validator.validate(image_data, check_content=False)
    return report.is_valid
