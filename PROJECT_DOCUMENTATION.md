# SISTEM DE SECURITATE INTELIGENT
## Detectare Automată OM vs ANIMAL cu Alertare Remote

**Echipă:** 2 persoane  
**Perioadă:** 25 Octombrie 2024 - Ianuarie 2025 (12 săptămâni)  
**Platform:** Raspberry Pi 4 2GB

---

## 📦 LISTA COMPONENTE

| Componentă | Specificații | Funcție |
|------------|-------------|---------|
| **Microcontroller** | Raspberry Pi 4 2GB | Procesor central, rulare algoritmi AI |
| **Cameră** | Hama USB Webcam (existent) | Captură video, detectare vizuală |
| **Senzor Mișcare** | PIR HC-SR501 | Detectare mișcare infraroșu |
| **Storage** | MicroSD 32GB Class 10 | Sistem operare + date |
| **Alimentare** | Adaptor 5V/3A USB-C | Power supply |
| **LED Roșu** | 5mm standard | Indicator alarmă activă |
| **LED Verde** | 5mm standard | Indicator sistem armed |
| **Buzzer** | Activ 5V | Alarmă sonoră locală |
| **Rezistențe** | 220Ω (20 buc) | Protecție LED-uri |
| **Breadboard** | 170 puncte | Prototipare circuite |
| **Fire jumper** | Mama-Tată 30cm (40 buc) | Conexiuni electronice |

---

## 🎯 CE FACEM ȘI DE CE?

### Scopul Proiectului
Sistem automat de securitate care **detectează intruziuni** și **diferențiază între oameni și animale**, trimițând alerte instant pe Telegram.

### De ce aceste tehnologii?

#### 🔧 **Raspberry Pi 4 2GB**
- **Putere:** 4 nuclee (Cortex-A72) → suficient pentru AI în timp real
- **RAM:** 2GB → poate rula YOLO + OpenCV simultan
- **GPIO:** 40 pini → control senzori și LED-uri
- **Comunitate:** Documentație excelentă, suport vast

#### 🐍 **Python 3.9+**
- **Ecosistem ML:** OpenCV, YOLO, TensorFlow
- **Rapid development:** Prototyping mai rapid decât C++
- **Librării mature:** `python-telegram-bot`, `Flask`, `RPi.GPIO`

#### 🤖 **YOLOv5 nano (AI)**
- **Optimizat edge:** Funcționează pe dispozitive mici
- **Acuratețe bună:** 75-85% în condiții normale
- **Viteze acceptabile:** 3-5 FPS pe Raspberry Pi
- **Pre-antrenat:** COCO dataset cu 80 clase (inclusiv oameni + 9 animale)

#### 💬 **Telegram Bot API**
- **Gratuit:** Fără costuri, fără limite
- **Instant push:** Notificări în < 3 secunde
- **Simplu:** API documentat excelent
- **Securitate:** Comunicare encriptată

#### 🌐 **Flask + MJPEG**
- **Lightweight:** Streaming video fără overhead mare
- **Cross-platform:** Funcționează în orice browser
- **Latență mică:** ~300-500ms în WiFi local

---

## 📅 MILESTONE-URI (7 ETAPE)

### **MILESTONE 1: Prezentare Documentație** 
📆 **25 Octombrie 2024** (Săptămâna 1)

**🎯 Obiectiv:** Prezentarea proiectului, tehnologiilor și planificării

#### Deliverables:
- ✅ Documentație completă (concept + arhitectură)
- ✅ Prezentare PowerPoint (10-12 slide-uri)
- ✅ Schema bloc sistem
- ✅ Distribuție clară task-uri

#### 👥 Împărțire Muncă:

**Persoana 1 - 2-3 task-uri:**
1. **Slide 1-3:** Introducere + Obiective proiect
2. **Slide 4-6:** Stack tehnologic (de ce Python, YOLO, Telegram)
3. **Slide 7-8:** Timeline milestone-uri (tabel simplu cu deadline-uri)

**Persoana 2:**
1. **Slide 9-10:** Lista componente + schema GPIO
2. **Slide 11-12:** Arhitectură sistem (flowchart: PIR→OpenCV→YOLO→Telegram)
3. **Q&A prep:** Pregătire răspunsuri la întrebări posibile

