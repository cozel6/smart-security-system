"""
Face Recognition Detector Module - Custom Person Recognition

This module implements face recognition to identify authorized persons.
Recognizes specific individuals (e.g., Cosmin, Coleg) and labels unknown persons as "Unknown Person".

Uses face_recognition library (based on dlib) for high-accuracy face detection and recognition.

Usage:
    from src.detection.face_recognition_detector import FaceRecognitionDetector
    
    detector = FaceRecognitionDetector()
    detector.load_model()
    
    result = detector.detect(frame, draw=True)
    # Returns same format as YOLODetector
"""

import cv2
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Optional
import face_recognition

from src.detection.yolo_detector import DetectionType, AlertLevel
from config.settings import settings


class FaceRecognitionDetector:
    """
    Face recognition detector for person identification.
    
    Compatible with YOLODetector API - can be used as a drop-in replacement.
    Detects faces and recognizes known persons from database.
    """
    
    def __init__(
        self,
        database_path: Optional[str] = None,
        tolerance: Optional[float] = None
    ):
        """
        Initialize face recognition detector.
        """
        # Load settings
        self.database_path = database_path or settings.known_faces_db
        self.tolerance = tolerance or settings.face_recognition_tolerance
        
        # Known faces database
        self.known_face_encodings = {}  
        self.model_loaded = False
        
        # Statistics
        self.inference_count = 0
        self.person_detections = 0
        self.authorized_detections = 0
        self.unknown_detections = 0
        
    def load_model(self) -> bool:
        """
        Load known faces database.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            db_file = Path(self.database_path)
            
            if not db_file.exists():
                print(f"⚠️  Database not found at {self.database_path}")
                print("   Creating empty database. Use register_person.py to add people.")
                
                # Create empty database
                db_file.parent.mkdir(parents=True, exist_ok=True)
                self.known_face_encodings = {}
                self._save_database()
                self.model_loaded = True
                return True
            
            # Load database
            print(f"Loading face recognition database: {self.database_path}")
            with open(db_file, 'rb') as f:
                self.known_face_encodings = pickle.load(f)
            
            # Log loaded persons
            person_count = len(self.known_face_encodings)
            print(f"✓ Face Recognition model loaded successfully!")
            print(f"  - Database: {self.database_path}")
            print(f"  - Known persons: {person_count}")
            if person_count > 0:
                print(f"  - Names: {', '.join(self.known_face_encodings.keys())}")
            print(f"  - Tolerance: {self.tolerance}")
            
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to load face recognition database: {e}")
            import traceback
            traceback.print_exc()
            self.model_loaded = False
            return False
    
    def detect(
        self,
        frame: np.ndarray,
        draw: bool = False
    ) -> Dict:
        """
        Detect and recognize faces in frame.
        """
        try:
            # Check if model is loaded
            if not self.model_loaded:
                print("Model not loaded, attempting to load...")
                if not self.load_model():
                    return self._empty_result(frame, draw)
            
            # Convert BGR to RGB (face_recognition uses RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # OPTIMIZE: Downsample to 50% for faster face detection (4x speedup)
            small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)

            # Detect faces on downsampled frame
            face_locations = face_recognition.face_locations(small_frame, model="hog")

            # If no faces detected
            if len(face_locations) == 0:
                return self._empty_result(frame, draw)

            # Extract face encodings from SAME downsampled frame (critical for accuracy!)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            # Scale face locations back to original frame size for drawing
            face_locations = [(top*2, right*2, bottom*2, left*2)
                            for (top, right, bottom, left) in face_locations]
            
            # Process each face
            detections = []
            authorized_count = 0
            unknown_count = 0
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Recognize face
                name, confidence, is_authorized = self._recognize_face(face_encoding)
                
                # Count
                if is_authorized:
                    authorized_count += 1
                else:
                    unknown_count += 1
                
                # Create detection dict (compatible with YOLO format)
                detection = {
                    'class': 0,  # Person class ID
                    'class_name': name,
                    'confidence': confidence,
                    'bbox': [left, top, right, bottom],  # [x1, y1, x2, y2]
                    'classification': 'authorized' if is_authorized else 'intruder'
                }
                detections.append(detection)
            
            # Determine detection type and alert level
            person_count = len(detections)
            detection_type = DetectionType.PERSON
            
            # Alert level based on authorization
            if unknown_count > 0:
                alert_level = AlertLevel.CRITICAL  # Unknown person = INTRUDER
            else:
                alert_level = AlertLevel.NONE  # All authorized = no alert
            
            # Draw detections if requested
            annotated_frame = None
            if draw:
                annotated_frame = self._draw_detections(frame.copy(), detections)
            
            # Update statistics
            self.inference_count += 1
            self.person_detections += person_count
            self.authorized_detections += authorized_count
            self.unknown_detections += unknown_count
            
            # Return result (compatible with YOLO format)
            result = {
                'type': detection_type,
                'alert_level': alert_level,
                'detections': detections,
                'frame': annotated_frame,
                'person_count': person_count,
                'animal_count': 0,  # Face recognition doesn't detect animals
                'authorized_person_detected': authorized_count > 0,  # Flag for authorized detection
                'authorized_names': [d['class_name'] for d in detections if d['classification'] == 'authorized'],
                'unknown_count': unknown_count,
                'authorized_count': authorized_count
            }

            return result
            
        except Exception as e:
            print(f"ERROR in detect(): {e}")
            import traceback
            traceback.print_exc()
            return self._empty_result(frame, draw)
    
    def _recognize_face(self, face_encoding: np.ndarray) -> tuple:
        """
        Recognize a face by comparing with known faces database.
        """
        # If no known faces, all are unknown
        if len(self.known_face_encodings) == 0:
            return ("Unknown Person", 0.5, False)
        
        # Compare with all known faces
        best_match_name = "Unknown Person"
        best_match_distance = 1.0  # Max distance
        is_authorized = False
        
        for name, encodings_list in self.known_face_encodings.items():
            # Compare with all encodings for this person
            distances = face_recognition.face_distance(encodings_list, face_encoding)
            min_distance = np.min(distances)

            # Check if this is the best match so far
            if min_distance < best_match_distance:
                best_match_distance = min_distance
                if min_distance <= self.tolerance:
                    best_match_name = name
                    is_authorized = True
        
        # Convert distance to confidence (0-1)
        confidence = 1.0 - min(best_match_distance, 1.0)

        return (best_match_name, confidence, is_authorized)
    
    def _draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict]
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame.
        """
        for det in detections:
            # Extract bbox [x1, y1, x2, y2]
            x1, y1, x2, y2 = map(int, det['bbox'])
            name = det['class_name']
            confidence = det['confidence']
            is_authorized = det['classification'] == 'authorized'
            
            # Choose color based on authorization
            if is_authorized:
                color = (0, 255, 0)  # Green for authorized (BGR)
                thickness = 2
            else:
                color = (0, 0, 255)  # Red for unknown/intruder (BGR)
                thickness = 3
            
            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Prepare label
            if is_authorized:
                label = f"{name} ({confidence:.2f})"
            else:
                label = "Person"  # Don't show confidence for unknown persons
            
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
    
    def _empty_result(self, frame: np.ndarray, draw: bool) -> Dict:
        """Return empty detection result."""
        return {
            'type': DetectionType.NONE,
            'alert_level': AlertLevel.NONE,
            'detections': [],
            'frame': frame.copy() if draw else None,
            'person_count': 0,
            'animal_count': 0
        }
    
    def _save_database(self) -> None:
        """Save known faces database to file."""
        db_file = Path(self.database_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(db_file, 'wb') as f:
            pickle.dump(self.known_face_encodings, f)
    
    def add_person(self, name: str, encodings: List[np.ndarray]) -> bool:
        """
        Add a person to the known faces database.
        
        Args:
            name: Person's name
            encodings: List of face encodings for this person
        
        Returns:
            bool: True if added successfully
        """
        try:
            self.known_face_encodings[name] = encodings
            self._save_database()
            print(f"✓ Added {name} to database ({len(encodings)} encodings)")
            return True
        except Exception as e:
            print(f"ERROR: Failed to add person: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get detection statistics.
        
        Returns:
            Dict with statistics
        """
        authorized_rate = (
            self.authorized_detections / self.person_detections
            if self.person_detections > 0
            else 0.0
        )
        
        unknown_rate = (
            self.unknown_detections / self.person_detections
            if self.person_detections > 0
            else 0.0
        )
        
        return {
            'inference_count': self.inference_count,
            'person_detections': self.person_detections,
            'authorized_detections': self.authorized_detections,
            'unknown_detections': self.unknown_detections,
            'authorized_rate': authorized_rate,
            'unknown_rate': unknown_rate,
            'model_loaded': self.model_loaded,
            'known_persons': list(self.known_face_encodings.keys()),
            'tolerance': self.tolerance
        }
    
    def set_tolerance(self, tolerance: float) -> None:
        """Update face matching tolerance."""
        if not 0.0 <= tolerance <= 1.0:
            raise ValueError(f"Tolerance must be between 0.0 and 1.0, got {tolerance}")
        self.tolerance = tolerance
        print(f"Tolerance updated to {tolerance}")
    
    def reset_statistics(self) -> None:
        """Reset detection statistics."""
        self.inference_count = 0
        self.person_detections = 0
        self.authorized_detections = 0
        self.unknown_detections = 0
    
    def __repr__(self) -> str:
        """String representation."""
        status = "loaded" if self.model_loaded else "not loaded"
        person_count = len(self.known_face_encodings)
        return f"<FaceRecognitionDetector: {person_count} persons, tolerance={self.tolerance}, {status}>"


if __name__ == "__main__":
    """Test face recognition detector."""
    print("Face Recognition Detector Test")
    print("=" * 50)
    
    detector = FaceRecognitionDetector()
    
    if detector.load_model():
        print("\n✓ Model loaded successfully")
        print(f"  {detector}")
        stats = detector.get_statistics()
        print(f"\nKnown persons: {stats['known_persons']}")
    else:
        print("\n✗ Failed to load model")