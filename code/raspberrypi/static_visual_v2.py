#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pygame
import sys
import time
import threading
import math

# --- SETTINGS ---
BROKER_IP = "192.168.1.100"
BROKER_PORT = 1883
TOPIC = "sensor/distance"
CLIENT_ID = "distance_display_client"
USERNAME = None
PASSWORD = None

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

current_distance = None
connected = False
last_disconnect_time = 0
reconnect_backoff = RECONNECT_INITIAL
reconnect_lock = threading.Lock()

start_time = time.time()
pulse_phase = 0.0

# Start/Stop control
started = False

# --- Drawing helpers ---
def draw_button(text, x, y, w, h, color, text_color=(255,255,255)):
    """Draws a button and returns the Rect for click detection."""
    # Draw button rectangle
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=8)
    # Draw border
    border_color = (max(color[0] - 40, 0), max(color[1] - 40, 0), max(color[2] - 40, 0))
    pygame.draw.rect(screen, border_color, (x, y, w, h), 3, border_radius=8)
    # Render label
    label = font_med.render(text, True, text_color)
    screen.blit(label, (x + (w - label.get_width())//2, y + (h - label.get_height())//2))
    return pygame.Rect(x, y, w, h)

def draw_radar(cx, cy, max_radius, distance_value, faded=False):
    global pulse_phase
    t = time.time() - start_time
    pulse_phase = (pulse_phase + 0.05) % (2 * math.pi)
    if distance_value is None:
        norm = 0.5
    else:
        norm = max(0.0, min(1.0, distance_value / 200.0))
    rings = 4
    offset = (math.sin(t * 1.2 + pulse_phase) + 1) / 2
    for i in range(rings):
        r = max_radius * ((i + 1) / float(rings)) * (0.6 + 0.4 * (1 - norm))
        alpha = int(70 * (1 - (i / rings)) * (0.6 + 0.4 * offset))
        base_color = (30, 200 - i * 30, 120 + i * 20)
        color = tuple([c if not faded else int(0.5*c+60) for c in base_color])
        s = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color + (alpha,), (max_radius, max_radius), int(r), width=6)
        screen.blit(s, (cx - max_radius, cy - max_radius))
    dot_r = 10 + int(10 * (1 - norm))
    dot_color = (255,255,255) if not faded else (180,180,180)
    pygame.draw.circle(screen, dot_color, (cx, cy), dot_r)
    pygame.draw.circle(screen, (0, 0, 0), (cx, cy), dot_r, 2)

def draw_bar_meter(x, y, w, h, distance_value, faded=False):
    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h), border_radius=6)
    t = time.time()
    if distance_value is None:
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
        norm = max(0.0, min(1.0, distance_value / 200.0))
        fill_w = int(w * norm)
        if fill_w > 0:
            fill_surf = pygame.Surface((fill_w, h))
            for i in range(fill_w):
                if not faded:
                    r = int(40 + 200 * (i / max(1, fill_w)))
                    g = int(200 - 100 * (i / max(1, fill_w)))
                    b = int(60 + 60 * (1 - i / max(1, fill_w)))
                else:
                    r = g = b = 150
                fill_surf.fill((r, g, b), rect=pygame.Rect(i, 0, 1, h))
            screen.blit(fill_surf, (x, y))
        color_line = (0,0,0) if not faded else (120,120,120)
        pygame.draw.line(screen, color_line, (x + fill_w, y), (x + fill_w, y + h), 3)
        lbl = f"{int(distance_value)} cm"
        label_color = (230, 230, 230) if not faded else (160,160,160)
        label = font_med.render(lbl, True, label_color)
        screen.blit(label, (x + w + 16, y + (h - label.get_height())//2))

def draw_no_data(cx, cy):
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
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if not started and start_btn_rect.collidepoint(mouse_pos):
                    started = True
                elif started and stop_btn_rect.collidepoint(mouse_pos):
                    started = False
                    current_distance = None  # Clear display

        # MQTT reconnect watchdog
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

        screen.fill((12, 18, 24))

        # Header
        header = font_med.render("Distance Visualizer", True, (200, 200, 220))
        screen.blit(header, (20, 12))
        status_text = "Connected" if connected else "Disconnected"
        status_color = (80, 220, 120) if connected else (220, 80, 80)
        status_lbl = font_small.render(f"MQTT: {status_text}", True, status_color)
        screen.blit(status_lbl, (SCREEN_SIZE[0] - 160, 14))

        if started:
            cx, cy = SCREEN_SIZE[0]//3, SCREEN_SIZE[1]//2
            radar_radius = min(SCREEN_SIZE[1]//2 - 40, SCREEN_SIZE[0]//3 - 40)
            draw_radar(cx, cy, radar_radius, current_distance)
            meter_x = SCREEN_SIZE[0]//3 * 2 - 280
            meter_y = SCREEN_SIZE[1]//2 - 40
            meter_w = 520
            meter_h = 80
            draw_bar_meter(meter_x, meter_y, meter_w, meter_h, current_distance)
            if current_distance is None:
                draw_no_data(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2)
            # Draw Stop button (Red)
            stop_btn_rect = draw_button("Stop", SCREEN_SIZE[0] - 180, SCREEN_SIZE[1] - 70, 160, 50, color=(220, 50, 30))
        else:
            draw_no_data(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2)
            # Draw Start button (Green)
            start_btn_rect = draw_button("Start", SCREEN_SIZE[0]//2 - 80, SCREEN_SIZE[1]//2 + 100, 160, 60, color=(50, 180, 50))

        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    print("Exiting by user.")
    try:
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    pygame.quit()
    sys.exit()
