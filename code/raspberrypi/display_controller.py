#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pygame
import sys
import threading
import time

# -----------------------------
# MQTT broker configuration
# -----------------------------
BROKER_IP = "192.160.100.191"  # <-- Change to your Pi's IP
TOPIC = "sensor/distance"

# -----------------------------
# Pygame setup
# -----------------------------
pygame.init()
SCREEN_SIZE = (800, 480)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Distance Controlled Display')
font = pygame.font.SysFont(None, 48)

# Global variables
current_distance = None
last_update_time = 0  # track last time MQTT data arrived

# -----------------------------
# Drawing function
# -----------------------------
def draw_color_for_distance(dist):
    screen.fill((30, 30, 30))  # default background

    if dist is None:
        label = font.render('Waiting for data...', True, (200, 200, 200))
        screen.blit(label, (40, SCREEN_SIZE[1]//2 - 24))
    else:
        if dist < 20:
            color = (200, 30, 30)  # red
            text = f'Very Close (<20 cm) - {dist} cm'
        elif dist < 50:
            color = (220, 180, 30)  # yellow
            text = f'Near (20-50 cm) - {dist} cm'
        else:
            color = (40, 180, 60)  # green
            text = f'Far (>50 cm) - {dist} cm'

        screen.fill(color)
        label = font.render(text, True, (0, 0, 0))
        screen.blit(label, (40, SCREEN_SIZE[1]//2 - 24))

    pygame.display.flip()

# -----------------------------
# MQTT Callbacks
# -----------------------------
def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker with result code ' + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global current_distance, last_update_time
    try:
        payload = msg.payload.decode()
        dist = int(payload)
        current_distance = dist
        last_update_time = time.time()
        print(f"MQTT Received: {dist} cm")
    except Exception as e:
        print('Error parsing message:', e)

# -----------------------------
# MQTT Client setup
# -----------------------------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER_IP, 1883, 60)
except Exception as e:
    print("MQTT connection failed:", e)
    sys.exit(1)

mqtt_thread = threading.Thread(target=client.loop_forever)
mqtt_thread.daemon = True
mqtt_thread.start()

# -----------------------------
# Main Loop
# -----------------------------
try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        # Show 'No recent data' if more than 5 seconds without update
        if current_distance is not None and (time.time() - last_update_time > 5):
            current_distance = None

        draw_color_for_distance(current_distance)
        pygame.time.wait(200)

except KeyboardInterrupt:
    pygame.quit()
    sys.exit(0)
