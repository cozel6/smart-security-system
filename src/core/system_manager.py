"""
System Manager Module - Main Orchestrator

This is the central orchestrator that coordinates all system components.
Manages initialization, threading, state, and communication between modules.

Components Managed:
- Hardware: Camera, PIR sensor, LEDs, Buzzer
- Detection: Motion detector, YOLO detector
- Alerts: Telegram bot, Alert manager
- Streaming: Flask server, Video streamer

Threading Architecture:
- Camera Thread: Continuous frame capture
- Detection Thread: Motion + YOLO processing
- Alert Thread: Alert queue processing
- Telegram Thread: Bot polling
- Flask Thread: Web server

System States:
- DISARMED: System inactive, no detection
- ARMED: System active, monitoring for intrusions
- ALARM: Intrusion detected, alerts sent

Usage:
    from src.core.system_manager import SystemManager

    system = SystemManager()
    system.initialize()
    system.arm()

    # System runs until stopped
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        system.stop()
"""

from pathlib import Path
import threading
import time
from enum import Enum
from typing import Optional
from datetime import datetime
import signal
import sys
import psutil
import numpy as np
import cv2

#from src.hardware import Camera, PIRSensor, LEDController, Buzzer
#from src.detection import MotionDetector, YOLODetector, DetectionType, AlertLevel
#from src.alerts import TelegramBot, AlertManager
from src.streaming import FlaskServer, VideoStreamer
from src.utils.logger import setup_logger, get_logger
from src.utils import helpers
from config.settings import settings


class SystemState(Enum):
    """System operational states."""
    DISARMED = "disarmed"
    ARMED = "armed"
    ALARM = "alarm"
    ERROR = "error"


