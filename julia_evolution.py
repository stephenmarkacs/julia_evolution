import math
import sys
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

# iterations and timing
MAX_IT = 256
AVG_IT_REF = MAX_IT / 2
HIGH_IT_THRESH = 85
HIGH_IT_FACTOR = 100
LOW_IT_THRESH = 70
LOW_IT_FACTOR = 35
DEEP_CNT_THRESH = 15
LOW_DEEP_THRESH = 0.06
HIGH_DEEP_THRESH = 0.3
DEEP_ADJUST = 3.2
DURATION = 100

#theta
THETA0 = 5.95
DTHETA_BASE = 2 * math.pi / 2400
THETA_REF = DTHETA_BASE / AVG_IT_REF
THETA_FACTOR_EXP = 0.7

#r
RMIN = 0.678
RMAX = 0.68168
DRDTHETA = 0.1 / math.pi

# canvas 
W = 800
XMIN = -1.4
XMAX = 1.4
YMIN = -1.4
YMAX = 1.4



font = ImageFont.load_default()

def it_factor_final(it_factor, deep_factor):
    if it_factor > HIGH_IT_THRESH:
        ret =  HIGH_IT_FACTOR
    elif it_factor < LOW_IT_THRESH:
        ret = LOW_IT_FACTOR
    else:
        ret = (
            LOW_IT_FACTOR + 
            (HIGH_IT_FACTOR - LOW_IT_FACTOR) * (it_factor - LOW_IT_THRESH) / (HIGH_IT_THRESH - LOW_IT_THRESH)
        )

    if deep_factor > HIGH_DEEP_THRESH:
        adjust = DEEP_ADJUST
    elif deep_factor > LOW_DEEP_THRESH:
        adjust = 1 + (DEEP_ADJUST - 1) * (deep_factor - LOW_DEEP_THRESH) / (HIGH_DEEP_THRESH - LOW_DEEP_THRESH)
    else:
        adjust = 1

    return ret / adjust

def when_exit(z, c):
    i = 0
    while(abs(z) < 2 and i < MAX_IT):
        z = z * z + c
        i += 1
    return i  

def colors_list():
    blues = []
    reds = []
    for i in range(1, 16):
        val = i * 17
        blues.append((0, 0, val))
        reds.append((val, 0, 255-val))
    return blues + reds

def main(filename_base):
    images = []

    black = (0, 0, 0)
    white = (255, 255, 255)
    theta = THETA0
    r = RMIN
    step_cnt = 1
    last = datetime.now()
    colors = colors_list()
    sign_dr = 1

    print(f"START: r0={r} theta0={theta} DTHETA_BASE={DTHETA_BASE} THETA_REF={THETA_REF}")

    while r >= RMIN and r <= RMAX:
        im = Image.new('RGB', (W, W), black)
        px = im.load()            
        c = complex(r * math.sin(theta), r * math.cos(theta))
        tot_it = 0
        deep_cnt = 0

        for i in range(0, W):
            for j in range(0, W):
                x = XMIN + (i/W) * (XMAX - XMIN)
                y = YMIN + (j/W) * (YMAX - YMIN)
                z = complex(x, y)
                cnt = when_exit(z, c)
                tot_it += cnt
                if cnt == MAX_IT or cnt == 0:
                    color = black
                else:
                    if cnt > DEEP_CNT_THRESH:
                        deep_cnt += 1
                    color = colors[cnt % 30]
                px[i, j] = color

        d = ImageDraw.Draw(im)

        now = datetime.now()
        it_factor = tot_it / (W*W)
        deep_factor = deep_cnt / (W*W)
        it_factor_used = it_factor_final(it_factor, deep_factor)
        # d.multiline_text((10,10), f"{r:.3f} {theta:.3f} {deep_factor:.3f} {it_factor:.3f} {it_factor_used:.3f}", font=font, fill=white)
        d.multiline_text((10,10), f"{r:.3f} {theta:.3f}", font=font, fill=white)
        images.append(im)

        print(now - last, step_cnt, r, theta, c, tot_it, it_factor, it_factor_used)

        dtheta = THETA_REF * it_factor_used
        #print(f"dtheta={dtheta} DRDTHETA={DRDTHETA}")
        theta += dtheta
        dr = sign_dr * DRDTHETA * dtheta
        #print(f"dr={dr}")
        r += dr
        if r > RMAX:
            sign_dr = -sign_dr
        step_cnt += 1
        last = now


    print("END")
    print(f"THETA={theta}")
    images[0].save(f"{filename_base}{datetime.now().strftime('%Y%m%d%H%M%S')}.gif",
                save_all=True, append_images=images[1:], optimize=False, duration=DURATION, loop=0)

if __name__ == "__main__":
    main(sys.argv[1])
