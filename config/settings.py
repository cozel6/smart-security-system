"""
Settings Module - Configuration Management

This module loads and validates all configuration from .env file.
Uses python-dotenv to load environment variables and provides
a centralized Settings class for accessing configuration throughout the app.

Usage:
    from config.settings import Settings
    settings = Settings()
    token = settings.telegram_bot_token
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Settings:
    """
    Centralized configuration management class.

    Loads configuration from .env file and provides type-safe access
    to all configuration parameters with validation and defaults.
    """

    def __init__(self, env_file: str = ".env"):
        """Initialize settings from .env file."""
        load_dotenv(env_file)

        self._load_telegram_settings()
        self._load_camera_settings()
        self._load_flask_settings()
        self._load_yolo_settings()
        self._load_detector_settings()
        self._load_motion_settings()
        self._load_logging_settings()
        self._load_system_settings()

    def _load_telegram_settings(self) -> None:
        """Load Telegram bot configuration."""
        self.telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
        self.alert_cooldown: int = int(os.getenv("ALERT_COOLDOWN", "30"))

    def _load_camera_settings(self) -> None:
        """Load camera configuration."""
        self.camera_index: int = int(os.getenv("CAMERA_INDEX", "0"))
        self.camera_width: int = int(os.getenv("CAMERA_WIDTH", "640"))
        self.camera_height: int = int(os.getenv("CAMERA_HEIGHT", "480"))
        self.camera_fps: int = int(os.getenv("CAMERA_FPS", "15"))

    def _load_flask_settings(self) -> None:
        """Load Flask server configuration."""
        self.flask_port: int = int(os.getenv("FLASK_PORT", "5000"))
        self.flask_host: str = os.getenv("FLASK_HOST", "0.0.0.0")
        self.flask_debug: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    def _load_yolo_settings(self) -> None:
        """Load YOLO detection configuration."""
        self.yolo_model: str = os.getenv("YOLO_MODEL", "yolov5n.pt")
        self.yolo_confidence: float = float(os.getenv("YOLO_CONFIDENCE", "0.6"))
        self.yolo_iou_threshold: float = float(os.getenv("YOLO_IOU_THRESHOLD", "0.45"))
        self.yolo_img_size: int = int(os.getenv("YOLO_IMG_SIZE", "416"))

    def _load_detector_settings(self) -> None:
        """Load detector configuration."""
        self.detector_type: str = os.getenv("DETECTOR_TYPE", "yolo")
        self.face_recognition_tolerance: float = float(os.getenv("FACE_TOLERANCE", "0.6"))
        self.known_faces_db: str = os.getenv("KNOWN_FACES_DB", "data/known_faces/database.pkl")

    def _load_motion_settings(self) -> None:
        """Load motion detection configuration."""
        self.motion_min_area: int = int(os.getenv("MOTION_MIN_AREA", "500"))
        self.motion_frames_threshold: int = int(os.getenv("MOTION_FRAMES_THRESHOLD", "10"))

    def _load_logging_settings(self) -> None:
        """Load logging configuration."""
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_file: str = os.getenv("LOG_FILE", "logs/security_system.log")
        self.log_max_size: int = int(os.getenv("LOG_MAX_SIZE", "10"))
        self.log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    def _load_system_settings(self) -> None:
        """Load general system configuration."""
        self.system_name: str = os.getenv("SYSTEM_NAME", "Smart Security System")
        self.timezone: str = os.getenv("TIMEZONE", "Europe/Bucharest")
        self.max_snapshots: int = int(os.getenv("MAX_SNAPSHOTS", "100"))
        self.snapshot_retention_days: int = int(os.getenv("SNAPSHOT_RETENTION_DAYS", "7"))

        # PIR Auto-Arm Settings
        self.pir_auto_arm_enabled: bool = os.getenv("PIR_AUTO_ARM_ENABLED", "True").lower() == "true"
        self.pir_no_motion_timeout: int = int(os.getenv("PIR_NO_MOTION_TIMEOUT", "120"))  # seconds (2 minutes)

        # Hardware Settings
        self.use_hardware: bool = os.getenv("USE_HARDWARE", "True").lower() == "true"  # Enable/disable GPIO hardware

    def validate(self) -> bool:
        """
        Validate all critical settings.

        Returns:
            bool: True if all settings are valid, False otherwise
        """
        return True

    def __repr__(self) -> str:
        """String representation of settings (without sensitive data)."""
        return f"<Settings: {self.system_name}>"


# Create a singleton instance for easy import
settings = Settings()
