# API Reference

Complete reference for Flask API endpoints and Telegram bot commands.

---

## Flask Web API

Base URL: `http://[raspberry-pi-ip]:5000`

### Dashboard Endpoints

#### GET /

**Description:** Main dashboard page

**Response:** HTML page with live stream and controls

**Example:**
```
http://192.168.1.100:5000/
```

---

#### GET /video_feed

**Description:** MJPEG video stream

**Response:** Multipart MJPEG stream

**Headers:**
```
Content-Type: multipart/x-mixed-replace; boundary=frame
```

**Usage in HTML:**
```html
<img src="http://192.168.1.100:5000/video_feed" />
```

---

### API Endpoints

#### GET /api/status

**Description:** Get current system status

**Response:**
```json
{
  "state": "armed",
  "uptime": 3600,
  "cpu_usage": 65.2,
  "ram_usage": 45.8,
  "temperature": 52.3,
  "camera_fps": 14.5,
  "detections": {
    "total": 15,
    "person": 3,
    "animal": 12
  },
  "last_detection": "2024-10-27T14:30:25"
}
```

**Fields:**
- `state`: System state (disarmed/armed/alarm)
- `uptime`: Seconds since system start
- `cpu_usage`: CPU usage percentage
- `ram_usage`: RAM usage percentage
- `temperature`: CPU temperature (Celsius)
- `camera_fps`: Current camera FPS
- `detections`: Detection counters
- `last_detection`: Timestamp of last detection (ISO 8601)

---

#### POST /api/arm

**Description:** Arm the security system

**Response:**
```json
{
  "success": true,
  "message": "System armed",
  "state": "armed"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "System already armed",
  "state": "armed"
}
```

---

#### POST /api/disarm

**Description:** Disarm the security system

**Response:**
```json
{
  "success": true,
  "message": "System disarmed",
  "state": "disarmed"
}
```

---

#### GET /api/snapshot

**Description:** Get current camera frame

**Response:** JPEG image

**Headers:**
```
Content-Type: image/jpeg
```

**Example:**
```bash
curl http://192.168.1.100:5000/api/snapshot -o snapshot.jpg
```

---

#### GET /api/logs

**Description:** Get recent event logs

**Query Parameters:**
- `limit`: Number of entries (default: 20)
- `level`: Filter by level (DEBUG/INFO/WARNING/ERROR)

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-10-27T14:30:25",
      "level": "WARNING",
      "module": "detection",
      "message": "Person detected"
    },
    {
      "timestamp": "2024-10-27T14:25:10",
      "level": "INFO",
      "module": "system",
      "message": "System armed"
    }
  ],
  "count": 2
}
```

---

## Telegram Bot Commands

Bot Username: `@your_bot_name`

### Command List

#### /start

**Description:** Initialize bot and show welcome message

**Response:**
```
🔐 Smart Security System Bot

Welcome! I'm your security system control bot.

Available commands:
/help - Show this message
/arm - Arm the system
/disarm - Disarm the system
/status - Get system status
/snapshot - Get current camera view
/logs - View recent events

Use /help for detailed information.
```

---

#### /help

**Description:** Show detailed help message

**Response:**
```
🔐 Smart Security System - Help

Commands:
━━━━━━━━━━━━━━━━━━━━━━
/arm - Activate security monitoring
/disarm - Deactivate security monitoring
/status - View system information
/snapshot - Get current camera frame
/logs - View last 10 events

System States:
━━━━━━━━━━━━━━━━━━━━━━
🟢 DISARMED - System inactive
🟢 ARMED - Monitoring active
🔴 ALARM - Intrusion detected

Alert Levels:
━━━━━━━━━━━━━━━━━━━━━━
🚨 CRITICAL - Person detected
⚠️ HIGH - Person + Animal
ℹ️ LOW - Animal only
```

---

#### /arm

**Description:** Arm the security system

**Response (Success):**
```
✅ System Armed

Status: 🟢 ARMED
Monitoring: Active
Started: 2024-10-27 14:30:00

The system is now monitoring for intrusions.
You will receive alerts when motion is detected.
```

**Response (Already Armed):**
```
⚠️ System is already armed.

Current status: 🟢 ARMED
Armed since: 2024-10-27 14:25:00
```

---

#### /disarm

**Description:** Disarm the security system

**Response:**
```
✅ System Disarmed

Status: ⚪ DISARMED
Monitoring: Inactive
Stopped: 2024-10-27 15:00:00

