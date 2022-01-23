import math
import sys
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

# timing and scaling
NUM_STEPS = 400
MAX_SCALE = 8

# canvas 
W = 800


font = ImageFont.load_default()
  
def main(filename_base):
    images = []

    black = (0, 0, 0)
    red = (255, 0, 0)
    white = (255, 255, 255)
    step_cnt = 1

    print(f"START")

    while step_cnt < NUM_STEPS:
        step_cnt += 1  # count including this step
        print(f"{step_cnt}")

        factor = 1 + MAX_SCALE * step_cnt / NUM_STEPS

        im = Image.new('RGB', (W, W), black)
        d = ImageDraw.Draw(im)
        d.ellipse(
            (factor * 10, factor * 10, factor * 100, factor * 100), 
            fill=white, outline=red
        )
        d.multiline_text((10,10), f"{step_cnt}", font=font, fill=white)

        images.append(im)

    print("END")
    file = f"{filename_base}_{datetime.now().strftime('%Y%m%d%H%M%S')}.gif"
    print(f"writing to {file}")
    images[0].save(file, save_all=True, append_images=images[1:], optimize=False, duration=100, loop=0)

if __name__ == "__main__":
    main(sys.argv[1])
