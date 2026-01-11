"""
PIR Sensor Module - Motion Detection Hardware Interface

This module interfaces with HC-SR501 PIR (Passive Infrared) motion sensor.
Detects motion through infrared radiation changes.

Responsibilities:
- Initialize GPIO for PIR sensor
- Detect motion via GPIO interrupt or polling
- Provide callback mechanism for motion events
- Cleanup GPIO on shutdown

PIR Sensor Specifications (HC-SR501):
- Operating Voltage: 5V-20V (5V recommended)
- Detection Range: Up to 7 meters
- Detection Angle: ~110 degrees
- Output: HIGH (3.3V) when motion detected, LOW (0V) otherwise
- Delay Time: Adjustable 0.3s to 5 minutes (via potentiometer)

Usage:
    from src.hardware.pir_sensor import PIRSensor

    def on_motion(channel):
        print("Motion detected!")

    pir = PIRSensor()
    pir.start(callback=on_motion)

    # ... system runs ...

    pir.stop()
"""

import RPi.GPIO as GPIO
import time
import threading
from typing import Optional, Callable
from datetime import datetime

from config.gpio_pins import gpio_pins


class PIRSensor:
    """
    PIR Motion Sensor interface using GPIO interrupt.

    Detects motion and triggers callback function when motion is detected.
    Uses GPIO event detection for efficient, interrupt-driven operation.
    """

    def __init__(self, pin: Optional[int] = None):
        """
        Initialize PIR sensor interface.

        Args:
            pin: GPIO pin number (BCM) for PIR sensor (default from config)

        TODO:
        - Load pin from config if not provided
        - Initialize GPIO mode (BCM)
        - Setup pin as INPUT
        - Initialize motion state tracking
        - Initialize callback storage
        """
        self.pin = pin or gpio_pins.PIR_PIN
        self.motion_detected = False
        self.last_motion_time = None
        self.callback = None
        self.started = False

    def start(self, callback: Optional[Callable[[int], None]] = None) -> None:
        """
        Start PIR sensor monitoring with optional callback.

        Args:
            callback: Function to call when motion detected (receives GPIO pin number)
        """
        self.callback = callback

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.pin, GPIO.IN)

            # Add event detection for motion (RISING edge = motion starts)
            GPIO.add_event_detect(
                self.pin,
                GPIO.RISING,
                callback=self._motion_callback,
                bouncetime=200
            )

            self.started = True
            print(f"✓ PIR Sensor initialized: Pin={self.pin}")
            print("  Waiting for sensor to stabilize (2 seconds)...")
            time.sleep(2)
            print("  ✓ PIR Sensor ready")

        except Exception as e:
            print(f"ERROR: Failed to initialize PIR Sensor: {e}")

    def _motion_callback(self, channel: int) -> None:
        """
        Internal callback when motion is detected (called by GPIO interrupt).

        Args:
            channel: GPIO pin number that triggered the interrupt
        """
        try:
            self.motion_detected = True
            self.last_motion_time = datetime.now()
            print(f"🔴 MOTION DETECTED! (Pin {channel})")

            # Call user callback if provided
            if self.callback:
                try:
                    self.callback(channel)
                except Exception as e:
                    print(f"ERROR in PIR callback: {e}")
        except Exception as e:
            print(f"ERROR in _motion_callback: {e}")

    def is_motion_detected(self) -> bool:
        """
        Check if motion is currently detected (polling method).

        Returns:
            bool: True if motion detected, False otherwise
        """
        try:
            return GPIO.input(self.pin) == GPIO.HIGH
        except:
            return False

    def wait_for_motion(self, timeout: Optional[float] = None) -> bool:
        """
        Block until motion is detected or timeout.

        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)

        Returns:
            bool: True if motion detected, False if timeout
        """
        try:
            # Convert timeout to milliseconds (None stays None)
            timeout_ms = int(timeout * 1000) if timeout else None
            channel = GPIO.wait_for_edge(self.pin, GPIO.RISING, timeout=timeout_ms)
            return channel is not None
        except:
            return False

    def get_last_motion_time(self) -> Optional[datetime]:
        """
        Get timestamp of last motion detection.

        Returns:
            Optional[datetime]: Timestamp of last motion, or None if no motion yet

        TODO:
        - Return self.last_motion_time
        - Useful for calculating time since last motion
        """
        return self.last_motion_time

    def time_since_last_motion(self) -> Optional[float]:
        """
        Calculate time elapsed since last motion detection.

        Returns:
            Optional[float]: Seconds since last motion, or None if no motion yet
        """
        if self.last_motion_time is None:
            return None
        elapsed = (datetime.now() - self.last_motion_time).total_seconds()
        return elapsed

    def stop(self) -> None:
        """
        Stop PIR sensor and cleanup GPIO.
        """
        if not self.started:
            return

        try:
            GPIO.remove_event_detect(self.pin)
            GPIO.cleanup(self.pin)
        except Exception as e:
            print(f"Warning during PIR cleanup: {e}")

        self.started = False
        print("✓ PIR Sensor stopped")

    def reset(self) -> None:
        """
        Reset motion detection state.

        TODO:
        - Set motion_detected to False
        - Clear last_motion_time
        - Useful after acknowledging an alert
        """
        self.motion_detected = False
        self.last_motion_time = None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def __repr__(self) -> str:
        """String representation."""
        status = "active" if self.started else "stopped"
        motion = "MOTION" if self.motion_detected else "IDLE"
        return f"<PIRSensor: pin={self.pin}, {status}, {motion}>"


# TODO: Add test code when running as main module
if __name__ == "__main__":
    """
    Test PIR sensor functionality.

    TODO:
    - Initialize PIR sensor
    - Define callback that prints "Motion detected!"
    - Start sensor with callback
    - Wait for motion detection (or timeout after 30 seconds)
    - Print statistics
    - Cleanup
    """
    print("PIR Sensor test - TODO: Implement test code")
    pass
