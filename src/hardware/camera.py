"""
Camera Module - USB Webcam Interface

This module handles video capture from USB webcam.
Implements threaded frame capture for better performance.

Responsibilities:
- Initialize USB camera with OpenCV
- Continuous frame capture in separate thread
- Thread-safe frame retrieval
- Graceful shutdown and resource cleanup

Usage:
    from src.hardware.camera import Camera

    camera = Camera(camera_index=0)
    camera.start()

    # Get frame
    frame = camera.get_frame()
    if frame is not None:
        # Process frame
        pass

    camera.stop()
"""

import cv2
import threading
import time
from queue import Queue, Empty
from typing import Optional, Tuple
import numpy as np

from config.settings import settings


class Camera:
    """
    Thread-safe camera capture class.

    Captures frames continuously in a background thread and provides
    thread-safe access to the latest frame via a queue.
    """

    def __init__(
        self,
        camera_index: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[int] = None,
    ):
        """
        Initialize camera interface.

        Args:
            camera_index: Camera device index (default from settings)
            width: Frame width in pixels (default from settings)
            height: Frame height in pixels (default from settings)
            fps: Target FPS (default from settings)

        TODO:
        - Load camera settings from config if not provided
        - Initialize cv2.VideoCapture with camera_index
        - Set camera properties (width, height, FPS)
        - Initialize threading components (thread, lock, event)
        - Initialize frame queue (maxsize=2 to keep only latest frames)
        - Set stopped flag to False
        """
        # Camera settings
        self.camera_index = camera_index or settings.camera_index
        self.width = width or settings.camera_width
        self.height = height or settings.camera_height
        self.fps = fps or settings.camera_fps

        # OpenCV VideoCapture object
        self.capture = None  # TODO: Initialize cv2.VideoCapture

        # Threading components
        self.thread = None  # TODO: Initialize Thread
        self.stopped = False  # Flag to stop capture thread
        self.lock = threading.Lock()  # Thread lock for frame access

        # Frame queue (keep only latest frames)
        self.frame_queue = Queue(maxsize=2)

        # Statistics
        self.frame_count = 0
        self.start_time = None

    def start(self) -> bool:
        """
        Start camera capture thread with auto-detection. / NEW

        Returns:
            bool: True if started successfully, False otherwise
        """
        # Try configured index first
        if self._try_camera(self.camera_index):
            print(f"Camera started at cofiguration index {self.camera_index} (from config)...")
            return self._finalize_start()
        
        # Auto-detect camera index
        print("Configured camera index failed. Starting auto-detection...")
        for index in range(5):
            if index == self.camera_index:
                continue

            # Auto-detection fallback
            print(f"Camera camera index {index}... ")
            if self._try_camera(index):
                print(f"✓ Found camera at index {index}")
                self.camera_index = index
                return self._finalize_start()
            
        print("No camera false")
        return False

    def _try_camera(self, index: int) -> bool:
        """
        Try to open camera at specific index.

        Args:
            index: Camera index to try

        Returns:
            bool: True if camera opened and can read frames
        """
        try:
            # Test if camera can be opened
            test_cap = cv2.VideoCapture(index)
            if not test_cap.isOpened():
                test_cap.release()
                return False
            
            # Try to read a test frame
            ret, _ = test_cap.read()
            test_cap.release()

            if not ret:
                return False
            
            # Success - now open for real use
            self.capture = cv2.VideoCapture(index)
            return self.capture.isOpened()
            
        except Exception as e:
            print(f"Error trying camera {index}: {e}")
            return False
    
    def _finalize_start(self) -> bool:
        """
        Finalize camera start - set properties and start thread.

        Called after camera is successfully opened.

        Returns:
            bool: True if finalization successful
        """
        # Set camera properties
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)

        # Get actual resolution
        actual_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"✓ Camera resolution: {actual_width}x{actual_height}")

        # Start capture thread
        self.stopped = False
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()  # IMPORTANT!

        # Wait for first frame
        time.sleep(0.5)
        
        # Verify frames are being captured
        if not self.frame_queue.empty():
            print(f"✓ Capturing frames ({self.frame_count} in queue)")
        else:
            print("⚠ Warning: No frames captured yet")

        print(f"✓ Camera started successfully")
        return True

    def _capture_loop(self) -> None:
        """
        Main capture loop (runs in separate thread).

        Continuously reads frames from camera and puts them in queue.
        Discards old frames if queue is full (keep only latest).

        TODO:
        - Loop while not self.stopped
        - Read frame from self.capture.read()
        - If frame read successfully:
            - Try to put frame in queue (non-blocking)
            - If queue full, remove old frame first
            - Increment frame_count
        - If frame read failed:
            - Log error
            - Sleep briefly and retry
        - Handle exceptions gracefully
        """
        # TODO: Implement capture loop
        pass

    def get_frame(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get the latest frame from camera.

        Args:
            timeout: Maximum time to wait for frame (seconds)

        Returns:
            numpy.ndarray: Latest frame, or None if no frame available

        TODO:
        - Try to get frame from queue (with timeout)
        - If queue empty, return None
        - Return frame as numpy array
        - Handle Empty exception from queue
        """
        # TODO: Implement thread-safe frame retrieval
        pass

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read frame (OpenCV-style interface for compatibility).

        Returns:
            Tuple[bool, Optional[np.ndarray]]: (success, frame)

        TODO:
        - Call get_frame()
        - Return (True, frame) if frame exists
        - Return (False, None) if no frame
        """
        # TODO: Implement OpenCV-compatible read method
        pass

    def stop(self) -> None:
        """
        Stop camera capture and cleanup resources.

        TODO:
        - Set self.stopped = True to signal thread to stop
        - Wait for capture thread to finish (thread.join with timeout)
        - Release camera (capture.release())
        - Clear frame queue
        - Log final statistics (total frames captured, average FPS)
        """
        # TODO: Implement graceful shutdown
        pass

    def is_opened(self) -> bool:
        """
        Check if camera is opened and capturing.

        Returns:
            bool: True if camera is active, False otherwise

        TODO:
        - Check if capture object exists and is opened
        - Check if thread is alive
        - Return True only if both conditions met
        """
        # TODO: Implement status check
        pass

    def get_fps(self) -> float:
        """
        Calculate actual capture FPS.

        Returns:
            float: Frames per second

        TODO:
        - Calculate elapsed time since start
        - Divide frame_count by elapsed time
        - Return calculated FPS
        - Handle edge cases (no frames captured yet)
        """
        # TODO: Implement FPS calculation
        pass

    def get_resolution(self) -> Tuple[int, int]:
        """
        Get current camera resolution.

        Returns:
            Tuple[int, int]: (width, height)

        TODO:
        - Get actual resolution from capture object
        - Return (width, height) tuple
        """
        return (self.width, self.height)

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def __repr__(self) -> str:
        """String representation."""
        status = "active" if self.is_opened() else "stopped"
        return f"<Camera: index={self.camera_index}, {self.width}x{self.height}, {status}>"


# TODO: Add test code when running as main module
if __name__ == "__main__":
    """
    Test camera functionality.

    TODO:
    - Initialize camera
    - Capture frames for 10 seconds
    - Display frames with cv2.imshow()
    - Print FPS statistics
    - Test graceful shutdown
    """
    print("Camera test - TODO: Implement test code")
    pass
