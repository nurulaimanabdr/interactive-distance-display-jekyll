# ESP32 + HC-SR04 + Raspberry Pi Zero 2 W Setup Guide

This guide walks you through connecting an **ESP32** with an **HC-SR04 ultrasonic sensor** and sending the distance data to a **Raspberry Pi Zero 2 W** via MQTT for display.

---

## Bill of Materials
- **ESP32 development board**
- **HC-SR04 ultrasonic sensor**
- **Raspberry Pi Zero 2 W** (with Raspberry Pi OS installed)
- **Monitor, keyboard, mouse** (for Raspberry Pi)
- **Breadboard and jumper wires**
- **USB power supplies** (for both ESP32 & Raspberry Pi)

---

## Wiring (ESP32 ↔ HC-SR04)

| HC-SR04 Pin | ESP32 Pin | Notes |
|-------------|-----------|-------|
| VCC         | 5V or 3.3V | Many modules accept 5V; check your datasheet |
| GND         | GND       | — |
| TRIG        | GPIO 5    | — |
| ECHO        | GPIO 18   | **If ECHO outputs 5V, use a voltage divider to step down to 3.3V** |

**Wiring Diagram:**  
![ESP32 & HC-SR04 wiring diagram](/docs/assets/wiring-diagram.png)  
<small>ESP32 & HC-SR04 wiring diagram</small>

---

## Networking
- Both **ESP32** and **Raspberry Pi** must be connected to the **same Wi-Fi network**.
- MQTT broker runs on the Raspberry Pi.
- Update the broker IP in `display_controller.py` and in your ESP32 sketch.

---

## Raspberry Pi Setup

1. **Update and install MQTT + Python dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y mosquitto mosquitto-clients python3-pip
   ```

2. **Install Python packages:**
   ```bash
   python3 -m pip install paho-mqtt pygame
   ```

3. **(Optional) Verify Mosquitto is running:**
   ```bash
   systemctl status mosquitto
   ```

---

## ESP32 Setup

1. Install **Arduino IDE** (or use PlatformIO in VS Code).
2. In Arduino IDE:
   - Go to **File → Preferences** → Add ESP32 board URL:
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     ```
   - Open **Tools → Board → Board Manager**, search for “ESP32”, and install.
3. Install **PubSubClient** library:
   - **Sketch → Include Library → Manage Libraries**
   - Search for `PubSubClient` and install.
4. Open:
   ```
   code/esp32/distance_sender.ino
   ```
5. Update Wi-Fi and MQTT settings in the sketch:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   const char* mqtt_server = "RASPBERRY_PI_IP_ADDRESS";
   ```

---

## Tips
- Keep `display_controller.py` and `distance_sender.ino` using the **same MQTT topic name** (`sensor/distance` in the examples).
- If your HC-SR04 outputs **5V** on ECHO, always use a voltage divider to protect the ESP32 GPIO.
- Test MQTT locally on Raspberry Pi with:
  ```bash
  mosquitto_sub -h localhost -t sensor/distance
  ```

---

## Troubleshooting
- **No data showing?**
  - Check both devices are on the same network.
  - Verify Mosquitto is running: `systemctl status mosquitto`
  - Test with `mosquitto_pub` and `mosquitto_sub` before running the scripts.
- **ESP32 can’t connect?**
  - Check Wi-Fi credentials and broker IP.
- **Display blank in Pygame?**
  - Ensure your monitor is connected to Raspberry Pi.
  - Run the Python script directly:  
    ```bash
    python3 display_controller.py
    ```
