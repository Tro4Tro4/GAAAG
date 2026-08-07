"""Draws the sprites for chapter one's five new rooms.

One script for five rooms, like their backgrounds, and for the same reason: they
share a kit. Each sprite is drawn at 1:1 for use at scale = 1 with the project's
Nearest filter, with its origin where the object meets the ground, because
Y-sorting looks at a node's Y and not at the extent of what it draws.

Palettes are imported from the backgrounds, never retyped. That is the project's
rule made mechanical — a sprite's colours are derived from its room's, and if
the room is regenerated the sprites move with it.

Duilio is drawn once and used twice, on the landing and in the bar. He is the
same man in both places and the player has to recognise him; two drawings would
be two chances to draw him differently.

Run from the project root:  python tools/make_chapter1_props.py
"""
import sys

sys.path.insert(0, "tools")
sys.path.insert(0, ".claude/skills/pixel-adventure-assets/scripts")

from make_apartment_background import BOARD, CARD, SKIRT, TAPE, WALL  # noqa: E402
from make_chapter1_backgrounds import BARGLOW, BARWOOD, BRICK, L_FLOOR  # noqa: E402
from make_lobby_pixel_background import BRASS, DOOR, NEON  # noqa: E402
from make_lobby_pixel_background import SKIRT as L_SKIRT
from make_lobby_pixel_background import WALL as L_WALL
from make_street_background import GLASS, STONE  # noqa: E402
from pixelkit import Canvas  # noqa: E402

SPRITES = "assets/sprites"
INK = (22, 18, 30)
PAPER = (206, 198, 180)
PAPER_D = (162, 154, 138)
SKIN = (196, 152, 120)
SKIN_D = (150, 112, 86)


def sprite(w, h):
    return Canvas(w, h, alpha=True)


def done(c, name):
    c.outline(INK)
    c.save(f"{SPRITES}/{name}.png")


# ============================================================== people =======
def duilio():
    """Lino's neighbour: forty units, standing, and conspicuously relaxed.

    Everybody else in chapter one is holding a document. He is holding a cup,
    which is the entire characterisation: the man being evicted tomorrow is the
    only one in the building who is not worried, because he already has
    somewhere to go.

    Nothing asymmetric on him — the game mirrors a side view to make the other
    side, so a bag on one shoulder would break the trick the day he ever walks.
    """
    c = sprite(24, 41)
    mid = 12
    CARDI = BARWOOD                     # a cardigan the colour of the bar
    TROUSER = SKIRT

    for x0 in (mid - 5, mid + 1):                       # legs and slippers
        c.rect(x0, 26, x0 + 4, 38, TROUSER[1])
        c.rect(x0, 26, x0 + 1, 38, TROUSER[0])
        c.rect(x0 - 1, 38, x0 + 4, 41, TROUSER[0])

    c.rect(mid - 7, 13, mid + 7, 29, CARDI[1])          # the cardigan
    c.rect(mid + 4, 13, mid + 7, 29, CARDI[2])
    c.rect(mid - 7, 13, mid - 5, 29, CARDI[0])
    c.rect(mid - 1, 14, mid + 1, 29, CARDI[0])          # its opening
    c.rect(mid - 4, 13, mid + 4, 19, PAPER_D)           # a collarless shirt

    for x0 in (mid - 10, mid + 7):                      # arms, bent forward
        c.rect(x0, 15, x0 + 3, 24, CARDI[1])
    c.rect(mid - 9, 24, mid - 6, 27, SKIN_D)
    c.rect(mid + 6, 24, mid + 9, 27, SKIN)

    # The cup, held in both hands at chest height. It is the lightest thing on
    # him and it is where the eye lands.
    c.rect(mid - 5, 21, mid + 5, 26, PAPER)
    c.rect(mid - 5, 21, mid + 5, 22, (232, 226, 210))
    c.rect(mid + 5, 22, mid + 7, 25, PAPER_D)           # the handle

    c.rect(mid - 5, 2, mid + 5, 13, SKIN)               # head
    c.rect(mid - 5, 2, mid - 3, 13, SKIN_D)
    c.rect(mid - 5, 0, mid + 5, 4, (86, 82, 92))        # grey hair, receding
    c.rect(mid - 3, 0, mid + 2, 2, SKIN)
    c.put(mid - 2, 7, INK)
    c.put(mid + 2, 7, INK)
    c.rect(mid - 1, 10, mid + 2, 11, SKIN_D)
    done(c, "prop_duilio")


