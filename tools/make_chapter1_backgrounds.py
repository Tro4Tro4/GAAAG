"""Draws the five backgrounds chapter one was still missing.

One script for five rooms rather than five scripts, and that is the kit decision
from CLAUDE.md put into practice: the rooms of a chapter share a palette, a
light direction and a construction, so what differs between them is a couple of
dozen lines each and not a file each. The mechanics live in tools/pixelkit.py.

The five, and what each is for:

  Landing   the shared landing outside Lino's flat: Duilio's door, the bells,
            the meter cupboard. Same building as the Apartment, so the same
            violets, and the light comes from the stairwell window on the right.
  Cellar    under the same building. The lowest and coldest room in the chapter,
            lit by one bulkhead lamp, and full of boxes that are not Lino's.
  Archive   the office's understairs room, where three years of incoming post
            has piled up. The Lobby's palette, one degree dustier.
  Backyard  behind the office, where the pneumatic line runs outside on
            brackets. Outdoors, so the Street's sky and its low sun.
  Bar       the last room of the chapter, and the only warm one in it. That is
            deliberate: everything else in chapter one is a corridor with a rule
            in it, and the place where somebody says goodbye should not look
            like the place where somebody stamped a form.

Every room draws its walkable band starting a few units below the floor line,
and every doorway meets the floor exactly on it — pixelkit.doorway asserts that
rather than trusting anybody to remember.

Run from the project root:  python tools/make_chapter1_backgrounds.py
"""
import sys

sys.path.insert(0, "tools")

import numpy as np  # noqa: E402

from make_apartment_background import BOARD, CARD, SKIRT, TAPE, WALL  # noqa: E402
from make_lobby_pixel_background import FLOOR as LOBBY_FLOOR  # noqa: E402
from make_lobby_pixel_background import BRASS, DOOR, NEON  # noqa: E402
from make_lobby_pixel_background import SKIRT as L_SKIRT
from make_lobby_pixel_background import WALL as L_WALL
from make_street_background import SKY, STONE  # noqa: E402
from pixelkit import Canvas, doorway, floorboards, ramp, skirting  # noqa: E402

BG = "assets/backgrounds"
INK = (22, 18, 30)

# The chapter's two new ramps, and both are derived rather than invented: the
# cellar is the building's brick, which is the cardboard ramp cooled until it
# stops being paper; the bar is its wood, which is the floorboards warmed until
# they stop being a floor.
BRICK = ramp((38, 32, 40), (118, 96, 92))
# The lobby's floor, cooled. Straight out of the lobby it is a saturated green,
# which is right next to that room's neon and lurid next to the archive's dust:
# a palette is inherited between rooms, not copied.
L_FLOOR = ramp((30, 30, 38), (124, 122, 112))
BARWOOD = ramp((56, 36, 30), (170, 118, 74))
BARGLOW = ramp((104, 62, 34), (246, 206, 138))   # the one warm light in chapter one


