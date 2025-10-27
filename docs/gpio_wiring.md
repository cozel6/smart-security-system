# GPIO Wiring Diagram

Complete GPIO connection guide for Raspberry Pi 4.

---

## Pin Numbering

This project uses **BCM (Broadcom) pin numbering**, not physical pin numbers.

```
BCM: GPIO numbers used in code (e.g., GPIO 18)
Physical: Pin position on board (e.g., Pin 12)
```

---

## Complete Pin Mapping

| Component | Function | BCM GPIO | Physical Pin | Notes |
|-----------|----------|----------|--------------|-------|
| **PIR Sensor** | Signal OUT | GPIO 18 | Pin 12 | Input, pull-down |
| **PIR Sensor** | VCC | 5V | Pin 2 or 4 | Power |
| **PIR Sensor** | GND | Ground | Pin 6 | Ground |
| **LED Green** | Anode (+) | GPIO 27 | Pin 13 | Output, via 220Ω |
| **LED Red** | Anode (+) | GPIO 17 | Pin 11 | Output, via 220Ω |
| **LEDs** | Cathode (-) | Ground | Pin 9 or 14 | Common ground |
| **Buzzer** | Positive (+) | GPIO 22 | Pin 15 | Output |
| **Buzzer** | Negative (-) | Ground | Pin 14 or 20 | Ground |
| **USB Camera** | USB | USB Port | - | Any USB port |

---

## Raspberry Pi 4 GPIO Pinout

```
Raspberry Pi 4 GPIO Header (40-pin)

     3V3  (1) (2)  5V    ← PIR VCC
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND   ← PIR GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
GPIO17 ←──(11) (12) GPIO18 ← PIR OUT
GPIO27 ←──(13) (14) GND    ← Buzzer GND
GPIO22 ←──(15) (16) GPIO23
     3V3 (17) (18) GPIO24
GPIO10  (19) (20) GND
  GPIO9 (21) (22) GPIO25
GPIO11  (23) (24) GPIO8
     GND (25) (26) GPIO7
  GPIO0 (27) (28) GPIO1
  GPIO5 (29) (30) GND
  GPIO6 (31) (32) GPIO12
 GPIO13 (33) (34) GND
 GPIO19 (35) (36) GPIO16
 GPIO26 (37) (38) GPIO20
     GND (39) (40) GPIO21

Legend:
────► Used by this project
```

---

## Circuit Diagram

### Full Circuit Schematic

```
                    Raspberry Pi 4
                    ┌──────────────┐
                    │              │
                    │     (Pin 2)  │◄──── 5V ──────┐
                    │              │               │
PIR HC-SR501        │     (Pin 6)  │◄──── GND ─┐   │
┌──────────┐        │              │          │   │
│          │        │     (Pin 12) │          │   │
│   VCC    │◄───────┤     GPIO 18  │◄─────────┤   │
│   OUT    │──────► │              │          │   │
│   GND    │──────┐ │     (Pin 11) │          │   │
└──────────┘      │ │     GPIO 17  │◄─────┐   │   │
                  │ │              │      │   │   │
                  │ │     (Pin 13) │      │   │   │
                  │ │     GPIO 27  │◄──┐  │   │   │
                  │ │              │   │  │   │   │
                  │ │     (Pin 15) │   │  │   │   │
                  │ │     GPIO 22  │◄┐ │  │   │   │
                  │ │              │ │ │  │   │   │
                  │ │     (Pin 9)  │ │ │  │   │   │
                  │ │     GND      │ │ │  │   │   │
                  │ └──────────────┘ │ │  │   │   │
                  │                  │ │  │   │   │
                  └──────────────────┼─┼──┼───┼───┘
                                     │ │  │   │
          ┌──────────────────────────┘ │  │   │
          │  ┌────────────────────────┬┘  │   │
          │  │  ┌───────────────────┬─┘   │   │
          │  │  │                   │     │   │
     ┌────▼──▼──▼───┐         ┌────▼─────▼───┐
     │    GND       │         │   Buzzer     │
     └──────────────┘         │   (+)   (-)  │
                              └──────────────┘
          │         │
     ┌────▼────┐ ┌──▼─────┐
     │ LED Red │ │LED Green│
     │ 220Ω    │ │  220Ω  │
     │ ┌─┴─┐   │ │ ┌─┴─┐  │
     │ │ ◄─┼───┘ └─┤ ◄─┤  │
     │ └─▲─┘       └─▲─┘  │
     └───┼───────────┼────┘
         GND        GND
```

---

## Component Wiring Details

### PIR Sensor (HC-SR501)

```
PIR Sensor Pinout:
┌──────────────┐
│   [  ]  [  ] │ ← Potentiometers (Sensitivity, Delay)
│              │
│   VCC        │ → Connect to Pi Pin 2 or 4 (5V)
│   OUT        │ → Connect to Pi Pin 12 (GPIO 18)
│   GND        │ → Connect to Pi Pin 6 (GND)
└──────────────┘

Configuration:
- Sensitivity: Adjust distance (3-7 meters)
- Delay: 0.3s to 5 minutes (recommend ~2-3 seconds)
- Jumper: Set to "H" (repeatable trigger mode)
```

---

### LED Connection (with Current Limiting Resistor)

