# Interactive Distance-Controlled Visual Output

A short lab manual and working code that demonstrates how to build an interactive prototype where a Raspberry Pi's visual output changes based on distance measured by an HC-SR04 attached to an ESP32. Communication is over MQTT on the local network.

**Quick features:**
- ESP32 + HC-SR04 measures distance and publishes to MQTT.
- Raspberry Pi subscribes to MQTT and uses `pygame` to display color/animation based on distance.
- Documentation ready for GitHub Pages in `/docs`.

## How to use
1. Copy repo contents to GitHub and enable Pages from the `/docs` folder.
2. On Raspberry Pi: install Mosquitto (MQTT broker), Python dependencies, and run `display_controller.py`.
3. On ESP32: update `ssid` and `password` placeholders, upload `distance_sender.ino`.
