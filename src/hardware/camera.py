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
        """
        while not self.stopped:
            try:
                # Read frame from camera
                ret, frame = self.capture.read()
                
                if ret and frame is not None:
                    # Try to put frame in queue (non-blocking)
                    try:
                        # If queue is full, remove old frame first
                        if self.frame_queue.full():
                            try:
                                self.frame_queue.get_nowait()
                            except Empty:
                                pass
                        
                        # Put new frame in queue
                        self.frame_queue.put(frame, block=False)
                        self.frame_count += 1
                        
                    except Exception as e:
                        # Queue operations failed, continue
                        pass
                else:
                    # Frame read failed
                    print(f"Warning: Failed to read frame from camera")
                    time.sleep(0.1)  # Wait before retry
                    
            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(0.1)

        print("Capture loop stopped")




    def get_frame(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get the latest frame from camera.

        Args:
            timeout: Maximum time to wait for frame (seconds)

        Returns:
            numpy.ndarray: Latest frame, or None if no frame available
        """
        try:
            # Try to get frame from queue with timeout
            frame = self.frame_queue.get(timeout=timeout)
            return frame
        except Empty:
            # No frame available
            return None

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read frame (OpenCV-style interface for compatibility).

        Returns:
            Tuple[bool, Optional[np.ndarray]]: (success, frame)
        """
        frame = self.get_frame()
        if frame is not None:
            return(True, frame)
        else:
            return(False, None)

    

    def stop(self) -> None:
        """
        Stop camera capture and cleanup resources.
        """
        if self.stopped:
            print(f"Camera already stopped")
            return
        # Singal thread to stop
        self.stopped = True

        # Wait for thread to finish (with timeout)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        # Release camera
        if self.capture:
            self.capture.release()
            self.capture = None

        # Clear fron queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except Empty:
                break

        # Log statistics
        if self.start_time:
            elapsed = time.time() - self.start_time
            avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
            print(f"✓ Camera stopped. Captured {self.frame_count} frames in {elapsed:.1f}s ({avg_fps:.1f} FPS)")
        else:
            print("✓ Camera stopped")

    def is_opened(self) -> bool:
        """
        Check if camera is opened and capturing.
        Returns:
            bool: True if camera is active, False otherwise
        """
        if self.capture is None:
            return False
            
        if not self.capture.isOpened():
            return False
        
        if self.thread is None or not self.thread.is_alive():
            return False
        
        return not self.stopped

    def get_fps(self) -> float:
        """
        Calculate actual capture FPS.

        Returns:
            float: Frames per second
        """
        if self.start_time is None or self.frame_count == 0:
            return 0.0
        
        elapsed = time.time() - self.start_time
        
        if elapsed == 0:
            return 0.0
        
        return self.frame_count / elapsed

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
