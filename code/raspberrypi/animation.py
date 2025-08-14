import os
from PIL import Image, ImageDraw, ImageFont

# Make sure assets folder exists
os.makedirs("assets", exist_ok=True)

# Try to load a nicer font, fall back to default if not found
try:
    font = ImageFont.truetype("arial.ttf", 40)
except:
    font = ImageFont.load_default()

def create_animated_gif(filename, bg_color, circle_color, text, expanding=True):
    frames = []
    width, height = 400, 300
    max_radius = 100
    num_frames = 15

    for i in range(num_frames):
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Circle animation
        progress = i / (num_frames - 1)
        radius = int(progress * max_radius) if expanding else int((1 - progress) * max_radius)
        draw.ellipse(
            [(width//2 - radius, height//2 - radius), 
             (width//2 + radius, height//2 + radius)],
            fill=circle_color
        )

        # Bouncing text
        text_x = width // 2 - 50
        text_y = int(height // 2 + (10 * (1 if i % 2 == 0 else -1)))
        draw.text((text_x, text_y), text, font=font, fill="white")

        frames.append(img)

    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=100, loop=0)

# Create the GIFs
create_animated_gif("assets/animation_close.gif", bg_color="red", circle_color="darkred", text="CLOSE", expanding=False)
create_animated_gif("assets/animation_far.gif", bg_color="green", circle_color="darkgreen", text="FAR", expanding=True)

print("Animated GIFs created in 'assets' folder.")
