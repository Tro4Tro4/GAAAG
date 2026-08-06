"""Draws the Street background: the first room of the game, two screens wide.

640x180, which is two screens at the game's 320x180, exactly as the corridor of
tubes is. The floor line is the corridor's too — the walkable band runs from
y 116 to y 172 — so a character crossing between the two rooms does not change
height on the way.

The construction is the Lobby's, because it works and because a chapter should
be made of one kit: ramps of five tones whose hue turns as it darkens, bands
quantised with dithering only where two bands meet, one light source, and every
shadow pointing away from it. What differs is that this is outdoors — so there
is a sky, and the light is a low sun coming from the right rather than a tube
on the ceiling.

Kept clear for sprites that land on top of this, because a background cannot
see what will be drawn over it:
  x 112..142, y  68..116   the door leaf (a hotspot, so it has to be a sprite)
  x 158..186, y  92..116   the bins
  x 371..529, y  56..120   the van
  x 562..638, y  84..120   the barrier

Run from the project root:  python tools/make_street_background.py
"""
import colorsys

import numpy as np
from PIL import Image

ASSET = "assets/backgrounds/bg_street.png"
W, H = 640, 180                   # two screens at the game's 320x180
PAVE_Y = 116                      # where the pavement starts — the Tubes line
SKY_Y = 34                        # where the buildings start
SUN_X = 600.0                     # a low sun off to the right

rng = np.random.default_rng(2031)

BAYER = np.array([
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]) / 64.0


def ramp(shadow, light, n=5):
    """Five tones from dark to light, with the hue turning as it goes.

    Note the hue wrap, which the Lobby's version does not have and did not need:
    interpolating a hue from 0.65 (deep blue) to 0.06 (warm) the short way round
    passes straight through 0.33, which is green. The first dawn sky drawn here
    came out lime. Taking the shorter of the two arcs on the colour wheel is the
    fix, and it is the difference between a violet dawn and a swamp.
    """
    a = list(colorsys.rgb_to_hsv(*[v / 255 for v in shadow]))
    b = list(colorsys.rgb_to_hsv(*[v / 255 for v in light]))
    if abs(b[0] - a[0]) > 0.5:
        b[0] += 1.0 if b[0] < a[0] else -1.0
    out = []
    for i in range(n):
        t = i / (n - 1)
        out.append(tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(
            (a[0] + (b[0] - a[0]) * t) % 1.0, a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)))
    return out


# The Lobby's violets carried outdoors: the render is the same family as the
# Lobby's wall so the two rooms read as the same town, and the sky is the one
# wide cold field the interiors do not have.
SKY = ramp((52, 56, 102), (214, 176, 168))
FAR = ramp((40, 40, 66), (96, 96, 124))       # the buildings across the way
WALL = ramp((52, 44, 68), (178, 166, 190))    # Lino's building
SHED = ramp((40, 42, 50), (142, 146, 152))    # the depot next door, colder
SHUT = ramp((44, 40, 52), (126, 118, 132))    # its roller shutter
STONE = ramp((36, 32, 48), (140, 132, 146))   # pavement slabs
KERB = ramp((30, 26, 40), (112, 104, 118))    # the contact shadow at the wall
GLASS = ramp((30, 34, 54), (150, 168, 190))
RUST = ramp((62, 44, 40), (146, 104, 72))
INK = (22, 18, 30)

# The layout, up here so the props script can import it instead of guessing.
ALLEY_0, ALLEY_1 = 286, 310       # the gap between the two buildings
WALL_TOP = SKY_Y + 10             # cornice of Lino's building
SHED_TOP = SKY_Y + 24             # the depot next door is lower
PLINTH = PAVE_Y - 14
DOOR_X0, DOOR_X1, DOOR_TOP = 112, 142, 68


