#!/bin/bash

# ==========================================
# SMART SECURITY SYSTEM - SETUP SCRIPT
# ==========================================
# Production-ready installation for Raspberry Pi
# Tested on: Raspberry Pi OS (Debian Bookworm/Bullseye)
# Run with: bash setup.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Smart Security System - Setup"
echo "=========================================="
echo ""

# ==========================================
# Check if running on Raspberry Pi
# ==========================================
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo -e "${YELLOW}⚠️  Warning: This script is designed for Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ==========================================
# 1. System Update
# ==========================================
echo -e "${BLUE}Step 1: Updating system packages...${NC}"
echo "This may take a few minutes..."
sudo apt-get update
sudo apt-get upgrade -y
echo -e "${GREEN}✓ System update complete${NC}"

# ==========================================
# 2. Install System Dependencies
# ==========================================
echo ""
echo -e "${BLUE}Step 2: Installing system dependencies...${NC}"
echo "This may take 5-10 minutes..."

# Install core system packages
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    cmake \
    build-essential \
    pkg-config

# Install scientific computing libraries (pre-compiled, no build needed)
sudo apt-get install -y \
    python3-numpy \
    python3-scipy \
    python3-pil \
    python3-pil.imagetk

# Install OpenCV dependencies
sudo apt-get install -y \
    python3-opencv \
    libopencv-dev \
    libjpeg-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev

# Install HDF5 for data handling
sudo apt-get install -y \
    libhdf5-dev \
    libhdf5-serial-dev

# Install additional libraries
sudo apt-get install -y \
    libharfbuzz0b \
    libwebp-dev \
    libopenexr-dev \
    libilmbase-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev

# Try to install ATLAS or OpenBLAS (for linear algebra)
echo "Installing linear algebra library..."
if sudo apt-get install -y libatlas-base-dev 2>/dev/null; then
    echo -e "${GREEN}✓ libatlas-base-dev installed${NC}"
elif sudo apt-get install -y libatlas3-base 2>/dev/null; then
    echo -e "${GREEN}✓ libatlas3-base installed${NC}"
elif sudo apt-get install -y libopenblas-dev 2>/dev/null; then
    echo -e "${GREEN}✓ libopenblas-dev installed (alternative)${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Could not install ATLAS/OpenBLAS${NC}"
fi

echo -e "${GREEN}✓ System dependencies installed${NC}"

# ==========================================
# 3. Create Virtual Environment
# ==========================================
echo ""
echo -e "${BLUE}Step 3: Creating Python virtual environment...${NC}"

# Remove old venv if exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create venv with access to system packages (numpy, scipy, PIL)
python3 -m venv --system-site-packages venv
echo -e "${GREEN}✓ Virtual environment created${NC}"

# ==========================================
# 4. Activate Virtual Environment
# ==========================================
echo ""
echo -e "${BLUE}Step 4: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# ==========================================
# 5. Upgrade pip
# ==========================================
echo ""
echo -e "${BLUE}Step 5: Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"

# ==========================================
# 6. Install Python Dependencies
# ==========================================
echo ""
echo -e "${BLUE}Step 6: Installing Python dependencies...${NC}"
echo -e "${YELLOW}⚠️  This may take 15-25 minutes on Raspberry Pi...${NC}"
echo "Please be patient..."
echo ""

# Install OpenCV (use pre-built binary or system package)
echo -e "${BLUE}Installing OpenCV...${NC}"
pip install opencv-python-headless==4.8.1.78 --no-cache-dir || \
pip install opencv-python==4.8.1.78 --no-cache-dir || \
echo -e "${YELLOW}⚠️  Using system OpenCV (python3-opencv)${NC}"
echo -e "${GREEN}✓ OpenCV ready${NC}"

# Install PyTorch (CPU-only, optimized for Raspberry Pi)
echo ""
echo -e "${BLUE}Installing PyTorch (this will take 5-10 minutes)...${NC}"
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
echo -e "${GREEN}✓ PyTorch installed${NC}"

# Install YOLO
echo ""
echo -e "${BLUE}Installing Ultralytics YOLO...${NC}"
pip install ultralytics==8.0.196 --no-cache-dir
echo -e "${GREEN}✓ Ultralytics installed${NC}"

# Install Flask and web dependencies
echo ""
echo -e "${BLUE}Installing Flask...${NC}"
pip install flask==3.0.0 --no-cache-dir
echo -e "${GREEN}✓ Flask installed${NC}"

echo -e "${BLUE}Installing Flask-CORS...${NC}"
pip install flask-cors==4.0.0 --no-cache-dir
echo -e "${GREEN}✓ Flask-CORS installed${NC}"

echo -e "${BLUE}Installing Werkzeug...${NC}"
pip install werkzeug==3.0.1 --no-cache-dir
echo -e "${GREEN}✓ Werkzeug installed${NC}"

# Install Telegram bot
echo ""
echo -e "${BLUE}Installing Telegram bot...${NC}"
pip install python-telegram-bot==20.6 --no-cache-dir
echo -e "${GREEN}✓ Telegram bot installed${NC}"

