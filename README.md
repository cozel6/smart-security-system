# 🔐 Smart Security System
## AI-Powered Intrusion Detection with Person vs Animal Classification

An intelligent security system running on Raspberry Pi 4 that uses computer vision and AI to detect intrusions, differentiate between humans and animals, and send instant alerts via Telegram.

---

## ✨ Features

- **Dual Motion Detection**: PIR sensor + OpenCV motion detection for reduced false positives
- **AI Classification**: YOLOv5 distinguishes between people and animals
- **Smart Alerts**:
  - 🚨 CRITICAL: Person detected (immediate alert)
  - ⚠️ HIGH: Person + Animal detected
  - ℹ️ LOW: Animal only
- **Remote Control**: Full system control via Telegram bot
- **Live Streaming**: Web dashboard with real-time video feed
- **Local Processing**: All AI runs on-device, no cloud dependency

---

## 🛠️ Hardware Components

| Component | Specification | Purpose |
|-----------|--------------|---------|
| **Microcontroller** | Raspberry Pi 4 (2GB RAM) | Main processor, runs AI |
| **Camera** | USB Webcam | Video capture |
| **Motion Sensor** | PIR HC-SR501 | Infrared motion detection |
| **Storage** | MicroSD 32GB Class 10 | OS and data storage |
| **LEDs** | Green + Red 5mm | Status indicators |
| **Buzzer** | Active 5V | Audio alarm |
| **Power Supply** | 5V/3A USB-C | Power adapter |

---

## 📋 Software Stack

- **Language**: Python 3.9+
- **Computer Vision**: OpenCV 4.8
- **AI Framework**: Ultralytics YOLOv5 nano
- **Web Server**: Flask 3.0
- **Bot Framework**: python-telegram-bot 20.6
- **GPIO Control**: RPi.GPIO 0.7

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd smart-security-system
```

### 2. Run Setup Script

```bash
bash setup.sh
```

This will:
- Install system dependencies
- Create Python virtual environment
- Install Python packages
- Setup GPIO permissions
- Download YOLO model

### 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

Edit `.env` with your credentials:
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/BotFather)
- `TELEGRAM_CHAT_ID` - Get from [@userinfobot](https://t.me/userinfobot)

### 4. Run System

```bash
python3 main.py --arm
```

Access web dashboard at: `http://[raspberry-pi-ip]:5000`

---

## 📱 Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot |
| `/help` | Show command list |
| `/arm` | Arm the system |
| `/disarm` | Disarm the system |
| `/status` | Get system status |
| `/snapshot` | Get current camera frame |
| `/logs` | View recent events |

---

## 🌐 Web Dashboard

Access at `http://[raspberry-pi-ip]:5000`

Features:
- Live MJPEG video stream
- System status (armed/disarmed)
- Arm/Disarm controls
- Recent detections
- System metrics (CPU, RAM, temp)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      System Manager                          │
│                   (Main Orchestrator)                        │
└─────────────────────────────────────────────────────────────┘
         │                │                │                │
    ┌────▼────┐     ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
    │ Hardware│     │Detection│     │  Alerts │     │Streaming│
    └─────────┘     └─────────┘     └─────────┘     └─────────┘
    │  │  │  │      │    │          │    │          │    │
    │  │  │  │      │    │          │    │          │    │
   CAM PIR LED BZ   MOT YOLO      TELE ALERT       WEB VIDEO
```

**Threading Model:**
- Thread 1: Camera capture (continuous)
- Thread 2: Detection pipeline (PIR → Motion → YOLO)
- Thread 3: Alert manager (queue processing)
- Thread 4: Telegram bot (polling)
- Thread 5: Flask server (web dashboard)

---

## 📊 Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| **Response Time** | < 3 sec | TBD |
| **Streaming FPS** | 10-15 FPS | TBD |
| **YOLO Inference** | 200-300ms | TBD |
| **CPU Usage** | < 85% | TBD |
| **RAM Usage** | ~700MB | TBD |
| **Detection Accuracy** | 75-85% | TBD |

---

## 📚 Documentation

- [Romanian README](README_RO.md) - Full documentation in Romanian
- [Project Documentation](PROJECT_DOCUMENTATION.md) - Complete project plan
- [Architecture](docs/architecture.md) - System architecture diagrams
- [Setup Guide](docs/setup_guide.md) - Detailed installation instructions
- [API Reference](docs/api_reference.md) - API endpoints and commands
- [GPIO Wiring](docs/gpio_wiring.md) - Hardware connection diagram

---

## 🧪 Testing

Run unit tests:

```bash
pytest tests/ -v
```

Run individual test suites:

```bash
pytest tests/test_hardware.py -v
pytest tests/test_detection.py -v
pytest tests/test_alerts.py -v
```

---

## 🐛 Troubleshooting

### Camera not working
```bash
# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAILED')"
```

### GPIO permission denied
```bash
sudo usermod -a -G gpio $USER
# Reboot required
```

### YOLO model not found
```bash
# Model will auto-download on first run
# Or manually download:
cd models
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt
```

---

## 👥 Team

**Project Team:** 2 developers
**Timeline:** October 2024 - January 2025 (12 weeks)
**Institution:** Faculty Project

---

## 📄 License

This project is for educational purposes.

---

## 🙏 Acknowledgments

- YOLOv5 by Ultralytics
- OpenCV community
- Raspberry Pi Foundation
- Python Telegram Bot library

---

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check documentation in `docs/`
- Review troubleshooting section

---

**Made with ❤️ for MIPE Faculty Project**
