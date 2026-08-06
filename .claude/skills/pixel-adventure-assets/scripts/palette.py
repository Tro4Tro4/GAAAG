#!/usr/bin/env python3
"""Estrae e visualizza la tavolozza di un'immagine.

Serve a una regola sola di AGGGA, che finora non aveva strumento: **la tavolozza
del personaggio si deriva da quella dello sfondo della stanza, non si inventa a
parte**. E' la regola che decide se pixel art e sfondo dipinto convivono o
litigano, ed e' quella che a occhio si sbaglia piu' facilmente, perche' due
verdi diversi sembrano lo stesso verde finche' non stanno accanto.

Il flusso e' in due passi: si estrae la tavolozza madre dallo sfondo di una
stanza, e la si usa per disegnare gli sprite che ci vanno dentro.

    python .claude/skills/pixel-adventure-assets/scripts/palette.py \
        extract assets/backgrounds/bg_lobby.webp -n 24 --out /tmp/lobby.hex
    python .claude/skills/pixel-adventure-assets/scripts/palette.py \
        swatch /tmp/lobby.hex -o /tmp/lobby_swatch.png

Poi `qa_check.py --palette-from assets/backgrounds/bg_lobby.webp` verifica che
uno sprite non se ne sia allontanato.

Le distanze si misurano in Oklab, dove la distanza euclidea approssima la
differenza percepita: due colori a distanza uguale in Oklab si somigliano
davvero altrettanto, cosa che in sRGB non vale.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pxlib import (load_palette, rgb_to_hsv_arr, rgb_to_oklab,  # noqa: E402
                   save_palette, swatch_png)


def kmeans_oklab(lab: np.ndarray, k: int, iters: int = 40,
                 seed: int = 0) -> np.ndarray:
    """k-means in Oklab, in numpy puro.

    Scritto a mano invece di importare scikit-learn perche' quella e' una
    dipendenza da centinaia di megabyte per un algoritmo che qui sta in venti
    righe, e il progetto installa le librerie a mano su un telefono.

    Inizializzazione k-means++: il primo centro a caso, ognuno dei successivi
    scelto con probabilita' proporzionale al quadrato della distanza dal piu'
    vicino gia' scelto. Serve a non far nascere due centri dentro la stessa
    macchia di colore, che e' il modo in cui k-means restituisce tavolozze con
    tre grigi identici e nessun rosso.
    """
    rng = np.random.default_rng(seed)
    k = min(k, len(lab))
    centres = lab[rng.integers(len(lab))][None]
    for _ in range(k - 1):
        d = ((lab[:, None] - centres[None]) ** 2).sum(-1).min(1)
        total = d.sum()
        if total <= 0:
            break
        centres = np.vstack([centres, lab[rng.choice(len(lab), p=d / total)]])

    for _ in range(iters):
        d = ((lab[:, None] - centres[None]) ** 2).sum(-1)
        labels = d.argmin(1)
        moved = False
        for i in range(len(centres)):
            m = labels == i
            if m.any():
                new = lab[m].mean(0)
                if not np.allclose(new, centres[i]):
                    centres[i] = new
                    moved = True
        if not moved:
            break
    return labels


def cmd_extract(args) -> int:
    from PIL import Image
    im = Image.open(args.input)
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    arr = np.array(im)
    if arr.shape[-1] == 4:                       # ignora il vuoto di uno sprite
        arr = arr[arr[..., 3] > 0][:, :3]
    else:
        arr = arr.reshape(-1, 3)
    if len(arr) == 0:
        print("immagine completamente trasparente")
        return 1

    uniq = np.unique(arr, axis=0)
    if len(uniq) <= args.n:
        # Gia' abbastanza povera di colori: e' il caso di uno sprite o di un
        # prop, e raggrupparlo perderebbe informazione invece di aggiungerne.
        out = uniq[np.argsort(uniq.astype(int).sum(1))]
        print(f"{len(out)} colori (l'immagine ne ha meno di {args.n}: nessun raggruppamento)")
    else:
        sample = arr
        if args.max_pixels and len(sample) > args.max_pixels:
            idx = np.random.default_rng(0).choice(len(sample), args.max_pixels,
                                                  replace=False)
            sample = sample[idx]
        lab = rgb_to_oklab(sample)
        labels = kmeans_oklab(lab, args.n)
        # Per ogni gruppo tiene il pixel reale piu' vicino al centro, cosi' i
        # colori restano colori che esistono nell'immagine e non medie
        # inventate: una media fra due tinte piatte e' una terza tinta che nello
        # sfondo non c'e', e uno sprite che la usa stona con entrambe.
        cols = []
        for kk in range(labels.max() + 1):
            m = labels == kk
            if not m.any():
                continue
            centre = lab[m].mean(0)
            d = ((lab[m] - centre) ** 2).sum(1)
            cols.append(tuple(int(v) for v in sample[m][d.argmin()]))
        out = np.array(sorted(set(cols), key=lambda c: sum(c)), dtype=np.uint8)
        print(f"{len(out)} colori estratti da {len(uniq)} unici")

    save_palette(out, args.out, Path(args.out).stem)
    hsv = rgb_to_hsv_arr(out)
    print(f"-> {args.out}")
    print(f"   S mediana {np.median(hsv[:, 1]):.0f} (max {hsv[:, 1].max():.0f}) | "
          f"V mediana {np.median(hsv[:, 2]):.0f} "
          f"(da {hsv[:, 2].min():.0f} a {hsv[:, 2].max():.0f})")
    return 0


def cmd_swatch(args) -> int:
    pal = load_palette(args.palette)
    swatch_png(pal, args.out, cell=args.cell, cols=args.cols)
    print(f"{len(pal)} colori -> {args.out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("extract", help="estrae la tavolozza di un'immagine")
    e.add_argument("input")
    e.add_argument("-n", type=int, default=24, help="quanti colori (default 24)")
    e.add_argument("--out", default="palette.hex")
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
