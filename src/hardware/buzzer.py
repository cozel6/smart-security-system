"""
Buzzer Module - Audio Alarm

This module controls an active buzzer for audio alarm.
Provides sound feedback for system events.

Responsibilities:
- Initialize GPIO for buzzer control
- Sound alarm with different patterns
- Support continuous and pulsed tones
- Cleanup GPIO on shutdown

Buzzer Types:
- Active Buzzer: Has internal oscillator, just needs DC voltage (simpler)
- Passive Buzzer: Requires PWM signal to generate tone (more control)

This module assumes ACTIVE buzzer (simpler, recommended for this project).

Usage:
    from src.hardware.buzzer import Buzzer

    buzzer = Buzzer()
    buzzer.start()

    buzzer.beep()           # Single short beep
    buzzer.alarm()          # Continuous alarm
    buzzer.pulse_alarm()    # Pulsing alarm pattern

    buzzer.stop()
"""

import RPi.GPIO as GPIO
import time
import threading
from typing import Optional

from config.gpio_pins import gpio_pins


class Buzzer:
    """
    Active buzzer controller for audio alarm.

    Supports single beeps, continuous alarm, and pulsing patterns.
    """

    def __init__(self, pin: Optional[int] = None):
        """
        Initialize buzzer controller.

        Args:
            pin: GPIO pin for buzzer (default from config)

        TODO:
        - Load pin from config if not provided
        - Initialize GPIO setup flag
        - Initialize alarm thread components
        """
        self.pin = pin or gpio_pins.BUZZER_PIN
        self.started = False

        # Alarm control
        self.alarm_thread = None
        self.alarm_stop_event = threading.Event()

    def start(self) -> None:
        """
        Initialize GPIO for buzzer control.

        TODO:
        - Setup GPIO mode (GPIO.BCM)
        - Setup pin as OUTPUT: GPIO.setup(self.pin, GPIO.OUT)
        - Set initial state to LOW (buzzer off)
        - Set started flag to True
        - Log initialization
        """
        # TODO: Implement GPIO setup
        pass

    def beep(self, duration: float = 0.1) -> None:
        """
        Single beep sound.

        Args:
            duration: Beep duration in seconds (default 0.1s)

        TODO:
        - Turn buzzer on (GPIO HIGH)
        - Sleep for duration
        - Turn buzzer off (GPIO LOW)
        - Useful for feedback on button press, etc.
        """
        # TODO: Implement single beep
        pass

    def beep_pattern(self, count: int = 3, duration: float = 0.1, pause: float = 0.1) -> None:
        """
        Multiple beeps in sequence.

        Args:
            count: Number of beeps
            duration: Duration of each beep in seconds
            pause: Pause between beeps in seconds

        TODO:
        - Loop count times
        - For each iteration:
            - Turn on buzzer
            - Sleep for duration
            - Turn off buzzer
            - Sleep for pause (except after last beep)
        - Useful for different alert levels (1 beep = info, 3 beeps = warning, etc.)
        """
        # TODO: Implement beep pattern
        pass

    def on(self) -> None:
        """
        Turn buzzer on continuously.

        TODO:
        - Set GPIO to HIGH
        - Buzzer will sound until turned off
        """
        # TODO: Implement on
        pass

    def off(self) -> None:
        """
        Turn buzzer off.

        TODO:
        - Set GPIO to LOW
        - Stop any alarm patterns
        """
        # TODO: Implement off
        pass

    def alarm(self, duration: Optional[float] = None) -> None:
        """
        Sound continuous alarm.

        Args:
            duration: Alarm duration in seconds (None = continuous until stop)

        TODO:
        - Turn buzzer on
        - If duration specified:
            - Sleep for duration
            - Turn buzzer off
        - If duration is None:
            - Leave buzzer on (must call stop_alarm() to turn off)
        """
        # TODO: Implement continuous alarm
        pass

    def pulse_alarm(self, on_time: float = 0.5, off_time: float = 0.5) -> None:
        """
        Start pulsing alarm pattern in background thread.

        Args:
            on_time: Time buzzer is on in each cycle (seconds)
            off_time: Time buzzer is off in each cycle (seconds)

        TODO:
        - Stop any existing alarm
        - Clear stop event
        - Create thread that pulses buzzer (on -> off -> on -> ...)
        - Start thread with daemon=True
        - Thread should check stop_event regularly
        """
        # TODO: Implement pulsing alarm
        pass

    def _pulse_loop(self, on_time: float, off_time: float) -> None:
        """
        Pulsing loop (runs in separate thread).

        Args:
            on_time: Duration buzzer is on
            off_time: Duration buzzer is off

        TODO:
        - Loop while not alarm_stop_event.is_set()
        - Turn buzzer on
        - Sleep for on_time (or until stop event)
        - Turn buzzer off
        - Sleep for off_time (or until stop event)
        - Exit when stop event is set
        """
        # TODO: Implement pulse loop
        pass

    def stop_alarm(self) -> None:
        """
        Stop any active alarm pattern.

        TODO:
        - Set stop event to signal thread to stop
        - Wait for thread to finish (join with timeout)
        - Turn buzzer off
        - Set alarm_thread to None
        """
        # TODO: Implement alarm stop
        pass

    def test(self) -> None:
        """
        Run test sequence to verify buzzer works.

        TODO:
        - Single beep
        - Three beeps pattern
        - Short continuous alarm (1 second)
        - Pulse alarm (3 pulses)
        - Turn off
        - Useful for hardware testing
        """
        # TODO: Implement test sequence
        pass

    def is_sounding(self) -> bool:
        """
        Check if buzzer is currently on.

        Returns:
            bool: True if buzzer is sounding, False otherwise

        TODO:
        - Read GPIO state
        - Return True if HIGH, False if LOW
        """
        # TODO: Implement status check
        pass

    def stop(self) -> None:
        """
        Stop buzzer and cleanup GPIO.

        TODO:
        - Stop any alarm patterns
        - Turn off buzzer
        - Cleanup GPIO pin
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
        sound = "SOUNDING" if self.is_sounding() else "SILENT"
        return f"<Buzzer: pin={self.pin}, {status}, {sound}>"


# TODO: Add test code when running as main module
if __name__ == "__main__":
    """
    Test buzzer functionality.

    TODO:
    - Initialize buzzer
    - Test single beep
    - Test beep patterns (1, 3, 5 beeps)
    - Test continuous alarm (2 seconds)
    - Test pulse alarm (5 seconds)
    - Run full test sequence
    - Cleanup
    """
    print("Buzzer test - TODO: Implement test code")
    pass
