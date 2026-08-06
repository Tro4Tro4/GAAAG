"""Draws the Tubes corridor's prop sprites.

Four things the painted background deliberately does not contain, each left out
for one of the three reasons recorded in CLAUDE.md:

* the porthole and the capsule change with the state of the puzzle;
* the plate is picked up, so it has to be able to stop existing;
* the plate and the posting point carry writing, and no image generator draws
  words that can be read.

The palette is derived from the two background planes rather than invented:
brass and olive off the pipes for whatever is bolted to them, cold grey-green
off the wall for whatever hangs on it. The corridor's light comes from above,
so the lit edge of everything here is its top.

Run from the project root:  python tools/make_tubes_props.py
"""
import sys

sys.path.insert(0, ".claude/skills/pixel-adventure-assets/scripts")
from pixel_helpers import PixelCanvas

OUT = "assets/sprites"
CLEAR = (0, 0, 0, 0)


def c(h, a=255):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


# Sampled from bg_tubes_pipes.webp — the bundle these are bolted to.
INK      = c("141915")
BRASS_D  = c("33352B")
BRASS_S  = c("4B4B3D")
BRASS    = c("7C7E62")
BRASS_L  = c("AEAB83")
BRASS_H  = c("D8C88F")
# Sampled from bg_tubes_wall.webp — the wall the rest hangs on.
STEEL_D  = c("2D322E")
STEEL_S  = c("3E433F")
STEEL    = c("5F645E")
STEEL_L  = c("96988E")
STEEL_H  = c("9BA7A3")
GLASS_D  = c("515A59")
GLASS    = c("6D7773")
GLASS_L  = c("72807F")
RUST     = c("8C6A4A")

