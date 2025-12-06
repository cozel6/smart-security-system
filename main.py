"""
Smart Security System - Main Entry Point

This is the main entry point for the intelligent security system.
Initializes and starts all system components.

Usage:
    python3 main.py [options]

Options:
    --arm           Start system in armed state
    --no-web        Disable web dashboard
    --no-telegram   Disable Telegram bot
    --debug         Enable debug mode

Example:
    python3 main.py --arm
"""

import sys
import argparse
import time
import signal
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.system_manager import SystemManager
from src.utils.logger import setup_logger, get_logger
from config.settings import settings


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Smart Security System - AI-powered intrusion detection'
    )

    parser.add_argument('--arm', action='store_true',
                       help='Start system in armed state')
    parser.add_argument('--no-web', action='store_true',
                       help='Disable web dashboard')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')

    args = parser.parse_args()
    return args


def print_banner():
    """
    Print application banner.
    """
    print("=" * 60)
    print("    SMART SECURITY SYSTEM")
    print("    AI-Powered Intrusion Detection")
    print("    Version 1.0.0")
    print("=" * 60)
    print(f"System Name: {settings.system_name}")
    print(f"Flask Server: http://0.0.0.0:{settings.flask_port}")
    print(f"YOLO Model: {settings.yolo_model}")
    print(f"Telegram Bot: {'Enabled' if settings.telegram_bot_token else 'Disabled'}")
    print("=" * 60)
    print()


def main():
    """
    Main application entry point.
    """
    # Parse arguments
    args = parse_arguments()

    # Print banner
    print_banner()

    # Setup logger
    logger = setup_logger()
    logger.info("Starting Smart Security System...")

    # Create and initialize system
    system = None
    try:
        logger.info("Initializing system components...")
        system = SystemManager()

        if not system.initialize():
            logger.error("System initialization failed!")
            sys.exit(1)

        logger.info("✓ System initialized successfully!")

        # Auto-arm if flag set
        if args.arm:
            logger.info("Auto-arming system...")
            system.arm()

        # Main loop - keep application running
        logger.info("System ready. Press Ctrl+C to stop.")
        logger.info(f"Web dashboard: http://0.0.0.0:{settings.flask_port}")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\nKeyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        # Cleanup
        if system:
            logger.info("Shutting down system...")
            system.stop()
        logger.info("Goodbye!")


if __name__ == "__main__":
    main()