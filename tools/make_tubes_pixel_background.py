"""Draws the Tubes corridor as pixel art, at the room's own 640x180.

This replaces the painted pair of layers. One texture pixel is one game unit,
the filter stays Nearest, and the corridor is finally made of the same size of
pixel as the people walking down it.

The palette is not invented here: it is lifted from tools/make_tubes_props.py,
whose steel and brass were themselves sampled from the painted background this
file retires. That direction is deliberate. The four props -- porthole, plate,
posting point, capsule -- are approved art already in the game, so the cheapest
coherent move is to make the new wall belong to them rather than redraw four
sprites to belong to a new wall.

The scene commands, the picture serves. Every coordinate below that matters is
dictated by Tubes.tscn, whose hotspots are verified against its navigation mesh:

    the door opening   x 35..65, threshold on the floor line
    the pneumatic tube  centred on y=52, thick enough to fill y 26..78
    porthole            x 236..264, y 49..77   -- left plain, a sprite covers it
    plate               x 234..266, y 77..89   -- left plain
    posting point       x 455..479, y 49..81   -- left plain

Drawing anything into those three windows would be a collision the background
cannot see coming, the same rule the lobby's fuse box had to obey.

Two techniques carry the look, both taken from the lobby and both about
restraint: ramps whose hue turns as they darken, and dithering only in the strip
where two bands meet. A gradient dithered across its whole width, at this
resolution, is a screen door.

The corridor is lit by three ceiling lamps rather than one tube. That is what
makes two screens read as long instead of as one screen repeated: the camera
scrolls past a rhythm of light and shadow, and the rhythm is the distance.

Run from the project root:  python tools/make_tubes_pixel_background.py
"""
import colorsys

import numpy as np
from PIL import Image

ASSET = "assets/backgrounds/bg_tubes.png"
# Two screens wide, one screen tall. The room is 640x180 and the camera scrolls
# across it; a background wider than the room would never be reached.
W, H = 640, 180
FLOOR_Y = 112
SKIRT_H = 6

# The tube. Its middle is the y the pipe hotspot is centred on, and its radius
# is set so the drawn cylinder fills that hotspot's 53-unit band.
TUBE_Y, TUBE_R = 52, 24

# The doorway, which is the other side of the lobby's door. The threshold is
# FLOOR_Y for the reason recorded in the lobby's generator: a door in a wall
# seen face on meets the floor exactly where the wall does, and drawn any lower
# it stops being an opening and becomes furniture.
DOOR_X, DOOR_W, DOOR_TOP, DOOR_BOT = 50, 30, FLOOR_Y - 46, FLOOR_Y

# Where the ceiling lamps hang. Three across two screens, so no single screen
# ever holds two: each is a landmark, and walking from one to the next is how
# the corridor's length gets felt.
LAMPS = (96, 320, 544)

# The three rectangles a sprite will cover, left plain so nothing painted shows
# through from behind. x0, y0, x1, y1.
KEEP_CLEAR = ((234, 47, 266, 91), (453, 47, 481, 83))

rng = np.random.default_rng(4711)

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


# Steel and brass exactly as tools/make_tubes_props.py has them, opened out into
# five-tone ramps. Anything added here has to come out of these.
STEEL = ramp((0x2D, 0x32, 0x2E), (0x9B, 0xA7, 0xA3))
BRASS = ramp((0x33, 0x35, 0x2B), (0xD8, 0xC8, 0x8F))
FLOOR = ramp((0x2A, 0x30, 0x2C), (0xA2, 0xA8, 0x9C))
LAMP = ramp((0x6E, 0x7A, 0x60), (0xF2, 0xF0, 0xC8))
RUST = ramp((0x3A, 0x2A, 0x22), (0x8C, 0x6A, 0x4A))
INK = (0x14, 0x19, 0x15)


