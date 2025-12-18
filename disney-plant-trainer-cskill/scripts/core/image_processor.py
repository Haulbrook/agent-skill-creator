"""
Image Processor for Disney Plant Trainer

Preprocessing and augmentation for training:
- Resize and normalize
- Color adjustments
- Geometric transforms
- Data augmentation pipeline
"""

import io
import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

logger = logging.getLogger(__name__)


class ResizeMode(Enum):
    """Image resize modes."""
    CONTAIN = "contain"
    COVER = "cover"
    STRETCH = "stretch"
    PAD = "pad"


@dataclass
class ProcessingConfig:
    """Configuration for image processing."""
    target_size: Tuple[int, int] = (512, 512)
    resize_mode: ResizeMode = ResizeMode.CONTAIN
    pad_color: Tuple[int, int, int] = (0, 0, 0)
    normalize: bool = True
    normalize_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    normalize_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)
    output_format: str = "RGB"
    quality: int = 95


@dataclass
class AugmentationConfig:
    """Configuration for data augmentation."""
    enabled: bool = True
    horizontal_flip: float = 0.5
    vertical_flip: float = 0.0
    rotation_range: Tuple[float, float] = (-15, 15)
    rotation_prob: float = 0.3
    brightness_range: Tuple[float, float] = (0.8, 1.2)
    brightness_prob: float = 0.3
    contrast_range: Tuple[float, float] = (0.8, 1.2)
    contrast_prob: float = 0.3
    saturation_range: Tuple[float, float] = (0.8, 1.2)
    saturation_prob: float = 0.3
    blur_prob: float = 0.1
    blur_radius: Tuple[float, float] = (0.5, 1.5)
    crop_scale_range: Tuple[float, float] = (0.8, 1.0)
    crop_prob: float = 0.3
    noise_prob: float = 0.1
    noise_std: float = 0.02


