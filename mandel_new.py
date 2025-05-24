import math
from datetime import datetime

import moviepy.editor as mp
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.load_default()

# this is the core of the mandelbrot: z -> z*2 + c per iteration
def when_exit(z, c):
    i = 0
    while(abs(z) < 2 and i < MAX_IT):
        z = z * z + c
        i += 1
    return i  

def colors_list():
    blues = []
    reds = []
    whites = []
    for i in range(0, 16):
        val = i * 15
        blues.append((0, 0, val))
        reds.append((val, 0, 255-val))
        whites.append((val, val, val))
    return blues + reds

# evolving location in the complex plane of c
THETA0 = 0    # ?in radians?
R0 = 0
DTHETA_DR = 2 * math.pi * 10   # once round every 0.1 r  
DR_PER_STEP = 0.001            # +1r over 1000 steps

# fixed square of z, the position that evolves over z->z**2+c
XMIN = -2
XMAX = 2
YMIN = -2
YMAX = 2

# how that chunk of complex z is laid on screen
FRAME_WIDTH_PIXELS = 400

# animation time: STEPS IS t IN THE VIDEO
MAX_STEPS = 2000

# mandel iteration: iterations are per image frame, per pixel
MAX_IT = 64  # max number of iterations of z->z**2+c per pixel

# speed factor configs
DEEP_IT_CNT_THRESH = 32

def main():
    images = []

    black = (0, 0, 0)
    white = (255, 255, 255)
    theta = THETA0
    r = R0

    steps = 0
    last = datetime.now()
    colors = colors_list()
    sign_dr = 1

    # speed factor math
    tot_it = 0
    deep_cnt = 0

    print(f"START: r0={r} theta0={theta} sign_dr={sign_dr}")

    while steps < MAX_STEPS:
        im = Image.new('RGB', (FRAME_WIDTH_PIXELS, FRAME_WIDTH_PIXELS), black)
        px = im.load()            
        c = complex(r * math.sin(theta), r * math.cos(theta))

        for i in range(0, FRAME_WIDTH_PIXELS):
            for j in range(0, FRAME_WIDTH_PIXELS):
                x = XMIN + (i/FRAME_WIDTH_PIXELS) * (XMAX - XMIN)
                y = YMIN + (j/FRAME_WIDTH_PIXELS) * (YMAX - YMIN)
                z = complex(x, y)
                cnt = when_exit(z, c)

                tot_it += cnt
                if cnt == MAX_IT or cnt == 0:
                    color = black
                else:
                    if cnt > DEEP_IT_CNT_THRESH:
                        deep_cnt += 1
                    color = colors[cnt % 48]
                px[i, j] = color

        d = ImageDraw.Draw(im)

        # add text showing where we're at onto the image
        d.multiline_text((10,10), f"[{r:.3f} {theta:.3f}]", font=font, fill=white)

        # append image to image list
        images.append(im)

        print(f"[{steps}]")

        # step
        r += sign_dr * DR_PER_STEP
        theta += DTHETA_DR * DR_PER_STEP
        steps += 1

    print("END")

    file_base = f"zoom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    gif = f"{file_base}.gif"
    print(f"writing gif: {gif}")
    images[0].save(gif, save_all=True, append_images=images[1:], optimize=False, duration=100, loop=0)
    mp4 = f"{file_base}.mp4"
    print(f"converting to mp4: ./{mp4}")
    video = mp.VideoFileClip(gif)
    video.write_videofile(mp4)


if __name__ == "__main__":
    main()
