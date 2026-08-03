"""Draws the playable characters and writes their SpriteFrames resources.

One sheet per character: rows are animations, columns are frames, every cell the
same size, which is what Godot's AnimatedSprite2D wants. Three drawn directions —
down, side, up — and the left is the side flipped horizontally at runtime, so a
character costs three drawings and not four.

Everything here is measured in game units, because in this project one texture
pixel is one game unit: a character is 40 px tall and goes into the scene at
scale 1. The cell is taller and wider than the body to leave room for the walk
bob and for the cap brim on the side view.

The light comes from above and slightly left, the same direction as the Lobby's
ceiling fluorescent — a character lit from elsewhere than its room reads as a
sticker. Shadows shift towards violet and highlights towards yellow rather than
being the same colour darkened, which is what stops a flat-shaded sprite from
looking grey.

Run from the project root:  python tools/make_character_sheets.py
"""
import sys

sys.path.insert(0, ".claude/skills/pixel-adventure-assets/scripts")
from pixel_helpers import PixelCanvas
from PIL import Image

SPRITES = "assets/sprites"
RESOURCES = "resources/characters"

CELL_W, CELL_H = 24, 44
BODY_H = 40
TOP = CELL_H - BODY_H            # the body sits on the bottom row of the cell
CX = 12                          # the cell's centre column

OUT = (38, 30, 46, 255)          # never pure black: a very dark violet reads warmer

# Animations, in the order the rows are written. "side" is drawn facing right.
ANIMATIONS = [
    ("idle_down", 1, 5.0), ("idle_side", 1, 5.0), ("idle_up", 1, 5.0),
    ("walk_down", 4, 9.0), ("walk_side", 4, 9.0), ("walk_up", 4, 9.0),
    ("talk_down", 2, 6.0), ("talk_side", 2, 6.0), ("talk_up", 2, 6.0),
]


def rgba(c):
    return (c[0], c[1], c[2], 255)


LINO = {
    "id": "lino",
    "cap": True,
    "skin": (238, 196, 158), "skin_l": (250, 222, 186), "skin_d": (198, 148, 126),
    "hair": (228, 188, 98), "hair_l": (247, 218, 136), "hair_d": (174, 130, 62),
    "cap_c": (188, 84, 62), "cap_l": (216, 118, 86), "cap_d": (134, 54, 54),
    "coat": (108, 118, 86), "coat_l": (138, 150, 110), "coat_d": (72, 82, 68),
    "shirt": (222, 214, 186), "shirt_d": (176, 168, 152),
    "pants": (66, 66, 98), "pants_l": (90, 90, 124), "pants_d": (46, 44, 72),
    "shoe": (74, 54, 46), "shoe_l": (102, 78, 62),
    "eye": (132, 190, 216),
}

# A first pass only: Cesare has not been described yet, and he is here so that
# the two characters stop being one sprite and one polygon. Recolouring him is
# this dictionary and nothing else.
CESARE = dict(LINO, id="cesare", cap=False,
              skin=(226, 176, 142), skin_l=(242, 202, 170), skin_d=(184, 130, 110),
              hair=(78, 62, 58), hair_l=(108, 88, 80), hair_d=(52, 40, 42),
              coat=(70, 104, 138), coat_l=(98, 136, 172), coat_d=(48, 72, 102),
              shirt=(206, 206, 198), shirt_d=(162, 162, 158),
              pants=(70, 68, 74), pants_l=(94, 92, 98), pants_d=(48, 46, 52),
              eye=(96, 84, 72))


def cell() -> PixelCanvas:
    return PixelCanvas(CELL_W, CELL_H)


