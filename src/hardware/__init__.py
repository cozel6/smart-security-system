"""
Hardware Package

This package contains all hardware interface modules:
- Camera: USB webcam interface and frame capture
- PIRSensor: Motion detection sensor interface (Raspberry Pi only)
- LEDController: LED indicator management (Raspberry Pi only)
- Buzzer: Buzzer alarm control (Raspberry Pi only)
"""

# Always import Camera (works on any platform with USB webcam)
from .camera import Camera

# Try to import Raspberry Pi specific hardware (optional)
try:
    from .pir_sensor import PIRSensor
    from .led_controller import LEDController
    from .buzzer import Buzzer
    RPI_HARDWARE_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    # Running on non-Raspberry Pi platform
    PIRSensor = None
    LEDController = None
    Buzzer = None
    RPI_HARDWARE_AVAILABLE = False

__all__ = ['Camera', 'PIRSensor', 'LEDController', 'Buzzer', 'RPI_HARDWARE_AVAILABLE']
