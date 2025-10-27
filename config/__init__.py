"""
Configuration Package

This package contains all configuration modules for the Smart Security System.
Includes settings management and GPIO pin mappings.
"""

from .settings import Settings
from .gpio_pins import GPIOPins

__all__ = ['Settings', 'GPIOPins']
