"""Draws the Lobby's prop sprites: notice board, form rack, chairs, door leaf.

These are sprites and not part of the background for the reasons recorded in
CLAUDE.md: the chairs sort in Y against the characters, the notice and the rack
carry writing, and the door leaf has two states that a StateVisual has to be able
to swap. The frame and the recess behind the leaf stay painted -- those never
change.

The palette is derived from assets/backgrounds/bg_lobby.png rather than invented,
which is the rule that keeps the two layers from fighting: one mother palette and
one light direction per room. The light in this room comes from the fluorescent
above and slightly left, so the lit edge of every prop is its top-left.

Run from the project root:  python tools/make_lobby_props.py
"""
import sys

sys.path.insert(0, ".claude/skills/pixel-adventure-assets/scripts")
from pixel_helpers import PixelCanvas

OUT = "assets/sprites"

# Sampled from the background, not chosen freehand.
OUTLINE = (40, 33, 48, 255)
COOL = (54, 44, 66)
PAPER = (223, 216, 186)
METAL = (138, 145, 158)
WOOD = (128, 100, 72)

# The door's own five tones and the brass of its handle, taken from the ramps in
# make_lobby_pixel_background.py so the leaf belongs to the frame painted around
# it. The last two are the corridor's floor, seen through the opening.
DOOR = [(0x28, 0x2A, 0x34, 255), (0x45, 0x49, 0x56, 255), (0x65, 0x6C, 0x77, 255),
        (0x87, 0x8F, 0x98, 255), (0xAC, 0xB4, 0xBA, 255)]
BRASS = [(0x5C, 0x4E, 0x2C, 255), (0xA2, 0x90, 0x5B, 255), (0xE8, 0xD6, 0x96, 255)]
DARK = (0x16, 0x18, 0x1E, 255)
BEYOND = (0x33, 0x40, 0x46, 255)
BEYOND_L = (0x4B, 0x5F, 0x51, 255)

# The opening the background paints, and therefore the size of both leaves.
LEAF_W, LEAF_H = 26, 44


def door_shut() -> PixelCanvas:
    """The leaf closed: two recessed panels and the handle, hinged on the right.

    Drawn here rather than painted into the background because the door has two
    states. The lobby used to show only the light on the floor and keep a closed
    door painted in the picture, which contradicted itself the moment the door
    was open.
    """
    k = PixelCanvas(LEAF_W, LEAF_H)
    k.rect(0, 0, LEAF_W - 1, LEAF_H - 1, DOOR[2])
    k.rect(0, 0, LEAF_W - 1, 0, DOOR[4])                   # lit along the top
    k.rect(0, 0, 1, LEAF_H - 1, DOOR[3])                   # and down the left
    k.rect(LEAF_W - 2, 1, LEAF_W - 1, LEAF_H - 1, DOOR[1])
    for y0, y1 in ((3, 18), (23, 37)):                     # the two panels
        k.rect(3, y0, LEAF_W - 4, y1, DOOR[1])
        k.rect(4, y0 + 1, LEAF_W - 5, y1 - 1, DOOR[2])
        k.rect(3, y0, LEAF_W - 4, y0, DOOR[0])
        k.rect(3, y0, 3, y1, DOOR[0])
        k.rect(4, y1, LEAF_W - 4, y1, DOOR[4])
    k.rect(2, 25, 7, 27, BRASS[1])                         # the handle
    k.rect(2, 25, 6, 25, BRASS[2])
    k.rect(3, 28, 6, 28, BRASS[0])
    k.rect(0, LEAF_H - 2, LEAF_W - 1, LEAF_H - 1, DARK)    # the gap underneath
    return k


