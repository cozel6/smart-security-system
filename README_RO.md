# 🔐 Sistem de Securitate Inteligent
## Detectare Automată OM vs ANIMAL cu Alertare Remote

Sistem inteligent de securitate care rulează pe Raspberry Pi 4, folosind viziune computerizată și AI pentru a detecta intruziuni, diferenția între oameni și animale, și trimite alerte instant prin Telegram.

---

## ✨ Funcționalități

- **Detectare Dual**: Senzor PIR + detectare mișcare OpenCV (reduce false positive)
- **Clasificare AI**: YOLOv5 distinge între oameni și animale
- **Alerte Inteligente**:
  - 🚨 CRITIC: Persoană detectată (alertă imediată)
  - ⚠️ RIDICAT: Persoană + Animal
  - ℹ️ SCĂZUT: Doar animal
- **Control Remote**: Control complet prin bot Telegram
- **Streaming Live**: Dashboard web cu video în timp real
- **Procesare Locală**: Tot AI-ul rulează pe dispozitiv, fără cloud

---

## 🛠️ Componente Hardware

| Componentă | Specificații | Funcție |
|------------|-------------|---------|
| **Microcontroller** | Raspberry Pi 4 (2GB RAM) | Procesor principal, rulează AI |
| **Cameră** | USB Webcam | Captură video |
| **Senzor Mișcare** | PIR HC-SR501 | Detectare mișcare infraroșu |
| **Storage** | MicroSD 32GB Class 10 | Stocare OS și date |
| **LED-uri** | Verde + Roșu 5mm | Indicatori status |
| **Buzzer** | Activ 5V | Alarmă sonoră |
| **Alimentare** | 5V/3A USB-C | Adaptor curent |

---

## 📋 Stack Tehnologic

- **Limbaj**: Python 3.9+
- **Viziune**: OpenCV 4.8
- **AI**: Ultralytics YOLOv5 nano
- **Server Web**: Flask 3.0
- **Bot**: python-telegram-bot 20.6
- **GPIO**: RPi.GPIO 0.7

---

## 🚀 Ghid Rapid

### 1. Clonare Repository

```bash
git clone <repository-url>
cd smart-security-system
```

### 2. Rulare Script Setup

```bash
bash setup.sh
```

Acest script va:
- Instala dependențe sistem
- Crea mediu virtual Python
- Instala pachete Python
- Configura permisiuni GPIO
- Descărca model YOLO

### 3. Configurare Mediu

```bash
cp .env.example .env
nano .env
```

