"""The drawing kit shared by chapter one's rooms.

CLAUDE.md asks for one palette and one kit per chapter, and gives the reason as
production arithmetic: the second background of a chapter has to cost a fraction
of the first, or forty-four rooms never get drawn. The first four rooms each
carried their own copy of the same ramp function, the same Bayer matrix and the
same banding — so this is that copy taken out and put in one place, at the point
where five more rooms were about to make a sixth.

What is here is only the mechanics. The *colours* stay with each room, because a
palette is a decision about a place and not a utility: the Street decides what
violet the chapter is, and the rooms inside that building import it from there.

Everything draws into a numpy array of uint8. Backgrounds are RGB (H, W, 3);
sprites are RGBA (H, W, 4), because a sprite has to have a silhouette and a
background must not have holes in it.

Two hard-won rules live in here as defaults rather than as comments somebody has
to remember:

  * `banded` defaults to a narrow transition strip (0.18). Measured across the
    rooms already drawn: the corridor used a narrow strip and came out at 6%
    isolated pixels, the lobby used the wide default and came out at 17%.
  * `banded` is for fields that change *quickly*. A slow gradient across a bare
    wall spreads its dither strip over however far the gradient takes to cross a
    band boundary, which on a 320-unit wall was thirty units of diagonal smear.
    For those, use `wedge` — light given as a shape with an edge — and leave the
    surface flat. That is the lesson the Apartment cost three attempts.

Not imported by the four rooms drawn before it: they work, they are verified on
the device, and rewriting a working generator to prove a point is how a project
breaks the thing it was tidying.
"""
from __future__ import annotations

import colorsys

import numpy as np
from PIL import Image

# The 8x8 ordered dither. One matrix for the whole chapter, so two rooms next to
# each other never disagree about where the pattern falls.
BAYER = np.array([
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]) / 64.0