def banded(field, pal, width=0.34):
    """Quantises a 0..1 field onto a ramp, dithering only where bands meet.

    The same function the lobby uses, and the same warning applies: do not add
    random noise to a field before banding it. Noise near a band boundary
    scatters single pixels across its whole width and reads as dirt. If a
    surface needs tooth, give it tooth deliberately, in shapes.
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
    if 0 <= y < H and 0 <= x < W:
        img[y, x] = colour


def is_clear(y, x):
    """True where a sprite will be drawn over, so nothing goes underneath."""
    for x0, y0, x1, y1 in KEEP_CLEAR:
        if x0 <= x < x1 and y0 <= y < y1:
            return False
    return True


def lamp_light(xx, spread):
    """How lit a column is, taking the nearest of the three lamps."""
    best = np.zeros_like(xx, dtype=float)
    for lx in LAMPS:
        best = np.maximum(best, np.clip(1 - np.abs(xx - lx) / spread, 0, 1))
    return best


def main():
    img = np.zeros((H, W, 3), dtype=np.uint8)

    # ---------------------------------------------------------------- wall ---
    yy, xx = np.mgrid[0:FLOOR_Y, 0:W]
    dy = np.clip(yy / FLOOR_Y, 0, 1)
    # Bright under each lamp and falling off between them, plus grime low down.
    # The three pools are what a corridor has instead of the lobby's single cone.
    lit = 0.34 + lamp_light(xx, 150) * 0.52 - dy * 0.18
    img[:FLOOR_Y] = banded(lit, STEEL, width=0.18)

    # Panel joints: the wall is made of sheets, and the seams are what say so.
    # Spaced 64 apart, which is not a multiple of the lamp spacing, so the two
    # rhythms never line up into a pattern.
    for x in range(0, W, 64):
        for y in range(0, FLOOR_Y):
            put(img, y, x, STEEL[0])
            put(img, y, x + 1, STEEL[2])

    # A rail of small rivets along the top of the wall, and one lower down.
    for y in (10, 78):
        for x in range(6, W, 16):
            put(img, y, x, STEEL[3])
            put(img, y + 1, x, STEEL[1])

    # ---------------------------------------------------------------- lamps --
    for lx in LAMPS:
        img[0:5, lx - 22:lx + 22] = STEEL[1]              # the fitting
        img[0:2, lx - 22:lx + 22] = STEEL[0]
        img[5:8, lx - 18:lx + 18] = LAMP[4]               # the tube itself
        img[8:9, lx - 16:lx + 16] = LAMP[2]
        # Un'aureola corta e non una nebbia: due passi di dithering appena sotto
        # il tubo, dove il vetro getta luce, e nient'altro. Il resto della luce
        # la porta il gradiente del muro, che e' bandeggiato e non punteggiato.
        for y in range(9, 15):
            v = 1 - (y - 9) / 6
            for x in range(max(0, lx - 20), min(W, lx + 20)):
                near = 1 - abs(x - lx) / 20
                if BAYER[y % 8, x % 8] < v * near * 0.9 and is_clear(y, x):
                    img[y, x] = LAMP[2]

    # ----------------------------------------------------------------- tube --
    # A cylinder seen from the side: the shading runs top to bottom only, which
    # is the whole of what makes a pipe look round. The specular strip sits
    # above the middle because the light is above it.
    for y in range(TUBE_Y - TUBE_R, TUBE_Y + TUBE_R + 1):
        across = (y - (TUBE_Y - TUBE_R)) / (2 * TUBE_R)
        # Brightest a third of the way down, falling off hard towards the belly.
        v = 1.0 - abs(across - 0.34) * (1.7 if across > 0.34 else 2.4)
        band = int(np.clip(v * 4.4, 0, 4))
        for x in range(W):
            if is_clear(y, x):
                img[y, x] = BRASS[band]

    for y in (TUBE_Y - TUBE_R, TUBE_Y + TUBE_R):           # the silhouette
        for x in range(W):
            if is_clear(y, x):
                img[y, x] = INK
    for x in range(W):                                     # the specular strip
        if is_clear(TUBE_Y - 8, x):
            img[TUBE_Y - 8, x] = BRASS[4]

    # Flange rings, and the brackets that carry the tube back to the wall. Not
    # drawn where a sprite will land: a flange behind the porthole would read as
    # a crack across the glass.
    for fx in range(32, W, 96):
        if not all(is_clear(TUBE_Y, x) for x in range(fx - 4, fx + 5)):
            continue
        img[TUBE_Y - TUBE_R - 3:TUBE_Y + TUBE_R + 4, fx - 3:fx + 4] = BRASS[1]
        img[TUBE_Y - TUBE_R - 3:TUBE_Y + TUBE_R + 4, fx - 3:fx - 1] = BRASS[3]
        img[TUBE_Y - TUBE_R - 3, fx - 3:fx + 4] = INK
        img[TUBE_Y + TUBE_R + 3, fx - 3:fx + 4] = INK
        # The bracket: up to the wall above, and a foot below.
        img[8:TUBE_Y - TUBE_R - 2, fx - 1:fx + 2] = STEEL[1]
        img[8:TUBE_Y - TUBE_R - 2, fx - 1:fx] = STEEL[3]
        img[TUBE_Y + TUBE_R + 4:FLOOR_Y - SKIRT_H, fx - 1:fx + 2] = STEEL[1]
        img[TUBE_Y + TUBE_R + 4:FLOOR_Y - SKIRT_H, fx - 1:fx] = STEEL[3]

    # Rust weeping from under a couple of flanges: the line is old, and it is
    # the reason the story can claim it is blocked.
    for rx, ry, ln in ((128, TUBE_Y + TUBE_R, 22), (416, TUBE_Y + TUBE_R, 16)):
        for i in range(ln):
            t = i / ln
            wob = int(np.sin(i * 0.4) * 1.3)
            if is_clear(ry + i, rx + wob):
                put(img, ry + i, rx + wob, RUST[1 if t < 0.6 else 2])
            if t < 0.4 and is_clear(ry + i, rx + 1 + wob):
                put(img, ry + i, rx + 1 + wob, RUST[3])

    # ------------------------------------------------------------- doorway ---
    # Only the opening and its frame. The leaf is a sprite, because it has two
    # states and a StateVisual has to be able to swap it.
    x0, x1 = DOOR_X - DOOR_W // 2, DOOR_X + DOOR_W // 2
    img[DOOR_TOP - 3:DOOR_BOT, x0 - 3:x1 + 3] = STEEL[0]
    img[DOOR_TOP - 2:DOOR_BOT, x0 - 2:x1 + 2] = STEEL[2]
    img[DOOR_TOP - 2:DOOR_BOT, x0 - 2:x0] = STEEL[3]
    img[DOOR_TOP - 2, x0 - 2:x1 + 2] = STEEL[4]
    img[DOOR_TOP:DOOR_BOT, x0:x1] = INK                    # the recess behind

    # ------------------------------------------------------------- skirting --
    s0 = FLOOR_Y - SKIRT_H
    band = np.linspace(0.9, 0.15, SKIRT_H)[:, None] * np.ones((1, W))
    band *= 0.5 + lamp_light(np.arange(W), 220)[None, :] * 0.5
    img[s0:FLOOR_Y] = banded(band, STEEL, width=0.5)
    img[s0] = STEEL[4]
    img[FLOOR_Y - 1] = INK
    # The doorway's threshold survives the skirting: a door opens onto a floor.
    img[s0:FLOOR_Y, x0:x1] = INK

    # ---------------------------------------------------------------- floor --
    fh = H - FLOOR_Y
    yy, xx = np.mgrid[0:fh, 0:W]
    depth = yy / fh
    pool = lamp_light(xx, 60 + depth * 130)
    lit = 0.34 + pool * (0.52 - depth * 0.12)
    img[FLOOR_Y:] = banded(lit, FLOOR, width=0.18)

    # Slabs, crowding together towards the back. Horizontal seams and nothing
    # radial: a floor seen square has no side vanishing point, which is the
    # mistake the lobby's first floor made.
    # Il passo cresce poco: a 1,30 la lastra davanti veniva alta venti unita' e
    # la fuga con la sua riga chiara si leggeva come l'alzata di un gradino.
    seams, y, step = [], 3.0, 2.6
    while y < fh:
        seams.append(int(y))
        step *= 1.17
        y += step
    for i, sy in enumerate(seams):
        gy = FLOOR_Y + sy
        # Solo la riga scura del giunto. Quella chiara sotto -- che c'era -- e'
        # cio' che trasformava ogni fuga nel bordo di un gradino.
        img[gy, :] = FLOOR[1]
        off = (i * 61) % 96
        for jx in range(-off, W, 96):
            bot = FLOOR_Y + (seams[i + 1] if i + 1 < len(seams) else fh)
            for j in range(gy, min(H, bot)):
                put(img, j, jx, FLOOR[1])
                put(img, j, jx + 1, FLOOR[2])

    # A painted line along the wall, the kind a place with a safety inspection
    # has. Brass rather than a yellow from nowhere: the palette is closed.
    for x in range(W):
        if (x // 6) % 8 != 7:                              # worn away in patches
            put(img, FLOOR_Y + 2, x, BRASS[3])
            put(img, FLOOR_Y + 3, x, BRASS[2])

    Image.fromarray(img).save(ASSET)
    colours = len(np.unique(img.reshape(-1, 3), axis=0))
    print(f"{ASSET}  {W}x{H}  ({colours} colori)")


if __name__ == "__main__":
    main()