#### 📊 Structură Prezentare Recomandată:
```
Slide 1: Titlu + Echipă
Slide 2: Problema (de ce e necesar sistemul)
Slide 3: Soluția (ce facem)
Slide 4: Hardware (componente + Raspberry Pi)
Slide 5: Software Stack (Python, YOLO, Telegram)
Slide 6: Arhitectură (diagram cu flow)
Slide 7: Funcționalități cheie (dual detection, alerte smart)
Slide 8: Timeline (7 milestone-uri, 12 săptămâni)
Slide 9: Metrici așteptate (FPS, acuratețe, latență)
Slide 10: Riscuri + Mitigare
Slide 11-12: Demo plan + Întrebări
```

**⏱️ Durată prezentare:** 10-12 minute  
**✅ Criterii succes:** Echipa înțelege proiectul, profesorul aprobă planul

---

### **MILESTONE 2: Setup Hardware & Environment**
📆 **28 Oct - 3 Nov 2024** (Săptămâna 2)

**🎯 Obiectiv:** Hardware complet asamblat + Python environment funcțional

#### Task-uri Împărțite:

**Persoana 1:**
- Instalare Raspberry Pi OS
- Setup Python 3.9+ (virtualenv)
- Instalare librării: `opencv-python`, `Flask`, `RPi.GPIO`
- Test cameră USB (captură frame-uri simple)

**Persoana 2:**
- Asamblare circuit pe breadboard
- Conectare PIR, LED-uri, buzzer la GPIO
- Test componente individuale (LED blink, buzzer test)
- Documentare conexiuni + fotografii

#### ✅ Criterii Succes:
- Camera captează video 640x480 @ 15 FPS
- PIR detectează mișcare (print în terminal)
- LED-uri și buzzer controlabile din Python
- Circuit fotografiat și schema documentată

---

### **MILESTONE 3: Motion Detection**
📆 **4-10 Nov 2024** (Săptămâna 3)

**🎯 Obiectiv:** Detectare mișcare dual-mode (PIR + OpenCV)

#### Task-uri Împărțite:

**Persoana 1:**
- Implementare motion detection OpenCV (Background Subtraction MOG2)
- Filtrare false positive (threshold contur minim)
- Integrare PIR ca trigger hardware
- Logging evenimente (timestamp, tip detectare)

**Persoana 2:**
- Web streaming Flask cu MJPEG
- Dashboard HTML/CSS responsive
- Overlay status (ARMED/DISARMED, timestamp)
- Test condiții diferite (zi, noapte)

#### ✅ Criterii Succes:
- PIR trigger + OpenCV confirmă mișcare
- Streaming accesibil la `http://[IP]:5000`
- False positive <20% (vs PIR singur)
- LED roșu + buzzer activare la detectare

---

### **MILESTONE 4: Telegram Integration**
📆 **11-17 Nov 2024** (Săptămâna 4)

**🎯 Obiectiv:** Control și alertare remote prin Telegram

#### Task-uri Împărțite:

**Persoana 1:**
- Creare Telegram Bot (BotFather)
- Implementare comenzi: `/arm`, `/disarm`, `/status`
- Trimitere alerte cu poze la detectare
- Sistem cooldown 30s între alerte

**Persoana 2:**
- Implementare comenzi: `/snapshot`, `/logs`
- Status sistem (uptime, CPU, RAM, temperatură)
- Salvare snapshots cu timestamp
- Formatare mesaje (emoji, structură clară)

#### ✅ Criterii Succes:
- Toate comenzile funcționează
- Alerte ajung în <3 sec de la detectare
- Poze clare atașate notificărilor
- Sistem controlabil 100% remote

---

### **MILESTONE 5: YOLO Object Detection**
📆 **18 Nov - 1 Dec 2024** (Săptămâni 5-6)

**🎯 Obiectiv:** Clasificare inteligentă OM vs ANIMAL

#### Task-uri Împărțite:

**Persoana 1:**
- Instalare Ultralytics YOLOv5
- Download model YOLOv5n (nano - 3.8MB)
- Optimizare inferență (rezoluție 416x416)
- Detectare Person (class 0) + animale (class 15-23)

**Persoana 2:**
- Desenare bounding boxes pe stream
- Clasificare alerte: CRITICAL (om), LOW (animal), HIGH (ambele)
- Optimizare: skip frames (1 din 3), threading
- Benchmark: măsurare FPS, CPU, acuratețe

#### ✅ Criterii Succes:
- YOLO rulează la 3-5 FPS
- Distinge corect om vs animal (75-85% acuratețe)
- Alerte contextualizate în Telegram
- Bounding boxes live pe stream

---

### **MILESTONE 6: Optimizare & Polish**
📆 **2-8 Dec 2024** (Săptămâna 7)