# A 3x5 stencil, only the glyphs the corridor's signs actually spell. Drawn
# rather than rendered: a font at this size would be anti-aliased into mush,
# and these five characters are the whole vocabulary.
GLYPHS = {
    "S": ("111", "100", "111", "001", "111"),
    "E": ("111", "100", "110", "100", "111"),
    "Z": ("111", "001", "010", "100", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "P": ("111", "101", "111", "100", "100"),
    "U": ("101", "101", "101", "101", "111"),
    "B": ("110", "101", "110", "101", "110"),
    "L": ("100", "100", "100", "100", "111"),
    "I": ("111", "010", "010", "010", "111"),
    "C": ("111", "100", "100", "100", "111"),
    "O": ("111", "101", "101", "101", "111"),
    ".": ("000", "000", "000", "000", "100"),
    " ": ("000", "000", "000", "000", "000"),
}


def text(canvas, x, y, s, colour):
    """Stamps a word one glyph at a time, a pixel of tracking between them."""
    for ch in s:
        g = GLYPHS.get(ch)
        if g is None:
            x += 4
            continue
        for dy, row in enumerate(g):
            for dx, on in enumerate(row):
                if on == "1":
                    canvas.set(x + dx, y + dy, colour)
        x += 4
    return x


def disc(canvas, cx, cy, r, colour):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                canvas.set(x, y, colour)


def ring(canvas, cx, cy, r0, r1, colour):
    for y in range(cy - r1, cy + r1 + 1):
        for x in range(cx - r1, cx + r1 + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if r0 * r0 < d <= r1 * r1:
                canvas.set(x, y, colour)


# ------------------------------------------------------------- porthole ------
def porthole() -> PixelCanvas:
    """The inspection window, 28x28, with the jammed capsule behind the glass.

    The blockage is the puzzle, so it has to be visible through the glass from
    the moment the player first looks: a dark mass filling the bore, not an
    empty pipe. The glass reads as glass by two things only at this size — a
    hard diagonal highlight across the top left, and the fact that what is
    behind it is dimmer than what is in front.
    """
    k = PixelCanvas(28, 28)
    cx = cy = 14

    disc(k, cx, cy, 13, INK)                       # outer edge
    ring(k, cx, cy, 9, 12, BRASS)                  # the collar
    ring(k, cx, cy, 11, 12, BRASS_S)               # its shaded outer lip
    ring(k, cx, cy, 9, 10, BRASS_L)                # its lit inner lip
    for x in range(cx - 9, cx + 10):               # light from above
        if (x - cx) ** 2 + 81 <= 144:
            k.set(x, cy - 11, BRASS_H)

    disc(k, cx, cy, 8, GLASS_D)                    # the bore behind the glass
    disc(k, cx, cy, 7, GLASS)

    # The stuck capsule, lying across the bore at an angle: a body with two
    # sealing bands and one rounded end showing. The first version was an
    # ellipse and read as a smudge — what makes it a capsule is the bands,
    # because they are the only straight lines inside a circular window.
    for y in range(cy, cy + 5):
        for x in range(cx - 6, cx + 6):
            if -6 < x - cx < 6 and (x - cx) ** 2 <= 40:
                k.set(x, y, STEEL_S)
    for x in range(cx - 5, cx + 5):
        k.set(x, cy, STEEL)                        # its lit upper curve
        k.set(x, cy + 4, STEEL_D)                  # its shaded underside
    for x in (cx - 3, cx + 1):                     # the two bands
        k.set(x, cy + 1, STEEL_D)
        k.set(x, cy + 2, STEEL_D)
        k.set(x, cy + 3, STEEL_D)
    k.set(cx - 5, cy + 2, STEEL_D)                 # the rounded end cap
    k.set(cx + 4, cy + 2, STEEL_L)
    k.set(cx - 1, cy + 3, RUST)                    # three years in the pipe
    k.set(cx + 3, cy + 1, RUST)

    for i in range(4):                             # the diagonal glass glint
        k.set(cx - 6 + i, cy - 6 + i, GLASS_L)
        k.set(cx - 5 + i, cy - 6 + i, STEEL_H)

    for i, (bx, by) in enumerate(                  # eight bolts around the ring
            ((0, -11), (8, -8), (11, 0), (8, 8),
             (0, 11), (-8, 8), (-11, 0), (-8, -8))):
        k.set(cx + bx, cy + by, BRASS_H if by < 0 else BRASS_D)
        k.set(cx + bx, cy + by + 1, BRASS_S)
    return k


# ---------------------------------------------------------------- plate ------
def plate() -> PixelCanvas:
    """SEZIONE 4, 32x12: enamelled, one screw left and already half out.

    The word is spelled with the stencil because the player has to read it —
    it is what the complaint form asks to be attached in the original.
    """
    k = PixelCanvas(32, 12)
    k.rect(0, 0, 31, 11, INK)
    k.rect(1, 1, 30, 10, GLASS_L)
    k.rect(1, 1, 30, 1, STEEL_H)                   # lit top edge
    k.rect(1, 10, 30, 10, GLASS_D)                 # shaded bottom edge
    k.rect(1, 1, 1, 10, STEEL_H)

    text(k, 3, 3, "SEZ", STEEL_D)
    text(k, 16, 3, "4", STEEL_D)

    # Two fixings, and they tell the story: the left hole is empty, the right
    # screw is still in and standing proud of the surface. The plate is
    # already half off, which is why taking it is not vandalism.
    k.set(22, 5, STEEL_D)                          # the empty hole
    k.set(23, 5, STEEL_D)
    k.set(22, 6, GLASS_D)
    k.set(23, 6, STEEL_D)
    disc(k, 27, 5, 2, BRASS_S)                     # the screw that is left
    k.set(27, 4, BRASS_H)
    k.set(26, 5, BRASS_L)
    k.set(28, 6, BRASS_D)
    k.set(27, 7, BRASS_D)
    k.set(27, 5, BRASS_D)                          # its slot
    return k


# -------------------------------------------------------- posting point ------
def posting_point() -> PixelCanvas:
    """The public posting hatch, 24x32: a slot, a flap, and a sign over it.

    Only the public line is unobstructed, so this is the one thing in the room
    that still works — it is drawn cleaner and brighter than everything around
    it, which is the visual half of that idea.
    """
    k = PixelCanvas(24, 32)
    k.rect(0, 0, 23, 31, INK)
    k.rect(1, 1, 22, 30, STEEL)
    k.rect(1, 1, 22, 2, STEEL_L)                   # lit top
    k.rect(1, 1, 2, 30, STEEL_L)                   # lit left
    k.rect(21, 3, 22, 30, STEEL_S)                 # shaded right
    k.rect(3, 29, 22, 30, STEEL_S)

    k.rect(3, 3, 20, 10, STEEL_D)                  # the sign plate
    k.rect(4, 4, 19, 9, GLASS_L)
    text(k, 6, 5, "PUB", STEEL_D)                  # 3 glyphs x 4 px, inside 16

    k.rect(3, 13, 20, 24, STEEL_S)                 # the recessed hatch
    k.rect(4, 14, 19, 23, STEEL_D)
    # The slot reads as a slot because it is a black gap with a lit lip above
    # and a flap hanging into it below — not because of texture. The first
    # version filled it with ribs and came out looking like a grille.
    k.rect(5, 16, 18, 20, INK)
    k.rect(5, 15, 18, 15, STEEL_L)                 # the lit lip over it
    k.rect(5, 19, 18, 20, STEEL_D)                 # the flap, hanging inside
    k.rect(6, 19, 17, 19, STEEL_S)
    k.set(5, 16, STEEL_D)
    k.set(18, 16, STEEL_D)

    disc(k, 12, 26, 2, BRASS)                      # the handle below
    k.set(12, 25, BRASS_H)
    k.set(11, 26, BRASS_L)
    k.set(12, 27, BRASS_D)
    k.rect(9, 26, 15, 26, BRASS_S)
    return k


# -------------------------------------------------------------- capsule ------
def capsule() -> PixelCanvas:
    """The pneumatic capsule, 20x12, arrived and lying on the floor.

    It carries the renewal that has been stuck in the line for three years, so
    it is scuffed and dusty rather than shiny: the shine would say "new", and
    the whole joke is that it is old.
    """
    k = PixelCanvas(20, 12)
    # A lozenge, not a box. The first version was a rectangle with the corner
    # pixels cleared and read as a small suitcase: what says "this travelled
    # down a tube" is that both ends are round, so the ends are built as half
    # discs and the body as the rectangle between them.
    disc(k, 4, 5, 4, INK)
    disc(k, 15, 5, 4, INK)
    k.rect(4, 1, 15, 9, INK)
    disc(k, 4, 5, 3, BRASS_S)
    disc(k, 15, 5, 3, BRASS_S)
    k.rect(4, 2, 15, 8, BRASS_S)

    k.rect(4, 2, 15, 3, BRASS)                     # lit upper curve
    k.rect(5, 2, 14, 2, BRASS_L)
    k.rect(4, 8, 15, 8, BRASS_D)                   # shaded underside
    k.set(2, 5, BRASS_D)
    k.set(17, 5, BRASS_L)

    for x in (7, 12):                              # the two sealing bands
        k.rect(x, 2, x, 8, STEEL_D)
        k.set(x, 2, STEEL)
    k.rect(9, 4, 10, 6, BRASS_D)                   # the catch on the lid
    k.set(9, 4, BRASS_L)
    k.set(3, 7, RUST)                              # three years of it
    k.set(14, 3, RUST)
    k.set(11, 7, RUST)
    return k


PROPS = [("prop_porthole", porthole), ("prop_plate", plate),
         ("prop_posting_point", posting_point), ("prop_capsule", capsule)]


if __name__ == "__main__":
    for name, fn in PROPS:
        k = fn()
        k.save(f"{OUT}/{name}.png")
        print(f"{OUT}/{name}.png  {k.image.size[0]}x{k.image.size[1]}")
