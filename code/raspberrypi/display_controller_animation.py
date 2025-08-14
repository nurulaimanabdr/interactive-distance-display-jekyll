import pygame
import paho.mqtt.client as mqtt

BROKER_IP = "192.168.x.x"  # Replace with broker IP
PORT = 1883
TOPIC = "distance"

# Load animations
CLOSE_ANIM = "assets/animation_close.gif"
FAR_ANIM = "assets/animation_far.gif"

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Interactive Space Display")

# Animation loader
def load_animation(path):
    try:
        return pygame.image.load(path)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

close_img = load_animation(CLOSE_ANIM)
far_img = load_animation(FAR_ANIM)

current_img = far_img

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global current_img
    try:
        distance = float(msg.payload.decode())
        if distance < 50:  # threshold in cm
            current_img = close_img
        else:
            current_img = far_img
    except ValueError:
        pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.loop_start()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if current_img:
        screen.blit(pygame.transform.scale(current_img, screen.get_size()), (0, 0))
    pygame.display.flip()

pygame.quit()
