#!/usr/bin/env python3
"""Assembla i frame in uno sprite sheet a griglia fissa + metadati JSON.

La griglia fissa e' quello che vogliono tutti gli engine: ogni cella ha la stessa
dimensione e il personaggio e' ancorato allo stesso punto, cosi' l'animazione non
"balla". Lo script normalizza le celle, allinea i frame al punto di ancoraggio e
scrive un JSON con le animazioni ricavate dal nome dei file.

Convenzione dei nomi:  <animazione>_<direzione>_<numero>.png
  walk_s_00.png  walk_s_01.png ...      s=sud (verso lo spettatore)
  idle_e_00.png                         n=nord  e=est  w=ovest
Lo script raggruppa per <animazione>_<direzione> e ordina per numero.

Esempi
  python spritesheet.py frames/ -o hero --cell 64x96 --anchor bottom-center
  python spritesheet.py frames/ -o hero --cell 64x96 --columns 8 --fps 12
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

NAME_RE = re.compile(r"^(?P<anim>[a-z0-9]+)_(?P<dir>[nsew]{1,2})_(?P<idx>\d+)$", re.I)


def parse_size(s: str) -> tuple[int, int]:
    a, b = s.lower().replace("×", "x").split("x")
    return int(a), int(b)


def content_bbox(im: Image.Image) -> tuple[int, int, int, int]:
    a = np.array(im)
    if a.shape[2] == 4:
        m = a[..., 3] > 0
    else:
        m = np.ones(a.shape[:2], bool)
    ys, xs = np.where(m)
    if len(ys) == 0:
        return (0, 0, im.width, im.height)
    return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)


def place(im: Image.Image, cw: int, ch: int, anchor: str) -> Image.Image:
    """Mette il frame in una cella cw x ch allineandolo al punto di ancoraggio."""
    cell = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    x0, y0, x1, y1 = content_bbox(im)
    crop = im.crop((x0, y0, x1, y1))
    cwid, chei = crop.size
    if cwid > cw or chei > ch:
        raise SystemExit(f"contenuto {cwid}x{chei} piu' grande della cella {cw}x{ch}")
    if anchor == "bottom-center":
        ox, oy = (cw - cwid) // 2, ch - chei
    elif anchor == "center":
        ox, oy = (cw - cwid) // 2, (ch - chei) // 2
    elif anchor == "top-left":
        ox, oy = 0, 0
    else:
        raise SystemExit(f"anchor sconosciuto: {anchor}")
    cell.paste(crop, (ox, oy))
    return cell


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("indir", help="cartella con i frame PNG")
    ap.add_argument("-o", "--out", required=True, help="output senza estensione")
    ap.add_argument("--cell", required=True, help="dimensione cella, es. 64x96")
    ap.add_argument("--columns", type=int, default=0,
                    help="colonne dello sheet (0 = una riga per animazione)")
    ap.add_argument("--anchor", default="bottom-center",
                    choices=["bottom-center", "center", "top-left"])
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--preview", type=int, default=0)
    args = ap.parse_args()

    cw, ch = parse_size(args.cell)
    files = sorted(Path(args.indir).glob("*.png"))
    if not files:
        raise SystemExit(f"nessun PNG in {args.indir}")

    groups: dict[str, list[Path]] = defaultdict(list)
    loose: list[Path] = []
    for f in files:
        m = NAME_RE.match(f.stem)
        if m:
            groups[f"{m['anim'].lower()}_{m['dir'].lower()}"].append(f)
        else:
            loose.append(f)
    for k in groups:
        groups[k].sort(key=lambda p: int(NAME_RE.match(p.stem)["idx"]))
    if loose:
        groups["default"] = loose
        print(f"nota: {len(loose)} file fuori convenzione raccolti in 'default'")

    order = sorted(groups)
    if args.columns > 0:
        cols = args.columns
        total = sum(len(groups[k]) for k in order)
        rows = -(-total // cols)
    else:
        cols = max(len(groups[k]) for k in order)
        rows = len(order)

    sheet = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    anims: dict[str, dict] = {}
    i = 0
    for r, key in enumerate(order):
        frames = []
        for j, f in enumerate(groups[key]):
            cell = place(Image.open(f).convert("RGBA"), cw, ch, args.anchor)
            if args.columns > 0:
                cx, cy = i % cols, i // cols
                i += 1
            else:
                cx, cy = j, r
            sheet.paste(cell, (cx * cw, cy * ch))
            frames.append({"index": cy * cols + cx, "x": cx * cw, "y": cy * ch})
        anims[key] = {"fps": args.fps, "loop": True, "frames": frames}

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet_path = out.with_suffix(".png")
    sheet.save(sheet_path)

    meta = {
        "image": sheet_path.name,
        "sheet": {"width": sheet.width, "height": sheet.height,
                  "columns": cols, "rows": rows},
        "cell": {"width": cw, "height": ch, "anchor": args.anchor},
        "animations": anims,
    }
    meta_path = out.with_suffix(".json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"sheet -> {sheet_path}  {sheet.width}x{sheet.height}  "
          f"({cols}x{rows} celle da {cw}x{ch})")
    print(f"meta  -> {meta_path}")
    for k in order:
        print(f"   {k:14s} {len(groups[k])} frame")

    if args.preview:
        pv = sheet.resize((sheet.width * args.preview, sheet.height * args.preview),
                          Image.NEAREST)
        p = out.with_name(out.name + f"_x{args.preview}").with_suffix(".png")
        pv.save(p)
        print(f"preview -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