def head_down(c, p, y, mouth):
    """The face, seen from the front. y is the row the head starts on."""
    if p["cap"]:
        c.rect(CX - 3, y, CX + 3, y, rgba(p["cap_c"]))
        c.rect(CX - 4, y + 1, CX + 4, y + 3, rgba(p["cap_c"]))
        c.rect(CX - 4, y + 1, CX - 1, y + 2, rgba(p["cap_l"]))       # lit top left
        c.rect(CX - 5, y + 4, CX + 5, y + 4, rgba(p["cap_d"]))       # the brim
        hair_y = y + 5
    else:
        c.rect(CX - 4, y, CX + 4, y + 2, rgba(p["hair"]))
        c.rect(CX - 4, y, CX - 1, y + 1, rgba(p["hair_l"]))
        hair_y = y + 3

    c.rect(CX - 4, hair_y, CX + 4, hair_y, rgba(p["hair"]))          # fringe
    c.rect(CX - 5, hair_y, CX - 5, hair_y + 2, rgba(p["hair_d"]))    # sideburns
    c.rect(CX + 5, hair_y, CX + 5, hair_y + 2, rgba(p["hair_d"]))

    face = hair_y + 1
    c.rect(CX - 4, face, CX + 4, face + 4, rgba(p["skin"]))
    c.rect(CX - 4, face, CX - 2, face + 3, rgba(p["skin_l"]))        # lit cheek
    c.rect(CX + 3, face, CX + 4, face + 4, rgba(p["skin_d"]))        # shaded cheek

    c.set(CX - 2, face + 1, rgba(p["eye"]))                          # eyes
    c.set(CX - 3, face + 1, OUT)
    c.set(CX + 2, face + 1, rgba(p["eye"]))
    c.set(CX + 3, face + 1, OUT)
    c.set(CX, face + 2, rgba(p["skin_d"]))                           # nose
    if mouth:
        c.rect(CX - 1, face + 4, CX + 1, face + 4, OUT)              # open
    else:
        c.rect(CX - 1, face + 4, CX + 1, face + 4, rgba(p["skin_d"]))
    c.rect(CX - 3, face + 5, CX + 3, face + 5, rgba(p["skin_d"]))    # jaw
    c.rect(CX - 1, face + 6, CX + 1, face + 6, rgba(p["skin_d"]))    # neck
    return face + 7


def head_side(c, p, y, mouth):
    """The face in profile, turned right: the nose is the whole point."""
    if p["cap"]:
        c.rect(CX - 4, y, CX + 2, y, rgba(p["cap_c"]))
        c.rect(CX - 5, y + 1, CX + 3, y + 3, rgba(p["cap_c"]))
        c.rect(CX - 5, y + 1, CX - 1, y + 2, rgba(p["cap_l"]))
        c.rect(CX + 1, y + 4, CX + 7, y + 4, rgba(p["cap_d"]))       # brim, forward
        hair_y = y + 5
    else:
        c.rect(CX - 5, y, CX + 3, y + 2, rgba(p["hair"]))
        c.rect(CX - 5, y, CX - 1, y + 1, rgba(p["hair_l"]))
        hair_y = y + 3

    c.rect(CX - 5, hair_y, CX - 3, hair_y + 3, rgba(p["hair"]))      # back of the head
    c.rect(CX - 5, hair_y + 2, CX - 4, hair_y + 3, rgba(p["hair_d"]))

    face = hair_y + 1
    c.rect(CX - 2, face - 1, CX + 3, face + 4, rgba(p["skin"]))
    c.rect(CX - 2, face - 1, CX + 1, face, rgba(p["skin_l"]))
    c.set(CX + 2, face + 1, rgba(p["eye"]))
    c.set(CX + 3, face + 1, OUT)
    c.rect(CX + 4, face + 2, CX + 4, face + 2, rgba(p["skin"]))      # the nose
    c.set(CX + 4, face + 3, rgba(p["skin_d"]))
    if mouth:
        c.rect(CX + 2, face + 4, CX + 3, face + 4, OUT)
    else:
        c.set(CX + 3, face + 4, rgba(p["skin_d"]))
    c.rect(CX - 1, face + 5, CX + 2, face + 5, rgba(p["skin_d"]))    # jaw
    c.rect(CX - 1, face + 6, CX + 1, face + 6, rgba(p["skin_d"]))    # neck
    return face + 7


def head_up(c, p, y):
    """The back of the head. No face at all, which is how you tell somebody
    walking away from somebody walking towards you."""
    if p["cap"]:
        c.rect(CX - 3, y, CX + 3, y, rgba(p["cap_c"]))
        c.rect(CX - 4, y + 1, CX + 4, y + 4, rgba(p["cap_c"]))
        c.rect(CX - 4, y + 1, CX - 1, y + 3, rgba(p["cap_l"]))
        c.rect(CX - 1, y + 4, CX + 1, y + 4, rgba(p["cap_d"]))       # the adjuster
        c.set(CX, y + 4, rgba(p["cap_l"]))
        hair_y = y + 5
    else:
        c.rect(CX - 4, y, CX + 4, y + 3, rgba(p["hair"]))
        c.rect(CX - 4, y, CX - 1, y + 2, rgba(p["hair_l"]))
        hair_y = y + 4

    c.rect(CX - 5, hair_y, CX + 5, hair_y + 2, rgba(p["hair"]))
    c.rect(CX - 5, hair_y, CX - 2, hair_y + 1, rgba(p["hair_l"]))
    c.rect(CX - 4, hair_y + 3, CX + 4, hair_y + 3, rgba(p["hair_d"]))   # nape
    c.rect(CX - 1, hair_y + 4, CX + 1, hair_y + 4, rgba(p["skin_d"]))   # neck
    return hair_y + 5