def banded(field, pal, width=0.34):
    """Quantises a 0..1 field onto a ramp, dithering only where bands meet.

    Never hand a whole surface to this at a high width, and never add random
    noise to a field before banding it: at this resolution both read as a
    screen door. Tooth is given deliberately, in shapes.
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


def rect(img, y0, y1, x0, x1, colour):
    img[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = colour


def window(img, x, y, w, h, sill=True):
    """A window in the facade: reveal, frame, glass, and grime under the sill."""
    rect(img, y - 1, y + h + 1, x - 1, x + w + 1, INK)
    rect(img, y, y + h, x, x + w, GLASS[1])
    rect(img, y, y + h // 2, x, x + w, GLASS[3])          # sky in the top half
    for i in range(1, 3):                                  # glazing bars
        rect(img, y, y + h, x + i * w // 3, x + i * w // 3 + 1, WALL[0])
    rect(img, y + h // 2, y + h // 2 + 1, x, x + w, WALL[0])
    rect(img, y - 2, y, x - 2, x + w + 2, WALL[3])         # lintel
    if sill:
        rect(img, y + h, y + h + 2, x - 2, x + w + 2, WALL[4])
        rect(img, y + h + 2, y + h + 3, x - 2, x + w + 2, WALL[0])
    for i in range(5):                                     # grime off the sill
        sx = x - 2 + int(rng.integers(0, w + 4))
        for j in range(int(rng.integers(2, 8))):
            put(img, y + h + 3 + j, sx, WALL[1])


def main():
    img = np.zeros((H, W, 3), dtype=np.uint8)

    # ----------------------------------------------------------------- sky ---
    yy, xx = np.mgrid[0:SKY_Y, 0:W]
    # Brighter towards the sun and towards the horizon: a flat sky reads as a
    # painted backdrop, and two gradients crossing is all it takes to stop it.
    glow = np.clip(1 - np.abs(xx - SUN_X) / 540.0, 0, 1)
    lit = 0.16 + glow * 0.46 + (yy / SKY_Y) * 0.34
    img[:SKY_Y] = banded(lit, SKY, width=0.5)

    # Flat cloud banks. Shapes, not noise: a cloud drawn with dithering at this
    # size is a smudge, one drawn as a silhouette is a cloud.
    for cx, cy, cw, ch in ((120, 12, 80, 6), (392, 7, 108, 5), (250, 22, 58, 4)):
        for x in range(cx, min(W, cx + cw)):
            t = (x - cx) / cw
            lift = int(round(ch * (0.35 + 0.65 * np.sin(t * 3.14159))))
            for y in range(max(0, cy - lift), cy + 1):
                put(img, y, x, SKY[3] if y > cy - lift + 1 else SKY[2])

    # ------------------------------------------------- buildings across the --
    # A skyline behind, flat and darker: it is far away and it is not the
    # subject, so it gets two tones and no detail. Filled down to the pavement
    # and not to the cornice — the one place it was left short came out as a
    # black band over the lower depot.
    roof = np.full(W, SKY_Y + 8)
    for x0, x1, top in ((0, 76, 22), (76, 176, 13), (176, 276, 27),
                        (276, 392, 16), (392, 492, 25), (492, 640, 10)):
        roof[x0:x1] = top
    for x in range(W):
        rect(img, roof[x], PAVE_Y, x, x + 1, FAR[1])
        put(img, roof[x], x, FAR[2])
    for x in range(5, W, 14):                              # far windows, lit
        for y in range(roof[x] + 3, SKY_Y + 8, 6):
            if rng.random() < 0.4:
                rect(img, y, y + 2, x, x + 2,
                     FAR[3] if rng.random() < 0.5 else GLASS[2])

    # ------------------------------------------------------------- facade ----
    # Two buildings and an alley between them, not one wall across two screens.
    # The first version was a single render with evenly spaced windows and it
    # read as a fence: a street needs at least one seam in it, and the seam is
    # also what tells the player the room is wider than the screen.
    yy, xx = np.mgrid[0:PAVE_Y, 0:W]
    side = np.clip(1 - (SUN_X - xx) / 760.0, 0, 1)
    down = np.clip((yy - SKY_Y) / (PAVE_Y - SKY_Y), 0, 1)
    lit = 0.30 + side * 0.46 - down * 0.24

    left = banded(lit, WALL)
    right = banded(lit * 0.92 + 0.04, SHED)
    img[WALL_TOP:PAVE_Y, :ALLEY_0] = left[WALL_TOP:PAVE_Y, :ALLEY_0]
    img[SHED_TOP:PAVE_Y, ALLEY_1:] = right[SHED_TOP:PAVE_Y, ALLEY_1:]

    # The alley: not a wall at all, a hole with a bit of the back of it.
    rect(img, SHED_TOP - 3, PAVE_Y, ALLEY_0, ALLEY_1, INK)
    rect(img, SHED_TOP + 6, PAVE_Y, ALLEY_0 + 4, ALLEY_1 - 4, (32, 28, 44))
    rect(img, PAVE_Y - 20, PAVE_Y - 18, ALLEY_0 + 4, ALLEY_1 - 4, (44, 38, 56))

    # Cornices, which is what makes a wall a building.
    for top, pal, xa, xb in ((WALL_TOP, WALL, 0, ALLEY_0),
                             (SHED_TOP, SHED, ALLEY_1, W)):
        rect(img, top - 2, top, xa, xb, pal[4])
        rect(img, top, top + 2, xa, xb, pal[3])
        rect(img, top + 2, top + 3, xa, xb, pal[1])

    # A stone plinth at street level. Darker than the render above it, not
    # lighter, and with no vertical joints: the first two versions were pale
    # with a bright top line and regular ticks, and the eye assembled a railing
    # standing in front of the house.
    band = np.linspace(0.55, 0.22, PAVE_Y - PLINTH)[:, None] * np.ones((1, W))
    band *= 0.72 + np.clip(1 - (SUN_X - np.arange(W)) / 760.0, 0, 1)[None, :] * 0.5
    plinth = banded(band, STONE, width=0.5)
    img[PLINTH:PAVE_Y, :ALLEY_0] = plinth[:, :ALLEY_0]
    img[PLINTH:PAVE_Y, ALLEY_1:] = plinth[:, ALLEY_1:]
    rect(img, PLINTH, PLINTH + 1, 0, ALLEY_0, STONE[2])
    rect(img, PLINTH, PLINTH + 1, ALLEY_1, W, STONE[2])

    # Damp rising out of the pavement, lighter than the render: a stain on
    # painted plaster leaches colour rather than making a hole.
    for bx, by, r in ((60, 94, 12), (218, 90, 10), (338, 96, 14), (574, 92, 11)):
        for y in range(max(SKY_Y, by - r), min(PLINTH, by + r)):
            for x in range(max(0, bx - r - 3), min(W, bx + r + 4)):
                wob = 0.18 * np.sin(x * 0.5 + y * 0.28)
                d = ((x - bx) / r) ** 2 + ((y - by) / (r * 0.9)) ** 2 + wob
                if d < 0.6 or (d < 1.0 and BAYER[y % 8, x % 8] < 0.7):
                    img[y, x] = WALL[3] if x < ALLEY_0 else SHED[3]

    # --------------------------------------------------------- the doorway ---
    # Only the reveal and the frame. The leaf is a sprite, because it is a
    # hotspot, and a hotspot whose picture is painted into the background can
    # never change.
    dx0, dx1, dtop = DOOR_X0, DOOR_X1, DOOR_TOP
    rect(img, dtop - 5, PAVE_Y, dx0 - 5, dx1 + 5, WALL[0])
    rect(img, dtop - 3, PAVE_Y, dx0 - 3, dx1 + 3, WALL[3])
    rect(img, dtop - 3, dtop - 2, dx0 - 3, dx1 + 3, WALL[4])
    rect(img, dtop, PAVE_Y, dx0, dx1, INK)                 # the dark of inside
    rect(img, dtop, dtop + 2, dx0, dx1, (14, 12, 20))
    for x in range(dx0 - 3, dx1 + 3):                      # the worn step
        dip = int(round(1.8 * np.sin((x - dx0 + 3) / (dx1 - dx0 + 6) * 3.14159)))
        rect(img, PAVE_Y - 4 + dip, PAVE_Y, x, x + 1, STONE[3])
        put(img, PAVE_Y - 4 + dip, x, STONE[4])

    # The number plate over the door, and the bells on the left jamb.
    rect(img, dtop - 13, dtop - 5, dx0 + 6, dx1 - 6, WALL[4])
    rect(img, dtop - 12, dtop - 6, dx0 + 7, dx1 - 7, WALL[1])
    rect(img, 80, 98, dx0 - 17, dx0 - 7, WALL[0])
    for i in range(4):
        rect(img, 82 + i * 4, 84 + i * 4, dx0 - 15, dx0 - 9, WALL[3])

    # A downpipe on the party wall, with its brackets and its rust.
    px = ALLEY_0 - 8
    for y in range(WALL_TOP + 3, PAVE_Y):
        rect(img, y, y + 1, px, px + 3, WALL[1])
        put(img, y, px, WALL[3])
        put(img, y, px + 2, WALL[0])
    for y in (WALL_TOP + 16, WALL_TOP + 42, PLINTH - 5):
        rect(img, y, y + 2, px - 2, px + 5, WALL[0])
    for i in range(24):
        put(img, PLINTH - 3 + i % 17, px + 4 + int(np.sin(i * 0.4)), RUST[1])

    # Windows on Lino's building. The ground floor stops short of the plinth,
    # which the first version did not, and the two collided.
    for wx in (30, 194, 238):
        window(img, wx, 72, 26, 20)
    for wx in (26, 86, 146, 206, 254):
        window(img, wx, 48, 22, 16)

    # A wall lamp over the door, off: it is morning, and nothing here is on
    # that does not have to be.
    rect(img, dtop - 24, dtop - 21, dx0 + 12, dx0 + 18, WALL[0])
    rect(img, dtop - 21, dtop - 16, dx0 + 10, dx0 + 20, WALL[1])
    rect(img, dtop - 20, dtop - 17, dx0 + 11, dx0 + 19, GLASS[1])

    # ------------------------------------------------------------ the depot --
    # The reason a removal van is parked here: a roller shutter it can back up
    # to. The van covers most of it, which is the point.
    sx0, sx1, stop = 366, 534, 64
    rect(img, stop - 4, PAVE_Y, sx0 - 4, sx1 + 4, SHED[0])
    rect(img, stop - 2, PAVE_Y, sx0 - 2, sx1 + 2, SHED[2])
    rect(img, stop, PAVE_Y, sx0, sx1, SHUT[1])
    for y in range(stop, PAVE_Y, 4):                       # the slats
        rect(img, y, y + 1, sx0, sx1, SHUT[0])
        rect(img, y + 1, y + 2, sx0, sx1, SHUT[3])
    rect(img, stop - 7, stop - 4, sx0 - 7, sx1 + 7, SHED[3])   # the lintel
    rect(img, stop - 4, stop - 3, sx0 - 7, sx1 + 7, SHED[0])

    # Strip windows high up on the depot, clear of the van and the barrier.
    for wx in (326, 552, 582, 612):
        window(img, wx, SHED_TOP + 8, 20, 11, sill=False)

    # ---------------------------------------------------------- pavement -----
    # No kerb. There was one, drawn as a bright line the whole width of the
    # room with joints along it, and it read as a railing between the player
    # and the house. Where a wall meets a pavement there is no kerb — there is
    # a contact shadow, and that is all this is.
    fy = PAVE_Y
    fh = H - fy
    yy, xx = np.mgrid[0:fh, 0:W]
    depth = yy / fh
    side = np.clip(1 - (SUN_X - xx) / 900.0, 0, 1)
    lit = 0.44 + side * 0.40 - depth * 0.14
    img[fy:] = banded(lit, STONE)

    # Slabs. Seams crowding towards the back, exactly as the Lobby's boards:
    # this is a flat-on view, so the perspective is spacing and nothing else.
    seams, y, step = [], 1.5, 2.0
    while y < fh:
        seams.append(int(y))
        step *= 1.44
        y += step
    for i, sy in enumerate(seams):
        gy = fy + sy
        rect(img, gy, gy + 1, 0, W, STONE[0])
        rect(img, gy + 1, gy + 2, 0, W, STONE[3])
        off = (i * 51) % 80
        for jx in range(-off, W, 80):
            bot = fy + (seams[i + 1] if i + 1 < len(seams) else fh)
            for j in range(gy, min(H, bot)):
                put(img, j, jx, STONE[1])

    # The contact shadow at the foot of the wall, in three hard steps. It is
    # the only thing separating building from pavement, and without it a
    # character standing near the wall looks stuck to it.
    for i, tone in enumerate((KERB[0], KERB[1], KERB[2])):
        for x in range(W):
            if ALLEY_0 <= x < ALLEY_1 and i < 2:
                continue                       # the alley is dark to the floor
            put(img, PAVE_Y + i, x, tone)

    # A drain, and a puddle that has been there long enough to have a rim.
    rect(img, H - 18, H - 12, 80, 96, STONE[0])
    for i in range(3):
        rect(img, H - 17 + i * 2, H - 16 + i * 2, 82, 94, INK)
    for y in range(H - 24, H - 5):
        for x in range(330, 400):
            d = ((x - 365) / 33.0) ** 2 + ((y - (H - 14)) / 9.0) ** 2
            if d < 0.82:
                img[y, x] = GLASS[1] if BAYER[y % 8, x % 8] < 0.75 else GLASS[0]
            elif d < 1.0:
                img[y, x] = STONE[0]

    Image.fromarray(img).save(ASSET)
    print(f"{ASSET}  {W}x{H}  "
          f"({len(np.unique(img.reshape(-1, 3), axis=0))} colori)")


if __name__ == "__main__":
    main()
