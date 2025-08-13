#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pygame
import sys
import time
import threading
import math

# --- SETTINGS ---
BROKER_IP = "192.168.1.100"  # Replace with your broker IP
BROKER_PORT = 1883
TOPIC = "sensor/distance"
CLIENT_ID = "distance_display_client"
USERNAME = None
PASSWORD = None

# Reconnect params
RECONNECT_INITIAL = 5
RECONNECT_MAX = 300

# --- Pygame Setup ---
pygame.init()
SCREEN_SIZE = (800, 480)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Distance Visualization")
clock = pygame.time.Clock()
font_big = pygame.font.SysFont(None, 96)
font_med = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 28)

# Visualization parameters
current_distance = None
connected = False
last_disconnect_time = 0
reconnect_backoff = RECONNECT_INITIAL
reconnect_lock = threading.Lock()

# Animation state
start_time = time.time()
pulse_phase = 0.0

# --- Drawing helpers ---
def draw_radar(cx, cy, max_radius, distance_value):
    """
    Draw a radar-like circular pulse. If distance_value provided, scale pulse.
    """
    global pulse_phase
    # base pulse speed and size
    t = time.time() - start_time
    pulse_phase = (pulse_phase + 0.05) % (2 * math.pi)
    # If we have distance, map to 0..1 (clamp)
    if distance_value is None:
        norm = 0.5
    else:
        # assume sensors range 0..200 cm (tune as needed)
        norm = max(0.0, min(1.0, distance_value / 200.0))

    # number of rings and animated offset
    rings = 4
    offset = (math.sin(t * 1.2 + pulse_phase) + 1) / 2  # 0..1
    for i in range(rings):
        r = max_radius * ((i + 1) / float(rings)) * (0.6 + 0.4 * (1 - norm))
        alpha = int(70 * (1 - (i / rings)) * (0.6 + 0.4 * offset))
        color = (30, 200 - i * 30, 120 + i * 20)
        s = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color + (alpha,), (max_radius, max_radius), int(r), width=6)
        screen.blit(s, (cx - max_radius, cy - max_radius))

    # center dot
    dot_r = 10 + int(10 * (1 - norm))
    pygame.draw.circle(screen, (255, 255, 255), (cx, cy), dot_r)
    pygame.draw.circle(screen, (0, 0, 0), (cx, cy), dot_r, 2)

