from datetime import datetime
from math import ceil, floor, cos, pi, sin
from socket import RCVALL_MAX

import moviepy.editor as mp
from PIL import Image, ImageDraw, ImageFont

i = complex(0, 1)

def c_sin(z: complex):
    return sin(z.real) * cos(i * z.imag) + cos(z.real) * sin(i * z.imag)

def c_cos(z: complex):
     return cos(z.real) * cos(i * z.imag) - sin(z.real) * sin(i * z.imag)

# fractal rules
EXPONENT = 2

# iterations and timing
MAX_IT = 128
AVG_IT_REF = MAX_IT / 2
HIGH_IT_THRESH = 85
HIGH_IT_FACTOR = 100
LOW_IT_THRESH = 70
LOW_IT_FACTOR = 35
DEEP_CNT_THRESH = 500
LOW_DEEP_THRESH = 0.01
HIGH_DEEP_THRESH = 0.03
DEEP_ADJUST = 6.0
GRADIENT_NEUTRAL = 10.0 # avg gradient, gets no adjust
GRADIENT_SCALE = 3.5    # how much to slow by gradient
GRADIENT_ADJUST_MIN = 0.2
BLACK_SCALE = 1.2       # how much to slow by blackness
BLACK_FACTOR_MIN = 0.005
BLACK_FACTOR_MAX = 0.02
DURATION = 100
JUMP_OUT_RADIUS = 2

#colors
NUM_COLORS = 32

#theta
THETA0 = 0 * pi
TICKS_PER_CIRCLE = 100
DTHETA_BASE = (2 * pi) / TICKS_PER_CIRCLE # but there's another factor, reduce this logic!
THETA_REF = DTHETA_BASE / AVG_IT_REF # AVG_IT_REF sure looks like its doing the same as TICKS_PER_CIRCLE

#r
RMIN = 0.2
DRDTHETA = 0.1 / pi
RMAX = 1.0

# canvas 
W = 400
XMIN = -1.4
XMAX = 1.4
YMIN = -1.4
YMAX = 1.4

font = ImageFont.load_default()

# speed adjustment factor
def it_factor_final(it_factor, deep_factor, gradient_factor, black_factor):
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

    gradient_adjust = max(GRADIENT_ADJUST_MIN, GRADIENT_SCALE * gradient_factor / GRADIENT_NEUTRAL)
    adjust *= gradient_adjust    

    black_adjust = BLACK_SCALE * BLACK_FACTOR_MAX / max(BLACK_FACTOR_MIN, min(black_factor, BLACK_FACTOR_MAX))
    adjust /= black_adjust

    return ret / adjust   # speed 

def when_exit(z, c):
    i = 0
    while(abs(z) < JUMP_OUT_RADIUS and i < MAX_IT):
        z = z**EXPONENT + c
        i += 1

    return i

def f(x):
    return min(255, x) # highlight clipping

def colors_cycle(n):
    blues = []
    reds = []
    for i in range(0, int(NUM_COLORS / 2)):
        val = i * (int(NUM_COLORS / 2) + 1)
        blues.append((0, f(16 + int(val/5)), val))
        reds.append((val, int(val/2), int((255-val) * 0.65)))
    
    uncycled = blues + reds

    # twist: rot(n)
    cycled = [None,] * NUM_COLORS
    for i in range(0, NUM_COLORS):
        rot = (n + i) % NUM_COLORS
        cycled[rot] = uncycled[i]

    return cycled

def plot_c(d: ImageDraw.ImageDraw, x, y, r, c: complex):
    d.ellipse([(x-r, y-r), (x+r, y+r)], outline=(256,256,256), width=2)
    cx = x + c.real * r
    cy = y + c.imag * r
    d.ellipse([(cx-2, cy-2), (cx+2, cy+2)], fill=(256, 256, 256))

