#!/usr/bin/env python3
"""Controllo automatico di un asset grafico di AGGGA.

Verifica meccanicamente le cose che in un PNG non si vedono ma in gioco si'.
Esce con codice 1 se almeno un controllo FALLISCE, quindi si puo' mettere in
uno script di build o in un hook pre-commit.

I numeri non sono di stile generico: vengono dalle decisioni registrate in
CLAUDE.md — base 384x216, un pixel di texture per unita' di gioco, filtro
Nearest, celle 24x44 con il corpo alto 40, sfondi alle misure della stanza.

    python .claude/skills/pixel-adventure-assets/scripts/qa_check.py \
        assets/sprites/char_lino_sheet.png --profile sheet \
        --palette-from assets/backgrounds/bg_lobby.png

    python .claude/skills/pixel-adventure-assets/scripts/qa_check.py \
        assets/backgrounds/bg_lobby.png --profile background

Profili: sheet (foglio personaggio), sprite (prop, oggetto, StateVisual),
background (sfondo di stanza), shadow (ombra di contatto — l'unica cosa che
puo' essere semitrasparente).
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pxlib import rgb_to_hex, rgb_to_oklab  # noqa: E402

# --- geometria del progetto, da CLAUDE.md e da tools/make_character_sheets.py -
CELL_W, CELL_H = 24, 44
BODY_H = 40
# Il contorno scuro sta *fuori* dalla figura, quindi un corpo alto 40 misura 41
# righe di pixel opachi. Misurato sui fogli approvati: il corpo va da y=4 a
# y=43, e la riga y=3 contiene solo il colore del contorno.
OUTLINE = 1
# Sui fotogrammi di passaggio della camminata il corpo si alza di un pixel: e'
# il "walk bob", ed e' il motivo per cui la cella e' piu' alta del corpo. Vale
# solo per le righe walk — un idle alto 42 sarebbe invece un errore di disegno.
BOB = 1
SHEET_ROWS = 9                    # nove animazioni
SHEET_COLS = 4                    # la camminata e' l'animazione piu' lunga
# Uno sfondo e' pixel art come tutto il resto: disegnato alle dimensioni della
# stanza, usato a scala 1 e filtro Nearest. Erano 1920x1080 finche' gli sfondi
# erano dipinti; da "Tutto in pixel art: anche gli sfondi" l'altezza e' quella
# dello schermo e la larghezza un suo multiplo — 384x216 per una stanza di una
# schermata, 768x216 per il corridoio largo due.
BG_W, BG_H = 384, 216
FRAMES_PER_ROW = [1, 1, 1, 4, 4, 4, 2, 2, 2]
ROW_NAMES = ["idle_down", "idle_side", "idle_up",
             "walk_down", "walk_side", "walk_up",
             "talk_down", "talk_side", "talk_up"]

# Distanza Oklab oltre la quale un colore non appartiene piu' alla tavolozza
# della stanza. Non e' una soglia di gusto presa da una guida generica: e'
# misurata sugli asset che il progetto ha gia' accettato, contro dei colori
# volutamente estranei. Sull'atrio, il colore piu' lontano di ogni asset:
#
#   char_lino_sheet     0.129        magenta puro   0.271
#   char_cesare_sheet   0.081        verde puro     0.232
#   prop_notice/rack    0.051
#   prop_chairs         0.036
#   shadow_contact      0.011
#
# Fra 0.13 e 0.23 c'e' un vuoto, e la soglia sta li' in mezzo: passa tutto
# quello che e' stato disegnato per questa stanza, ferma quello che viene da
# un'altra tavolozza. Rimisurala se cambia lo sfondo di riferimento.
PALETTE_TOLERANCE = 0.16

# Tetti per non far esplodere il confronto: e' una matrice di distanze fra
# tutti i colori dell'asset e tutti quelli del riferimento, quindi cresce come
# il prodotto. Uno sfondo contro se stesso sarebbe 18388 x 18388 e riempirebbe
# la memoria; con questi tetti resta sotto il decimo di secondo.
MAX_KINSHIP_COLORS = 512
MAX_REF_COLORS = 4096

# Il vuoto piu' i due livelli di trasparenza dell'ombra di contatto.
SHADOW_LEVELS = 3

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
_rows: list[tuple[str, str, str]] = []


def check(name: str, ok: bool, detail: str = "", soft: bool = False) -> None:
    _rows.append((PASS if ok else (WARN if soft else FAIL), name, detail))


def detect_block_size(rgb: np.ndarray, max_b: int = 8) -> int:
    """Se l'immagine e' un upscale NxN, ogni blocco NxN e' di tinta unita.

    E' il controllo che intercetta l'errore che CLAUDE.md teme di piu' sugli
    sprite: disegnare piu' grande e rimpicciolire in scena. Con il filtro
    Nearest un fattore non intero fa uscire alcuni pixel del doppio degli
    altri, e sul viso si legge come asimmetria della faccia.
    """
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


def check_sheet_geometry(alpha: np.ndarray) -> None:
    """I controlli che valgono solo per un foglio personaggio.

    Il piu' importante e' l'ancoraggio dei piedi: in ogni cella l'ultima riga
    con pixel opachi deve essere l'ultima riga della cella. Un frame con i
    piedi un pixel piu' su fa sobbalzare il personaggio a ogni passo, e in un
    PNG guardato da fermo non si vede.
    """
    h, w = alpha.shape
    ok_size = (w, h) == (CELL_W * SHEET_COLS, CELL_H * SHEET_ROWS)
    check("griglia del foglio", ok_size,
          f"{w}x{h}" if ok_size else
          f"trovato {w}x{h}, atteso {CELL_W * SHEET_COLS}x{CELL_H * SHEET_ROWS} "
          f"({SHEET_COLS} colonne x {SHEET_ROWS} righe di celle {CELL_W}x{CELL_H})")
    if not ok_size:
        return

    unanchored, empty, tall, filler = [], [], [], []
    for r, (name, n) in enumerate(zip(ROW_NAMES, FRAMES_PER_ROW)):
        for c in range(SHEET_COLS):
            cell = alpha[r * CELL_H:(r + 1) * CELL_H, c * CELL_W:(c + 1) * CELL_W]
            used = np.where(cell.any(axis=1))[0]
            if c >= n:
                if cell.any():
                    filler.append(f"{name}[{c}]")
                continue
            if len(used) == 0:
                empty.append(f"{name}[{c}]")
                continue
            if int(used.max()) != CELL_H - 1:
                unanchored.append(f"{name}[{c}] piedi a {int(used.max())} "
                                  f"invece di {CELL_H - 1}")
            limit = BODY_H + OUTLINE + (BOB if name.startswith("walk") else 0)
            if int(used.max()) - int(used.min()) + 1 > limit:
                tall.append(f"{name}[{c}] "
                            f"{int(used.max()) - int(used.min()) + 1} px "
                            f"(max {limit})")

    check("piedi ancorati al fondo della cella", not unanchored,
          "tutte le celle" if not unanchored else
          f"{len(unanchored)}: " + "; ".join(unanchored[:4]))
    check("nessuna cella vuota fra i frame attesi", not empty,
          "" if not empty else ", ".join(empty[:6]))
    check(f"figura entro {BODY_H} px piu' il contorno", not tall,
          "" if not tall else ", ".join(tall[:6]))
    check("celle di riempimento trasparenti", not filler,
          "" if not filler else ", ".join(filler[:6]), soft=True)


def check_palette_kinship(uniq: np.ndarray, ref_path: str, tol: float) -> None:
    """Quanto i colori dell'asset appartengono alla tavolozza della stanza.

    Non e' aderenza a una palette fissa: il progetto non ne ha una, ha una
    tavolozza madre per stanza da cui gli sprite si derivano. Qui si misura
    quanto ogni colore dista dal piu' vicino dello sfondo, in Oklab.
    """
    if len(uniq) > MAX_KINSHIP_COLORS:
        # Uno sfondo dipinto ha decine di migliaia di colori: la domanda "da
        # quale tavolozza derivi" non si applica a lui, e' lui la tavolozza.
        check("tavolozza derivata", True,
              f"saltato: {len(uniq)} colori, e' una sorgente e non un derivato",
              soft=True)
        return

    ref = Image.open(ref_path)
    ref = ref.convert("RGBA") if ref.mode in ("RGBA", "LA", "P") else ref.convert("RGB")
    ra = np.array(ref)
    ra = ra[ra[..., 3] > 0][:, :3] if ra.shape[-1] == 4 else ra.reshape(-1, 3)
    ref_uniq = np.unique(ra, axis=0)
    if len(ref_uniq) > MAX_REF_COLORS:
        # Campionamento deterministico: due esecuzioni sullo stesso sfondo
        # devono dare lo stesso verdetto, o il controllo non e' un controllo.
        idx = np.random.default_rng(0).choice(len(ref_uniq), MAX_REF_COLORS,
                                              replace=False)
        ref_uniq = ref_uniq[idx]

    d = np.sqrt(((rgb_to_oklab(uniq)[:, None]
                  - rgb_to_oklab(ref_uniq)[None]) ** 2).sum(-1)).min(1)
    far = uniq[d > tol]
    worst = ", ".join(f"#{rgb_to_hex(c)} ({v:.2f})"
                      for c, v in sorted(zip(far, d[d > tol]),
                                         key=lambda t: -t[1])[:4])
    check(f"tavolozza derivata da {Path(ref_path).name}", len(far) == 0,
          f"distanza max {d.max():.2f} (soglia {tol:.2f})" if len(far) == 0 else
          f"{len(far)} colori estranei su {len(uniq)}. Peggiori: {worst}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--profile",
                    choices=("sheet", "sprite", "background", "shadow"),
                    required=True)
    ap.add_argument("--palette-from", metavar="IMG",
                    help="sfondo della stanza da cui la tavolozza va derivata")
    ap.add_argument("--tolerance", type=float, default=PALETTE_TOLERANCE)
    ap.add_argument("--max-colors", type=int,
                    help="tetto di colori (default: 24 sprite, nessuno sfondo)")
    args = ap.parse_args()

    path = Path(args.input)
    im = Image.open(path)
    is_bg = args.profile == "background"
    im = im.convert("RGB") if is_bg else im.convert("RGBA")
    arr = np.array(im)
    rgb, alpha = arr[..., :3], (None if is_bg else arr[..., 3])
    h, w = rgb.shape[:2]

    vis = np.ones((h, w), bool) if alpha is None else alpha > 0
    vrgb = rgb[vis]
    if len(vrgb) == 0:
        print("immagine completamente trasparente")
        return 1
    uniq = np.unique(vrgb.reshape(-1, 3), axis=0)

    # --- formato del file ----------------------------------------------------
    # PNG per tutto: da quando gli sfondi sono pixel art alle dimensioni della
    # stanza pesano 9 kB, quindi il .webp con perdita che li reggeva a 1920x1080
    # non ha piu' niente da comprimere — e la pixel art vuole l'esattezza pixel
    # per pixel.
    want = ".png"
    check("formato del file", path.suffix.lower() == want,
          f"{path.suffix}" if path.suffix.lower() == want else
          f"{path.suffix}, atteso {want} (la pixel art vuole un formato senza perdita)")

    # --- geometria -----------------------------------------------------------
    if is_bg:
        # Una stanza larga il doppio vuole uno sfondo largo il doppio, quindi
        # la larghezza e' un multiplo della schermata ma l'altezza e' sempre
        # quella dello schermo: un pixel di texture resta un'unita' di gioco.
        ok = h == BG_H and w % BG_W == 0
        check("dimensioni dello sfondo", ok,
              f"{w}x{h}" + (f" ({w // BG_W} schermate)" if ok else
                            f", attesa altezza {BG_H} e larghezza multipla di {BG_W}"))
    elif args.profile == "sheet":
        check_sheet_geometry(alpha)
    else:
        ys, xs = np.where(vis)
        bh = int(ys.max() - ys.min() + 1)
        check("altezza entro la figura intera", bh <= BODY_H,
              f"{bh} px" + ("" if bh <= BODY_H else
                            f" (un personaggio a figura intera e' {BODY_H})"),
              soft=True)

    # --- un pixel di texture = un'unita' di gioco ----------------------------
    if not is_bg:
        b = detect_block_size(rgb)
        check("un pixel = un pixel", b == 1,
              "ok" if b == 1 else
              f"blocchi da {b}px: e' un upscale, salvalo a {w // b}x{h // b}")

        levels = sorted(int(v) for v in np.unique(alpha))
        if args.profile == "shadow":
            # L'ombra di contatto e' l'unica cosa del progetto che puo' essere
            # semitrasparente, ma a livelli discreti: una sfumatura continua
            # sarebbe l'unico elemento morbido di uno sprite disegnato netto.
            check("alpha a pochi livelli", len(levels) <= SHADOW_LEVELS,
                  f"livelli {levels}" if len(levels) <= SHADOW_LEVELS else
                  f"{len(levels)} livelli distinti: e' una sfumatura, "
                  f"non due livelli di trasparenza")
        else:
            soft_px = int(((alpha > 0) & (alpha < 255)).sum())
            check("alpha binaria", soft_px == 0,
                  "" if soft_px == 0 else
                  f"{soft_px} pixel semitrasparenti "
                  f"(con il filtro Nearest si vedono)")

    # --- colori --------------------------------------------------------------
    cap = args.max_colors or (None if is_bg else 24)
    if cap:
        check("numero di colori", len(uniq) <= cap, f"{len(uniq)} / max {cap}")
    else:
        check("numero di colori", True, f"{len(uniq)}", soft=True)

    if args.palette_from:
        check_palette_kinship(uniq, args.palette_from, args.tolerance)

    # --- stampa --------------------------------------------------------------
    width = max(len(r[1]) for r in _rows)
    fails = 0
    print(f"\nQA  {path.name}  [{args.profile}]\n" + "-" * (width + 34))
    for status, name, detail in _rows:
        mark = {PASS: "  ok  ", WARN: " warn ", FAIL: " FAIL "}[status]
        print(f"[{mark}] {name.ljust(width)}  {detail}")
        fails += status == FAIL
    print("-" * (width + 34))
    print("nessun problema bloccante" if not fails else f"{fails} controlli falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