# ============================================================= landing =======
def landing_doors():
    """Two identical doors, told apart entirely by what is stuck to them."""
    for name, notice in (("prop_door_lino", True), ("prop_door_duilio", False)):
        c = sprite(32, 48)
        c.rect(0, 0, 32, 48, SKIRT[2])
        c.rect(0, 0, 32, 2, SKIRT[3])
        c.rect(30, 0, 32, 48, SKIRT[1])
        for y0, y1 in ((5, 21), (25, 43)):              # two sunk panels
            c.rect(4, y0, 28, y1, SKIRT[1])
            c.rect(5, y0 + 1, 27, y1 - 1, SKIRT[2])
            c.rect(5, y0 + 1, 27, y0 + 2, SKIRT[3])
        c.rect(3, 23, 8, 26, BRASS[3])                  # handle and number
        c.rect(13, 2, 19, 4, BRASS[2])
        if notice:
            # The same withdrawal notice as the one on the street door, printed
            # smaller and stuck on with the same tape. Two copies of one form is
            # how an office says it means it.
            c.rect(9, 9, 23, 19, PAPER)
            c.rect(9, 9, 23, 11, PAPER_D)
            for i in range(3):
                c.rect(11, 13 + i * 2, 21 - i * 2, 14 + i * 2, (120, 116, 128))
            c.rect(8, 8, 12, 10, TAPE)
            c.rect(20, 18, 24, 20, TAPE)
        else:
            # A doormat that says nothing, and a cardboard sign: GONE. Duilio is
            # the only person in the building who has finished packing.
            c.rect(10, 24, 22, 32, CARD[2])
            c.rect(10, 24, 22, 25, CARD[3])
            c.rect(12, 27, 20, 29, CARD[0])
        done(c, name)


def bells():
    """The entryphone panel: one button per flat, and most of them blank."""
    c = sprite(18, 30)
    c.rect(0, 0, 18, 30, L_SKIRT[1])
    c.rect(0, 0, 18, 2, L_SKIRT[3])
    c.rect(16, 0, 18, 30, L_SKIRT[0])
    for i in range(6):
        y = 3 + i * 4
        c.rect(3, y, 9, y + 3, PAPER if i in (1, 3) else L_SKIRT[2])
        if i in (1, 3):
            c.rect(4, y + 1, 8, y + 2, (120, 116, 128))
        c.rect(11, y, 14, y + 3, BRASS[2])
        c.rect(11, y, 14, y + 1, BRASS[3])
    done(c, "prop_bells")


# ============================================================== cellar =======
def cellar_boxes():
    """Other people's boxes, catalogued and stacked to the ceiling.

    Same cardboard as the flat, one step darker: down here nothing has been
    lit properly in years. Tags on every one, because down here the rule the
    chapter runs on is at its most literal.
    """
    c = sprite(72, 54)
    for x0, y0, x1, y1, tone in ((0, 22, 30, 54, 1), (30, 14, 66, 54, 2),
                                 (4, 0, 34, 22, 2), (34, 0, 62, 14, 1)):
        c.rect(x0, y0, x1, y1, CARD[tone])
        c.rect(x0, y0, x1, y0 + 1, CARD[tone + 1])
        c.rect(x1 - 2, y0, x1, y1, CARD[tone - 1])
        mid = (x0 + x1) // 2
        c.rect(mid - 1, y0, mid + 1, y1, TAPE)
        c.rect(x0, y0 + 5, x1, y0 + 6, CARD[tone - 1])
        c.rect(x0 + 3, y0 + 9, x0 + 11, y0 + 15, PAPER)     # the catalogue tag
        c.rect(x0 + 4, y0 + 11, x0 + 10, y0 + 12, (120, 116, 128))
    done(c, "prop_cellar_boxes")


