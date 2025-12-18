"""
Plant Trainer for Disney Plant Trainer

ML model training for:
- Plant species classification
- Arrangement type detection
- Disney-style scoring
- Spatial relationship learning
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of models that can be trained."""
    SPECIES_CLASSIFIER = "species_classifier"
    ARRANGEMENT_CLASSIFIER = "arrangement_classifier"
    DISNEY_SCORER = "disney_scorer"
    SPATIAL_RELATIONSHIP = "spatial_relationship"
    HEIGHT_PREDICTOR = "height_predictor"
    OBJECT_DETECTOR = "object_detector"


class TrainingStatus(Enum):
    """Status of training process."""
    NOT_STARTED = "not_started"
    PREPARING = "preparing"
    TRAINING = "training"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TrainingConfig:
    """Configuration for model training."""
    model_type: ModelType = ModelType.SPECIES_CLASSIFIER
    epochs: int = 50
    batch_size: int = 32
    learning_rate: float = 0.001
    validation_split: float = 0.15
    early_stopping_patience: int = 10
    checkpoint_frequency: int = 5
    input_size: Tuple[int, int] = (224, 224)
    num_classes: Optional[int] = None
    pretrained: bool = True
    freeze_backbone: bool = False
    augmentation: bool = True
    mixed_precision: bool = False
    optimizer: str = "adam"
    scheduler: str = "cosine"
    weight_decay: float = 0.0001
    dropout: float = 0.2


@dataclass
class TrainingMetrics:
    """Metrics tracked during training."""
    epoch: int = 0
    train_loss: float = 0.0
    train_accuracy: float = 0.0
    val_loss: float = 0.0
    val_accuracy: float = 0.0
    learning_rate: float = 0.0
    epoch_time: float = 0.0


@dataclass
class TrainingHistory:
    """Complete training history."""
    model_type: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: List[TrainingMetrics] = field(default_factory=list)
    best_epoch: int = 0
    best_val_accuracy: float = 0.0
    best_val_loss: float = float('inf')
    total_time: float = 0.0
    status: str = "not_started"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class ModelCheckpoint:
    """Model checkpoint information."""
    epoch: int
    path: str
    val_accuracy: float
    val_loss: float
    is_best: bool
    timestamp: str