@dataclass
class ProcessedImage:
    """Result of image processing."""
    image: Image.Image
    original_size: Tuple[int, int]
    processed_size: Tuple[int, int]
    augmentations_applied: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ImageProcessor:
    """
    Image processor for plant training dataset preparation.

    Features:
    - Configurable resize and padding
    - Standard preprocessing pipeline
    - Data augmentation for training
    - Batch processing support
    - Export to various formats
    """

    def __init__(
        self,
        config: Optional[ProcessingConfig] = None,
        augmentation: Optional[AugmentationConfig] = None
    ):
        """
        Initialize the image processor.

        Args:
            config: Processing configuration
            augmentation: Augmentation configuration
        """
        if not HAS_PIL:
            raise ImportError("PIL is required for image processing")

        self.config = config or ProcessingConfig()
        self.augmentation = augmentation or AugmentationConfig()

        logger.info(
            f"Image processor initialized: target={self.config.target_size}, "
            f"augmentation={'enabled' if self.augmentation.enabled else 'disabled'}"
        )

    def process(
        self,
        image: Union[Image.Image, bytes, str, Path],
        augment: bool = False
    ) -> ProcessedImage:
        """
        Process a single image.

        Args:
            image: PIL Image, bytes, or file path
            augment: Whether to apply augmentation

        Returns:
            ProcessedImage with processed image and metadata
        """
        img = self._load_image(image)
        original_size = img.size
        augmentations = []

        img = img.convert(self.config.output_format)

        if augment and self.augmentation.enabled:
            img, augmentations = self._apply_augmentation(img)

        img = self._resize(img)

        if self.config.normalize:
            pass

        return ProcessedImage(
            image=img,
            original_size=original_size,
            processed_size=img.size,
            augmentations_applied=augmentations,
            metadata={"format": self.config.output_format}
        )

    def _load_image(self, image: Union[Image.Image, bytes, str, Path]) -> Image.Image:
        """Load image from various sources."""
        if isinstance(image, Image.Image):
            return image.copy()
        elif isinstance(image, bytes):
            return Image.open(io.BytesIO(image))
        elif isinstance(image, (str, Path)):
            return Image.open(image)
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")

    def _resize(self, img: Image.Image) -> Image.Image:
        """Resize image according to configuration."""
        target_w, target_h = self.config.target_size
        orig_w, orig_h = img.size

        if self.config.resize_mode == ResizeMode.STRETCH:
            return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        elif self.config.resize_mode == ResizeMode.CONTAIN:
            ratio = min(target_w / orig_w, target_h / orig_h)
            new_w = int(orig_w * ratio)
            new_h = int(orig_h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            result = Image.new(self.config.output_format, (target_w, target_h), self.config.pad_color)
            paste_x = (target_w - new_w) // 2
            paste_y = (target_h - new_h) // 2
            result.paste(img, (paste_x, paste_y))
            return result

        elif self.config.resize_mode == ResizeMode.COVER:
            ratio = max(target_w / orig_w, target_h / orig_h)
            new_w = int(orig_w * ratio)
            new_h = int(orig_h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            return img.crop((left, top, left + target_w, top + target_h))

        elif self.config.resize_mode == ResizeMode.PAD:
            img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            result = Image.new(self.config.output_format, (target_w, target_h), self.config.pad_color)
            paste_x = (target_w - img.width) // 2
            paste_y = (target_h - img.height) // 2
            result.paste(img, (paste_x, paste_y))
            return result

        return img

    def _apply_augmentation(
        self,
        img: Image.Image
    ) -> Tuple[Image.Image, List[str]]:
        """Apply random augmentations to image."""
        applied = []

        if random.random() < self.augmentation.horizontal_flip:
            img = ImageOps.mirror(img)
            applied.append("horizontal_flip")

        if random.random() < self.augmentation.vertical_flip:
            img = ImageOps.flip(img)
            applied.append("vertical_flip")

        if random.random() < self.augmentation.rotation_prob:
            angle = random.uniform(*self.augmentation.rotation_range)
            img = img.rotate(angle, resample=Image.Resampling.BILINEAR, expand=False, fillcolor=self.config.pad_color)
            applied.append(f"rotation_{angle:.1f}")

        if random.random() < self.augmentation.crop_prob:
            scale = random.uniform(*self.augmentation.crop_scale_range)
            w, h = img.size
            new_w = int(w * scale)
            new_h = int(h * scale)
            left = random.randint(0, w - new_w)
            top = random.randint(0, h - new_h)
            img = img.crop((left, top, left + new_w, top + new_h))
            img = img.resize((w, h), Image.Resampling.LANCZOS)
            applied.append(f"crop_{scale:.2f}")

        if random.random() < self.augmentation.brightness_prob:
            factor = random.uniform(*self.augmentation.brightness_range)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(factor)
            applied.append(f"brightness_{factor:.2f}")

        if random.random() < self.augmentation.contrast_prob:
            factor = random.uniform(*self.augmentation.contrast_range)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(factor)
            applied.append(f"contrast_{factor:.2f}")

        if random.random() < self.augmentation.saturation_prob:
            factor = random.uniform(*self.augmentation.saturation_range)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(factor)
            applied.append(f"saturation_{factor:.2f}")

        if random.random() < self.augmentation.blur_prob:
            radius = random.uniform(*self.augmentation.blur_radius)
            img = img.filter(ImageFilter.GaussianBlur(radius=radius))
            applied.append(f"blur_{radius:.2f}")

        if random.random() < self.augmentation.noise_prob and HAS_NUMPY:
            img = self._add_noise(img)
            applied.append("noise")

        return img, applied

    def _add_noise(self, img: Image.Image) -> Image.Image:
        """Add Gaussian noise to image."""
        if not HAS_NUMPY:
            return img

        arr = np.array(img).astype(np.float32) / 255.0
        noise = np.random.normal(0, self.augmentation.noise_std, arr.shape)
        arr = np.clip(arr + noise, 0, 1)
        arr = (arr * 255).astype(np.uint8)

        return Image.fromarray(arr)

    def process_batch(
        self,
        images: List[Union[Image.Image, bytes, str, Path]],
        augment: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ProcessedImage]:
        """
        Process multiple images.

        Args:
            images: List of images to process
            augment: Whether to apply augmentation
            progress_callback: Callback(current, total) for progress

        Returns:
            List of ProcessedImage results
        """
        results = []

        for i, image in enumerate(images):
            try:
                result = self.process(image, augment=augment)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process image {i}: {e}")
                results.append(None)

            if progress_callback:
                progress_callback(i + 1, len(images))

        return results

    def create_augmented_variants(
        self,
        image: Union[Image.Image, bytes, str, Path],
        num_variants: int = 5
    ) -> List[ProcessedImage]:
        """
        Create multiple augmented variants of an image.

        Args:
            image: Source image
            num_variants: Number of variants to create

        Returns:
            List of augmented ProcessedImage variants
        """
        variants = []

        original = self.process(image, augment=False)
        variants.append(original)

        for _ in range(num_variants - 1):
            variant = self.process(image, augment=True)
            variants.append(variant)

        return variants

    def to_numpy(self, processed: ProcessedImage) -> 'np.ndarray':
        """
        Convert ProcessedImage to numpy array.

        Args:
            processed: ProcessedImage to convert

        Returns:
            Numpy array of shape (H, W, C)
        """
        if not HAS_NUMPY:
            raise ImportError("numpy is required for this operation")

        arr = np.array(processed.image)

        if self.config.normalize:
            arr = arr.astype(np.float32) / 255.0
            mean = np.array(self.config.normalize_mean)
            std = np.array(self.config.normalize_std)
            arr = (arr - mean) / std

        return arr

    def to_tensor_format(
        self,
        processed: ProcessedImage,
        channel_first: bool = True
    ) -> 'np.ndarray':
        """
        Convert to tensor format for deep learning frameworks.

        Args:
            processed: ProcessedImage to convert
            channel_first: If True, output shape is (C, H, W)

        Returns:
            Numpy array in tensor format
        """
        arr = self.to_numpy(processed)

        if channel_first:
            arr = np.transpose(arr, (2, 0, 1))

        return arr

    def save(
        self,
        processed: ProcessedImage,
        output_path: Union[str, Path],
        format: Optional[str] = None,
        quality: Optional[int] = None
    ) -> Path:
        """
        Save processed image to file.

        Args:
            processed: ProcessedImage to save
            output_path: Output file path
            format: Image format (inferred from extension if not specified)
            quality: JPEG quality (default from config)

        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save_kwargs = {}

        if format:
            save_format = format.upper()
        else:
            ext = output_path.suffix.lower()
            format_map = {
                ".jpg": "JPEG",
                ".jpeg": "JPEG",
                ".png": "PNG",
                ".webp": "WEBP",
                ".gif": "GIF"
            }
            save_format = format_map.get(ext, "JPEG")

        if save_format == "JPEG":
            save_kwargs["quality"] = quality or self.config.quality
            save_kwargs["optimize"] = True

        processed.image.save(output_path, format=save_format, **save_kwargs)

        return output_path

    def create_grid(
        self,
        images: List[ProcessedImage],
        grid_size: Optional[Tuple[int, int]] = None,
        spacing: int = 2,
        background: Tuple[int, int, int] = (255, 255, 255)
    ) -> Image.Image:
        """
        Create a grid visualization of multiple images.

        Args:
            images: List of ProcessedImage to arrange
            grid_size: (rows, cols) or None for auto
            spacing: Pixels between images
            background: Background color

        Returns:
            PIL Image of the grid
        """
        if not images:
            raise ValueError("No images provided")

        n = len(images)

        if grid_size:
            rows, cols = grid_size
        else:
            cols = int(n ** 0.5)
            rows = (n + cols - 1) // cols

        img_w, img_h = images[0].processed_size

        grid_w = cols * img_w + (cols - 1) * spacing
        grid_h = rows * img_h + (rows - 1) * spacing

        grid = Image.new("RGB", (grid_w, grid_h), background)

        for idx, processed in enumerate(images):
            if idx >= rows * cols:
                break

            row = idx // cols
            col = idx % cols

            x = col * (img_w + spacing)
            y = row * (img_h + spacing)

            grid.paste(processed.image, (x, y))

        return grid

    def extract_color_palette(
        self,
        image: Union[Image.Image, ProcessedImage],
        num_colors: int = 5
    ) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from image.

        Args:
            image: Image to analyze
            num_colors: Number of colors to extract

        Returns:
            List of RGB tuples
        """
        if isinstance(image, ProcessedImage):
            img = image.image
        else:
            img = image

        img = img.convert("RGB")
        small = img.resize((50, 50), Image.Resampling.LANCZOS)

        quantized = small.quantize(colors=num_colors)
        palette = quantized.getpalette()[:num_colors * 3]

        colors = []
        for i in range(0, len(palette), 3):
            colors.append((palette[i], palette[i + 1], palette[i + 2]))

        return colors

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            "processing": {
                "target_size": self.config.target_size,
                "resize_mode": self.config.resize_mode.value,
                "normalize": self.config.normalize,
                "output_format": self.config.output_format
            },
            "augmentation": {
                "enabled": self.augmentation.enabled,
                "horizontal_flip": self.augmentation.horizontal_flip,
                "rotation_range": self.augmentation.rotation_range,
                "brightness_range": self.augmentation.brightness_range
            }
        }


def preprocess_for_training(
    image_path: Union[str, Path],
    target_size: Tuple[int, int] = (224, 224),
    augment: bool = True
) -> 'np.ndarray':
    """
    Convenience function for training preprocessing.

    Args:
        image_path: Path to image
        target_size: Target dimensions
        augment: Whether to apply augmentation

    Returns:
        Numpy array ready for model input
    """
    config = ProcessingConfig(target_size=target_size)
    augmentation = AugmentationConfig(enabled=augment)
    processor = ImageProcessor(config, augmentation)

    processed = processor.process(image_path, augment=augment)
    return processor.to_tensor_format(processed)
