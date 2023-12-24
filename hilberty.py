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
MARGIN = 5

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# iteration and timing
FRAME_MAX = 2
DURATION = 100


class Orientation(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

CW_ROTATOR = {
    Orientation.UP: Orientation.RIGHT,
    Orientation.RIGHT: Orientation.DOWN,
    Orientation.DOWN: Orientation.LEFT,
    Orientation.LEFT: Orientation.UP,
}

CCW_ROTATOR = {
    Orientation.UP: Orientation.LEFT,
    Orientation.LEFT: Orientation.DOWN,
    Orientation.DOWN: Orientation.RIGHT,
    Orientation.RIGHT: Orientation.UP,
}

def cwise(orientation):
    return CW_ROTATOR.get(orientation)
    
def ccwise(orientation):
    return CCW_ROTATOR.get(orientation)


sizes = [0.0]
n = 0
val = 0.0
while val < WIDTH:
    val = 1 + 2.0 * val
    n += 1
    sizes.append(val)


def hilby(draw, numRecursions, p1, p2, orientation):
    if numRecursions < 0:
        return 

    color = RED if numRecursions % 3 == 0 else GREEN if numRecursions % 3 == 1 else BLUE
    print(f"ENTER hilby(draw, {numRecursions}, {p1}, {p2}, {orientation}): {color}")

    #draw.ellipse((p1, p2), outline=color, width=3)

    if numRecursions == 0:
        pass
    else:
        # ---- 4 recursions ----
        xmin, xmax = p1[0], p2[0]
        ymin, ymax = p1[1], p2[1]
        
        y_width = ymax - ymin
        x_width = xmax - xmin
        fraction_near = sizes[numRecursions - 1] / sizes[numRecursions] 
        x_step = fraction_near * x_width
        y_step = fraction_near * y_width
        x_connect = x_width * (1 - 2 * fraction_near)
        y_connect = y_width * (1 - 2 * fraction_near)        

        recursion_zones = [
            ((xmin, ymin + y_step + y_connect), (xmin + x_step, ymax)), # bottom left
            ((xmin + x_step + x_connect, ymin + y_step + y_connect), (xmax, ymax)), # bottom right
            ((xmin, ymin), (xmin + x_step, ymin + y_step)), # up left
            ((xmin + x_step + x_connect, ymin), (xmax, ymin + y_step)), # up right
        ]

        def rot(zones, qtrs):
            # print()
            # print('zones', zones, type(zones))
            # print('n', n, type(n))
            # print('qtrs', qtrs, type(qtrs))

            ret = []

            for i in range(0, 4):
                index = (i - qtrs) % 4
                ret.append(zones[index])

            return ret

        tester = [10, 20, 30, 40]
        print(tester)
        print(rot(tester, 1))
        print(rot(tester, 2))
        print(rot(tester, 3))
        raise 

        shifties = rot(recursion_zones, orientation.value)
        print(f"shifties = {shifties}")

        # 2 bottoms match orientation with parent
        # bottom left
        print(f"bottom left")
        hilby(draw, numRecursions - 1, *shifties[0], orientation)

        # bottom right
        print(f"bottom right")
        hilby(draw, numRecursions - 1, *shifties[1], orientation)

        # # up left is rotated counter-clockwise
        # print(f"up left")
        # hilby(draw, numRecursions - 1, *shifties[2], ccwise(orientation))

        # # up right is rotated clockwise
        print(f"up right")
        hilby(draw, numRecursions - 1, *shifties[3], cwise(orientation))


        # ---- 3 connections ----
        # 2 side connectors are on the outside
        if orientation in (Orientation.UP, Orientation.DOWN):
            # left and right walls
            draw.line((
                (xmin, ymin + y_step), 
                (xmin, ymin + y_step + y_connect)
            ), fill=color, width=4)
            draw.line((
                (xmax, ymin + y_step), 
                (xmax, ymin + y_step + y_connect)
            ), fill=color, width=4)
        else:
            # top and bottom walls
            draw.line((
                (xmin + x_step, ymin),
                (xmin + x_step + x_connect, ymin)
            ), fill=color, width=4)
            draw.line((
                (xmin + x_step, ymax),
                (xmin + x_step + x_connect, ymax)
            ), fill=color, width=4)

        # 1 middle connector is in the middle
        up_left =    (xmin + x_step,                ymin + y_step)
        up_right =   (xmin + x_step + x_connect,    ymin + y_step)
        down_left =  (xmin + x_step,                ymin + y_step + y_connect)
        down_right = (xmin + x_step + x_connect,    ymin + y_step + y_connect)
        draw.line((
            up_left if orientation in (Orientation.DOWN, Orientation.RIGHT) else down_right,
            up_right if orientation in (Orientation.DOWN, Orientation.LEFT) else down_left
        ), fill=color, width=4)

    print(f"<-EXIT hilby(draw, {numRecursions}, {p1}, {p2}, {orientation}): {color}")


def main():
    images = []
    frame_count = 0

    frame_count = 1

    while frame_count < FRAME_MAX:
        print(f"calc frame {frame_count}")

        im = Image.new('RGB', (WIDTH, WIDTH), BLACK)
        frame = im.load()
        draw = ImageDraw.Draw(im)

        hilby(draw, 3, (XMIN + MARGIN, YMIN + MARGIN), (XMAX - MARGIN, YMAX - MARGIN), Orientation.UP)

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
