"""
Disney Plant Trainer - Main Orchestrator

Unified interface for:
- Scraping plant images from royalty-free sources
- Downloading and validating images
- Processing and augmenting for training
- Analyzing spatial arrangements
- Training ML models for Disney-style patterns
"""

import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .core.scraper import PlantImageScraper, ScrapedImage, ScrapingConfig
from .core.image_downloader import ImageDownloader, DownloadConfig, DownloadProgress
from .core.image_processor import ImageProcessor, ProcessingConfig, AugmentationConfig
from .core.spatial_analyzer import SpatialAnalyzer, ArrangementAnalysis, PlantPosition
from .core.trainer import PlantTrainer, TrainingConfig, TrainingHistory, ModelType
from .utils.cache_manager import CacheManager
from .utils.rate_limiter import RateLimiter, RateLimitConfig
from .utils.image_validator import ImageValidator, ValidationConfig
from .utils.dataset_organizer import DatasetOrganizer, DatasetSplit

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DisneyPlantTrainerConfig:
    """Master configuration for Disney Plant Trainer."""
    base_dir: str = "./disney_plant_data"
    api_keys: Dict[str, str] = None
    scraping: ScrapingConfig = None
    download: DownloadConfig = None
    processing: ProcessingConfig = None
    augmentation: AugmentationConfig = None
    validation: ValidationConfig = None
    training: TrainingConfig = None
    cache_enabled: bool = True
    cache_max_gb: float = 10.0

    def __post_init__(self):
        if self.api_keys is None:
            self.api_keys = {}
        if self.scraping is None:
            self.scraping = ScrapingConfig()
        if self.download is None:
            self.download = DownloadConfig()
        if self.processing is None:
            self.processing = ProcessingConfig()
        if self.augmentation is None:
            self.augmentation = AugmentationConfig()
        if self.validation is None:
            self.validation = ValidationConfig()
        if self.training is None:
            self.training = TrainingConfig()


