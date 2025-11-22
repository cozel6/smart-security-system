"""
Logger Module - Logging Configuration

This module provides centralized logging setup for the entire application.
Configures both file and console logging with rotation.

Features:
- Rotating file handler (prevents huge log files)
- Console handler with colored output (optional)
- Configurable log levels
- Structured log format with timestamps
- Separate loggers for different modules

Usage:
    from src.utils.logger import setup_logger, get_logger
    # Setup once at application start
    setup_logger()

    # Get logger in any module
    logger = get_logger(__name__)
    logger.info("System started")
    logger.warning("Motion detected")
    logger.error("Camera failed")
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime

from config.settings import settings


def setup_logger(
    name: str = "security_system",
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    max_bytes: Optional[int] = None,
    backup_count: Optional[int] = None,
) -> logging.Logger:
    """
    Setup and configure logger with file and console handlers.

    Args:
        name: Logger name
        log_file: Log file path (default from settings)
        log_level: Log level (default from settings)
        max_bytes: Max log file size in bytes (default from settings)
        backup_count: Number of backup files (default from settings)

    Returns:
        logging.Logger: Configured logger instance

    TODO:
    - Load configuration from settings if not provided
    - Create logs directory if not exists
    - Create logger with name
    - Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Create formatter with timestamp, level, module, message
    - Add rotating file handler
    - Add console handler with colored output (optional)
    - Return configured logger
    """
    # Load deafults from settings if not provided
    log_file = log_file or settings.log_file
    log_level = log_level or settings.log_level
    max_bytes = max_bytes or (settings.log_max_size * 1024 * 1024)  # Convert MB to bytes
    backup_count = backup_count or settings.log_backup_count

    #Create log directory if not exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    #Create or get logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    #Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    #Create formatter with timestamp, level, module, message
    formatter = logging.Formatter(
    fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )

    #Add rotating file handler (prevent huge files)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes= max_bytes,
        backupCount= backup_count,
        encoding='utf-8'
    )

    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    # Use ColoredFormatter for console (we'll implement it next)
    console_handler.setFormatter(ColoredFormatter(
        fmt='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console_handler)

    return logger



def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance
   """

    # Get logger by name
    logger = logging.getLogger(name)

    # If logger has no hadlers, or not cofigured yet
    if not logger.hasHandlers():
        setup_logger(name)
        logger = logging.getLogger(name)
    
    return logger



def log_system_event(event_type: str, message: str, level: str = "INFO") -> None:
    """
    Log system event with structured format.

    Args:
        event_type: Event type (e.g., "MOTION", "DETECTION", "ALERT")
        message: Event message
        level: Log level

    TODO:
    - Get logger
    - Format message with event_type
    - Log at appropriate level
    - Useful for consistent event logging
    """
    # TODO: Implement system event logging
    pass


def log_detection(detection_type: str, confidence: float, details: str = "") -> None:
    """
    Log detection event with details.

    Args:
        detection_type: Type of detection (person, animal, etc.)
        confidence: Detection confidence (0.0-1.0)
        details: Additional details

    TODO:
    - Format detection message
    - Log with INFO level
    - Include timestamp, type, confidence, details
    """
    # TODO: Implement detection logging
    pass


def log_alert(alert_level: str, message: str, sent: bool = False) -> None:
    """
    Log alert event.

    Args:
        alert_level: Alert level (LOW, HIGH, CRITICAL)
        message: Alert message
        sent: Whether alert was sent successfully

    TODO:
    - Format alert message
    - Log with WARNING or ERROR level
    - Include sent status
    """
    # TODO: Implement alert logging
    pass


def get_recent_logs(count: int = 20) -> list:
    """
    Read recent log entries from file.

    Args:
        count: Number of recent entries to retrieve

    Returns:
        list: List of log entry strings

    TODO:
    - Open log file
    - Read last 'count' lines
    - Return as list
    - Handle file not found
    """
    # TODO: Implement log reading
    pass


def clear_old_logs(days: int = 7) -> int:
    """
    Delete log files older than specified days.

    Args:
        days: Age threshold in days

    Returns:
        int: Number of files deleted

    TODO:
    - Find all log files in logs directory
    - Check file modification time
    - Delete files older than threshold
    - Return count of deleted files
    """
    # TODO: Implement log cleanup
    pass


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colored output for console (optional enhancement).

    TODO:
    - Add ANSI color codes for different log levels:
        - DEBUG: Gray
        - INFO: Green
        - WARNING: Yellow
        - ERROR: Red
        - CRITICAL: Bold Red
    - Override format() method
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[1;31m',  # Bold Red
        'RESET': '\033[0m',     # Reset
    }

    def format(self, record):
        """
        Format log record with colors.
        """
        # Get the original formatted message
        log_message = super().format(record)
        
        # Get color based on log level
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']

        # Apply color only to the level name in the message
        colored_message = log_message.replace(
            f'[{record.levelname}]',
            f'[{level_color}{record.levelname}{reset_color}]'
        )

        return colored_message



# TODO: Initialize logger on module import
# Uncomment when ready:
# _root_logger = None
#
# def _init_root_logger():
#     global _root_logger
#     if _root_logger is None:
#         _root_logger = setup_logger()
#
# _init_root_logger()


if __name__ == "__main__":
    """Test logger functionality."""
    print("=== Testing Logger ===\n")

    # Test setup_logger
    logger = setup_logger(name="test_logger", log_file="logs/test.log")
    print("✓ Logger created")

    # Test different log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")

    print("\n✓ Check console output above for colored messages")
    print("✓ Check logs/test.log for file output")

    # Test get_logger
    logger2 = get_logger("test_logger")
    logger2.info("Testing get_logger() - this should work")


    print("\n=== Logger test completed ===")