# Install GPIO (will build from source - this is necessary)
echo ""
echo -e "${BLUE}Installing RPi.GPIO...${NC}"
pip install RPi.GPIO==0.7.1 --no-cache-dir
echo -e "${GREEN}✓ RPi.GPIO installed${NC}"

# Install utilities (using system PIL/Pillow to avoid build issues)
echo ""
echo -e "${BLUE}Installing utilities...${NC}"
pip install python-dotenv==1.0.0 --no-cache-dir
echo -e "${GREEN}✓ python-dotenv installed${NC}"

pip install requests==2.31.0 --no-cache-dir
echo -e "${GREEN}✓ requests installed${NC}"

pip install psutil==5.9.6 --no-cache-dir
echo -e "${GREEN}✓ psutil installed${NC}"

echo ""
echo -e "${GREEN}✓ All Python dependencies installed successfully!${NC}"

# ==========================================
# 7. Setup GPIO Permissions
# ==========================================
echo ""
echo -e "${BLUE}Step 7: Setting up GPIO permissions...${NC}"
sudo usermod -a -G gpio $USER
sudo usermod -a -G video $USER
echo -e "${GREEN}✓ GPIO permissions set${NC}"
echo -e "${YELLOW}⚠️  You'll need to reboot for GPIO permissions to take effect${NC}"

# ==========================================
# 8. Create .env File
# ==========================================
echo ""
echo -e "${BLUE}Step 8: Creating .env configuration file...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# ==========================================
# TELEGRAM BOT CONFIGURATION
# ==========================================
# Get bot token from: https://t.me/BotFather
# Get chat ID from: https://t.me/userinfobot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================
DEBUG=False
LOG_LEVEL=INFO

# ==========================================
# CAMERA CONFIGURATION
# ==========================================
CAMERA_INDEX=0
FRAME_WIDTH=640
FRAME_HEIGHT=480
FPS=15

# ==========================================
# DETECTION CONFIGURATION
# ==========================================
CONFIDENCE_THRESHOLD=0.5
MOTION_THRESHOLD=1000
YOLO_MODEL_PATH=models/yolov5n.pt

# ==========================================
# WEB SERVER CONFIGURATION
# ==========================================
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
EOF
    echo -e "${GREEN}✓ .env file created with default values${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file with your Telegram credentials!${NC}"
    echo -e "   Get bot token from: ${BLUE}https://t.me/BotFather${NC}"
    echo -e "   Get chat ID from: ${BLUE}https://t.me/userinfobot${NC}"
else
    echo -e "${YELLOW}.env file already exists, skipping...${NC}"
fi

# ==========================================
# 9. Create Required Directories
# ==========================================
echo ""
echo -e "${BLUE}Step 9: Creating required directories...${NC}"
mkdir -p logs
mkdir -p models
mkdir -p data/captures
mkdir -p data/events
mkdir -p config
mkdir -p src/hardware
mkdir -p src/detection
mkdir -p src/alerts
mkdir -p src/streaming
mkdir -p tests
echo -e "${GREEN}✓ Directory structure created${NC}"

# ==========================================
# 10. Verify Installation
# ==========================================
echo ""
echo -e "${BLUE}Step 10: Verifying installation...${NC}"
python3 << 'PYTHON_VERIFY'
import sys
packages = {
    'cv2': 'OpenCV',
    'torch': 'PyTorch',
    'flask': 'Flask',
    'telegram': 'Telegram Bot',
    'RPi.GPIO': 'GPIO',
    'dotenv': 'python-dotenv',
    'requests': 'Requests'
}

missing = []
for module, name in packages.items():
    try:
        __import__(module)
        print(f"✓ {name} - OK")
    except ImportError:
        print(f"✗ {name} - MISSING")
        missing.append(name)

if missing:
    print(f"\n⚠️  Missing packages: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\n✓ All packages verified successfully!")
PYTHON_VERIFY

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Installation verification passed${NC}"
else
    echo -e "${RED}✗ Some packages failed verification${NC}"
    echo -e "${YELLOW}You may need to install them manually${NC}"
fi

# ==========================================
# Setup Complete
# ==========================================
echo ""
echo "=========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo ""
echo -e "${YELLOW}1. 🔑 Configure Telegram credentials (optional - can be done later):${NC}"
echo "   nano .env"
echo "   - Get bot token from: https://t.me/BotFather"
echo "   - Get chat ID from: https://t.me/userinfobot"
echo ""
echo -e "${YELLOW}2. 🔄 REBOOT the Raspberry Pi (REQUIRED):${NC}"
echo "   sudo reboot"
echo ""
echo -e "${YELLOW}3. 🧪 After reboot, test components individually${NC}"
echo ""
echo -e "${YELLOW}4. 🚀 When ready, run the system:${NC}"
echo "   cd $(pwd)"
echo "   source venv/bin/activate"
echo "   python3 main.py --arm"
echo ""
echo -e "${YELLOW}5. 🌐 Access web dashboard:${NC}"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${RED}⚠️  IMPORTANT: REBOOT NOW for GPIO permissions!${NC}"
echo "   Run: sudo reboot"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