class PlantTrainer:
    """
    ML trainer for plant-related models.

    Features:
    - Multiple model types (classifier, detector, scorer)
    - Training with checkpointing
    - Transfer learning support
    - Training history tracking
    - Model export for inference
    """

    SUPPORTED_BACKBONES = [
        "resnet18", "resnet34", "resnet50",
        "efficientnet_b0", "efficientnet_b1", "efficientnet_b2",
        "mobilenet_v2", "mobilenet_v3_small", "mobilenet_v3_large"
    ]

    def __init__(
        self,
        output_dir: Union[str, Path],
        config: Optional[TrainingConfig] = None
    ):
        """
        Initialize the plant trainer.

        Args:
            output_dir: Directory for saving models and logs
            config: Training configuration
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.config = config or TrainingConfig()
        self.history = TrainingHistory()
        self.status = TrainingStatus.NOT_STARTED
        self.checkpoints: List[ModelCheckpoint] = []

        self._model = None
        self._optimizer = None
        self._scheduler = None
        self._device = "cpu"
        self._callbacks: List[Callable] = []

        self._detect_framework()

        logger.info(f"Plant trainer initialized: {self.output_dir}")

    def _detect_framework(self) -> None:
        """Detect available ML framework."""
        self._framework = None

        try:
            import torch
            self._framework = "pytorch"
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using PyTorch on {self._device}")
            return
        except ImportError:
            pass

        try:
            import tensorflow as tf
            self._framework = "tensorflow"
            gpus = tf.config.list_physical_devices('GPU')
            self._device = "GPU" if gpus else "CPU"
            logger.info(f"Using TensorFlow on {self._device}")
            return
        except ImportError:
            pass

        logger.warning("No ML framework detected - training disabled")

    def prepare_dataset(
        self,
        data_dir: Union[str, Path],
        class_mapping: Optional[Dict[str, int]] = None
    ) -> Tuple[Any, Any, Dict[str, int]]:
        """
        Prepare dataset for training.

        Args:
            data_dir: Directory containing image data
            class_mapping: Optional mapping of class names to indices

        Returns:
            Tuple of (train_loader, val_loader, class_mapping)
        """
        data_dir = Path(data_dir)

        if class_mapping is None:
            class_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
            class_mapping = {d.name: i for i, d in enumerate(sorted(class_dirs))}

        self.config.num_classes = len(class_mapping)

        if self._framework == "pytorch":
            return self._prepare_pytorch_dataset(data_dir, class_mapping)
        elif self._framework == "tensorflow":
            return self._prepare_tensorflow_dataset(data_dir, class_mapping)
        else:
            logger.error("No ML framework available for dataset preparation")
            return None, None, class_mapping

    def _prepare_pytorch_dataset(
        self,
        data_dir: Path,
        class_mapping: Dict[str, int]
    ) -> Tuple[Any, Any, Dict[str, int]]:
        """Prepare PyTorch DataLoaders."""
        try:
            import torch
            from torch.utils.data import DataLoader, Dataset, random_split
            from torchvision import transforms
        except ImportError:
            logger.error("PyTorch/torchvision not available")
            return None, None, class_mapping

        class PlantDataset(Dataset):
            def __init__(self, data_dir, class_map, transform=None):
                self.samples = []
                self.transform = transform

                for class_name, class_idx in class_map.items():
                    class_dir = data_dir / class_name
                    if class_dir.exists():
                        for img_path in class_dir.glob("*"):
                            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                                self.samples.append((str(img_path), class_idx))

            def __len__(self):
                return len(self.samples)

            def __getitem__(self, idx):
                img_path, label = self.samples[idx]
                image = Image.open(img_path).convert('RGB')
                if self.transform:
                    image = self.transform(image)
                return image, label

        train_transform = transforms.Compose([
            transforms.Resize(self.config.input_size),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        val_transform = transforms.Compose([
            transforms.Resize(self.config.input_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        full_dataset = PlantDataset(data_dir, class_mapping, train_transform)

        val_size = int(len(full_dataset) * self.config.validation_split)
        train_size = len(full_dataset) - val_size

        train_dataset, val_dataset = random_split(
            full_dataset, [train_size, val_size],
            generator=torch.Generator().manual_seed(42)
        )

        val_dataset.dataset.transform = val_transform

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True
        )

        logger.info(f"Dataset prepared: {train_size} train, {val_size} val samples")

        return train_loader, val_loader, class_mapping

    def _prepare_tensorflow_dataset(
        self,
        data_dir: Path,
        class_mapping: Dict[str, int]
    ) -> Tuple[Any, Any, Dict[str, int]]:
        """Prepare TensorFlow datasets."""
        try:
            import tensorflow as tf
        except ImportError:
            logger.error("TensorFlow not available")
            return None, None, class_mapping

        train_ds = tf.keras.preprocessing.image_dataset_from_directory(
            str(data_dir),
            validation_split=self.config.validation_split,
            subset="training",
            seed=42,
            image_size=self.config.input_size,
            batch_size=self.config.batch_size
        )

        val_ds = tf.keras.preprocessing.image_dataset_from_directory(
            str(data_dir),
            validation_split=self.config.validation_split,
            subset="validation",
            seed=42,
            image_size=self.config.input_size,
            batch_size=self.config.batch_size
        )

        normalization = tf.keras.layers.Rescaling(1./255)
        train_ds = train_ds.map(lambda x, y: (normalization(x), y))
        val_ds = val_ds.map(lambda x, y: (normalization(x), y))

        AUTOTUNE = tf.data.AUTOTUNE
        train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
        val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

        return train_ds, val_ds, class_mapping

    def build_model(
        self,
        backbone: str = "resnet18",
        pretrained: bool = True
    ) -> Any:
        """
        Build model architecture.

        Args:
            backbone: Backbone architecture name
            pretrained: Whether to use pretrained weights

        Returns:
            Model instance
        """
        if self._framework == "pytorch":
            return self._build_pytorch_model(backbone, pretrained)
        elif self._framework == "tensorflow":
            return self._build_tensorflow_model(backbone, pretrained)
        else:
            logger.error("No ML framework available")
            return None

    def _build_pytorch_model(self, backbone: str, pretrained: bool) -> Any:
        """Build PyTorch model."""
        try:
            import torch
            import torch.nn as nn
            from torchvision import models
        except ImportError:
            logger.error("PyTorch not available")
            return None

        weights = "IMAGENET1K_V1" if pretrained else None

        if backbone == "resnet18":
            model = models.resnet18(weights=weights)
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Dropout(self.config.dropout),
                nn.Linear(num_features, self.config.num_classes)
            )
        elif backbone == "resnet34":
            model = models.resnet34(weights=weights)
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Dropout(self.config.dropout),
                nn.Linear(num_features, self.config.num_classes)
            )
        elif backbone == "resnet50":
            model = models.resnet50(weights=weights)
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Dropout(self.config.dropout),
                nn.Linear(num_features, self.config.num_classes)
            )
        elif backbone == "mobilenet_v2":
            model = models.mobilenet_v2(weights=weights)
            num_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(self.config.dropout),
                nn.Linear(num_features, self.config.num_classes)
            )
        elif backbone == "efficientnet_b0":
            model = models.efficientnet_b0(weights=weights)
            num_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(self.config.dropout),
                nn.Linear(num_features, self.config.num_classes)
            )
        else:
            logger.warning(f"Unknown backbone {backbone}, using resnet18")
            model = models.resnet18(weights=weights)
            num_features = model.fc.in_features
            model.fc = nn.Linear(num_features, self.config.num_classes)

        if self.config.freeze_backbone:
            for param in model.parameters():
                param.requires_grad = False
            for param in model.fc.parameters():
                param.requires_grad = True

        self._model = model.to(self._device)
        logger.info(f"Built PyTorch {backbone} model with {self.config.num_classes} classes")

        return self._model

    def _build_tensorflow_model(self, backbone: str, pretrained: bool) -> Any:
        """Build TensorFlow model."""
        try:
            import tensorflow as tf
            from tensorflow.keras import layers, Model
            from tensorflow.keras.applications import (
                ResNet50, MobileNetV2, EfficientNetB0
            )
        except ImportError:
            logger.error("TensorFlow not available")
            return None

        weights = "imagenet" if pretrained else None
        input_shape = (*self.config.input_size, 3)

        if backbone == "resnet50":
            base = ResNet50(weights=weights, include_top=False, input_shape=input_shape)
        elif backbone == "mobilenet_v2":
            base = MobileNetV2(weights=weights, include_top=False, input_shape=input_shape)
        elif backbone == "efficientnet_b0":
            base = EfficientNetB0(weights=weights, include_top=False, input_shape=input_shape)
        else:
            logger.warning(f"Unknown backbone {backbone}, using MobileNetV2")
            base = MobileNetV2(weights=weights, include_top=False, input_shape=input_shape)

        if self.config.freeze_backbone:
            base.trainable = False

        x = layers.GlobalAveragePooling2D()(base.output)
        x = layers.Dropout(self.config.dropout)(x)
        outputs = layers.Dense(self.config.num_classes, activation='softmax')(x)

        self._model = Model(inputs=base.input, outputs=outputs)

        self._model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.config.learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

        logger.info(f"Built TensorFlow {backbone} model with {self.config.num_classes} classes")

        return self._model

    def train(
        self,
        train_loader: Any,
        val_loader: Any,
        progress_callback: Optional[Callable[[TrainingMetrics], None]] = None
    ) -> TrainingHistory:
        """
        Train the model.

        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            progress_callback: Callback for progress updates

        Returns:
            TrainingHistory with results
        """
        if self._model is None:
            raise ValueError("Model not built - call build_model() first")

        self.status = TrainingStatus.PREPARING
        self.history = TrainingHistory(
            model_type=self.config.model_type.value,
            config=asdict(self.config),
            started_at=datetime.now().isoformat()
        )

        start_time = time.time()

        if self._framework == "pytorch":
            self._train_pytorch(train_loader, val_loader, progress_callback)
        elif self._framework == "tensorflow":
            self._train_tensorflow(train_loader, val_loader, progress_callback)
        else:
            self.status = TrainingStatus.FAILED
            self.history.status = "failed"
            return self.history

        self.history.total_time = time.time() - start_time
        self.history.completed_at = datetime.now().isoformat()

        self._save_training_history()

        return self.history

    def _train_pytorch(
        self,
        train_loader: Any,
        val_loader: Any,
        progress_callback: Optional[Callable]
    ) -> None:
        """PyTorch training loop."""
        try:
            import torch
            import torch.nn as nn
            import torch.optim as optim
        except ImportError:
            return

        criterion = nn.CrossEntropyLoss()

        if self.config.optimizer == "adam":
            self._optimizer = optim.Adam(
                self._model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        elif self.config.optimizer == "sgd":
            self._optimizer = optim.SGD(
                self._model.parameters(),
                lr=self.config.learning_rate,
                momentum=0.9,
                weight_decay=self.config.weight_decay
            )
        else:
            self._optimizer = optim.Adam(
                self._model.parameters(),
                lr=self.config.learning_rate
            )

        if self.config.scheduler == "cosine":
            self._scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self._optimizer,
                T_max=self.config.epochs
            )
        elif self.config.scheduler == "step":
            self._scheduler = optim.lr_scheduler.StepLR(
                self._optimizer,
                step_size=10,
                gamma=0.1
            )

        best_val_acc = 0.0
        patience_counter = 0

        self.status = TrainingStatus.TRAINING

        for epoch in range(self.config.epochs):
            epoch_start = time.time()

            self._model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0

            for inputs, labels in train_loader:
                inputs = inputs.to(self._device)
                labels = labels.to(self._device)

                self._optimizer.zero_grad()
                outputs = self._model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                self._optimizer.step()

                train_loss += loss.item()
                _, predicted = outputs.max(1)
                train_total += labels.size(0)
                train_correct += predicted.eq(labels).sum().item()

            self._model.eval()
            val_loss = 0.0
            val_correct = 0
            val_total = 0

            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs = inputs.to(self._device)
                    labels = labels.to(self._device)

                    outputs = self._model(inputs)
                    loss = criterion(outputs, labels)

                    val_loss += loss.item()
                    _, predicted = outputs.max(1)
                    val_total += labels.size(0)
                    val_correct += predicted.eq(labels).sum().item()

            if self._scheduler:
                self._scheduler.step()

            train_acc = train_correct / train_total
            val_acc = val_correct / val_total
            avg_train_loss = train_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)

            metrics = TrainingMetrics(
                epoch=epoch + 1,
                train_loss=avg_train_loss,
                train_accuracy=train_acc,
                val_loss=avg_val_loss,
                val_accuracy=val_acc,
                learning_rate=self._optimizer.param_groups[0]['lr'],
                epoch_time=time.time() - epoch_start
            )

            self.history.metrics.append(metrics)

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self.history.best_epoch = epoch + 1
                self.history.best_val_accuracy = val_acc
                self.history.best_val_loss = avg_val_loss
                patience_counter = 0

                self._save_checkpoint(epoch + 1, val_acc, avg_val_loss, is_best=True)
            else:
                patience_counter += 1

            if (epoch + 1) % self.config.checkpoint_frequency == 0:
                self._save_checkpoint(epoch + 1, val_acc, avg_val_loss, is_best=False)

            if progress_callback:
                progress_callback(metrics)

            logger.info(
                f"Epoch {epoch + 1}/{self.config.epochs} - "
                f"Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.4f}, "
                f"Val Loss: {avg_val_loss:.4f}, Val Acc: {val_acc:.4f}"
            )

            if patience_counter >= self.config.early_stopping_patience:
                logger.info(f"Early stopping at epoch {epoch + 1}")
                break

        self.status = TrainingStatus.COMPLETED
        self.history.status = "completed"

    def _train_tensorflow(
        self,
        train_ds: Any,
        val_ds: Any,
        progress_callback: Optional[Callable]
    ) -> None:
        """TensorFlow training."""
        try:
            import tensorflow as tf
        except ImportError:
            return

        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                patience=self.config.early_stopping_patience,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ModelCheckpoint(
                str(self.output_dir / "best_model.h5"),
                save_best_only=True,
                monitor='val_accuracy'
            )
        ]

        if self.config.scheduler == "cosine":
            callbacks.append(
                tf.keras.callbacks.LearningRateScheduler(
                    lambda epoch: self.config.learning_rate *
                    (1 + np.cos(np.pi * epoch / self.config.epochs)) / 2
                )
            )

        self.status = TrainingStatus.TRAINING

        history = self._model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=self.config.epochs,
            callbacks=callbacks,
            verbose=1
        )

        for epoch, (loss, acc, val_loss, val_acc) in enumerate(zip(
            history.history['loss'],
            history.history['accuracy'],
            history.history['val_loss'],
            history.history['val_accuracy']
        )):
            metrics = TrainingMetrics(
                epoch=epoch + 1,
                train_loss=loss,
                train_accuracy=acc,
                val_loss=val_loss,
                val_accuracy=val_acc
            )
            self.history.metrics.append(metrics)

            if progress_callback:
                progress_callback(metrics)

        best_idx = np.argmax(history.history['val_accuracy'])
        self.history.best_epoch = best_idx + 1
        self.history.best_val_accuracy = history.history['val_accuracy'][best_idx]
        self.history.best_val_loss = history.history['val_loss'][best_idx]

        self.status = TrainingStatus.COMPLETED
        self.history.status = "completed"

    def _save_checkpoint(
        self,
        epoch: int,
        val_acc: float,
        val_loss: float,
        is_best: bool
    ) -> None:
        """Save model checkpoint."""
        checkpoint_name = f"checkpoint_epoch_{epoch}.pt" if not is_best else "best_model.pt"
        checkpoint_path = self.output_dir / checkpoint_name

        if self._framework == "pytorch":
            import torch
            torch.save({
                'epoch': epoch,
                'model_state_dict': self._model.state_dict(),
                'optimizer_state_dict': self._optimizer.state_dict(),
                'val_accuracy': val_acc,
                'val_loss': val_loss,
                'config': asdict(self.config)
            }, checkpoint_path)

        checkpoint = ModelCheckpoint(
            epoch=epoch,
            path=str(checkpoint_path),
            val_accuracy=val_acc,
            val_loss=val_loss,
            is_best=is_best,
            timestamp=datetime.now().isoformat()
        )

        self.checkpoints.append(checkpoint)
        logger.info(f"Saved checkpoint: {checkpoint_path}")

    def _save_training_history(self) -> None:
        """Save training history to JSON."""
        history_path = self.output_dir / "training_history.json"

        history_dict = asdict(self.history)
        history_dict['metrics'] = [asdict(m) for m in self.history.metrics]

        with open(history_path, 'w') as f:
            json.dump(history_dict, f, indent=2)

        logger.info(f"Saved training history: {history_path}")

    def load_checkpoint(self, checkpoint_path: Union[str, Path]) -> None:
        """Load model from checkpoint."""
        checkpoint_path = Path(checkpoint_path)

        if self._framework == "pytorch":
            import torch
            checkpoint = torch.load(checkpoint_path, map_location=self._device)

            if self._model is None:
                config_dict = checkpoint.get('config', {})
                self.config.num_classes = config_dict.get('num_classes', 10)
                self.build_model()

            self._model.load_state_dict(checkpoint['model_state_dict'])
            logger.info(f"Loaded checkpoint from {checkpoint_path}")

        elif self._framework == "tensorflow":
            import tensorflow as tf
            self._model = tf.keras.models.load_model(str(checkpoint_path))
            logger.info(f"Loaded model from {checkpoint_path}")

    def predict(
        self,
        images: Union[Any, List[Any]],
        return_probabilities: bool = False
    ) -> Union[List[int], List[List[float]]]:
        """
        Make predictions on images.

        Args:
            images: Single image or batch of images
            return_probabilities: If True, return class probabilities

        Returns:
            Predicted class indices or probabilities
        """
        if self._model is None:
            raise ValueError("Model not loaded")

        if self._framework == "pytorch":
            return self._predict_pytorch(images, return_probabilities)
        elif self._framework == "tensorflow":
            return self._predict_tensorflow(images, return_probabilities)
        else:
            return []

    def _predict_pytorch(
        self,
        images: Any,
        return_probabilities: bool
    ) -> Union[List[int], List[List[float]]]:
        """PyTorch prediction."""
        import torch
        import torch.nn.functional as F

        self._model.eval()

        with torch.no_grad():
            if not isinstance(images, torch.Tensor):
                images = torch.stack(images)
            images = images.to(self._device)

            outputs = self._model(images)

            if return_probabilities:
                probs = F.softmax(outputs, dim=1)
                return probs.cpu().numpy().tolist()
            else:
                _, predicted = outputs.max(1)
                return predicted.cpu().numpy().tolist()

    def _predict_tensorflow(
        self,
        images: Any,
        return_probabilities: bool
    ) -> Union[List[int], List[List[float]]]:
        """TensorFlow prediction."""
        import numpy as np

        predictions = self._model.predict(images)

        if return_probabilities:
            return predictions.tolist()
        else:
            return np.argmax(predictions, axis=1).tolist()

    def export_model(
        self,
        export_path: Union[str, Path],
        format: str = "onnx"
    ) -> Path:
        """
        Export model for deployment.

        Args:
            export_path: Path to save exported model
            format: Export format (onnx, torchscript, savedmodel)

        Returns:
            Path to exported model
        """
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)

        if self._framework == "pytorch":
            if format == "onnx":
                return self._export_pytorch_onnx(export_path)
            elif format == "torchscript":
                return self._export_pytorch_torchscript(export_path)
        elif self._framework == "tensorflow":
            if format == "savedmodel":
                return self._export_tensorflow_savedmodel(export_path)

        logger.warning(f"Export format {format} not supported")
        return export_path

    def _export_pytorch_onnx(self, export_path: Path) -> Path:
        """Export PyTorch model to ONNX."""
        import torch

        self._model.eval()
        dummy_input = torch.randn(1, 3, *self.config.input_size).to(self._device)

        export_path = export_path.with_suffix('.onnx')
        torch.onnx.export(
            self._model,
            dummy_input,
            str(export_path),
            export_params=True,
            opset_version=11,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
        )

        logger.info(f"Exported model to {export_path}")
        return export_path

    def _export_pytorch_torchscript(self, export_path: Path) -> Path:
        """Export PyTorch model to TorchScript."""
        import torch

        self._model.eval()
        dummy_input = torch.randn(1, 3, *self.config.input_size).to(self._device)

        export_path = export_path.with_suffix('.pt')
        traced_model = torch.jit.trace(self._model, dummy_input)
        traced_model.save(str(export_path))

        logger.info(f"Exported model to {export_path}")
        return export_path

    def _export_tensorflow_savedmodel(self, export_path: Path) -> Path:
        """Export TensorFlow model to SavedModel."""
        self._model.save(str(export_path))
        logger.info(f"Exported model to {export_path}")
        return export_path

    def get_status(self) -> Dict[str, Any]:
        """Get current training status."""
        return {
            "status": self.status.value,
            "framework": self._framework,
            "device": self._device,
            "model_built": self._model is not None,
            "epochs_completed": len(self.history.metrics),
            "best_accuracy": self.history.best_val_accuracy,
            "checkpoints": len(self.checkpoints)
        }
