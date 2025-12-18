# Disney Plant Trainer Skill

## Table of Contents

1. [Overview](#overview)
2. [Core Capabilities](#core-capabilities)
3. [Technical Architecture](#technical-architecture)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage Guide](#usage-guide)
7. [API Reference](#api-reference)
8. [Training Pipeline](#training-pipeline)
9. [Disney Design Principles](#disney-design-principles)
10. [Error Handling](#error-handling)
11. [Performance Optimization](#performance-optimization)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The Disney Plant Trainer is a comprehensive Claude Skill for creating and training machine learning models that understand Disney-style landscape design patterns. It scrapes royalty-free plant images from multiple sources, processes them for ML training, analyzes spatial relationships between plants, and trains models to recognize and score arrangements based on Disney's legendary landscape design principles.

### Key Features

- **Multi-Source Image Scraping**: Collects plant images from Unsplash, Pexels, Pixabay, and custom botanical websites
- **Intelligent Rate Limiting**: Respects robots.txt and implements polite scraping with exponential backoff
- **Image Validation**: Validates image quality, format, and detects duplicates using perceptual hashing
- **Spatial Analysis**: Analyzes plant arrangements for height relationships, spacing patterns, and layering
- **Disney-Style Scoring**: Evaluates arrangements against Disney's landscape design principles
- **ML Training Pipeline**: Trains classifiers for species identification and arrangement classification
- **Data Augmentation**: Creates training variants with rotation, color adjustment, and geometric transforms

### Target Users

- Landscape architects studying professional design patterns
- Theme park designers learning Disney-style landscaping
- Horticulturists training plant identification systems
- ML engineers building botanical image classifiers
- Garden designers seeking inspiration and validation

---

## Core Capabilities

### 1. Web Scraping for Plant Images

The skill scrapes royalty-free images from multiple sources:

```python
from scripts.main import DisneyPlantTrainer, DisneyPlantTrainerConfig

config = DisneyPlantTrainerConfig(
    api_keys={
        "unsplash": "your_unsplash_key",
        "pexels": "your_pexels_key",
        "pixabay": "your_pixabay_key"
    }
)

trainer = DisneyPlantTrainer(config)

# Collect images by species
summary = trainer.collect_dataset(
    species=["rose", "tulip", "palm", "boxwood", "petunia"],
    images_per_species=100
)

# Collect images by arrangement type
arrangements = trainer.collect_arrangements(
    arrangement_types=["flower_bed", "hedge_row", "disney_style"],
    images_per_type=150
)
```

**Supported Sources:**
- **Unsplash**: High-quality photography with good botanical coverage
- **Pexels**: Large collection of landscape and garden images
- **Pixabay**: Extensive royalty-free botanical images
- **Custom Websites**: Configurable scraping for botanical databases

### 2. Image Processing and Augmentation

Prepares images for ML training with extensive augmentation options:

```python
from scripts.core.image_processor import ImageProcessor, ProcessingConfig, AugmentationConfig

processor = ImageProcessor(
    config=ProcessingConfig(
        target_size=(512, 512),
        resize_mode="contain",
        normalize=True
    ),
    augmentation=AugmentationConfig(
        horizontal_flip=0.5,
        rotation_range=(-15, 15),
        brightness_range=(0.8, 1.2),
        contrast_range=(0.8, 1.2)
    )
)

# Process single image
processed = processor.process("garden.jpg", augment=True)

# Create multiple variants for training
variants = processor.create_augmented_variants("rose.jpg", num_variants=5)
```

**Processing Features:**
- Resize with multiple modes (contain, cover, stretch, pad)
- ImageNet normalization for transfer learning
- Geometric transforms (rotation, flip, crop)
- Color adjustments (brightness, contrast, saturation)
- Gaussian blur and noise injection
- Perceptual hashing for deduplication

### 3. Spatial Relationship Analysis

Analyzes plant arrangements to understand Disney-style design patterns:

```python
from scripts.core.spatial_analyzer import SpatialAnalyzer

analyzer = SpatialAnalyzer()

# Analyze arrangement in image
analysis = analyzer.analyze_image("disney_garden.jpg")

print(f"Arrangement Type: {analysis.arrangement_type.value}")
print(f"Disney Score: {analysis.disney_style_score}")
print(f"Forced Perspective: {analysis.forced_perspective}")
print(f"Layering Score: {analysis.layering_score}")
print(f"Recommendations: {analysis.recommendations}")
```

**Analysis Metrics:**
- **Arrangement Type**: Linear, cluster, radial, grid, organic, layered, border, focal_point
- **Height Distribution**: Ground cover, low, medium, tall, canopy zones
- **Spacing Statistics**: Mean, standard deviation, min/max distances
- **Symmetry Score**: Bilateral balance assessment
- **Layering Score**: Depth and height variety evaluation
- **Color Harmony**: Green ratio and color diversity
- **Forced Perspective**: Detection of Disney's signature depth technique

### 4. Disney-Style Design Scoring

Evaluates arrangements against professional Disney landscape principles:

```python
# Get detailed Disney metrics
disney_metrics = analyzer.compute_disney_metrics(analysis)

print(f"Forced Perspective: {disney_metrics.forced_perspective_score}")
print(f"Color Story: {disney_metrics.color_story_score}")
print(f"Immersion Score: {disney_metrics.immersion_score}")
print(f"Photo Spot Quality: {disney_metrics.photo_spot_quality}")
print(f"Hidden Mickey Potential: {disney_metrics.hidden_mickey_potential}")
```

**Disney Principles Evaluated:**
- **Forced Perspective**: Taller plants in back, shorter in front
- **Color Harmony**: Complementary colors creating visual flow
- **Layering**: Multiple height zones for depth
- **Focal Points**: Clear visual anchors
- **Symmetry Balance**: Balanced but natural appearance
- **Seasonal Interest**: Year-round visual appeal
- **Maintenance Access**: Practical spacing for care

### 5. ML Model Training

Train classifiers for species identification and arrangement scoring:

```python
from scripts.core.trainer import PlantTrainer, TrainingConfig, ModelType

trainer = PlantTrainer(
    output_dir="./models",
    config=TrainingConfig(
        model_type=ModelType.SPECIES_CLASSIFIER,
        epochs=50,
        batch_size=32,
        learning_rate=0.001,
        backbone="resnet18",
        pretrained=True
    )
)

# Prepare dataset
train_loader, val_loader, class_mapping = trainer.prepare_dataset("./processed_data")

# Build and train model
trainer.build_model(backbone="resnet18")
history = trainer.train(train_loader, val_loader)

# Export for deployment
trainer.export_model("plant_classifier.onnx", format="onnx")
```

**Supported Architectures:**
- ResNet (18, 34, 50)
- EfficientNet (B0, B1, B2)
- MobileNet (V2, V3)

**Training Features:**
- Transfer learning from ImageNet
- Early stopping with patience
- Learning rate scheduling (cosine, step)
- Model checkpointing
- ONNX and TorchScript export

---

## Technical Architecture

### Module Structure

```
disney-plant-trainer-cskill/
├── .claude-plugin/
│   └── marketplace.json          # Skill manifest with 3-layer activation
├── SKILL.md                      # This specification document
├── README.md                     # Quick start guide
├── requirements.txt              # Python dependencies
├── scripts/
│   ├── main.py                  # Main orchestrator (DisneyPlantTrainer)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scraper.py           # Multi-source web scraping
│   │   ├── image_downloader.py  # Robust image downloading
│   │   ├── image_processor.py   # Preprocessing and augmentation
│   │   ├── spatial_analyzer.py  # Arrangement analysis
│   │   └── trainer.py           # ML model training
│   └── utils/
│       ├── __init__.py
│       ├── cache_manager.py     # Multi-tier caching
│       ├── rate_limiter.py      # Polite scraping
│       ├── image_validator.py   # Quality validation
│       └── dataset_organizer.py # Dataset management
├── references/
│   ├── disney-design-principles.md
│   ├── scraping-best-practices.md
│   └── training-guide.md
├── assets/
│   └── config.json              # Default configuration
└── data/                        # Dataset storage
    ├── raw/
    ├── processed/
    ├── models/
    └── annotations/
```

### Data Flow

```
┌─────────────────┐
│   API Sources   │
│ (Unsplash, etc) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PlantScraper   │──▶ ScrapedImage metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ImageDownloader │──▶ Raw images with validation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ImageProcessor  │──▶ Processed + augmented images
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SpatialAnalyzer │──▶ Arrangement analysis + annotations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PlantTrainer   │──▶ Trained ML models
└─────────────────┘
```

### Activation System (3-Layer)

**Layer 1: Keywords (54 exact phrases)**
```
scrape plant images, download plant photos, train plant classifier,
disney landscape training, plant spatial relationships, garden arrangement patterns,
forced perspective plants, analyze plant heights, theme park landscaping...
```

**Layer 2: Patterns (12 regex patterns)**
```regex
(?i)(scrape|harvest|download)\\s+(plant|flower|botanical)\\s+(image|photo)
(?i)(train|build|create)\\s+(plant|landscape)\\s+(model|classifier)
(?i)(disney|theme\\s*park)\\s+(style|landscape)\\s+(training|pattern)
(?i)(analyze|learn|detect)\\s+(plant|garden)\\s+(spacing|height|arrangement)
```

**Layer 3: Natural Language Description**
```
Comprehensive Disney-style landscape plant training system. Scrapes royalty-free
plant images from botanical websites, Unsplash, Pexels, and Pixabay. Downloads
high-resolution photos of flowers, shrubs, trees, hedges, and ground cover.
Analyzes spatial relationships between plants including spacing, height ratios,
layering depth, color transitions, and focal point placement...
```

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Internet connection for API access

### Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

**requirements.txt:**
```
requests>=2.31.0
beautifulsoup4>=4.12.0
pillow>=10.0.0
numpy>=1.24.0
imagehash>=4.3.0

# Optional: ML training
torch>=2.0.0
torchvision>=0.15.0
# OR
tensorflow>=2.13.0

# Optional: Async downloads
aiohttp>=3.8.0
```

### API Keys Setup

1. **Unsplash**: Register at https://unsplash.com/developers
2. **Pexels**: Get key at https://www.pexels.com/api/
3. **Pixabay**: Register at https://pixabay.com/api/docs/

---

## Configuration

### Master Configuration

```python
from scripts.main import DisneyPlantTrainerConfig

config = DisneyPlantTrainerConfig(
    base_dir="./disney_plant_data",

    api_keys={
        "unsplash": "your_key",
        "pexels": "your_key",
        "pixabay": "your_key"
    },

    scraping=ScrapingConfig(
        max_images_per_query=100,
        min_width=800,
        min_height=600,
        safe_search=True
    ),

    download=DownloadConfig(
        max_concurrent=5,
        timeout_seconds=30,
        max_retries=3
    ),

    processing=ProcessingConfig(
        target_size=(512, 512),
        normalize=True
    ),

    training=TrainingConfig(
        epochs=50,
        batch_size=32,
        learning_rate=0.001
    ),

    cache_enabled=True,
    cache_max_gb=10.0
)
```

### Configuration File (assets/config.json)

```json
{
  "scraping": {
    "max_images_per_query": 100,
    "max_pages": 10,
    "min_width": 800,
    "min_height": 600,
    "safe_search": true
  },
  "download": {
    "max_concurrent": 5,
    "timeout_seconds": 30,
    "max_retries": 3,
    "max_file_size_mb": 50
  },
  "processing": {
    "target_size": [512, 512],
    "resize_mode": "contain",
    "normalize": true
  },
  "training": {
    "epochs": 50,
    "batch_size": 32,
    "learning_rate": 0.001,
    "early_stopping_patience": 10
  },
  "rate_limiting": {
    "requests_per_second": 1.0,
    "respect_robots_txt": true
  }
}
```

---

## Usage Guide

### Quick Start

```python
from scripts.main import create_trainer

# Create trainer with API keys
trainer = create_trainer(
    base_dir="./my_plant_dataset",
    unsplash_key="your_key",
    pexels_key="your_key",
    pixabay_key="your_key"
)

# 1. Collect dataset
trainer.collect_dataset(
    species=["rose", "tulip", "lavender", "boxwood"],
    images_per_species=100
)

# 2. Process images
trainer.process_dataset(augment=True, variants_per_image=3)

# 3. Analyze arrangements
trainer.analyze_dataset()

# 4. Train classifier
history = trainer.train_classifier(
    backbone="resnet18",
    epochs=50
)

# 5. Make predictions
predictions = trainer.predict_species("test_image.jpg", top_k=3)
for species, confidence in predictions:
    print(f"{species}: {confidence:.2%}")
```

### Analyzing a Garden Image

```python
# Score any garden image for Disney-style quality
score_data = trainer.score_arrangement("garden_photo.jpg")

print(f"Overall Disney Score: {score_data['disney_score']:.2f}")
print(f"Arrangement Type: {score_data['arrangement_type']}")
print(f"Uses Forced Perspective: {score_data['forced_perspective']}")
print("\nDetailed Metrics:")
for metric, value in score_data['detailed_metrics'].items():
    print(f"  {metric}: {value:.2f}")
print("\nRecommendations:")
for rec in score_data['recommendations']:
    print(f"  - {rec}")
```

### Training Custom Models

```python
from scripts.core.trainer import PlantTrainer, TrainingConfig, ModelType

# Train arrangement classifier
trainer = PlantTrainer(
    output_dir="./models/arrangement",
    config=TrainingConfig(
        model_type=ModelType.ARRANGEMENT_CLASSIFIER,
        epochs=100,
        batch_size=16,
        learning_rate=0.0005,
        freeze_backbone=True  # Transfer learning
    )
)

train_loader, val_loader, classes = trainer.prepare_dataset("./by_arrangement")
trainer.build_model(backbone="efficientnet_b0", pretrained=True)
history = trainer.train(train_loader, val_loader)

print(f"Best validation accuracy: {history.best_val_accuracy:.2%}")
```

---

## API Reference

### DisneyPlantTrainer

Main orchestrator class.

**Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `collect_dataset(species, images_per_species)` | Scrape and download images by species | Dict summary |
| `collect_arrangements(types, images_per_type)` | Collect images by arrangement type | Dict summary |
| `process_dataset(augment, variants)` | Process images for training | Dict summary |
| `analyze_image(path)` | Analyze single image arrangement | ArrangementAnalysis |
| `analyze_dataset()` | Analyze all images in dataset | Dict summary |
| `train_classifier(backbone, epochs)` | Train species classifier | TrainingHistory |
| `train_arrangement_classifier(...)` | Train arrangement classifier | TrainingHistory |
| `predict_species(path, top_k)` | Predict plant species | List[Tuple] |
| `score_arrangement(path)` | Score Disney-style quality | Dict |
| `export_dataset(format)` | Export annotations | Path |
| `get_stats()` | Get comprehensive statistics | Dict |

### SpatialAnalyzer

**Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `analyze_arrangement(plants, image_size)` | Analyze plant positions | ArrangementAnalysis |
| `analyze_image(image)` | Analyze image file | ArrangementAnalysis |
| `compute_disney_metrics(analysis)` | Calculate Disney scores | DisneyStyleMetrics |

### PlantTrainer

**Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `prepare_dataset(data_dir)` | Create data loaders | Tuple |
| `build_model(backbone, pretrained)` | Build neural network | Model |
| `train(train_loader, val_loader)` | Train model | TrainingHistory |
| `predict(images, return_probs)` | Make predictions | List |
| `export_model(path, format)` | Export for deployment | Path |
| `load_checkpoint(path)` | Load saved model | None |

---

## Training Pipeline

### Complete Workflow

```
1. DATA COLLECTION
   ├── Configure API keys
   ├── Define species list
   ├── Scrape from multiple sources
   └── Download with validation

2. DATA PREPARATION
   ├── Validate image quality
   ├── Remove duplicates
   ├── Resize and normalize
   └── Create augmented variants

3. ANNOTATION
   ├── Auto-detect arrangements
   ├── Calculate spatial metrics
   ├── Compute Disney scores
   └── Store in dataset organizer

4. TRAINING
   ├── Create train/val/test splits
   ├── Build model with transfer learning
   ├── Train with early stopping
   └── Save checkpoints

5. EVALUATION
   ├── Validate on held-out test set
   ├── Analyze confusion matrix
   ├── Compute per-class metrics
   └── Generate reports

6. DEPLOYMENT
   ├── Export to ONNX/TorchScript
   ├── Create inference pipeline
   └── Integrate with applications
```

### Training Tips

1. **Start with pretrained weights** - Transfer learning dramatically improves results
2. **Freeze backbone initially** - Train only the classifier head first
3. **Use data augmentation** - Creates robust models
4. **Monitor validation loss** - Early stopping prevents overfitting
5. **Balance classes** - Ensure similar sample counts per class

---

## Disney Design Principles

The spatial analyzer evaluates arrangements against these professional Disney landscape design principles:

### 1. Forced Perspective
Plants are arranged with taller specimens in the back and progressively shorter ones toward the front, creating an illusion of greater depth and distance.

### 2. Color Harmony
Colors are chosen to complement each other and create visual flow. Disney uses "color stories" that guide the eye and evoke specific emotions.

### 3. Layering
Multiple height zones (ground cover, low, medium, tall, canopy) create visual depth and interest. Professional Disney landscapes typically use 4-5 distinct layers.

### 4. Focal Points
Clear visual anchors draw the eye and create memorable moments. Specimen plants, unique colors, or architectural elements serve as focal points.

### 5. Symmetry Balance
Arrangements appear balanced but avoid rigid formal symmetry. Asymmetrical balance creates a more natural, inviting appearance.

### 6. Seasonal Interest
Plant selection ensures year-round visual appeal with staggered bloom times and interesting foliage.

### 7. Maintenance Access
Practical spacing allows for maintenance while maintaining the designed aesthetic. Disney's meticulous upkeep is enabled by thoughtful spacing.

---

## Error Handling

### Common Errors and Solutions

**API Rate Limiting:**
```python
# Error: 429 Too Many Requests
# Solution: The skill automatically backs off. Reduce requests_per_second if persistent.
config.rate_limiting.requests_per_second = 0.5
```

**Image Validation Failures:**
```python
# Error: Validation failed: too_small
# Solution: Adjust minimum dimensions
config.validation.min_width = 400
config.validation.min_height = 400
```

**Training Memory Issues:**
```python
# Error: CUDA out of memory
# Solution: Reduce batch size
config.training.batch_size = 8
```

**Missing Dependencies:**
```python
# Error: No ML framework detected
# Solution: Install PyTorch or TensorFlow
# pip install torch torchvision
```

---

## Performance Optimization

### Scraping Performance

- Use all three API sources for maximum coverage
- Enable caching to avoid re-downloading
- Set appropriate rate limits per domain

### Training Performance

- Use GPU acceleration when available
- Enable mixed precision training for larger batches
- Use efficient backbones (MobileNet, EfficientNet-B0)

### Memory Optimization

- Process images in batches
- Clear cache periodically
- Use generators instead of loading all data

---

## Troubleshooting

### No Images Found

1. Check API keys are valid
2. Verify network connectivity
3. Try different search queries
4. Check rate limiter status

### Low Model Accuracy

1. Collect more training images (100+ per class)
2. Use more augmentation
3. Try different backbones
4. Increase training epochs
5. Check class balance

### Slow Training

1. Enable GPU if available
2. Reduce image size
3. Use smaller backbone
4. Enable mixed precision

### Analysis Inconsistent

1. Ensure images are high quality
2. Use consistent image sizes
3. Verify green plant detection threshold

---

## Version History

- **v1.0.0** (2025-12-18): Initial release with full training pipeline

---

## License

This skill is provided for educational and personal use. Ensure compliance with image source terms of service when collecting data.

---

## Support

For issues and feature requests, consult the skill documentation or contact the development team.