class DisneyPlantTrainer:
    """
    Main orchestrator for Disney-style plant training.

    This class provides a unified interface to:
    1. Scrape plant images from royalty-free sources (Unsplash, Pexels, Pixabay)
    2. Download and validate images
    3. Process images for ML training
    4. Analyze plant spatial relationships
    5. Train models to recognize Disney-style patterns

    Usage:
        trainer = DisneyPlantTrainer(config)

        # Scrape and download images
        trainer.collect_dataset(
            species=["rose", "tulip", "palm"],
            images_per_species=100
        )

        # Analyze arrangements
        analysis = trainer.analyze_image("path/to/garden.jpg")

        # Train a model
        trainer.train_classifier(backbone="resnet18", epochs=50)
    """

    def __init__(self, config: Optional[DisneyPlantTrainerConfig] = None):
        """
        Initialize the Disney Plant Trainer.

        Args:
            config: Master configuration object
        """
        self.config = config or DisneyPlantTrainerConfig()

        self.base_dir = Path(self.config.base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self._setup_directories()
        self._initialize_components()

        logger.info(f"Disney Plant Trainer initialized at {self.base_dir}")

    def _setup_directories(self) -> None:
        """Create directory structure."""
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.models_dir = self.base_dir / "models"
        self.cache_dir = self.base_dir / "cache"
        self.exports_dir = self.base_dir / "exports"
        self.annotations_dir = self.base_dir / "annotations"

        for directory in [
            self.raw_dir, self.processed_dir, self.models_dir,
            self.cache_dir, self.exports_dir, self.annotations_dir
        ]:
            directory.mkdir(exist_ok=True)

    def _initialize_components(self) -> None:
        """Initialize all component modules."""
        if self.config.cache_enabled:
            self.cache = CacheManager(
                self.cache_dir,
                max_size_gb=self.config.cache_max_gb
            )
        else:
            self.cache = None

        self.rate_limiter = RateLimiter(RateLimitConfig(
            requests_per_second=1.0,
            respect_robots_txt=True
        ))

        self.scraper = PlantImageScraper(
            api_keys=self.config.api_keys,
            cache=self.cache,
            config=self.config.scraping
        )

        self.validator = ImageValidator(self.config.validation)

        self.downloader = ImageDownloader(
            self.raw_dir,
            config=self.config.download,
            cache=self.cache,
            rate_limiter=self.rate_limiter,
            validator=self.validator
        )

        self.processor = ImageProcessor(
            self.config.processing,
            self.config.augmentation
        )

        self.analyzer = SpatialAnalyzer()

        self.dataset = DatasetOrganizer(self.base_dir)

        self.trainer = None

    def collect_dataset(
        self,
        species: List[str],
        images_per_species: int = 50,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Collect a dataset of plant images.

        Args:
            species: List of plant species to collect
            images_per_species: Target images per species
            progress_callback: Callback(species, current, total)

        Returns:
            Summary of collected images
        """
        logger.info(f"Collecting dataset for {len(species)} species")

        summary = {
            "species": {},
            "total_scraped": 0,
            "total_downloaded": 0,
            "total_validated": 0,
            "started_at": datetime.now().isoformat()
        }

        for idx, plant_species in enumerate(species):
            logger.info(f"Processing species {idx + 1}/{len(species)}: {plant_species}")

            if progress_callback:
                progress_callback(plant_species, idx, len(species))

            scraped_images = list(self.scraper.scrape(
                queries=[plant_species],
                expand_queries=True,
                max_total=images_per_species * 2
            ))

            summary["total_scraped"] += len(scraped_images)

            species_dir = self.raw_dir / plant_species.replace(" ", "_")
            species_dir.mkdir(exist_ok=True)

            species_downloader = ImageDownloader(
                species_dir,
                config=self.config.download,
                cache=self.cache,
                validator=self.validator
            )

            download_results, download_summary = species_downloader.download_from_scraper(
                scraped_images[:images_per_species]
            )

            successful = [r for r in download_results if r.success]
            summary["total_downloaded"] += len(successful)

            for result in successful:
                if result.file_path and result.file_path != "(cached)":
                    for img in scraped_images:
                        if img.url == result.url:
                            image_id = self.dataset.add_image(
                                Path(result.file_path).read_bytes(),
                                source_url=img.url,
                                metadata={
                                    "source": img.source,
                                    "title": img.title,
                                    "tags": img.tags,
                                    "species_query": plant_species
                                }
                            )

                            self.dataset.annotate_image(
                                image_id,
                                plant_species=[plant_species],
                                tags=img.tags
                            )
                            summary["total_validated"] += 1
                            break

            summary["species"][plant_species] = {
                "scraped": len(scraped_images),
                "downloaded": download_summary["successful"],
                "failed": download_summary["failed"]
            }

            species_downloader.close()

        summary["completed_at"] = datetime.now().isoformat()

        summary_path = self.base_dir / "collection_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Dataset collection complete: {summary['total_validated']} images")

        return summary

    def collect_arrangements(
        self,
        arrangement_types: List[str],
        images_per_type: int = 100,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Collect images organized by arrangement type.

        Args:
            arrangement_types: Types like "flower_bed", "hedge_row", "disney_style"
            images_per_type: Target images per type
            progress_callback: Progress callback

        Returns:
            Collection summary
        """
        logger.info(f"Collecting arrangement dataset for {len(arrangement_types)} types")

        arrangement_dataset = self.scraper.scrape_arrangement_dataset(
            arrangement_types,
            images_per_type
        )

        summary = {
            "arrangement_types": {},
            "total": 0
        }

        for arr_type, images in arrangement_dataset.items():
            type_dir = self.raw_dir / "arrangements" / arr_type
            type_dir.mkdir(parents=True, exist_ok=True)

            type_downloader = ImageDownloader(
                type_dir,
                config=self.config.download,
                validator=self.validator
            )

            results, _ = type_downloader.download_from_scraper(images)
            successful = sum(1 for r in results if r.success)

            summary["arrangement_types"][arr_type] = successful
            summary["total"] += successful

            for result in results:
                if result.success and result.file_path:
                    for img in images:
                        if img.url == result.url:
                            image_id = self.dataset.add_image(
                                Path(result.file_path).read_bytes(),
                                source_url=img.url,
                                metadata={"arrangement_query": arr_type}
                            )
                            self.dataset.annotate_image(
                                image_id,
                                arrangement_type=arr_type,
                                tags=img.tags
                            )
                            break

            type_downloader.close()

        return summary

    def process_dataset(
        self,
        augment: bool = True,
        variants_per_image: int = 3,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Process all raw images for training.

        Args:
            augment: Whether to create augmented variants
            variants_per_image: Number of variants per image
            progress_callback: Progress callback

        Returns:
            Processing summary
        """
        logger.info("Processing dataset for training")

        raw_images = list(self.raw_dir.rglob("*.jpg")) + \
                    list(self.raw_dir.rglob("*.jpeg")) + \
                    list(self.raw_dir.rglob("*.png"))

        summary = {
            "raw_images": len(raw_images),
            "processed": 0,
            "augmented_variants": 0
        }

        for idx, image_path in enumerate(raw_images):
            try:
                rel_path = image_path.relative_to(self.raw_dir)
                output_dir = self.processed_dir / rel_path.parent
                output_dir.mkdir(parents=True, exist_ok=True)

                processed = self.processor.process(image_path, augment=False)
                output_path = output_dir / f"{image_path.stem}_processed.jpg"
                self.processor.save(processed, output_path)
                summary["processed"] += 1

                if augment:
                    variants = self.processor.create_augmented_variants(
                        image_path,
                        num_variants=variants_per_image
                    )

                    for var_idx, variant in enumerate(variants[1:], 1):
                        var_path = output_dir / f"{image_path.stem}_aug{var_idx}.jpg"
                        self.processor.save(variant, var_path)
                        summary["augmented_variants"] += 1

                if progress_callback:
                    progress_callback(idx + 1, len(raw_images))

            except Exception as e:
                logger.error(f"Failed to process {image_path}: {e}")

        logger.info(f"Processing complete: {summary['processed']} images")

        return summary

    def analyze_image(
        self,
        image_path: Union[str, Path]
    ) -> ArrangementAnalysis:
        """
        Analyze plant arrangement in an image.

        Args:
            image_path: Path to image file

        Returns:
            ArrangementAnalysis with spatial relationships
        """
        return self.analyzer.analyze_image(image_path)

    def analyze_dataset(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Analyze all images in dataset and annotate with spatial data.

        Args:
            progress_callback: Progress callback

        Returns:
            Analysis summary
        """
        logger.info("Analyzing dataset spatial relationships")

        annotations = self.dataset.list_entries(limit=10000)

        summary = {
            "analyzed": 0,
            "arrangement_distribution": {},
            "avg_disney_score": 0.0,
            "forced_perspective_count": 0
        }

        disney_scores = []

        for idx, ann in enumerate(annotations):
            try:
                image_path = self.dataset.get_image_path(ann.image_id)
                if image_path is None:
                    continue

                analysis = self.analyzer.analyze_image(image_path)

                self.dataset.annotate_image(
                    ann.image_id,
                    arrangement_type=analysis.arrangement_type.value,
                    disney_style_score=analysis.disney_style_score,
                    spacing_data=analysis.spacing_stats,
                    height_data={
                        zone.value: count
                        for zone, count in analysis.height_distribution.items()
                    }
                )

                arr_type = analysis.arrangement_type.value
                summary["arrangement_distribution"][arr_type] = \
                    summary["arrangement_distribution"].get(arr_type, 0) + 1

                disney_scores.append(analysis.disney_style_score)

                if analysis.forced_perspective:
                    summary["forced_perspective_count"] += 1

                summary["analyzed"] += 1

                if progress_callback:
                    progress_callback(idx + 1, len(annotations))

            except Exception as e:
                logger.error(f"Failed to analyze {ann.image_id}: {e}")

        if disney_scores:
            summary["avg_disney_score"] = sum(disney_scores) / len(disney_scores)

        return summary

    def prepare_training_data(
        self,
        split_config: Optional[DatasetSplit] = None
    ) -> Tuple[Any, Any, Dict[str, int]]:
        """
        Prepare dataset for training with splits.

        Args:
            split_config: Train/val/test split configuration

        Returns:
            Tuple of (train_loader, val_loader, class_mapping)
        """
        self.dataset.create_splits(split_config)

        train_dir = self.base_dir / "splits" / "train"

        if self.trainer is None:
            self.trainer = PlantTrainer(self.models_dir, self.config.training)

        return self.trainer.prepare_dataset(train_dir)

    def train_classifier(
        self,
        backbone: str = "resnet18",
        epochs: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> TrainingHistory:
        """
        Train a plant species classifier.

        Args:
            backbone: Model backbone architecture
            epochs: Number of training epochs
            progress_callback: Training progress callback

        Returns:
            TrainingHistory with results
        """
        logger.info(f"Training classifier with {backbone} backbone")

        if epochs:
            self.config.training.epochs = epochs

        self.config.training.model_type = ModelType.SPECIES_CLASSIFIER

        if self.trainer is None:
            self.trainer = PlantTrainer(self.models_dir, self.config.training)

        train_loader, val_loader, class_mapping = self.prepare_training_data()

        self.trainer.build_model(backbone=backbone, pretrained=True)

        history = self.trainer.train(
            train_loader,
            val_loader,
            progress_callback=progress_callback
        )

        class_mapping_path = self.models_dir / "class_mapping.json"
        with open(class_mapping_path, 'w') as f:
            json.dump(class_mapping, f, indent=2)

        return history

    def train_arrangement_classifier(
        self,
        backbone: str = "resnet18",
        epochs: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> TrainingHistory:
        """
        Train an arrangement type classifier.

        Args:
            backbone: Model backbone
            epochs: Training epochs
            progress_callback: Progress callback

        Returns:
            TrainingHistory
        """
        logger.info("Training arrangement classifier")

        self.config.training.model_type = ModelType.ARRANGEMENT_CLASSIFIER

        if self.trainer is None:
            self.trainer = PlantTrainer(self.models_dir, self.config.training)

        self._reorganize_by_arrangement()

        return self.train_classifier(backbone, epochs, progress_callback)

    def _reorganize_by_arrangement(self) -> None:
        """Reorganize dataset by arrangement type for training."""
        arrangement_dir = self.processed_dir / "by_arrangement"
        arrangement_dir.mkdir(exist_ok=True)

        annotations = self.dataset.list_entries(limit=10000)

        for ann in annotations:
            if ann.arrangement_type:
                image_path = self.dataset.get_image_path(ann.image_id, processed=True)
                if image_path is None:
                    image_path = self.dataset.get_image_path(ann.image_id)

                if image_path and image_path.exists():
                    type_dir = arrangement_dir / ann.arrangement_type
                    type_dir.mkdir(exist_ok=True)

                    dest_path = type_dir / image_path.name
                    if not dest_path.exists():
                        import shutil
                        shutil.copy2(image_path, dest_path)

    def train_disney_scorer(
        self,
        backbone: str = "resnet18",
        epochs: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> TrainingHistory:
        """
        Train a Disney-style scoring model (regression).

        Args:
            backbone: Model backbone
            epochs: Training epochs
            progress_callback: Progress callback

        Returns:
            TrainingHistory
        """
        logger.info("Training Disney style scorer")

        self.config.training.model_type = ModelType.DISNEY_SCORER
        self.config.training.num_classes = 1

        if self.trainer is None:
            self.trainer = PlantTrainer(self.models_dir, self.config.training)

        return self.trainer.train(None, None, progress_callback)

    def predict_species(
        self,
        image_path: Union[str, Path],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Predict plant species in an image.

        Args:
            image_path: Path to image
            top_k: Number of top predictions to return

        Returns:
            List of (species_name, confidence) tuples
        """
        if self.trainer is None or self.trainer._model is None:
            best_model = self.models_dir / "best_model.pt"
            if not best_model.exists():
                raise ValueError("No trained model found")

            self.trainer = PlantTrainer(self.models_dir)
            self.trainer.load_checkpoint(best_model)

        class_mapping_path = self.models_dir / "class_mapping.json"
        if class_mapping_path.exists():
            with open(class_mapping_path) as f:
                class_mapping = json.load(f)
            idx_to_class = {v: k for k, v in class_mapping.items()}
        else:
            idx_to_class = {}

        processed = self.processor.process(image_path, augment=False)
        tensor = self.processor.to_tensor_format(processed)

        import torch
        input_tensor = torch.tensor(tensor).unsqueeze(0)

        probs = self.trainer.predict(input_tensor, return_probabilities=True)[0]

        indexed_probs = list(enumerate(probs))
        indexed_probs.sort(key=lambda x: -x[1])

        results = []
        for idx, prob in indexed_probs[:top_k]:
            species_name = idx_to_class.get(idx, f"class_{idx}")
            results.append((species_name, prob))

        return results

    def score_arrangement(
        self,
        image_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Score an arrangement for Disney-style quality.

        Args:
            image_path: Path to image

        Returns:
            Score and detailed metrics
        """
        analysis = self.analyze_image(image_path)
        disney_metrics = self.analyzer.compute_disney_metrics(analysis)

        return {
            "disney_score": analysis.disney_style_score,
            "arrangement_type": analysis.arrangement_type.value,
            "forced_perspective": analysis.forced_perspective,
            "layering_score": analysis.layering_score,
            "color_harmony": analysis.color_harmony_score,
            "symmetry_score": analysis.symmetry_score,
            "recommendations": analysis.recommendations,
            "detailed_metrics": {
                "forced_perspective_score": disney_metrics.forced_perspective_score,
                "color_story_score": disney_metrics.color_story_score,
                "seasonal_interest": disney_metrics.seasonal_interest_score,
                "hidden_mickey_potential": disney_metrics.hidden_mickey_potential,
                "immersion_score": disney_metrics.immersion_score,
                "maintenance_friendliness": disney_metrics.maintenance_friendliness,
                "guest_flow_optimization": disney_metrics.guest_flow_optimization,
                "photo_spot_quality": disney_metrics.photo_spot_quality
            }
        }

    def export_dataset(
        self,
        format: str = "coco",
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Export dataset in standard format.

        Args:
            format: Export format (coco, yolo, csv)
            output_path: Output path

        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.exports_dir / f"dataset_{format}"

        return self.dataset.export_annotations(format, output_path)

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        dataset_stats = self.dataset.compute_stats()

        return {
            "dataset": asdict(dataset_stats),
            "scraper": self.scraper.get_stats(),
            "cache": self.cache.get_stats() if self.cache else None,
            "trainer": self.trainer.get_status() if self.trainer else None,
            "directories": {
                "base": str(self.base_dir),
                "raw_images": len(list(self.raw_dir.rglob("*.jpg"))),
                "processed_images": len(list(self.processed_dir.rglob("*.jpg")))
            }
        }

    def cleanup(
        self,
        remove_cache: bool = False,
        remove_raw: bool = False
    ) -> None:
        """
        Clean up temporary files.

        Args:
            remove_cache: Remove cached data
            remove_raw: Remove raw (unprocessed) images
        """
        if remove_cache and self.cache:
            self.cache.clear()
            logger.info("Cache cleared")

        if remove_raw:
            import shutil
            shutil.rmtree(self.raw_dir)
            self.raw_dir.mkdir()
            logger.info("Raw images removed")

        self.dataset.cleanup()


def create_trainer(
    base_dir: str = "./disney_plant_data",
    unsplash_key: Optional[str] = None,
    pexels_key: Optional[str] = None,
    pixabay_key: Optional[str] = None
) -> DisneyPlantTrainer:
    """
    Convenience function to create a configured trainer.

    Args:
        base_dir: Base directory for data
        unsplash_key: Unsplash API key
        pexels_key: Pexels API key
        pixabay_key: Pixabay API key

    Returns:
        Configured DisneyPlantTrainer instance
    """
    api_keys = {}
    if unsplash_key:
        api_keys["unsplash"] = unsplash_key
    if pexels_key:
        api_keys["pexels"] = pexels_key
    if pixabay_key:
        api_keys["pixabay"] = pixabay_key

    config = DisneyPlantTrainerConfig(
        base_dir=base_dir,
        api_keys=api_keys
    )

    return DisneyPlantTrainer(config)


if __name__ == "__main__":
    trainer = create_trainer()

    print("Disney Plant Trainer initialized")
    print(f"Stats: {trainer.get_stats()}")
