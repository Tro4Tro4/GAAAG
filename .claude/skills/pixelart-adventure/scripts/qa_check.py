#!/usr/bin/env python3
"""Controllo qualita' automatico di un asset pixel art.

Verifica meccanicamente le cose che l'occhio perdona ma il gioco no: risoluzione
sbagliata, colori fuori palette, anti-aliasing residuo del generatore AI, alpha
sfumata sugli sprite, saturazione fuori dai limiti di stile, blocchi non
allineati alla griglia (segno che l'immagine e' un upscale mascherato).

Esce con codice 1 se almeno un controllo FALLISCE, cosi' e' usabile in uno
script di build o in un hook pre-commit.

Esempi
  python qa_check.py bg_ufficio.png --native 640x360 \
      --palette ../assets/palettes/master-modern.hex
  python qa_check.py sprite.png --native 96x96 --sprite --max-colors 24
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pxlib import load_palette, rgb_to_hex, rgb_to_hsv_arr, rgb_to_oklab  # noqa: E402

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
_rows: list[tuple[str, str, str]] = []


def check(name: str, ok: bool, detail: str = "", soft: bool = False) -> None:
    _rows.append((PASS if ok else (WARN if soft else FAIL), name, detail))


def detect_block_size(rgb: np.ndarray, max_b: int = 8) -> int:
    """Se l'immagine e' un upscale NxN, le differenze fra colonne/righe adiacenti
    sono nulle tranne ogni N pixel. Cerca il piu' grande N coerente."""
    best = 1
    for b in range(2, max_b + 1):
        h, w = rgb.shape[:2]
        if w % b or h % b:
            continue
        blocks = rgb[:h // b * b, :w // b * b].reshape(h // b, b, w // b, b, -1)
        flat = blocks.transpose(0, 2, 1, 3, 4).reshape(h // b, w // b, b * b, -1)
        if np.all(flat.max(2) == flat.min(2)):
            best = b
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--native", help="risoluzione nativa attesa, es. 640x360")
    ap.add_argument("--palette", help="palette di riferimento")
    ap.add_argument("--max-colors", type=int, help="tetto di colori per l'asset")
    ap.add_argument("--sprite", action="store_true",
                    help="richiede alpha binaria e sfondo trasparente")
    ap.add_argument("--grid", type=int, default=0,
                    help="verifica che le dimensioni siano multiple di N (es. 8)")
    ap.add_argument("--max-sat", type=float, default=50.0)
    ap.add_argument("--max-val", type=float, default=90.0)
    args = ap.parse_args()

    im = Image.open(args.input)
    mode_alpha = im.mode in ("RGBA", "LA")
    im = im.convert("RGBA") if mode_alpha else im.convert("RGB")
    arr = np.array(im)
    rgb = arr[..., :3]
    alpha = arr[..., 3] if mode_alpha else None
    h, w = rgb.shape[:2]

    # visibile = pixel opachi (per gli sprite ignora il vuoto)
    vis = np.ones((h, w), bool) if alpha is None else alpha > 0
    vrgb = rgb[vis]
    if len(vrgb) == 0:
        print("immagine completamente trasparente")
        return 1

    # --- risoluzione ---------------------------------------------------------
    if args.native:
        tw, th = (int(x) for x in args.native.lower().replace("×", "x").split("x"))
        check("risoluzione nativa", (w, h) == (tw, th),
              f"{w}x{h}" if (w, h) == (tw, th) else f"trovata {w}x{h}, attesa {tw}x{th}")
    else:
        check("risoluzione", True, f"{w}x{h}", soft=True)

    if args.grid:
        check(f"dimensioni multiple di {args.grid}",
              w % args.grid == 0 and h % args.grid == 0, f"{w}x{h}")

    # --- upscale mascherato --------------------------------------------------
    b = detect_block_size(rgb)
    check("un pixel = un pixel", b == 1,
          "ok" if b == 1 else f"blocchi da {b}px: e' un upscale, ridimensiona a {w//b}x{h//b}")

    # --- conteggio colori ----------------------------------------------------
    uniq = np.unique(vrgb.reshape(-1, 3), axis=0)
    n = len(uniq)
    if args.max_colors:
        check("numero di colori", n <= args.max_colors, f"{n} / max {args.max_colors}")
    else:
        check("numero di colori", n <= 64, f"{n} (oltre 64 lo stile si sfalda)", soft=n > 64)

    # --- fuori palette -------------------------------------------------------
    if args.palette:
        pal = load_palette(args.palette)
        pl = rgb_to_oklab(pal)
        ul = rgb_to_oklab(uniq)
        d = np.sqrt(((ul[:, None] - pl[None]) ** 2).sum(-1)).min(1)
        off = uniq[d > 1e-6]
        # peso di ciascun colore fuori palette
        if len(off):
            flat = vrgb.reshape(-1, 3)
            tot = len(flat)
            worst = []
            for c in off[:200]:
                cnt = int(np.all(flat == c, axis=1).sum())
                worst.append((cnt, c))
            worst.sort(reverse=True, key=lambda x: x[0])
            top = ", ".join(f"#{rgb_to_hex(c)} ({100*k/tot:.2f}%)" for k, c in worst[:5])
            check("aderenza alla palette", False,
                  f"{len(off)} colori fuori palette. Peggiori: {top}")
        else:
            check("aderenza alla palette", True, f"tutti i {n} colori sono in palette")

    # --- residui di anti-aliasing -------------------------------------------
    flat = vrgb.reshape(-1, 3)
    view = np.ascontiguousarray(flat).view([("", flat.dtype)] * 3)
    _, counts = np.unique(view, return_counts=True)
    tot = counts.sum()
    orphan = int((counts / tot < 0.0005).sum())
    check("nessun residuo di anti-aliasing", orphan <= max(2, n // 10),
          f"{orphan} colori sotto lo 0,05% dei pixel"
          + ("" if orphan <= max(2, n // 10) else " -> riquantizza"),
          soft=True)

    # --- alpha ---------------------------------------------------------------
    if args.sprite:
        check("canale alpha presente", alpha is not None, "" if alpha is not None else "manca RGBA")
        if alpha is not None:
            soft_px = int(((alpha > 0) & (alpha < 255)).sum())
            check("alpha binaria", soft_px == 0, f"{soft_px} pixel semitrasparenti")
            border = np.concatenate([alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]])
            clean = border.max() == 0
            check("sfondo ritagliato", clean,
                  "bordo trasparente" if clean else
                  "lo sprite tocca il bordo: manca 1 px di margine per il contorno",
                  soft=True)

    # --- limiti di stile -----------------------------------------------------
    hsv = rgb_to_hsv_arr(uniq)
    over_s = int((hsv[:, 1] > args.max_sat + 0.5).sum())
    check(f"saturazione <= {args.max_sat:.0f}", over_s == 0,
          f"{over_s} colori troppo saturi" if over_s else
          f"S mediana {np.median(hsv[:,1]):.0f}")
    over_v = int((hsv[:, 2] > args.max_val + 0.5).sum())
    check(f"valore <= {args.max_val:.0f}", over_v <= 2,
          f"{over_v} colori troppo chiari (ammessi 2 per le fonti di luce)")

    vis_hsv = rgb_to_hsv_arr(vrgb)
    med_v = float(np.median(vis_hsv[:, 2]))
    check("mediana dei valori nella fascia scura", 18 <= med_v <= 48,
          f"V mediana {med_v:.0f} (target 25-40)", soft=True)

    # Il tetto sulla saturazione non basta: un'immagine puo' rispettarlo ed
    # essere comunque troppo accesa, perche' conta l'area che ogni colore
    # occupa. Sul riferimento la mediana pesata sull'area sta a 29 e solo il
    # 5% dei pixel supera S=50: e' questa la firma dello stile.
    med_s = float(np.median(vis_hsv[:, 1]))
    check("mediana della saturazione sull'area", 20 <= med_s <= 38,
          f"S mediana {med_s:.0f} (target 20-38)", soft=True)
    hot = float((vis_hsv[:, 1] > 50).mean() * 100)
    check("saturazione usata come accento", hot <= 12,
          f"{hot:.1f}% dei pixel sopra S 50 (target < 12%)", soft=True)

    # --- stampa --------------------------------------------------------------
    width = max(len(r[1]) for r in _rows)
    fails = 0
    print(f"\nQA  {Path(args.input).name}\n" + "-" * (width + 30))
    for status, name, detail in _rows:
        mark = {PASS: "  ok  ", WARN: " warn ", FAIL: " FAIL "}[status]
        print(f"[{mark}] {name.ljust(width)}  {detail}")
        fails += status == FAIL
    print("-" * (width + 30))
    print("nessun problema bloccante" if not fails else f"{fails} controlli falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
