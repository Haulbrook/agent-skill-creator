"""
Dataset Organizer for Disney Plant Trainer

Manages the structure and organization of:
- Raw downloaded images
- Processed training images
- Annotation data
- Model checkpoints
- Training/validation/test splits
"""

import json
import logging
import os
import random
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ImageAnnotation:
    """Annotation for a single image."""
    image_id: str
    file_path: str
    source_url: Optional[str] = None
    plant_species: List[str] = field(default_factory=list)
    plant_positions: List[Dict[str, Any]] = field(default_factory=list)
    height_data: Dict[str, Any] = field(default_factory=dict)
    spacing_data: Dict[str, Any] = field(default_factory=dict)
    arrangement_type: Optional[str] = None
    disney_style_score: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None


@dataclass
class DatasetSplit:
    """Configuration for dataset splits."""
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    random_seed: int = 42
    stratify_by: Optional[str] = None


@dataclass
class DatasetStats:
    """Statistics for a dataset."""
    total_images: int = 0
    annotated_images: int = 0
    unique_species: int = 0
    arrangement_types: Dict[str, int] = field(default_factory=dict)
    images_by_source: Dict[str, int] = field(default_factory=dict)
    total_size_mb: float = 0.0
    train_count: int = 0
    val_count: int = 0
    test_count: int = 0


