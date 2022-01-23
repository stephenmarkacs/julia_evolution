import math
import sys
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

# timing and scaling
NUM_STEPS = 400
MAX_SCALE = 10

# canvas 
W = 800

# colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

font = ImageFont.load_default()

def circles(image_draw, scale):
    image_draw.ellipse(
        (scale * 10, scale * 10, scale * 100, scale * 100), 
        fill=WHITE, outline=RED
    )    

def main(filename_base):
    images = []

    step_cnt = 1

    print(f"START")

    while step_cnt < NUM_STEPS:
        step_cnt += 1  # count including this step
        print(f"{step_cnt}")

        scale = 1 + MAX_SCALE * step_cnt / NUM_STEPS

        im = Image.new('RGB', (W, W), BLACK)
        d = ImageDraw.Draw(im)
        circles(d, scale)
        d.multiline_text((10,10), f"{step_cnt}", font=font, fill=WHITE)

        images.append(im)

    print("END")
    file = f"{filename_base}_{datetime.now().strftime('%Y%m%d%H%M%S')}.gif"
    print(f"writing to {file}")
    images[0].save(file, save_all=True, append_images=images[1:], optimize=False, duration=100, loop=0)

if __name__ == "__main__":
    main(sys.argv[1])
