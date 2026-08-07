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
# Cardboard, and the first tones in this set that do not come from the Lobby:
# the document box is picked up in the Apartment, so its colours are the ones
# make_apartment_background.py already put in that room. Same rule as before —
# an item looks like the place it came out of — applied to a second place.
CARD = (146, 116, 82, 255)
CARD_L = (176, 140, 100, 255)
CARD_D = (108, 84, 62, 255)


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


def draw_certificate(c: PixelCanvas) -> None:
    """Certificato di occupazione: the sheet that sat in the tube for three years.

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



def draw_documents(c: PixelCanvas) -> None:
    """Scatola dei documenti: cardboard, landscape, with the old label on it.

    The only box in the set, so the silhouette alone separates it from the four
    flat things — which matters more here than anywhere, because Lino carries it
    around for the rest of the chapter and it has to be findable in a full bag
    at a glance.

    The label is the whole point of the object and so it gets the lightest value
    in the icon: it is what made the box takeable, and the player worked for it.
    """
    # The lid, drawn as a band overhanging the body on both sides. That overhang
    # is the whole of "this is a box and not a rectangle": a first attempt with
    # the lid flush and a seam line across the middle read as a shelf.
    c.rect(0, 2, 11, 5, OUT)
    c.rect(1, 3, 10, 4, CARD_L)
    for x in range(1, 11):
        c.set(x, 4, CARD)

    # The body, one pixel narrower each side so the lid sits proud of it.
    c.rect(1, 5, 10, 10, OUT)
    c.rect(2, 6, 9, 9, CARD)
    for y in range(6, 10):
        c.set(9, y, CARD_D)

    # The delivery label: small, on the right of the front face, and the
    # lightest thing in the icon. It is what made the box takeable, so it is
    # what the eye should land on.
    c.rect(5, 6, 8, 9, PAPER_L)
    c.set(6, 7, INK)
    c.set(7, 7, INK)
    c.set(6, 8, INK)


ICONS = [
    ("item_form_blank", draw_form_blank),
    ("item_form_filled", draw_form_filled),
    ("item_certificate", draw_certificate),
    ("item_plate", draw_plate),
    ("item_documents", draw_documents),
]


def main() -> None:
    for name, draw in ICONS:
        c = PixelCanvas(SIZE, SIZE)
        draw(c)
        c.save(f"{SPRITES}/{name}.png")
        print(f"{SPRITES}/{name}.png  {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
