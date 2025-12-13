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
from typing import Optional, Dict
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
        self.logger = get_logger(__name__)

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
        self.face_detector = None  # For two-stage detection

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
        self._last_fps = 0.0  # Track actual FPS

        # Face recognition queue for async processing
        self.face_recognition_results = {}  # {frame_id: result}
        self.face_recognition_lock = threading.Lock()

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

            # 3. Initialize Detectors (YOLO + Face Recognition for two-stage detection)
            self.logger.info("Initializing two-stage detection (YOLO + Face Recognition)...")

            # Load YOLO detector (stage 1: detect persons)
            from src.detection.yolo_detector import YOLODetector
            self.yolo_detector = YOLODetector()
            if not self.yolo_detector.load_model():
                self.logger.error("Failed to load YOLO model")
            else:            
                self.logger.info(f"✓ YOLO detector loaded: {self.yolo_detector}")
            
            # Load Face Recognition detector (stage 2: identify authorized persons)
            try:
                from src.detection.face_recognition_detector import FaceRecognitionDetector
                self.face_detector = FaceRecognitionDetector()
                if self.face_detector.load_model():
                    self.logger.info(f"✓ Face Recognition detector loaded: {self.face_detector}")
                else:
                    self.logger.warning("Face Recognition detector failed to load (no authorized persons?)")
                    self.face_detector = None
            except Exception as e:
                self.logger.warning(f"Face Recognition detector not available: {e}")
                self.face_detector = None

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

                # 3. Two-Stage Detection: YOLO (stage 1) → Face Recognition (stage 2)
                if self.yolo_detector and self.yolo_detector.model_loaded:
                    # Run YOLO detection first (without drawing if person might be detected)
                    detection_result = self.yolo_detector.detect(frame, draw=False)

                    # 4. Process detection results
                    if detection_result['type'] != DetectionType.NONE:
                        # STAGE 2: If person detected, check if authorized (Face Recognition)
                        if detection_result['person_count'] > 0 and self.face_detector:
                            self.logger.info("Person detected by YOLO, running Face Recognition in background...")

                            # Run face recognition in BACKGROUND THREAD (non-blocking)
                            frame_copy = frame.copy()
                            frame_id = time.time()

                            def run_face_recognition_async():
                                try:
                                    # Enable drawing to show names and bounding boxes on frame
                                    face_result = self.face_detector.detect(frame_copy, draw=True)

                                    # Store result with frame_id
                                    with self.face_recognition_lock:
                                        self.face_recognition_results[frame_id] = face_result

                                        # Keep only last 5 results (prevent memory leak)
                                        if len(self.face_recognition_results) > 5:
                                            oldest_key = min(self.face_recognition_results.keys())
                                            del self.face_recognition_results[oldest_key]

                                except Exception as e:
                                    self.logger.error(f"Face recognition error: {e}")

                            # Start background thread with 3-second timeout
                            face_thread = threading.Thread(target=run_face_recognition_async, daemon=True)
                            face_thread.start()

                            # Wait maximum 3 seconds for face recognition result
                            face_thread.join(timeout=3.0)

                            # Check if result available
                            with self.face_recognition_lock:
                                face_result = self.face_recognition_results.get(frame_id)

                            if face_result:
                                # Update annotated frame with face recognition results (always show names)
                                face_annotated = face_result.get('frame')
                                if face_annotated is not None:
                                    with self.frame_lock:
                                        self.latest_annotated_frame = face_annotated

                                # Check if authorized person detected
                                if face_result.get('authorized_person_detected', False):
                                    authorized_names = face_result.get('authorized_names', [])
                                    self.logger.info(f"✓ Authorized person detected: {authorized_names} - NO ALERT")

                                    # Skip alert for authorized persons
                                    continue
                                else:
                                    self.logger.warning("⚠ Unknown person detected - TRIGGERING ALERT")
                            else:
                                # Face recognition timeout - draw YOLO results manually
                                self.logger.warning("Face recognition timeout or failed - using YOLO detection")
                                yolo_annotated = self._draw_yolo_detections(frame.copy(), detection_result)
                                with self.frame_lock:
                                    self.latest_annotated_frame = yolo_annotated

                        # Process detection (triggers alert if not authorized)
                        self._process_detection(frame, detection_result)
                    else:
                        # No person detected, but maybe animals - draw YOLO results
                        if detection_result['animal_count'] > 0:
                            yolo_annotated = self._draw_yolo_detections(frame.copy(), detection_result)
                            with self.frame_lock:
                                self.latest_annotated_frame = yolo_annotated
                        else:
                            # No detections at all - show clean frame
                            with self.frame_lock:
                                self.latest_annotated_frame = frame

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

                # Calculate and store FPS
                actual_loop_time = time.time() - loop_start_time
                if actual_loop_time > 0:
                    self._last_fps = 1.0 / actual_loop_time
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

            # Initialize snapshot_path for alert manager usage
            snapshot_path = None

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

                # Save snapshot (with cooldown) in BACKGROUND THREAD
                current_time = time.time()
                if current_time - self.last_person_snapshot_time >= self.snapshot_cooldown:
                    frame_copy = frame.copy()  # Prevent race conditions
                    self.last_person_snapshot_time = current_time  # Update BEFORE thread starts
                    
                    def save_snapshot_async():
                        nonlocal snapshot_path
                        try:
                            from pathlib import Path
                            from datetime import datetime

                            Path("snapshots").mkdir(parents=True, exist_ok=True)

                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                            filename = f"snapshot_{timestamp}.jpg"
                            snapshot_path = f"snapshots/{filename}"

                            cv2.imwrite(snapshot_path, frame_copy, [cv2.IMWRITE_JPEG_QUALITY, 95])
                            self.logger.info(f"Snapshot saved: {snapshot_path}")

                        except Exception as e:
                            self.logger.error(f"Failed to save snapshot: {e}")
                    
                    # Run in background thread
                    threading.Thread(target=save_snapshot_async, daemon=True).start()
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

                # Save snapshot with cooldown (animals have longer cooldown) in BACKGROUND THREAD
                current_time = time.time()
                animal_cooldown = self.snapshot_cooldown * 3  # 30 seconds for animals
                if current_time - self.last_animal_snapshot_time >= animal_cooldown:
                    frame_copy = frame.copy()  # Prevent race conditions
                    self.last_animal_snapshot_time = current_time  # Update BEFORE thread starts
                    
                    def save_animal_snapshot_async():
                        nonlocal snapshot_path
                        try:
                            from pathlib import Path
                            from datetime import datetime

                            Path("snapshots").mkdir(parents=True, exist_ok=True)

                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                            filename = f"snapshot_animal_{timestamp}.jpg"
                            snapshot_path = f"snapshots/{filename}"

                            cv2.imwrite(snapshot_path, frame_copy, [cv2.IMWRITE_JPEG_QUALITY, 95])
                            self.logger.info(f"Animal snapshot saved: {snapshot_path}")

                        except Exception as e:
                            self.logger.error(f"Failed to save snapshot: {e}")
                    
                    # Run in background thread
                    threading.Thread(target=save_animal_snapshot_async, daemon=True).start()
                else:
                    remaining = animal_cooldown - (current_time - self.last_animal_snapshot_time)
                    self.logger.debug(f"Animal snapshot skipped (cooldown: {remaining:.1f}s remaining)")
        except Exception as e:
            self.logger.error(f"Error processing detection: {e}", exc_info=True)

    def _draw_yolo_detections(self, frame: np.ndarray, detection_result: Dict) -> np.ndarray:
        """
        Draw YOLO detection boxes on frame.
        Helper function to avoid running YOLO detection twice.
        """
        detections = detection_result.get('detections', [])

        for det in detections:
            # Extract bbox
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)

            # Get class info
            class_name = det['class_name']
            confidence = det['confidence']

            # Choose color (red for person, yellow for animal)
            if class_name.lower() == 'person':
                color = (0, 0, 255)  # Red (BGR)
                thickness = 3
            else:
                color = (0, 255, 255)  # Yellow for animals (BGR)
                thickness = 2

            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            # Prepare label
            label = f"{class_name} ({confidence:.2f})"

            # Get text size for background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, font_thickness
            )

            # Draw label background
            label_y = y1 - 10 if y1 - 10 > text_height else y1 + text_height + 10
            cv2.rectangle(
                frame,
                (x1, label_y - text_height - baseline),
                (x1 + text_width, label_y + baseline),
                color,
                -1  # Filled
            )

            # Draw label text
            cv2.putText(
                frame,
                label,
                (x1, label_y),
                font,
                font_scale,
                (255, 255, 255),  # White text
                font_thickness,
                cv2.LINE_AA
            )

        return frame

    def get_status(self) -> dict:
        """Get current system status with proper format for dashboard."""
        from src.utils.helpers import get_cpu_usage, get_memory_usage, get_cpu_temperature
        import time

        # Calculate uptime in SECONDS (not formatted)
        uptime_seconds = time.time() - self.start_time if hasattr(self, 'start_time') and isinstance(self.start_time, (int, float)) else 0

        # Get CPU temperature (handle None on Mac)
        cpu_temp = get_cpu_temperature()

        # Calculate actual camera FPS
        camera_fps = 0.0
        if self.camera and hasattr(self.camera, 'get_fps'):
            camera_fps = self.camera.get_fps()
        elif hasattr(self, '_last_fps'):
            camera_fps = self._last_fps

        status = {
            # Frontend expects "state" not "armed"
            "state": self.state.value if hasattr(self, 'state') else "disarmed",

            # Numeric values, not formatted strings
            "cpu_usage": round(get_cpu_usage(), 1),
            "ram_usage": round(get_memory_usage(), 1),
            "temperature": round(cpu_temp, 1) if cpu_temp is not None else None,

            # CRITICAL: Send uptime as NUMBER (seconds), not formatted string
            "uptime": uptime_seconds,

            # Calculate actual camera FPS
            "camera_fps": round(camera_fps, 1),

            # Add detection statistics
            "detections": {
                "total": self.total_detections,
                "person": self.person_detections,
                "animal": self.animal_detections
            },

            # Last detection timestamp
            "last_detection": self.last_detection_time.isoformat() if hasattr(self, 'last_detection_time') and self.last_detection_time else None
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

        # Stop Face Recognition detector
        if self.face_detector:
            self.logger.info("Stopping Face Recognition detector...")
            
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
        """Get system statistics."""
        stats = {
            'total_detections': self.total_detections,
            'person_detections': self.person_detections,
            'animal_detections': self.animal_detections,
            'uptime_seconds': self.get_uptime(),
            'state': self.state.value
        }
        
        # Add component statistics if available
        if self.yolo_detector:
            stats['yolo'] = self.yolo_detector.get_statistics()
        if self.motion_detector:
            stats['motion'] = self.motion_detector.get_statistics()
        if self.alert_manager:
            stats['alerts'] = self.alert_manager.get_statistics()
        if self.video_streamer:
            stats['streaming'] = self.video_streamer.get_statistics()
        
        return stats

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
