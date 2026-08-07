"""Draws the Apartment sprites: door, window, boxes, tags, mattress, and the
loading clerk — the first person in the game who is not a playable character.

Everything here is pixel art at 1:1, drawn to be used at scale = 1 with the
project's Nearest filter, and every node's origin is where the object meets the
floor, because Y-sorting looks at the node's Y and not at the extent of what it
draws.

The palette is imported from make_apartment_background.py rather than copied.
Copying is how a room drifts: the background is regenerated, two tones move, and
the props go on being the old room's colours while nothing complains. Importing
means the check that the two agree cannot be skipped, because there is only one
list.

Why these are sprites and not paint, one reason each:
  * the door leaf and the window are hotspots, and a hotspot whose picture is in
    the background can never change its appearance;
  * the stack, the document box and the mattress stand on the floor inside the
    navmesh, so a character walks in front of and behind them;
  * the two tags are a StateVisual pair — the same tag ticked and struck
    through — and a thing with states cannot be one image;
  * the clerk is a person.

Run from the project root:  python tools/make_apartment_props.py
"""
import sys

sys.path.insert(0, ".claude/skills/pixel-adventure-assets/scripts")
sys.path.insert(0, "tools")

from pixel_helpers import PixelCanvas

from make_apartment_background import BOARD, CARD, GLASS, INK, SKIRT, SKY, TAPE, WALL

SPRITES = "assets/sprites"
CLEAR = (0, 0, 0, 0)


def rgba(colour, alpha=255):
    return (colour[0], colour[1], colour[2], alpha)


OUT = rgba(INK)
# The clerk's own colours, derived from the room and not invented: the overall
# is the skirting board's blue-grey, the clipboard is cardboard, and the skin
# and hair sit in the warm end the boxes already occupy. Deriving rather than
# inventing is what keeps him inside the palette check.
COAT = rgba((72, 82, 104))
COAT_L = rgba((96, 108, 132))
COAT_D = rgba((48, 55, 72))
SKIN = rgba((196, 152, 120))
SKIN_D = rgba((150, 112, 86))
HAIR = rgba((74, 56, 46))
BOOT = rgba((40, 36, 46))