Editează `.env` cu credențialele tale:
- `TELEGRAM_BOT_TOKEN` - Obține de la [@BotFather](https://t.me/BotFather)
- `TELEGRAM_CHAT_ID` - Obține de la [@userinfobot](https://t.me/userinfobot)

### 4. Pornire Sistem

```bash
python3 main.py --arm
```

Accesează dashboard-ul la: `http://[raspberry-pi-ip]:5000`

---

## 📱 Comenzi Telegram

| Comandă | Descriere |
|---------|-----------|
| `/start` | Inițializează bot-ul |
| `/help` | Afișează lista comenzi |
| `/arm` | Armează sistemul |
| `/disarm` | Dezarmează sistemul |
| `/status` | Obține status sistem |
| `/snapshot` | Capturează frame curent |
| `/logs` | Vezi evenimente recente |

---

## 🌐 Dashboard Web

Accesează la `http://[raspberry-pi-ip]:5000`

Funcții:
- Stream video MJPEG live
- Status sistem (armat/dezarmat)
- Controale arm/disarm
- Detectări recente
- Metrici sistem (CPU, RAM, temperatură)

---

## 🏗️ Arhitectură

```
┌─────────────────────────────────────────────────────────────┐
│                    System Manager                            │
│                  (Orchestrator Principal)                    │
└─────────────────────────────────────────────────────────────┘
         │                │                │                │
    ┌────▼────┐     ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
    │ Hardware│     │Detectare│     │  Alerte │     │Streaming│
    └─────────┘     └─────────┘     └─────────┘     └─────────┘
    │  │  │  │      │    │          │    │          │    │
    │  │  │  │      │    │          │    │          │    │
   CAM PIR LED BZ   MOT YOLO      TELE ALERT       WEB VIDEO
```

**Model Threading:**
- Thread 1: Captură cameră (continuu)
- Thread 2: Pipeline detectare (PIR → Motion → YOLO)
- Thread 3: Manager alerte (procesare queue)
- Thread 4: Bot Telegram (polling)
- Thread 5: Server Flask (dashboard web)

---

## 📊 Metrici Performanță

| Metrică | Target | Actual |
|---------|--------|--------|
| **Timp Răspuns** | < 3 sec | TBD |
| **Streaming FPS** | 10-15 FPS | TBD |
| **Inferență YOLO** | 200-300ms | TBD |
| **Utilizare CPU** | < 85% | TBD |
| **Utilizare RAM** | ~700MB | TBD |
| **Acuratețe Detectare** | 75-85% | TBD |

---

## 📚 Documentație

- [English README](README.md) - Documentație completă în engleză
- [Documentație Proiect](PROJECT_DOCUMENTATION.md) - Plan complet proiect cu milestone-uri
- [Arhitectură](docs/architecture.md) - Diagrame arhitectură sistem
- [Ghid Setup](docs/setup_guide.md) - Instrucțiuni instalare detaliate
- [Referință API](docs/api_reference.md) - Endpoint-uri API și comenzi
- [Schema GPIO](docs/gpio_wiring.md) - Diagramă conexiuni hardware

---

## 🧪 Testare

Rulare teste:

```bash
pytest tests/ -v
```

Teste individuale:

```bash
pytest tests/test_hardware.py -v
pytest tests/test_detection.py -v
pytest tests/test_alerts.py -v
```

---

## 🐛 Rezolvare Probleme

### Camera nu funcționează
```bash
# Test cameră
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAILED')"
```

### Permisiune GPIO refuzată
```bash
sudo usermod -a -G gpio $USER
# Necesită reboot
```

### Model YOLO lipsește
```bash
# Modelul se descarcă automat la prima rulare
# Sau manual:
cd models
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt
```

---

## 📅 Milestone-uri Proiect

### Milestone 1: Prezentare (25 Oct 2024)
- ✅ Documentație completă
- ✅ Prezentare PowerPoint
- ✅ Schema bloc sistem

### Milestone 2: Setup Hardware (28 Oct - 3 Nov)
- Hardware asamblat
- Environment Python configurat
- Test componente

### Milestone 3: Motion Detection (4-10 Nov)
- Detectare mișcare dual-mode (PIR + OpenCV)
- Web streaming Flask
- Dashboard basic

### Milestone 4: Telegram Integration (11-17 Nov)
- Bot Telegram funcțional
- Comenzi control (arm/disarm/status)
- Alerte cu poze

### Milestone 5: YOLO Detection (18 Nov - 1 Dec)
- Clasificare OM vs ANIMAL
- Bounding boxes pe stream
- Alerte contextuale

### Milestone 6: Optimizare (2-8 Dec)
- Fine-tuning thresholds
- UI/UX dashboard
- Logging persistent

### Milestone 7: Testing & Finalizare (9 Dec - 15 Ian)
- Testare extensivă
- Documentație tehnică finală
- Video demo
- Prezentare finală

---

## 👥 Echipă

**Echipă Proiect:** 2 dezvoltatori
**Timeline:** Octombrie 2024 - Ianuarie 2025 (12 săptămâni)
**Instituție:** Proiect Facultate MIPE

---

## 📄 Licență

Acest proiect este pentru scopuri educaționale.

---

## 🙏 Mulțumiri

- YOLOv5 de Ultralytics
- Comunitatea OpenCV
- Raspberry Pi Foundation
- Python Telegram Bot library

---

## 📞 Suport

Pentru probleme și întrebări:
- Creați un issue în repository
- Consultați documentația din `docs/`
- Revedeți secțiunea de troubleshooting

---

**Realizat cu ❤️ pentru Proiectul Facultății MIPE**
