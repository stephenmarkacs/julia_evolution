from datetime import datetime
from math import cos, pi, sin
from numba import jit
from enum import Enum

import moviepy.editor as mp
from PIL import Image, ImageDraw, ImageFont

# canvas
WIDTH = 500
XMIN = 0
XMAX = 499
YMIN = 0
YMAX = 499

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# iteration and timing
FRAME_MAX = 64
DURATION = 100

class Orientation(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

sizes = [0.0]
n = 0
val = 0.0
while val < WIDTH:
    val = 1 + 2.0 * val
    n += 1
    sizes.append(val)

def hilby(draw, xmin, xmax, ymin, ymax, numRecursions, orientation):
    if numRecursions < 0:
        return 

    print(f"ENTER hilby(draw, {xmin}, {xmax}, {ymin}, {ymax}, {numRecursions}, {orientation})")


    # ---- 4 recursions ----
    if numRecursions == 0:
        draw.ellipse(((xmin, ymin), (xmax, ymax)), outline=WHITE, width=3)
    else:
        y_width = ymax - ymin
        x_width = xmax - xmin
        fraction_near = sizes[numRecursions - 1] / sizes[numRecursions] 
        x_step = fraction_near * x_width
        y_step = fraction_near * y_width
        x_connect = x_width * (1 - 2 * fraction_near)
        y_connect = y_width * (1 - 2 * fraction_near)        

        # 2 bottoms match orientation with parent
        # bottom left
        hilby(draw, xmin, ymin + y_step + y_connect, xmin + x_step, ymax, numRecursions - 1, orientation)

        # bottom right
        hilby(draw, xmin + x_step + x_connect, ymin + y_step + y_connect, xmax, ymax, numRecursions - 1, orientation)

        # ---- 3 connections ----
        # 2 side connectors are on the outside
        if orientation in (Orientation.UP, Orientation.DOWN):
            # left and right walls
            draw.line((
                (xmin, ymin + y_step), 
                (xmin, ymin + y_step + y_connect)
            ), fill=WHITE, width=4)
            draw.line((
                (xmax, ymin + y_step), 
                (xmax, ymin + y_step + y_connect)
            ), fill=WHITE, width=4)
        else:
            # top and bottom walls
            draw.line((
                (xmin + x_step, ymin),
                (xmin + x_step + x_connect, ymin)
            ))
            draw.line((
                (xmin + x_step, ymax),
                (xmin + x_step + x_connect, ymax)
            ), fill=WHITE, width=4)

        # 1 middle connector is in the middle
        up_left =    (xmin + x_step,                ymin + y_step)
        up_right =   (xmin + x_step + x_connect,    ymin + y_step)
        down_left =  (xmin + x_step,                ymin + y_step + y_connect)
        down_right = (xmin + x_step + x_connect,    ymin + y_step + y_connect)
        draw.line((
            up_left if orientation in (Orientation.DOWN, Orientation.RIGHT) else down_right,
            up_right if orientation in (Orientation.DOWN, Orientation.LEFT) else down_left
        ), fill=WHITE, width=4)

    print(f"EXIT hilby(draw, {xmin}, {xmax}, {ymin}, {ymax}, {numRecursions}, {orientation})")


def main():
    images = []
    frame_count = 0

    frame_count = 1

    while frame_count < FRAME_MAX:
        print(f"calc frame {frame_count}")

        im = Image.new('RGB', (WIDTH, WIDTH), BLACK)
        frame = im.load()
        draw = ImageDraw.Draw(im)

        hilby(draw, XMIN, XMAX, YMIN, YMAX, 3, Orientation.UP)

        images.append(im)

        frame_count += 1

    print("END")
    file_base = f"hilby{datetime.now().strftime('%Y%m%d%H%M%S')}"
    gif = f"{file_base}.gif"
    print(f"writing gif: {gif}")
    images[0].save(gif, save_all=True, append_images=images[1:], optimize=False, duration=DURATION, loop=0)
    mp4 = f"{file_base}.mp4"
    print(f"converting to mp4: ./{mp4}")
    video = mp.VideoFileClip(gif)
    video.write_videofile(mp4)  

if __name__ == "__main__":
    main()