**🎯 Obiectiv:** Fine-tuning performanță și interfață

#### Task-uri Împărțite:

**Persoana 1:**
- Fine-tuning thresholds YOLO (confidence 0.5→0.6)
- Îmbunătățire acuratețe în lumină slabă
- Profiling cod (identificare bottlenecks)
- Reducere CPU usage (<80%)

**Persoana 2:**
- UI/UX dashboard (butoane arm/disarm în web)
- Logging persistent (SQLite sau JSON)
- Statistici zilnice (număr detectări, tipuri)
- Cleanup cod + comentarii complete

#### ✅ Criterii Succes:
- False positive <10%
- CPU usage <85% în timpul detectării
- Cod curat, bine documentat
- Dashboard funcțional și estetic

---

### **MILESTONE 7: Testing & Finalizare**
📆 **9 Dec 2024 - 15 Ian 2025** (Săptămâni 8-12)

**🎯 Obiectiv:** Sistem robust, testat extensiv, gata de prezentare

#### Task-uri Împărțite (Ambii):

**Săptămâna 8-9 (Testing):**
- Test scenarii: zi, noapte, multiple persoane
- Edge cases: ocluzie parțială, obiecte mici, animale rapide
- Test stabilitate 24/7 (rulare continuă 6+ ore)
- Bug fixing prioritar

**Săptămâna 10-11 (Documentație):**
- Documentație tehnică finală (25-30 pagini)
- Schema electrică Fritzing
- Flowcharts sistem (draw.io sau Lucidchart)
- Screenshots funcționalități + rezultate teste

**Săptămâna 12 (Prezentare):**
- Video demo 5-7 minute (scenarii: zi/noapte, om/animal)
- Prezentare PowerPoint finală (20 slide-uri)
- Pregătire Q&A (întrebări posibile)
- Rehearsal prezentare (timing, claritate)

#### ✅ Criterii Succes:
- Sistem stabil >6 ore continuous
- Video demo profesional (montaj, voiceover)
- Documentație completă cu toate diagramele
- Prezentare clară, sub 15 minute

---

## 📊 METRICI DE PERFORMANȚĂ AȘTEPTATE

| Metric | Target | Măsurare |
|--------|--------|----------|
| **Response time** | <3 sec | PIR trigger → Telegram alert |
| **FPS streaming** | 10-15 FPS | 640×480 rezoluție |
| **YOLO inference** | 200-300ms | Per frame (416x416) |
| **CPU usage** | <85% | În timpul detectării |
| **RAM usage** | ~700MB | Cu YOLO loaded |
| **Acuratețe YOLO** | 75-85% | Lumină naturală |
| **False positive** | <10% | Cu dual detection (PIR+OpenCV) |

---

## 🎓 NOTA AȘTEPTATĂ

**9-10** cu toate milestone-urile îndeplinite:
- **8-9:** Core features funcționale (motion + Telegram + streaming)
- **10:** YOLO om/animal funcțional + documentație excelentă
- **Bonus:** Optimizări avansate, prezentare impecabilă

---

## 📌 STRUCTURA PROIECTULUI

Acest repository conține:

```
smart-security-system/
├── config/              # Configurări (settings, GPIO pins)
├── src/                 # Cod sursă
│   ├── hardware/        # Interfețe hardware (cameră, senzori, LED-uri)
│   ├── detection/       # Algoritmi detectare (motion, YOLO)
│   ├── alerts/          # Sistem alerte (Telegram, alert manager)
│   ├── streaming/       # Server web (Flask, video streaming)
│   ├── utils/           # Funcții utilitare
│   └── core/            # Orchestrator sistem
├── web/                 # Dashboard web (HTML, CSS, JS)
├── docs/                # Documentație tehnică
├── tests/               # Teste unitare
├── models/              # Modele AI (YOLO)
├── logs/                # Fișiere log
└── snapshots/           # Capturi detectări
```

---

## 🚀 COMENZI RAPIDE

```bash
# Setup inițial
bash setup.sh

# Pornire sistem (manual)
python3 main.py

# Pornire sistem armat
python3 main.py --arm

# Rulare teste
pytest tests/ -v

# Verificare cameră
python3 -m src.hardware.camera

# Verificare GPIO
python3 -m src.hardware.pir_sensor
```

---

**📅 Următorul checkpoint:** Vezi README.md pentru instrucțiuni detaliate de utilizare

---

**Documentație creată:** 27 Octombrie 2024
**Ultima actualizare:** 27 Octombrie 2024