def main():
    images = []
    frame_count = 0

    black = (0, 0, 0)
    white = (255, 255, 255)
    theta = THETA0
    r = RMIN
    step_cnt = 1
    last = datetime.now()
    sign_dr = 1

    print(f"START: r0={r} theta0={theta} DTHETA_BASE={DTHETA_BASE} THETA_REF={THETA_REF}")
    print(f"RMIN={RMIN} RMAX={RMAX} DRDTHETA={DRDTHETA} W={W}")

    # currently not cycling colors, so just get the colors once up front
    colors = colors_cycle(1)

    while r >= RMIN and r <= RMAX:
        frame_count += 1
        #colors = colors_cycle(frame_count)
        #print(f"colors: {colors}")
        im = Image.new('RGB', (W, W), black)
        px = im.load()            
        c = complex(r * cos(theta), r * sin(theta))
        tot_it = 0
        deep_cnt = 0
        gradient_count = 0
        black_count = 0

        for i in range(0, W):
            last_count = None
            for j in range(0, W):
                x = XMIN + (i/W) * (XMAX - XMIN)
                y = YMIN + (j/W) * (YMAX - YMIN)
                z = complex(x, y)
                cnt = when_exit(z, c) # julia
                #cnt = when_exit(c, z) # standard mandelbrot
                if last_count is not None:
                    gradient_count += abs(cnt - last_count)
                tot_it += cnt
                if cnt >= MAX_IT or cnt == 0:
                    color = black
                    black_count += 1
                else:
                    if cnt > DEEP_CNT_THRESH:
                        deep_cnt += 1 
                    color = colors[cnt % NUM_COLORS]

                px[i, j] = color
                last_count = cnt

        d = ImageDraw.Draw(im)

        now = datetime.now()
        num_pixels = W*W
        it_factor = tot_it / num_pixels
        deep_factor = float(deep_cnt) / num_pixels  # the deep count really just reduces the count to a binary (crossed thresh or not)
        black_factor = float(black_count) / num_pixels
        gradient_factor = gradient_count / num_pixels  # average interpixel count delta
        it_factor_used = it_factor_final(it_factor, deep_factor, gradient_factor, black_factor)
        #d.multiline_text((10,10), f"z(n+2) = z(n+1)^2 + {double_delay_strength:.2f} * z(n) + c")
        d.multiline_text((10,10), f"{XMIN:.1f}<x<{XMAX:.1f} {YMIN:.1f}<y<{YMAX:.1f}", font=font, fill=white)
        d.multiline_text((10,28), f"r:{r:.5f} theta/pi:{(theta / pi):.3f}", font=font, fill=white)
        # d.multiline_text((10,46), f"deep_factor:{deep_factor:.2f}", font=font, fill=white)
        # d.multiline_text((10,64), f"it_factor:{it_factor:.2f}", font=font, fill=white)
        d.multiline_text((10,46), f"if: {it_factor:.1f}, df: {deep_factor:.3f}", font=font, fill=white)
        d.multiline_text((10,64), f"bf: {black_factor:.3f}, gf: {gradient_factor:.1f}", font=font, fill=white)
        d.multiline_text((10,82), f"speed:{it_factor_used:.1f}", font=font, fill=white)

        PAD = 10
        PLOT_R = 40
        plot_c(d, W-PAD-PLOT_R, PAD+PLOT_R, PLOT_R, c)

        images.append(im)

        print(now - last, step_cnt, r, theta / pi, c, tot_it, it_factor, it_factor_used)

        dtheta = THETA_REF * it_factor_used
        #print(f"dtheta={dtheta} DRDTHETA={DRDTHETA}")
        theta += dtheta
        if theta > 2 * pi:
            theta -= 2 * pi
        dr = sign_dr * DRDTHETA * dtheta
        #print(f"dr={dr}")
        r += dr

        # to turn around, if we are terminating based on something other than R
        # if r > RMAX:
        #     sign_dr = -sign_dr

        step_cnt += 1
        last = now
        
    print("END")
    print(f"THETA={theta}")
    file_base = f"mandelish{datetime.now().strftime('%Y%m%d%H%M%S')}"
    gif = f"{file_base}.gif"
    print(f"writing gif: {gif}")
    images[0].save(gif, save_all=True, append_images=images[1:], optimize=False, duration=DURATION, loop=0)
    mp4 = f"{file_base}.mp4"
    print(f"converting to mp4: {mp4}")
    video = mp.VideoFileClip(gif)
    video.write_videofile(mp4)

if __name__ == "__main__":
    main()


# @tonyophuans interesting locations list
# {-.432,.580}, {.23,.56}, {.33,.05}, {-.75,.11}, {-.1,.651}
# , {-.4,-.6}, {-1.26,.38}, {-1.19,.3}, {-.16,1.04}, {-.04,-.99}
# , {-.36,.64}, {-.1,-.92}, {-.5125,.5215}, {.285,.01}, {-.7454,.113}
# , {-.7269,.1889}, {-.75,.11}, {.5,.25}, {.3968,-.3628}, {.3511,-.3867}
# , {.285,.013}, {-.4044,.6133}, {-.7511,.08}, {-.7778,-.1244}, {-1.2178,-.1333}
# , {-1.1956,-.1733}, {.2978,-.0089}, {.3467,-.04}, {.3556,-.3556}, {.3556,-.3467}
# , {.3244,-.4267}, {.2844,-.48}, {.1822,-.5911}, {.0933,-.6178}, {.0667,-.6222}
# , {-.0311,-.6933}, {-.0756,-.6578}, {-.0444,-.8044}, {-1.34882,-.454238}, {.34,-.05}
# , {.37,.1}, {.355,.355}, {-.54,.54}, {-.52,.57}, {.355534,-.337292}
# , {-.12,-.77}, {-1.476,0}, {.28,.008}, {.3,-.01}, {-.162,1.04}
# //50
# , {-.79,.15}, {-.624,.435}, {.295,.55}, {-.12,.75}, {-1.037,.17}
# , {-.20242,.39527}, {.38,.333}, {-.36,.62}, {-.67,.34}, {0,1}
# , {-.75,0}, {-.391,-.587}, {-0.755,0.15},{0.563, 0.0}, {-.7589,-.0753}
# , {-.16012,1.037572}, {1,.3}