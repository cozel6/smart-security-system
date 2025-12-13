"""
Register Person Script - Add Authorized Person to Face Recognition Database

This script captures multiple photos of a person and adds them to the
face recognition database for authorized person identification.

Usage:
    python scripts/register_person.py --name "Cosmin"
    python scripts/register_person.py --name "Coleg" --photos 5

Instructions:
    1. Script will open camera
    2. Position your face in the frame
    3. Press SPACE to capture photo (do 5 times with different angles)
    4. Press Q to finish
    5. Encodings will be saved to database
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import cv2
import face_recognition
import pickle
import numpy as np
from datetime import datetime

from config.settings import settings


def capture_photos(name: str, num_photos: int = 5):
    """
    Capture multiple photos of a person using webcam.

    Args:
        name: Person's name
        num_photos: Number of photos to capture

    Returns:
        list: List of captured frames
    """
    print(f"\n📷 Capturing {num_photos} photos for: {name}")
    print("\nInstructions:")
    print("  - Look at the camera")
    print("  - Press SPACE to take a photo")
    print("  - Try different angles (front, left, right, up, down)")
    print("  - Press Q to quit\n")

    # Open camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return []

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    captured_frames = []
    photo_count = 0

    while photo_count < num_photos:
        ret, frame = cap.read()

        if not ret:
            print("❌ Error: Failed to read frame")
            break

        # Display frame
        display_frame = frame.copy()

        # Add text overlay
        text = f"Photos: {photo_count}/{num_photos} - Press SPACE to capture"
        cv2.putText(display_frame, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Draw face detection box if face found
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow(f"Register {name}", display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):  # Space key
            if len(face_locations) == 0:
                print("⚠️  No face detected! Please try again.")
            elif len(face_locations) > 1:
                print("⚠️  Multiple faces detected! Please ensure only one person is visible.")
            else:
                captured_frames.append(frame.copy())
                photo_count += 1
                print(f"✓ Photo {photo_count}/{num_photos} captured!")

        elif key == ord('q'):  # Quit
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"\n✓ Captured {len(captured_frames)} photos")
    return captured_frames


def extract_encodings(frames):
    """
    Extract face encodings from captured frames.

    Args:
        frames: List of captured frames

    Returns:
        list: List of face encodings (128D vectors)
    """
    print("\n🔍 Extracting face encodings...")

    encodings = []

    for i, frame in enumerate(frames):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)

        if len(face_locations) == 0:
            print(f"  ⚠️  Photo {i+1}: No face detected, skipping")
            continue

        if len(face_locations) > 1:
            print(f"  ⚠️  Photo {i+1}: Multiple faces detected, using first one")

        # Extract encoding
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if len(face_encodings) > 0:
            encodings.append(face_encodings[0])
            print(f"  ✓ Photo {i+1}: Encoding extracted")
        else:
            print(f"  ⚠️  Photo {i+1}: Failed to extract encoding")

    print(f"\n✓ Extracted {len(encodings)} encodings")
    return encodings


def save_to_database(name: str, encodings: list):
    """
    Save person's encodings to database.

    Args:
        name: Person's name
        encodings: List of face encodings

    Returns:
        bool: True if saved successfully
    """
    print(f"\n💾 Saving to database...")

    db_path = Path(settings.known_faces_db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing database
    if db_path.exists():
        with open(db_path, 'rb') as f:
            database = pickle.load(f)
        print(f"  Loaded existing database with {len(database)} persons")
    else:
        database = {}
        print("  Creating new database")

    # Add/Update person
    database[name] = encodings

    # Save database
    with open(db_path, 'wb') as f:
        pickle.dump(database, f)

    print(f"✓ Saved {len(encodings)} encodings for '{name}' to: {db_path}")
    print(f"\nDatabase now contains {len(database)} persons:")
    for person_name, person_encodings in database.items():
        print(f"  - {person_name}: {len(person_encodings)} encodings")

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Register a person for face recognition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/register_person.py --name "xyz" --photos 5

After registration, update .env:
  DETECTOR_TYPE=custom

Then run the system:
  python main.py --arm
        """
    )

    parser.add_argument(
        '--name',
        type=str,
        required=True,
        help='Name of the person to register'
    )

    parser.add_argument(
        '--photos',
        type=int,
        default=5,
        help='Number of photos to capture (default: 5)'
    )

    args = parser.parse_args()

    print("="  * 60)
    print("  FACE REGISTRATION - Smart Security System")
    print("=" * 60)
    print(f"  Person: {args.name}")
    print(f"  Photos: {args.photos}")
    print("=" * 60)

    # Step 1: Capture photos
    frames = capture_photos(args.name, args.photos)

    if len(frames) == 0:
        print("\n❌ No photos captured. Exiting.")
        return 1

    # Step 2: Extract encodings
    encodings = extract_encodings(frames)

    if len(encodings) == 0:
        print("\n❌ No face encodings extracted. Exiting.")
        return 1

    if len(encodings) < 3:
        print(f"\n⚠️  Warning: Only {len(encodings)} encodings extracted.")
        print("   For best results, capture at least 3-5 photos with different angles.")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return 1

    # Step 3: Save to database
    save_to_database(args.name, encodings)

    print("\n" + "=" * 60)
    print("✓ Registration complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Update .env file:")
    print("     DETECTOR_TYPE=custom")
    print("  2. Run the system:")
    print("     python main.py --arm")
    print("  3. Test recognition with camera!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
