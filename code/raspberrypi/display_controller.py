#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pygame
import sys
import time
import threading

# --- SETTINGS ---
BROKER_IP = "192.168.1.100"  # Replace with your broker IP
BROKER_PORT = 1883
TOPIC = "sensor/distance"
CLIENT_ID = "distance_display_client"
USERNAME = None    # e.g. "myuser" if needed, otherwise None
PASSWORD = None    # e.g. "mypassword" if needed, otherwise None

# Reconnect params
RECONNECT_INITIAL = 5     # Initial seconds between reconnect attempts
RECONNECT_MAX = 300       # Max seconds backoff interval

# --- Pygame Setup ---
pygame.init()
SCREEN_SIZE = (800, 480)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Distance Display")
font = pygame.font.SysFont(None, 48)

current_distance = None
connected = False
last_disconnect_time = 0
reconnect_backoff = RECONNECT_INITIAL
reconnect_lock = threading.Lock()

def draw_display():
    screen.fill((30, 30, 30))  # default background
    if current_distance is None:
        label = font.render("Waiting for data...", True, (200, 200, 200))
    else:
        try:
            d = int(current_distance)
        except Exception:
            d = None
        if d is None:
            label = font.render("Invalid data", True, (220, 100, 100))
        else:
            if d < 20:
                color = (200, 30, 30)
                text = f"Very Close ({d} cm)"
            elif d < 50:
                color = (220, 180, 30)
                text = f"Near ({d} cm)"
            else:
                color = (40, 180, 60)
                text = f"Far ({d} cm)"
            screen.fill(color)
            label = font.render(text, True, (0, 0, 0))
    screen.blit(label, (40, SCREEN_SIZE[1]//2 - 24))
    pygame.display.flip()

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
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    global current_distance
    payload = msg.payload.decode(errors='ignore').strip()
    try:
        # Accept integer data; modify here if your sensor sends differently
        current_distance = int(payload)
        print(f"Received distance: {current_distance} cm")
    except ValueError:
        print(f"Invalid MQTT payload received: '{payload}'")

def on_disconnect(client, userdata, rc):
    global connected, last_disconnect_time
    connected = False
    last_disconnect_time = time.time()
    if rc == 0:
        print("Clean disconnect from broker.")
    else:
        print(f"Unexpected MQTT disconnect (rc={rc}).")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed (mid={mid}, qos={granted_qos})")

# --- MQTT Client Setup ---
client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe

if USERNAME and PASSWORD:
    client.username_pw_set(USERNAME, PASSWORD)

# Last Will message is optional; lets broker know if you go offline suddenly
client.will_set("clients/" + CLIENT_ID + "/status", payload="offline", qos=1, retain=True)

def try_connect():
    try:
        client.connect(BROKER_IP, BROKER_PORT, keepalive=60)
        client.loop_start()
    except Exception as e:
        print(f"Initial connect failed: {e}")

# Initial connection
try_connect()

# --- Main loop with reconnect handling ---
try:
    while True:
        # Handle pygame events
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
                    print(f"[Reconnect] Trying in {reconnect_backoff} seconds...")
                    try:
                        client.reconnect()
                    except Exception as e:
                        print(f"[Reconnect] Failed: {e}")
                        last_disconnect_time = now
                        reconnect_backoff = min(reconnect_backoff * 2, RECONNECT_MAX)
                # If it connects, reconnect_backoff is reset in on_connect

        draw_display()
        pygame.time.wait(100)  # ~10 fps

except KeyboardInterrupt:
    print("Shutting down.")
    try:
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    pygame.quit()
    sys.exit()