# =========================================================== the landing =====
def landing():
    """Outside Lino's flat: three doors, the bells, and the meter cupboard."""
    W, H, FLOOR_Y = 320, 180, 106
    c = Canvas(W, H)

    c.rect(0, 0, W, FLOOR_Y, WALL[2])
    # Light from the stairwell window, high on the right. Flat wall plus one
    # shape, never a gradient across the room: on a bare wall a slow gradient
    # spreads its dither strip over tens of units and reads as dirt.
    c.wash(272, 62, 66, 58, WALL[3])
    c.wash(268, 46, 40, 34, WALL[4], strength=0.7)
    c.rect(250, 8, 300, 40, INK)
    c.rect(252, 10, 298, 38, SKY[3])
    c.rect(252, 24, 298, 38, SKY[1])
    for i in range(1, 3):                                  # glazing bars
        c.rect(252 + i * 15, 10, 253 + i * 15, 38, WALL[1])
    c.rect(248, 38, 302, 42, WALL[4])

    # Lino's door on the left, Duilio's on the right of centre. Deliberately
    # identical: they are the same builder's doors on the same landing, and the
    # difference is entirely in what is stuck to them.
    doorway(c, 26, 58, FLOOR_Y - 48, FLOOR_Y, WALL, INK)
    doorway(c, 150, 182, FLOOR_Y - 48, FLOOR_Y, WALL, INK)
    # And the cellar door, with a sign over it, because it is the one opening on
    # this landing that needs saying. The first version of the room had no such
    # door: the way down to the street was an invisible rectangle in the middle
    # of the floor and the only drawn stairwell led to the cellar, so a player
    # who went into the flat could not get back out to the street.
    doorway(c, 196, 228, FLOOR_Y - 48, FLOOR_Y, WALL, INK, sign=True)

    # The stairwell going down, on the far right.
    #
    # Three attempts. Plain bars in a black rectangle read as a grille; treads
    # alone read as a louvred vent. What makes a stairwell a stairwell is the
    # **handrail**, which is the one part of a staircase that is never anything
    # else — so it gets drawn, descending, with its newel post at the near end.
    c.rect(268, FLOOR_Y - 40, 318, FLOOR_Y, INK)
    c.rect(270, FLOOR_Y - 38, 316, FLOOR_Y - 1, SKIRT[0])
    for i in range(6):                                     # treads, going away
        y = FLOOR_Y - 34 + i * 5
        c.rect(274 + i * 4, y, 316, y + 4, SKIRT[1])
        c.rect(274 + i * 4, y, 316, y + 1, SKIRT[3])

    for i in range(24):                                    # the rail, descending
        x = 272 + i * 2
        y = FLOOR_Y - 40 + int(i * 1.5)
        c.rect(x, y, x + 2, y + 3, BRASS[2])
        c.rect(x, y, x + 2, y + 1, BRASS[3])
    for i, x in enumerate((274, 288, 302)):                # and its balusters
        top = FLOOR_Y - 39 + int((x - 272) / 2 * 1.5)
        c.rect(x, top, x + 2, top + 14 - i * 2, SKIRT[2])
    c.rect(270, FLOOR_Y - 44, 276, FLOOR_Y - 12, SKIRT[2])  # the newel post
    c.rect(270, FLOOR_Y - 44, 276, FLOOR_Y - 41, BRASS[2])
    c.rect(268, FLOOR_Y - 42, 318, FLOOR_Y - 40, WALL[0])

    # The meter cupboard, and the row of bells beside Lino's door.
    c.rect(96, FLOOR_Y - 62, 130, FLOOR_Y - 28, INK)
    c.rect(98, FLOOR_Y - 60, 128, FLOOR_Y - 30, SKIRT[2])
    c.rect(98, FLOOR_Y - 60, 128, FLOOR_Y - 58, SKIRT[3])
    c.rect(112, FLOOR_Y - 58, 114, FLOOR_Y - 32, SKIRT[0])   # the two doors
    c.rect(108, FLOOR_Y - 46, 111, FLOOR_Y - 43, BRASS[3])   # and their catch

    skirting(c, FLOOR_Y, SKIRT)
    c.rect(26, FLOOR_Y - 7, 58, FLOOR_Y, INK)
    c.rect(150, FLOOR_Y - 7, 182, FLOOR_Y, INK)
    c.rect(196, FLOOR_Y - 7, 228, FLOOR_Y, INK)
    c.rect(272, FLOOR_Y - 7, 316, FLOOR_Y, INK)

    c.rect(0, FLOOR_Y, W, H, BOARD[2])
    floorboards(c, FLOOR_Y, H, BOARD)
    # Worn tracks where forty years of feet went from the stairs to the doors.
    # A wash and not a wedge: wear has no edge, and drawn with one it came out
    # as two planks lying across the landing.
    # One long shallow band and not three round patches: drawn as circles the
    # wear read as three puddles somebody had left on the landing.
    c.wash(170, FLOOR_Y + 26, 190, 22, BOARD[3], strength=0.45)
    c.speckle(0, FLOOR_Y, W, FLOOR_Y + 4, BOARD[1], 0.22)

    c.report(f"{BG}/bg_landing.png")


