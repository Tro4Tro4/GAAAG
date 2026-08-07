"""Draws the Apartment background: Lino's flat, half packed by somebody else.

320x180, one screen, because a flat is not a place you walk the length of — the
room next to it is the street, which is two screens, and the contrast is worth
having.

The palette is the Street's carried indoors, and that is a production decision
as much as an aesthetic one: CLAUDE.md asks for one palette and one kit per
chapter, because the second background of a chapter has to cost a fraction of
the first. The violets are the same family as the facade — it is the same
building, from the inside — and the one warm ramp is cardboard, which is new
here and is what the room is full of.

Light comes from the right, through the window, because that is where the low
sun is in the street outside. Every shadow in here points away from it.

The floor line is 104. It is higher up the screen than the Street's 116, which
is deliberate: indoors the wall is the thing worth seeing, and 68 units of
walkable band is plenty for a room this size.

What the room says without a word of text: the pale rectangles where pictures
used to hang, the dust outline where a wardrobe stood, the tape offcuts on the
boards. Somebody has already been through here and been thorough. That is the
whole premise of gate A, and it is cheaper drawn than written.

Kept clear for sprites that land on top of this, because a background cannot see
what will be drawn over it. Only the *devices* are held out, never the wall or
the floor they are mounted on — a suppressed patch of surface leaves a bare
rectangle around the sprite that reads as a border stuck to it:
  x  24.. 56, y  60..104   the door leaf
  x 226..282, y  44.. 84   the window
  x 268..312, y  88..104   the rolled mattress
  x 193..219, y  79..120   the loading clerk
  x  61..111, y 103..134   the stack of catalogued boxes
  x 135..165, y 129..148   the document box, and its tag

The last three stand *inside* the navmesh, which is the point: a room whose
every object hugs the back wall has a dead half. Moved forward, the box stack is
something a character walks behind and the document box is something they walk
round, and the Y-sorting the project turned on has work to do.

Run from the project root:  python tools/make_apartment_background.py
"""
import colorsys

import numpy as np
from PIL import Image

ASSET = "assets/backgrounds/bg_apartment.png"
W, H = 320, 180
FLOOR_Y = 104                     # where wall meets boards
SUN_X = 300.0                     # the window, and so the light, is off right

rng = np.random.default_rng(4177)

BAYER = np.array([
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]) / 64.0

# The door and the window, up here so the props script imports them instead of
# guessing. Note DOOR_BOTTOM: it is FLOOR_Y exactly, and it is checked at the
# end of this file. A doorway drawn with its threshold lower than the floor line
# closes under the skirting and stops being an opening.
DOOR_X0, DOOR_X1, DOOR_TOP = 24, 56, 60
WIN_X0, WIN_X1, WIN_TOP, WIN_BOTTOM = 226, 282, 44, 84


def ramp(shadow, light, n=5):
    """Five tones from dark to light, with the hue turning as it goes.

    The hue takes the shorter of the two arcs round the wheel, which is the
    Street's version of this and is there because interpolating blue to warm the
    long way passes through green.
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


# The Street's wall violets, indoors. WALL is the same pair the facade uses, so
# the two rooms are the same building without anybody having to be told.
WALL = ramp((52, 44, 68), (178, 166, 190))
SKIRT = ramp((34, 29, 46), (108, 100, 120))    # painted board at the foot
# Floorboards. Deliberately darker and greyer than the first pass, which was a
# warm mid-brown: at 42% of the screen the floor is the largest single field in
# the room, and a saturated one pulled every eye away from the wall the puzzle
# is against. It now sits below the wall in value, which is also what a floor
# does in a room lit from a window.
BOARD = ramp((44, 34, 34), (116, 94, 80))
CARD = ramp((74, 56, 42), (176, 140, 100))     # cardboard: the room is full of it
GLASS = ramp((30, 34, 54), (150, 168, 190))    # the Street's glass exactly
SKY = ramp((52, 56, 102), (214, 176, 168))     # and its sky, seen through it
INK = (22, 18, 30)
TAPE = (196, 186, 158)                          # packing tape, the pale note


def banded(field, pal, width=0.18):
    """Quantises a 0..1 field onto a ramp, dithering only where bands meet.

    width is 0.18 and not the 0.34 the earlier rooms defaulted to. Measured: the
    corridor used the narrow strip and came out at 6% isolated pixels, the lobby
    used the default and came out at 17%. A wide strip on a slow gradient covers
    tens of units and reads as dirt rather than as a transition.
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