def ramp(shadow, light, n=5):
    """Five tones from dark to light, with the hue turning as it goes.

    The hue takes the shorter of the two arcs round the wheel. Without that,
    interpolating a deep blue towards a warm highlight passes through green, and
    the first dawn sky drawn in this project came out lime.
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


def banded(field, pal, width=0.18):
    """Quantises a 0..1 field onto a ramp, dithering only where bands meet."""
    h, w = field.shape
    tile = np.tile(BAYER, (h // 8 + 1, w // 8 + 1))[:h, :w]
    level = np.clip(field, 0, 1) * (len(pal) - 1)
    base = np.floor(level)
    frac = level - base
    t = np.clip((frac - (0.5 - width / 2)) / max(width, 1e-6), 0, 1)
    idx = np.clip(base + (tile < t), 0, len(pal) - 1).astype(int)
    return np.array(pal, dtype=np.uint8)[idx]


class Canvas:
    """A drawing surface that knows its own bounds, so nothing has to check."""

    def __init__(self, w, h, alpha=False):
        self.w, self.h = w, h
        self.alpha = alpha
        self.img = np.zeros((h, w, 4 if alpha else 3), dtype=np.uint8)

    def _c(self, colour):
        return tuple(colour) + ((255,) if self.alpha and len(colour) == 3 else ())

    def put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img[y, x] = self._c(colour)

    def rect(self, x0, y0, x1, y1, colour):
        """Half-open in x1/y1, like every other rectangle in this project."""
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, x1), min(self.h, y1)
        if x0 < x1 and y0 < y1:
            self.img[y0:y1, x0:x1] = self._c(colour)

    def frame(self, x0, y0, x1, y1, colour):
        self.rect(x0, y0, x1, y0 + 1, colour)
        self.rect(x0, y1 - 1, x1, y1, colour)
        self.rect(x0, y0, x0 + 1, y1, colour)
        self.rect(x1 - 1, y0, x1, y1, colour)

    def band(self, x0, y0, x1, y1, field, pal, width=0.18):
        """Bands a field into a rectangle. The field is generated per pixel."""
        h, w = y1 - y0, x1 - x0
        yy, xx = np.mgrid[0:h, 0:w]
        block = banded(field(xx / max(1, w - 1), yy / max(1, h - 1)), pal, width)
        if self.alpha:
            self.img[y0:y1, x0:x1, :3] = block
            self.img[y0:y1, x0:x1, 3] = 255
        else:
            self.img[y0:y1, x0:x1] = block

    def speckle(self, x0, y0, x1, y1, colour, density):
        """Dithered fill at a fixed density: grain given as pattern, not noise.

        Never add random noise to a field before banding it — near a boundary it
        scatters single pixels and reads as dirt. Grain goes on afterwards, in
        shapes or at a fixed threshold like this.
        """
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                if BAYER[y % 8, x % 8] < density:
                    self.put(x, y, colour)

    def wedge(self, x_at, y0, y1, half, colour, edge_colour, feather=4):
        """Light given as a shape: a sheared patch with a soft vertical edge.

        [param x_at] and [param half] are called with the 0..1 depth down the
        patch, so a caller decides how it leans and how it opens. The near and
        far edges stay hard — that is where the opening's own edge is, and
        softening them turns light into a smudge.
        """
        for y in range(max(0, y0), min(self.h, y1)):
            t = (y - y0) / max(1, y1 - y0)
            cx, hw = x_at(t), half(t)
            a, b = int(round(cx - hw)), int(round(cx + hw))
            for x in range(max(0, a), min(self.w, b)):
                near = min(x - a, b - 1 - x)
                if near > feather:
                    self.put(x, y, colour)
                elif BAYER[y % 8, x % 8] < near / float(feather):
                    self.put(x, y, edge_colour)

    def wash(self, cx, cy, rx, ry, colour, strength=0.85):
        """Light on a surface, as dithering only and with no solid core.

        The difference between this and `wedge` is what the light is doing.
        `wedge` is for light that has a *shape* — a window's patch on the floor,
        a doorway's slab — where the edge is the edge of the opening and wants
        to be hard. `wash` is for light that merely falls on a wall, which has
        no edge at all.

        Getting that backwards is what the first pass of these five rooms did,
        and the result was unmistakable: a lamp drawn with `wedge` came out as a
        solid pale triangle standing on the floor, which the eye reads as a tent
        rather than as light. A wash cannot do that, because there is no solid
        region in it to read as a surface.
        """
        for y in range(max(0, int(cy - ry)), min(self.h, int(cy + ry) + 1)):
            for x in range(max(0, int(cx - rx)), min(self.w, int(cx + rx) + 1)):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d < 1.0 and BAYER[y % 8, x % 8] < (1.0 - d) * strength:
                    self.put(x, y, colour)

    def bricks(self, x0, y0, x1, y1, pal, course=6, length=26):
        """Courses of brick, with the tone varying brick by brick.

        Deterministic and not random. Random tones at this size read as static;
        a fixed pattern reads as brick, because real brickwork is also a fixed
        pattern that merely looks irregular.
        """
        self.rect(x0, y0, x1, y1, pal[1])
        for i, y in enumerate(range(y0, y1, course)):
            offset = (i % 2) * (length // 2)
            for k, x in enumerate(range(x0 - offset, x1, length)):
                tone = pal[1 + ((k * 7 + i * 3) % 3 == 0)]
                self.rect(x + 1, y + 1, x + length - 1, y + course, tone)
                self.rect(x, y, x + length, y + 1, pal[0])
                self.rect(x, y, x + 1, y + course, pal[0])

    def outline(self, colour):
        """One dark pixel around everything opaque, grown outwards.

        Outwards, so a figure keeps the size it was designed at: a body 40 tall
        measures 41 rows once outlined, which is what the character sheets do
        and what qa_check expects.
        """
        a = self.img[..., 3] > 0
        grown = np.zeros_like(a)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            grown |= np.roll(np.roll(a, dy, 0), dx, 1)
        edge = grown & ~a
        self.img[edge, :3] = colour
        self.img[edge, 3] = 255

    def report(self, path):
        """Saves, and prints the two numbers worth knowing about a background.

        Isolated pixels is the measurable form of "the dithering went
        everywhere": a healthy background sits under 10%.
        """
        Image.fromarray(self.img).save(path)
        flat = self.img.reshape(-1, self.img.shape[2])
        colours = len(np.unique(flat, axis=0))
        a = self.img[:, 1:-1].astype(int)
        lone = ((np.abs(a - self.img[:, :-2]).sum(2) > 0)
                & (np.abs(a - self.img[:, 2:]).sum(2) > 0)).mean()
        print(f"{path}  {self.w}x{self.h}  "
              f"({colours} colori, {lone * 100:.0f}% pixel isolati)")

    def save(self, path):
        Image.fromarray(self.img).save(path)
        print(f"{path}  {self.w}x{self.h}")


def floorboards(c, y0, y1, pal, spacing=3.0, growth=1.44, joints=2):
    """Seams crowding towards the back, and a few butt joints near the front.

    A flat-on view has no side vanishing point: the perspective is the spacing
    of the seams and nothing else. Each seam is one dark line — given a bright
    line under it as well, and joints on every course, a floor comes out as a
    brick wall lying down.
    """
    seams, y, step = [], 2.0, spacing
    while y < y1 - y0:
        seams.append(int(y))
        step *= growth
        y += step
    for sy in seams:
        c.rect(0, y0 + sy, c.w, y0 + sy + 1, pal[1])
    for i, sy in enumerate(seams[-joints:], start=len(seams) - joints):
        top = y0 + sy
        bot = y0 + (seams[i + 1] if i + 1 < len(seams) else y1 - y0)
        for jx in ((i * 83) % 160, (i * 83) % 160 + 160):
            for j in range(top + 1, min(c.h, bot)):
                c.put(jx, j, pal[1])
    return seams


def skirting(c, floor_y, pal, height=7):
    """The dark band where a wall meets a floor.

    It is the only thing separating the two, and without it anybody standing at
    the back of a room looks stuck to the plaster. One dithered strip and then
    one solid band: drawn as a single fade it comes out as a dotted border,
    because a fade whose whole width is transition is never read as a fade.
    """
    for y in range(floor_y - height - 6, floor_y - height):
        near = (y - (floor_y - height - 6)) / 6.0
        for x in range(c.w):
            if BAYER[y % 8, x % 8] < near:
                c.put(x, y, pal[1])
    c.rect(0, floor_y - height, c.w, floor_y - 2, pal[2])
    c.rect(0, floor_y - height, c.w, floor_y - height + 1, pal[3])
    c.rect(0, floor_y - 2, c.w, floor_y, pal[0])


def doorway(c, x0, x1, top, floor_y, wall, dark, sign=False):
    """An opening in a wall seen face on: frame, reveal, and nothing else.

    The threshold is [param floor_y] exactly. Drawn lower the frame closes under
    the skirting and paints over the near floor, so the opening stops being an
    opening and becomes a cabinet standing in front of the wall. This project
    has got that wrong twice on the two faces of one door, so the caller is
    given no way to pass a different number.

    The leaf is never drawn here: a door is a hotspot, and a hotspot whose
    picture is in the background can never change.
    """
    c.rect(x0 - 4, top - 4, x1 + 4, floor_y, dark)
    c.rect(x0 - 3, top - 3, x1 + 3, floor_y - 1, wall[1])
    c.rect(x0 - 3, top - 3, x1 + 3, top - 2, wall[4])
    c.rect(x0 - 3, top - 3, x0 - 1, floor_y - 1, wall[3])
    c.rect(x1 + 1, top - 3, x1 + 3, floor_y - 1, wall[0])
    c.rect(x0, top, x1, floor_y, dark)
    c.rect(x0, top, x1, top + 1, wall[0])
    if sign:
        c.rect(x0 - 2, top - 14, x1 + 2, top - 5, dark)
        c.rect(x0 - 1, top - 13, x1 + 1, top - 6, wall[2])
        c.rect(x0 - 1, top - 13, x1 + 1, top - 12, wall[3])
        for i in range(2):
            c.rect(x0 + 2, top - 11 + i * 3, x1 - 2, top - 10 + i * 3, wall[0])
    assert not (c.img[floor_y, (x0 + x1) // 2][:3] == dark[:3]).all(), \
        "soglia sotto la linea del pavimento"