def manifest():
    """The removers' master list, pinned up where they actually work.

    Deliberately the largest sheet of paper in the game so far: everything else
    is a form about one thing, and this is a list of everything.

    Its paper is greyer than every other sheet in the chapter, and that is not a
    style choice: the cellar has no warm pale anywhere in it, and the shared
    cream measured 0.17 against the room. Paper under a bare bulb in a brick
    cellar *is* grey, so the tool and the fiction wanted the same thing.
    """
    c = sprite(40, 52)
    COLD = (198, 196, 194)
    COLD_L = (226, 224, 222)
    COLD_D = (156, 152, 156)
    c.rect(0, 0, 40, 52, COLD)
    c.rect(0, 0, 40, 2, COLD_L)
    c.rect(0, 50, 40, 52, COLD_D)
    c.rect(3, 4, 37, 9, (120, 116, 128))                    # the heading block
    for i in range(11):                                     # line after line
        y = 13 + i * 3
        c.rect(3, y, 24 - (i % 4) * 3, y + 1, (120, 116, 128))
        c.rect(28, y, 37, y + 1, (150, 146, 158))
    c.rect(3, 46, 20, 48, (90, 86, 100))                    # and a total
    # Steel pins and not brass: brass is an office material and there is none of
    # it in a brick cellar, which qa_check said in the only way it can — by
    # measuring the tone as foreign.
    for x, y in ((1, 1), (37, 1), (1, 49), (37, 49)):       # drawing pins
        c.rect(x, y, x + 2, y + 2, STONE[4])
        c.put(x, y, STONE[2])
    done(c, "prop_manifest")


# ============================================================= archive =======
def office_door():
    """A plain internal door of the office, standing open. Used twice."""
    c = sprite(32, 46)
    c.rect(0, 0, 32, 46, L_SKIRT[2])
    c.rect(0, 0, 32, 2, L_SKIRT[3])
    c.rect(30, 0, 32, 46, L_SKIRT[1])
    c.rect(4, 5, 28, 41, L_SKIRT[1])
    c.rect(5, 6, 27, 40, L_SKIRT[2])
    c.rect(5, 6, 27, 7, L_SKIRT[3])
    c.rect(3, 22, 8, 25, DOOR[3])
    done(c, "prop_office_door")


def archive_sacks():
    """Three years of incoming post, in the sacks it arrived in.

    Sacks and not boxes: a box is something somebody packed, a sack is something
    nobody has opened. The difference is the whole point of the room.
    """
    c = sprite(64, 34)
    for x0, w, h, tone in ((0, 26, 28, 1), (22, 28, 34, 2), (46, 18, 24, 1)):
        top = 34 - h
        for y in range(top, 34):
            t = (y - top) / float(h)
            # Wider towards the bottom, so it slumps instead of standing.
            bulge = int(round((w / 2.0) * (0.55 + 0.45 * t)))
            cx = x0 + w // 2
            c.rect(cx - bulge, y, cx + bulge, y + 1, CARD[tone])
            c.put(cx - bulge, y, CARD[tone - 1] if tone else CARD[0])
            c.rect(cx + bulge - 2, y, cx + bulge, y + 1, CARD[max(0, tone - 1)])
        cx = x0 + w // 2
        c.rect(cx - 5, top, cx + 5, top + 3, CARD[tone + 1])      # the neck
        c.rect(cx - 6, top + 2, cx + 6, top + 4, L_SKIRT[1])      # and its tie
        c.rect(cx - 4, top + 8, cx + 4, top + 13, PAPER)          # a docket
        c.rect(cx - 3, top + 10, cx + 3, top + 11, (120, 116, 128))
    done(c, "prop_archive_sacks")


def archive_desk():
    """The receipting desk: a stamp, a pad, and a pen on a chain."""
    c = sprite(56, 30)
    c.rect(0, 6, 56, 12, L_FLOOR[2])                     # the top
    c.rect(0, 6, 56, 7, L_FLOOR[3])
    c.rect(0, 11, 56, 13, L_FLOOR[0])
    c.rect(2, 13, 12, 30, L_FLOOR[1])                    # legs and a pedestal
    c.rect(44, 13, 54, 30, L_FLOOR[1])
    c.rect(44, 15, 54, 20, L_FLOOR[2])
    c.rect(45, 16, 53, 17, L_FLOOR[0])
    c.rect(16, 0, 26, 6, L_SKIRT[1])                     # the stamp, on its end
    c.rect(17, 0, 25, 2, L_SKIRT[3])
    c.rect(19, 2, 23, 6, BRASS[2])
    c.rect(30, 2, 44, 6, PAPER)                          # the receipt pad
    c.rect(30, 2, 44, 3, (232, 226, 210))
    c.rect(32, 4, 40, 5, (120, 116, 128))
    c.rect(46, 3, 48, 6, DOOR[3])                        # the pen on its chain
    for i in range(4):
        c.put(48 + (i % 2), 5 + i, DOOR[1])
    done(c, "prop_archive_desk")


