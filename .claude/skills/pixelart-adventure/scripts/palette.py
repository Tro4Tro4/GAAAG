#!/usr/bin/env python3
"""Costruisce, estrae e visualizza palette.

Tre sottocomandi:

  build    genera la palette master del progetto (9 rampe x 5 valori = 45 colori
           + 3 estremi) applicando hue-shifting: le ombre virano al freddo, le
           luci al caldo. E' la regola che rende la pixel art "dipinta" invece
           che "sbiadita", perche' imita il comportamento della luce reale.

  extract  ricava una palette da un'immagine con k-means in Oklab. Serve per
           campionare un riferimento o per capire quanti colori usa un asset.

  swatch   esporta un PNG di controllo della palette.

Esempi
  python palette.py build --out ../assets/palettes
  python palette.py extract ref.png -n 32 --out estratta.hex
  python palette.py swatch ../assets/palettes/master-modern.hex -o check.png
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pxlib import (hsl_to_rgb, load_palette, rgb_to_hex, rgb_to_hsv_arr,  # noqa: E402
                   rgb_to_oklab, save_palette, swatch_png)

# Limiti di stile misurati sul riferimento: nessun colore supera S=50 (HSV),
# i valori vivono fra ~10 e ~78 con mediana bassa. Le rampe rispettano questo.
MAX_HSV_SAT = 50.0

# nome: (hue ombra, hue luce, sat ombra, sat luce, [5 stop di lightness HSL])
RAMPS: dict[str, tuple] = {
    # MATERIALI: coprono l'80-90% dell'area di una scena, quindi sono loro a
    # determinare la saturazione percepita. Tarati sul riferimento, dove i
    # colori di materiale vivono fra S=6 e S=38 con mediana 24.
    "ink":      (250, 210, 18, 6,  [7, 15, 26, 42, 78]),
    "concrete": (225, 200, 20, 10, [14, 24, 36, 52, 70]),
    "wood":     (355, 34,  18, 20, [12, 22, 33, 46, 62]),
    "skin":     (350, 32,  22, 24, [18, 30, 44, 58, 74]),
    "denim":    (235, 205, 20, 14, [13, 22, 33, 45, 60]),
    "foliage":  (175, 78,  18, 20, [12, 20, 30, 42, 58]),
    # ACCENTI: occupano pochi pixel e per questo possono restare saturi. Sono
    # il contrasto che tiene su la scena: luce artificiale, ruggine, schermi.
    "tungsten": (18,  48,  36, 40, [24, 38, 52, 66, 80]),
    "rust":     (350, 28,  30, 32, [16, 27, 39, 52, 66]),
    "screen":   (215, 172, 34, 38, [16, 27, 40, 54, 70]),
}

# Colori riservati: NON usarli per materiali, solo per leggibilita' funzionale.
RESERVED = {
    "pure_black": (0, 0, 0),        # solo per il vuoto/letterbox
    "pure_white": (255, 255, 255),  # solo per specular puntuale, max 1-2 px
    "key_magenta": (255, 0, 255),   # colorkey nei tool che non gestiscono alpha
}


def build_ramp(h0, h1, s0, s1, ls) -> list[tuple[int, int, int]]:
    n = len(ls)
    out = []
    for i, l in enumerate(ls):
        t = i / (n - 1)
        h = h0 + (h1 - h0) * t if abs(h1 - h0) <= 180 else \
            h0 + ((h1 - h0) - 360 * np.sign(h1 - h0)) * t
        s = s0 + (s1 - s0) * t
        # abbassa la saturazione HSL fino a rispettare il tetto HSV
        for _ in range(40):
            c = hsl_to_rgb(h, s, l)
            hsv = rgb_to_hsv_arr(np.array([[c]], dtype=np.uint8))[0, 0]
            if hsv[1] <= MAX_HSV_SAT or s <= 1:
                break
            s -= 1.5
        out.append(hsl_to_rgb(h, s, l))
    return out


def cmd_build(args) -> int:
    colors: list[tuple[int, int, int]] = []
    report: list[str] = []
    for name, (h0, h1, s0, s1, ls) in RAMPS.items():
        ramp = build_ramp(h0, h1, s0, s1, ls)
        colors += ramp
        report.append(f"{name:9s} " + " ".join("#" + rgb_to_hex(c) for c in ramp))
    colors += list(RESERVED.values())

    arr = np.array(colors, dtype=np.uint8)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = args.name
    save_palette(arr, outdir / f"{stem}.hex", stem)
    save_palette(arr, outdir / f"{stem}.gpl", stem)
    save_palette(arr, outdir / f"{stem}.json", stem)
    swatch_png(arr, outdir / f"{stem}.png", cell=24, cols=5)

    print("\n".join(report))
    hsv = rgb_to_hsv_arr(arr[:-3])  # esclude i riservati
    print(f"\n{len(arr)} colori. Materiali: S max {hsv[:,1].max():.0f} "
          f"(tetto {MAX_HSV_SAT:.0f}), V da {hsv[:,2].min():.0f} a {hsv[:,2].max():.0f}")
    print(f"scritti in {outdir}/{stem}.[hex|gpl|json|png]")
    return 0


def cmd_extract(args) -> int:
    from PIL import Image
    im = Image.open(args.input).convert("RGB")
    arr = np.array(im).reshape(-1, 3)
    if args.max_pixels and len(arr) > args.max_pixels:
        idx = np.random.default_rng(0).choice(len(arr), args.max_pixels, replace=False)
        arr = arr[idx]
    lab = rgb_to_oklab(arr)

    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=args.n, n_init=4, random_state=0).fit(lab)
    # per ogni cluster prende il pixel reale piu' vicino al centroide,
    # cosi' i colori restano colori esistenti e non medie inventate
    cols = []
    for k in range(args.n):
        m = km.labels_ == k
        if not m.any():
            continue
        sub_lab, sub_rgb = lab[m], arr[m]
        d = ((sub_lab - km.cluster_centers_[k]) ** 2).sum(1)
        cols.append(tuple(int(v) for v in sub_rgb[d.argmin()]))
    out = np.array(sorted(cols, key=lambda c: sum(c)), dtype=np.uint8)
    save_palette(out, args.out, Path(args.out).stem)
    hsv = rgb_to_hsv_arr(out)
    print(f"{len(out)} colori -> {args.out}")
    print(f"S mediana {np.median(hsv[:,1]):.0f} max {hsv[:,1].max():.0f} | "
          f"V mediana {np.median(hsv[:,2]):.0f} range {hsv[:,2].min():.0f}-{hsv[:,2].max():.0f}")
    return 0


def cmd_swatch(args) -> int:
    pal = load_palette(args.palette)
    swatch_png(pal, args.out, cell=args.cell, cols=args.cols)
    print(f"{len(pal)} colori -> {args.out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="genera la palette master")
    b.add_argument("--out", default="../assets/palettes")
    b.add_argument("--name", default="master-modern")
    b.set_defaults(func=cmd_build)

    e = sub.add_parser("extract", help="estrae una palette da un'immagine")
    e.add_argument("input")
    e.add_argument("-n", type=int, default=32)
    e.add_argument("--out", default="extracted.hex")
    e.add_argument("--max-pixels", type=int, default=200_000)
    e.set_defaults(func=cmd_extract)

    s = sub.add_parser("swatch", help="esporta un PNG di controllo")
    s.add_argument("palette")
    s.add_argument("-o", "--out", default="swatch.png")
    s.add_argument("--cell", type=int, default=24)
    s.add_argument("--cols", type=int, default=8)
    s.set_defaults(func=cmd_swatch)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