def draw_door(c: PixelCanvas) -> None:
    """The leaf, standing open against the wall — the movers keep it wedged.

    It has no state in the scene, which is why there is one drawing and not two:
    a door that is held open by somebody else's rubber wedge is not something
    Lino opens and shuts, it is a way through. The same is already true of the
    street door downstairs, and the text there says so.
    """
    w, h = c.width, c.height
    c.rect(0, 0, w - 1, h - 1, OUT)
    c.rect(1, 1, w - 2, h - 2, rgba(SKIRT[2]))

    # Two panels, which is what makes a slab of colour read as a door.
    for y0, y1 in ((4, h // 2 - 3), (h // 2 + 1, h - 6)):
        c.rect(3, y0, w - 4, y1, rgba(SKIRT[1]))
        c.rect(4, y0 + 1, w - 5, y1 - 1, rgba(SKIRT[2]))
        for x in range(4, w - 4):
            c.set(x, y0 + 1, rgba(SKIRT[3]))

    # The lit edge down the hinge side: it stands open into the room, so the
    # daylight from the window catches it.
    for y in range(1, h - 1):
        c.set(w - 2, y, rgba(SKIRT[3]))

    # The wedge holding it, and the handle.
    c.rect(w - 5, h - 4, w - 2, h - 2, rgba(BOARD[3]))
    c.rect(1, h // 2 - 1, 3, h // 2 + 1, rgba(GLASS[3]))


def draw_window(c: PixelCanvas) -> None:
    """Frame, bars and glass, with the street behind it.

    The glass carries a sliver of what is outside — sky above, the depot roof
    below — because a window showing nothing is a mirror, and there is a removal
    van down there that the player has already met.
    """
    w, h = c.width, c.height
    c.rect(0, 0, w - 1, h - 1, OUT)
    c.rect(1, 1, w - 2, h - 2, rgba(WALL[1]))

    # The glass: sky in the upper part, the buildings opposite below it.
    c.rect(3, 3, w - 4, h - 4, rgba(SKY[2]))
    c.rect(3, h // 2, w - 4, h - 4, rgba(GLASS[2]))
    c.rect(3, h - 9, w - 4, h - 4, rgba(GLASS[1]))
    for x in range(4, w - 4, 7):                      # roofs across the street
        c.rect(x, h - 12, x + 4, h - 9, rgba(GLASS[1]))

    # The van's roof, bottom right: the one thing out there worth recognising.
    c.rect(w - 20, h - 8, w - 5, h - 5, rgba(BOARD[4]))
    c.rect(w - 20, h - 8, w - 5, h - 7, rgba(CARD[4]))

    # Glazing bars, and the reflection streak that says there is glass in it.
    c.rect(w // 2 - 1, 2, w // 2, h - 3, rgba(WALL[1]))
    c.rect(2, h // 2 - 1, w - 3, h // 2, rgba(WALL[1]))
    for i in range(9):
        c.set(5 + i, 5 + i, rgba(SKY[4]))
        c.set(6 + i, 5 + i, rgba(SKY[4]))

    # The frame's lit inner edge, and the grime in the corners.
    for x in range(1, w - 1):
        c.set(x, 1, rgba(WALL[3]))
    for y in range(1, h - 1):
        c.set(1, y, rgba(WALL[3]))
    for x, y in ((3, h - 5), (4, h - 5), (w - 5, h - 5), (w - 4, 3)):
        c.set(x, y, rgba(WALL[0]))


def _box(c: PixelCanvas, x0, y0, x1, y1, tone=2, taped=True):
    """One cardboard box with its tape and its flap seam."""
    c.rect(x0, y0, x1, y1, OUT)
    c.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, rgba(CARD[tone]))
    for x in range(x0 + 1, x1):
        c.set(x, y0 + 1, rgba(CARD[min(4, tone + 1)]))
    for y in range(y0 + 1, y1):
        c.set(x1 - 1, y, rgba(CARD[max(0, tone - 1)]))
    if taped:
        mid = (x0 + x1) // 2
        c.rect(mid - 1, y0 + 1, mid, y1 - 1, rgba(TAPE))
        c.rect(x0 + 1, y0 + 5, x1 - 1, y0 + 5, rgba(CARD[max(0, tone - 1)]))


def _tag(c: PixelCanvas, x0, y0):
    """The catalogue tag: a small pale label with a printed line on it.

    Drawn on the boxes that are under catalogue. It is the room's way of saying
    which things Lino may not touch, and it says it without a word of text.
    """
    c.rect(x0, y0, x0 + 7, y0 + 5, OUT)
    c.rect(x0 + 1, y0 + 1, x0 + 6, y0 + 4, rgba((196, 190, 176)))
    c.rect(x0 + 2, y0 + 2, x0 + 5, y0 + 2, rgba(SKIRT[1]))


def draw_boxes(c: PixelCanvas) -> None:
    """The stack of catalogued boxes: three up, two along, tags on the front.

    These are the rule made visible. Everything in this stack has been listed by
    somebody else, and the tags are how the player knows it before anybody says
    so.
    """
    _box(c, 0, 12, 26, 30, tone=2)
    _box(c, 26, 8, 50, 30, tone=1)
    _box(c, 4, 0, 30, 12, tone=3)
    _tag(c, 8, 18)
    _tag(c, 32, 14)
    _tag(c, 12, 4)



def draw_docbox(c: PixelCanvas) -> None:
    """The document box: smaller, older, and never unpacked.

    Deliberately not the same cardboard as the stack — it is a shade darker and
    it has no fresh tape, because this one was sealed three years ago and has
    been in a corner ever since. The player has to be able to pick it out of a
    room full of boxes, and the difference cannot be a label they have to read.
    """
    w, h = c.width, c.height
    _box(c, 0, 4, w, h, tone=1, taped=False)

    # Old tape, yellowed and lifting at one end: the difference that says "this
    # one has been shut for years" at a glance.
    mid = w // 2
    c.rect(mid - 1, 5, mid, h - 2, rgba((150, 138, 106)))
    c.set(mid - 1, 5, rgba((178, 166, 130)))
    c.set(mid - 2, 6, rgba((178, 166, 130)))

    # The flap seam, and dust on the top face.
    c.rect(1, 9, w - 2, 9, rgba(CARD[0]))
    for x in range(2, w - 3, 3):
        c.set(x, 5, rgba(CARD[3]))



def draw_delivery_tag(c: PixelCanvas, struck: bool) -> None:
    """The old delivery label on the document box, before and after.

    A StateVisual pair, and drawn as one object in two states rather than as two
    objects that resemble each other — the same rule the verb icons follow for
    Apri and Chiudi, and the inventory icons for the blank and filled form. If
    the player cannot see that the puzzle moved forward, the drawing has failed
    however pretty it is.

    Struck through in the clerk's own ink, diagonally, because that is what a
    person with a pen does to a line on a list.
    """
    w, h = c.width, c.height
    c.rect(0, 0, w - 1, h - 1, OUT)
    c.rect(1, 1, w - 2, h - 2, rgba((204, 196, 178)))
    for x in range(1, w - 1):
        c.set(x, 1, rgba((224, 218, 202)))

    # Printed lines standing in for the consignment details. Never legible at
    # this size, and never meant to be: what it says is in the hotspot's text.
    for y, end in ((3, w - 4), (5, w - 6)):
        c.rect(2, y, end, y, rgba(SKIRT[1]))

    if struck:
        for i in range(w - 4):
            y = 2 + (i * (h - 5)) // max(1, w - 5)
            c.set(2 + i, y, rgba((58, 48, 74)))
            c.set(2 + i, y + 1, rgba((58, 48, 74)))


def draw_mattress(c: PixelCanvas) -> None:
    """A mattress rolled, tied and laid along the wall.

    Horizontal, and that is the third try. Stood on end it was a rectangle with
    bands across it and read as a metal locker; stood on end with a rounded cap
    and pinched ties it read as a water heater. Both failures are the same one:
    a tall cylinder in a room is furniture, and no amount of shading argues with
    that. Lying down, a cylinder with round ends and two straps can only be a
    rolled-up something, and what it is exactly does not have to be legible —
    the hotspot's line says it.
    """
    w, h = c.width, c.height
    body, roll = rgba((162, 152, 154)), rgba((132, 124, 130))
    lit, deep = rgba((196, 188, 190)), rgba((104, 96, 106))
    ties = (w // 3, 2 * w // 3)

    for x in range(w):
        # Round ends, so the silhouette closes instead of being cut off square.
        cap = (3, 1, 0)[min(2, x)] if x < 3 else (3, 1, 0)[min(2, w - 1 - x)] if x > w - 4 else 0
        # Pinched at each strap: a roll tied tight is narrower where the tie is.
        squeeze = 1 if any(abs(x - t) <= 1 for t in ties) else 0
        y0, y1 = cap + squeeze, h - 1 - cap - squeeze

        c.set(x, y0, OUT)
        c.set(x, y1, OUT)
        for y in range(y0 + 1, y1):
            down = (y - y0) / max(1, y1 - y0)
            # Lit along the top, shading under: the light is from above and from
            # the window, and this gradient across the height is what says round.
            c.set(x, y, lit if down < 0.24 else body if down < 0.62
                  else roll if down < 0.84 else deep)

    # The spiral at the near end, seen end-on: the detail that names the object.
    c.rect(1, 4, 5, h - 5, roll)
    c.rect(2, 5, 4, h - 6, body)
    c.set(3, h // 2, lit)

    # The straps, and the knot on each.
    for x in ties:
        c.rect(x, 1, x + 1, h - 2, rgba(SKIRT[0]))
        c.rect(x - 1, 3, x + 2, 5, rgba(SKIRT[1]))


def draw_clerk(c: PixelCanvas) -> None:
    """The loading clerk: forty units tall, standing, holding a list.

    The first non-playable person in the game, and deliberately a single still
    drawing rather than a character sheet. He does not walk and he does not
    carry anything — that is the joke and it is also what makes one drawing
    honest: everybody else is hauling wardrobes down the stairs, and this one
    stands in the middle of somebody's flat ticking things off.

    Forty units is the height the project settled on for a full figure, so he
    reads as the same species as Lino without sharing his sheet. The clipboard
    is held at chest height, which is where the player's eye goes.
    """
    w, h = c.width, c.height          # 26 x 41: forty of body plus the outline
    mid = w // 2

    # Legs and boots. Slightly apart, which at this size is the whole of
    # "standing squarely and not going anywhere".
    for x0 in (mid - 5, mid + 1):
        c.rect(x0, h - 15, x0 + 4, h - 3, OUT)
        c.rect(x0 + 1, h - 15, x0 + 3, h - 4, COAT_D)
        c.rect(x0, h - 4, x0 + 4, h - 1, OUT)
        c.rect(x0 + 1, h - 4, x0 + 3, h - 2, BOOT)

    # The coat: a warehouse overall, one size too big, hem below the knee.
    c.rect(mid - 8, 12, mid + 7, h - 11, OUT)
    c.rect(mid - 7, 13, mid + 6, h - 12, COAT)
    for y in range(13, h - 12):                       # lit down the window side
        c.set(mid + 6, y, COAT_L)
    for y in range(13, h - 12):
        c.set(mid - 7, y, COAT_D)
    c.rect(mid - 1, 14, mid, h - 13, COAT_D)          # the button placket
    c.rect(mid - 7, 20, mid + 6, 21, COAT_D)          # a belt he does not need

    # Arms, both forward, because both hands are on the clipboard.
    for x0 in (mid - 10, mid + 7):
        c.rect(x0, 16, x0 + 3, 27, OUT)
        c.rect(x0 + 1, 17, x0 + 2, 26, COAT_L if x0 > mid else COAT_D)
    c.rect(mid - 10, 25, mid - 7, 28, OUT)
    c.rect(mid - 9, 26, mid - 8, 27, SKIN_D)
    c.rect(mid + 7, 25, mid + 10, 28, OUT)
    c.rect(mid + 8, 26, mid + 9, 27, SKIN)

    # The clipboard, and the pen. It is the only thing he is holding and it is
    # the thing the whole conversation is about, so it gets the lightest value
    # in the sprite and sits where the eye lands first.
    c.rect(mid - 8, 22, mid + 7, 32, OUT)
    c.rect(mid - 7, 23, mid + 6, 31, rgba((206, 198, 180)))
    for y in range(24, 31, 2):
        c.rect(mid - 5, y, mid + 4, y, rgba(SKIRT[1]))
    c.rect(mid - 8, 21, mid + 7, 22, rgba(CARD[1]))   # the clip
    c.rect(mid + 4, 19, mid + 5, 24, OUT)             # the pen, behind his ear
    c.rect(mid + 4, 20, mid + 4, 23, rgba(GLASS[3]))

    # Head, ears, and the flat cap of somebody who has been on since six.
    c.rect(mid - 5, 1, mid + 4, 13, OUT)
    c.rect(mid - 4, 2, mid + 3, 12, SKIN)
    for y in range(3, 12):                            # the side away from the
        c.set(mid - 4, y, SKIN_D)                     # window is in shadow
    c.rect(mid - 5, 0, mid + 4, 4, OUT)
    c.rect(mid - 4, 1, mid + 3, 3, HAIR)
    c.rect(mid + 3, 3, mid + 6, 4, OUT)               # the peak
    c.rect(mid + 3, 3, mid + 5, 3, HAIR)

    # Eyes and mouth: three marks, and no more. At forty units a face is a
    # silhouette with three marks in it, and a fourth turns it into a smudge.
    c.set(mid - 2, 7, OUT)
    c.set(mid + 1, 7, OUT)
    c.rect(mid - 1, 10, mid + 1, 10, SKIN_D)

    # Contact shadow, taken from the alpha of the sprite's own last rows: drawn
    # on the bounding rectangle instead it sticks out past the boots and becomes
    # the very border it was there to remove.


PROPS = [
    ("prop_flat_door", 32, 44, draw_door),
    ("prop_flat_window", 56, 40, draw_window),
    ("prop_flat_boxes", 50, 31, draw_boxes),
    ("prop_flat_docbox", 30, 19, draw_docbox),
    ("prop_flat_tag_ticked", 11, 8, lambda c: draw_delivery_tag(c, False)),
    ("prop_flat_tag_struck", 11, 8, lambda c: draw_delivery_tag(c, True)),
    ("prop_flat_mattress", 44, 16, draw_mattress),
    ("prop_clerk", 26, 41, draw_clerk),
]


def main() -> None:
    for name, w, h, draw in PROPS:
        c = PixelCanvas(w, h)
        draw(c)
        c.save(f"{SPRITES}/{name}.png")
        print(f"{SPRITES}/{name}.png  {w}x{h}")


if __name__ == "__main__":
    main()