# ============================================================ the cellar =====
def cellar():
    """Under the building: brick, one lamp, and other people's boxes."""
    W, H, FLOOR_Y = 320, 180, 100
    c = Canvas(W, H)

    # Brick with the tone varying brick by brick. The first pass laid a 28%
    # speckle over the whole wall and the room came out at 33% isolated pixels —
    # a third of every row disagreeing with both neighbours, which is the
    # measurable form of "the dithering went everywhere". Bricks are pattern,
    # so they are drawn as pattern.
    c.bricks(0, 0, W, FLOOR_Y, BRICK)

    # One bulkhead lamp in a cage, and the only pool of light in the room. The
    # far corners stay dark, which is what makes a cellar a cellar.
    lamp_x = 172
    c.rect(lamp_x - 10, 12, lamp_x + 10, 26, INK)
    c.rect(lamp_x - 8, 14, lamp_x + 8, 24, NEON[3])
    for i in range(-6, 8, 3):
        c.rect(lamp_x + i, 14, lamp_x + i + 1, 24, INK)
    c.wash(lamp_x, 44, 88, 58, BRICK[2], strength=0.7)
    c.wash(lamp_x, 30, 44, 26, BRICK[3], strength=0.7)

    doorway(c, 22, 54, FLOOR_Y - 44, FLOOR_Y, BRICK, INK)   # the way up

    # A vaulted alcove at the back, bricked round, where the building's meters
    # used to be before somebody moved them upstairs.
    c.rect(236, FLOOR_Y - 52, 292, FLOOR_Y - 8, BRICK[0])
    c.rect(240, FLOOR_Y - 48, 288, FLOOR_Y - 12, INK)
    for i in range(5):
        c.rect(238 + i, FLOOR_Y - 54 + i, 290 - i, FLOOR_Y - 53 + i, BRICK[2])
    # The old meter boards still screwed to the back of it, with their cables
    # cut off flush. A black alcove with nothing in it reads as a mistake.
    for bx in (248, 266):
        c.rect(bx, FLOOR_Y - 42, bx + 14, FLOOR_Y - 24, BRICK[0])
        c.rect(bx + 1, FLOOR_Y - 41, bx + 13, FLOOR_Y - 25, SKIRT[1])
        c.rect(bx + 3, FLOOR_Y - 38, bx + 11, FLOOR_Y - 34, SKIRT[0])
        c.rect(bx + 6, FLOOR_Y - 24, bx + 8, FLOOR_Y - 16, SKIRT[0])

    skirting(c, FLOOR_Y, BRICK, height=5)
    c.rect(22, FLOOR_Y - 5, 54, FLOOR_Y, INK)

    # A concrete floor, not boards: no seams crowding, just slabs and damp.
    c.rect(0, FLOOR_Y, W, H, STONE[1])
    c.band(0, FLOOR_Y, W, H, lambda x, y: 0.30 + y * 0.22
           + np.clip(1 - np.abs(x - lamp_x / W) * 2.2, 0, 1) * 0.30, STONE)
    for y in (FLOOR_Y + 12, FLOOR_Y + 30, FLOOR_Y + 54):
        c.rect(0, y, W, y + 1, STONE[0])
    c.speckle(0, FLOOR_Y, W, H, STONE[0], 0.08)
    c.wash(lamp_x, FLOOR_Y + 28, 92, 46, STONE[2], strength=0.55)

    c.report(f"{BG}/bg_cellar.png")


# =========================================================== the archive =====
def archive():
    """The office's understairs room: shelving, sacks, and a receipting desk."""
    W, H, FLOOR_Y = 320, 180, 104
    c = Canvas(W, H)

    c.rect(0, 0, W, FLOOR_Y, L_WALL[2])
    # The underside of the stairs, running down to the right: the shape that
    # says "understairs" without a caption having to.
    for x in range(W):
        top = int(6 + (x / W) * 54)
        c.rect(x, 0, x + 1, top, INK)
        c.rect(x, top, x + 1, top + 3, L_SKIRT[1])
        if x % 14 < 2:
            c.rect(x, max(0, top - 8), x + 1, top, L_SKIRT[0])

    c.wash(46, 70, 38, 48, L_WALL[3], strength=0.7)
    doorway(c, 30, 62, FLOOR_Y - 46, FLOOR_Y, L_WALL, INK)   # back to the lobby

    # Shelving along the back, deep and full. Drawn as bays rather than as one
    # long rack, because a single unbroken horizontal at this size reads as a
    # shelf-shaped wall.
    for bx in (120, 190, 260):
        c.rect(bx - 32, FLOOR_Y - 58, bx + 32, FLOOR_Y - 6, INK)
        c.rect(bx - 30, FLOOR_Y - 56, bx + 30, FLOOR_Y - 8, L_SKIRT[1])
        for i in range(3):
            y = FLOOR_Y - 52 + i * 16
            c.rect(bx - 30, y, bx + 30, y + 2, L_SKIRT[3])
            # Files leaning on each shelf. Varied in width and height by a fixed
            # pattern, never randomly: a random shelf looks like static.
            x = bx - 28
            for k in range(9):
                wdt = 3 + (k * 5 + i * 3 + bx) % 4
                hgt = 9 + (k * 7 + i) % 4
                tone = (LOBBY_FLOOR, CARD, L_SKIRT)[(k + i) % 3]
                c.rect(x, y - hgt + 2, x + wdt, y + 2, tone[2 + (k % 2)])
                c.rect(x, y - hgt + 2, x + 1, y + 2, tone[1])
                x += wdt + 1
                if x > bx + 27:
                    break

    skirting(c, FLOOR_Y, L_SKIRT, height=6)
    c.rect(30, FLOOR_Y - 6, 62, FLOOR_Y, INK)

    c.rect(0, FLOOR_Y, W, H, L_FLOOR[1])
    c.band(0, FLOOR_Y, W, H, lambda x, y: 0.34 + y * 0.16
           + np.clip(1 - np.abs(x - 0.15) * 2.6, 0, 1) * 0.22, L_FLOOR)
    floorboards(c, FLOOR_Y, H, L_FLOOR, spacing=3.4)
    c.speckle(0, FLOOR_Y, W, H, L_FLOOR[0], 0.06)

    c.report(f"{BG}/bg_archive.png")