def archive_tray():
    """The outgoing tray: three years of certificates that never went."""
    c = sprite(34, 22)
    c.rect(0, 14, 34, 22, L_SKIRT[1])                    # the wire basket
    c.rect(0, 14, 34, 15, L_SKIRT[3])
    for x in range(2, 33, 4):
        c.rect(x, 15, x + 1, 21, L_SKIRT[0])
    # The stack in it, leaning, each sheet a hair out of true. A neat pile would
    # read as one solid block; the offsets are what make it read as paper.
    for i in range(7):
        y = 12 - i * 2
        off = (i * 3) % 5
        c.rect(3 + off, y, 30 + off - 4, y + 2, PAPER if i % 2 else PAPER_D)
        c.rect(3 + off, y, 30 + off - 4, y + 1, (232, 226, 210))
    done(c, "prop_archive_tray")


# ============================================================ backyard =======
def flange_panel():
    """The junction of section 4: numbered flanges, and the frost line.

    The one thing in the yard the puzzle needs, so it gets the strongest
    contrast in the room and sits at hand height. The frost stops part way
    along, which is what says where the blockage is without a word of text —
    air flows up to it and not past it.
    """
    c = sprite(96, 26)
    c.rect(0, 8, 96, 19, BRASS[1])                       # the run itself
    c.rect(0, 8, 96, 11, BRASS[2])
    c.rect(0, 9, 96, 10, BRASS[3])
    c.rect(0, 17, 96, 19, BRASS[0])

    for i in range(5):
        x = 8 + i * 20
        c.rect(x, 5, x + 6, 22, BRASS[0])                # a flange
        c.rect(x + 1, 6, x + 5, 21, BRASS[2])
        c.rect(x + 1, 6, x + 5, 7, BRASS[3])
        c.rect(x - 3, 0, x + 9, 5, L_SKIRT[1])           # its number plate
        c.rect(x - 2, 1, x + 8, 4, PAPER)
        c.rect(x, 2, x + 4 - (i % 2), 3, (90, 86, 100))
        # Frost, and it stops after the third flange. Drawn as a hard-edged
        # crust and not a fade: it is information, and information gets an edge.
        if i < 3:
            # Thick enough to be the first thing seen. A first pass drew it as a
            # two-pixel sheen and it was invisible at game size — which for the
            # one object a puzzle depends on is the same as not drawing it.
            c.rect(x + 6, 8, min(96, x + 21), 14, (214, 226, 234))
            c.rect(x + 6, 8, min(96, x + 21), 10, (240, 248, 252))
            c.rect(x + 6, 14, min(96, x + 21), 16, (168, 182, 196))
    # And the frost line itself, marked where it stops: the answer to "where"
    # is a place on this pipe, so the place gets an edge.
    c.rect(68, 6, 70, 21, (240, 248, 252))
    done(c, "prop_flanges")


def yard_gate():
    """The gate out of the yard, chained. It goes nowhere and says so."""
    c = sprite(34, 52)
    c.rect(0, 0, 34, 52, L_SKIRT[0])
    c.rect(2, 2, 32, 50, STONE[1])
    for x in range(4, 31, 6):
        c.rect(x, 2, x + 3, 50, STONE[2])
        c.rect(x, 2, x + 1, 50, STONE[0])
    c.rect(0, 22, 34, 26, L_SKIRT[1])                    # the rail
    c.rect(0, 22, 34, 23, L_SKIRT[3])
    for i in range(5):                                   # the chain and padlock
        c.rect(12 + (i % 2) * 2, 26 + i * 3, 16 + (i % 2) * 2, 29 + i * 3,
               L_SKIRT[2])
    c.rect(11, 40, 19, 47, L_SKIRT[3])
    c.rect(13, 42, 17, 45, L_SKIRT[0])
    done(c, "prop_yard_gate")