```
LED Wiring (Each LED):

Raspberry Pi GPIO ──► 220Ω Resistor ──► LED Anode (+) ──► LED Cathode (-) ──► GND

Green LED:
GPIO 27 (Pin 13) ──► 220Ω ──► ─┬─ ──► GND
                                └─┘

Red LED:
GPIO 17 (Pin 11) ──► 220Ω ──► ─┬─ ──► GND
                                └─┘

LED Polarity:
┌─────┐
│  ─┬─ │  ← LED symbol
│  └─┘ │
│  │ │ │
│  │ └─┼─ Cathode (-) - shorter leg, flat edge
│  └───┼─ Anode (+) - longer leg
└─────┘

220Ω Resistor Color Code:
Red-Red-Brown-Gold
```

---

### Buzzer Connection

```
Active Buzzer Pinout:
┌────────┐
│   ●    │ ← Sound opening
│ ┌────┐ │
│ │    │ │
│ └────┘ │
│  +  -  │
└────────┘

Connection:
Buzzer (+) → GPIO 22 (Pin 15)
Buzzer (-) → GND (Pin 14 or 20)

Note: Active buzzer has internal oscillator.
Just apply 5V to make sound (no PWM needed).
```

---

### USB Camera

```
USB Webcam Connection:

1. Plug into any USB port on Raspberry Pi
2. Verify detection:
   ls /dev/video*
   # Should show: /dev/video0

3. Test:
   v4l2-ctl --list-devices

Camera should be /dev/video0 (CAMERA_INDEX=0 in .env)
```

---

## Breadboard Layout

```
Breadboard Layout (Simplified Top View):

                 Raspberry Pi GPIO Header
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
    │   Power Rails     │   Component Area  │
    │                   │                   │
    │ + 5V ──────(Pin 2)│                   │
    │                   │                   │
    │ - GND ─────(Pin 6)│     PIR Sensor    │
    │     │             │     ┌─────────┐   │
    │     │             │     │  VCC ←──┼───┤ 5V
    │     │             │     │  OUT ←──┼───┤ Pin 12
    │     │             │     │  GND ←──┼───┤ GND
    │     │             │     └─────────┘   │
    │     │             │                   │
    │     ├──────��──────┼───► LED Green     │
    │     │   (Pin 13) ─┼─► 220Ω ─► ┬──┬   │
    │     │             │           └──┘    │
    │     │             │                   │
    │     ├─────────────┼───► LED Red       │
    │     │   (Pin 11) ─┼─► 220Ω ─► ┬──┬   │
    │     │             │           └──┘    │
    │     │             │                   │
    │     └─────────────┼───► Buzzer        │
    │         (Pin 15) ─┼─────► (+)         │
    │                   │         (-)───GND │
    └───────────────────┴───────────────────┘

Legend:
──► Wire connection
┬──┬ LED symbol
```

---

## Safety Precautions

### ⚠️ Important Safety Notes

1. **Power Off First**: Always disconnect power before wiring
2. **Correct Polarity**: 
   - LEDs: Wrong polarity = LED won't light (won't damage)
   - PIR: Wrong polarity = May damage sensor
   - Buzzer: Wrong polarity = No sound or damage
3. **Resistors Required**: Always use 220Ω resistors with LEDs
4. **GPIO Voltage**: Raspberry Pi GPIO is 3.3V tolerant
   - PIR outputs 3.3V (safe)
   - Don't connect 5V signals directly to GPIO
5. **Current Limits**: Max 16mA per GPIO pin
6. **Common Ground**: Ensure all components share common ground

---

## Verification Steps

### 1. Visual Inspection
- [ ] Check all connections match diagram
- [ ] Verify LED polarity (longer leg = positive)
- [ ] Confirm resistors are present on LED lines
- [ ] Check PIR sensor orientation

### 2. Continuity Test (Power OFF!)
- [ ] Use multimeter to verify connections
- [ ] Check for short circuits

### 3. Power-On Test
- [ ] LEDs should NOT light immediately (unless GPIO set HIGH)
- [ ] PIR sensor LED should blink (warmup period ~1 min)
- [ ] No smoke, no burning smell

### 4. Software Test
```bash
# Test GPIO setup
python3 -m src.hardware.led_controller
python3 -m src.hardware.buzzer
python3 -m src.hardware.pir_sensor
```

---

## Troubleshooting

### PIR Not Triggering
- Check 5V power connection
- Verify OUT connected to GPIO 18
- Adjust sensitivity potentiometer
- Wait for sensor warmup (~60 seconds)

### LEDs Not Lighting
- Check polarity (long leg = +)
- Verify resistor is present
- Test with simple script:
  ```python
  import RPi.GPIO as GPIO
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(17, GPIO.OUT)
  GPIO.output(17, GPIO.HIGH)
  ```

### Buzzer Not Sounding
- Verify it's an active buzzer (has oscillator)
- Check polarity
- Test with GPIO HIGH

---

## Alternative Pin Configurations

Can modify pin assignments in `.env`:

```bash
# Custom GPIO pins
PIR_PIN=23          # Use GPIO 23 instead of 18
LED_RED_PIN=24      # Use GPIO 24 instead of 17
LED_GREEN_PIN=25    # Use GPIO 25 instead of 27
BUZZER_PIN=12       # Use GPIO 12 instead of 22
```

**Caution:** Avoid reserved pins (I2C, SPI, UART) unless needed.

---

## Tools Needed

- Breadboard
- Jumper wires (Male-Female, Male-Male)
- 220Ω resistors (at least 2)
- Multimeter (for testing)
- Wire strippers (if using solid core wire)

---

## References

- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [HC-SR501 Datasheet](https://www.epitran.it/ebayDrive/datasheet/44.pdf)
- [RPi.GPIO Documentation](https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/)

---

**Last Updated:** 2024-10-27

**TODO:** Add Fritzing diagram image
