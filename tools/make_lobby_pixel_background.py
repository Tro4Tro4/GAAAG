"""Draws the Lobby background as pixel art, at the game's own 384x216.

This replaces the painted image. One texture pixel is one game unit, the filter
stays Nearest, and the wall behind Lino is made of the same size of pixel he
is: that is the whole point of the change.

Two things carry the look, and both are about restraint.

Ramps, not fills. Each material is five tones whose hue turns as it darkens —
shadows swing violet, lights swing warm — because a colour that is merely
darkened reads as grey plastic.

Dithering at the edges only. A first version dithered every gradient across its
whole width and the result was a screen door: at this resolution a large field
of alternating pixels reads as noise, not as shading. Here a gradient is
quantised into flat bands and only the narrow strip where two bands meet is
dithered, which is how the technique is meant to be used — the flat areas stay
flat and the eye reads a soft transition anyway.

The room is lit by one fluorescent tube slightly left of centre. Every shadow
points away from it and the floor carries its reflection: a light source that
does not touch the floor reads as painted on.

Run from the project root:  python tools/make_lobby_pixel_background.py
"""
import colorsys

import numpy as np
from PIL import Image

ASSET = "assets/backgrounds/bg_lobby.png"
W, H = 384, 216
FLOOR_Y = 136
SKIRT_H = 7
DOOR_X, DOOR_W, DOOR_TOP, DOOR_BOT = 313, 26, 102, 146
NEON_X, NEON_Y, NEON_W = 170, 9, 80
VP_X, VP_Y = 176, 96              # vanishing point for the floor

rng = np.random.default_rng(1994)

BAYER = np.array([
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]) / 64.0


def ramp(shadow, light, n=5):
    a = colorsys.rgb_to_hsv(*[v / 255 for v in shadow])
    b = colorsys.rgb_to_hsv(*[v / 255 for v in light])
    out = []
    for i in range(n):
        t = i / (n - 1)
        out.append(tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(
            a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)))
    return out


WALL = ramp((56, 46, 70), (186, 174, 198))
FLOOR = ramp((34, 30, 44), (146, 136, 130))
SKIRT = ramp((28, 24, 38), (92, 84, 104))
DOOR = ramp((40, 42, 52), (172, 180, 186))
NEON = ramp((92, 172, 168), (236, 255, 250))
RUST = ramp((62, 44, 40), (146, 104, 72))
BRASS = ramp((92, 78, 44), (232, 214, 150))
INK = (24, 20, 32)


