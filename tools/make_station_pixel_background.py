"""Draws the Station background as pixel art, at the room's own 320x180.

The last room to stop being a blockout. Until now the station was four flat
Polygon2D rectangles -- wall, floor, skirting, shelf -- and its four objects were
flat polygons too; this gives it a wall and a floor, and make_station_props.py
gives it the objects.

The palette is the corridor's, and that is a statement about the fiction as much
as about colour: the station operates the pneumatic line, so it is the same
facility, the same steel, the same olive brass. What it has that the corridor
does not is warm light, because this is the one room in the prototype where
somebody sits and works: the console glows amber, and that amber is the only
warm note, so the eye goes to the thing the puzzle is about.

The scene commands, the picture serves. These are dictated by Station.tscn, whose
hotspots are verified against its navigation mesh, and drawing into them would be
a collision the background cannot see coming:

    service point   x 38..62,  y 52..84
    console         x 77..157, y 20..100
    lever           x 173..193, y 30..74
    log book        x 234..270, y 79..93

The shelf the log sits on is *not* in that list. It never changes and nobody
touches it, so it belongs in the picture -- the same rule that keeps the lobby's
skirting and door frame painted rather than instanced.

Run from the project root:  python tools/make_station_pixel_background.py
"""
import colorsys

import numpy as np
from PIL import Image

ASSET = "assets/backgrounds/bg_station.png"
W, H = 320, 180
# Higher than the lobby's 108: this is a machine room and the console is 80 tall,
# so the wall has to have somewhere to put it.
FLOOR_Y = 100
SKIRT_H = 6

# Where the pneumatic line comes through the wall to reach the service point.
# Its middle lines up with the service point's, so the tube and the hatch read as
# one installation rather than two things that happen to be near each other.
TUBE_Y, TUBE_R = 68, 13

SHELF_X0, SHELF_X1, SHELF_Y = 223, 280, 92

KEEP_CLEAR = ((38, 52, 62, 84), (77, 20, 157, 100),
              (173, 30, 193, 74), (234, 79, 270, 93))

rng = np.random.default_rng(2718)

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


STEEL = ramp((0x2D, 0x32, 0x2E), (0x9B, 0xA7, 0xA3))
BRASS = ramp((0x33, 0x35, 0x2B), (0xD8, 0xC8, 0x8F))
FLOOR = ramp((0x2A, 0x30, 0x2C), (0xA2, 0xA8, 0x9C))
AMBER = ramp((0x5A, 0x3C, 0x1E), (0xF0, 0xC0, 0x6A))
RUST = ramp((0x3A, 0x2A, 0x22), (0x8C, 0x6A, 0x4A))
INK = (0x14, 0x19, 0x15)


