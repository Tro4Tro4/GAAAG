"""
pixel_helpers.py
Funzioni di supporto per generare asset pixel art (personaggi, sfondi, oggetti, UI)
per avventure grafiche, usando Pillow (PIL).

Uso tipico:

    import sys
    sys.path.insert(0, '/home/claude/skills/pixel-adventure-assets/scripts')
    from pixel_helpers import PixelCanvas, build_spritesheet, upscale_nearest, apply_outline, ordered_dither

    canvas = PixelCanvas(32, 32)
    canvas.set(10, 10, (255, 0, 0, 255))
    canvas.rect(5, 5, 10, 10, (0, 255, 0, 255), fill=True)
    canvas.save('/home/claude/char_test.png')
"""

from PIL import Image
from typing import Tuple, List, Optional

RGBA = Tuple[int, int, int, int]


class PixelCanvas:
    """Canvas a griglia di 'pixel logici'. Ogni set/get lavora su un singolo pixel
    logico che corrisponde 1:1 a un pixel dell'immagine PIL sottostante (a bassa
    risoluzione). Usa upscale_nearest() solo alla fine per l'export ingrandito."""

    def __init__(self, width: int, height: int, background: RGBA = (0, 0, 0, 0)):
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), background)
        self.pixels = self.image.load()

    def set(self, x: int, y: int, color: RGBA):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[x, y] = color

    def get(self, x: int, y: int) -> RGBA:
        return self.pixels[x, y]

    def rect(self, x0: int, y0: int, x1: int, y1: int, color: RGBA, fill: bool = True):
        """Rettangolo con coordinate incluse su entrambi gli estremi."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if fill or x in (x0, x1) or y in (y0, y1):
                    self.set(x, y, color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color: RGBA):
        """Linea pixel-perfect con algoritmo di Bresenham (niente anti-aliasing)."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def flood_fill(self, x: int, y: int, color: RGBA):
        """Riempimento a partire da (x,y), sostituisce il colore contiguo uguale."""
        target = self.get(x, y)
        if target == color:
            return
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if 0 <= cx < self.width and 0 <= cy < self.height and self.get(cx, cy) == target:
                self.set(cx, cy, color)
                stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])

    def mirror_horizontal(self) -> "PixelCanvas":
        """Ritorna una nuova canvas specchiata orizzontalmente (utile per animazioni simmetriche)."""
        mirrored = PixelCanvas(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                mirrored.set(self.width - 1 - x, y, self.get(x, y))
        return mirrored

    def save(self, path: str):
        self.image.save(path)


def upscale_nearest(image: Image.Image, factor: int) -> Image.Image:
    """Ingrandisce mantenendo i bordi netti (NEAREST). Usare SEMPRE questo,
    mai BILINEAR/BICUBIC, per non rovinare l'effetto pixel art."""
    w, h = image.size
    return image.resize((w * factor, h * factor), Image.NEAREST)


def apply_outline(image: Image.Image, color: RGBA = (0, 0, 0, 255)) -> Image.Image:
    """Aggiunge un contorno di 1px attorno ai pixel opachi, sul bordo esterno
    della silhouette (outline nero pieno classico). L'immagine deve avere alpha."""
    w, h = image.size
    src = image.convert("RGBA")
    out = src.copy()
    src_px = src.load()
    out_px = out.load()
    for y in range(h):
        for x in range(w):
            if src_px[x, y][3] == 0:  # pixel trasparente
                # se adiacente a un pixel opaco, diventa outline
                neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                for nx, ny in neighbors:
                    if 0 <= nx < w and 0 <= ny < h and src_px[nx, ny][3] > 0:
                        out_px[x, y] = color
                        break
    return out


def ordered_dither(image: Image.Image, color_a: RGBA, color_b: RGBA, threshold_map: Optional[List[List[int]]] = None) -> Image.Image:
    """Applica un ordered dither (Bayer 4x4 di default) su un'area, alternando
    color_a/color_b in base a una matrice di soglie. Utile per transizioni morbide
    (cieli, muri) senza aumentare il numero di colori reali usati."""
    if threshold_map is None:
        # matrice di Bayer 4x4 normalizzata 0-15
        threshold_map = [
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5],
        ]
    w, h = image.size
    out = Image.new("RGBA", (w, h))
    out_px = out.load()
    n = len(threshold_map)
    for y in range(h):
        for x in range(w):
            t = threshold_map[y % n][x % n]
            out_px[x, y] = color_a if t < (n * n) / 2 else color_b
    return out


def build_spritesheet(frames: List[Image.Image], columns: int, padding: int = 0,
                       background: RGBA = (0, 0, 0, 0)) -> Image.Image:
    """Compone una lista di frame (stessa dimensione) in un'unica sprite sheet,
    su una griglia con 'columns' colonne. Ogni cella ha la dimensione del frame
    più il padding indicato."""
    if not frames:
        raise ValueError("Nessun frame fornito")
    fw, fh = frames[0].size
    rows = (len(frames) + columns - 1) // columns
    sheet_w = columns * (fw + padding) - padding
    sheet_h = rows * (fh + padding) - padding
    sheet = Image.new("RGBA", (sheet_w, sheet_h), background)
    for i, frame in enumerate(frames):
        col = i % columns
        row = i // columns
        x = col * (fw + padding)
        y = row * (fh + padding)
        sheet.paste(frame, (x, y), frame if frame.mode == "RGBA" else None)
    return sheet


def build_color_ramp(base_color: RGBA, steps: int = 4, hue_shift: bool = True) -> List[RGBA]:
    """Genera una rampa di colori da ombra a luce a partire da un colore base.
    Se hue_shift=True, le ombre spostano leggermente verso il blu/viola e le luci
    verso il giallo/arancio (tecnica classica di pixel art), invece di un semplice
    scurimento/schiarimento lineare."""
    r, g, b, a = base_color
    ramp = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0.5  # 0 = ombra, 1 = luce
        factor = 0.4 + 0.9 * t  # da 40% a 130% di luminosità circa
        nr, ng, nb = r * factor, g * factor, b * factor
        if hue_shift:
            if t < 0.5:  # verso ombra: aggiungi blu/viola
                shift = (0.5 - t) * 2
                nb += 40 * shift
                nr -= 10 * shift
            else:  # verso luce: aggiungi giallo/arancio
                shift = (t - 0.5) * 2
                nr += 30 * shift
                ng += 15 * shift
        clamp = lambda v: max(0, min(255, int(v)))
        ramp.append((clamp(nr), clamp(ng), clamp(nb), a))
    return ramp
