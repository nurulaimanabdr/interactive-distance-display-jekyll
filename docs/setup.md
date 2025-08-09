# Setup — Hardware & Software

## Bill of Materials
- ESP32 development board
- HC-SR04 ultrasonic sensor
- Raspberry Pi Zero 2 W (with Raspberry Pi OS installed)
- Monitor, keyboard, mouse (for Pi)
- Breadboard and jumper wires
- USB power (for ESP32 & Pi)

## Wiring (ESP32 + HC-SR04)
- VCC (HC-SR04) -> 5V or 3.3V depending on your module (many modules accept 5V)
- GND -> GND
- TRIG -> GPIO 5
- ECHO -> GPIO 18 (use voltage divider if ECHO is 5V)

(Place a wiring-diagram image at `docs/assets/wiring-diagram.png`.)

## Network
- Both the ESP32 and Raspberry Pi must be on the same local network (WiFi).
- MQTT broker will run on Raspberry Pi. In the code we use the MQTT broker address `192.168.1.100` (placeholder) — if your Pi has a different IP, update `display_controller.py`.

## Raspberry Pi — software steps
1. Update & install packages:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y mosquitto mosquitto-clients python3-pip
```
2. Install Python packages:
```bash
python3 -m pip install paho-mqtt pygame
```
3. Optional: enable autostart for mosquitto (usually starts automatically). Verify with:
```bash
systemctl status mosquitto
```

## ESP32 — software steps
1. Install Arduino IDE (or use PlatformIO).
2. Add ESP32 board support and install `PubSubClient` library.
3. Open `code/esp32/distance_sender.ino`, fill your WiFi SSID & password, and upload.