# ========================================================== the backyard =====
def backyard():
    """Behind the office: the line runs outside, on brackets, in daylight."""
    W, H, FLOOR_Y = 320, 180, 108
    c = Canvas(W, H)

    SKY_Y = 44
    c.band(0, 0, W, SKY_Y, lambda x, y: 0.30 + (1 - x) * 0.30 + y * 0.30, SKY,
           width=0.5)
    # The backs of the buildings across the yard: flat, dark, two tones. It is
    # far away and it is not the subject.
    for x0, x1, top in ((0, 90, 18), (90, 176, 8), (176, 250, 22), (250, W, 12)):
        c.rect(x0, SKY_Y - 30 + top, x1, SKY_Y, STONE[1])
        c.rect(x0, SKY_Y - 30 + top, x1, SKY_Y - 29 + top, STONE[2])

    # The office's own back wall, and the yard gate in it.
    c.rect(0, SKY_Y, W, FLOOR_Y, L_WALL[2])
    c.speckle(0, SKY_Y, W, FLOOR_Y, L_WALL[1], 0.16)
    c.wash(298, FLOOR_Y - 34, 74, 50, L_WALL[3])
    doorway(c, 30, 62, FLOOR_Y - 44, FLOOR_Y, L_WALL, INK)   # back inside

    # The pneumatic line, outside on brackets, running the width of the yard.
    # This is the room's whole reason to exist, so it sits at hand height and
    # gets the most contrast in the picture.
    pipe_y = FLOOR_Y - 30
    c.rect(0, pipe_y, W, pipe_y + 11, INK)
    c.rect(0, pipe_y + 1, W, pipe_y + 10, BRASS[1])
    c.rect(0, pipe_y + 1, W, pipe_y + 4, BRASS[2])
    c.rect(0, pipe_y + 2, W, pipe_y + 3, BRASS[3])
    c.rect(0, pipe_y + 8, W, pipe_y + 10, BRASS[0])
    # Frost on the run upstream of the blockage. It belongs in the background as
    # much as on the sprite: cold air goes through this part of the line, so the
    # part of it the sprite does not cover has to be frosted too. Painting only
    # the sprite left the yard with a bare brass pipe that suddenly iced over
    # where the hotspot began — and it also left the sprite's near-white outside
    # the room's palette, which qa_check measured at 0.21 and was right about.
    # One fix for a wrong picture and a failed check at once.
    FROST = (214, 226, 234)
    FROST_L = (240, 248, 252)
    FROST_D = (168, 182, 196)
    c.rect(0, pipe_y, 132, pipe_y + 6, FROST)
    c.rect(0, pipe_y, 132, pipe_y + 2, FROST_L)
    c.rect(0, pipe_y + 6, 132, pipe_y + 8, FROST_D)

    for x in range(24, W, 56):                                # brackets
        c.rect(x - 3, pipe_y - 4, x + 4, pipe_y + 15, INK)
        c.rect(x - 2, pipe_y - 3, x + 3, pipe_y + 14, L_SKIRT[1])
        c.rect(x - 2, pipe_y - 3, x + 3, pipe_y - 2, L_SKIRT[3])

    skirting(c, FLOOR_Y, L_SKIRT, height=5)
    c.rect(30, FLOOR_Y - 5, 62, FLOOR_Y, INK)

    # Yard paving: slabs, wet in the shade, and the sun cutting across.
    c.rect(0, FLOOR_Y, W, H, STONE[1])
    c.band(0, FLOOR_Y, W, H, lambda x, y: 0.36 + x * 0.28 + y * 0.14, STONE)
    for i, y in enumerate((FLOOR_Y + 8, FLOOR_Y + 22, FLOOR_Y + 42, FLOOR_Y + 66)):
        c.rect(0, y, W, y + 1, STONE[0])
        for x in range((i * 37) % 90, W, 90):
            c.rect(x, y, x + 1, min(H, y + 20), STONE[0])
    # The sun coming over the roof opposite and landing on the paving. This one
    # keeps its edge: it is the shadow of a building, and a building has one.
    c.wedge(lambda t: 244 - t * 52, FLOOR_Y, H, lambda t: 38 + t * 26,
            STONE[3], STONE[2], feather=6)

    c.report(f"{BG}/bg_backyard.png")


