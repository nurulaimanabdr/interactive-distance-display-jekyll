---
layout: docs
title: Setup — Hardware & Software
description: ESP32 + Raspberry Pi Interactive Distance Display
---

<div class="card panel">
  <h2>Bill of Materials</h2>
  <ul>
    <li>ESP32 development board</li>
    <li>HC-SR04 ultrasonic sensor</li>
    <li>Raspberry Pi Zero 2 W (with Raspberry Pi OS installed)</li>
    <li>Monitor, keyboard, mouse (for Pi)</li>
    <li>Breadboard and jumper wires</li>
    <li>USB power (for ESP32 & Pi)</li>
  </ul>
</div>

<hr>

### Wiring (ESP32 + HC-SR04)

<ul>
  <li>VCC (HC-SR04) → 5V or 3.3V depending on your module (many accept 5V)</li>
  <li>GND → GND</li>
  <li>TRIG → GPIO 5</li>
  <li>ECHO → GPIO 18 <em>(use a voltage divider if ECHO is 5V)</em></li>
</ul>

<div class="image-center">
  <img src="/docs/assets/wiring-diagram.png" alt="Wiring diagram ESP32 + HC-SR04" />
  <small class="muted">ESP32 & HC-SR04 wiring diagram</small>
</div>

<div class="callout info">
  <strong>Networking:</strong> Both ESP32 and Raspberry Pi must be on the same local Wi‑Fi network.<br>
  MQTT broker runs on the Raspberry Pi — update the IP in <code>display_controller.py</code> if needed.
</div>

---

## Raspberry Pi — software steps

<div class="code-block">
  <button class="copy-btn" data-target="rp-update">Copy</button>
  <pre id="rp-update"><code>sudo apt update && sudo apt upgrade -y
sudo apt install -y mosquitto mosquitto-clients python3-pip
</code></pre>
</div>

<div class="code-block">
  <button class="copy-btn" data-target="rp-pip">Copy</button>
  <pre id="rp-pip"><code>python3 -m pip install paho-mqtt pygame
</code></pre>
</div>

<p>Verify mosquitto status (optional):</p>

<div class="code-block">
  <button class="copy-btn" data-target="rp-status">Copy</button>
  <pre id="rp-status"><code>systemctl status mosquitto
</code></pre>
</div>

---

## ESP32 — software steps

1. Install Arduino IDE (or use PlatformIO).  
2. Add ESP32 board support and install the <code>PubSubClient</code> library.  
3. Open <code>code/esp32/distance_sender.ino</code>, fill your Wi‑Fi SSID &amp; password, and upload.
