"""
LED Controller Module - Visual Indicators

This module controls LED indicators for system status.
- Green LED: System armed (ready to detect)
- Red LED: Alarm active (motion/intrusion detected)

Responsibilities:
- Initialize GPIO for LED control
- Provide high-level methods for status indication
- Support blinking patterns for different states
- Cleanup GPIO on shutdown

LED States:
- DISARMED: All LEDs off
- ARMED: Green LED solid on
- ALARM: Red LED solid on or blinking
- ERROR: Red LED blinking fast

Usage:
    from src.hardware.led_controller import LEDController

    leds = LEDController()
    leds.start()

    leds.set_armed()    # Green LED on
    leds.set_alarm()    # Red LED on
    leds.set_disarmed() # All LEDs off

    leds.stop()
"""

import RPi.GPIO as GPIO
import time
import threading
from typing import Optional
from enum import Enum

from config.gpio_pins import gpio_pins


class LEDState(Enum):
    """LED system states."""
    DISARMED = "disarmed"
    ARMED = "armed"
    ALARM = "alarm"
    ERROR = "error"


class LEDController:
    """
    LED indicator controller for system status visualization.

    Controls green (armed) and red (alarm) LEDs with support for
    solid and blinking patterns.
    """

    def __init__(
        self,
        green_pin: Optional[int] = None,
        red_pin: Optional[int] = None,
    ):
        """
        Initialize LED controller.

        Args:
            green_pin: GPIO pin for green LED (default from config)
            red_pin: GPIO pin for red LED (default from config)

        TODO:
        - Load pins from config if not provided
        - Initialize GPIO setup flags
        - Initialize current state
        - Initialize blinking thread components
        """
        self.green_pin = green_pin or gpio_pins.LED_GREEN_PIN
        self.red_pin = red_pin or gpio_pins.LED_RED_PIN

        self.current_state = LEDState.DISARMED
        self.started = False

        # Blinking control
        self.blink_thread = None
        self.blink_stop_event = threading.Event()

    def start(self) -> None:
        """
        Initialize GPIO for LED control.
        """
        try:
            # Setup GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            # Setup pins as OUTPUT
            GPIO.setup(self.green_pin, GPIO.OUT)
            GPIO.setup(self.red_pin, GPIO.OUT)

            # Set initial state to LOW (LEDs off)
            GPIO.output(self.green_pin, GPIO.LOW)
            GPIO.output(self.red_pin, GPIO.LOW)

            self.started = True
            print(f"✓ LED Controller initialized: Green={self.green_pin}, Red={self.red_pin}")
        except Exception as e:
            print(f"ERROR: Failed to initialize LED Controller: {e}")

    def set_disarmed(self) -> None:
        """
        Set system to DISARMED state (all LEDs off).
        """
        self._stop_blink()
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.red_pin, GPIO.LOW)
        self.current_state = LEDState.DISARMED

    def set_armed(self) -> None:
        """
        Set system to ARMED state (green LED on).
        """
        self._stop_blink()
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.red_pin, GPIO.LOW)
        self.current_state = LEDState.ARMED

    def set_alarm(self, blink: bool = False) -> None:
        """
        Set system to ALARM state (red LED on or blinking).

        Args:
            blink: If True, blink red LED; if False, solid on
        """
        self._stop_blink()
        GPIO.output(self.green_pin, GPIO.LOW)

        if blink:
            self._start_blink(self.red_pin, interval=0.5)
        else:
            GPIO.output(self.red_pin, GPIO.HIGH)

        self.current_state = LEDState.ALARM

    def set_error(self) -> None:
        """
        Set system to ERROR state (red LED fast blinking).
        """
        self._stop_blink()
        GPIO.output(self.green_pin, GPIO.LOW)
        self._start_blink(self.red_pin, interval=0.2)
        self.current_state = LEDState.ERROR

    def _start_blink(self, pin: int, interval: float = 0.5) -> None:
        """
        Start LED blinking in separate thread.

        Args:
            pin: GPIO pin to blink
            interval: Blink interval in seconds
        """
        self._stop_blink()
        self.blink_stop_event.clear()
        self.blink_thread = threading.Thread(
            target=self._blink_loop,
            args=(pin, interval),
            daemon=True
        )
        self.blink_thread.start()

    def _blink_loop(self, pin: int, interval: float) -> None:
        """
        Blinking loop (runs in separate thread).

        Args:
            pin: GPIO pin to blink
            interval: Blink interval in seconds
        """
        while not self.blink_stop_event.is_set():
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(interval)
            if self.blink_stop_event.is_set():
                break
            GPIO.output(pin, GPIO.LOW)
            time.sleep(interval)

    def _stop_blink(self) -> None:
        """
        Stop any active blinking pattern.
        """
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_stop_event.set()
            self.blink_thread.join(timeout=1.0)
            self.blink_thread = None

    def turn_on(self, color: str) -> None:
        """
        Turn on specific LED.

        Args:
            color: "green" or "red"
        """
        if color.lower() == "green":
            GPIO.output(self.green_pin, GPIO.HIGH)
        elif color.lower() == "red":
            GPIO.output(self.red_pin, GPIO.HIGH)
        else:
            raise ValueError(f"Invalid LED color: {color}")

    def turn_off(self, color: str) -> None:
        """
        Turn off specific LED.

        Args:
            color: "green" or "red"
        """
        if color.lower() == "green":
            GPIO.output(self.green_pin, GPIO.LOW)
        elif color.lower() == "red":
            GPIO.output(self.red_pin, GPIO.LOW)
        else:
            raise ValueError(f"Invalid LED color: {color}")

    def all_off(self) -> None:
        """
        Turn off all LEDs.
        """
        self._stop_blink()
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.red_pin, GPIO.LOW)

    def test_pattern(self) -> None:
        """
        Run test pattern to verify LEDs work.
        """
        print("Testing LED pattern...")

        # Blink green LED 3 times
        for _ in range(3):
            GPIO.output(self.green_pin, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(self.green_pin, GPIO.LOW)
            time.sleep(0.3)

        # Blink red LED 3 times
        for _ in range(3):
            GPIO.output(self.red_pin, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(self.red_pin, GPIO.LOW)
            time.sleep(0.3)

        # Blink both LEDs 3 times
        for _ in range(3):
            GPIO.output(self.green_pin, GPIO.HIGH)
            GPIO.output(self.red_pin, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(self.green_pin, GPIO.LOW)
            GPIO.output(self.red_pin, GPIO.LOW)
            time.sleep(0.3)

        print("✓ LED test pattern complete")

    def get_state(self) -> LEDState:
        """
        Get current LED state.

        Returns:
            LEDState: Current state enum
        """
        return self.current_state

    def stop(self) -> None:
        """
        Stop LED controller and cleanup GPIO.
        """
        if not self.started:
            return

        self._stop_blink()
        self.all_off()

        # Cleanup GPIO pins
        try:
            GPIO.cleanup([self.green_pin, self.red_pin])
        except:
            pass

        self.started = False
        print("✓ LED Controller stopped")

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
        return f"<LEDController: green={self.green_pin}, red={self.red_pin}, state={self.current_state.value}, {status}>"


# TODO: Add test code when running as main module
if __name__ == "__main__":
    """
    Test LED controller functionality.

    TODO:
    - Initialize LED controller
    - Test each state: disarmed, armed, alarm, error
    - Test blinking patterns
    - Test manual on/off
    - Run test pattern
    - Cleanup
    """
    print("LED Controller test - TODO: Implement test code")
    pass
