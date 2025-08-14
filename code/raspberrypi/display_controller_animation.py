import pygame
import paho.mqtt.client as mqtt
from PIL import Image

BROKER_IP = "192.168.x.x"  # Replace with broker IP
PORT = 1883
TOPIC = "distance"

CLOSE_ANIM = "assets/animation_close.gif"
FAR_ANIM = "assets/animation_far.gif"

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Interactive Space Display")
font = pygame.font.Font(None, 80)

# --- Function to load GIF frames ---
def load_gif_frames(path):
    frames = []
    try:
        pil_img = Image.open(path)
        while True:
            frame = pil_img.copy().convert("RGB")
            mode = frame.mode
            size = frame.size
            data = frame.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)
            frames.append(py_image)
            pil_img.seek(len(frames))  # go to next frame
    except EOFError:
        pass
    return frames

# Load animations
close_frames = load_gif_frames(CLOSE_ANIM)
far_frames = load_gif_frames(FAR_ANIM)
current_frames = far_frames
frame_index = 0
frame_delay = 5  # adjust for speed

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global current_frames
    if not running_distance:
        return
    try:
        distance = float(msg.payload.decode())
        if distance < 50:
            current_frames = close_frames
        else:
            current_frames = far_frames
    except ValueError:
        pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.loop_start()

# Buttons
start_button = pygame.Rect(600, 400, 300, 120)
stop_button = pygame.Rect(600, 400, 300, 120)

running = True
running_distance = False

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not running_distance and start_button.collidepoint(event.pos):
                running_distance = True
            elif running_distance and stop_button.collidepoint(event.pos):
                running_distance = False

    if not running_distance:
        pygame.draw.rect(screen, (0, 255, 0), start_button)
        screen.blit(font.render("START", True, (0, 0, 0)), (start_button.x + 60, start_button.y + 30))
    else:
        if current_frames:
            frame_to_show = current_frames[frame_index // frame_delay]
            screen.blit(pygame.transform.scale(frame_to_show, screen.get_size()), (0, 0))
            frame_index = (frame_index + 1) % (len(current_frames) * frame_delay)

        pygame.draw.rect(screen, (255, 0, 0), stop_button)
        screen.blit(font.render("STOP", True, (255, 255, 255)), (stop_button.x + 70, stop_button.y + 30))

    pygame.display.flip()
    pygame.time.Clock().tick(30)  # 30 FPS

pygame.quit()