def draw_bar_meter(x, y, w, h, distance_value):
    """
    Horizontal bar from left (near) to right (far).
    """
    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h), border_radius=6)
    # If no data, show an animated scanning segment
    t = time.time()
    if distance_value is None:
        # animated gradient block scanning
        scan_w = w // 6
        scan_x = x + int(((math.sin(t * 1.5) + 1) / 2) * (w - scan_w))
        grad = pygame.Surface((scan_w, h), pygame.SRCALPHA)
        for i in range(scan_w):
            alpha = int(180 * (1 - abs(i - scan_w/2) / (scan_w/2)))
            grad.fill((80, 120, 200, alpha), rect=pygame.Rect(i, 0, 1, h))
        screen.blit(grad, (scan_x, y))
        label = font_small.render("Waiting for sensor...", True, (200, 200, 200))
        screen.blit(label, (x + 8, y + (h - label.get_height())//2))
    else:
        # Fill proportionally
        norm = max(0.0, min(1.0, distance_value / 200.0))  # tune range
        fill_w = int(w * norm)
        # gradient fill
        fill_surf = pygame.Surface((fill_w, h))
        for i in range(fill_w):
            r = int(40 + 200 * (i / max(1, fill_w)))
            g = int(200 - 100 * (i / max(1, fill_w)))
            b = int(60 + 60 * (1 - i / max(1, fill_w)))
            fill_surf.fill((r, g, b), rect=pygame.Rect(i, 0, 1, h))
        screen.blit(fill_surf, (x, y))
        # indicator line
        pygame.draw.line(screen, (0,0,0), (x + fill_w, y), (x + fill_w, y + h), 3)
        # numeric label
        lbl = f"{int(distance_value)} cm"
        label = font_med.render(lbl, True, (230, 230, 230))
        screen.blit(label, (x + w + 16, y + (h - label.get_height())//2))

def draw_no_data(cx, cy):
    """
    Big pulsing question mark when no data.
    """
    t = time.time()
    scale = 1.0 + 0.05 * math.sin(t * 2.0)
    q = font_big.render("?", True, (200, 200, 200))
    qs = pygame.transform.rotozoom(q, 0, scale)
    screen.blit(qs, (cx - qs.get_width()//2, cy - qs.get_height()//2))
    label = font_small.render("No data yet", True, (180, 180, 180))
    screen.blit(label, (cx - label.get_width()//2, cy + qs.get_height()//2 + 8))

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    global connected, reconnect_backoff
    if rc == 0:
        connected = True
        reconnect_backoff = RECONNECT_INITIAL
        print("Connected to MQTT broker.")
        client.subscribe(TOPIC)
    else:
        connected = False
        print(f"Failed to connect, rc={rc}")

def on_message(client, userdata, msg):
    global current_distance
    payload = msg.payload.decode(errors='ignore').strip()
    try:
        current_distance = int(payload)
        # clamp to reasonable range
        if current_distance < 0:
            current_distance = 0
        elif current_distance > 10000:
            current_distance = 10000
        print(f"Received distance: {current_distance} cm")
    except ValueError:
        print(f"Invalid payload: '{payload}'")

def on_disconnect(client, userdata, rc):
    global connected, last_disconnect_time
    connected = False
    last_disconnect_time = time.time()
    if rc == 0:
        print("Clean disconnect.")
    else:
        print(f"Unexpected disconnect (rc={rc}).")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed (mid={mid}, qos={granted_qos}).")

# --- MQTT Client Setup ---
client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe

if USERNAME and PASSWORD:
    client.username_pw_set(USERNAME, PASSWORD)

client.will_set(f"clients/{CLIENT_ID}/status", payload="offline", qos=1, retain=True)

def try_connect():
    try:
        client.connect(BROKER_IP, BROKER_PORT, keepalive=60)
        client.loop_start()
    except Exception as e:
        print(f"Initial connect failed: {e}")

try_connect()

# --- Main Loop ---
try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    client.loop_stop()
                    client.disconnect()
                except Exception:
                    pass
                pygame.quit()
                sys.exit()

        # Reconnect watchdog
        if not connected:
            now = time.time()
            with reconnect_lock:
                if now - last_disconnect_time >= reconnect_backoff:
                    print(f"[Reconnect] Attempting to reconnect (backoff={reconnect_backoff}s)...")
                    try:
                        client.reconnect()
                    except Exception as e:
                        print(f"[Reconnect] Failed: {e}")
                        last_disconnect_time = now
                        reconnect_backoff = min(reconnect_backoff * 2, RECONNECT_MAX)

        # Draw background
        screen.fill((12, 18, 24))

        # Layout positions
        cx, cy = SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//2
        radar_radius = min(SCREEN_SIZE[1]//2 - 40, SCREEN_SIZE[0]//3 - 40)
        draw_radar(cx, cy, radar_radius, current_distance)

        # Right-side meter
        meter_x = SCREEN_SIZE[0]//3 * 2 - 280
        meter_y = SCREEN_SIZE[1]//2 - 40
        meter_w = 520
        meter_h = 80
        draw_bar_meter(meter_x, meter_y, meter_w, meter_h, current_distance)

        # Header text
        header = font_med.render("Distance Visualizer", True, (200, 200, 220))
        screen.blit(header, (20, 12))
        # Connection status
        status_text = "Connected" if connected else "Disconnected"
        status_color = (80, 220, 120) if connected else (220, 80, 80)
        status_lbl = font_small.render(f"MQTT: {status_text}", True, status_color)
        screen.blit(status_lbl, (SCREEN_SIZE[0] - 160, 14))

        # If no data, show big question mark
        if current_distance is None:
            draw_no_data(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2)

        # Footer hint
        hint = font_small.render("Press window close button to exit", True, (120, 120, 140))
        screen.blit(hint, (20, SCREEN_SIZE[1] - 28))

        pygame.display.flip()
        clock.tick(30)  # 30 FPS-ish

except KeyboardInterrupt:
    print("Exiting by user.")
    try:
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    pygame.quit()
    sys.exit()