class DatasetOrganizer:
    """
    Comprehensive dataset management for plant training.

    Features:
    - Hierarchical directory structure
    - JSON-based annotation storage
    - Train/val/test splitting
    - Species-based organization
    - Dataset statistics and reporting
    """

    STRUCTURE = {
        "raw": "raw/",
        "processed": "processed/",
        "train": "splits/train/",
        "val": "splits/val/",
        "test": "splits/test/",
        "annotations": "annotations/",
        "models": "models/",
        "cache": "cache/",
        "exports": "exports/"
    }

    def __init__(self, base_dir: Union[str, Path]):
        """
        Initialize the dataset organizer.

        Args:
            base_dir: Base directory for the dataset
        """
        self.base_dir = Path(base_dir)
        self._annotations: Dict[str, ImageAnnotation] = {}
        self._species_index: Dict[str, Set[str]] = {}
        self._arrangement_index: Dict[str, Set[str]] = {}

        self._setup_directories()
        self._load_annotations()

        logger.info(f"Dataset organizer initialized at {self.base_dir}")

    def _setup_directories(self) -> None:
        """Create the dataset directory structure."""
        for name, subpath in self.STRUCTURE.items():
            dir_path = self.base_dir / subpath
            dir_path.mkdir(parents=True, exist_ok=True)
            setattr(self, f"{name}_dir", dir_path)

        self.annotations_file = self.base_dir / "annotations" / "annotations.json"
        self.stats_file = self.base_dir / "dataset_stats.json"
        self.manifest_file = self.base_dir / "manifest.json"

    def _load_annotations(self) -> None:
        """Load existing annotations from disk."""
        if self.annotations_file.exists():
            try:
                data = json.loads(self.annotations_file.read_text())
                for item in data.get("annotations", []):
                    ann = ImageAnnotation(**item)
                    self._annotations[ann.image_id] = ann
                    self._index_annotation(ann)

                logger.info(f"Loaded {len(self._annotations)} existing annotations")
            except Exception as e:
                logger.error(f"Failed to load annotations: {e}")

    def _save_annotations(self) -> None:
        """Save annotations to disk."""
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "count": len(self._annotations),
            "annotations": [asdict(ann) for ann in self._annotations.values()]
        }

        self.annotations_file.write_text(json.dumps(data, indent=2))
        logger.debug(f"Saved {len(self._annotations)} annotations")

    def _index_annotation(self, ann: ImageAnnotation) -> None:
        """Update internal indexes for an annotation."""
        for species in ann.plant_species:
            if species not in self._species_index:
                self._species_index[species] = set()
            self._species_index[species].add(ann.image_id)

        if ann.arrangement_type:
            if ann.arrangement_type not in self._arrangement_index:
                self._arrangement_index[ann.arrangement_type] = set()
            self._arrangement_index[ann.arrangement_type].add(ann.image_id)

    def add_image(
        self,
        image_data: bytes,
        source_url: Optional[str] = None,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a raw image to the dataset.

        Args:
            image_data: Raw image bytes
            source_url: Source URL of the image
            filename: Optional filename (auto-generated if not provided)
            metadata: Additional metadata

        Returns:
            Image ID
        """
        image_id = hashlib.sha256(image_data).hexdigest()[:16]

        if filename:
            ext = Path(filename).suffix or ".jpg"
        else:
            ext = self._detect_extension(image_data)

        file_path = self.raw_dir / f"{image_id}{ext}"
        file_path.write_bytes(image_data)

        annotation = ImageAnnotation(
            image_id=image_id,
            file_path=str(file_path.relative_to(self.base_dir)),
            source_url=source_url,
            metadata=metadata or {}
        )

        self._annotations[image_id] = annotation
        self._save_annotations()

        logger.debug(f"Added image {image_id} to dataset")
        return image_id

    def _detect_extension(self, data: bytes) -> str:
        """Detect file extension from image data."""
        if data[:8] == b'\x89PNG\r\n\x1a\n':
            return ".png"
        elif data[:2] == b'\xff\xd8':
            return ".jpg"
        elif data[:6] in (b'GIF87a', b'GIF89a'):
            return ".gif"
        elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
            return ".webp"
        return ".jpg"

    def annotate_image(
        self,
        image_id: str,
        plant_species: Optional[List[str]] = None,
        plant_positions: Optional[List[Dict[str, Any]]] = None,
        height_data: Optional[Dict[str, Any]] = None,
        spacing_data: Optional[Dict[str, Any]] = None,
        arrangement_type: Optional[str] = None,
        disney_style_score: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Add or update annotations for an image.

        Args:
            image_id: Image to annotate
            plant_species: List of plant species in image
            plant_positions: Bounding boxes/positions for plants
            height_data: Height analysis data
            spacing_data: Spacing analysis data
            arrangement_type: Type of arrangement (row, cluster, etc.)
            disney_style_score: How Disney-like the arrangement is (0-1)
            tags: Additional tags

        Returns:
            True if annotation was successful
        """
        if image_id not in self._annotations:
            logger.warning(f"Image {image_id} not found in dataset")
            return False

        ann = self._annotations[image_id]

        if plant_species is not None:
            ann.plant_species = plant_species
        if plant_positions is not None:
            ann.plant_positions = plant_positions
        if height_data is not None:
            ann.height_data = height_data
        if spacing_data is not None:
            ann.spacing_data = spacing_data
        if arrangement_type is not None:
            ann.arrangement_type = arrangement_type
        if disney_style_score is not None:
            ann.disney_style_score = disney_style_score
        if tags is not None:
            ann.tags = tags

        ann.updated_at = datetime.now().isoformat()

        self._index_annotation(ann)
        self._save_annotations()

        return True

    def get_annotation(self, image_id: str) -> Optional[ImageAnnotation]:
        """Get annotation for an image."""
        return self._annotations.get(image_id)

    def get_image_path(self, image_id: str, processed: bool = False) -> Optional[Path]:
        """
        Get the file path for an image.

        Args:
            image_id: Image ID
            processed: If True, return processed image path

        Returns:
            Path to the image file
        """
        ann = self._annotations.get(image_id)
        if ann is None:
            return None

        if processed:
            for ext in [".jpg", ".png", ".webp"]:
                path = self.processed_dir / f"{image_id}{ext}"
                if path.exists():
                    return path
            return None

        return self.base_dir / ann.file_path

    def add_processed_image(
        self,
        image_id: str,
        processed_data: bytes,
        suffix: str = ""
    ) -> Optional[Path]:
        """
        Add a processed version of an image.

        Args:
            image_id: Original image ID
            processed_data: Processed image bytes
            suffix: Optional suffix for the filename

        Returns:
            Path to saved processed image
        """
        if image_id not in self._annotations:
            logger.warning(f"Image {image_id} not found")
            return None

        ext = self._detect_extension(processed_data)
        filename = f"{image_id}{suffix}{ext}"
        path = self.processed_dir / filename

        path.write_bytes(processed_data)
        return path

    def create_splits(
        self,
        split_config: Optional[DatasetSplit] = None,
        filter_annotated: bool = True
    ) -> Dict[str, List[str]]:
        """
        Create train/val/test splits of the dataset.

        Args:
            split_config: Split configuration
            filter_annotated: Only include annotated images

        Returns:
            Dictionary mapping split name to image IDs
        """
        config = split_config or DatasetSplit()

        if filter_annotated:
            image_ids = [
                iid for iid, ann in self._annotations.items()
                if ann.plant_species or ann.arrangement_type
            ]
        else:
            image_ids = list(self._annotations.keys())

        if not image_ids:
            logger.warning("No images to split")
            return {"train": [], "val": [], "test": []}

        random.seed(config.random_seed)

        if config.stratify_by == "arrangement_type":
            splits = self._stratified_split(image_ids, config)
        else:
            splits = self._random_split(image_ids, config)

        for split_name, ids in splits.items():
            split_dir = getattr(self, f"{split_name}_dir")

            for existing in split_dir.glob("*"):
                if existing.is_symlink():
                    existing.unlink()

            for image_id in ids:
                src_path = self.get_image_path(image_id, processed=True)
                if src_path is None:
                    src_path = self.get_image_path(image_id, processed=False)

                if src_path and src_path.exists():
                    dst_path = split_dir / src_path.name
                    if not dst_path.exists():
                        dst_path.symlink_to(src_path.absolute())

        self._save_split_manifest(splits)

        logger.info(
            f"Created splits: train={len(splits['train'])}, "
            f"val={len(splits['val'])}, test={len(splits['test'])}"
        )

        return splits

    def _random_split(
        self,
        image_ids: List[str],
        config: DatasetSplit
    ) -> Dict[str, List[str]]:
        """Perform random split."""
        random.shuffle(image_ids)

        n = len(image_ids)
        train_end = int(n * config.train_ratio)
        val_end = train_end + int(n * config.val_ratio)

        return {
            "train": image_ids[:train_end],
            "val": image_ids[train_end:val_end],
            "test": image_ids[val_end:]
        }

    def _stratified_split(
        self,
        image_ids: List[str],
        config: DatasetSplit
    ) -> Dict[str, List[str]]:
        """Perform stratified split by arrangement type."""
        by_type: Dict[str, List[str]] = {}

        for image_id in image_ids:
            ann = self._annotations[image_id]
            arr_type = ann.arrangement_type or "unknown"
            if arr_type not in by_type:
                by_type[arr_type] = []
            by_type[arr_type].append(image_id)

        splits = {"train": [], "val": [], "test": []}

        for arr_type, ids in by_type.items():
            random.shuffle(ids)
            n = len(ids)
            train_end = int(n * config.train_ratio)
            val_end = train_end + int(n * config.val_ratio)

            splits["train"].extend(ids[:train_end])
            splits["val"].extend(ids[train_end:val_end])
            splits["test"].extend(ids[val_end:])

        for split_ids in splits.values():
            random.shuffle(split_ids)

        return splits

    def _save_split_manifest(self, splits: Dict[str, List[str]]) -> None:
        """Save split manifest to disk."""
        manifest = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "splits": splits,
            "counts": {name: len(ids) for name, ids in splits.items()}
        }

        manifest_path = self.base_dir / "splits" / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

    def get_images_by_species(self, species: str) -> List[str]:
        """Get all image IDs containing a species."""
        return list(self._species_index.get(species, set()))

    def get_images_by_arrangement(self, arrangement_type: str) -> List[str]:
        """Get all image IDs with a specific arrangement type."""
        return list(self._arrangement_index.get(arrangement_type, set()))

    def list_species(self) -> List[Tuple[str, int]]:
        """List all species and their counts."""
        return [
            (species, len(ids))
            for species, ids in sorted(
                self._species_index.items(),
                key=lambda x: -len(x[1])
            )
        ]

    def list_arrangement_types(self) -> List[Tuple[str, int]]:
        """List all arrangement types and their counts."""
        return [
            (arr_type, len(ids))
            for arr_type, ids in sorted(
                self._arrangement_index.items(),
                key=lambda x: -len(x[1])
            )
        ]

    def compute_stats(self) -> DatasetStats:
        """Compute comprehensive dataset statistics."""
        stats = DatasetStats()

        stats.total_images = len(self._annotations)

        stats.annotated_images = sum(
            1 for ann in self._annotations.values()
            if ann.plant_species or ann.arrangement_type
        )

        stats.unique_species = len(self._species_index)

        stats.arrangement_types = {
            arr_type: len(ids)
            for arr_type, ids in self._arrangement_index.items()
        }

        for ann in self._annotations.values():
            source = ann.metadata.get("source", "unknown")
            stats.images_by_source[source] = stats.images_by_source.get(source, 0) + 1

        total_bytes = 0
        for ann in self._annotations.values():
            path = self.base_dir / ann.file_path
            if path.exists():
                total_bytes += path.stat().st_size
        stats.total_size_mb = round(total_bytes / (1024 * 1024), 2)

        splits_manifest = self.base_dir / "splits" / "manifest.json"
        if splits_manifest.exists():
            manifest = json.loads(splits_manifest.read_text())
            counts = manifest.get("counts", {})
            stats.train_count = counts.get("train", 0)
            stats.val_count = counts.get("val", 0)
            stats.test_count = counts.get("test", 0)

        self.stats_file.write_text(json.dumps(asdict(stats), indent=2))

        return stats

    def export_annotations(
        self,
        format: str = "coco",
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Export annotations in a standard format.

        Args:
            format: Export format (coco, yolo, csv)
            output_path: Output file path

        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.exports_dir / f"annotations_{format}.json"

        if format == "coco":
            data = self._export_coco()
        elif format == "yolo":
            data = self._export_yolo()
        elif format == "csv":
            data = self._export_csv()
        else:
            raise ValueError(f"Unknown format: {format}")

        if isinstance(data, dict):
            output_path.write_text(json.dumps(data, indent=2))
        else:
            output_path.write_text(data)

        logger.info(f"Exported annotations to {output_path}")
        return output_path

    def _export_coco(self) -> Dict[str, Any]:
        """Export in COCO format."""
        species_to_id = {
            species: idx + 1
            for idx, species in enumerate(sorted(self._species_index.keys()))
        }

        images = []
        annotations = []
        ann_id = 1

        for img_idx, (image_id, ann) in enumerate(self._annotations.items()):
            path = self.base_dir / ann.file_path

            images.append({
                "id": img_idx + 1,
                "file_name": path.name,
                "width": ann.metadata.get("width", 0),
                "height": ann.metadata.get("height", 0)
            })

            for pos in ann.plant_positions:
                if "bbox" in pos:
                    bbox = pos["bbox"]
                    species = pos.get("species", "unknown")

                    annotations.append({
                        "id": ann_id,
                        "image_id": img_idx + 1,
                        "category_id": species_to_id.get(species, 0),
                        "bbox": bbox,
                        "area": bbox[2] * bbox[3] if len(bbox) >= 4 else 0,
                        "iscrowd": 0
                    })
                    ann_id += 1

        categories = [
            {"id": cat_id, "name": species, "supercategory": "plant"}
            for species, cat_id in species_to_id.items()
        ]

        return {
            "info": {
                "description": "Disney Plant Training Dataset",
                "version": "1.0",
                "year": datetime.now().year
            },
            "images": images,
            "annotations": annotations,
            "categories": categories
        }

    def _export_yolo(self) -> str:
        """Export in YOLO format (returns class list)."""
        species_list = sorted(self._species_index.keys())

        for image_id, ann in self._annotations.items():
            path = self.base_dir / ann.file_path
            label_path = self.exports_dir / "labels" / f"{path.stem}.txt"
            label_path.parent.mkdir(exist_ok=True)

            lines = []
            for pos in ann.plant_positions:
                if "bbox" in pos:
                    species = pos.get("species", "unknown")
                    class_id = species_list.index(species) if species in species_list else 0
                    bbox = pos["bbox"]

                    img_w = ann.metadata.get("width", 1)
                    img_h = ann.metadata.get("height", 1)
                    x_center = (bbox[0] + bbox[2] / 2) / img_w
                    y_center = (bbox[1] + bbox[3] / 2) / img_h
                    width = bbox[2] / img_w
                    height = bbox[3] / img_h

                    lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

            label_path.write_text("\n".join(lines))

        return "\n".join(species_list)

    def _export_csv(self) -> str:
        """Export as CSV."""
        lines = ["image_id,file_path,species,arrangement_type,disney_score,source_url"]

        for image_id, ann in self._annotations.items():
            species = ";".join(ann.plant_species) if ann.plant_species else ""
            lines.append(
                f"{image_id},{ann.file_path},{species},{ann.arrangement_type or ''},"
                f"{ann.disney_style_score or ''},{ann.source_url or ''}"
            )

        return "\n".join(lines)

    def cleanup(self, remove_unannotated: bool = False) -> int:
        """
        Clean up the dataset.

        Args:
            remove_unannotated: Remove images without annotations

        Returns:
            Number of items cleaned
        """
        cleaned = 0

        for image_id, ann in list(self._annotations.items()):
            path = self.base_dir / ann.file_path
            if not path.exists():
                del self._annotations[image_id]
                cleaned += 1
                continue

            if remove_unannotated:
                if not ann.plant_species and not ann.arrangement_type:
                    path.unlink()
                    del self._annotations[image_id]
                    cleaned += 1

        if cleaned > 0:
            self._save_annotations()
            logger.info(f"Cleaned {cleaned} items from dataset")

        return cleaned
