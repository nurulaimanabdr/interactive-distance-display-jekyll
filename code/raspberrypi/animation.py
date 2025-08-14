import os
from PIL import Image, ImageDraw

os.makedirs("assets", exist_ok=True)

def create_gif(filename, color, text):
    frames = []
    for i in range(10):
        img = Image.new("RGB", (400, 300), color)
        draw = ImageDraw.Draw(img)
        draw.text((150, 140), text, fill="white")
        frames.append(img)
    frames[0].save(filename, save_all=True, append_images=frames[1:], duration=100, loop=0)

create_gif("assets/animation_close.gif", "red", "CLOSE")
create_gif("assets/animation_far.gif", "green", "FAR")

print("GIFs created in 'assets' folder")
