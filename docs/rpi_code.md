# Raspberry Pi — display_controller.py

**MQTT broker IP used in the project:** `192.168.1.100` (assumes mosquitto on Pi)

**Behavior:** Subscribes to `sensor/distance`. Based on distance it changes screen:
- `< 20 cm` -> strong red/warning
- `20–50 cm` -> yellow/attention
- `> 50 cm` -> green/relaxed

**How to run:**
```bash
python3 code/raspberrypi/display_controller.py
```

**Notes:** Run this on the Pi with display connected. If running headless, you'll need to configure a virtual frame buffer — but for the demo a connected monitor is easiest.
