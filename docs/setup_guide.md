# Setup Guide - Detailed Installation Instructions

## Prerequisites

- Raspberry Pi 4 (2GB+ RAM recommended)
- MicroSD card (32GB+ Class 10)
- USB Webcam
- PIR HC-SR501 sensor
- LEDs (green, red), Buzzer, resistors
- Breadboard and jumper wires
- Power supply (5V 3A USB-C)
- Internet connection

---

## 1. Raspberry Pi OS Installation

### Option A: Raspberry Pi Imager (Recommended)

```bash
# On your computer:
# 1. Download Raspberry Pi Imager: https://www.raspberrypi.com/software/
# 2. Select OS: Raspberry Pi OS (64-bit) Lite or Desktop
# 3. Select SD card
# 4. Click Write
# 5. Insert SD card into Raspberry Pi and boot
```

### Option B: Manual Installation

```bash
# Download Raspberry Pi OS
wget https://downloads.raspberrypi.org/raspios_lite_arm64/images/.../raspios.img.xz

# Flash to SD card (replace /dev/sdX with your SD card)
sudo dd if=raspios.img of=/dev/sdX bs=4M status=progress
sync
```

---

## 2. Initial Raspberry Pi Configuration

```bash
# First boot - run raspi-config
sudo raspi-config

# Configure:
# 1. System Options → Hostname (optional)
# 2. Interface Options → Camera → Enable (if using Pi Camera)
# 3. Interface Options → SSH → Enable (for remote access)
# 4. Localisation → Timezone → Your timezone
# 5. Finish and reboot
```

---

## 3. System Update

```bash
# Update package lists
sudo apt-get update

# Upgrade packages
sudo apt-get upgrade -y

# Install essential tools
sudo apt-get install -y git python3-pip python3-venv
```

---

## 4. Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone repository
git clone <repository-url> smart-security-system
cd smart-security-system
```

---

## 5. Run Automated Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (this may take 15-20 minutes)
bash setup.sh
```

**What setup.sh does:**
- Installs system dependencies (OpenCV, libraries)
- Creates Python virtual environment
- Installs Python packages from requirements.txt
- Sets up GPIO permissions
- Downloads YOLO model
- Creates necessary directories

---

## 6. Manual Setup (If Automated Fails)

### Install System Dependencies

```bash
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-opencv \
    libopencv-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    git \
    cmake
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Python Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Setup GPIO Permissions

```bash
sudo usermod -a -G gpio $USER
sudo usermod -a -G video $USER
# Logout and login again for changes to take effect
```

---

## 7. Hardware Assembly

### GPIO Pin Connections (BCM Numbering)

| Component | GPIO Pin | Physical Pin |
|-----------|----------|--------------|
| PIR Sensor (OUT) | GPIO 18 | Pin 12 |
| LED Green (Armed) | GPIO 27 | Pin 13 |
| LED Red (Alarm) | GPIO 17 | Pin 11 |
| Buzzer | GPIO 22 | Pin 15 |

### Wiring Instructions

#### PIR Sensor
```
PIR VCC  → Pi Pin 2 (5V)
PIR GND  → Pi Pin 6 (GND)
PIR OUT  → Pi Pin 12 (GPIO 18)
```

#### LEDs (with 220Ω resistors)
```
LED Green (+) → 220Ω → Pi Pin 13 (GPIO 27)
LED Green (-) → Pi Pin 9 (GND)

LED Red (+) → 220Ω → Pi Pin 11 (GPIO 17)
LED Red (-) → Pi Pin 9 (GND)
```

#### Buzzer
```
Buzzer (+) → Pi Pin 15 (GPIO 22)
Buzzer (-) → Pi Pin 14 (GND)
```

#### USB Camera
```
USB Camera → Any USB port on Raspberry Pi
```

**See [gpio_wiring.md](gpio_wiring.md) for detailed diagrams**

---

## 8. Configuration

### Create .env File

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env
```

### Required Configuration

```bash
# Telegram Bot (Required for alerts)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Camera (usually 0 for first USB camera)
CAMERA_INDEX=0

# GPIO Pins (if different from defaults)
PIR_PIN=18
LED_RED_PIN=17
LED_GREEN_PIN=27
BUZZER_PIN=22
```

### Get Telegram Credentials

1. **Create Bot:**
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Follow instructions to create bot
   - Copy the token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Chat ID:**
   - Search for [@userinfobot](https://t.me/userinfobot) in Telegram
   - Start chat and it will show your ID
   - Copy the number

---

## 9. Testing Components

### Test Camera

```bash
python3 -m src.hardware.camera
# Should show camera status and capture test frames
```

### Test GPIO Components

```bash
# Test PIR Sensor
python3 -m src.hardware.pir_sensor
# Move in front of sensor to test

# Test LEDs
python3 -m src.hardware.led_controller
# Should see LED test pattern

# Test Buzzer
python3 -m src.hardware.buzzer
# Should hear test beeps
```

### Test YOLO Model

```bash
python3 -c "from src.detection.yolo_detector import YOLODetector; d = YOLODetector(); d.load_model(); print('Model loaded successfully!')"
```

---

## 10. Running the System

### Manual Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run system
python3 main.py
```

### Start Armed

```bash
python3 main.py --arm
```

### Systemd Service (Auto-start on boot)

```bash
# Create service file
sudo nano /etc/systemd/system/security-system.service
```

```ini
[Unit]
Description=Smart Security System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/smart-security-system
Environment="PATH=/home/pi/smart-security-system/venv/bin"
ExecStart=/home/pi/smart-security-system/venv/bin/python3 main.py --arm
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable security-system
sudo systemctl start security-system

# Check status
sudo systemctl status security-system

# View logs
sudo journalctl -u security-system -f
```

---

## 11. Accessing the System

### Web Dashboard

```
http://[raspberry-pi-ip]:5000
```

Find Raspberry Pi IP:
```bash
hostname -I
```

### Telegram Bot

Send `/start` to your bot in Telegram

---

## Troubleshooting

### Camera Issues

```bash
# Check if camera is detected
ls /dev/video*

# Test with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAILED'); cap.release()"

# Check permissions
sudo usermod -a -G video $USER
```

### GPIO Permission Denied

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Reboot
sudo reboot
```

### Import Errors

```bash
# Verify virtual environment is activated
which python3
# Should show: /home/pi/smart-security-system/venv/bin/python3

# Reinstall packages
pip install --upgrade --force-reinstall -r requirements.txt
```

### Telegram Bot Not Responding

- Verify token is correct in .env
- Check internet connection
- Test token: `curl https://api.telegram.org/bot<TOKEN>/getMe`

---

## Next Steps

1. Test all components individually
2. Run system in disarmed mode first
3. Test arm/disarm via Telegram
4. Test motion detection
5. Test YOLO classification
6. Fine-tune thresholds if needed

---

**Need Help?** Check [README.md](../README.md) or create an issue.
