"""Funzioni condivise: conversioni colore percettive, I/O palette, quantizzazione.

Usa Oklab per la distanza colore: in Oklab la distanza euclidea approssima la
differenza percepita molto meglio che in sRGB, quindi la quantizzazione non
"sporca" le ombre ne' sposta le tinte.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------- colore -----
def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = c.astype(np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c: np.ndarray) -> np.ndarray:
    c = np.clip(c, 0.0, 1.0)
    out = np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
    return np.clip(np.round(out * 255.0), 0, 255).astype(np.uint8)


_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])


def rgb_to_oklab(rgb: np.ndarray) -> np.ndarray:
    """rgb uint8 (...,3) -> oklab float (...,3)"""
    lin = srgb_to_linear(rgb)
    lms = lin @ _M1.T
    lms = np.cbrt(np.maximum(lms, 0.0))
    return lms @ _M2.T


def rgb_to_hsv_arr(rgb: np.ndarray) -> np.ndarray:
    """rgb uint8 (...,3) -> h[0,360) s[0,100] v[0,100]"""
    c = rgb.astype(np.float64) / 255.0
    mx = c.max(-1)
    mn = c.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    nz = d > 1e-9
    with np.errstate(invalid="ignore", divide="ignore"):
        hr = np.where(mx == r, ((g - b) / d) % 6, 0)
        hg = np.where(mx == g, (b - r) / d + 2, 0)
        hb = np.where(mx == b, (r - g) / d + 4, 0)
    h = np.where(nz, np.where(mx == r, hr, np.where(mx == g, hg, hb)) * 60, 0)
    s = np.where(mx > 1e-9, d / np.maximum(mx, 1e-9), 0) * 100
    return np.stack([h % 360, s, mx * 100], axis=-1)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """h in gradi, s e l in 0..100 -> tupla uint8"""
    h = (h % 360) / 360.0
    s, l = s / 100.0, l / 100.0
    if s == 0:
        v = int(round(l * 255))
        return (v, v, v)
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q

    def f(t):
        t %= 1.0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    return tuple(int(round(max(0.0, min(1.0, f(h + o))) * 255))
                 for o in (1 / 3, 0.0, -1 / 3))


# --------------------------------------------------------------- palette -----
def load_palette(path: str | Path) -> np.ndarray:
    """Legge .hex (un colore per riga), .gpl (GIMP/Aseprite), .json o .png/.aco-swatch.

    Ritorna array uint8 (N,3). Ignora duplicati mantenendo l'ordine.
    """
    p = Path(path)
    text_suffixes = {".hex", ".txt", ".gpl", ".json"}
    cols: list[tuple[int, int, int]] = []

    if p.suffix.lower() in text_suffixes:
        raw = p.read_text(encoding="utf-8", errors="ignore")
        if p.suffix.lower() == ".json":
            data = json.loads(raw)
            items = data["colors"] if isinstance(data, dict) else data
            for it in items:
                if isinstance(it, str):
                    cols.append(_hex_to_rgb(it))
                else:
                    cols.append(tuple(int(x) for x in it[:3]))
        else:
            for line in raw.splitlines():
                line = line.split("#!")[0].strip()
                if not line or line.lower().startswith(("gimp palette", "name:", "columns:")):
                    continue
                m = re.fullmatch(r"#?([0-9a-fA-F]{6})", line.split()[0].lstrip("#") if line.split() else "")
                if m:
                    cols.append(_hex_to_rgb(m.group(1)))
                    continue
                nums = re.findall(r"\d+", line)
                if len(nums) >= 3:
                    cols.append(tuple(int(n) for n in nums[:3]))
    else:  # immagine swatch: prende i colori unici
        from PIL import Image
        arr = np.array(Image.open(p).convert("RGB")).reshape(-1, 3)
        seen = {}
        for c in map(tuple, arr):
            seen.setdefault(c, None)
        cols = list(seen.keys())

    out, seen = [], set()
    for c in cols:
        if c not in seen:
            seen.add(c)
            out.append(c)
    if not out:
        raise ValueError(f"nessun colore leggibile in {p}")
    return np.array(out, dtype=np.uint8)


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.strip().lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(c) -> str:
    return "%02X%02X%02X" % (int(c[0]), int(c[1]), int(c[2]))


def save_palette(colors: np.ndarray, path: str | Path, name: str = "palette") -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix.lower() == ".gpl":
        lines = ["GIMP Palette", f"Name: {name}", "Columns: 8", "#"]
        lines += [f"{int(r):3d} {int(g):3d} {int(b):3d}\t{rgb_to_hex((r,g,b))}"
                  for r, g, b in colors]
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    elif p.suffix.lower() == ".json":
        p.write_text(json.dumps({"name": name,
                                 "colors": [rgb_to_hex(c) for c in colors]}, indent=2),
                     encoding="utf-8")
    else:
        p.write_text("\n".join(rgb_to_hex(c) for c in colors) + "\n", encoding="utf-8")


def swatch_png(colors: np.ndarray, path: str | Path, cell: int = 24, cols: int = 8) -> None:
    from PIL import Image
    rows = int(np.ceil(len(colors) / cols))
    img = Image.new("RGB", (cols * cell, rows * cell), (0, 0, 0))
    px = img.load()
    for i, c in enumerate(colors):
        ox, oy = (i % cols) * cell, (i // cols) * cell
        for y in range(cell):
            for x in range(cell):
                px[ox + x, oy + y] = tuple(int(v) for v in c)
    img.save(path)


# ---------------------------------------------------- quantizzazione ---------
_BAYER = {
    2: np.array([[0, 2], [3, 1]]) / 4.0,
    4: np.array([[0, 8, 2, 10], [12, 4, 14, 6],
                 [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0,
    8: None,  # costruito sotto
}


def bayer_matrix(n: int) -> np.ndarray:
    if n in (2, 4) and _BAYER[n] is not None:
        return _BAYER[n]
    if n == 8:
        b4 = _BAYER[4] * 16
        m = np.block([[b4 * 4, b4 * 4 + 2], [b4 * 4 + 3, b4 * 4 + 1]]) / 256.0
        return m
    raise ValueError("bayer supporta 2, 4, 8")


def quantize(rgb: np.ndarray, palette: np.ndarray, dither: str = "none",
             strength: float = 0.5, chunk: int = 200_000) -> np.ndarray:
    """Mappa ogni pixel al colore di palette piu' vicino in Oklab.

    dither: 'none' | 'bayer2' | 'bayer4' | 'bayer8'
    strength: ampiezza del pattern, in unita' di distanza media fra colori.
    """
    h, w = rgb.shape[:2]
    src = rgb[..., :3].astype(np.float64)

    if dither != "none":
        n = int(dither.replace("bayer", ""))
        m = bayer_matrix(n)
        tile = np.tile(m, (h // n + 1, w // n + 1))[:h, :w]
        # ampiezza proporzionale al passo medio della palette
        step = _mean_palette_step(palette)
        src = src + (tile - 0.5)[..., None] * step * strength
        src = np.clip(src, 0, 255)

    pal_lab = rgb_to_oklab(palette)
    flat = src.reshape(-1, 3)
    out_idx = np.empty(len(flat), dtype=np.int32)
    for i in range(0, len(flat), chunk):
        blk = rgb_to_oklab(np.clip(flat[i:i + chunk], 0, 255).astype(np.uint8))
        d = ((blk[:, None, :] - pal_lab[None, :, :]) ** 2).sum(-1)
        out_idx[i:i + chunk] = d.argmin(1)
    out = palette[out_idx].reshape(h, w, 3)
    return out.astype(np.uint8)


def _mean_palette_step(palette: np.ndarray) -> float:
    if len(palette) < 2:
        return 16.0
    lum = palette.astype(np.float64).mean(1)
    lum.sort()
    return float(max(6.0, np.mean(np.diff(lum)) if len(lum) > 1 else 16.0))
