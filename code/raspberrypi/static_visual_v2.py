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

# Start/Stop control
started = False

# --- Drawing helpers ---
def draw_button(text, x, y, w, h, active=True):
    """Draws a button and returns the Rect for click detection."""
    color = (80, 200, 120) if active else (150, 150, 150)
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=8)
    pygame.draw.rect(screen, (0, 0, 0), (x, y, w, h), 2, border_radius=8)
    label = font_med.render(text, True, (0, 0, 0))
    screen.blit(label, (x + (w - label.get_width())//2, y + (h - label.get_height())//2))
    return pygame.Rect(x, y, w, h)

def draw_radar(cx, cy, max_radius, distance_value):
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
        color = (30, 200 - i * 30, 120 + i * 20)
        s = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color + (alpha,), (max_radius, max_radius), int(r), width=6)
        screen.blit(s, (cx - max_radius, cy - max_radius))
    dot_r = 10 + int(10 * (1 - norm))
    pygame.draw.circle(screen, (255, 255, 255), (cx, cy), dot_r)
    pygame.draw.circle(screen, (0, 0, 0), (cx, cy), dot_r, 2)

def draw_bar_meter(x, y, w, h, distance_value):
    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h), border_radius=6)
    t = time.time()
    if distance_va_