def banded(field, pal, width=0.18):
    """Quantises a 0..1 field onto a ramp, dithering only where bands meet.

    The default width is the narrow one the corridor settled on, not the wide
    one the lobby started with: a slow gradient with a wide mixing strip spreads
    single pixels over tens of units and reads as dirt.
    """
    h, w = field.shape
    tile = np.tile(BAYER, (h // 8 + 1, w // 8 + 1))[:h, :w]
    level = np.clip(field, 0, 1) * (len(pal) - 1)
    base = np.floor(level)
    frac = level - base
    t = np.clip((frac - (0.5 - width / 2)) / max(width, 1e-6), 0, 1)
    idx = np.clip(base + (tile < t), 0, len(pal) - 1).astype(int)
    return np.array(pal, dtype=np.uint8)[idx]


def put(img, y, x, colour):
    if 0 <= y < H and 0 <= x < W and is_clear(y, x):
        img[y, x] = colour


def is_clear(y, x):
    for x0, y0, x1, y1 in KEEP_CLEAR:
        if x0 <= x < x1 and y0 <= y < y1:
            return False
    return True


def main():
    img = np.zeros((H, W, 3), dtype=np.uint8)

    # ---------------------------------------------------------------- wall ---
    yy, xx = np.mgrid[0:FLOOR_Y, 0:W]
    dy = np.clip(yy / FLOOR_Y, 0, 1)
    # Lit from above and from the console: the amber pool on the wall is why the
    # room reads as occupied rather than abandoned, which is the corridor's job.
    lit = 0.32 + np.clip(1 - dy * 1.5, 0, 1) * 0.34
    lit += np.clip(1 - np.abs(xx - 117) / 130, 0, 1) * (0.30 - dy * 0.10)
    lit -= np.clip(1 - np.minimum(xx, W - xx) / 40, 0, 1) * 0.12
    img[:FLOOR_Y] = banded(lit, STEEL)

    for x in range(0, W, 48):                              # sheet joints
        for y in range(0, FLOOR_Y):
            put(img, y, x, STEEL[0])
            put(img, y, x + 1, STEEL[2])

    # A cable tray along the top, with the cables it carries. Every control room
    # has one, and it is the cheapest thing that says "this wall does work".
    img[6:10, :] = STEEL[1]
    img[6, :] = STEEL[3]
    img[10, :] = INK
    for i, cy in enumerate((7, 8, 9)):
        for x in range(W):
            if (x + i * 5) % 3 == 0:
                put(img, cy, x, STEEL[0] if i else STEEL[2])
    for x in range(12, W, 40):                             # tray hangers
        for y in range(0, 6):
            put(img, y, x, STEEL[1])
            put(img, y, x + 1, STEEL[0])

    # ------------------------------------------------------------ the line ---
    # The tube coming in through the left wall to feed the service hatch: a
    # cylinder shaded top to bottom, ending where the hatch begins.
    for y in range(TUBE_Y - TUBE_R, TUBE_Y + TUBE_R + 1):
        across = (y - (TUBE_Y - TUBE_R)) / (2 * TUBE_R)
        v = 1.0 - abs(across - 0.34) * (1.7 if across > 0.34 else 2.4)
        band = int(np.clip(v * 4.4, 0, 4))
        for x in range(0, 44):
            put(img, y, x, BRASS[band])
    for y in (TUBE_Y - TUBE_R, TUBE_Y + TUBE_R):
        for x in range(0, 44):
            put(img, y, x, INK)
    for x in range(0, 44):
        put(img, TUBE_Y - 5, x, BRASS[4])
    for fx in (14, 30):                                    # two flanges
        for y in range(TUBE_Y - TUBE_R - 2, TUBE_Y + TUBE_R + 3):
            for x in range(fx - 2, fx + 3):
                put(img, y, x, BRASS[1] if x > fx - 1 else BRASS[3])
        for x in range(fx - 2, fx + 3):
            put(img, TUBE_Y - TUBE_R - 2, x, INK)
            put(img, TUBE_Y + TUBE_R + 2, x, INK)

    # A schematic of the line, screwed to the wall on the right: the one thing in
    # the room that explains what the room is for. Lines and pins, no lettering —
    # nothing legible can be promised at this size, and what has to be read is
    # written in the hotspot texts.
    bx, by, bw, bh = 236, 24, 64, 40
    img[by:by + bh, bx:bx + bw] = INK
    img[by + 1:by + bh - 1, bx + 1:bx + bw - 1] = STEEL[1]
    img[by + 1, bx + 1:bx + bw - 1] = STEEL[3]
    for i, ly in enumerate((10, 20, 30)):
        img[by + ly, bx + 5:bx + bw - 5] = STEEL[3]
        for px in range(bx + 8 + i * 3, bx + bw - 6, 14):
            img[by + ly - 1:by + ly + 2, px:px + 2] = BRASS[3] if i == 1 else STEEL[4]
    img[by + 4:by + 7, bx + 5:bx + 26] = STEEL[0]          # a title plate
    img[by + 5, bx + 6:bx + 25] = STEEL[2]

    # Two pressure gauges above the lever, because the lever needs a reason to be
    # believed: something has to be reading the pressure it changes.
    for gx in (170, 196):
        for y in range(14, 26):
            for x in range(gx - 6, gx + 7):
                if (x - gx) ** 2 + ((y - 20) * 1.1) ** 2 <= 36:
                    put(img, y, x, STEEL[3])
                elif (x - gx) ** 2 + ((y - 20) * 1.1) ** 2 <= 49:
                    put(img, y, x, INK)
        put(img, 20, gx, INK)
        put(img, 18, gx + 2, AMBER[3])
        put(img, 19, gx + 1, AMBER[2])

    # ---------------------------------------------------------------- shelf --
    img[SHELF_Y:SHELF_Y + 2, SHELF_X0:SHELF_X1] = STEEL[4]
    img[SHELF_Y + 2:SHELF_Y + 6, SHELF_X0:SHELF_X1] = STEEL[1]
    img[SHELF_Y + 6, SHELF_X0:SHELF_X1] = INK
    for sx in (SHELF_X0 + 4, SHELF_X1 - 6):                 # brackets
        img[SHELF_Y + 6:SHELF_Y + 12, sx:sx + 2] = STEEL[1]
        img[SHELF_Y + 6:SHELF_Y + 12, sx:sx + 1] = STEEL[3]

    # ------------------------------------------------------------- skirting --
    s0 = FLOOR_Y - SKIRT_H
    band = np.linspace(0.9, 0.15, SKIRT_H)[:, None] * np.ones((1, W))
    band *= 0.6 + np.clip(1 - np.abs(np.arange(W) - 117) / 200, 0, 1)[None, :] * 0.4
    img[s0:FLOOR_Y] = banded(band, STEEL, width=0.4)
    img[s0] = STEEL[4]
    img[FLOOR_Y - 1] = INK

    # ---------------------------------------------------------------- floor --
    fh = H - FLOOR_Y
    yy, xx = np.mgrid[0:fh, 0:W]
    depth = yy / fh
    pool = np.clip(1 - np.abs(xx - 117) / (50 + depth * 190), 0, 1)
    lit = 0.34 + pool * (0.50 - depth * 0.12)
    img[FLOOR_Y:] = banded(lit, FLOOR)

    seams, y, step = [], 3.0, 2.6
    while y < fh:
        seams.append(int(y))
        step *= 1.17
        y += step
    for i, sy in enumerate(seams):
        gy = FLOOR_Y + sy
        img[gy, :] = FLOOR[1]
        off = (i * 61) % 88
        for jx in range(-off, W, 88):
            bot = FLOOR_Y + (seams[i + 1] if i + 1 < len(seams) else fh)
            for j in range(gy, min(H, bot)):
                put(img, j, jx, FLOOR[1])
                put(img, j, jx + 1, FLOOR[2])

    # The amber the console throws on the floor in front of it. Warm on a cool
    # floor is what tells the eye where the working end of the room is.
    for y in range(FLOOR_Y, FLOOR_Y + 18):
        t = 1 - (y - FLOOR_Y) / 18
        half = int(14 + (y - FLOOR_Y) * 1.4)
        for x in range(117 - half, 117 + half):
            if BAYER[y % 8, x % 8] < t * 0.30 * (1 - abs(x - 117) / half):
                put(img, y, x, AMBER[1])

    # Worn brass along the front of the console, where a chair has been pushed
    # back and forth for years.
    for x in range(84, 152):
        if (x // 5) % 6 != 5:
            put(img, FLOOR_Y + 2, x, BRASS[2])

    Image.fromarray(img).save(ASSET)
    colours = len(np.unique(img.reshape(-1, 3), axis=0))
    print(f"{ASSET}  {W}x{H}  ({colours} colori)")


if __name__ == "__main__":
    main()