class SystemManager:
    """
    Main system orchestrator.

    Coordinates all components and manages system lifecycle.
    """

    def __init__(self):
        """
        Initialize system manager.

        TODO:
        - Setup logger
        - Initialize all components (set to None initially)
        - Initialize state
        - Initialize threading components
        - Initialize statistics
        - Register signal handlers (SIGINT, SIGTERM)
        """
        # Logger
        self.logger = None  # TODO: Setup logger

        # System state
        self.state = SystemState.DISARMED
        self.start_time = datetime.now()

        # Hardware components
        self.camera = None
        self.pir_sensor = None
        self.led_controller = None
        self.buzzer = None

        # Detection components
        self.motion_detector = None
        self.yolo_detector = None

        # Alert components
        self.telegram_bot = None
        self.alert_manager = None

        # Streaming components
        self.flask_server = None
        self.video_streamer = None

        # Threading
        self.detection_thread = None
        self.stop_event = threading.Event()

        # Statistics
        self.total_detections = 0
        self.person_detections = 0
        self.animal_detections = 0

    def initialize(self) -> bool:
        """
        Initialize all system components.

        Returns:
            bool: True if initialization successful
        
        """
        try:
            # 1. Setup logger
            self.logger = get_logger("_name_")
            self.logger.info("=" * 60)
            self.logger.info("Initializing Smart Security System...")
            self.logger.info("=" * 60)

            # 2. For minimal version, we skip hardware initialization
            self.logger.info("Running in minimal mode - skipping hardware initialization.")

            # 3. Initialize Flask server with callbacks
            self.logger.info("Initializing Flask server...")
            self.flask_server = FlaskServer()
            

            # 4. Start Flask server
            self.logger.info("Registering Flask callbacks...")
            self.flask_server.register_callbacks(
                get_frame=self.get_current_frame,
                get_status=self.get_status,
                arm=self.arm,
                disarm=self.disarm,
            )
            self.flask_server.start()
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Initialization failed: {e}", exc_info=True)
            else:
                print(f"ERROR: Initialization failed: {e}")
            return False
    



    def arm(self) -> bool:
        """
        Arm the security system.

        Returns:
            bool: True if armed successfully
        """
        try:
            self.logger.info("Arming system...")
            
            # 1. Check if already armed
            if self.state == SystemState.ARMED:
                self.logger.warning("System is already armed")
                return True
            
            # 2. Set state to ARMED
            self.state = SystemState.ARMED
            
            # 3. Turn on green LED (armed indicator) - if available
            if self.led_controller:
                self.led_controller.set_armed()
            
            # 4. Start PIR sensor monitoring - Pentru Raspberry Pi
            if self.pir_sensor:
                self.pir_sensor.start()
            
            # 5. In future, we'll start detection thread here
            # TODO: Uncomment when camera + detection are ready
            # self.stop_event.clear()
            # self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            # self.detection_thread.start()
            
            self.logger.info("System armed successfully (camera detection disabled in minimal mode)")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to arm system: {e}", exc_info=True)
            return False

    def disarm(self) -> bool:
        """
        Disarm the security system.

        Returns:
            bool: True if disarmed successfully
        """

        try:
            self.logger.info("Disarming system...")
            
            # 1. Stop detection thread if running
            if self.detection_thread and self.detection_thread.is_alive():
                self.stop_event.set()
                self.detection_thread.join(timeout=5)
                self.detection_thread = None
                self.stop_event.clear()
            
            # 2. Set state to DISARMED
            self.state = SystemState.DISARMED
            
            # 3. Turn off LEDs (if available)
            if self.led_controller:
                self.led_controller.turn_off_all()
            
            # 4. Stop buzzer (if available)
            if self.buzzer:
                self.buzzer.stop()
            
            # 5. Stop PIR sensor (if available) - Pentru Raspberry Pi
            if self.pir_sensor:
                self.pir_sensor.stop()
            
            self.logger.info("System disarmed successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to disarm system: {e}", exc_info=True)
            return False
            
            

    def _detection_loop(self) -> None:
        """
        Main detection loop (runs in separate thread).

        This is the core monitoring loop that processes frames and detects intrusions.

        TODO:
        1. Loop while not stop_event.is_set() and state == ARMED
        2. Get frame from camera
        3. If no frame, sleep and continue
        4. Check PIR sensor state
        5. If PIR triggered or previous motion:
            a. Run motion detection (OpenCV)
            b. If motion detected:
                - Run YOLO detection
                - Classify result (person/animal/both)
                - Determine alert level
                - If person detected:
                    - Set state to ALARM
                    - Trigger red LED and buzzer
                    - Queue alert with high priority
                - If only animal:
                    - Queue alert with low priority
                - Draw detection boxes on frame
        6. Update video streamer with processed frame
        7. Sleep briefly to control loop rate
        8. Handle exceptions
        """
        # TODO: Implement detection loop
        pass

    def _handle_pir_trigger(self, channel: int) -> None:
        """
        Handle PIR sensor trigger (callback).

        Args:
            channel: GPIO pin that triggered

        TODO:
        - Log PIR trigger
        - If system is ARMED:
            - Set flag to start motion detection
            - Optional: Brief buzzer beep as feedback
        """
        # TODO: Implement PIR callback
        pass

    def _process_detection(
        self,
        frame,
        detection_result: dict
    ) -> None:
        """
        Process YOLO detection result and trigger alerts.

        Args:
            frame: Detected frame
            detection_result: YOLO detection dictionary

        TODO:
        - Extract detection type and alert level
        - If person detected:
            - Activate alarm (red LED, buzzer)
            - Queue CRITICAL alert
            - Save snapshot
            - Increment statistics
        - If animal only:
            - Queue LOW alert
            - Save snapshot
        - Log detection
        """
        # TODO: Implement detection processing
        pass

    def get_status(self) -> dict:
        """
        Get current system status.
        """
        from src.utils.helpers import get_cpu_usage, get_memory_usage, format_uptime
        import time 

        # Calculate uptime
        uptime_seconds = time.time() - self._start_time if hasattr(self, '_start_time') else 0

        # Get system info
        status = {
            "armed": getattr(self, '_is_armed', False),
            "uptime": format_uptime(uptime_seconds),
            "cpu_usage": f"{get_cpu_usage():.1f}%",
            "memory_usage": f"{get_memory_usage():.1f}%",
            "camera_fps": 0,  # TODO: Calculate actual FPS when camera is implemented
            "last_detection": None,  # TODO: Track last detection when detection is implemented
        }
        return status

    def get_current_frame(self):
        """
        Get current camera frame (for snapshots/streaming).

        TODO:
        - Get frame from camera
        - Return frame
        - Handle camera not initialized
        """
        # TODO: Implement frame retrieval
        if self.camera:
            frame = self.camera.get_frame()
            return frame
        #Fallback : now retrun dummy data , for prod we should raise exception or handle it properly
        return self._generate_dummy_frame()

    def _generate_dummy_frame(self) -> np.ndarray:
        """
        Generate colored test frame with system info (for testing without camera).
        
        Returns:
            np.ndarray: 640x480 BGR frame with text overlay
        """
        # Create blank frame (480 height x 640 width x 3 color channels)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Fill with orange color (BGR format: Blue, Green, Red)
        frame[:] = (60, 120, 180)  
        
        # Add text overlays
        font = cv2.FONT_HERSHEY_SIMPLEX
        white = (255, 255, 255)
        
        # Title
        cv2.putText(frame, "TEST MODE - NO CAMERA", (140, 180), 
                    font, 0.9, white, 2, cv2.LINE_AA)
        
        # Current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (200, 240), 
                    font, 0.7, white, 2, cv2.LINE_AA)
        
        # System state
        state_text = f"State: {self.state.value.upper()}"
        state_color = (0, 255, 0) if self.state == SystemState.ARMED else (100, 100, 100)
        cv2.putText(frame, state_text, (230, 300), 
                    font, 0.8, state_color, 2, cv2.LINE_AA)
        
        return frame


    def trigger_alarm(self) -> None:
        """
        Trigger alarm (LEDs, buzzer, state change).

        TODO:
        - Set state to ALARM
        - Turn on red LED (blinking)
        - Activate buzzer (pulsing)
        - Log alarm trigger
        """
        # TODO: Implement alarm trigger
        pass

    def clear_alarm(self) -> None:
        """
        Clear alarm state (return to armed).

        TODO:
        - Set state back to ARMED
        - Stop red LED blinking (back to green)
        - Stop buzzer
        - Log alarm clear
        """
        # TODO: Implement alarm clear
        pass

    def stop(self) -> None:
        """
        Stop system and cleanup all components.

        TODO:
        1. Log shutdown
        2. Set stop event
        3. Wait for detection thread to finish
        4. Stop all components:
            - Camera
            - PIR sensor
            - LED controller (turn off all)
            - Buzzer (turn off)
            - YOLO detector
            - Telegram bot
            - Alert manager
            - Flask server
        5. Cleanup GPIO
        6. Log final statistics
        7. Log shutdown complete
        """
        # TODO: Implement system shutdown
        pass

    def _signal_handler(self, signum, frame):
        """
        Handle system signals (SIGINT, SIGTERM).

        TODO:
        - Log signal received
        - Call stop()
        - Exit gracefully
        """
        self.logger.info(f"Signal {signum} received, shutting down...")
        self.stop()
        sys.exit(0)

    def get_statistics(self) -> dict:
        """
        Get system statistics.

        TODO:
        - Return dict with all statistics
        - Include detection counts, rates, uptime, etc.
        """
        # TODO: Implement statistics retrieval
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"<SystemManager: state={self.state.value}, uptime={helpers.format_uptime(self.get_uptime())}>"

    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()


if __name__ == "__main__":
    """Test system manager."""
    print("System Manager test - TODO: Implement test code")
    print("Testing get_current_frame()...")
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.utils.logger import setup_logger, get_logger

    setup_logger()

    manager = SystemManager()
    frame = manager.get_current_frame()
    if frame is not None:
        print("Frame retrieved successfully.")
        cv2.imshow("Test Frame", frame)
        cv2.waitKey(2000)  # Display for 2 seconds
        cv2.destroyAllWindows()
    else:
        print("Failed to retrieve frame.")