# ================================================================= bar =======
def bar_counter():
    """The counter: the only thing in the chapter you can lean on.

    Twenty-six units and not forty. Drawn a person's height it read as a wall
    with bottles behind it, and worse, its top surface came out a foot above
    where a standing figure's hands are — the measure this project checks every
    reachable object against.
    """
    c = sprite(120, 26)
    c.rect(0, 0, 120, 5, BARWOOD[3])                     # the top, lit
    c.rect(0, 3, 120, 5, BARWOOD[4])
    c.rect(0, 5, 120, 26, BARWOOD[1])
    c.rect(0, 5, 120, 7, BARWOOD[2])
    for x in range(0, 120, 10):                          # panelled front
        c.rect(x, 8, x + 1, 24, BARWOOD[0])
        c.rect(x + 1, 8, x + 2, 24, BARWOOD[2])
    c.rect(0, 23, 120, 26, BARWOOD[0])                   # the foot rail shadow
    c.rect(6, 19, 114, 21, BRASS[1])
    c.rect(6, 19, 114, 20, BRASS[3])
    # A cloth left on it, and two rings where glasses stood.
    c.rect(84, 0, 104, 4, (168, 178, 172))
    c.rect(86, 0, 102, 1, (196, 204, 198))
    for rx in (22, 44):
        c.rect(rx, 1, rx + 8, 2, BARWOOD[4])
    done(c, "prop_bar_counter")


def bar_clock():
    """The clock the last puzzle of the chapter turns on.

    Deliberately legible: it is the only dial in the game whose reading matters,
    so the hands are drawn thick and the twelve is marked. Set at a few minutes
    past midnight, which is the whole problem.
    """
    c = sprite(26, 26)
    for y in range(26):                                  # a round case
        half = int(round(12.5 * (1 - ((y - 12.5) / 12.5) ** 2) ** 0.5))
        c.rect(13 - half, y, 13 + half, y + 1, L_SKIRT[1])
        c.rect(13 - half, y, 13 - half + 2, y + 1, L_SKIRT[2])
    for y in range(3, 23):
        half = int(round(9.5 * (1 - ((y - 13) / 10.0) ** 2) ** 0.5))
        c.rect(13 - half, y, 13 + half, y + 1, PAPER)
    c.rect(12, 4, 14, 6, INK)                            # the twelve
    for x, y in ((20, 12), (12, 20), (5, 12)):
        c.rect(x, y, x + 2, y + 2, (120, 116, 128))
    # Both hands near the top, a few minutes apart: it is just after midnight,
    # which is the whole problem. Drawn thick, because this is the only dial in
    # the game whose reading the player has to act on.
    c.rect(12, 6, 14, 14, INK)                           # the hour hand, at 12
    for i in range(6):                                   # the minute hand, past
        c.rect(13 + i, 12 - (5 - i), 15 + i, 14 - (5 - i), INK)
    c.rect(11, 11, 15, 15, BRASS[2])
    c.rect(12, 12, 14, 14, BRASS[3])
    done(c, "prop_bar_clock")


def bar_papers():
    """Duilio's departure papers, spread on the counter and waiting a name."""
    c = sprite(30, 16)
    for i, (dx, dy) in enumerate(((0, 4), (5, 2), (11, 0))):
        c.rect(dx, dy, dx + 18, dy + 12, PAPER if i else PAPER_D)
        c.rect(dx, dy, dx + 18, dy + 1, (232, 226, 210))
        for k in range(3):
            c.rect(dx + 2, dy + 3 + k * 2, dx + 14 - k * 3, dy + 4 + k * 2,
                   (120, 116, 128))
    c.rect(14, 10, 26, 12, (90, 86, 100))                # the line to sign on
    c.rect(26, 6, 28, 12, DOOR[3])                       # and the pen
    done(c, "prop_bar_papers")


if __name__ == "__main__":
    duilio()
    landing_doors()
    bells()
    cellar_boxes()
    manifest()
    office_door()
    archive_sacks()
    archive_desk()
    archive_tray()
    flange_panel()
    yard_gate()
    bar_counter()
    bar_clock()
    bar_papers()
