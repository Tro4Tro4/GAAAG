"""Draws the inventory item icons.

The inventory slot is 88x16 units with an 8 px font (see inventory_panel.gd),
and a Button adds the theme's padding on top of whatever it contains, so an
icon here is 12x12: it fits inside the existing slot instead of pushing it
taller. It sits beside the name, it does not replace it — at this size a
drawing says "paper" or "metal" at a glance, but never *which* form it is.

The palette is not invented. It is derived from the Lobby, where these things
are picked up, and shares the rack's paper tones exactly: a form pulled out of
that rack has to look like it came from there. Light falls from above and
slightly left, like the Lobby's fluorescent and like the character sheets.

The set is designed together, because three of the eight items are sheets of
paper and two are buttons. What tells them apart is the thing the puzzle cares
about: the empty box on the complaint form, the plate stuck into it on the
filled one, the label on the button. Read side by side, the icons say what the
puzzle is about.

Run from the project root:  python tools/make_item_icons.py
"""
import sys

sys.path.insert(0, ".claude/skills/pixel-adventure-assets/scripts")
from pixel_helpers import PixelCanvas

SPRITES = "assets/sprites"
SIZE = 12

CLEAR = (0, 0, 0, 0)
# From prop_rack.png — the thing the forms are pulled out of.
OUT = (40, 33, 48, 255)          # 282130
PAPER = (188, 180, 161, 255)     # BCB4A1
PAPER_L = (223, 216, 186, 255)   # DFD8BA
PAPER_D = (150, 143, 128, 255)   # derived: paper towards the outline
INK = (103, 103, 119, 255)       # 676777 — printed text, never black
# From the Lobby's cold end: enamel and painted metal.
ENAMEL = (120, 156, 149, 255)    # 768C85
ENAMEL_L = (163, 192, 196, 255)  # A3C0C4
METAL = (120, 124, 139, 255)     # 787C8B
METAL_L = (138, 145, 158, 255)   # 8A919E
# The one warm note in the game, and it is Lino's hair: the sticker borrows it
# so that it reads as "not part of the building" without leaving the palette.
OCHRE = (216, 180, 110, 255)
OCHRE_D = (170, 132, 74, 255)


# --------------------------------------------------------------- paper -------
def _sheet(c: PixelCanvas, fold: int = 2) -> None:
    """The sheet every paper item is drawn on: body, folded corner, lit edge."""
    left, right, top, bottom = 2, 9, 0, 11
    c.rect(left, top, right, bottom, OUT)
    c.rect(left + 1, top + 1, right - 1, bottom - 1, PAPER)

    # The folded corner. Without it the silhouette is a rectangle, and a
    # rectangle at this size reads as a card, not as paper.
    for i in range(fold):
        for x in range(right - fold + 1 + i, right + 1):
            c.set(x, top + i, CLEAR)
        c.set(right - fold + i, top + i, OUT)
    c.set(right, top + fold, OUT)
    c.set(right - 1, top + fold, PAPER_D)

    for y in range(top + 1, bottom):
        c.set(left + 1, y, PAPER_L)
    for x in range(left + 2, right):
        c.set(x, bottom - 1, PAPER_D)


def _lines(c: PixelCanvas, rows) -> None:
    for y, end in rows:
        for x in range(4, end + 1):
            c.set(x, y, INK)


def draw_form(c: PixelCanvas) -> None:
    """Modulo 12-B: print all the way down, and nothing to fill in.

    It is the only paper item with no box, which is the joke — the form whose
    next entry does not exist.
    """
    _sheet(c)
    _lines(c, ((2, 8), (4, 7), (6, 8), (8, 7)))


def draw_form_blank(c: PixelCanvas) -> None:
    """Modulo di reclamo: print, then the empty box the plate has to go in."""
    _sheet(c)
    _lines(c, ((2, 8), (4, 7)))
    c.rect(4, 6, 8, 9, INK, fill=False)


def draw_form_filled(c: PixelCanvas) -> None:
    """Reclamo compilato: the same sheet, with the plate stuck in the box.

    Deliberately the same drawing as the blank one plus the enamel: the pair
    has to read as one object before and after, or the player cannot see that
    the puzzle moved forward.
    """
    _sheet(c)
    _lines(c, ((2, 8), (4, 7)))
    c.rect(4, 6, 8, 9, INK, fill=False)
    c.rect(5, 7, 7, 8, ENAMEL)
    c.set(5, 7, ENAMEL_L)


