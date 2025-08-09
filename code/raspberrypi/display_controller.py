#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import pygame
import sys
import threading

# MQTT broker configuration
BROKER_IP = "192.168.1.100"  # <-- set to Pi IP (as requested)
TOPIC = "sensor/distance"

# Pygame setup
pygame.init()
SCREEN_SIZE = (800, 480)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Distance Controlled Display')

# simple text rendering
font = pygame.font.SysFont(None, 48)

current_distance = None

def draw_color_for_distance(dist):
    if dist is None:
        screen.fill((30, 30, 30))
        label = font.render('Waiting for data...', True, (200,200,200))
        screen.blit(label, (40, SCREEN_SIZE[1]//2 - 24))
        pygame.display.flip()
        return

    if dist < 20:
        color = (200, 30, 30)  # red
        text = 'Very Close (<20 cm)'
    elif dist < 50:
        color = (220, 180, 30) # yellow
        text = 'Near (20-50 cm)'
    else:
        color = (40, 180, 60)  # green
        text = 'Far (>50 cm)'

    screen.fill(color)
    label = font.render(f'{text} - {dist} cm', True, (0,0,0))
    screen.blit(label, (40, SCREEN_SIZE[1]//2 - 24))
    pygame.display.flip()

def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker with result code ' + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global current_distance
    try:
        payload = msg.payload.decode()
        dist = int(payload)
        current_distance = dist
        # update display on main thread via event
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'distance': dist}))
    except Exception as e:
        print('Error parsing message:', e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_IP, 1883, 60)

# Run MQTT client loop in a separate thread
mqtt_thread = threading.Thread(target=client.loop_forever)
mqtt_thread.daemon = True
mqtt_thread.start()

# initial display
draw_color_for_distance(None)

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.USEREVENT:
                dist = event.__dict__.get('distance')
                draw_color_for_distance(dist)
        pygame.time.wait(50)
except KeyboardInterrupt:
    pygame.quit()
    sys.exit(0)
