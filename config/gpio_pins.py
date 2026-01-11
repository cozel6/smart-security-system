"""
GPIO Pin Configuration

This module defines all GPIO pin mappings for Raspberry Pi.
Uses BCM (Broadcom) pin numbering scheme.

Pin Reference (Raspberry Pi 4):
- Physical pins: 1-40 (physical board layout)
- BCM pins: GPIO numbers used in code

Usage:
    from config.gpio_pins import GPIOPins
    pins = GPIOPins()
    pir_pin = pins.PIR_PIN
"""

import os
from typing import Dict, List


class GPIOPins:
    """
    GPIO pin configuration for all hardware components.

    Uses BCM pin numbering (GPIO numbers, not physical pin numbers).
    All pin numbers can be overridden via environment variables if needed.
    """

    def __init__(self):
        """
        Initialize GPIO pin configuration.

        TODO:
        - Load pin numbers from environment variables (with defaults)
        - Validate pin numbers are in valid range (0-27 for RPi 4)
        - Check for pin conflicts (same pin used twice)
        """
        self._load_pin_configuration()
        self._validate_pins()

    def _load_pin_configuration(self) -> None:
        """
        Load GPIO pin numbers from environment or use defaults.

        Default Pin Mapping:
        - PIR Sensor: GPIO 18 (Physical pin 12)
        - LED Red (Alarm): GPIO 17 (Physical pin 11)
        - LED Green (Armed): GPIO 27 (Physical pin 13)
        - Buzzer: GPIO 22 (Physical pin 15)

        TODO:
        - Load pin numbers from .env if provided
        - Use default values if not specified
        - Store in instance variables
        """
        # PIR Motion Sensor (GPIO 24, Physical Pin 18)
        self.PIR_PIN: int = int(os.getenv("PIR_PIN", "24"))

        # LED Indicators
        self.LED_RED_PIN: int = int(os.getenv("LED_RED_PIN", "17"))  # Physical Pin 11
        self.LED_GREEN_PIN: int = int(os.getenv("LED_GREEN_PIN", "27"))  # Physical Pin 13

        # Buzzer (GPIO 23, Physical Pin 16)
        self.BUZZER_PIN: int = int(os.getenv("BUZZER_PIN", "23"))

    def _validate_pins(self) -> None:
        """
        Validate GPIO pin configuration.

        TODO:
        - Check all pins are in valid range (0-27 for RPi 4)
        - Check for duplicate pin assignments
        - Raise ValueError with clear message if invalid
        - Warn about reserved pins if used (I2C, SPI, UART pins)
        """
        # Get all configured pins
        all_pins = self.get_all_pins()

        # TODO: Validate range (0-27 for Raspberry Pi 4)
        # for pin_name, pin_number in all_pins.items():
        #     if not (0 <= pin_number <= 27):
        #         raise ValueError(f"Invalid pin number for {pin_name}: {pin_number}")

        # TODO: Check for duplicates
        # pin_numbers = list(all_pins.values())
        # if len(pin_numbers) != len(set(pin_numbers)):
        #     raise ValueError("Duplicate pin assignments detected!")

        # TODO: Warn about reserved pins
        # Reserved pins on Raspberry Pi 4:
        # - GPIO 2, 3: I2C (avoid unless using I2C devices)
        # - GPIO 14, 15: UART (avoid unless using serial)
        # - GPIO 7, 8, 9, 10, 11: SPI (avoid unless using SPI devices)

        pass

    def get_all_pins(self) -> Dict[str, int]:
        """
        Get dictionary of all configured pins.

        Returns:
            Dict[str, int]: Dictionary mapping pin names to GPIO numbers

        TODO:
        - Return dictionary with all pin mappings
        - Useful for validation and debugging
        """
        return {
            "PIR_PIN": self.PIR_PIN,
            "LED_RED_PIN": self.LED_RED_PIN,
            "LED_GREEN_PIN": self.LED_GREEN_PIN,
            "BUZZER_PIN": self.BUZZER_PIN,
        }

    def get_output_pins(self) -> List[int]:
        """
        Get list of all OUTPUT pins (LEDs, Buzzer).

        Returns:
            List[int]: List of GPIO pin numbers configured as outputs

        TODO:
        - Return list of pins that should be configured as GPIO.OUT
        """
        return [self.LED_RED_PIN, self.LED_GREEN_PIN, self.BUZZER_PIN]

    def get_input_pins(self) -> List[int]:
        """
        Get list of all INPUT pins (PIR Sensor).

        Returns:
            List[int]: List of GPIO pin numbers configured as inputs

        TODO:
        - Return list of pins that should be configured as GPIO.IN
        """
        return [self.PIR_PIN]

    def print_configuration(self) -> None:
        """
        Print human-readable pin configuration.

        TODO:
        - Print formatted table of all pin assignments
        - Include both GPIO number and physical pin number
        - Useful for debugging and documentation
        """
        print("=" * 50)
        print("GPIO Pin Configuration (BCM Numbering)")
        print("=" * 50)

        # TODO: Implement formatted output
        # Example:
        # Component         | GPIO Pin | Physical Pin
        # -----------------|----------|-------------
        # PIR Sensor       |    18    |     12
        # LED Red (Alarm)  |    17    |     11
        # LED Green (Armed)|    27    |     13
        # Buzzer           |    22    |     15

        pass

    def __repr__(self) -> str:
        """String representation of GPIO configuration."""
        return f"<GPIOPins: {len(self.get_all_pins())} pins configured>"


# GPIO Pin to Physical Pin Mapping Reference (Raspberry Pi 4)
# Useful for wiring and documentation
GPIO_TO_PHYSICAL = {
    2: 3,   3: 5,   4: 7,   17: 11,  27: 13,  22: 15,  10: 19,  9: 21,
    11: 23, 5: 29,  6: 31,  13: 33,  19: 35,  26: 37,  14: 8,   15: 10,
    18: 12, 23: 16, 24: 18, 25: 22,  8: 24,   7: 26,   12: 32,  16: 36,
    20: 38, 21: 40,
}

# Create a singleton instance for easy import
gpio_pins = GPIOPins()
