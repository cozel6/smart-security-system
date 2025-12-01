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

#from src.hardware import PIRSensor, LEDController, Buzzer
#from src.alerts import TelegramBot, AlertManager
from src.detection import  YOLODetector, DetectionType, AlertLevel # , MotionDetector
from src.streaming import FlaskServer, VideoStreamer
from src.utils.logger import setup_logger, get_logger
from src.utils import helpers
from config.settings import settings
from src.hardware import Camera 


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

        # Latest annotated frame for streaming
        self.latest_annotated_frame = None
        self.frame_lock = threading.Lock()

        # Snapshot cooldown tracking
        self.last_person_snapshot_time = 0
        self.last_animal_snapshot_time = 0
        self.snapshot_cooldown = 10  # seconds between snapshots

        # Statistics
        self.total_detections = 0
        self.person_detections = 0
        self.animal_detections = 0

    def initialize(self) -> bool:
        """
        Initialize all system components.
        """
        try:
            # 1. Setup logger
            self.logger = get_logger("_name_")
            self.logger.info("=" * 60)
            self.logger.info("Initializing Smart Security System...")
            self.logger.info("=" * 60)

            # 2. Initialization camera
            self.logger.info("Initializing camera...")
            self.camera = Camera()
            if not self.camera.start():
                self.logger.error("Failed to start camera")
                return False
            self.logger.info(f"Camera initialized: {self.camera}")

            # 3. Initialize YOLO detector
            self.logger.info("Initializing YOLO detector...")
            from src.detection.yolo_detector import YOLODetector
            self.yolo_detector = YOLODetector()

            if not self.yolo_detector.load_model():
                self.logger.error("Failed to load yolo model")
                # Continue anyway - detection will be disabled
            else:
                self.logger.info(f"YOLO detector initialized: {self.yolo_detector}")
            



            # 4. Initialize Flask server with callbacks
            self.logger.info("Initializing Flask server...")
            self.flask_server = FlaskServer()
            

            # 5. Start Flask server
            self.logger.info("Registering Flask callbacks...")
            self.flask_server.register_callbacks(
                get_frame=self.get_current_frame,
                get_status=self.get_status,
                arm=self.arm,
                disarm=self.disarm,
            )
            self.flask_server.start()
            self.start_time = time.time()
            self._is_armed = False
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
            
            # 5. Start detection thread
            if self.yolo_detector and self.yolo_detector.model_loaded:
                self.logger.info("Starting detection thread...")
                self.stop_event.clear()
                self.detection_thread = threading.Thread(
                    target=self._detection_loop,
                    daemon=True,
                    name="DetectionThread"
                )
                self.detection_thread.start()
                self.logger.info("✓ Detection thread started")
            else:
                self.logger.warning("YOLO detector not available, detection disabled")

            self.logger.info("System armed successfully")

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
        """
        self.logger.info("Detection loop started")

        # Target FPS for detection (lower than camera FPS)
        detection_fps = 5 # Run detection at 5 fps
        frame_interval = 1.0 / detection_fps

        consecutive_empty_frames = 0
        max_empty_frames = 10

        try:
            while not self.stop_event.is_set():
                # Check if still armed
                if self.state != SystemState.ARMED and self.state != SystemState.ALARM:
                    self.logger.info("Detection loop: System not armed, pausing...")
                    time.sleep(1)
                    continue
                loop_start_time = time.time()

                # 1. Get frame from camera
                frame = None
                if self.camera and self.camera.is_opened():
                    frame = self.camera.get_frame(timeout=0.5)
                
                # 2. Check frame is valid
                if frame is None:
                    consecutive_empty_frames += 1
                    if consecutive_empty_frames >= max_empty_frames:
                        self.logger.error("To many failed frame reads, stopping detection")
                        break
                    time.sleep(0.1)
                    continue
                # Reset empty frame counter 
                consecutive_empty_frames = 0

                # 3. YOLO Detection
                if self.yolo_detector and self.yolo_detector.model_loaded:
                    detection_result = self.yolo_detector.detect(frame, draw=True)

                    # Update latest annotated frame for streaming
                    # Use annotated frame if available, otherwise use original frame
                    annotated = detection_result.get('frame')
                    with self.frame_lock:
                        self.latest_annotated_frame = annotated if annotated is not None else frame

                    # 4. Process detection results
                    if detection_result['type'] != DetectionType.NONE:
                        self._process_detection(frame, detection_result)
                # 5. Control loop rate
                elapsed = time.time() - loop_start_time
                sleep_time = frame_interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                # Log performance 
                if self.yolo_detector.inference_count % 50 == 0 and self.yolo_detector.inference_count > 0:
                    stats = self.yolo_detector.get_statistics()
                    self.logger.info(
                    f"Detection stats: {stats['inference_count']} inferences, "
                    f"{stats['person_detections']} persons, "
                    f"{stats['animal_detections']} animals"
                )
        except Exception as e:
            self.logger.error(f"Error in detection loop: {e}", exc_info=True)
        
        finally:
            self.logger.info("Detection loop stopped")


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
        """
        try:
            detection_type = detection_result['type']
            alert_level = detection_result['alert_level']
            person_count = detection_result['person_count']
            animal_count = detection_result['animal_count']

            # Log detection
            self.logger.info(
                f"Detection: {detection_type.value} - "
                f"Alert: {alert_level.value} - "
                f"Persons: {person_count}, Animals: {animal_count}"
            )
            # Update statistics
            self.total_detections += 1
            if person_count > 0:
                self.person_detections += person_count
            if animal_count > 0:
                self.animal_detections += animal_count
            
            # Handle PERSON detection (CRITICAL alert)
            if detection_type == DetectionType.PERSON or detection_type == DetectionType.BOTH:
                self.logger.warning(f"CRITICAL: Person detected! Count: {person_count}")

                # Trigger alarm
                self.trigger_alarm()

                # Save snapshot (with cooldown)
                current_time = time.time()
                if current_time - self.last_person_snapshot_time >= self.snapshot_cooldown:
                    try:
                        from pathlib import Path
                        from datetime import datetime

                        Path("snapshots").mkdir(parents=True, exist_ok=True)

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        filename = f"snapshot_{timestamp}.jpg"
                        snapshot_path = f"snapshots/{filename}"

                        cv2.imwrite(snapshot_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        self.logger.info(f"Snapshot saved: {snapshot_path}")

                        # Update last snapshot time
                        self.last_person_snapshot_time = current_time

                    except Exception as e:
                        self.logger.error(f"Failed to save snapshot: {e}")
                else:
                    # Skip snapshot due to cooldown
                    remaining = self.snapshot_cooldown - (current_time - self.last_person_snapshot_time)
                    self.logger.debug(f"Snapshot skipped (cooldown: {remaining:.1f}s remaining)")

                #Queue alert (if alert manager available)
                if self.alert_manager:
                    self.alert_manager.queue_alert(
                        alert_type="person_detected",
                        alert_level=alert_level,
                        message=f"Person detected! Count: {person_count}",
                        snapshot_path=snapshot_path
                    )
                # Send Telegram alert (if bot available)
                if self.telegram_bot:
                    self.telegram_bot.send_alert(
                        f"🚨 CRITICAL ALERT 🚨\n\n"
                        f"Person detected!\n"
                        f"Persons: {person_count}\n"
                        f"Animals: {animal_count}\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                # Handle ANIMAL-only detection (LOW alert)
            elif detection_type == DetectionType.ANIMAL:
                self.logger.info(f"Animal detected: {animal_count}")

                # Save snapshot with cooldown (animals have longer cooldown)
                current_time = time.time()
                animal_cooldown = self.snapshot_cooldown * 3  # 30 seconds for animals
                if current_time - self.last_animal_snapshot_time >= animal_cooldown:
                    try:
                        from pathlib import Path
                        from datetime import datetime

                        Path("snapshots").mkdir(parents=True, exist_ok=True)

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        filename = f"snapshot_animal_{timestamp}.jpg"
                        snapshot_path = f"snapshots/{filename}"

                        cv2.imwrite(snapshot_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        self.logger.info(f"Animal snapshot saved: {snapshot_path}")

                        # Update last snapshot time
                        self.last_animal_snapshot_time = current_time

                    except Exception as e:
                        self.logger.error(f"Failed to save snapshot: {e}")
                else:
                    remaining = animal_cooldown - (current_time - self.last_animal_snapshot_time)
                    self.logger.debug(f"Animal snapshot skipped (cooldown: {remaining:.1f}s remaining)")

        except Exception as e:
            self.logger.error(f"Error processing detection: {e}", exc_info=True)




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
        Returns annotated frame with detections if available, otherwise raw camera frame.
        """
        # Try to return annotated frame first (with YOLO detections)
        if self.state == SystemState.ARMED or self.state == SystemState.ALARM:
            with self.frame_lock:
                if self.latest_annotated_frame is not None:
                    return self.latest_annotated_frame.copy()

        # Fallback to raw camera frame
        if self.camera and self.camera.is_opened():
            frame = self.camera.get_frame(timeout=0.5)
            if frame is not None:
                return frame

        # Fallback to dummy frame if camera unavailable
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
        """
        try:
            # Set state to ALARM
            self.state = SystemState.ALARM
            self.logger.warning("⚠️  ALARM TRIGGERED ⚠️")

            # Turn on red LED (if available)
            if self.led_controller:
                self.led_controller.set_alarm()

            # Activate buzzer (if available)
            if self.buzzer:
                self.buzzer.pulse()

            self.logger.info("Alarm activated: LEDs and buzzer triggered")

        except Exception as e:
            self.logger.error(f"Error triggering alarm: {e}", exc_info=True)

    def clear_alarm(self) -> None:
        """
        Clear alarm state (return to armed).
        """
        try:
            # Set state back to ARMED
            self.state = SystemState.ARMED
            self.logger.info("Alarm cleared, returning to armed state")

            # Stop red LED, return to green
            if self.led_controller:
                self.led_controller.set_armed()

            # Stop buzzer
            if self.buzzer:
                self.buzzer.stop()

            self.logger.info("Alarm cleared: LEDs and buzzer deactivated")

        except Exception as e:
            self.logger.error(f"Error clearing alarm: {e}", exc_info=True)

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

  
        if self.logger:
            self.logger.info("Shutting down system...")

        # Stop detection thread if running
        if self.detection_thread and self.detection_thread.is_alive():
            self.stop_event.set()
            self.detection_thread.join(timeout=5)

        # Stop Flask server
        if self.flask_server:
            self.logger.info("Stopping Flask server...")
            self.flask_server.stop()

        # Stop YOLO detector
        if self.yolo_detector:
            self.logger.info("Stopping YOLO detector...")
            stats = self.yolo_detector.get_statistics()
            self.logger.info(f"Detection statistics: {stats}")
            
        # Stop camera
        if self.camera:
            self.logger.info("Stopping camera...")
            self.camera.stop()

        # Turn off hardware (if available)
        if self.led_controller:
            self.led_controller.turn_off_all()
        
        if self.buzzer:
            self.buzzer.stop()

        if self.logger:
            self.logger.info("✓ System shutdown complete")
        
        

        



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
