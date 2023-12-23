from datetime import datetime
from math import cos, pi, sin
from numba import jit

import moviepy.editor as mp
from PIL import Image, ImageDraw, ImageFont

i = complex(0, 1)

# fractal rules
EXPONENT = 7

# iterations and timing
MAX_IT = 1024
DURATION = 100
JUMP_OUT_RADIUS = 2

# factor controls
CURVE_COEFF = 5.
CURVE_BUMP_START = 10
CURVE_BUMP_END = 25

BLACK_COEFF = 5.
BLACK_BUMP_START = 0.05
BLACK_BUMP_END = 0.15

THETA_COEFF = 0.0      # height of peak theta factor
THETA_TARGET = 0.6640  # in pi radians, the peak of theta_factor
THETA_WIDTH = 0.0042   # width of ramps down

#colors
NUM_COLORS = 32

#theta
THETA0 = 0
TICKS_PER_CIRCLE = 720
DTHETA_BASE = (2 * pi) / TICKS_PER_CIRCLE

#r
RMIN = 0.644
RMAX = 0.649
DRDTHETA = 0 # 0.06 / pi
SIGN_DR = -1

# canvas
W = 500
XMIN = -1.4
XMAX = 1.4
YMIN = -1.4
YMAX = 1.4

font = ImageFont.load_default()

################# speed adjustment factors ###################
# all XXX_factor fns should output in range 0 - 1

@jit(nopython=True)
def curve_factor_fn(iter_cnt):
    if iter_cnt < CURVE_BUMP_START:
        return 0
    elif iter_cnt < CURVE_BUMP_END:
        return 1
    else:
        return 0

@jit(nopython=True)
def black_factor_fn(black_fraction):
    if black_fraction < BLACK_BUMP_START:
        return 0
    elif black_fraction < BLACK_BUMP_END:
        return 1
    else:
        return 0

@jit(nopython=True)
def theta_factor_fn(theta):
    theta_diff = abs(theta/pi - THETA_TARGET)
    if theta_diff < THETA_WIDTH:
        return 1
    elif theta_diff < 2 * THETA_WIDTH:
        return 1 - (theta_diff - THETA_WIDTH) / THETA_WIDTH
    else:
        return 0

# @jit(nopython=True)
# def ramp(a, b, va, vb, x):
#     if x <= a:
#         return va
#     if x >= b:
#         return vb
#     return va + ((x - a) / (b - a)) * vb

@jit(nopython=True)
def when_exit(z, c):
    i = 0
    while(abs(z) < JUMP_OUT_RADIUS and i < MAX_IT):
        z = z**EXPONENT + c
        i += 1

    return i

@jit(nopython=True)
def f(x):
    return min(255, x) # highlight clipping

# to not cycle, just call this once before the time loop
def colors_cycle(n):
    blues = []
    reds = []
    for i in range(0, int(NUM_COLORS / 2)):
        val = i * (int(NUM_COLORS / 2) + 1)
        blues.append((0, f(int(val/5)), val))
        reds.append((val, int(val/3), int((255-val) * 0.75)))

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
    r = RMIN if SIGN_DR >= 0 else RMAX
    step_cnt = 1
    total_delta_theta = 0
    last = datetime.now()
    sign_dr = SIGN_DR

    num_pixels = W*W

    print(f"START: r0={r} theta0={theta} DTHETA_BASE={DTHETA_BASE}")
    print(f"RMIN={RMIN} RMAX={RMAX} DRDTHETA={DRDTHETA} W={W}")

    # colors = colors_cycle(1)

    # while r >= RMIN and r <= RMAX:
    while total_delta_theta <= 2 * pi:
        frame_count += 1
        colors = colors_cycle(int(frame_count / 5))
        im = Image.new('RGB', (W, W), black)
        px = im.load()
        c = complex(r * cos(theta), r * sin(theta))
        curve_factor = 0.
        black_count = 0.

        for i in range(0, W):
            #last_count = None   # for gradient factors
            for j in range(0, W):
                x = XMIN + (i/W) * (XMAX - XMIN)
                y = YMIN + (j/W) * (YMAX - YMIN)
                z = complex(x, y)
                cnt = when_exit(z, c) # julia
                #cnt = when_exit(c, z) # standard mandelbrot

                # if last_count is not None:
                #     gradient_count += abs(cnt - last_count)

                if cnt >= MAX_IT or cnt == 0:
                    color = black
                    black_count += 1
                else:
                    # if cnt > DEEP_CNT_THRESH:
                    #     deep_cnt += 1
                    color = colors[cnt % NUM_COLORS]
                    curve_factor += curve_factor_fn(cnt)

                px[i, j] = color
                # last_count = cnt

        # normalize to avg curve factor
        curve_factor /= num_pixels   
        black_fraction = black_count / num_pixels
        black_factor = black_factor_fn(black_fraction)
        theta_factor = theta_factor_fn(theta)

        d = ImageDraw.Draw(im)
        d.multiline_text((10, 10), f"z -> z**1.5 + c, z0(pixel), c(t)")
        d.multiline_text((10,28), f"{XMIN:.1f}<x<{XMAX:.1f} {YMIN:.1f}<y<{YMAX:.1f}", font=font, fill=white)
        d.multiline_text((10,46), f"r:{r:.5f} theta/pi:{(theta / pi):.4f}", font=font, fill=white)
        d.multiline_text((10,64), f"curve: {curve_factor:.3f} {'*'*int(20 * curve_factor)}", font=font, fill=white)
        d.multiline_text((10,82), f"black:{black_fraction:.3f} {black_factor:.3f} {'*'*int(20 * black_factor)}", font=font, fill=white)
        d.multiline_text((10,100), f"theta: {theta_factor:.3f} {'*'*int(20 * theta_factor)}", font=font, fill=white)

        PAD = 20
        PLOT_R = 40
        plot_c(d, W-PAD-PLOT_R, PAD+PLOT_R, PLOT_R, c)

        images.append(im)

        final_factor = (1 + CURVE_COEFF * curve_factor) * (1 + BLACK_COEFF * black_factor) * (1 + THETA_COEFF * theta_factor)

        now = datetime.now()
        print(now - last, step_cnt, r, theta / pi, c, curve_factor, black_factor, theta_factor, final_factor)

        dtheta = DTHETA_BASE / final_factor
        theta += dtheta
        total_delta_theta += dtheta
        if theta > 2 * pi:
            theta -= 2 * pi
        dr = sign_dr * DRDTHETA * dtheta
        r += dr
        # print(f"curve={curve_factor:.3f} black={black_factor:.3f} final={final_factor:.3f} dtheta={dtheta:.3f} dr={dr:.3f}")

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
    print(f"converting to mp4: ./{mp4}")
    video = mp.VideoFileClip(gif)
    video.write_videofile(mp4)

if __name__ == "__main__":
    main()

