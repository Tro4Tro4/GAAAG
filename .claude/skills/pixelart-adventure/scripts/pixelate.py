#!/usr/bin/env python3
"""Converte un render AI ad alta risoluzione in pixel art nativa reale.

Un generatore AI produce "immagini che assomigliano a pixel art": i blocchi non
sono allineati a una griglia, i bordi hanno anti-aliasing e i colori sono
migliaia. Questo script impone la griglia vera e la palette vera.

Pipeline:
  1. crop opzionale al rapporto d'aspetto esatto (evita deformazioni)
  2. downscale alla risoluzione nativa (BOX = media dei pixel, no ringing)
  3. quantizzazione alla palette master in Oklab, con dithering opzionale
  4. salvataggio del file nativo + anteprima ingrandita nearest-neighbor

Esempi
  python pixelate.py render.png -o bg_ufficio --native 640x360 \
      --palette ../assets/palettes/master-modern.hex --preview 3
  python pixelate.py sprite.png -o walk_01 --native 96x96 --alpha-threshold 128
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pxlib import load_palette, quantize  # noqa: E402


def parse_size(s: str) -> tuple[int, int]:
    a, b = s.lower().replace("×", "x").split("x")
    return int(a), int(b)


def crop_to_aspect(im: Image.Image, tw: int, th: int) -> Image.Image:
    w, h = im.size
    target = tw / th
    cur = w / h
    if abs(cur - target) < 1e-6:
        return im
    if cur > target:  # troppo largo -> taglia ai lati
        nw = int(round(h * target))
        x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(round(w / target))  # troppo alto -> taglia sopra/sotto
    y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True,
                    help="percorso di output senza estensione")
    ap.add_argument("--native", default="640x360", help="risoluzione nativa (def 640x360)")
    ap.add_argument("--palette", help="file palette .hex/.gpl/.json; se assente non quantizza")
    ap.add_argument("--dither", default="none",
                    choices=["none", "bayer2", "bayer4", "bayer8"])
    ap.add_argument("--dither-strength", type=float, default=0.5)
    ap.add_argument("--preview", type=int, default=3,
                    help="fattore di ingrandimento anteprima, 0 per non generarla")
    ap.add_argument("--no-crop", action="store_true",
                    help="deforma invece di ritagliare al rapporto d'aspetto")
    ap.add_argument("--alpha-threshold", type=int, default=0,
                    help=">0 rende l'alpha binaria a quella soglia (obbligatorio per gli sprite)")
    ap.add_argument("--resample", default="box", choices=["box", "lanczos", "nearest"])
    args = ap.parse_args()

    tw, th = parse_size(args.native)
    im = Image.open(args.input)
    has_alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
    im = im.convert("RGBA" if has_alpha else "RGB")

    if not args.no_crop:
        im = crop_to_aspect(im, tw, th)

    filt = {"box": Image.BOX, "lanczos": Image.LANCZOS, "nearest": Image.NEAREST}[args.resample]
    small = im.resize((tw, th), filt)

    arr = np.array(small)
    rgb = arr[..., :3]
    alpha = arr[..., 3] if has_alpha else None

    if args.alpha_threshold > 0 and alpha is not None:
        alpha = np.where(alpha >= args.alpha_threshold, 255, 0).astype(np.uint8)

    if args.palette:
        pal = load_palette(args.palette)
        rgb = quantize(rgb, pal, dither=args.dither, strength=args.dither_strength)
        print(f"quantizzato su {len(pal)} colori di palette")

    if alpha is not None:
        out_arr = np.dstack([rgb, alpha])
        out_im = Image.fromarray(out_arr, "RGBA")
    else:
        out_im = Image.fromarray(rgb, "RGB")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    native_path = out.with_suffix(".png")
    out_im.save(native_path)
    n_col = len(np.unique(rgb.reshape(-1, 3), axis=0))
    print(f"nativo  -> {native_path}  {tw}x{th}  {n_col} colori")

    if args.preview > 0:
        pv = out_im.resize((tw * args.preview, th * args.preview), Image.NEAREST)
        pv_path = out.with_name(out.name + f"_x{args.preview}").with_suffix(".png")
        pv.save(pv_path)
        print(f"preview -> {pv_path}  {pv.size[0]}x{pv.size[1]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
