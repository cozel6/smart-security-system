"""
Video Streamer Module - MJPEG Streaming

This module provides MJPEG (Motion JPEG) streaming for web dashboard.
Encodes frames as JPEG and streams via multipart HTTP response.

MJPEG Format:
- Each frame is a complete JPEG image
- Frames separated by multipart boundary
- Simple, widely supported, low latency
- Higher bandwidth than H.264 but acceptable for local network

Usage:
    from src.streaming.video_streamer import VideoStreamer

    streamer = VideoStreamer(get_frame_callback=camera.get_frame)

    # Use in Flask route
    @app.route('/video_feed')
    def video_feed():
        return Response(
            streamer.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
"""

import cv2
import numpy as np
from typing import Callable, Optional, Generator
import time


class VideoStreamer:
    """
    MJPEG video streamer for Flask.
    Generates MJPEG stream from frame source (camera or processed frames).
    """

    def __init__(
        self,
        get_frame_callback: Optional[Callable] = None,
        jpeg_quality: int = 85,
        max_fps: int = 15,
    ):
        """
        Initialize video streamer.
        """
        self.get_frame_callback = get_frame_callback
        self.jpeg_quality = jpeg_quality
        self.max_fps = max_fps
        self.frame_interval = 1.0 / max_fps

        # Statistics
        self.frames_streamed = 0
        self.bytes_sent = 0

    def generate_frames(self) -> Generator[bytes, None, None]:
        """
        Generate MJPEG stream frames.
        """
        last_frame_time = 0
        while True:
            try:
                # Check if we need to wait to respect max_fps
                current_time = time.time()
                elapsed = current_time - last_frame_time
                if elapsed < self.frame_interval:
                    time.sleep(self.frame_interval - elapsed)
                
                # Get frame from callback
                if self.get_frame_callback is None:
                    time.sleep(0.1)
                    continue

                frame = self.get_frame_callback()

                # Skip if no frame available
                if frame is None:
                    time.sleep(0.1)
                    continue

                # Encode frame as JPEG
                jpeg_data = self.encode_frame(frame)

                # Format as MJPEG multipart frame
                mjpeg_frame = self.format_mjpeg_frame(jpeg_data)

                # Yiald frame data
                yield mjpeg_frame

                # Update statistics
                self.frames_streamed += 1
                self.bytes_sent += len(mjpeg_frame)

                # Update last frame time 
                last_frame_time = time.time()

            except GeneratorExit:
                # Client disconnected
                break
            except Exception as e:
                print(f"Error in generate_frames: {e}")
                time.sleep(0.1)
                continue

    def encode_frame(self, frame: np.ndarray) -> bytes:
        """
        Encode frame as JPEG.
        """
        try:
            # Encode frame as JPEG with quality parameter
            ret, buffer = cv2.imencode(
                '.jpg',
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
            )

            if not ret:
                raise RuntimeError("Failed to encode frame as JPEG")
            
            # Convert to bytes
            return buffer.tobytes()
        
        except Exception as e:
            raise RuntimeError(f"JPEG encoding failed: {e}")

    def format_mjpeg_frame(self, jpeg_data: bytes) -> bytes:
        """
        Format JPEG data as MJPEG multipart frame.
        """
         # Create multipart frame with headers
        frame_data = (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n'
            b'Content-Length: ' + str(len(jpeg_data)).encode() + b'\r\n'
            b'\r\n' +
            jpeg_data +
            b'\r\n'
        )
    
        return frame_data
        

    def set_frame_callback(self, callback: Callable) -> None:
        """
        Update frame source callback.
        """
        self.get_frame_callback = callback

    def set_quality(self, quality: int) -> None:
        """
        Update JPEG quality.
        """
        # Validate fps is positive
        if not 0 <= quality <= 100:
            raise ValueError(f"Quality must be between 0-100, got {quality}")
        
        self.jpeg_quality = quality


    def set_max_fps(self, fps: int) -> None:
        """
        Update maximum streaming FPS.
        """
        # Validate fps is positive
        if fps <= 0:
            raise ValueError(f"FPS must be positive, got {fps}")
        
        self.max_fps = fps
        self.frame_interval = 1.0 / fps

    def get_statistics(self) -> dict:
        """
        Get streaming statistics.
        """
        # Calculate average frame size
        avg_frame_size = (
            self.bytes_sent / self.frames_streamed
            if self.frames_streamed > 0
            else 0
        )
        # Calculate bandwidth in Mbps (rough estimate)
        # Assumes frames_streamed happened over time
        bandwidth_mbps = 0.0
        if self.frames_streamed > 0 and self.max_fps > 0:
            bytes_per_second = avg_frame_size * self.max_fps
            bandwidth_mbps = (bytes_per_second * 8) / (1024 * 1024)
        
        return {
            'frames_streamed': self.frames_streamed,
            'bytes_sent': self.bytes_sent,
            'average_frame_size': round(avg_frame_size, 2),
            'bandwidth_mbps': round(bandwidth_mbps, 2)
        }


    def reset_statistics(self) -> None:
        """
        Reset streaming statistics.
        """
        self.frames_streamed = 0
        self.bytes_sent = 0

    def __repr__(self) -> str:
        """String representation."""
        return f"<VideoStreamer: quality={self.jpeg_quality}, max_fps={self.max_fps}, frames={self.frames_streamed}>"


# Utility function for standalone MJPEG streaming
def create_mjpeg_stream(frame_source: Callable, quality: int = 85, max_fps: int = 15) -> Generator:
    """
    Create MJPEG stream from frame source (utility function).
    """
    streamer = VideoStreamer(
        get_frame_callback=frame_source,
        jpeg_quality=quality,
        max_fps=max_fps
    )
    return streamer.generate_frames()


if __name__ == "__main__":
    """Test video streamer."""
    print("Video Streamer test - TODO: Implement test code")
    pass
