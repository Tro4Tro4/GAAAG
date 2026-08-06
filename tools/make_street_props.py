"""Draws the sprites that stand in front of the Street background.

Everything here is a hotspot's picture, which is why none of it is painted into
the background: a hotspot whose figure is in the background can never change,
and three of these five have to.

The palette is imported from the background script rather than retyped. That is
the project's rule — a sprite's colours are *derived* from the room's, never
invented beside them — made mechanical: there is one list of ramps for this
chapter and both files read it.

Every sprite is drawn with its origin at the bottom, because the node of a thing
goes where the thing touches the ground: Y-sorting looks at the node's Y and not
at the extent of what it draws.

Sizes are for the game's 320x180. A person is 40 tall, so the street door is 48
and the van is 64 — the van is not much taller than a person is, which is right
for a van you can see the roof of.

Run from the project root:  python tools/make_street_props.py
"""
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, "tools")
from make_street_background import (  # noqa: E402
    BAYER, GLASS, INK, RUST, SHED, STONE, WALL, ramp)

rng = np.random.default_rng(4407)

# The van belongs to the removals firm: institutional, cold, and repainted
# often enough that the current colour is the fourth one.
VAN = ramp((38, 46, 58), (150, 168, 176))
PAPER = ramp((92, 88, 78), (222, 214, 196))
WOOD = ramp((44, 34, 34), (150, 112, 84))


def canvas(w, h):
    return np.zeros((h, w, 4), dtype=np.uint8)


def fill(img, y0, y1, x0, x1, colour):
    h, w = img.shape[:2]
    y0, y1 = max(0, y0), min(h, y1)
    x0, x1 = max(0, x0), min(w, x1)
    if y0 >= y1 or x0 >= x1:
        return
    img[y0:y1, x0:x1, :3] = colour
    img[y0:y1, x0:x1, 3] = 255


def dot(img, y, x, colour):
    h, w = img.shape[:2]
    if 0 <= y < h and 0 <= x < w:
        img[y, x, :3] = colour
        img[y, x, 3] = 255


def outline(img, colour=INK):
    """Puts a one pixel dark edge around everything opaque.

    Drawn outwards, so the figure keeps the size it was designed at and the
    outline sits outside it — the same convention the character sheets use, and
    the reason a body 40 tall measures 41 rows of opaque pixels.
    """
    a = img[..., 3] > 0
    grown = np.zeros_like(a)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        grown |= np.roll(np.roll(a, dy, 0), dx, 1)
    edge = grown & ~a
    img[edge, :3] = colour
    img[edge, 3] = 255


def save(img, name):
    Image.fromarray(img).save(f"assets/sprites/{name}.png")
    print(f"assets/sprites/{name}.png  {img.shape[1]}x{img.shape[0]}")