def torso(c, p, y, facing, arm, back=False):
    """Shoulders, jacket and arms. arm is how far the visible arm swings."""
    half = 6 if facing != "side" else 4
    c.rect(CX - half, y, CX + half, y + 11, rgba(p["coat"]))
    c.rect(CX - half, y, CX + half, y, rgba(p["coat_l"]))            # lit shoulders
    c.rect(CX + half - 1, y + 1, CX + half, y + 11, rgba(p["coat_d"]))

    if facing == "down":
        c.rect(CX - 1, y + 1, CX + 1, y + 6, rgba(p["shirt"]))       # open jacket
        c.set(CX + 1, y + 1, rgba(p["shirt_d"]))
        c.rect(CX - 2, y + 1, CX - 2, y + 6, rgba(p["coat_d"]))
        c.rect(CX + 2, y + 1, CX + 2, y + 6, rgba(p["coat_d"]))
    elif back:
        c.rect(CX, y + 1, CX, y + 10, rgba(p["coat_d"]))             # the back seam

    if facing == "side":
        # Only the near arm is drawn — the far one is behind the body — and a
        # dark line separates it from the jacket, or at this size the two merge
        # into one shape and the arm reads as a bag.
        ax = CX + 1
        c.rect(ax - 1, y + 2, ax - 1, y + 10, rgba(p["coat_d"]))
        c.rect(ax, y + 2 + max(0, arm), ax + 1, y + 9 + max(0, arm), rgba(p["coat"]))
        c.rect(ax, y + 2 + max(0, arm), ax, y + 9 + max(0, arm), rgba(p["coat_l"]))
        c.rect(ax, y + 10 + max(0, arm), ax + 1, y + 11 + max(0, arm),
               rgba(p["skin"]))
    else:
        c.rect(CX - half - 1, y + 2, CX - half - 1, y + 8, rgba(p["coat"]))
        c.rect(CX + half + 1, y + 2, CX + half + 1, y + 8, rgba(p["coat_d"]))
        c.rect(CX - half - 1, y + 9, CX - half - 1, y + 10, rgba(p["skin"]))
        c.rect(CX + half + 1, y + 9, CX + half + 1, y + 10, rgba(p["skin_d"]))
    return y + 12


def legs(c, p, y, facing, stride, lift=0):
    """Two legs and two shoes.

    In profile one leg goes forward and the other back, and the near one is
    drawn last so it overlaps: at rest they must still read as two legs, not as
    one post. Seen from the front or the back there is no forwards to go, so a
    step is a foot lifted off the floor — which is what lift is for."""
    bottom = CELL_H - 1
    if facing == "side":
        back_x, front_x = CX - 3 - stride, CX - 1 + stride
        for x, tone, shoe, toe in ((back_x, p["pants_d"], p["shoe"], 1),
                                   (front_x, p["pants"], p["shoe_l"], 2)):
            c.rect(x, y, x + 2, bottom - 3, rgba(tone))
            c.rect(x - 1, bottom - 2, x + 2 + toe, bottom, rgba(shoe))
            c.rect(x - 1, bottom, x + 2 + toe, bottom, OUT)
    else:
        gap = 1 + stride
        for side, tone, shoe, up in ((-1, p["pants"], p["shoe_l"], lift > 0),
                                     (1, p["pants_d"], p["shoe"], lift < 0)):
            x0 = CX + gap if side > 0 else CX - gap - 3
            x1 = x0 + 3
            foot = bottom - (1 if up else 0)
            c.rect(x0, y, x1, foot - 3, rgba(tone))
            c.rect(x0, foot - 2, x1, foot, rgba(shoe))
            c.rect(x0, foot, x1, foot, OUT)


def outline(c):
    """One dark pixel all round the silhouette. Against a wall painted in the
    character's own colours, tonal contrast alone is not enough."""
    w, h = c.image.size
    edge = [(x, y) for y in range(h) for x in range(w)
            if c.get(x, y)[3] == 0 and any(
                0 <= x + dx < w and 0 <= y + dy < h and c.get(x + dx, y + dy)[3] > 0
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                               (1, 1), (1, -1), (-1, 1), (-1, -1)))]
    for x, y in edge:
        c.set(x, y, OUT)
    return c