def banded(field, pal, width=0.34):
    """Quantises a 0..1 field onto a ramp, dithering only where bands meet.

    `width` is how much of each step is allowed to dither. Small values give
    hard bands; at 1.0 this degenerates into ordered dithering everywhere,
    which is the thing being avoided.

    Do not add random noise to a field before banding it. Noise near a band
    boundary scatters single pixels across the whole width of the noise, and
    that reads as dirt rather than as texture — it is what made the first two
    attempts look like a screen door. Ordered dithering gives a regular weave,
    which is the thing that reads as shading; if a surface needs tooth, give it
    tooth deliberately, in shapes.
    """
    h, w = field.shape
    tile = np.tile(BAYER, (h // 8 + 1, w // 8 + 1))[:h, :w]
    level = np.clip(field, 0, 1) * (len(pal) - 1)
    base = np.floor(level)
    frac = level - base
    # Only the middle `width` of the step is mixed; outside it, snap to a band.
    t = np.clip((frac - (0.5 - width / 2)) / max(width, 1e-6), 0, 1)
    idx = np.clip(base + (tile < t), 0, len(pal) - 1).astype(int)
    return np.array(pal, dtype=np.uint8)[idx]


def put(img, y, x, colour):
    if 0 <= y < H and 0 <= x < W:
        img[y, x] = colour


def main():
    img = np.zeros((H, W, 3), dtype=np.uint8)

    # ---------------------------------------------------------------- wall ---
    yy, xx = np.mgrid[0:FLOOR_Y, 0:W]
    cx = NEON_X + NEON_W / 2
    # The cone from the tube, plus grime low down and in the corners. A wall is
    # dirtiest where mops and shoulders reach it, and that gradient alone is
    # what stops a big flat surface from reading as cardboard.
    dy = np.clip(yy / FLOOR_Y, 0, 1)
    cone = np.clip(1 - np.abs(xx - cx) / (70 + dy * 300), 0, 1)
    lit = 0.30 + cone * 0.62 - dy * 0.22
    lit -= np.clip(1 - np.minimum(xx, W - xx) / 64, 0, 1) * 0.14
    img[:FLOOR_Y] = banded(lit, WALL)

    # Damp blooms. Lighter than the wall, not darker: a stain on painted
    # plaster leaches the colour out rather than making a hole, and the first
    # version drew them dark and they read as craters.
    for bx, by, r in ((46, 62, 19), (206, 44, 24), (238, 88, 14),
                      (100, 106, 12), (344, 34, 16), (296, 116, 10)):
        for y in range(max(0, by - r - 4), min(FLOOR_Y, by + r + 5)):
            for x in range(max(0, bx - r - 5), min(W, bx + r + 6)):
                wob = 0.16 * np.sin(x * 0.55 + y * 0.3) + 0.12 * np.sin(y * 0.8)
                d = ((x - bx) / r) ** 2 + ((y - by) / (r * 0.68)) ** 2 + wob
                if d < 0.55:
                    img[y, x] = WALL[3]
                elif d < 1.0 and BAYER[y % 8, x % 8] < 0.75:
                    img[y, x] = WALL[3]
                elif d < 1.25 and BAYER[y % 8, x % 8] < 0.35:
                    img[y, x] = WALL[1]

    # Rust runs: something above has been leaking for years. Drawn as thin
    # tapering streaks so they read as flow, not as scratches.
    for rx, ry, ln in ((228, 22, 46), (232, 22, 30), (92, 40, 26), (350, 50, 34)):
        for i in range(ln):
            t = i / ln
            put(img, ry + i, rx + int(np.sin(i * 0.35) * 1.4), RUST[1 if t < 0.6 else 2])
            if t < 0.45:
                put(img, ry + i, rx + 1 + int(np.sin(i * 0.35) * 1.4), RUST[3])

    # Cracks: a walk that mostly goes down, with a lit pixel on one side of the
    # upper half so it reads as an opening rather than a drawn line.
    for sx, sy, steps in ((80, 14, 58), (266, 20, 44), (152, 66, 28),
                          (336, 70, 30), (20, 92, 20)):
        x, y = sx, sy
        for i in range(steps):
            put(img, y, x, INK)
            if i < steps * 0.55:
                put(img, y, x + 1, WALL[4])
            y += 1
            x += int(rng.integers(-1, 2))

    # Chipped plaster, and the coarser layer underneath.
    for px, py, pw, ph in ((122, 118, 11, 6), (252, 124, 15, 7), (58, 126, 8, 5),
                           (328, 120, 9, 6), (188, 128, 13, 5)):
        for y in range(py, min(FLOOR_Y, py + ph)):
            for x in range(px, min(W, px + pw)):
                edge = (x == px or y == py or x == px + pw - 1)
                if rng.random() > 0.2:
                    img[y, x] = WALL[0] if edge else WALL[1]

    # A fuse box: the room needs one thing that is made, among all the decay.
    # Kept clear of x 64..96 and x 160..180, where the notice board and the
    # form rack hang: a painted fixture behind a sprite is a collision the
    # background cannot see coming.
    bx, by, bw, bh = 246, 74, 22, 26
    img[by:by + bh, bx:bx + bw] = INK
    img[by + 1:by + bh - 1, bx + 1:bx + bw - 1] = DOOR[1]
    img[by + 1:by + bh - 1, bx + 1:bx + 3] = DOOR[3]
    img[by + 1, bx + 1:bx + bw - 1] = DOOR[3]
    img[by + bh - 2, bx + 2:bx + bw - 1] = DOOR[0]
    for i in range(3):                                    # louvres
        img[by + 6 + i * 5:by + 8 + i * 5, bx + 4:bx + bw - 4] = DOOR[0]
        img[by + 6 + i * 5, bx + 4:bx + bw - 4] = DOOR[2]
    img[by + bh - 6:by + bh - 4, bx + bw - 7:bx + bw - 4] = BRASS[3]

    # Conduit running from the box up to the ceiling, with two clips.
    for y in range(6, by):
        img[y, bx + 9:bx + 11] = DOOR[1]
        img[y, bx + 9] = DOOR[3]
    for y in (30, 58):
        img[y:y + 2, bx + 7:bx + 13] = DOOR[0]

    # ------------------------------------------------------------- skirting --
    s0 = FLOOR_Y - SKIRT_H
    band = np.linspace(0.95, 0.2, SKIRT_H)[:, None] * np.ones((1, W))
    band *= 0.55 + np.clip(1 - np.abs(np.arange(W) - cx) / 300, 0, 1)[None, :] * 0.5
    img[s0:FLOOR_Y] = banded(band, SKIRT, width=0.5)
    img[s0] = SKIRT[4]
    img[s0 - 1] = SKIRT[2]
    img[FLOOR_Y - 1] = INK
    for x in range(0, W, 1):                              # scuffs along the top
        if rng.random() < 0.06:
            img[s0 + 1:s0 + 3, x] = SKIRT[1]

    # ---------------------------------------------------------------- floor --
    fh = H - FLOOR_Y
    yy, xx = np.mgrid[0:fh, 0:W]
    depth = yy / fh
    pool = np.clip(1 - np.abs(xx - cx) / (54 + depth * 250), 0, 1)
    lit = 0.26 + pool * (0.60 - depth * 0.22) - depth * 0.06
    img[FLOOR_Y:] = banded(lit, FLOOR)

    # Boards laid across the room, seen head on. They are drawn as horizontal
    # seams that crowd together towards the back, which is the whole of the
    # perspective a flat-on adventure view needs. An earlier version ran every
    # seam through a vanishing point and the floor came out as a starburst:
    # that construction is right for a floor seen from a corner, and this room
    # is seen square.
    seams, y, step = [], 2.0, 2.4
    while y < fh:
        seams.append(int(y))
        step *= 1.34                                  # each board nearer, taller
        y += step
    for i, sy in enumerate(seams):
        gy = FLOOR_Y + sy
        img[gy, :] = FLOOR[0]
        if gy + 1 < H:
            img[gy + 1, :] = FLOOR[3]                 # the lit edge of the next
        # End joints, staggered board to board like a real floor.
        off = (i * 97) % 160
        for jx in range(-off, W, 160):
            top = gy
            bot = FLOOR_Y + (seams[i + 1] if i + 1 < len(seams) else fh)
            for j in range(top, min(H, bot)):
                put(img, j, jx, FLOOR[1])
                put(img, j, jx + 1, FLOOR[2])

    # ----------------------------------------------------------------- neon --
    gx0, gx1 = NEON_X - 5, NEON_X + NEON_W + 5
    for r in range(10, 0, -1):                            # glow, dithered out
        v = 1 - r / 10
        for y in range(max(0, NEON_Y - 4 - r), min(H, NEON_Y + 6 + r)):
            for x in range(max(0, gx0 - r * 2), min(W, gx1 + r * 2)):
                if BAYER[y % 8, x % 8] < v * 0.55:
                    img[y, x] = NEON[0] if v < 0.55 else NEON[1]
    img[NEON_Y - 4:NEON_Y + 6, gx0:gx1] = INK             # the fitting
    img[NEON_Y - 3:NEON_Y + 5, gx0 + 1:gx1 - 1] = DOOR[1]
    img[NEON_Y - 3, gx0 + 1:gx1 - 1] = DOOR[3]
    img[NEON_Y - 1:NEON_Y + 3, NEON_X:NEON_X + NEON_W] = NEON[2]   # the tube
    img[NEON_Y - 1:NEON_Y + 2, NEON_X + 1:NEON_X + NEON_W - 1] = NEON[4]
    img[NEON_Y + 2, NEON_X + 2:NEON_X + NEON_W - 2] = NEON[3]

    # ----------------------------------------------------------------- door --
    x0, x1 = DOOR_X - DOOR_W // 2, DOOR_X + DOOR_W // 2
    img[DOOR_TOP - 4:DOOR_BOT, x0 - 4:x1 + 4] = INK
    img[DOOR_TOP - 3:DOOR_BOT - 1, x0 - 3:x1 + 3] = DOOR[1]
    img[DOOR_TOP - 3:DOOR_BOT - 1, x0 - 3:x0 - 1] = DOOR[3]
    img[DOOR_TOP - 3, x0 - 3:x1 + 3] = DOOR[4]
    img[DOOR_TOP - 3:DOOR_BOT - 1, x1 + 1:x1 + 3] = DOOR[0]
    img[DOOR_TOP:DOOR_BOT - 2, x0:x1] = DOOR[2]
    for py0, py1 in ((DOOR_TOP + 3, DOOR_TOP + 18), (DOOR_TOP + 23, DOOR_BOT - 7)):
        img[py0:py1, x0 + 3:x1 - 3] = DOOR[1]
        img[py0 + 1:py1 - 1, x0 + 4:x1 - 4] = DOOR[2]
        img[py0, x0 + 3:x1 - 3] = DOOR[0]
        img[py0:py1, x0 + 3] = DOOR[0]
        img[py1 - 1, x0 + 4:x1 - 3] = DOOR[4]
    hy = DOOR_TOP + 25
    img[hy:hy + 3, x0 + 2:x0 + 8] = BRASS[1]
    img[hy, x0 + 2:x0 + 7] = BRASS[4]
    img[hy + 1, x0 + 2:x0 + 4] = BRASS[3]
    img[hy + 3, x0 + 3:x0 + 7] = BRASS[0]
    img[DOOR_BOT - 2:DOOR_BOT, x0:x1] = INK               # the gap underneath

    for y in range(DOOR_TOP - 4, DOOR_BOT):               # shadow on the wall
        for x in range(x1 + 4, min(W, x1 + 9)):
            if BAYER[y % 8, x % 8] < 0.5 - (x - x1 - 4) * 0.1:
                img[y, x] = WALL[1]

    Image.fromarray(img).save(ASSET)
    print(f"{ASSET}  {W}x{H}  ({len(np.unique(img.reshape(-1, 3), axis=0))} colori)")


if __name__ == "__main__":
    main()
