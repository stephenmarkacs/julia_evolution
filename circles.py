import math
import sys
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

# timing and scaling
NUM_STEPS = 400
MAX_SCALE = 6

# canvas 
W = 800

# colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# CIRCLES FRACTAL MATH
# factor is ratio of the full circle radius to that of the radius of the next larger circles 3
FACTOR = 1 + 0.5 * ( math.sqrt(3) + ( 1 / math.sqrt(3) ) )


font = ImageFont.load_default()

def circles(image_draw, remain, 
            x, y, r):
    # i find it feels cleaner to let the children do nothing here 
    # than to have to worry about termination when i recurse
    # may change my mind, thinking...
    if remain > 0:
        # funny toggle?
        color = WHITE if remain % 2 else BLACK

        # primary circle - can this be the only circle in this iteration?
        image_draw.ellipse(
            (x - r, y - r, x + r, y + r), # bounding box (x0, y0, x1, y1)
            fill=color, outline=RED
        )

        # recurse fractally by threes
        # circles



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

        # the first branch
        circles(d, 3, 100 * scale, 100 * scale, 100 * scale)

        # notations in the corner
        d.multiline_text((10,10), f"{step_cnt}", font=font, fill=WHITE)

        images.append(im)

    print("END")
    file = f"{filename_base}_{datetime.now().strftime('%Y%m%d%H%M%S')}.gif"
    print(f"writing to {file}")
    images[0].save(file, save_all=True, append_images=images[1:], optimize=False, duration=100, loop=0)

if __name__ == "__main__":
    main(sys.argv[1])
