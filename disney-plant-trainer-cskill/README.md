# Disney Plant Trainer

A comprehensive ML training system for learning Disney-style landscape plant arrangements from web images.

## Quick Start

```python
from scripts.main import create_trainer

# Initialize with API keys
trainer = create_trainer(
    unsplash_key="your_unsplash_key",
    pexels_key="your_pexels_key",
    pixabay_key="your_pixabay_key"
)

# Collect plant images
trainer.collect_dataset(
    species=["rose", "tulip", "boxwood", "palm"],
    images_per_species=100
)

# Process and train
trainer.process_dataset(augment=True)
history = trainer.train_classifier(backbone="resnet18", epochs=50)

# Analyze any garden image
score = trainer.score_arrangement("garden.jpg")
print(f"Disney Score: {score['disney_score']:.2f}")
```

## Features

- **Multi-Source Scraping**: Unsplash, Pexels, Pixabay, custom sites
- **Intelligent Caching**: Avoid re-downloading with perceptual hash deduplication
- **Spatial Analysis**: Understand plant relationships, spacing, and height patterns
- **Disney-Style Scoring**: Evaluate arrangements against professional design principles
- **ML Training**: Train classifiers with PyTorch or TensorFlow

## Installation

```bash
pip install -r requirements.txt
```

## API Keys

1. Unsplash: https://unsplash.com/developers
2. Pexels: https://www.pexels.com/api/
3. Pixabay: https://pixabay.com/api/docs/

## Documentation

See [SKILL.md](SKILL.md) for complete documentation.

## License

Educational use. Respect image source terms of service.
