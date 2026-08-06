"""Turns the two generated images into the Tubes corridor's two planes.

The corridor is two screens wide and the camera scrolls across it, so it is
built as two layers instead of one picture: the back wall drifts at 85% of the
camera while the pipes stay locked to the floor. The pipes have to be on the
game plane and not in front, because the porthole, the plate and the posting
point are hotspots pinned to fixed coordinates — a layer moving at its own
speed would slide the picture out from under them, and the player would touch
the glass and get the wall.

    python tools/make_tubes_background.py <wall.png> <pipes-on-green.png>

Neither source is in the repository, the same way the Lobby's is not.

What this does:

* the wall is scaled to cover 3840x1080 — five times the room's 768x216 — and
  used whole. Its floor line falls where the generator put it, at 62% of the
  height, and the room follows: an earlier version lifted the image to meet the
  room's own line and filled the gap by repeating the last row, which came out
  as vertical smears. Real art wins over the blockout, as already recorded for
  the Lobby;
* the pipes arrive on pure green and the green is removed by hue rather than by
  connectivity, then the halo the generator leaves around the edges is pulled
  back by one pixel — without that the pipes carry a green rim that shows up
  against a grey wall;
* the pipe image is not wide enough for two screens, so it is laid down twice,
  the second copy mirrored. Mirroring rather than repeating hides the seam: the
  same run of flanges appearing twice in a row is what the eye catches, and a
  corridor whose pipes are symmetrical about its middle reads as a corridor.

The measurements the room's scene depends on, and which the scene was moved to
match: the wall/floor line is at y = 134 of 216 — not the 110 the blockout
assumed — and the pipe bundle spans y = 30 to y = 95.
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

WALL_ASSET = "assets/backgrounds/bg_tubes_wall.webp"
PIPES_ASSET = "assets/backgrounds/bg_tubes_pipes.webp"

OUT_W, OUT_H = 3840, 1080          # 5x the room's 768x216
FLOOR_LINE = 0.51                  # y = 110 of 216
PIPES_TOP, PIPES_BOTTOM = 30, 95   # in game units, out of 216
SOURCE_SIZE = (1952, 544)          # what the boxes below were measured on
SPARKLE = (1798, 392, 1858, 460)   # the generator's signature, in the source
PATCH_FROM = -120                  # offset of the clean wall to borrow from


def build_wall(source: str) -> None:
    """Scales the wall to cover the room and reports where its floor line fell.

    The image is used whole. An earlier version lifted it so that its floor
    line landed on the room's, and filled the gap left underneath by repeating
    the last row — which came out as vertical smears, because a row of a
    painted image is not a texture. The room moves instead: it is the rule
    already recorded for the Lobby, where the navmesh was moved rather than the
    picture cropped. Real art wins over the blockout.
    """
    im = Image.open(source).convert("RGB")
    if im.size == SOURCE_SIZE:
        im = Image.fromarray(despeckle(np.array(im)))
    else:
        print(f"  warning: {im.size} non e' {SOURCE_SIZE}, la stellina resta")
    scale = max(OUT_W / im.width, OUT_H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left = (im.width - OUT_W) // 2
    im = im.crop((left, 0, left + OUT_W, OUT_H))
    im.save(WALL_ASSET, quality=92, method=6)

    d = np.abs(np.diff(np.array(im).astype(int).mean(axis=1), axis=0)).sum(1)
    lo, hi = int(OUT_H * 0.4), int(OUT_H * 0.8)
    line = int(d[lo:hi].argmax() + lo)
    print(f"{WALL_ASSET}  {OUT_W}x{OUT_H}")
    print(f"  linea muro/pavimento a y={line} di {OUT_H}  ->  y={line/OUT_H*216:.0f} "
          f"in coordinate di gioco: e' questa che la stanza deve seguire")


def despeckle(a: np.ndarray) -> np.ndarray:
    """Paints out the four-pointed sparkle the generator signs its work with.

    The box is measured by hand, in the source's own 1952x544, exactly as the
    Lobby's is. Two ways of finding it automatically were tried and both did
    damage: the brightest pixel of the image is not the sparkle but one of the
    pale wall panels, which are lighter in absolute terms (190 against the
    sparkle's 163); and local contrast against a blurred copy picks the
    wall/floor line first, because a hard straight edge stands out from its
    surroundings more than a soft small shape does.

    There is no clever version of this. The sparkle is only recognisable by its
    shape, the source is a fixed input, and measuring it once costs a minute.
    """
    x0, y0, x1, y1 = SPARKLE
    pad = 24
    box = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)

    # Blurred away rather than replaced. Two replacement strategies were tried
    # and both left a rectangle: interpolating across the hole ignores that
    # this wall shades vertically, and copying a patch from further along
    # brings that patch's own cracks with it. Blurring keeps the wall's own
    # colour and gradient and only destroys the small hard shape sitting on
    # top of it, and a feathered mask means there is no edge anywhere.
    region = Image.fromarray(a[box[1]:box[3], box[0]:box[2]].astype(np.uint8))
    blurred = region.filter(ImageFilter.GaussianBlur(14))

    h, w = box[3] - box[1], box[2] - box[0]
    yy = np.abs(np.linspace(-1, 1, h))[:, None]
    xx = np.abs(np.linspace(-1, 1, w))[None, :]
    mask = np.clip(1.6 * (1.0 - np.maximum(yy, xx)), 0, 1)[..., None]

    out = a.copy()
    out[box[1]:box[3], box[0]:box[2]] = (
        np.array(region) * (1 - mask) + np.array(blurred) * mask).astype(np.uint8)
    print(f"  stellina sfocata via da {SPARKLE}")
    return out


def cut_green(source: str) -> Image.Image:
    im = Image.open(source).convert("RGB")
    a = np.array(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = (g > 150) & (g > r + 60) & (g > b + 60)

    # The generator leaves a soft green rim. Anything still leaning green after
    # the cut gets dropped too, then one pixel is eroded off the whole
    # silhouette: cheaper than de-fringing, and at this scale invisible.
    halo = (g > r + 20) & (g > b + 20)
    keep = ~(green | halo)
    k = keep.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        k &= np.roll(keep, (dy, dx), axis=(0, 1))

    rgba = np.dstack([a.astype(np.uint8), (k * 255).astype(np.uint8)])
    return Image.fromarray(rgba, "RGBA")


def build_pipes(source: str) -> None:
    im = cut_green(source)
    ys = np.where(np.array(im)[..., 3].any(axis=1))[0]
    band_h = round((PIPES_BOTTOM - PIPES_TOP) / 216 * OUT_H)
    scale = band_h / (ys.max() - ys.min() + 1)

    im = im.crop((0, ys.min(), im.width, ys.max() + 1))
    im = im.resize((round(im.width * scale), band_h), Image.LANCZOS)

    out = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    top = round(PIPES_TOP / 216 * OUT_H)
    x, flip = 0, False
    while x < OUT_W:
        tile = im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
        out.alpha_composite(tile, (x, top))
        x += im.width
        flip = not flip
    out.save(PIPES_ASSET, quality=92, method=6)
    print(f"{PIPES_ASSET}  {OUT_W}x{OUT_H}  (fascia y {top}..{top+band_h}, "
          f"{-(-OUT_W // im.width)} copie)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    build_wall(sys.argv[1])
    build_pipes(sys.argv[2])
