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
        """
        try:
            from pathlib import Path
            import os

            # Log model loading
            print(f"Loading YOLO model: {self.model_path}")

            # Chek if model file exists
            model_file = Path(self.model_path)

            # If model doesn't exist, ultralytics will auto-download
            if not model_file.exists():
                print(f"Model not found at {self.model_path}")
                print("Ultralytics will auto-dounload on first use...")

                # Create models directory if it dosen't exists
                model_file.parent.mkdir(parents=True, exist_ok=True)

                # Load model (will triger auto-download)
                self.model = YOLO(self.model_path)

            else:
                #Model exists, load it directly
                print(f"Found existing model at {self.model_path}")
                self.model = YOLO(self.model_path)
            
            # Verify model loaded successfully
            if self.model is None:
                print("ERROR: Failed to load YOLO model")
                return False
            
            # Set model_loaded flag
            self.model_loaded = True

            # Log model information
            print(f"✓ YOLO model loaded successfully!")
            print(f"  - Model: {self.model_path}")
            print(f"  - Classes: {len(self.model.names)} ({', '.join(list(self.model.names.values())[:5])}...)")
            print(f"  - Confidence threshold: {self.confidence}")
            print(f"  - Image size: {self.img_size}")

            return True
        
        except Exception as e:
            print(f"ERROR: Failed to load YOLO model: {e}")
            import traceback
            traceback.print_exc()
            self.model_loaded = False
            return False


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

        """
        try:
            # 1. Check if model is loaded
            if not self.model_loaded:
                print("Model not loaded, attempting to load...")
                if not self.load_model():
                    return {
                        'type': DetectionType.NONE,
                        'alert_level': AlertLevel.NONE,
                        'detections': [],
                        'frame': frame.copy() if draw else None,
                        'person_count': 0,
                        'animal_count': 0,
                    }
            # 2. Keep the original frame
            original_frame = frame.copy()
            inference_frame = frame

            # 3. Run inference
            results = self.model(
                inference_frame,
                conf = self.confidence,
                imgsz = self.img_size,
                verbose = False
            )

            # 4. Parse the results
            detections = []
            person_count = 0
            animal_count = 0

            # Get the first result (single image inference)
            result = results[0]

            # Extract boxes, classes and confidence
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes.xyxy.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()

                # Process each detection
                for i in range(len(boxes)):
                    class_id = int(classes[i])
                    conf_score = float(confidences[i])
                    bbox = boxes[i].tolist()

                    #Classify detection
                    classification = self._classify_detection(class_id)


                    # Skip detection that are not person or animal
                    if classification == "other" :
                        continue

                    #Count person or animal
                    if classification == "person":
                        person_count += 1
                    elif classification == "animal":
                        animal_count += 1
                    
                    # Get class name
                    class_name = self.get_class_name(class_id)

                    # Add detection to list
                    detections.append({
                        'class': class_id,
                        'class_name' : class_name,
                        'confidence' : conf_score,
                        'bbox': bbox,
                        'classification' : classification,
                    })

            # 5. Determine detection type
            if person_count > 0 and animal_count > 0:
                detection_type = DetectionType.BOTH
            elif person_count > 0:
                detection_type = DetectionType.PERSON
            elif animal_count > 0:
                detection_type = DetectionType.ANIMAL
            else:
                detection_type = DetectionType.NONE
            
            # 6. Determine alert level
            alert_level = self._determine_alert_level(person_count, animal_count)

            # 7. Draw detection if requested
            annotated_frame = None
            if draw:
                annotated_frame = self._draw_detections(original_frame, detections)
            
            # 8. Increment statistics
            self.inference_count += 1
            if person_count > 0:
                self.person_detections += 1
            if animal_count > 0:
                self.animal_detections += 1

            # 9. Return results dictionary
            return {
                'type': detection_type,
                'alert_level': alert_level,
                'detections': detections,
                'frame': annotated_frame,
                'person_count': person_count,
                'animal_count': animal_count,
            }

        except Exception as e:
            print(f"ERROR in detect(): {e}")
            import traceback
            traceback.print_exc()

            return {
            'type': DetectionType.NONE,
            'alert_level': AlertLevel.NONE,
            'detections': [],
            'frame': frame.copy() if draw else None,
            'person_count': 0,
            'animal_count': 0,
        }






    def _classify_detection(self, class_id: int) -> str:
        """
        Classify detection as person or animal.
        """
        if class_id == self.PERSON_CLASS:
            return "person"
        elif class_id in self.ANIMAL_CLASSES:
            return "animal"
        else:
            return "other"

    def _determine_alert_level(self, person_count: int, animal_count: int) -> AlertLevel:
        """
        Determine alert level based on detection counts.
        """
        # CRITICAL: Person detected (human intruder)
        if person_count > 0 and animal_count == 0:
            return AlertLevel.CRITICAL
        
        # HIGH: both person and animal detected
        elif person_count > 0 and animal_count > 0:
            return AlertLevel.HIGH
        
        # LOW: Only animal detected
        elif person_count == 0 and animal_count > 0:
            return AlertLevel.LOW

        # No detection
        else:
            return AlertLevel.NONE

    def _draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict]
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame.
        """
        
        # Create a copy to avoid modifying original
        annotated_frame = frame.copy()

        # Draw each detection
        for det in detections:
            # Get bbox coordinates [x1, y1, x2, y2]
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)

            # Get classification and confidence
            classification = det['classification']
            class_name = det['class_name']
            confidence = det['confidence']

            # Choose color based and classification
            if classification == "person":
                color = (0, 0, 255)  # Red for person (BGR Format)
                thickness = 3  # Thicker box for person
            elif classification == "animal":
                color = (0, 255, 0)  # Green for animal
                thickness = 2
            else:
                color = (255, 0, 0)  # Blue for other
                thickness = 2
            
            # Draw rectangle
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)

            # Prepare label text
            label = f"{class_name} {confidence:.2f}"

            # Get text size for background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, font_thickness
            )

            # Draw label background (filled rectangle)
            label_y = y1 - 10 if y1 - 10 > text_height else y1 + text_height + 10
            cv2.rectangle(
                annotated_frame,
                (x1, label_y - text_height - baseline),
                (x1 + text_width, label_y + baseline),
                color,
                -1  # Filled rectangle
            )

            # Draw label text
            cv2.putText(
                annotated_frame,
                label,
                (x1, label_y),
                font,
                font_scale,
                (255, 255, 255),  # White text
                font_thickness,
                cv2.LINE_AA
            )

        return annotated_frame


    def get_class_name(self, class_id: int) -> str:
        """
        Get human-readable class name from class ID.
        """
        try:
            if self.model is not None and hasattr(self.model, 'names'):
                return self.model.names[class_id]
            else:
                return f"class_{class_id}"
        except (KeyError, IndexError):
            return f"unknown_{class_id}"
        


    def set_confidence(self, confidence: float) -> None:
        """
        Update confidence threshold.
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be betweeen 0.0 and 1.0. got {confidence}")

        self.confidence = confidence
        print(f"Confidence threshold updated to {confidence}")

    def get_statistics(self) -> Dict:
        """
        Get detection statistics.
        """
        person_rate = (
            self.person_detections / self.inference_count
            if self.inference_count > 0
            else 0.0
        )
        animal_rate = (
            self.animal_detections / self.inference_count
            if self.inference_count > 0 
            else 0.0
        )

        return {
        'inference_count': self.inference_count,
        'person_detections': self.person_detections,
        'animal_detections': self.animal_detections,
        'person_rate': person_rate,
        'animal_rate': animal_rate,
        'model_loaded': self.model_loaded,
        'confidence_threshold': self.confidence,
        }


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
        """
        import time
        if not self.model_loaded:
            print("Model not loaded, cannot benchmark")
            return {}
        print(f"Running benchmark with {iterations} iterations...")

        inference_times = []

        for i in range(iterations):
            start_time = time.time()
            _ = self.detect(frame, draw=False)
            end_time = time.time()
            inference_time = end_time - start_time
            inference_times.append(inference_time)
            print(f"  Iteration {i+1}/{iterations}: {inference_time*1000:.1f}ms")

        # Calculate statistics
        avg_time = sum(inference_times) / len(inference_times)
        min_time = min(inference_times)
        max_time = max(inference_times)
        fps = 1.0 / avg_time if avg_time > 0 else 0.0

        results = {
            'iterations': iterations,
            'avg_time_ms': avg_time * 1000,
            'min_time_ms': min_time * 1000,
            'max_time_ms': max_time * 1000,
            'fps': fps,
            'model': self.model_path,
            'img_size': self.img_size,
            'confidence': self.confidence,
        }

        print("\nBenchmark Results:")
        print(f"  Average time: {results['avg_time_ms']:.1f}ms")
        print(f"  Min time: {results['min_time_ms']:.1f}ms")
        print(f"  Max time: {results['max_time_ms']:.1f}ms")
        print(f"  FPS: {results['fps']:.1f}")

        return results



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