def frame(p, facing, stride=0, arm=0, bob=0, mouth=0, lift=0) -> Image.Image:
    c = cell()
    y = TOP - bob
    if facing == "down":
        y = head_down(c, p, y, mouth)
    elif facing == "side":
        y = head_side(c, p, y, mouth)
    else:
        y = head_up(c, p, y)
    y = torso(c, p, y, facing, arm, back=(facing == "up"))
    legs(c, p, y, facing, stride, lift)
    return outline(c).image


def frames_for(p, name):
    kind, facing = name.split("_")
    if kind == "idle":
        return [frame(p, facing)]
    if kind == "talk":
        return [frame(p, facing, mouth=0), frame(p, facing, mouth=1)]
    # contact, passing, contact the other way, passing — the bob lifts on the
    # passing frames, which is what gives a four-frame walk its weight.
    wide = 2 if facing == "side" else 1
    return [frame(p, facing, stride=wide, arm=1, lift=1),
            frame(p, facing, stride=0, arm=0, bob=1),
            frame(p, facing, stride=wide, arm=0, lift=-1),
            frame(p, facing, stride=0, arm=1, bob=1)]


def build(p):
    rows = [(name, frames_for(p, name), speed) for name, count, speed in ANIMATIONS]
    columns = max(len(f) for _, f, _ in rows)
    sheet = Image.new("RGBA", (columns * CELL_W, len(rows) * CELL_H), (0, 0, 0, 0))
    for r, (_, images, _) in enumerate(rows):
        for col, img in enumerate(images):
            sheet.paste(img, (col * CELL_W, r * CELL_H))
    path = f"{SPRITES}/char_{p['id']}_sheet.png"
    sheet.save(path)
    write_frames(p, rows, path)
    print(f"{path}  {sheet.width}x{sheet.height}  "
          f"{sum(len(f) for _, f, _ in rows)} frames")
    return sheet


def write_frames(p, rows, sheet_path):
    """Writes the SpriteFrames .tres from the same data that drew the sheet, so
    the two can never drift apart."""
    atlases, animations = [], []
    for r, (name, images, speed) in enumerate(rows):
        ids = []
        for col in range(len(images)):
            fid = f"f{r}_{col}"
            ids.append(fid)
            atlases.append(
                f'[sub_resource type="AtlasTexture" id="{fid}"]\n'
                f'atlas = ExtResource("1_sheet")\n'
                f'region = Rect2({col * CELL_W}, {r * CELL_H}, {CELL_W}, {CELL_H})\n')
        frames = ", ".join(
            '{\n"duration": 1.0,\n"texture": SubResource("%s")\n}' % f for f in ids)
        animations.append(
            '{\n"frames": [%s],\n"loop": true,\n"name": &"%s",\n"speed": %s\n}'
            % (frames, name, speed))

    body = (f'[gd_resource type="SpriteFrames" load_steps={len(atlases) + 2} '
            f'format=3]\n\n'
            f'[ext_resource type="Texture2D" path="res://{sheet_path}" '
            f'id="1_sheet"]\n\n'
            + "\n".join(atlases)
            + '\n[resource]\nanimations = [' + ", ".join(animations) + ']\n')
    out = f"{RESOURCES}/{p['id']}_frames.tres"
    with open(out, "w") as f:
        f.write(body)
    print(f"{out}")


def contact_shadow():
    """A blocky ellipse in two alpha steps rather than a soft blur: the project
    draws characters with Nearest filtering, so a blurred shadow would be the one
    thing on the sprite with fuzzy edges."""
    c = PixelCanvas(16, 5)
    inner, outer = (24, 18, 32, 130), (24, 18, 32, 60)
    for y, (x0, x1) in enumerate(((4, 11), (2, 13), (1, 14), (2, 13), (4, 11))):
        c.rect(x0, y, x1, y, outer)
    for y, (x0, x1) in enumerate(((6, 9), (3, 12), (2, 13), (3, 12), (6, 9))):
        if y in (1, 2, 3):
            c.rect(x0, y, x1, y, inner)
    path = f"{SPRITES}/shadow_contact.png"
    c.save(path)
    print(path)


if __name__ == "__main__":
    import os
    os.makedirs(RESOURCES, exist_ok=True)
    contact_shadow()
    for who in (LINO, CESARE):
        build(who)
