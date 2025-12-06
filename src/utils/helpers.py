"""
Helper Functions Module - Utility Functions

This module contains various helper functions used throughout the application.

Categories:
- Time and date utilities
- Image processing utilities
- File management utilities
- System information utilities
- Formatting utilities
"""

import cv2
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
import psutil
import os


# ====================
# Time and Date Utilities
# ====================

def get_timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get current timestamp as formatted string.
    """
    from datetime import datetime
    return datetime.now().strftime(fmt)


def get_filename_timestamp() -> str:
    """
    Get timestamp suitable for filenames (no spaces or colons).
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def parse_timestamp(timestamp_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse timestamp string to datetime object.
    """
    try:
        return datetime.strptime(timestamp_str, fmt)
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}") from e

def time_ago(timestamp: datetime) -> str:
    """
    Get human-readable time difference (e.g., "5 minutes ago").
    """
    now = datetime.now()
    diff = now - timestamp
    seconds = diff.total_seconds()

    if seconds < 10:
        return "just now"
    elif seconds < 60:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    

# ====================
# Image Processing Utilities
# ====================

def resize_frame(
    frame: np.ndarray,
    width: Optional[int] = None,
    height: Optional[int] = None,
    keep_aspect_ratio: bool = True
) -> np.ndarray:
    """
    Resize frame to target dimensions.
    """

    if frame is None:
        raise ValueError("Frame is None")
    
    h,w = frame.shape[:2]

    if width is None and height is None:
        return frame
    
    if keep_aspect_ratio:
        if width is not None:
            height = int(h * (width / w))
        elif height is not None:
            width = int(w * (height / h))
    else:
        if width is None:
            width = w
        if height is None:
            height = h

    return cv2.resize(frame , (width,height) , interpolation= cv2.INTER_AREA)


def add_text_to_frame(
    frame: np.ndarray,
    text: str,
    position: Tuple[int, int] = (10, 30),
    font_scale: float = 0.7,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """
    Add text overlay to frame.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)
    return frame


def draw_bounding_box(
    frame: np.ndarray,
    bbox: Tuple[int, int, int, int],
    label: str = "",
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """
    Draw bounding box with optional label.
    """
    x1, y1, x2, y2 = bbox

    # Draw rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

    # Draw label if provided
    if label:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1

        # Get text size for backround
        (text_width, text_height), baseline = cv2.getTextSize(
            label, font, font_scale, font_thickness
        )

       # Draw background rectangle for text
        cv2.rectangle(frame, (x1, y1 - text_height - 10),
                     (x1 + text_width, y1), color, -1)
        
        #Draw text 
        cv2.putText(frame, label, (x1, y1 -5), font, font_scale, (0, 0, 0), font_thickness, cv2.LINE_AA)
        
    return frame



def convert_to_jpeg(frame: np.ndarray, quality: int = 85) -> bytes:
    """
    Convert frame to JPEG bytes.
    """
    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality]) 
    if not ret:
        raise RuntimeError("Failed to encode frame as JPEG")
    
    return buffer.tobytes()


def frame_to_pil(frame: np.ndarray):
    """
    Convert OpenCV frame (BGR) to PIL Image (RGB).
    """
    from PIL import Image

    # Convert BGR TO RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_frame)

# ====================
# File Management Utilities
# ====================

def save_snapshot(frame: np.ndarray, directory: str = "snapshots") -> str:
    """
    Save frame as snapshot with timestamp filename.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

    # Genrates filename with time stamp
    timestamp = get_filename_timestamp()
    filename = f"snapshot_{timestamp}.jpg"
    filepath = Path(directory) / filename

    # Save frame with cv2.imwrite()
    success = cv2.imwrite(str(filepath), frame)

    if not success:
        raise RuntimeError(f"Filed to save snapshot to {filepath}")
    
    return str(filepath)


def cleanup_old_snapshots(directory: str = "snapshots", max_age_days: int = 7) -> int:
    """
    Delete snapshots older than specified days.
    """
    import time
    directory_path = Path(directory)
    if not directory_path.exists():
        return 0
    count = 0
    current_time = time.time()
    max_age_seconds = max_age_days * 86400
    for file_path in directory_path.glob("*.jpg"):
        file_age = current_time - file_path.stat().st_mtime
        if file_age > max_age_seconds:
            file_path.unlink()
            count += 1
    return count


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in MB.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    size_bytes = path.stat().st_size

    return size_bytes / (1024 * 1024)


# ====================
# System Information Utilities
# ====================

def get_cpu_usage() -> float:
    """
    Get current CPU usage percentage.
    """
    return psutil.virtual_memory().percent


def get_memory_usage() -> float:
    """
    Get current RAM usage percentage.
    """
    return psutil.virtual_memory().percent


def get_cpu_temperature() -> Optional[float]:
    """
    Get Raspberry Pi CPU temperature (Celsius).
    """
    # Try Raspberry Pi method first
    thermal_path = Path("/sys/class/thermal/thermal_zone0/temp")
    if thermal_path.exists():
        try:
            temp_str = thermal_path.read_text().strip()
            # Pi returns millidegrees, convert to degrees
            return float(temp_str) / 1000.0
        except Exception:
            pass
    
    # Fallback for Mac - try psutil sensors_temperatures (if available)
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                # Get first available temperature sensor
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
    except (AttributeError, Exception):
        pass
    
    # Return None if temperature not available (Mac without sensors)
    return None


def get_system_uptime() -> float:
    """
    Get system uptime in seconds.
    """
    import time
    boot_time = psutil.boot_time()
    return time.time() - boot_time




def format_uptime(seconds: float) -> str:
    """
    Format uptime as human-readable string.
    
    Args:
        seconds: Uptime in seconds
    """
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    #Build formatted string
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")

    return " ".join(parts)



# ====================
# Formatting Utilities
# ====================

def format_bytes(bytes: int) -> str:
    """
    Format bytes as human-readable size.
    """
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 ** 2:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 ** 3:
        return f"{bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes / (1024 ** 3):.2f} GB"


def format_confidence(confidence: float) -> str:
    """
    Format confidence as percentage string.
    """
    return f"{confidence * 100:.1f}%"


def format_fps(fps: float) -> str:
    """
    Format FPS value.
    """
    return f"{fps:.1f} FPS"


# ====================
# Validation Utilities
# ====================

def validate_image(frame: np.ndarray) -> bool:
    """
    Validate if frame is valid image.
    """
    if frame is None:
        return False
    
    if not isinstance(frame, np.ndarray):
        return False
    
    if len(frame.shape) < 2:
        return False
    
    h, w = frame.shape[:2]
    
    return h >= 1 and w >= 1

    

def validate_bounding_box(bbox: tuple, frame_shape: tuple) -> bool:
    """
    Validate if bounding box is within frame bounds.
    """
    if len(bbox) != 4:
        return False
    
    x1, y1, x2, y2 = bbox
    h, w = frame_shape[:2]

    return(
        0 <= x1 < w and 0 <= y1 < h and
        0 <= x2 < w and 0 <= y2 < h and
        x1 < x2 and y1 < y2
    ) 
    


if __name__ == "__main__":
    """Test helper functions."""
    print("Helper functions test - TODO: Implement test code")
    pass
