#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pygame
import sys

# --- SETTINGS ---
BROKER_IP = "192.168.1.100"  # Replace with your broker IP
TOPIC = "sensor/distance"

# --- Pygame Setup ---
pygame.init()
SCREEN_SIZE = (800, 480)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Distance Display")
font = pygame.font.SysFont(None, 48)

current_distance = None

# --- Drawing Function ---
def draw_display():
    screen.fill((30, 30, 30))  # default gray
    if current_distance is None:
        label = font.render("Waiting for data...", True, (200, 200, 200))
    else:
        if current_distance < 20:
            color = (200, 30, 30)
            text = f"Very Close ({current_distance} cm)"
        elif current_distance < 50:
            color = (220, 180, 30)
            text = f"Near ({current_distance} cm)"
        else:
            color = (40, 180, 60)
            text = f"Far ({current_distance} cm)"
        screen.fill(color)
        label = font.render(text, True, (0, 0, 0))
    screen.blit(label, (40, SCREEN_SIZE[1]//2 - 24))
    pygame.display.flip()

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker, code:", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global current_distance
    try:
        current_distance = int(msg.payload.decode())
        print(f"Received distance: {current_distance} cm")
    except ValueError:
        print("Invalid distance value")

# --- MQTT Setup ---
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_IP, 1883, 60)
client.loop_start()  # non-blocking loop

# --- Main Loop ---
try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                client.loop_stop()
                sys.exit()
        draw_display()
        pygame.time.wait(100)  # update every 100ms
except KeyboardInterrupt:
    pygame.quit()
    client.loop_stop()
    sys.exit()
