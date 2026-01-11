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
        """
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.LOW)
            self.started = True
            print(f"✓ Buzzer initialized: Pin={self.pin}")
        except Exception as e:
            print(f"ERROR: Failed to initialize Buzzer: {e}")

    def beep(self, duration: float = 0.1) -> None:
        """
        Single beep sound.

        Args:
            duration: Beep duration in seconds (default 0.1s)
        """
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.pin, GPIO.LOW)

    def beep_pattern(self, count: int = 3, duration: float = 0.1, pause: float = 0.1) -> None:
        """
        Multiple beeps in sequence.

        Args:
            count: Number of beeps
            duration: Duration of each beep in seconds
            pause: Pause between beeps in seconds
        """
        for i in range(count):
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.pin, GPIO.LOW)
            if i < count - 1:  # Don't pause after last beep
                time.sleep(pause)

    def on(self) -> None:
        """
        Turn buzzer on continuously.
        """
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self) -> None:
        """
        Turn buzzer off.
        """
        self.stop_alarm()
        GPIO.output(self.pin, GPIO.LOW)

    def alarm(self, duration: Optional[float] = None) -> None:
        """
        Sound continuous alarm.

        Args:
            duration: Alarm duration in seconds (None = continuous until stop)
        """
        GPIO.output(self.pin, GPIO.HIGH)
        if duration is not None:
            time.sleep(duration)
            GPIO.output(self.pin, GPIO.LOW)

    def pulse_alarm(self, on_time: float = 0.5, off_time: float = 0.5) -> None:
        """
        Start pulsing alarm pattern in background thread.

        Args:
            on_time: Time buzzer is on in each cycle (seconds)
            off_time: Time buzzer is off in each cycle (seconds)
        """
        self.stop_alarm()
        self.alarm_stop_event.clear()
        self.alarm_thread = threading.Thread(
            target=self._pulse_loop,
            args=(on_time, off_time),
            daemon=True
        )
        self.alarm_thread.start()

    def _pulse_loop(self, on_time: float, off_time: float) -> None:
        """
        Pulsing loop (runs in separate thread).

        Args:
            on_time: Duration buzzer is on
            off_time: Duration buzzer is off
        """
        while not self.alarm_stop_event.is_set():
            GPIO.output(self.pin, GPIO.HIGH)
            if self.alarm_stop_event.wait(timeout=on_time):
                break
            GPIO.output(self.pin, GPIO.LOW)
            if self.alarm_stop_event.wait(timeout=off_time):
                break

    def stop_alarm(self) -> None:
        """
        Stop any active alarm pattern.
        """
        if self.alarm_thread and self.alarm_thread.is_alive():
            self.alarm_stop_event.set()
            self.alarm_thread.join(timeout=1.0)
            self.alarm_thread = None
        GPIO.output(self.pin, GPIO.LOW)

    def test(self) -> None:
        """
        Run test sequence to verify buzzer works.
        """
        print("Testing buzzer...")

        # Single beep
        print("  - Single beep")
        self.beep(0.1)
        time.sleep(0.5)

        # Three beeps pattern
        print("  - Three beeps pattern")
        self.beep_pattern(3, 0.1, 0.2)
        time.sleep(0.5)

        # Short continuous alarm
        print("  - Continuous alarm (1 second)")
        self.alarm(duration=1.0)
        time.sleep(0.5)

        # Pulse alarm
        print("  - Pulse alarm (3 seconds)")
        self.pulse_alarm(0.3, 0.3)
        time.sleep(3.0)
        self.stop_alarm()

        print("✓ Buzzer test complete")

    def is_sounding(self) -> bool:
        """
        Check if buzzer is currently on.

        Returns:
            bool: True if buzzer is sounding, False otherwise
        """
        try:
            return GPIO.input(self.pin) == GPIO.HIGH
        except:
            return False

    def stop(self) -> None:
        """
        Stop buzzer and cleanup GPIO.
        """
        if not self.started:
            return

        self.stop_alarm()
        GPIO.output(self.pin, GPIO.LOW)

        try:
            GPIO.cleanup(self.pin)
        except:
            pass

        self.started = False
        print("✓ Buzzer stopped")

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
