"""
Disney Plant Trainer - Core Modules

This package provides the main functionality:
- PlantImageScraper: Web scraping for royalty-free plant images
- ImageDownloader: Robust image downloading with retry logic
- ImageProcessor: Preprocessing and augmentation for training
- SpatialAnalyzer: Plant arrangement and relationship analysis
- PlantTrainer: ML model training for Disney-style patterns
"""

from .scraper import PlantImageScraper
from .image_downloader import ImageDownloader
from .image_processor import ImageProcessor
from .spatial_analyzer import SpatialAnalyzer
from .trainer import PlantTrainer

__all__ = [
    'PlantImageScraper',
    'ImageDownloader',
    'ImageProcessor',
    'SpatialAnalyzer',
    'PlantTrainer'
]