def street_door():
    """The street door of Lino's building. Fills the reveal in the background."""
    w, h = 30, 48
    img = canvas(w, h)
    fill(img, 0, h, 0, w, WOOD[1])
    fill(img, 0, 2, 0, w, WOOD[3])                 # the top catches the light
    fill(img, 0, h, 0, 2, WOOD[2])
    fill(img, 0, h, w - 2, w, WOOD[0])

    # A fanlight, then two sunk panels.
    fill(img, 2, 11, 4, w - 4, GLASS[0])
    fill(img, 3, 10, 5, w - 5, GLASS[1])
    for i in range(1, 3):
        fill(img, 2, 11, 3 + i * (w - 8) // 3, 4 + i * (w - 8) // 3, WOOD[0])
    for py0, py1 in ((15, 28), (32, h - 3)):
        fill(img, py0, py1, 4, w - 4, WOOD[0])
        fill(img, py0 + 1, py1 - 1, 5, w - 5, WOOD[2])
        fill(img, py1 - 2, py1 - 1, 5, w - 5, WOOD[3])

    # Handle and lock, on the opening side.
    fill(img, 27, 29, 21, 26, RUST[3])
    fill(img, 27, 28, 21, 25, RUST[4])
    fill(img, 31, 33, 23, 25, RUST[1])

    # Kicked and scuffed along the bottom. Dark marks only, and few: the first
    # version scattered light ones too and the foot of the door read as a heap
    # of mud piled against it.
    for _ in range(8):
        dot(img, int(rng.integers(h - 9, h - 3)), int(rng.integers(4, w - 4)),
            WOOD[0])
    outline(img)
    save(img, "prop_street_door")


def eviction_notice():
    """The notice taped to the door. Small, and the first thing to click."""
    w, h = 11, 14
    img = canvas(w, h)
    fill(img, 0, h, 0, w, PAPER[3])
    fill(img, 0, 1, 0, w, PAPER[4])
    fill(img, h - 2, h, 0, w, PAPER[1])
    fill(img, 2, 4, 2, w - 2, PAPER[0])            # the heading, heavier
    for i in range(3):
        fill(img, 6 + i * 2, 7 + i * 2, 2, w - 2 - (i % 3), PAPER[1])
    for i in range(2):                             # a corner curled off the tape
        img[h - 1 - i, w - 3 + i:w, 3] = 0
    outline(img)
    save(img, "prop_notice_eviction")


def bins():
    """Two wheelie bins by the door. Scenery, but clickable scenery."""
    w, h = 28, 24
    img = canvas(w, h)
    for bx, bw, bh, pal in ((0, 15, 21, SHED), (14, 14, 24, WALL)):
        top = h - bh
        fill(img, top + 3, h - 2, bx + 1, bx + bw - 1, pal[1])
        fill(img, top + 3, h - 2, bx + 1, bx + 3, pal[2])
        fill(img, top + 3, h - 2, bx + bw - 3, bx + bw - 1, pal[0])
        fill(img, top, top + 3, bx, bx + bw, pal[3])       # the lid
        fill(img, top, top + 1, bx + 1, bx + bw - 1, pal[4])
        fill(img, top + 3, top + 4, bx + 1, bx + bw - 1, pal[0])
        fill(img, h - 2, h - 1, bx + 2, bx + 4, INK)       # the wheels
        fill(img, h - 2, h - 1, bx + bw - 5, bx + bw - 3, INK)
    fill(img, 0, 2, 15, 26, WALL[4])               # one lid not quite shut
    outline(img)
    save(img, "prop_bins")


def van():
    """The removal van, backed up to the depot shutter, rear doors open."""
    w, h = 158, 64
    img = canvas(w, h)
    body_top, floor = 6, h - 7

    # Box body on the right, cab stepped down on the left.
    fill(img, body_top, floor, 38, w - 2, VAN[2])
    fill(img, body_top, body_top + 2, 38, w - 2, VAN[4])
    fill(img, floor - 10, floor, 38, w - 2, VAN[1])        # dirty lower band
    fill(img, floor - 11, floor - 10, 38, w - 2, VAN[0])
    for x in range(42, w - 4, 11):                         # body ribs
        fill(img, body_top + 3, floor - 12, x, x + 1, VAN[1])
        fill(img, body_top + 3, floor - 12, x + 1, x + 2, VAN[3])

    fill(img, body_top + 9, floor, 5, 40, VAN[2])          # the cab
    fill(img, body_top + 9, body_top + 11, 5, 40, VAN[3])
    fill(img, body_top + 12, body_top + 24, 8, 25, GLASS[1])    # windscreen
    fill(img, body_top + 12, body_top + 18, 8, 25, GLASS[3])
    fill(img, body_top + 12, body_top + 24, 27, 36, GLASS[1])   # door window
    fill(img, floor - 10, floor, 5, 40, VAN[1])
    fill(img, body_top + 26, body_top + 28, 28, 34, VAN[0])     # door handle

    # Rear doors swung open towards us: two leaves edge-on plus the dark of the
    # load space, which says "being loaded" without needing an arrow.
    fill(img, body_top + 2, floor - 2, w - 25, w - 4, (26, 24, 34))
    for i in range(3):
        fill(img, body_top + 5 + i * 12, body_top + 9 + i * 12,
             w - 22, w - 7, VAN[0])
    fill(img, body_top, floor + 2, w - 5, w - 2, VAN[3])   # the near leaf
    fill(img, body_top, floor + 2, w - 3, w - 2, VAN[0])

    # Wheels, with a hint of arch above each.
    for cx in (28, 110):
        for y in range(floor - 3, h):
            for x in range(cx - 10, cx + 11):
                d = ((x - cx) / 10.0) ** 2 + ((y - (floor + 1)) / 9.0) ** 2
                if d < 1.0:
                    dot(img, y, x, INK if d > 0.42 else VAN[1])
        fill(img, floor - 5, floor - 3, cx - 11, cx + 11, VAN[0])

    # A blank panel on the flank where a firm's name would be. Left blank on
    # purpose: no generator writes readable words, and words here would be an
    # untranslatable string baked into a picture.
    fill(img, body_top + 10, body_top + 28, 62, 124, VAN[3])
    fill(img, body_top + 11, body_top + 27, 63, 123, VAN[4])
    fill(img, body_top + 15, body_top + 17, 68, 118, VAN[1])
    fill(img, body_top + 20, body_top + 22, 68, 104, VAN[1])

    # Rust along the bottom seam, because this van has done this before.
    for _ in range(55):
        x, y = int(rng.integers(8, w - 6)), int(rng.integers(floor - 5, floor))
        if BAYER[y % 8, x % 8] < 0.6:
            dot(img, y, x, RUST[1])
    outline(img)
    save(img, "prop_van")


def barrier():
    """The barrier closing the street. Striped, and lower than a person."""
    w, h = 76, 36
    img = canvas(w, h)
    # The post, on the right, weighted at the foot.
    fill(img, 5, h - 3, w - 10, w - 4, STONE[1])
    fill(img, 5, h - 3, w - 10, w - 8, STONE[3])
    fill(img, h - 5, h, w - 15, w, STONE[0])

    # The bar, slightly off level, because nothing here is maintained. The
    # stripes are dark red against near-white and not two mid tones: the first
    # version used the rust ramp against paper and the bar read as a plank.
    for x in range(0, w - 10):
        y = 11 + int(round(x * 0.035))
        band = (x // 9) % 2
        fill(img, y, y + 6, x, x + 1, RUST[0] if band else PAPER[4])
        dot(img, y, x, RUST[1] if band else PAPER[4])
        dot(img, y + 5, x, RUST[0] if band else PAPER[2])

    fill(img, 16, h - 2, 3, 7, STONE[1])           # the leg at the far end
    fill(img, h - 3, h, 0, 10, STONE[0])
    outline(img)
    save(img, "prop_barrier")


if __name__ == "__main__":
    street_door()
    eviction_notice()
    bins()
    van()
    barrier()
