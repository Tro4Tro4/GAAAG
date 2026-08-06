"""Draws the Station's four objects: console, lever, service hatch, log book.

They were flat Polygon2D rectangles in the scene until now. Each sprite here is
exactly the bounding box of the polygon it replaces, so the scene keeps its
verified hotspot geometry and only the picture changes:

    prop_service_point   24x32, at the node
    prop_console         80x80, at the node
    prop_lever           20x44, offset (0, -8)
    prop_log             36x14, offset (0, -3)

Palette: the corridor's steel and brass, because it is the same facility, plus
amber for anything lit. Amber is spent deliberately and only here — the console's
screen, the lamp, the lever's ready light — so that the warm pixels in the room
are exactly the ones the puzzle is about.

The light comes from above and slightly left, as in every other room, so the lit
edge of everything is its top and its left.

Run from the project root:  python tools/make_station_props.py
"""
import sys

sys.path.insert(0, ".claude/skills/pixel-adventure-assets/scripts")
from pixel_helpers import PixelCanvas

OUT = "assets/sprites"


def c(h, a=255):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


INK = c("141915")
STEEL_D = c("2D322E")
STEEL_S = c("3E433F")
STEEL = c("5F645E")
STEEL_L = c("96988E")
STEEL_H = c("9BA7A3")
BRASS_D = c("33352B")
BRASS = c("7C7E62")
BRASS_L = c("AEAB83")
BRASS_H = c("D8C88F")
AMBER_D = c("5A3C1E")
AMBER = c("C08A34")
AMBER_L = c("F0C06A")
GLASS_D = c("22302C")
RUST = c("8C6A4A")


def boxed(k, x0, y0, x1, y1, fill, lit=None, shade=None):
    """A panel with a dark outline, a lit top-left and a shaded bottom-right.

    Every object in this room is made of these, which is what makes four
    separately drawn things look like they came out of the same workshop.
    """
    k.rect(x0, y0, x1, y1, INK)
    k.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill)
    if lit:
        k.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 1, lit)
        k.rect(x0 + 1, y0 + 1, x0 + 1, y1 - 1, lit)
    if shade:
        k.rect(x0 + 1, y1 - 1, x1 - 1, y1 - 1, shade)
        k.rect(x1 - 1, y0 + 2, x1 - 1, y1 - 1, shade)


