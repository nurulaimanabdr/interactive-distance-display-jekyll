# Troubleshooting

**MQTT broker not reachable**
- Check Pi IP with `hostname -I` and update the broker IP in both ESP32 and Pi code if needed.
- Ensure mosquitto service is running: `sudo systemctl status mosquitto`.

**Distance always zero or unrealistic**
- Check wiring for TRIG/ECHO.
- Ensure ECHO pin voltage is safe for ESP32 (use voltage divider if needed).
- Print distance to Serial (ESP32) to verify readings.

**Pygame window not visible**
- Ensure you are running the script on the Pi desktop (not via SSH unless X forwarding is configured).
- Use `python3 -m pip install --upgrade pygame` if errors occur.