def door_open() -> PixelCanvas:
    """The leaf swung back: what says "open" is seeing the corridor through it.

    The floor beyond is the corridor's colour and not this room's, which is the
    one detail that makes the opening read as somewhere else rather than as a
    black rectangle.
    """
    k = PixelCanvas(LEAF_W, LEAF_H)
    k.rect(0, 0, LEAF_W - 1, LEAF_H - 1, DARK)
    k.rect(1, LEAF_H - 13, LEAF_W - 2, LEAF_H - 1, BEYOND) # the corridor's floor
    k.rect(1, LEAF_H - 13, LEAF_W - 2, LEAF_H - 13, BEYOND_L)
    k.rect(1, LEAF_H - 6, LEAF_W - 2, LEAF_H - 5, BEYOND_L)
    # The leaf itself, standing open against the far side of the opening.
    k.rect(LEAF_W - 7, 0, LEAF_W - 1, LEAF_H - 1, DOOR[1])
    k.rect(LEAF_W - 3, 0, LEAF_W - 1, LEAF_H - 1, DOOR[2])
    k.rect(LEAF_W - 7, 0, LEAF_W - 7, LEAF_H - 1, DOOR[0])
    k.rect(LEAF_W - 7, 0, LEAF_W - 1, 0, DOOR[3])
    return k


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def ramp(base, n=3):
    """Three tones of one colour: shadow, body, light. Index 2 is the lit side."""
    return [lerp(base, COOL, 0.42 - i * 0.21) + (255,) for i in range(n)]


def notice() -> PixelCanvas:
    """The regulations, 32x24. The lines only suggest text — the words the
    player reads come from the localised look_text, not from the sprite."""
    c = PixelCanvas(32, 24)
    p = ramp(PAPER)
    c.rect(0, 0, 31, 23, OUTLINE)
    c.rect(1, 1, 30, 22, p[1])
    c.rect(1, 1, 30, 2, p[2])                       # lit top edge
    c.rect(1, 22, 30, 22, p[0])
    for i, y in enumerate(range(5, 22, 3)):
        c.rect(3, y, 28 - (i % 3) * 5, y, p[0])     # ragged lines of small print
    return c


def rack() -> PixelCanvas:
    """The form holder, 20x28: two trays, the upper one full and the lower empty.
    The joke is in the look_text; the sprite only has to make it visible."""
    c = PixelCanvas(20, 28)
    m = ramp(METAL)
    p = ramp(PAPER)
    c.rect(0, 0, 19, 27, OUTLINE)
    c.rect(1, 1, 18, 26, m[1])
    c.rect(1, 1, 18, 2, m[2])
    c.rect(2, 3, 17, 12, m[0])                      # upper tray, with forms
    c.rect(3, 4, 16, 11, p[1])
    c.rect(3, 4, 16, 5, p[2])
    c.rect(2, 15, 17, 25, m[0])                     # lower tray, empty
    c.rect(3, 16, 16, 24, m[0])
    return c


def chairs() -> PixelCanvas:
    """Four chairs in a row, 48x20, seen from a little above. The node goes where
    they touch the floor, so the sprite is drawn with its feet on the last row."""
    c = PixelCanvas(48, 20)
    w = ramp(WOOD)
    for i in range(4):
        x = i * 12
        c.rect(x + 1, 1, x + 9, 7, w[0])            # back
        c.rect(x + 2, 2, x + 8, 6, w[1])
        c.rect(x + 1, 8, x + 10, 11, w[1])          # seat
        c.rect(x + 1, 8, x + 10, 9, w[2])
        c.rect(x + 1, 12, x + 2, 19, w[0])          # legs
        c.rect(x + 9, 12, x + 10, 19, w[1])
        c.rect(x + 4, 12, x + 5, 17, w[0])
        c.rect(x + 7, 12, x + 8, 17, w[0])
    return c


def outline(c: PixelCanvas) -> PixelCanvas:
    """One dark pixel around the silhouette, so a sprite drawn in the room's own
    colours still separates from a wall painted in those same colours."""
    w, h = c.image.size
    edges = [(x, y) for y in range(h) for x in range(w)
             if c.get(x, y)[3] == 0 and any(
                 0 <= x + dx < w and 0 <= y + dy < h and c.get(x + dx, y + dy)[3] > 0
                 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in edges:
        c.set(x, y, OUTLINE)
    return c


if __name__ == "__main__":
    for name, canvas in (("prop_notice", notice()),
                         ("prop_rack", rack()),
                         ("prop_chairs", outline(chairs())),
                         ("prop_lobby_door_shut", door_shut()),
                         ("prop_lobby_door_open", door_open())):
        path = f"{OUT}/{name}.png"
        canvas.save(path)
        print(f"{path}  {canvas.image.size[0]}x{canvas.image.size[1]}")
