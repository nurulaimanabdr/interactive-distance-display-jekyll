import pygame
import paho.mqtt.client as mqtt

# MQTT Config
BROKER_IP = "192.168.x.x"  # Replace with your broker IP
PORT = 1883
TOPIC = "distance"

# Assets
CLOSE_ANIM = "assets/animation_close.png"  # Use PNG/JPG for static
FAR_ANIM = "assets/animation_far.png"

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Interactive Space Display")
font = pygame.font.Font(None, 80)

# Load image safely
def load_image(path):
    try:
        return pygame.image.load(path)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

close_img = load_image(CLOSE_ANIM)
far_img = load_image(FAR_ANIM)
current_img = far_img

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global current_img
    try:
        distance = float(msg.payload.decode())
        if distance < 50:
            current_img = close_img
        else:
            current_img = far_img
    except ValueError:
        pass

# Setup MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Buttons
def draw_button(text, y, color=(0, 128, 255)):
    button_surf = font.render(text, True, (255, 255, 255))
    button_rect = button_surf.get_rect(center=(screen.get_width() // 2, y))
    pygame.draw.rect(screen, color, button_rect.inflate(40, 20))
    screen.blit(button_surf, button_rect)
    return button_rect

# Main loop
running = True
started = False

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if not started:
                if start_btn.collidepoint(mouse_pos):
                    client.connect(BROKER_IP, PORT, 60)
                    client.loop_start()
                    started = True
            else:
                if stop_btn.collidepoint(mouse_pos):
                    running = False

    if not started:
        start_btn = draw_button("START", screen.get_height() // 2)
    else:
        if current_img:
            screen.blit(pygame.transform.scale(current_img, screen.get_size()), (0, 0))
        stop_btn = draw_button("STOP", screen.get_height() - 100, color=(200, 0, 0))

    pygame.display.flip()

pygame.quit()