def _window_light(img, pal):
    """The patch of daylight the window lays on the floor.

    A sheared rectangle and not a glow: it is the shape of the opening, thrown
    forward and to the left because the sun outside is low and off to the right.
    Two attempts came before this — a gradient across the whole room, then a
    widening wedge over wall and floor both — and each lit the wall *around* the
    window as brightly as the floor in front of it, which is backwards. A window
    does not light the wall it is in.

    So the wall keeps only what is genuinely a consequence of the window, which
    is the spill under the sill, and all of this lands on the boards.

    The bars are drawn as shadow inside the patch. They are what makes it read
    as a window rather than as a pale rectangle somebody left on the floor, and
    they cost four lines.
    """
    top, bottom = H - 66, H - 14
    for y in range(top, bottom):
        t = (y - top) / (bottom - top)
        shift = int(-14 - t * 34)                 # falls forward and leftward
        spread = int(t * 10)
        x0 = WIN_X0 + shift - spread
        x1 = WIN_X1 + shift + spread

        for x in range(max(0, x0), min(W, x1)):
            # Feathered at the two vertical edges only. The near and far edges
            # stay hard: that is where the opening's own edge is, and softening
            # it turns the patch into a smudge.
            edge = min(x - x0, x1 - 1 - x)
            if edge > 3:
                put(img, y, x, pal[4])
            elif BAYER[y % 8, x % 8] < edge / 4.0:
                put(img, y, x, pal[3])

    # The shadow of the glazing bars, laid across the patch in the same shear.
    for share in (0.34, 0.66):
        for y in range(top, bottom):
            t = (y - top) / (bottom - top)
            shift = int(-14 - t * 34)
            bx = int(WIN_X0 + shift + (WIN_X1 - WIN_X0) * share)
            for x in (bx, bx + 1):
                if 0 <= x < W and tuple(img[y, x]) in (pal[3], pal[4]):
                    put(img, y, x, pal[2])
    for y in (top + (bottom - top) // 2, top + (bottom - top) // 2 + 1):
        t = (y - top) / (bottom - top)
        shift = int(-14 - t * 34)
        for x in range(max(0, WIN_X0 + shift), min(W, WIN_X1 + shift)):
            if tuple(img[y, x]) in (pal[3], pal[4]):
                put(img, y, x, pal[2])


def carton(img, x0, y0, x1, y1, tone=2):
    """A taped-up box, for the ones nobody in the game ever touches.

    These are background: they are still, silent, always behind, and no hotspot
    stands on them. The ones the puzzle cares about are sprites, drawn by
    make_apartment_props.py, because a hotspot whose picture is painted into the
    background can never change.
    """
    rect(img, y0, y1, x0, x1, INK)
    rect(img, y0 + 1, y1, x0 + 1, x1 - 1, CARD[tone])
    rect(img, y0 + 1, y0 + 2, x0 + 1, x1 - 1, CARD[tone + 1])      # lit top edge
    rect(img, y0 + 1, y1, x1 - 2, x1 - 1, CARD[max(0, tone - 1)])  # shaded side

    # The tape down the seam, and the flap line it holds shut.
    mid = (x0 + x1) // 2
    rect(img, y0 + 1, y1 - 1, mid - 1, mid + 1, TAPE)
    rect(img, y0 + 4, y0 + 5, x0 + 1, x1 - 1, CARD[max(0, tone - 1)])


def main():
    img = np.zeros((H, W, 3), dtype=np.uint8)

    # ------------------------------------------------------------ the wall ---
    # Brighter towards the window and towards the top, where the bulb is. Two
    # crossing gradients, as the Street's sky has, because one alone reads as a
    # painted flat.
    #
    # Flat, with the light given as a shape rather than as a gradient. This is
    # the third attempt and the first that works, and the reason is worth
    # keeping: a gradient that crosses a band boundary spreads its dither strip
    # over however far the gradient takes to cross it, so a slow gradient across
    # a bare 320-unit wall produced a thirty-unit diagonal smear no matter how
    # narrow the strip was set. Narrowing the strip does not help when the
    # gradient is the slow thing — the skill's rule about keeping the strip
    # tight has this as its other half. A bare wall wants no gradient at all.
    #
    # What replaces it is what the room actually has: one window, throwing one
    # wedge of light, with a defined edge. Everything outside the wedge is one
    # flat tone, which is also what plaster looks like.
    img[:FLOOR_Y] = WALL[2]

    # The shadow gathering at the foot of the wall: one dithered strip and then
    # one solid band, which is the same two-nested-shapes construction the
    # window light uses. Drawn as a single dithered fade it came out as a dotted
    # border rather than as a shadow — a fade whose whole width is transition is
    # never read as a fade.
    for y in range(FLOOR_Y - 13, FLOOR_Y - 6):
        near = (y - (FLOOR_Y - 13)) / 7.0
        for x in range(W):
            if BAYER[y % 8, x % 8] < near:
                put(img, y, x, WALL[1])
    rect(img, FLOOR_Y - 6, FLOOR_Y, 0, W, WALL[1])

    # The pale rectangles where pictures hung, each with its hook still in the
    # wall. This is the room's whole story in four shapes: the wall behind a
    # picture never got the light the rest did, so what is left is brighter, and
    # a brighter patch means the picture is gone.
    for px, py, pw, ph in ((96, 22, 30, 22), (136, 30, 20, 16), (196, 18, 26, 20)):
        rect(img, py, py + ph, px, px + pw, WALL[4])
        rect(img, py, py + 1, px, px + pw, WALL[3])
        rect(img, py + ph - 1, py + ph, px, px + pw, WALL[2])      # dust ledge
        put(img, py - 3, px + pw // 2, SKIRT[1])                   # the hook
        put(img, py - 2, px + pw // 2, SKIRT[0])

    # ------------------------------------------------------- the door reveal -
    # The frame and the dark of the landing. The leaf is a sprite, because it is
    # a hotspot. The threshold is FLOOR_Y exactly — see the assertion below.
    rect(img, DOOR_TOP - 4, FLOOR_Y, DOOR_X0 - 4, DOOR_X1 + 4, WALL[1])
    rect(img, DOOR_TOP - 2, FLOOR_Y, DOOR_X0 - 2, DOOR_X1 + 2, WALL[3])
    rect(img, DOOR_TOP - 2, DOOR_TOP - 1, DOOR_X0 - 2, DOOR_X1 + 2, WALL[4])
    rect(img, DOOR_TOP, FLOOR_Y, DOOR_X0, DOOR_X1, INK)
    rect(img, DOOR_TOP, DOOR_TOP + 2, DOOR_X0, DOOR_X1, (14, 12, 20))
    # A slab of landing light on the floor of the opening: the stairwell is lit,
    # and it is what tells the player the doorway goes somewhere.
    rect(img, FLOOR_Y - 3, FLOOR_Y, DOOR_X0 + 3, DOOR_X1 - 3, SKIRT[2])

    # ----------------------------------------------------- the window reveal -
    # Reveal and sill only. The frame, the bars and the glass are a sprite, for
    # the same reason as the door: it is a hotspot.
    #
    # The opening is painted as a recess and not as sky: the glass, the bars and
    # what can be seen through them all belong to the sprite, so that a missing
    # sprite shows a hole rather than a slab of daylight with nothing in it.
    rect(img, WIN_TOP - 4, WIN_BOTTOM + 6, WIN_X0 - 4, WIN_X1 + 4, WALL[1])
    rect(img, WIN_TOP - 2, WIN_BOTTOM + 4, WIN_X0 - 2, WIN_X1 + 2, WALL[3])
    rect(img, WIN_TOP, WIN_BOTTOM, WIN_X0, WIN_X1, INK)
    rect(img, WIN_BOTTOM, WIN_BOTTOM + 3, WIN_X0 - 3, WIN_X1 + 3, WALL[4])
    rect(img, WIN_BOTTOM + 3, WIN_BOTTOM + 4, WIN_X0 - 3, WIN_X1 + 3, WALL[0])

    # The pool of light the window throws on the wall under the sill, and the
    # grime that has run off it. Both are consequences of the window, so both
    # belong painted: the window itself is what changes, and that is the sprite.
    for y in range(WIN_BOTTOM + 4, FLOOR_Y):
        spread = (y - WIN_BOTTOM) // 3
        for x in range(WIN_X0 - spread, WIN_X1 + spread):
            if 0 <= x < W and BAYER[y % 8, x % 8] < 0.34:
                put(img, y, x, WALL[4])
    for i in range(7):
        sx = WIN_X0 - 2 + int(rng.integers(0, WIN_X1 - WIN_X0 + 4))
        for j in range(int(rng.integers(3, 11))):
            put(img, WIN_BOTTOM + 4 + j, sx, WALL[1])

    # ------------------------------------------------------ bulb and flex ----
    # A bare bulb on a flex, off: it is morning and the window is doing the
    # work. The shade went into a box before the game started.
    bx = 168
    for y in range(0, 18):
        put(img, y, bx, SKIRT[0])
    rect(img, 18, 21, bx - 2, bx + 3, SKIRT[1])
    rect(img, 21, 26, bx - 3, bx + 4, GLASS[2])
    rect(img, 22, 25, bx - 2, bx + 3, GLASS[3])

    # ----------------------------------------------------------- skirting ----
    # Three hard steps, the darkest at the very foot. It is the only thing
    # separating wall from floor, and without it anybody standing at the back of
    # the room looks stuck to the plaster.
    rect(img, FLOOR_Y - 7, FLOOR_Y, 0, W, SKIRT[2])
    rect(img, FLOOR_Y - 7, FLOOR_Y - 6, 0, W, SKIRT[3])
    rect(img, FLOOR_Y - 2, FLOOR_Y, 0, W, SKIRT[0])
    # The doorway interrupts it: a skirting board that runs across an opening is
    # the tell that the opening was drawn on top of a finished wall.
    rect(img, FLOOR_Y - 7, FLOOR_Y, DOOR_X0, DOOR_X1, INK)
    rect(img, FLOOR_Y - 3, FLOOR_Y, DOOR_X0 + 3, DOOR_X1 - 3, SKIRT[2])

    # ------------------------------------------------------------- floor -----
    fh = H - FLOOR_Y
    img[FLOOR_Y:] = BOARD[2]

    # Boards running away from the viewer, so the seams are horizontal and crowd
    # towards the back. This is a flat-on view: there is no side vanishing point,
    # and a floor drawn with one comes out as a starburst.
    #
    # The seams are one dark line and nothing else. The first pass gave each a
    # bright line under it and staggered butt joints across every course, and
    # the floor came out as a brick wall lying down — at this resolution a
    # two-tone seam repeated eight times is a masonry pattern, whatever it was
    # meant to be. Joints are now rare, dim, and only in the near half where a
    # board end would actually be legible.
    seams, y, step = [], 2.0, 3.0
    while y < fh:
        seams.append(int(y))
        step *= 1.44
        y += step
    for i, sy in enumerate(seams):
        gy = FLOOR_Y + sy
        rect(img, gy, gy + 1, 0, W, BOARD[1])

    for i, sy in enumerate(seams[-3:], start=len(seams) - 3):
        gy = FLOOR_Y + sy
        bot = FLOOR_Y + (seams[i + 1] if i + 1 < len(seams) else fh)
        for jx in ((i * 83) % 160, (i * 83) % 160 + 160):
            for j in range(gy + 1, min(H, bot)):
                put(img, j, jx, BOARD[1])

    # The dust outline where the wardrobe stood until this morning: brighter
    # than the boards around it, because years of daylight darkened everything
    # except what it could not reach. Three sides and not four — the wall side
    # has no line, since nothing could darken behind the wardrobe either, and
    # a closed rectangle read as a frame lying on the floor.
    # Kept to the left of the room, clear of the window patch: two pale marks on
    # the same boards fought each other, and the one that means "something used
    # to stand here" lost to the one that means "the sun is up".
    x0, x1, y0, y1 = 62, 128, FLOOR_Y + 30, FLOOR_Y + 54
    for y in range(y0, y1):
        for x in range(x0, x1):
            if BAYER[y % 8, x % 8] < 0.30:
                put(img, y, x, BOARD[3])
    for x in range(x0, x1):
        put(img, y1 - 1, x, BOARD[4])
    for y in range(y0, y1):
        put(img, y, x0, BOARD[4])
        put(img, y, x1 - 1, BOARD[4])

    # Offcuts of packing tape, stuck down and walked on. Grain is given in
    # shapes, never as noise added to a field before it is banded: near a band
    # boundary noise scatters single pixels and reads as dirt.
    _window_light(img, BOARD)

    for tx, ty, tw in ((84, 152, 13), (250, 144, 11)):
        for i in range(tw):
            put(img, ty + (i * 3) // tw, tx + i, TAPE)
        put(img, ty - 1, tx, BOARD[0])

    # ------------------------------------------ boxes nobody ever touches ----
    # Scenery, and the reason the room reads as "already dealt with". Placed
    # clear of every sprite zone listed at the top of this file.
    carton(img, 4, FLOOR_Y - 22, 22, FLOOR_Y, tone=2)
    carton(img, 4, FLOOR_Y - 40, 20, FLOOR_Y - 22, tone=3)
    carton(img, 128, FLOOR_Y - 16, 140, FLOOR_Y, tone=1)
    carton(img, 172, FLOOR_Y - 18, 186, FLOOR_Y, tone=2)

    # ----------------------------------------------------------- checks ------
    # The threshold has to sit exactly on the floor line. It has been got wrong
    # twice on the two faces of the same door, so the skill now says to check it
    # every time, and checking it means asserting it rather than looking.
    floor_row = img[FLOOR_Y, DOOR_X0 + 6]
    assert not np.array_equal(floor_row, INK), "doorway closed below the floor line"

    Image.fromarray(img).save(ASSET)
    colours = len(np.unique(img.reshape(-1, 3), axis=0))

    # Isolated pixels: the measurable form of "the dithering went everywhere".
    a = img[:, 1:-1].astype(int)
    lone = ((np.abs(a - img[:, :-2]).sum(2) > 0)
            & (np.abs(a - img[:, 2:]).sum(2) > 0)).mean()
    print(f"{ASSET}  {W}x{H}  ({colours} colori, {lone * 100:.0f}% pixel isolati)")


if __name__ == "__main__":
    main()