The system is no longer monitoring.
Use /arm to reactivate.
```

---

#### /status

**Description:** Get comprehensive system status

**Response:**
```
🔐 System Status

State: 🟢 ARMED
Uptime: 2 hours, 15 minutes

📊 Performance:
━━━━━━━━━━━━━━━━━━━━━━
CPU: 65.2%
RAM: 45.8%
Temp: 52.3°C
Camera: 14.5 FPS

📈 Statistics:
━━━━━━━━━━━━━━━━━━━━━━
Total Detections: 15
  👤 Person: 3
  🐾 Animal: 12

Last Detection: 5 minutes ago

📡 Network:
━━━━━━━━━━━━━━━━━━━━━━
Dashboard: http://192.168.1.100:5000
```

---

#### /snapshot

**Description:** Get current camera frame

**Response:** Photo with caption

**Caption:**
```
📸 Snapshot
Time: 2024-10-27 15:05:30
State: 🟢 ARMED
```

---

#### /logs

**Description:** View recent event logs

**Response:**
```
📋 Recent Events (Last 10)

🕐 15:05 [WARNING] Detection: Person detected
🕐 15:03 [INFO] System: Alarm cleared
🕐 15:00 [WARNING] Detection: Motion detected
🕐 14:55 [INFO] Alert: Message sent to Telegram
🕐 14:50 [INFO] System: System armed
🕐 14:45 [INFO] System: System initialized
🕐 14:40 [DEBUG] Camera: Capture started
🕐 14:35 [INFO] Hardware: PIR sensor initialized
🕐 14:30 [INFO] System: Application started
🕐 14:25 [DEBUG] Config: Configuration loaded
```

---

## Alert Messages

### CRITICAL Alert (Person Detected)

```
🚨 CRITICAL ALERT

Type: 👤 Person Detected
Time: 2024-10-27 15:10:30
Confidence: 92.5%

Immediate action recommended!

[Attached Photo]
```

### HIGH Alert (Person + Animal)

```
⚠️ HIGH PRIORITY ALERT

Type: 👤 Person + 🐾 Animal
Time: 2024-10-27 15:12:15
Confidence: Person 89%, Animal 76%

[Attached Photo]
```

### LOW Alert (Animal Only)

```
ℹ️ LOW PRIORITY

Type: 🐾 Animal Detected (Cat)
Time: 2024-10-27 15:15:00
Confidence: 82.3%

[Attached Photo]
```

---

## Error Responses

### API Errors

#### 404 Not Found
```json
{
  "error": "Endpoint not found",
  "status": 404
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Camera not available",
  "status": 500
}
```

### Telegram Errors

#### Unauthorized User
```
⛔ Access Denied

You are not authorized to use this bot.
Contact system administrator.
```

#### System Error
```
❌ Error

Unable to execute command.
Reason: Camera not available

Please try again later or contact support.
```

---

## Rate Limiting

- **API Endpoints**: No rate limit (local network)
- **Telegram Alerts**: 30-second cooldown between alerts (configurable)
- **Telegram Commands**: No limit

---

## Authentication

- **Flask API**: No authentication by default (local network only)
- **Telegram Bot**: Authenticated via chat_id (configured in .env)

---

## WebSocket Support

Currently not implemented. All updates via polling or page refresh.

**Future Enhancement:** WebSocket for real-time dashboard updates.

---

## Example Usage

### Python

```python
import requests

# Get status
response = requests.get('http://192.168.1.100:5000/api/status')
status = response.json()
print(f"System state: {status['state']}")

# Arm system
response = requests.post('http://192.168.1.100:5000/api/arm')
print(response.json()['message'])

# Get snapshot
response = requests.get('http://192.168.1.100:5000/api/snapshot')
with open('snapshot.jpg', 'wb') as f:
    f.write(response.content)
```

### JavaScript (Dashboard)

```javascript
// Get status
fetch('/api/status')
  .then(response => response.json())
  .then(data => {
    console.log('State:', data.state);
    console.log('CPU:', data.cpu_usage);
  });

// Arm system
fetch('/api/arm', { method: 'POST' })
  .then(response => response.json())
  .then(data => alert(data.message));
```

### cURL

```bash
# Get status
curl http://192.168.1.100:5000/api/status

# Arm system
curl -X POST http://192.168.1.100:5000/api/arm

# Get snapshot
curl http://192.168.1.100:5000/api/snapshot -o snapshot.jpg

# Get logs
curl http://192.168.1.100:5000/api/logs?limit=5
```

---

**Last Updated:** 2024-10-27
