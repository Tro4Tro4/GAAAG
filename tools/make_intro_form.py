"""Draws the paper and the stamp for the opening of the game.

The intro is a removal order filling itself in, and this makes the two pictures
it needs. Neither carries a single word: every readable thing in the intro is a
Label over this paper, looked up as a key, so the order is written in it.tres
and en.tres like the rest of the game.

The stamp is deliberately illegible. A stamp with a word on it would be a word
baked into an image — and an unreadable stamp is funnier and truer to a game
whose signature line reads "firmato: illeggibile".

Palette note: the game is cold everywhere, so the paper is the one warm surface
and the stamp the one warm accent. Both are UI, not room assets, so they are
not measured against a room's mother palette.

Run from the project root:  python tools/make_intro_form.py
"""
import numpy as np
from PIL import Image

PAPER_ASSET = "assets/ui/ui_order_form.png"
STAMP_ASSET = "assets/ui/ui_stamp.png"
W, H = 320, 180                   # the game's own resolution: this fills the screen

rng = np.random.default_rng(1958)

BAYER = np.array([
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]) / 64.0

DESK = (26, 22, 34)          # what the paper is lying on
PAPER = (214, 206, 188)      # the sheet
PAPER_SHADE = (188, 178, 158)
PAPER_DEEP = (162, 150, 130)
RULE = (120, 110, 96)        # printed rules and boxes
RULE_FAINT = (168, 158, 140)
INK = (34, 28, 40)
STAMP_IN = (140, 52, 56)
STAMP_DARK = (104, 36, 42)


def paper() -> None:
    """The sheet.

    Flat, on purpose. The first version shaded the whole surface with ordered
    dithering and the result was a screen door — the very thing CLAUDE.md warns
    about. A sheet of paper at this resolution is one flat tone; what makes it
    read as paper is the *shapes* on it: a vignette of two hard steps at the
    edge, two fold creases with a shadow and a highlight each, a coffee ring, a
    torn corner. Tooth is given deliberately, never as noise.
    """
    img = np.zeros((H, W, 4), dtype=np.uint8)
    img[..., :3] = DESK
    img[..., 3] = 255

    x0, y0, x1, y1 = 8, 5, 312, 176
    img[y0:y1, x0:x1, :3] = PAPER

    # Vignette: two hard steps at the edge, not a gradient. A sheet lifts very
    # slightly at its edges, and two bands say that better than fifty do.
    for inset, colour in ((0, PAPER_DEEP), (1, PAPER_SHADE), (2, PAPER_SHADE)):
        img[y0 + inset, x0 + inset:x1 - inset, :3] = colour
        img[y1 - 1 - inset, x0 + inset:x1 - inset, :3] = colour
        img[y0 + inset:y1 - inset, x0 + inset, :3] = colour
        img[y0 + inset:y1 - inset, x1 - 1 - inset, :3] = colour

    # Folded in three for years: each crease is a shadow with a lit edge under
    # it, which is what makes it a fold and not a drawn line.
    for fy in (y0 + 57, y0 + 115):
        img[fy, x0 + 3:x1 - 3, :3] = PAPER_SHADE
        img[fy + 1, x0 + 3:x1 - 3, :3] = PAPER_DEEP
        img[fy + 2, x0 + 3:x1 - 3, :3] = PAPER

    # A ring from a cup somebody put down on it, which is the whole story of
    # how much this document was respected.
    ring_cx, ring_cy, ring_r = 248, 50, 18
    for y in range(ring_cy - ring_r - 2, ring_cy + ring_r + 3):
        for x in range(ring_cx - ring_r - 2, ring_cx + ring_r + 3):
            if not (y0 < y < y1 - 1 and x0 < x < x1 - 1):
                continue
            d = ((x - ring_cx) / ring_r) ** 2 + ((y - ring_cy) / (ring_r * 0.82)) ** 2
            if 0.88 < d < 1.06:
                img[y, x, :3] = PAPER_DEEP
            elif 0.72 < d <= 0.88:
                img[y, x, :3] = PAPER_SHADE

    # The torn top-right corner: somebody has already detached the receipt.
    for i in range(13):
        cut = 13 - i + int(rng.integers(0, 2))
        img[y0 + i, x1 - cut:x1, :3] = DESK

    # ---- what is printed on the form ---------------------------------------
    # A heading band, a body area with faint guide lines, and the box the stamp
    # lands in. No words: every readable thing is a Label over this.
    img[y0 + 5, x0 + 8:x1 - 8, :3] = RULE
    img[y0 + 7, x0 + 8:x1 - 8, :3] = RULE_FAINT
    img[y0 + 27, x0 + 8:x1 - 8, :3] = RULE
    img[y0 + 28, x0 + 8:x1 - 8, :3] = RULE_FAINT
    img[y1 - 8, x0 + 8:x1 - 8, :3] = RULE_FAINT

    # The margin rule: everything in this world has a column for the office to
    # write in that nobody ever writes in.
    img[y0 + 29:y1 - 8, x0 + 22, :3] = RULE_FAINT

    # No ruled guide lines under the body. There were, spaced to the VBox in
    # Main.tscn, and they cannot survive contact with the text: the lines wrap
    # to two rows in one language and one in the other, so any spacing drawn
    # here is wrong in at least one of them. The margin rule and the frame do
    # the same job and do not have to agree with anything.

    # The stamp box, empty until the order is executed.
    bx0, by0, bx1, by1 = 204, 122, 302, 168
    img[by0, bx0:bx1, :3] = RULE
    img[by1, bx0:bx1, :3] = RULE
    img[by0:by1 + 1, bx0, :3] = RULE
    img[by0:by1 + 1, bx1 - 1, :3] = RULE

    # Two punch holes in the margin: nothing here is ever filed loose.
    for hy in (58, 124):
        for y in range(hy - 4, hy + 5):
            for x in range(x0 + 6, x0 + 18):
                if ((y - hy) / 3.0) ** 2 + ((x - (x0 + 12)) / 3.0) ** 2 < 1.0:
                    img[y, x, :3] = DESK
                elif ((y - hy) / 4.0) ** 2 + ((x - (x0 + 12)) / 4.0) ** 2 < 1.0:
                    img[y, x, :3] = PAPER_DEEP

    Image.fromarray(img).save(PAPER_ASSET)
    print(f"{PAPER_ASSET}  {W}x{H}  "
          f"({len(np.unique(img[..., :3].reshape(-1, 3), axis=0))} colori)")


