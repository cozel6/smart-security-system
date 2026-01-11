# Hardware Setup Guide

## Overview

Acest sistem de securitate folosește următoarele componente hardware pe Raspberry Pi:

- **LED Verde (GPIO 27)** - Indicator sistem armat
- **LED Roșu (GPIO 17)** - Indicator alarmă vizuală
- **Buzzer Activ (GPIO 23)** - Alarmă sonoră
- **Senzor PIR HC-SR501 (GPIO 24)** - Detectare mișcare

## Specificații Hardware

### LED-uri
- **Tensiune**: 3.3V (conectare directă la GPIO)
- **Curent**: ~20mA
- **Rezistor**: 220Ω (OBLIGATORIU - altfel LED-urile se ard!)

### Buzzer Activ
- **Tip**: Active Buzzer (are oscilator intern)
- **Tensiune**: 3.3V-5V
- **Pin**: GPIO 23

### Senzor PIR HC-SR501
- **Tensiune**: 5V (alimentare din pin 5V)
- **Output**: 3.3V (HIGH) / 0V (LOW)
- **Rază detectare**: până la 7 metri
- **Unghi detectare**: ~110 grade
- **Calibrare**: 10 secunde la pornire

## Pinout Raspberry Pi (BCM Numbering)

```
Component       GPIO Pin    Physical Pin    Notes
─────────────────────────────────────────────────
PIR Sensor         24           18         Input (motion detection)
LED Red            17           11         Output (alarm indicator)
LED Green          27           13         Output (armed indicator)
Buzzer             23           16         Output (alarm sound)
```

## Schema de Conexiuni

### Breadboard Setup

**Folosim un breadboard 170 puncte împărțit în 2 părți:**

#### Partea DREAPTA (coloanele f-j):
- LED Verde + Rezistor 220Ω
- LED Roșu + Rezistor 220Ω
- Buzzer

#### Partea STÂNGĂ (coloanele a-b):
- Conectiuni PIR Sensor (prin cabluri mamă-tată)

### Conexiuni LED Verde (Armed Indicator)

```
GPIO 27 (Pin 13) ──→ Rezistor 220Ω ──→ LED (Anod +) ──→ LED (Catod -) ──→ GND
```

### Conexiuni LED Roșu (Alarm Indicator)

```
GPIO 17 (Pin 11) ──→ Rezistor 220Ω ──→ LED (Anod +) ──→ LED (Catod -) ──→ GND
```

### Conexiuni Buzzer

```
GPIO 23 (Pin 16) ──→ Buzzer (+)
GND              ──→ Buzzer (-)
```

### Conexiuni PIR Sensor

```
5V  (Pin 2)     ──→ PIR VCC (roșu)
GND (Pin 6)     ──→ PIR GND (negru)
GPIO 24 (Pin 18)──→ PIR OUT (galben/alb)
```

**IMPORTANT**: PIR se conectează prin breadboard cu cabluri mamă-tată (dacă nu ai cabluri mamă-mamă).

## Configurare Software

### 1. Instalare Dependințe RPi.GPIO

```bash
pip install RPi.GPIO
```

### 2. Configurare .env

Copiază `.env.example` la `.env` și configurează:

```bash
# GPIO Pin Configuration
PIR_PIN=24
LED_RED_PIN=17
LED_GREEN_PIN=27
BUZZER_PIN=23

# Enable Hardware
USE_HARDWARE=True

# PIR Auto-Arm Settings
PIR_AUTO_ARM_ENABLED=True
PIR_NO_MOTION_TIMEOUT=120  # 2 minutes
```

### 3. Permisiuni GPIO

Asigură-te că utilizatorul are permisiuni pentru GPIO:

```bash
sudo usermod -a -G gpio $USER
```

Apoi restart sesiunea sau reboot.

## Funcționare

### Comportament LED-uri

| Stare Sistem | LED Verde | LED Roșu |
|--------------|-----------|----------|
| DISARMED     | OFF       | OFF      |
| ARMED        | ON        | OFF      |
| ALARM        | OFF       | BLINK    |

### Comportament Buzzer

