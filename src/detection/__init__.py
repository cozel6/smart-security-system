"""
Detection Package

This package contains detection algorithms:
- MotionDetector: OpenCV-based motion detection
- YOLODetector: AI object detection for person vs animal classification
- FaceRecognitionDetector: Face recognition for authorized person identification
"""

from .motion_detector import MotionDetector
from .yolo_detector import YOLODetector, DetectionType, AlertLevel
from .face_recognition_detector import FaceRecognitionDetector

__all__ = ['MotionDetector', 'YOLODetector', 'DetectionType', 'AlertLevel', 'FaceRecognitionDetector']
