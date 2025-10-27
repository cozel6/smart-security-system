"""
YOLO Detector Module - AI Object Detection

This module implements person vs animal detection using YOLOv5.
Classifies detections to differentiate between human intruders and animals.

YOLO (You Only Look Once):
- Fast real-time object detection
- YOLOv5n (nano): Optimized for edge devices like Raspberry Pi
- Pre-trained on COCO dataset (80 classes)

COCO Classes Used:
- Person: class 0
- Animals: classes 15-23 (bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe)

Alert Levels:
- CRITICAL: Person detected (human intruder)
- LOW: Only animal detected
- HIGH: Both person and animal detected

Usage:
    from src.detection.yolo_detector import YOLODetector, DetectionType

    detector = YOLODetector()
    detector.load_model()

    results = detector.detect(frame)
    if results['type'] == DetectionType.PERSON:
        print("CRITICAL: Person detected!")
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from enum import Enum
from ultralytics import YOLO

from config.settings import settings


class DetectionType(Enum):
    """Detection classification types."""
    NONE = "none"
    PERSON = "person"
    ANIMAL = "animal"
    BOTH = "both"


class AlertLevel(Enum):
    """Alert priority levels."""
    NONE = 0
    LOW = 1      # Animal only
    HIGH = 2     # Person + Animal
    CRITICAL = 3  # Person only


class YOLODetector:
    """
    YOLOv5-based object detector for person vs animal classification.

    Uses pre-trained YOLOv5 nano model optimized for Raspberry Pi.
    """

    # COCO dataset class IDs
    PERSON_CLASS = 0
    ANIMAL_CLASSES = [15, 16, 17, 18, 19, 20, 21, 22, 23]
    # 15: bird, 16: cat, 17: dog, 18: horse, 19: sheep
    # 20: cow, 21: elephant, 22: bear, 23: zebra, 24: giraffe

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence: Optional[float] = None,
        img_size: Optional[int] = None,
    ):
        """
        Initialize YOLO detector.

        Args:
            model_path: Path to YOLO model file (default from settings)
            confidence: Detection confidence threshold 0.0-1.0 (default from settings)
            img_size: Input image size for inference (default from settings)

        TODO:
        - Load model path from settings if not provided
        - Load confidence and img_size from settings
        - Initialize model to None (will load on first use)
        - Initialize statistics counters
        """
        self.model_path = model_path or f"models/{settings.yolo_model}"
        self.confidence = confidence or settings.yolo_confidence
        self.img_size = img_size or settings.yolo_img_size

        self.model = None
        self.model_loaded = False

        # Statistics
        self.inference_count = 0
        self.person_detections = 0
        self.animal_detections = 0

    def load_model(self) -> bool:
        """
        Load YOLO model.

        Returns:
            bool: True if loaded successfully, False otherwise

        TODO:
        - Check if model file exists
        - If not exists:
            - Download YOLOv5n model automatically
            - ultralytics will auto-download on first use
        - Load model: self.model = YOLO(self.model_path)
        - Set model_loaded flag to True
        - Log model info (classes, parameters, etc.)
        - Return True if successful
        - Handle exceptions (file not found, download failed, etc.)
        """
        # TODO: Implement model loading
        pass

    def detect(
        self,
        frame: np.ndarray,
        draw: bool = False
    ) -> Dict:
        """
        Detect objects in frame and classify as person/animal/both.

        Args:
            frame: Input frame (BGR color image)
            draw: If True, draw bounding boxes on frame

        Returns:
            Dict containing:
            - 'type': DetectionType enum (NONE, PERSON, ANIMAL, BOTH)
            - 'alert_level': AlertLevel enum (NONE, LOW, HIGH, CRITICAL)
            - 'detections': List of detection dicts with:
                - 'class': class ID
                - 'class_name': class name (e.g., "person", "cat")
                - 'confidence': detection confidence (0.0-1.0)
                - 'bbox': bounding box (x1, y1, x2, y2)
            - 'frame': processed frame with boxes (if draw=True)
            - 'person_count': number of persons detected
            - 'animal_count': number of animals detected

        TODO:
        1. Check if model is loaded, if not load it
        2. Resize frame to img_size if needed (for faster inference)
        3. Run inference: results = self.model(frame, conf=self.confidence)
        4. Parse results:
            - Extract bounding boxes, classes, confidences
            - Filter by confidence threshold
            - Classify detections (person vs animal)
        5. Count persons and animals
        6. Determine detection type (NONE/PERSON/ANIMAL/BOTH)
        7. Determine alert level based on type
        8. If draw=True:
            - Draw bounding boxes with labels
            - Use different colors for person (red) and animal (green)
        9. Increment statistics
        10. Return results dictionary
        """
        # TODO: Implement detection
        pass

    def _classify_detection(self, class_id: int) -> str:
        """
        Classify detection as person or animal.

        Args:
            class_id: COCO class ID

        Returns:
            str: "person", "animal", or "other"

        TODO:
        - If class_id == PERSON_CLASS, return "person"
        - If class_id in ANIMAL_CLASSES, return "animal"
        - Otherwise return "other"
        """
        # TODO: Implement classification
        pass

    def _determine_alert_level(self, person_count: int, animal_count: int) -> AlertLevel:
        """
        Determine alert level based on detection counts.

        Args:
            person_count: Number of persons detected
            animal_count: Number of animals detected

        Returns:
            AlertLevel: Priority level for alert

        TODO:
        - If person_count > 0 and animal_count == 0: CRITICAL
        - If person_count > 0 and animal_count > 0: HIGH
        - If person_count == 0 and animal_count > 0: LOW
        - If both == 0: NONE
        """
        # TODO: Implement alert level determination
        pass

    def _draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict]
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame.

        Args:
            frame: Input frame
            detections: List of detection dictionaries

        Returns:
            np.ndarray: Frame with drawn boxes

        TODO:
        - For each detection:
            - Get bbox coordinates
            - Choose color based on classification (red for person, green for animal)
            - Draw rectangle: cv2.rectangle()
            - Draw label with class name and confidence
            - Use different thickness for person (thicker = more important)
        - Return annotated frame
        """
        # TODO: Implement drawing
        pass

    def get_class_name(self, class_id: int) -> str:
        """
        Get human-readable class name from class ID.

        Args:
            class_id: COCO class ID

        Returns:
            str: Class name (e.g., "person", "cat", "dog")

        TODO:
        - Use model.names dictionary to get class name
        - Return class name string
        - Handle invalid class IDs
        """
        # TODO: Implement class name lookup
        pass

    def set_confidence(self, confidence: float) -> None:
        """
        Update confidence threshold.

        Args:
            confidence: New confidence value (0.0-1.0)

        TODO:
        - Validate confidence is between 0.0 and 1.0
        - Update self.confidence
        - Raise ValueError if invalid
        """
        # TODO: Implement confidence update
        pass

    def get_statistics(self) -> Dict:
        """
        Get detection statistics.

        Returns:
            Dict: Statistics including inference count, detection counts, etc.

        TODO:
        - Return dict with:
            - inference_count
            - person_detections
            - animal_detections
            - person_rate (person_detections / inference_count)
            - animal_rate (animal_detections / inference_count)
        - Useful for analysis and debugging
        """
        # TODO: Implement statistics
        pass

    def reset_statistics(self) -> None:
        """
        Reset detection statistics.

        TODO:
        - Set all counters to 0
        """
        self.inference_count = 0
        self.person_detections = 0
        self.animal_detections = 0

    def benchmark(self, frame: np.ndarray, iterations: int = 10) -> Dict:
        """
        Benchmark inference performance.

        Args:
            frame: Test frame
            iterations: Number of iterations to run

        Returns:
            Dict: Benchmark results (avg time, FPS, etc.)

        TODO:
        - Run detection iterations times
        - Measure inference time for each iteration
        - Calculate statistics:
            - Average inference time
            - Min/max time
            - FPS (1 / avg_time)
        - Return results dict
        - Useful for performance tuning
        """
        # TODO: Implement benchmark
        pass

    def __repr__(self) -> str:
        """String representation."""
        status = "loaded" if self.model_loaded else "not loaded"
        return f"<YOLODetector: {self.model_path}, confidence={self.confidence}, {status}>"


# TODO: Add test code when running as main module
if __name__ == "__main__":
    """
    Test YOLO detector with camera or image file.

    TODO:
    - Load test image or initialize camera
    - Create YOLODetector instance
    - Load model
    - Run detection on test images
    - Print results and statistics
    - Display annotated image
    - Run benchmark
    """
    print("YOLO Detector test - TODO: Implement test code")
    pass
