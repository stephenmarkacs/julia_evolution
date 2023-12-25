from datetime import datetime
from math import cos, pi, sin
from numba import jit
from enum import Enum

import moviepy.editor as mp
from PIL import Image, ImageDraw, ImageFont

num_nodes = [0]
for i in range(1, 40):
    num_nodes.append((4 * num_nodes[-1]) + 3)
print(f"num_nodes: {num_nodes}")

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
COLORS = [(4*i, 256-(4*i), 64) for i in range(0,64)]
REDS = [(64 + 48 * i, 32, 64) for i in range(0,4)]
GREENS = [(32, 64 + 48 * i, 64) for i in range(0,4)]

# iteration and timing
RECURSION_DEPTH = 5
FRAME_MAX = 256
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

frame_count = 0

def hilby(draw, numRecursions, minIndex, chirality, p1, p2, orientation):
    global frame_count
    if numRecursions < 0:
        return 

    color = RED if numRecursions % 3 == 0 else GREEN if numRecursions % 3 == 1 else BLUE
    #print(f"ENTER hilby(draw, {numRecursions}, {minIndex}, {chirality}, {p1}, {p2}, {orientation}): {color}")

    #draw.ellipse((p1, p2), outline=color, width=3)

    indexOffset = minIndex - 1

    if numRecursions == 0:
        color_index = -(minIndex + frame_count) % 64
        if color_index < 4 or (color_index + 32) % 64 < 4:
            ellipse_size = 5
            color = REDS[color_index] if color_index < 4 else GREENS[(color_index + 32) % 64]
            #print(f"ELLIPSE: ({p1}, {p2})")
            draw.ellipse((
                        (p1[0] - ellipse_size, p1[1] - ellipse_size), 
                        (p2[0] + ellipse_size, p2[1] + ellipse_size), 
                        ), 
                        outline=color, 
                        width=2)
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
            ((xmin + x_step + x_connect, ymin), (xmax, ymin + y_step)), # up right
            ((xmin, ymin), (xmin + x_step, ymin + y_step)), # up left
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

        shifties = rot(recursion_zones, orientation.value)
        #print(f"shifties = {shifties}")

        index0 = 1
        index1 = 2**(2 * numRecursions)
        index2 = 2 * index1
        index3 = 3 * index1

        # up left is rotated counter-clockwise
        hilby(draw, 
              numRecursions - 1, 
              indexOffset + (index0 if chirality else index3), 
              not chirality, 
              *shifties[3], 
              ccwise(orientation)
        )

        # bottom left
        hilby(draw, 
              numRecursions - 1,
              indexOffset + (index1 if chirality else index2), 
              chirality, 
              *shifties[0], 
              orientation
        )

        # bottom right
        hilby(draw, 
              numRecursions - 1, 
              indexOffset + (index2 if chirality else index1), 
              chirality, 
              *shifties[1], 
              orientation
        )

        # up right is rotated clockwise
        hilby(draw, 
              numRecursions - 1, 
              indexOffset + (index3 if chirality else index0), 
              not chirality, 
              *shifties[2], 
              cwise(orientation)
        )

        line_width = 1

        # ---- 3 connections ----

        # 2 side connectors are on the outside
        if orientation in (Orientation.UP, Orientation.DOWN):
            # left and right walls
            draw.line((
                (xmin, ymin + y_step), 
                (xmin, ymin + y_step + y_connect)
            ), fill=WHITE, width=line_width)
            draw.line((
                (xmax, ymin + y_step), 
                (xmax, ymin + y_step + y_connect)
            ), fill=WHITE, width=line_width)
        else:
            # top and bottom walls
            draw.line((
                (xmin + x_step, ymin),
                (xmin + x_step + x_connect, ymin)
            ), fill=WHITE, width=line_width)
            draw.line((
                (xmin + x_step, ymax),
                (xmin + x_step + x_connect, ymax)
            ), fill=WHITE, width=line_width)

        # 1 middle connector is in the middle
        up_left =    (xmin + x_step,                ymin + y_step)
        up_right =   (xmin + x_step + x_connect,    ymin + y_step)
        down_left =  (xmin + x_step,                ymin + y_step + y_connect)
        down_right = (xmin + x_step + x_connect,    ymin + y_step + y_connect)
        draw.line((
            up_left if orientation in (Orientation.DOWN, Orientation.RIGHT) else down_right,
            up_right if orientation in (Orientation.DOWN, Orientation.LEFT) else down_left
        ), fill=WHITE, width=line_width)

    #print(f"<-EXIT hilby(draw, {numRecursions}, {minIndex}, {chirality}, {p1}, {p2}, {orientation}): {color}")


def main():
    images = []
    global frame_count

    while frame_count < FRAME_MAX:
        print(f"calc frame {frame_count}")

        im = Image.new('RGB', (WIDTH, WIDTH), BLACK)
        frame = im.load()
        draw = ImageDraw.Draw(im)

        hilby(draw, 
              RECURSION_DEPTH, # recursion depth
              1, # starting index
              True, # chirality flag
              (XMIN + MARGIN, YMIN + MARGIN), (XMAX - MARGIN, YMAX - MARGIN), # bounding box
              Orientation.UP # direction this current U opens to
        )

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
