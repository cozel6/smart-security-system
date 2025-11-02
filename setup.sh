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

# ==========================================
# Check if running on Raspberry Pi
# ==========================================
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ==========================================
# 1. System Update
# ==========================================
echo "Step 1: Updating system packages..."
echo "This may take a few minutes..."
sudo apt-get update
sudo apt-get upgrade -y
echo "✓ System update complete"

# ==========================================
# 2. Install System Dependencies
# ==========================================
echo ""
echo "Step 2: Installing system dependencies..."
echo "This may take 5-10 minutes..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-opencv \
    libopencv-dev \
    libatlas-base-dev \
    libjpeg-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp-dev \
    libopenexr-dev \
    libilmbase-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    git \
    cmake \
    build-essential

echo "✓ System dependencies installed"

# ==========================================
# 3. Create Virtual Environment
# ==========================================
echo ""
echo "Step 3: Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# ==========================================
# 4. Activate Virtual Environment
# ==========================================
echo ""
echo "Step 4: Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# ==========================================
# 5. Upgrade pip
# ==========================================
echo ""
echo "Step 5: Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ pip upgraded"

# ==========================================
# 6. Install Python Dependencies
# ==========================================
echo ""
echo "Step 6: Installing Python dependencies..."
echo "⚠️  This may take 10-20 minutes on Raspberry Pi..."
echo "Please be patient..."

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing packages manually..."
    
    # Core packages
    pip install numpy==1.24.3
    pip install opencv-python==4.8.1.78
    
    # YOLOv5
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    pip install ultralytics==8.0.196
    
    # Web framework
    pip install flask==3.0.0
    pip install flask-cors==4.0.0
    
    # Telegram bot
    pip install python-telegram-bot==20.6
    
    # GPIO
    pip install RPi.GPIO==0.7.1
    
    # Utilities
    pip install python-dotenv==1.0.0
    pip install pillow==10.1.0
    pip install requests==2.31.0
fi

echo "✓ Python dependencies installed"

# ==========================================
# 7. Setup GPIO Permissions
# ==========================================
echo ""
echo "Step 7: Setting up GPIO permissions..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G video $USER
echo "✓ GPIO permissions set"

# ==========================================
# 8. Create .env File
# ==========================================
echo ""
echo "Step 8: Creating .env configuration file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created from template"
    else
        # Create basic .env file
        cat > .env << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# System Configuration
DEBUG=False
LOG_LEVEL=INFO

# Camera Configuration
CAMERA_INDEX=0
FRAME_WIDTH=640
FRAME_HEIGHT=480
FPS=15

# Detection Configuration
CONFIDENCE_THRESHOLD=0.5
MOTION_THRESHOLD=1000

# Web Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
EOF
        echo "✓ .env file created with default values"
    fi
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your Telegram credentials!"
    echo "   Get bot token from: https://t.me/BotFather"
    echo "   Get chat ID from: https://t.me/userinfobot"
else
    echo ".env file already exists, skipping..."
fi

# ==========================================
# 9. Create Required Directories
# ==========================================
echo ""
echo "Step 9: Creating required directories..."
mkdir -p logs
mkdir -p models
mkdir -p data/captures
mkdir -p data/events
echo "✓ Directory structure created"

# ==========================================
# 10. YOLO Model (Skipped)
# ==========================================
echo ""
echo "Step 10: YOLO model download skipped"
echo "Note: You can download a model later when ready"

# ==========================================
# Setup Complete
# ==========================================
echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Next steps:"
echo ""
echo "1. 🔑 Configure Telegram credentials:"
echo "   nano .env"
echo "   - Get bot token from: https://t.me/BotFather"
echo "   - Get chat ID from: https://t.me/userinfobot"
echo ""
echo "2. 🔄 REBOOT the Raspberry Pi (REQUIRED):"
echo "   sudo reboot"
echo ""
echo "3. 🧪 After reboot, we'll test components individually"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  IMPORTANT: REBOOT NOW for GPIO permissions!"
echo "   Run: sudo reboot"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""