def stamp() -> None:
    """An illegible stamp: two rings and a scribble that is almost writing."""
    sw, sh = 80, 36
    img = np.zeros((sh, sw, 4), dtype=np.uint8)
    cx, cy = sw / 2, sh / 2

    yy, xx = np.mgrid[0:sh, 0:sw]
    d = ((xx - cx) / (sw / 2 - 2)) ** 2 + ((yy - cy) / (sh / 2 - 2)) ** 2
    # Two rings. The ink is uneven, which is what a rubber stamp does and what
    # keeps it from reading as a drawn rectangle.
    ring_a = (d > 0.80) & (d < 1.00)
    ring_b = (d > 0.58) & (d < 0.68)
    ink = ring_a | ring_b

    # The scribble inside. Not dashes — a continuous wavering line that rises
    # and falls like handwriting, with a couple of ascenders. Dashes read as a
    # barcode; this reads as a word you cannot make out, which is the point.
    for row, ry in enumerate((13, 22)):
        x = 20
        phase = row * 2.1
        while x < sw - 20:
            # Two slow waves rather than one fast one: a single high-frequency
            # sine at this size comes out as a mountain range, not as writing.
            wob = int(round(1.7 * np.sin(x * 0.21 + phase)
                            + 1.1 * np.sin(x * 0.53 + phase * 2)))
            ink[ry + wob, x] = True
            ink[ry + wob + 1, x] = True
            if rng.random() < 0.12:                       # an ascender
                ink[ry + wob - 3:ry + wob, x] = True
            x += 1
        # A break in the middle, so it reads as two words.
        gap = sw // 2 + row * 3
        ink[ry - 5:ry + 5, gap:gap + 3] = False

    # Patchy coverage, so the stamp looks pressed rather than printed.
    patchy = ink & (np.tile(BAYER, (sh // 8 + 1, sw // 8 + 1))[:sh, :sw] < 0.86)
    img[patchy, :3] = STAMP_IN
    heavy = patchy & (yy > cy)
    img[heavy, :3] = STAMP_DARK
    img[patchy, 3] = 255

    Image.fromarray(img).save(STAMP_ASSET)
    print(f"{STAMP_ASSET}  {sw}x{sh}")


if __name__ == "__main__":
    paper()
    stamp()
