"""
Detection Package

This package contains detection algorithms:
- MotionDetector: OpenCV-based motion detection
- YOLODetector: AI object detection for person vs animal classification
"""

from .motion_detector import MotionDetector
from .yolo_detector import YOLODetector

__all__ = ['MotionDetector', 'YOLODetector']
