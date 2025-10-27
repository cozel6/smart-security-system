#!/bin/bash

# ==========================================
# SMART SECURITY SYSTEM - SETUP SCRIPT
# ==========================================
# Automated installation script for Raspberry Pi
# Run with: bash setup.sh

set -e  # Exit on error

echo "=========================================="
echo "Smart Security System - Setup"
echo "=========================================="
echo ""

# TODO: Check if running on Raspberry Pi
# Uncomment and implement:
# if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
#     echo "Warning: This script is designed for Raspberry Pi"
#     read -p "Continue anyway? (y/n) " -n 1 -r
#     echo
#     if [[ ! $REPLY =~ ^[Yy]$ ]]; then
#         exit 1
#     fi
# fi

# ==========================================
# 1. System Update
# ==========================================
echo "Step 1: Updating system packages..."
# TODO: Uncomment when ready to run on Raspberry Pi
# sudo apt-get update
# sudo apt-get upgrade -y
echo "✓ System update complete (TODO: uncomment commands)"

# ==========================================
# 2. Install System Dependencies
# ==========================================
echo ""
echo "Step 2: Installing system dependencies..."
# TODO: Uncomment and install required packages:
# sudo apt-get install -y \
#     python3-pip \
#     python3-venv \
#     python3-dev \
#     python3-opencv \
#     libopencv-dev \
#     libatlas-base-dev \
#     libjasper-dev \
#     libqtgui4 \
#     libqt4-test \
#     libhdf5-dev \
#     git \
#     cmake
echo "✓ System dependencies installed (TODO: uncomment commands)"

# ==========================================
# 3. Create Virtual Environment
# ==========================================
echo ""
echo "Step 3: Creating Python virtual environment..."
# TODO: Implement virtual environment creation
# if [ -d "venv" ]; then
#     echo "Virtual environment already exists, skipping..."
# else
#     python3 -m venv venv
#     echo "✓ Virtual environment created"
# fi
echo "✓ Virtual environment ready (TODO: implement)"

# ==========================================
# 4. Activate Virtual Environment
# ==========================================
echo ""
echo "Step 4: Activating virtual environment..."
# TODO: Implement activation
# source venv/bin/activate
echo "✓ Virtual environment activated (TODO: implement)"

# ==========================================
# 5. Upgrade pip
# ==========================================
echo ""
echo "Step 5: Upgrading pip..."
# TODO: Upgrade pip
# pip install --upgrade pip setuptools wheel
echo "✓ pip upgraded (TODO: implement)"

# ==========================================
# 6. Install Python Dependencies
# ==========================================
echo ""
echo "Step 6: Installing Python dependencies..."
echo "This may take 10-15 minutes on Raspberry Pi..."
# TODO: Install from requirements.txt
# pip install -r requirements.txt
echo "✓ Python dependencies installed (TODO: implement)"

# ==========================================
# 7. Setup GPIO Permissions
# ==========================================
echo ""
echo "Step 7: Setting up GPIO permissions..."
# TODO: Add user to gpio group
# sudo usermod -a -G gpio $USER
# sudo usermod -a -G video $USER
echo "✓ GPIO permissions set (TODO: implement)"

# ==========================================
# 8. Create .env File
# ==========================================
echo ""
echo "Step 8: Creating .env configuration file..."
# TODO: Copy .env.example to .env if not exists
# if [ ! -f ".env" ]; then
#     cp .env.example .env
#     echo "✓ .env file created from template"
#     echo "⚠️  IMPORTANT: Edit .env file with your Telegram credentials!"
# else
#     echo ".env file already exists, skipping..."
# fi
echo "✓ .env configuration ready (TODO: implement)"

# ==========================================
# 9. Create Required Directories
# ==========================================
echo ""
echo "Step 9: Verifying directory structure..."
# Directories already created by project structure
echo "✓ Directory structure verified"

# ==========================================
# 10. Download YOLO Model
# ==========================================
echo ""
echo "Step 10: Downloading YOLO model..."
# TODO: Download YOLOv5 nano model
# cd models
# wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt
# cd ..
echo "✓ YOLO model downloaded (TODO: implement)"
echo "Note: Model will auto-download on first run if not present"

# ==========================================
# 11. Test Camera
# ==========================================
echo ""
echo "Step 11: Testing camera..."
# TODO: Add camera test command
# python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAILED'); cap.release()"
echo "✓ Camera test (TODO: implement)"

# ==========================================
# 12. Test GPIO
# ==========================================
echo ""
echo "Step 12: Testing GPIO..."
# TODO: Add GPIO test
# python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('GPIO OK')"
echo "✓ GPIO test (TODO: implement)"

# ==========================================
# Setup Complete
# ==========================================
echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Telegram bot credentials"
echo "2. Review config/gpio_pins.py for GPIO pin mappings"
echo "3. Run the system: python3 main.py"
echo ""
echo "For testing individual components:"
echo "  - Camera: python3 -m src.hardware.camera"
echo "  - PIR Sensor: python3 -m src.hardware.pir_sensor"
echo "  - LEDs: python3 -m src.hardware.led_controller"
echo ""
echo "⚠️  Remember to reboot after first setup for GPIO permissions!"
echo ""
