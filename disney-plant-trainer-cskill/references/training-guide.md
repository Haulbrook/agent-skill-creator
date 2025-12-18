# Training Guide for Disney Plant Trainer

This guide covers best practices for training high-quality plant classification and arrangement scoring models.

## Dataset Preparation

### Recommended Dataset Sizes

| Task | Minimum | Recommended | Optimal |
|------|---------|-------------|---------|
| Species Classification | 50/class | 200/class | 500+/class |
| Arrangement Classification | 100/class | 300/class | 500+/class |
| Disney Scoring | 500 total | 2000 total | 5000+ total |

### Data Collection Strategy

1. **Diversity**: Collect from multiple sources (Unsplash, Pexels, Pixabay)
2. **Quality**: Validate minimum resolution (800x600)
3. **Balance**: Ensure similar counts per class
4. **Variety**: Include different lighting, angles, seasons

### Augmentation Strategy

Enable augmentation to increase effective dataset size:

```python
augmentation=AugmentationConfig(
    horizontal_flip=0.5,      # Most plants are symmetric
    vertical_flip=0.0,        # Don't flip upside down
    rotation_range=(-15, 15), # Slight rotation natural
    brightness_range=(0.8, 1.2),
    contrast_range=(0.8, 1.2),
    saturation_range=(0.8, 1.2)
)
```

## Model Selection

### Backbone Comparison

| Backbone | Params | Speed | Accuracy | Use Case |
|----------|--------|-------|----------|----------|
| MobileNet V2 | 3.4M | Fast | Good | Mobile deployment |
| ResNet18 | 11.7M | Fast | Good | General purpose |
| ResNet34 | 21.8M | Medium | Better | More classes |
| ResNet50 | 25.6M | Medium | Best | Complex tasks |
| EfficientNet-B0 | 5.3M | Medium | Better | Balance |

### Recommended Settings by Task

**Species Classification (5-20 classes)**:
```python
TrainingConfig(
    model_type=ModelType.SPECIES_CLASSIFIER,
    epochs=50,
    batch_size=32,
    learning_rate=0.001,
    backbone="resnet18"
)
```

**Species Classification (50+ classes)**:
```python
TrainingConfig(
    model_type=ModelType.SPECIES_CLASSIFIER,
    epochs=100,
    batch_size=16,
    learning_rate=0.0005,
    backbone="resnet50"
)
```

**Arrangement Classification**:
```python
TrainingConfig(
    model_type=ModelType.ARRANGEMENT_CLASSIFIER,
    epochs=75,
    batch_size=16,
    learning_rate=0.0005,
    backbone="efficientnet_b0"
)
```

## Training Strategies

### Transfer Learning (Recommended)

1. Start with ImageNet pretrained weights
2. Freeze backbone initially (first 10-20 epochs)
3. Unfreeze and fine-tune with lower learning rate

```python
# Phase 1: Train classifier head only
config.freeze_backbone = True
config.learning_rate = 0.001
trainer.train(train_loader, val_loader)

# Phase 2: Fine-tune entire network
config.freeze_backbone = False
config.learning_rate = 0.0001
trainer.train(train_loader, val_loader)
```

### Learning Rate Scheduling

**Cosine Annealing** (Recommended):
- Smoothly decreases learning rate
- Allows exploration then convergence

**Step Decay**:
- Reduces LR by factor at fixed intervals
- Simple but effective

### Early Stopping

```python
TrainingConfig(
    early_stopping_patience=10,  # Stop if no improvement for 10 epochs
    checkpoint_frequency=5       # Save every 5 epochs
)
```

## Monitoring Training

### Key Metrics to Watch

1. **Training Loss**: Should decrease steadily
2. **Validation Loss**: Should decrease, watch for divergence
3. **Validation Accuracy**: Primary metric for classification
4. **Learning Rate**: Ensure scheduling is working

### Signs of Problems

| Problem | Symptoms | Solution |
|---------|----------|----------|
| Overfitting | Val loss increases while train decreases | More augmentation, dropout, early stopping |
| Underfitting | Both losses high and stable | Larger model, more epochs, higher LR |
| Learning rate too high | Loss oscillates or explodes | Reduce LR by 10x |
| Learning rate too low | Very slow progress | Increase LR by 10x |

## Evaluation

### Confusion Matrix Analysis

After training, analyze per-class performance:

```python
# Identify problematic classes
# Look for:
# - Classes with low recall (model misses them)
# - Classes with low precision (model over-predicts)
# - Confused class pairs (commonly mistaken)
```

### Common Issues

1. **Similar Species Confused**: Add more distinctive examples
2. **Class Imbalance**: Oversample minority classes
3. **Poor Generalization**: Increase augmentation variety

## Export and Deployment

### ONNX Export (Cross-platform)

```python
trainer.export_model("model.onnx", format="onnx")
```

### TorchScript Export (PyTorch inference)

```python
trainer.export_model("model.pt", format="torchscript")
```

### SavedModel Export (TensorFlow Serving)

```python
trainer.export_model("model/", format="savedmodel")
```

## Performance Optimization

### GPU Training

- Use CUDA-enabled PyTorch/TensorFlow
- Increase batch size to utilize GPU memory
- Enable mixed precision for faster training

### Memory Management

```python
# For limited GPU memory:
TrainingConfig(
    batch_size=8,           # Reduce batch size
    mixed_precision=True,   # Use FP16
    input_size=(224, 224)   # Smaller input
)
```

## Recommended Workflow

1. **Start Small**: 10-20 species, 100 images each
2. **Establish Baseline**: Train basic model, evaluate
3. **Iterate**: Add more data, try different backbones
4. **Analyze Errors**: Use confusion matrix to guide collection
5. **Fine-tune**: Adjust hyperparameters based on validation
6. **Validate**: Test on held-out data before deployment