# =============================================================== the bar =====
def bar():
    """The last room of the chapter, and the only warm one in it."""
    W, H, FLOOR_Y = 320, 180, 108
    c = Canvas(W, H)

    c.rect(0, 0, W, FLOOR_Y, BARWOOD[1])
    # Tongue-and-groove panelling to half height, plaster above: two materials,
    # which is the cheapest way to make a room look like somewhere people go
    # rather than somewhere people queue.
    c.rect(0, 0, W, 44, WALL[1])
    c.speckle(0, 0, W, 44, WALL[2], 0.10)
    c.rect(0, 44, W, 48, BARWOOD[3])
    for x in range(0, W, 9):
        c.rect(x, 48, x + 1, FLOOR_Y, BARWOOD[0])
        c.rect(x + 1, 48, x + 2, FLOOR_Y, BARWOOD[2])

    # Two hanging lamps with real pools of light on the wall behind them. This
    # is the only room in the chapter lit by something somebody chose.
    for lx in (86, 232):
        c.rect(lx - 1, 0, lx + 1, 16, INK)
        c.rect(lx - 9, 16, lx + 9, 20, INK)
        c.rect(lx - 8, 17, lx + 8, 20, BARGLOW[3])
        c.rect(lx - 5, 19, lx + 5, 22, BARGLOW[4])
        c.wash(lx, 40, 54, 40, BARGLOW[1])
        c.wash(lx, 28, 26, 20, BARGLOW[2], strength=0.7)

    doorway(c, 20, 52, FLOOR_Y - 48, FLOOR_Y, BARWOOD, INK)   # out to the alley

    # The back bar: shelves of bottles behind, and the mirror strip that every
    # bar of this kind has. Kept above the counter, which is a sprite.
    c.rect(120, 26, 296, 74, INK)
    c.rect(122, 28, 294, 72, BARWOOD[0])
    for i in range(2):
        y = 40 + i * 20
        c.rect(122, y, 294, y + 2, BARWOOD[2])
        for k in range(22):
            bx = 126 + k * 7
            if bx > 288:
                break
            hgt = 10 + (k * 5) % 6
            tone = (BARGLOW, NEON, DOOR)[(k + i) % 3]
            c.rect(bx, y - hgt, bx + 4, y, tone[1 + (k % 3)])
            c.rect(bx, y - hgt, bx + 1, y, tone[3])
    c.rect(124, 30, 292, 38, DOOR[1])                        # the mirror strip
    c.speckle(124, 30, 292, 38, DOOR[2], 0.18)

    skirting(c, FLOOR_Y, BARWOOD, height=6)
    c.rect(20, FLOOR_Y - 6, 52, FLOOR_Y, INK)

    # A tiled floor, because the one place in the chapter that gets mopped is
    # the one place that sells drinks.
    c.rect(0, FLOOR_Y, W, H, STONE[1])
    c.band(0, FLOOR_Y, W, H, lambda x, y: 0.32 + y * 0.20
           + np.clip(1 - np.abs(x - 0.28) * 2.0, 0, 1) * 0.16, STONE)
    rows, y, step = [], 3.0, 5.0
    while y < H - FLOOR_Y:
        rows.append(int(y))
        step *= 1.34
        y += step
    for i, sy in enumerate(rows):
        gy = FLOOR_Y + sy
        c.rect(0, gy, W, gy + 1, STONE[0])
        pitch = 16 + i * 7
        for x in range((i * 9) % pitch, W, pitch):
            bot = FLOOR_Y + (rows[i + 1] if i + 1 < len(rows) else H - FLOOR_Y)
            c.rect(x, gy, x + 1, min(H, bot), STONE[0])

    c.report(f"{BG}/bg_bar.png")


if __name__ == "__main__":
    landing()
    cellar()
    archive()
    backyard()
    bar()
