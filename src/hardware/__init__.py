"""
Hardware Package

This package contains all hardware interface modules:
- Camera: USB webcam interface and frame capture
- PIRSensor: Motion detection sensor interface
- LEDController: LED indicator management
- Buzzer: Buzzer alarm control
"""

from .camera import Camera
from .pir_sensor import PIRSensor
from .led_controller import LEDController
from .buzzer import Buzzer

__all__ = ['Camera', 'PIRSensor', 'LEDController', 'Buzzer']
