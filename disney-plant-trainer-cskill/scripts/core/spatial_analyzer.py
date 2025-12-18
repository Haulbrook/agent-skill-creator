"""
Spatial Analyzer for Disney Plant Trainer

Analyzes plant arrangements to learn:
- Spatial relationships between plants
- Height hierarchies and layering
- Spacing patterns and density
- Disney-style design principles
"""

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

logger = logging.getLogger(__name__)


class ArrangementType(Enum):
    """Types of plant arrangements."""
    LINEAR = "linear"
    CLUSTER = "cluster"
    RADIAL = "radial"
    GRID = "grid"
    ORGANIC = "organic"
    LAYERED = "layered"
    BORDER = "border"
    FOCAL_POINT = "focal_point"
    MIXED = "mixed"


class HeightZone(Enum):
    """Height classification zones."""
    GROUND_COVER = "ground_cover"
    LOW = "low"
    MEDIUM = "medium"
    TALL = "tall"
    CANOPY = "canopy"


@dataclass
class PlantPosition:
    """Position and properties of a detected plant."""
    x: float
    y: float
    width: float
    height: float
    confidence: float = 1.0
    species: Optional[str] = None
    height_zone: Optional[HeightZone] = None
    color_dominant: Optional[Tuple[int, int, int]] = None
    is_focal_point: bool = False


@dataclass
class SpatialRelationship:
    """Relationship between two plants."""
    plant_a_idx: int
    plant_b_idx: int
    distance: float
    angle: float
    height_difference: float
    relationship_type: str


@dataclass
class ArrangementAnalysis:
    """Complete analysis of a plant arrangement."""
    arrangement_type: ArrangementType
    plants: List[PlantPosition]
    relationships: List[SpatialRelationship]
    height_distribution: Dict[HeightZone, int]
    spacing_stats: Dict[str, float]
    symmetry_score: float
    layering_score: float
    disney_style_score: float
    color_harmony_score: float
    focal_point_detected: bool
    forced_perspective: bool
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DisneyStyleMetrics:
    """Metrics specific to Disney landscape design principles."""
    forced_perspective_score: float = 0.0
    color_story_score: float = 0.0
    seasonal_interest_score: float = 0.0
    hidden_mickey_potential: float = 0.0
    immersion_score: float = 0.0
    maintenance_friendliness: float = 0.0
    guest_flow_optimization: float = 0.0
    photo_spot_quality: float = 0.0