# ------------------------------------------------------------------ console ---
def console() -> PixelCanvas:
    k = PixelCanvas(80, 80)
    # The body: a cabinet standing on the floor, so its bottom is the sprite's
    # bottom and the shading gets darker downwards.
    boxed(k, 4, 6, 75, 79, STEEL, STEEL_L, STEEL_D)
    k.rect(5, 60, 74, 78, STEEL_S)
    k.rect(5, 60, 74, 60, STEEL_L)

    # The screen, recessed: outline in, dark glass, then the amber lines. Two
    # rows of them, unevenly spaced, so it reads as a readout and not a grille.
    boxed(k, 12, 12, 67, 44, GLASS_D, STEEL_D, STEEL_L)
    for i, y in enumerate((17, 21, 25, 31, 35)):
        w = (34, 26, 30, 20, 24)[i]
        k.rect(16, y, 16 + w, y, AMBER if i % 2 else AMBER_L)
        k.rect(16, y + 1, 16 + w - 6, y + 1, AMBER_D)
    k.rect(14, 14, 65, 14, c("32403C"))                    # the glass's sheen
    k.rect(14, 15, 40, 15, c("2A3834"))

    # The sloped desk under the screen, with two rows of keys and a dial.
    boxed(k, 8, 46, 71, 58, STEEL_S, STEEL_L, STEEL_D)
    for row, y in enumerate((49, 54)):
        for x in range(12, 56, 5):
            k.rect(x, y, x + 3, y + 2, STEEL_L if (x // 5 + row) % 3 else BRASS_L)
            k.rect(x, y, x + 3, y, STEEL_H)
    for y in range(48, 57):                                # the dial
        for x in range(59, 68):
            if (x - 63) ** 2 + (y - 52) ** 2 <= 16:
                k.set(x, y, BRASS)
    k.rect(63, 49, 63, 52, BRASS_H)
    k.set(63, 52, INK)

    # The lamp that says the desk is live, and its little brass bezel.
    boxed(k, 30, 64, 44, 74, STEEL_D, STEEL, None)
    k.rect(33, 66, 41, 72, AMBER_D)
    k.rect(34, 67, 40, 71, AMBER)
    k.rect(35, 68, 38, 69, AMBER_L)

    k.rect(6, 76, 73, 78, STEEL_D)                         # the plinth
    k.rect(6, 76, 73, 76, STEEL)
    k.set(70, 22, RUST)
    k.set(9, 55, RUST)
    return k


# -------------------------------------------------------------------- lever ---
def lever() -> PixelCanvas:
    # 20x44 and not the 16x40 of the polygon it replaces: it fills its collision
    # shape instead of sitting inside it. Drawn narrower it read as a scratch on
    # the wall -- a lever needs its quadrant plate to be legible at all.
    k = PixelCanvas(20, 44)
    # A quadrant plate bolted to the wall, with the lever standing in it. The
    # plate is what makes the lever legible: a bare stick reads as a scratch.
    boxed(k, 2, 8, 17, 43, STEEL_S, STEEL_L, STEEL_D)
    k.rect(7, 12, 12, 40, STEEL_D)                         # the slot
    k.rect(7, 12, 12, 12, INK)
    for y in (17, 24, 31, 38):                             # notches
        k.rect(4, y, 15, y, STEEL_L)
        k.set(3, y, INK)
        k.set(16, y, INK)
        k.rect(4, y + 1, 15, y + 1, STEEL_D)

    # The shaft, up in the "not yet pulled" position, and the knob on top.
    k.rect(8, 2, 11, 22, INK)
    k.rect(9, 3, 10, 21, BRASS)
    k.rect(9, 3, 9, 21, BRASS_L)
    boxed(k, 5, 0, 14, 7, BRASS, BRASS_H, BRASS_D)
    k.rect(7, 2, 12, 4, BRASS_L)
    k.rect(7, 2, 9, 2, BRASS_H)

    k.rect(4, 41, 6, 42, AMBER_D)                          # the ready light
    k.set(5, 41, AMBER_L)
    k.set(15, 15, RUST)
    return k


# ------------------------------------------------------------ service hatch ---
def service_point() -> PixelCanvas:
    k = PixelCanvas(24, 32)
    # The staff end of the pneumatic line: a hatch in a brass housing, with the
    # posting slot across it. Brass and not steel, so it reads as belonging to
    # the tube rather than to the wall — and so it matches the corridor's public
    # posting point, which is its counterpart at the other end.
    boxed(k, 1, 1, 22, 30, BRASS, BRASS_L, BRASS_D)
    boxed(k, 4, 4, 19, 17, STEEL_S, STEEL_L, STEEL_D)      # the flap
    k.rect(6, 7, 17, 8, INK)                               # the slot
    k.rect(6, 9, 17, 9, STEEL_D)
    k.rect(6, 6, 17, 6, STEEL_H)
    k.rect(7, 12, 16, 14, STEEL_D)                         # a label plate
    k.rect(8, 13, 15, 13, STEEL_L)

    boxed(k, 5, 20, 18, 27, BRASS_D, BRASS, None)          # the catch and lamp
    k.rect(7, 22, 11, 25, BRASS_L)
    k.rect(13, 22, 16, 25, AMBER_D)
    k.rect(14, 23, 15, 24, AMBER)
    for y in (2, 29):                                      # four fixing bolts
        for x in (3, 20):
            k.set(x, y, BRASS_H)
    k.set(21, 18, RUST)
    return k


# ----------------------------------------------------------------- log book ---
def log_book() -> PixelCanvas:
    k = PixelCanvas(36, 14)
    # Lying open on the shelf, seen from slightly above: two pages, a spine down
    # the middle, ruled lines. It has to read as paper at a glance, because it is
    # the thing the whole complaint has to end up inside.
    k.rect(0, 2, 35, 13, INK)
    k.rect(1, 3, 34, 12, c("6B6F5C"))                      # the cover
    k.rect(1, 3, 34, 3, c("8A8D72"))
    k.rect(3, 4, 32, 12, c("C9C7AA"))                      # the pages
    k.rect(3, 4, 32, 4, c("E4E1C4"))
    k.rect(17, 4, 18, 12, c("9A9880"))                     # the spine
    for y in (6, 8, 10):
        k.rect(5, y, 15, y, c("9A9880"))
        k.rect(20, y, 30, y, c("9A9880"))
    k.rect(5, 6, 11, 6, c("7C7A66"))                       # an entry, written in
    k.rect(20, 6, 24, 6, c("7C7A66"))
    k.rect(24, 0, 30, 3, BRASS_D)                          # the pen across it
    k.rect(25, 1, 29, 2, BRASS_L)
    k.set(30, 3, INK)
    return k


PROPS = [("prop_console", console), ("prop_lever", lever),
         ("prop_service_point", service_point), ("prop_log", log_book)]


if __name__ == "__main__":
    for name, fn in PROPS:
        k = fn()
        k.save(f"{OUT}/{name}.png")
        print(f"{OUT}/{name}.png  {k.image.size[0]}x{k.image.size[1]}")