| Event                    | Pattern Buzzer |
|--------------------------|----------------|
| System ARM (manual)      | - (silent)     |
| System ARM (PIR auto)    | 1 beep         |
| System DISARM (manual)   | - (silent)     |
| System DISARM (PIR auto) | 2 beeps        |
| Unknown Person Detected  | PULSE (0.5s on, 0.5s off) |
| Motion (while armed)     | Short beep (0.05s) |

### Comportament PIR Auto-Arm/Disarm

Când `PIR_AUTO_ARM_ENABLED=True`:

1. **Detectare mișcare** → Sistem se ARMEAZĂ automat
   - LED verde se aprinde
   - Camera pornește
   - Buzzer: 1 beep

2. **Sistem armat** → Monitorizare continuă
   - La fiecare mișcare detectată, timer-ul se resetează

3. **Fără mișcare timp de 2 minute** → Sistem se DEZARMEAZĂ automat
   - LED verde se stinge
   - Camera se oprește
   - Buzzer: 2 beeps

### Comportament Alarmă (Unknown Person)

Când se detectează o persoană necunoscută:

1. LED roșu CLIPEȘTE (0.5s on, 0.5s off)
2. Buzzer PULSEAZĂ (0.5s on, 0.5s off) - pattern ALTERNATIV
3. Alarmă continuă până la clear_alarm()

## Testare Hardware

### Test LED-uri

```bash
python3 -c "
from src.hardware import LEDController
led = LEDController()
led.start()
led.test_pattern()
led.stop()
"
```

### Test Buzzer

```bash
python3 -c "
from src.hardware import Buzzer
buzzer = Buzzer()
buzzer.start()
buzzer.test()
buzzer.stop()
"
```

### Test PIR Sensor

```bash
python3 -c "
from src.hardware import PIRSensor
import time

def on_motion(pin):
    print(f'MOTION DETECTED on pin {pin}!')

pir = PIRSensor()
pir.start(callback=on_motion)
print('Waiting for motion... (press Ctrl+C to stop)')
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pir.stop()
"
```

## Troubleshooting

### LED-ul nu se aprinde
- Verifică polaritatea (anod + la rezistor, catod - la GND)
- Verifică rezistorul (220Ω)
- Testează LED-ul direct între 3.3V și GND (cu rezistor!)

### Buzzer nu sună
- Verifică polaritatea (+ la GPIO, - la GND)
- Testează buzzer-ul direct între 3.3V și GND

### PIR nu detectează mișcare
- Așteaptă 2 secunde pentru calibrare după pornire
- Verifică alimentarea (5V, nu 3.3V!)
- Verifică conexiunea OUT la GPIO 24
- Ajustează potențiometrele pe senzor:
  - Sensitivity (Sx): distanță detectare
  - Time Delay (Tx): timp răspuns

### Eroare "RuntimeError: No access to /dev/mem"
```bash
sudo usermod -a -G gpio $USER
# apoi logout/login sau reboot
```

### Eroare "GPIO.setwarnings(False) not working"
- Normal - warnings-urile sunt pentru protecție
- Verifică că nu folosești același pin de 2 ori

## Siguranță

⚠️ **ATENȚIE**:
- NICIODATĂ nu conecta LED-uri fără rezistor (se ard instant!)
- Nu conecta direct 5V la pinii GPIO (doar la VCC)
- Nu conecta mai mult de 16mA pe un pin GPIO
- Nu conecta dispozitive inductive (motoare) direct la GPIO

## Diagrame

### Pinout Raspberry Pi 4 (BCM)

```
     3.3V ──┐     ┌── 5V
          1 │ x x │ 2
    GPIO 2 ── x x ── 5V
    GPIO 3 ── x x ── GND
    GPIO 4 ── x x ── GPIO 14
       GND ── x x ── GPIO 15
    GPIO17 ── x x ──│GPIO 18 (PIR)
   GPIO 27 ──│x x ── GND
          ↑ │     │ ↑
   (LED_GREEN) (PIR_GND)
    GPIO22 ── x x ── GPIO 23 ←── (BUZZER)
          ...
```

## Referințe

- [RPi.GPIO Documentation](https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/)
- [Raspberry Pi Pinout](https://pinout.xyz/)
- [HC-SR501 PIR Sensor Datasheet](https://www.mpja.com/download/31227sc.pdf)