class SpatialAnalyzer:
    """
    Analyzer for plant spatial relationships and Disney-style patterns.

    Features:
    - Plant position detection and mapping
    - Height zone classification
    - Spacing pattern analysis
    - Disney design principle evaluation
    - Arrangement type classification
    - Optimization recommendations
    """

    HEIGHT_THRESHOLDS = {
        HeightZone.GROUND_COVER: 0.1,
        HeightZone.LOW: 0.25,
        HeightZone.MEDIUM: 0.5,
        HeightZone.TALL: 0.75,
        HeightZone.CANOPY: 1.0
    }

    DISNEY_PRINCIPLES = {
        "forced_perspective": {
            "description": "Taller plants in back, progressively shorter toward front",
            "weight": 0.2
        },
        "color_harmony": {
            "description": "Colors that complement and create visual flow",
            "weight": 0.15
        },
        "layering": {
            "description": "Multiple height layers creating depth",
            "weight": 0.2
        },
        "focal_points": {
            "description": "Clear visual anchors drawing the eye",
            "weight": 0.15
        },
        "symmetry_balance": {
            "description": "Balanced but not rigid formal symmetry",
            "weight": 0.1
        },
        "seasonal_rotation": {
            "description": "Variety that allows year-round interest",
            "weight": 0.1
        },
        "maintenance_access": {
            "description": "Practical spacing for maintenance",
            "weight": 0.1
        }
    }

    def __init__(self):
        """Initialize the spatial analyzer."""
        if not HAS_NUMPY:
            logger.warning("NumPy not available - some features limited")

        logger.info("Spatial analyzer initialized")

    def analyze_arrangement(
        self,
        plants: List[PlantPosition],
        image_size: Optional[Tuple[int, int]] = None
    ) -> ArrangementAnalysis:
        """
        Analyze a plant arrangement.

        Args:
            plants: List of detected plant positions
            image_size: (width, height) of source image

        Returns:
            ArrangementAnalysis with complete analysis
        """
        if not plants:
            return self._empty_analysis()

        normalized_plants = self._normalize_positions(plants, image_size)

        relationships = self._compute_relationships(normalized_plants)

        arrangement_type = self._classify_arrangement(normalized_plants, relationships)

        height_distribution = self._analyze_height_distribution(normalized_plants)

        spacing_stats = self._compute_spacing_stats(relationships)

        symmetry_score = self._compute_symmetry_score(normalized_plants)

        layering_score = self._compute_layering_score(normalized_plants)

        color_harmony = self._compute_color_harmony(normalized_plants)

        focal_points = [p for p in normalized_plants if p.is_focal_point]
        focal_point_detected = len(focal_points) > 0

        forced_perspective = self._detect_forced_perspective(normalized_plants)

        disney_score = self._compute_disney_score(
            layering_score=layering_score,
            symmetry_score=symmetry_score,
            color_harmony=color_harmony,
            has_focal_point=focal_point_detected,
            forced_perspective=forced_perspective,
            spacing_stats=spacing_stats
        )

        recommendations = self._generate_recommendations(
            plants=normalized_plants,
            arrangement_type=arrangement_type,
            spacing_stats=spacing_stats,
            disney_score=disney_score
        )

        return ArrangementAnalysis(
            arrangement_type=arrangement_type,
            plants=normalized_plants,
            relationships=relationships,
            height_distribution=height_distribution,
            spacing_stats=spacing_stats,
            symmetry_score=symmetry_score,
            layering_score=layering_score,
            disney_style_score=disney_score,
            color_harmony_score=color_harmony,
            focal_point_detected=focal_point_detected,
            forced_perspective=forced_perspective,
            recommendations=recommendations
        )

    def _empty_analysis(self) -> ArrangementAnalysis:
        """Return empty analysis for no plants."""
        return ArrangementAnalysis(
            arrangement_type=ArrangementType.MIXED,
            plants=[],
            relationships=[],
            height_distribution={zone: 0 for zone in HeightZone},
            spacing_stats={"mean": 0, "std": 0, "min": 0, "max": 0},
            symmetry_score=0.0,
            layering_score=0.0,
            disney_style_score=0.0,
            color_harmony_score=0.0,
            focal_point_detected=False,
            forced_perspective=False
        )

    def _normalize_positions(
        self,
        plants: List[PlantPosition],
        image_size: Optional[Tuple[int, int]]
    ) -> List[PlantPosition]:
        """Normalize plant positions to 0-1 range."""
        if not plants:
            return []

        if image_size:
            w, h = image_size
        else:
            max_x = max(p.x + p.width for p in plants)
            max_y = max(p.y + p.height for p in plants)
            w, h = max_x, max_y

        normalized = []
        for p in plants:
            norm_plant = PlantPosition(
                x=p.x / w if w > 0 else 0,
                y=p.y / h if h > 0 else 0,
                width=p.width / w if w > 0 else 0,
                height=p.height / h if h > 0 else 0,
                confidence=p.confidence,
                species=p.species,
                height_zone=p.height_zone or self._classify_height_zone(p.height / h if h > 0 else 0),
                color_dominant=p.color_dominant,
                is_focal_point=p.is_focal_point
            )
            normalized.append(norm_plant)

        return normalized

    def _classify_height_zone(self, relative_height: float) -> HeightZone:
        """Classify a height into zones."""
        for zone, threshold in self.HEIGHT_THRESHOLDS.items():
            if relative_height <= threshold:
                return zone
        return HeightZone.CANOPY

    def _compute_relationships(
        self,
        plants: List[PlantPosition]
    ) -> List[SpatialRelationship]:
        """Compute relationships between all plant pairs."""
        relationships = []

        for i, plant_a in enumerate(plants):
            for j, plant_b in enumerate(plants):
                if i >= j:
                    continue

                center_a = (plant_a.x + plant_a.width / 2, plant_a.y + plant_a.height / 2)
                center_b = (plant_b.x + plant_b.width / 2, plant_b.y + plant_b.height / 2)

                dx = center_b[0] - center_a[0]
                dy = center_b[1] - center_a[1]

                distance = math.sqrt(dx * dx + dy * dy)
                angle = math.degrees(math.atan2(dy, dx))
                height_diff = plant_b.height - plant_a.height

                rel_type = self._classify_relationship(distance, angle, height_diff)

                relationships.append(SpatialRelationship(
                    plant_a_idx=i,
                    plant_b_idx=j,
                    distance=distance,
                    angle=angle,
                    height_difference=height_diff,
                    relationship_type=rel_type
                ))

        return relationships

    def _classify_relationship(
        self,
        distance: float,
        angle: float,
        height_diff: float
    ) -> str:
        """Classify the type of relationship between two plants."""
        if distance < 0.1:
            return "adjacent"
        elif distance < 0.2:
            return "nearby"
        elif distance < 0.4:
            return "moderate_distance"
        else:
            return "far"

    def _classify_arrangement(
        self,
        plants: List[PlantPosition],
        relationships: List[SpatialRelationship]
    ) -> ArrangementType:
        """Classify the overall arrangement type."""
        if len(plants) < 2:
            return ArrangementType.FOCAL_POINT if plants else ArrangementType.MIXED

        x_coords = [p.x + p.width / 2 for p in plants]
        y_coords = [p.y + p.height / 2 for p in plants]

        x_variance = self._variance(x_coords) if len(x_coords) > 1 else 0
        y_variance = self._variance(y_coords) if len(y_coords) > 1 else 0

        if x_variance < 0.02:
            return ArrangementType.LINEAR

        if y_variance < 0.02:
            return ArrangementType.BORDER

        grid_score = self._compute_grid_score(plants)
        if grid_score > 0.8:
            return ArrangementType.GRID

        radial_score = self._compute_radial_score(plants)
        if radial_score > 0.7:
            return ArrangementType.RADIAL

        cluster_score = self._compute_cluster_score(relationships)
        if cluster_score > 0.6:
            return ArrangementType.CLUSTER

        height_zones = set(p.height_zone for p in plants if p.height_zone)
        if len(height_zones) >= 3:
            return ArrangementType.LAYERED

        return ArrangementType.ORGANIC

    def _variance(self, values: List[float]) -> float:
        """Compute variance of a list of values."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)

    def _compute_grid_score(self, plants: List[PlantPosition]) -> float:
        """Compute how grid-like the arrangement is."""
        if len(plants) < 4:
            return 0.0

        x_coords = sorted(set(round(p.x, 2) for p in plants))
        y_coords = sorted(set(round(p.y, 2) for p in plants))

        if len(x_coords) < 2 or len(y_coords) < 2:
            return 0.0

        x_spacings = [x_coords[i + 1] - x_coords[i] for i in range(len(x_coords) - 1)]
        y_spacings = [y_coords[i + 1] - y_coords[i] for i in range(len(y_coords) - 1)]

        x_variance = self._variance(x_spacings) if x_spacings else 1.0
        y_variance = self._variance(y_spacings) if y_spacings else 1.0

        regularity = 1.0 / (1.0 + x_variance + y_variance)

        return min(regularity, 1.0)

    def _compute_radial_score(self, plants: List[PlantPosition]) -> float:
        """Compute how radial the arrangement is."""
        if len(plants) < 3:
            return 0.0

        center_x = sum(p.x for p in plants) / len(plants)
        center_y = sum(p.y for p in plants) / len(plants)

        distances = []
        for p in plants:
            dx = (p.x + p.width / 2) - center_x
            dy = (p.y + p.height / 2) - center_y
            distances.append(math.sqrt(dx * dx + dy * dy))

        if not distances:
            return 0.0

        variance = self._variance(distances)
        mean_dist = sum(distances) / len(distances)

        if mean_dist == 0:
            return 0.0

        cv = math.sqrt(variance) / mean_dist
        radial_score = 1.0 / (1.0 + cv * 5)

        return radial_score

    def _compute_cluster_score(self, relationships: List[SpatialRelationship]) -> float:
        """Compute clustering score from relationships."""
        if not relationships:
            return 0.0

        distances = [r.distance for r in relationships]
        mean_dist = sum(distances) / len(distances)

        close_pairs = sum(1 for d in distances if d < mean_dist * 0.5)
        far_pairs = sum(1 for d in distances if d > mean_dist * 1.5)

        if len(distances) == 0:
            return 0.0

        cluster_ratio = (close_pairs - far_pairs) / len(distances)
        return max(0, min(1, (cluster_ratio + 1) / 2))

    def _analyze_height_distribution(
        self,
        plants: List[PlantPosition]
    ) -> Dict[HeightZone, int]:
        """Analyze distribution of plants across height zones."""
        distribution = {zone: 0 for zone in HeightZone}

        for plant in plants:
            if plant.height_zone:
                distribution[plant.height_zone] += 1

        return distribution

    def _compute_spacing_stats(
        self,
        relationships: List[SpatialRelationship]
    ) -> Dict[str, float]:
        """Compute spacing statistics from relationships."""
        if not relationships:
            return {"mean": 0, "std": 0, "min": 0, "max": 0, "cv": 0}

        distances = [r.distance for r in relationships]

        mean_dist = sum(distances) / len(distances)
        variance = sum((d - mean_dist) ** 2 for d in distances) / len(distances)
        std_dist = math.sqrt(variance)

        return {
            "mean": round(mean_dist, 4),
            "std": round(std_dist, 4),
            "min": round(min(distances), 4),
            "max": round(max(distances), 4),
            "cv": round(std_dist / mean_dist, 4) if mean_dist > 0 else 0
        }

    def _compute_symmetry_score(self, plants: List[PlantPosition]) -> float:
        """Compute bilateral symmetry score."""
        if len(plants) < 2:
            return 0.0

        center_x = sum(p.x + p.width / 2 for p in plants) / len(plants)

        left_plants = [p for p in plants if (p.x + p.width / 2) < center_x]
        right_plants = [p for p in plants if (p.x + p.width / 2) > center_x]

        if not left_plants or not right_plants:
            return 0.0

        count_diff = abs(len(left_plants) - len(right_plants))
        count_balance = 1.0 - (count_diff / max(len(left_plants), len(right_plants)))

        left_heights = [p.height for p in left_plants]
        right_heights = [p.height for p in right_plants]

        mean_left = sum(left_heights) / len(left_heights)
        mean_right = sum(right_heights) / len(right_heights)

        height_balance = 1.0 - abs(mean_left - mean_right)

        return (count_balance * 0.5 + height_balance * 0.5)

    def _compute_layering_score(self, plants: List[PlantPosition]) -> float:
        """Compute how well the arrangement demonstrates layering."""
        if len(plants) < 3:
            return 0.0

        height_zones_present = set(p.height_zone for p in plants if p.height_zone)
        zone_diversity = len(height_zones_present) / len(HeightZone)

        sorted_by_y = sorted(plants, key=lambda p: p.y)
        height_progression = 0
        for i in range(len(sorted_by_y) - 1):
            if sorted_by_y[i].height <= sorted_by_y[i + 1].height:
                height_progression += 1

        progression_score = height_progression / (len(plants) - 1) if len(plants) > 1 else 0

        return (zone_diversity * 0.6 + progression_score * 0.4)

    def _compute_color_harmony(self, plants: List[PlantPosition]) -> float:
        """Compute color harmony score from plant colors."""
        colors = [p.color_dominant for p in plants if p.color_dominant]

        if len(colors) < 2:
            return 0.5

        green_count = sum(1 for c in colors if c[1] > c[0] and c[1] > c[2])
        green_ratio = green_count / len(colors)

        unique_hues = len(set(self._rgb_to_hue(c) for c in colors))
        diversity = min(unique_hues / 6, 1.0)

        return (green_ratio * 0.4 + diversity * 0.3 + 0.3)

    def _rgb_to_hue(self, rgb: Tuple[int, int, int]) -> int:
        """Convert RGB to hue value (0-360)."""
        r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
        max_c = max(r, g, b)
        min_c = min(r, g, b)

        if max_c == min_c:
            return 0

        diff = max_c - min_c

        if max_c == r:
            h = (g - b) / diff
        elif max_c == g:
            h = 2 + (b - r) / diff
        else:
            h = 4 + (r - g) / diff

        h *= 60
        if h < 0:
            h += 360

        return int(h) // 30 * 30

    def _detect_forced_perspective(self, plants: List[PlantPosition]) -> bool:
        """Detect if arrangement uses forced perspective."""
        if len(plants) < 3:
            return False

        sorted_by_y = sorted(plants, key=lambda p: p.y)

        front_avg_height = sum(p.height for p in sorted_by_y[:len(sorted_by_y) // 3]) / max(1, len(sorted_by_y) // 3)
        back_avg_height = sum(p.height for p in sorted_by_y[-len(sorted_by_y) // 3:]) / max(1, len(sorted_by_y) // 3)

        return back_avg_height > front_avg_height * 1.2

    def _compute_disney_score(
        self,
        layering_score: float,
        symmetry_score: float,
        color_harmony: float,
        has_focal_point: bool,
        forced_perspective: bool,
        spacing_stats: Dict[str, float]
    ) -> float:
        """Compute overall Disney-style score."""
        scores = {
            "layering": layering_score * self.DISNEY_PRINCIPLES["layering"]["weight"],
            "symmetry": symmetry_score * self.DISNEY_PRINCIPLES["symmetry_balance"]["weight"],
            "color": color_harmony * self.DISNEY_PRINCIPLES["color_harmony"]["weight"],
            "focal_point": (1.0 if has_focal_point else 0.3) * self.DISNEY_PRINCIPLES["focal_points"]["weight"],
            "perspective": (1.0 if forced_perspective else 0.5) * self.DISNEY_PRINCIPLES["forced_perspective"]["weight"]
        }

        spacing_regularity = 1.0 - min(spacing_stats.get("cv", 0), 1.0)
        scores["maintenance"] = spacing_regularity * self.DISNEY_PRINCIPLES["maintenance_access"]["weight"]

        scores["seasonal"] = 0.5 * self.DISNEY_PRINCIPLES["seasonal_rotation"]["weight"]

        total_score = sum(scores.values())

        return round(min(total_score, 1.0), 3)

    def _generate_recommendations(
        self,
        plants: List[PlantPosition],
        arrangement_type: ArrangementType,
        spacing_stats: Dict[str, float],
        disney_score: float
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        height_zones = set(p.height_zone for p in plants if p.height_zone)
        if len(height_zones) < 3:
            recommendations.append(
                "Add more height variety - include ground cover, mid-height shrubs, and tall elements"
            )

        cv = spacing_stats.get("cv", 0)
        if cv > 0.5:
            recommendations.append(
                "Consider more consistent spacing between plants for a polished look"
            )
        elif cv < 0.1 and arrangement_type != ArrangementType.GRID:
            recommendations.append(
                "Add some variation to spacing to create a more natural appearance"
            )

        focal_count = sum(1 for p in plants if p.is_focal_point)
        if focal_count == 0:
            recommendations.append(
                "Add a focal point element - a specimen plant or feature to draw the eye"
            )
        elif focal_count > 3:
            recommendations.append(
                "Too many focal points can be distracting - consider reducing to 1-2 key features"
            )

        if disney_score < 0.5:
            recommendations.append(
                "Layer plants with taller elements in back, medium in middle, low in front"
            )

        if arrangement_type == ArrangementType.LINEAR:
            recommendations.append(
                "Break up linear arrangements with curved edges or grouped clusters"
            )

        return recommendations

    def compute_disney_metrics(
        self,
        analysis: ArrangementAnalysis
    ) -> DisneyStyleMetrics:
        """
        Compute detailed Disney-style metrics.

        Args:
            analysis: ArrangementAnalysis to evaluate

        Returns:
            DisneyStyleMetrics with detailed scores
        """
        metrics = DisneyStyleMetrics()

        metrics.forced_perspective_score = 1.0 if analysis.forced_perspective else 0.3

        metrics.color_story_score = analysis.color_harmony_score

        height_zones = set(p.height_zone for p in analysis.plants if p.height_zone)
        metrics.seasonal_interest_score = min(len(height_zones) / 4, 1.0)

        if analysis.arrangement_type == ArrangementType.CLUSTER:
            cluster_count = self._count_clusters(analysis.plants)
            if cluster_count == 3:
                metrics.hidden_mickey_potential = 0.8
            elif cluster_count > 0:
                metrics.hidden_mickey_potential = 0.3

        metrics.immersion_score = (
            analysis.layering_score * 0.4 +
            (1.0 if analysis.focal_point_detected else 0.0) * 0.3 +
            analysis.disney_style_score * 0.3
        )

        cv = analysis.spacing_stats.get("cv", 1.0)
        metrics.maintenance_friendliness = 1.0 - min(cv, 1.0)

        metrics.guest_flow_optimization = analysis.symmetry_score * 0.5 + 0.5

        metrics.photo_spot_quality = (
            (1.0 if analysis.focal_point_detected else 0.0) * 0.4 +
            analysis.color_harmony_score * 0.3 +
            analysis.layering_score * 0.3
        )

        return metrics

    def _count_clusters(self, plants: List[PlantPosition]) -> int:
        """Count distinct clusters in arrangement."""
        if len(plants) < 3:
            return len(plants)

        visited = [False] * len(plants)
        clusters = 0
        threshold = 0.15

        for i in range(len(plants)):
            if visited[i]:
                continue

            clusters += 1
            stack = [i]

            while stack:
                curr = stack.pop()
                if visited[curr]:
                    continue
                visited[curr] = True

                for j in range(len(plants)):
                    if visited[j]:
                        continue

                    dx = plants[curr].x - plants[j].x
                    dy = plants[curr].y - plants[j].y
                    dist = math.sqrt(dx * dx + dy * dy)

                    if dist < threshold:
                        stack.append(j)

        return clusters

    def analyze_image(
        self,
        image: Union['Image.Image', str],
        detection_model: Optional[Any] = None
    ) -> ArrangementAnalysis:
        """
        Analyze an image for plant arrangements.

        Args:
            image: PIL Image or path to image
            detection_model: Optional pre-trained detection model

        Returns:
            ArrangementAnalysis of detected plants
        """
        if not HAS_PIL:
            raise ImportError("PIL required for image analysis")

        if isinstance(image, str):
            image = Image.open(image)

        if detection_model:
            plants = self._detect_with_model(image, detection_model)
        else:
            plants = self._simple_detection(image)

        return self.analyze_arrangement(plants, image.size)

    def _simple_detection(self, image: 'Image.Image') -> List[PlantPosition]:
        """Simple green-based plant detection."""
        if not HAS_NUMPY:
            return []

        img = image.convert("RGB")
        arr = np.array(img)

        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

        green_mask = (g > r * 0.9) & (g > b * 0.9) & (g > 50)

        h, w = green_mask.shape
        grid_h, grid_w = 4, 4
        cell_h, cell_w = h // grid_h, w // grid_w

        plants = []
        for i in range(grid_h):
            for j in range(grid_w):
                cell = green_mask[
                    i * cell_h:(i + 1) * cell_h,
                    j * cell_w:(j + 1) * cell_w
                ]

                green_ratio = np.mean(cell)
                if green_ratio > 0.2:
                    plants.append(PlantPosition(
                        x=j * cell_w,
                        y=i * cell_h,
                        width=cell_w,
                        height=cell_h,
                        confidence=green_ratio,
                        height_zone=self._classify_height_zone((grid_h - i) / grid_h)
                    ))

        return plants

    def _detect_with_model(
        self,
        image: 'Image.Image',
        model: Any
    ) -> List[PlantPosition]:
        """Detect plants using a trained model."""
        logger.warning("Model-based detection not implemented - using simple detection")
        return self._simple_detection(image)
