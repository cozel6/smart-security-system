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

        TODO:
        - Setup GPIO mode (GPIO.BCM)
        - Setup both pins as OUTPUT: GPIO.setup(pin, GPIO.OUT)
        - Set initial state to LOW (LEDs off)
        - Set started flag to True
        - Log initialization
        """
        # TODO: Implement GPIO setup
        pass

    def set_disarmed(self) -> None:
        """
        Set system to DISARMED state (all LEDs off).

        TODO:
        - Stop any blinking patterns
        - Turn off both LEDs (GPIO.output LOW)
        - Update current_state
        """
        # TODO: Implement disarmed state
        pass

    def set_armed(self) -> None:
        """
        Set system to ARMED state (green LED on).

        TODO:
        - Stop any blinking patterns
        - Turn on green LED (GPIO.output HIGH)
        - Turn off red LED (GPIO.output LOW)
        - Update current_state
        """
        # TODO: Implement armed state
        pass

    def set_alarm(self, blink: bool = False) -> None:
        """
        Set system to ALARM state (red LED on or blinking).

        Args:
            blink: If True, blink red LED; if False, solid on

        TODO:
        - Stop any previous blinking patterns
        - Turn off green LED
        - If blink=True:
            - Start blinking thread for red LED (0.5s on, 0.5s off)
        - If blink=False:
            - Turn on red LED solid
        - Update current_state
        """
        # TODO: Implement alarm state
        pass

    def set_error(self) -> None:
        """
        Set system to ERROR state (red LED fast blinking).

        TODO:
        - Stop any previous blinking patterns
        - Turn off green LED
        - Start fast blinking thread for red LED (0.2s on, 0.2s off)
        - Update current_state
        """
        # TODO: Implement error state
        pass

    def _start_blink(self, pin: int, interval: float = 0.5) -> None:
        """
        Start LED blinking in separate thread.

        Args:
            pin: GPIO pin to blink
            interval: Blink interval in seconds

        TODO:
        - Stop any existing blink thread
        - Clear stop event
        - Create new thread that toggles LED state
        - Thread should check stop_event regularly
        - Start thread with daemon=True
        """
        # TODO: Implement blinking thread
        pass

    def _blink_loop(self, pin: int, interval: float) -> None:
        """
        Blinking loop (runs in separate thread).

        Args:
            pin: GPIO pin to blink
            interval: Blink interval in seconds

        TODO:
        - Loop while not stop_event.is_set()
        - Toggle LED state (HIGH -> LOW -> HIGH)
        - Sleep for interval
        - Exit when stop_event is set
        """
        # TODO: Implement blink loop
        pass

    def _stop_blink(self) -> None:
        """
        Stop any active blinking pattern.

        TODO:
        - Set stop_event to signal thread to stop
        - Wait for thread to finish (join with timeout)
        - Set blink_thread to None
        """
        # TODO: Implement blink stop
        pass

    def turn_on(self, color: str) -> None:
        """
        Turn on specific LED.

        Args:
            color: "green" or "red"

        TODO:
        - Get appropriate pin based on color
        - Set GPIO to HIGH
        - Raise ValueError if invalid color
        """
        # TODO: Implement direct LED control
        pass

    def turn_off(self, color: str) -> None:
        """
        Turn off specific LED.

        Args:
            color: "green" or "red"

        TODO:
        - Get appropriate pin based on color
        - Set GPIO to LOW
        - Raise ValueError if invalid color
        """
        # TODO: Implement direct LED control
        pass

    def all_off(self) -> None:
        """
        Turn off all LEDs.

        TODO:
        - Stop blinking
        - Turn off green LED
        - Turn off red LED
        """
        # TODO: Implement all off
        pass

    def test_pattern(self) -> None:
        """
        Run test pattern to verify LEDs work.

        TODO:
        - Blink green LED 3 times
        - Blink red LED 3 times
        - Blink both LEDs 3 times
        - Turn all off
        - Useful for hardware testing
        """
        # TODO: Implement test pattern
        pass

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

        TODO:
        - Stop any blinking threads
        - Turn off all LEDs
        - Cleanup GPIO pins
        - Set started flag to False
        """
        # TODO: Implement cleanup
        pass

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