def draw_renewal(c: PixelCanvas) -> None:
    """Rinnovo dell'accreditamento: the letter that sat in the tube for years.

    The stamp is the only round thing in the paper family, so it carries the
    whole difference at a glance.
    """
    _sheet(c)
    _lines(c, ((2, 8), (4, 6)))
    # A round stamp: the only circle in the paper family, which is what
    # carries the whole difference at a glance. Ring first, then the fill,
    # so the ring stays a ring and does not close up.
    for x, y in ((5, 6), (6, 6), (4, 7), (7, 7),
                 (4, 8), (7, 8), (5, 9), (6, 9)):
        c.set(x, y, OCHRE_D)
    c.rect(5, 7, 6, 8, OCHRE)


# --------------------------------------------------------------- metal -------
def draw_plate(c: PixelCanvas) -> None:
    """Targhetta SEZIONE 4: enamel, landscape, one screw still in it.

    Landscape where every other item is portrait — the shape alone separates
    it from the paper without needing the text to be legible.
    """
    c.rect(1, 3, 10, 8, OUT)
    c.rect(2, 4, 9, 7, ENAMEL)
    for x in range(2, 10):
        c.set(x, 4, ENAMEL_L)
    for x in range(3, 10):
        c.set(x, 7, (94, 124, 120, 255))
    # Two lines standing in for SEZIONE 4, and the screw that is half out.
    for x in range(4, 9):
        c.set(x, 5, OUT)
    for x in range(4, 7):
        c.set(x, 6, OUT)
    c.set(3, 5, METAL_L)
    c.set(3, 6, METAL)


# A disc of diameter 8, written as the span of each row. Spelled out instead
# of computed: at twelve pixels a circle drawn from an equation comes out
# lopsided, and the only way to know is to look at every row.
_DISC = {2: (4, 7), 3: (3, 8), 4: (2, 9), 5: (2, 9),
         6: (2, 9), 7: (2, 9), 8: (3, 8), 9: (4, 7)}


def _button_body(c: PixelCanvas) -> None:
    """A round push button seen from above, filling the icon.

    The first version was six pixels wide inside its outline and read as a
    battery: at this size a disc has to be nearly as wide as the canvas, or
    the outline eats the shape it is meant to describe.
    """
    for y, (x0, x1) in _DISC.items():                       # outline
        c.rect(x0, y, x1, y, OUT)
    for y, (x0, x1) in _DISC.items():                       # face, inset by 1
        if 3 <= y <= 8:
            c.rect(x0 + 1, y, x1 - 1, y, METAL)
    for x in range(4, 8):                                   # lit top
        c.set(x, 3, METAL_L)
    c.set(3, 4, METAL_L)
    c.set(3, 5, METAL_L)
    for x in range(4, 8):                                   # shaded underside
        c.set(x, 8, (86, 90, 104, 255))


def draw_button(c: PixelCanvas) -> None:
    """Pulsante: grey, detached from everything, convinced of itself."""
    _button_body(c)


def draw_labelled_button(c: PixelCanvas) -> None:
    """Pulsante etichettato: the same button with the sticker on it.

    Same body plus the ochre, exactly as the filled form is the blank one plus
    the enamel. The two pairs teach the same reading.
    """
    _button_body(c)
    # A band right across the disc, edge to edge: a label stuck on, not a
    # smaller shape floating in the middle of the button.
    c.rect(3, 5, 8, 7, OCHRE)
    for x in range(3, 9):
        c.set(x, 5, (232, 202, 146, 255))
    for x in range(3, 9):
        c.set(x, 7, OCHRE_D)
    for x in range(4, 8):
        c.set(x, 6, OUT)


def draw_sticker(c: PixelCanvas) -> None:
    """Adesivo NON IMPILARE: a peeling label, curled at one corner.

    The curl is what says "it comes off", which is the only property of it the
    puzzle uses.
    """
    c.rect(2, 2, 9, 9, OUT)
    c.rect(3, 3, 8, 8, OCHRE)
    for x in range(3, 9):
        c.set(x, 3, (232, 202, 146, 255))
    for x in range(3, 9):
        c.set(x, 8, OCHRE_D)
    for x in range(4, 8):
        c.set(x, 5, OUT)
    for x in range(4, 7):
        c.set(x, 7, OUT)
    # The peeled corner: paper-white underside lifting off the bottom right.
    for x, y in ((8, 9), (9, 9), (9, 8)):
        c.set(x, y, PAPER_L)
    c.set(9, 9, OUT)


ICONS = [
    ("item_form", draw_form),
    ("item_form_blank", draw_form_blank),
    ("item_form_filled", draw_form_filled),
    ("item_renewal", draw_renewal),
    ("item_plate", draw_plate),
    ("item_button", draw_button),
    ("item_labelled_button", draw_labelled_button),
    ("item_sticker", draw_sticker),
]


def main() -> None:
    for name, draw in ICONS:
        c = PixelCanvas(SIZE, SIZE)
        draw(c)
        c.save(f"{SPRITES}/{name}.png")
        print(f"{SPRITES}/{name}.png  {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
