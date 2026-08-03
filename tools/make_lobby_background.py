"""Turns the generated Lobby image into the background the game loads.

The source is an image made outside the project — the same route the seven verb
icons took — and it is not in the repository, the same way their references are
not. Pass it in:

    python tools/make_lobby_background.py <image.png>

What this does, and why each step is here rather than done by hand:

* resizes to 1920x1080, exactly five times the game's 384x216, so on a phone
  1080 tall the background lands 1:1 and in scene it is a Sprite2D at scale 0.2;
* paints out the small sparkle the generator leaves on the floor, by
  interpolating the floor across it — every surface in this room is constant
  vertically and only changes horizontally, which is what makes that work;
* saves WebP rather than PNG. On a flat-shaded painting quality 92 differs from
  the original by at most 10/255 anywhere and 1.0 on average, and the file goes
  from 1934 kB to 91 kB. Godot imports WebP like any other texture.

The measurements the room's scene depends on, taken from this image and written
here so that a new image can be checked against them: the wall/floor line is at
y = 146 of 216, and the door is 36 wide by 58 tall centred at x = 313.
"""
import random
import sys

from PIL import Image

ASSET = "assets/backgrounds/bg_lobby.webp"
SPARKLE = (1228, 612, 1292, 686)          # in the source's own 1376x768
random.seed(1994)


def inpaint(px, box, feather=12):
    x0, y0, x1, y1 = box
    span = x1 - x0
    for y in range(y0, y1 + 1):
        a, b = px[x0 - feather, y], px[x1 + feather, y]
        for x in range(x0, x1 + 1):
            t = (x - x0) / span
            n = random.randint(-3, 3)
            px[x, y] = tuple(
                max(0, min(255, int(a[i] + (b[i] - a[i]) * t) + n)) for i in range(3))


def main(source: str) -> None:
    img = Image.open(source).convert("RGB")
    if img.size == (1376, 768):
        inpaint(img.load(), SPARKLE)
    else:
        print(f"warning: {img.size} is not the size the sparkle was measured on, "
              "skipping the clean-up")
    img.resize((1920, 1080), Image.LANCZOS).save(ASSET, quality=92, method=6)
    print(f"{ASSET} written")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
