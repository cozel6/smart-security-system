"""
Motion Detector Module - OpenCV Motion Detection

This module implements motion detection using OpenCV background subtraction.
Works in conjunction with PIR sensor for dual-mode motion detection.

Algorithms:
- Background Subtraction (MOG2): Adaptive gaussian mixture model
- Contour Detection: Find moving objects by contour area
- Thresholding: Filter small movements (false positives)

Responsibilities:
- Initialize background subtractor
- Process frames to detect motion
- Filter false positives (minimum area threshold)
- Return motion status and detection coordinates

Usage:
    from src.detection.motion_detector import MotionDetector

    detector = MotionDetector(min_area=500)

    # Process frame
    has_motion, contours, motion_frame = detector.detect(frame)

    if has_motion:
        print(f"Motion detected! {len(contours)} objects")
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional

from config.settings import settings


class MotionDetector:
    """
    OpenCV-based motion detection using background subtraction.

    Uses MOG2 (Mixture of Gaussians) algorithm for adaptive
    background modeling and motion detection.
    """

    def __init__(
        self,
        min_area: Optional[int] = None,
        blur_kernel: Tuple[int, int] = (21, 21),
        threshold_value: int = 25,
    ):
        """
        Initialize motion detector.

        Args:
            min_area: Minimum contour area to consider as motion (default from settings)
            blur_kernel: Gaussian blur kernel size (must be odd numbers)
            threshold_value: Binary threshold value (0-255)

        TODO:
        - Load min_area from settings if not provided
        - Initialize MOG2 background subtractor: cv2.createBackgroundSubtractorMOG2()
        - Store blur kernel and threshold parameters
        - Initialize frame counter
        - Initialize previous frame storage
        """
        self.min_area = min_area or settings.motion_min_area
        self.blur_kernel = blur_kernel
        self.threshold_value = threshold_value

        # Background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True
        )

        # Statistics
        self.frame_count = 0
        self.motion_count = 0

    def detect(
        self,
        frame: np.ndarray,
        draw_contours: bool = False
    ) -> Tuple[bool, List[Tuple[int, int, int, int]], Optional[np.ndarray]]:
        """
        Detect motion in frame.
        """
        if frame is None:
            return False
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, self.blur_kernel, 0)

        # Apply background subtractor to get foreground mask
        fg_mask = self.bg_subtractor.apply(blurred)

        # Apply threshold to binary image
        _, thresh = cv2.threshold(fg_mask, self.threshold_value, 255, cv2.THRESH_BINARY)

        # Dilate to fill holes in detect objects
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=2)

        # Find contours in binary image
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filled contours by minium area not get bounding boxes
        bounding_boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= self.min_area:
                x, y, w, h = cv2.boundingRect(contour)
                bounding_boxes.append((x, y, w, h))

        has_motion = len(bounding_boxes) > 0

        # Draw contours if requested
        processed_frame = frame.copy() if draw_contours else None
        if draw_contours and has_motion:
            for(x, y, w, h) in bounding_boxes:
                cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Update statistics
        self.frame_count += 1
        if has_motion:
            self.motion_count += 1
        
        return has_motion, bounding_boxes, processed_frame

    def reset(self) -> None:
        """
        Reset background model.
        """
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True
        )

        # Reset counters
        self.frame_count = 0
        self.motion_count = 0

    def get_motion_mask(self, frame: np.ndarray) -> np.ndarray:
        """
        Get binary motion mask without contour detection.
        """
        if frame is None:
            return None
        
         # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Blur
        blurred = cv2.GaussianBlur(gray, self.blur_kernel, 0)

        # Apply backround subtractor
        fg_mask = self.bg_subtractor.apply(blurred)
        
        # Threshold
        _, thresh = cv2.threshold(fg_mask, self.threshold_value, 255, cv2.THRESH_BINARY)

        return thresh


    def calibrate(self, frames: List[np.ndarray]) -> None:
        """
        Calibrate background model with initial frames.
        """
        # Reset backround model
        self.reset()

        # Process each frame to build backround model
        for frame in frames:
            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, self.blur_kernel, 0)
                # Apply with high learning rate for faster calibration
                self.bg_subtractor.apply(blurred, learningRate=0.5)



    def set_min_area(self, min_area: int) -> None:
        """
        Update minimum area threshold.
        """
        self.min_area = min_area

    def get_sensitivity(self) -> int:
        """
        Get current sensitivity (inverse of min_area).
        """
        # Lower min_area = higher sensitivity
        # Return inverse value (scaled to 0-100 range)
        if self.min_area <= 0:
            return 100
        
        # Map min_area (typical range 100-1000) to sensitivity (100-0)
        max_area = 1000
        sensitivity = int(100 * (1 - min(self.min_area, max_area) / max_area))
        return max(0, min(100, sensitivity))

    def get_statistics(self) -> dict:
        """
        Get motion detection statistics.
        """
        detection_rate = (self.motion_count / self.frame_count * 100) if self.frame_count > 0 else 0
        return {
            "frame_count": self.frame_count,
            "motion_count": self.motion_count,
            "detection_rate": round(detection_rate, 2),
            "min_area": self.min_area,
            "sensitivity": self.get_sensitivity()
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"<MotionDetector: min_area={self.min_area}, frames={self.frame_count}, detections={self.motion_count}>"


# TODO: Add test code when running as main module
if __name__ == "__main__":
    """
    Test motion detector with camera or video file.

    TODO:
    - Initialize camera or load video file
    - Create MotionDetector instance
    - Process frames in loop
    - Display frames with contours
    - Print statistics
    - Press 'q' to quit
    """
    print("Motion Detector test - TODO: Implement test code")
    pass
