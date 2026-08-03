# Prompt per i generatori

## Il principio che cambia tutto

**Non chiedere al generatore la pixel art finale.** Nessun modello di diffusione
sa allineare i pixel a una griglia: produce immagini *che assomigliano* a pixel
art, con blocchi di dimensione irregolare, anti-aliasing e migliaia di colori.

Il flusso corretto e':

> chiedi un'**illustrazione a palette limitata, contrasto netto e forme leggibili**
> a **2x o 3x** la risoluzione nativa → `pixelate.py` impone griglia e palette →
> rifinitura a mano

Chiedere "640x360 pixel art" produce quasi sempre un'immagine peggiore, perche' il
modello cerca di simulare i pixel e aggiunge un pattern di rumore che poi va
combattuto in fase di downscale.

Risoluzioni da chiedere: **1280x720** (x2, migliore fedelta' al downscale) o
**1920x1080** (x3, piu' dettaglio ma piu' rumore da collassare).

## Struttura del prompt in sei blocchi

Sempre in questo ordine. I modelli pesano di piu' l'inizio del prompt.

```
1. TIPO       che asset e' e come e' inquadrato
2. SOGGETTO   contenuto concreto, elencato per piani
3. LUCE       key / fill / practical, con direzione e temperatura
4. PALETTE    rampe e limiti
5. TECNICA    il blocco di ancoraggio dello stile (sotto, invariato)
6. NEGATIVI   cosa escludere
```

Scrivere i prompt **in inglese**: tutti i modelli rendono meglio, anche quelli
multilingua.

## Blocco di ancoraggio dello stile (copiare invariato)

```
STYLE ANCHOR
16-bit era hand-crafted pixel art, side-on diorama staging, orthographic front
view, single centered vanishing point, horizon at 47% height. Strictly limited
palette of 32 desaturated colors, no color above 50% saturation, overall mid-tone
value around 32%, only the light source reaching bright values. Hard-edged pixel
clusters, crisp edges, zero anti-aliasing, zero gradients, no bloom. Selective
dark outlines on interactive props only, no uniform black outlines. Dense detail
concentrated in the eye-level band, calm flat surfaces in floor and ceiling. Dark
near-silhouette foreground framing elements at the left and right edges. Cohesive
lighting with warm key and cool ambient fill.
```

## Blocco negativi (copiare invariato)

```
NEGATIVE
3d render, blender, octane, photorealistic, photograph, blur, depth of field,
bloom, glow, soft shadow, smooth gradient, anti-aliasing, jpeg artifacts,
painterly brushstrokes, watercolor, oil painting, vector art, flat design,
cel shading, oversaturated, neon magenta, pastel, isometric, top-down, bird's eye,
tilted camera, dutch angle, fisheye, wide angle distortion, text, letters,
watermark, signature, ui, hud, health bar, inventory bar, letterbox bars, frame,
border, anime face, chibi, cluttered, busy, uniform detail
```

---

## Flusso "blockout first" (composizione sotto controllo)

Il modo professionale per non farsi dettare la composizione dal modello:

1. Dipingere a mano un **blockout** a 640x360: solo blocchi piatti di colore che
   rappresentano i 5 livelli (vedi `backgrounds.md`), 8-10 colori, 10 minuti di
   lavoro. Serve a fissare punto di fuga, spazio libero per il personaggio,
   posizione degli hotspot.
2. Ingrandirlo a 1280x720 con nearest.
3. Usarlo come base:
   - Flux/SD: ControlNet (depth o scribble, weight 0.5-0.7) oppure img2img con
     denoise 0.6-0.75
   - Midjourney: come immagine in prompt con `--iw 1.5`
   - Gemini/DALL·E: allegarlo e chiedere "keep this exact layout and camera"
4. Generare 4-8 varianti, scegliere, pixelare, rifinire.

Con il blockout il tasso di scarto crolla: la composizione e' tua, il modello
fornisce solo la resa.

---

## Midjourney

Formato:

```
/imagine <TIPO+SOGGETTO+LUCE+PALETTE>, <STYLE ANCHOR> --ar 16:9 --style raw
--stylize 120 --sref <url_immagine_stile> --sw 200 --no 3d, blur, gradient,
text, watermark, isometric, photorealistic
```

Parametri che contano:
- `--ar 16:9` — sempre, per i fondali
- `--style raw` — riduce l'abbellimento automatico, indispensabile qui
- `--stylize 80-150` — valori bassi: obbedisce al prompt invece di "fare arte"
- `--sref <url> --sw 150-300` — riferimento di **stile**. Lo `--sw` va da 0 a 1000,
  default 100; per bloccare uno stile pixel servono valori alti
- `--cref <url> --cw 80-100` — riferimento di **personaggio**, per la coerenza tra
  scene di uno stesso personaggio
- `--iw 1.5-2` — peso dell'immagine in prompt, per il blockout
- `--no ...` — Midjourney non ha un campo negativo separato, si usa `--no`

Nota: Midjourney cambia sintassi e range fra le versioni. Verificare i parametri
correnti su `docs.midjourney.com` prima di impostare uno script di produzione.

Limiti pratici: e' il piu' bravo sull'atmosfera dei fondali e il piu' testardo
sulla composizione. Ottimo con il blockout, frustrante senza. Non usarlo per gli
sprite: reinventa le proporzioni a ogni generazione.

---

## Flux / Stable Diffusion (locale o ComfyUI)

E' l'opzione che da' controllo reale, quindi quella da preferire per la produzione.

Impostazioni di partenza:

| Parametro | Flux.1 dev | SDXL |
|---|---|---|
| Risoluzione | 1280x720 | 1216x704 (poi resize a 1280x720) |
| Step | 25-30 | 30-35 |
| CFG / guidance | 3.0-3.5 | 6.0-7.0 |
| Sampler | euler / dpmpp_2m | dpmpp_2m karras |
| Negativi | poco efficaci, insistere sui positivi | molto efficaci, usare il blocco intero |

Componenti da aggiungere:
- **LoRA pixel art**: uno solo, peso 0.6-0.8. Sopra 0.9 impasta i dettagli.
  Con due LoRA di stile insieme il risultato e' sempre peggiore della somma.
- **ControlNet** dal blockout: `depth` per la profondita', `scribble`/`lineart`
  per gli spigoli architettonici, weight 0.5-0.7, end_percent 0.7 (lasciare
  libera la parte finale del campionamento migliora la texture).
- **IPAdapter** con l'immagine di ancoraggio stilistico, weight 0.4-0.6: e' il
  modo migliore per la coerenza fra decine di fondali.
- **img2img** per le varianti (giorno/notte, stanza prima/dopo): denoise 0.35-0.45
  partendo dal fondale gia' approvato. Sopra 0.5 cambia troppo.

Non usare upscaler: qui si scende, non si sale.

## Gemini (Nano Banana) / DALL·E

Modelli conversazionali: il punto di forza e' l'**editing iterativo** e la
capacita' di tenere fermo un soggetto fra richieste diverse. Il prompt e' prosa,
non lista di tag.

Ottimi per:
- **set di icone in un colpo solo**: "Generate a 4x3 grid on a neutral grey
  background: 12 everyday modern objects (keys, cracked phone, badge, USB stick,
  mug, receipt, screwdriver, flashlight, pill bottle, wallet, train ticket,
  charger). Every object seen from the same three-quarter angle from above, 30
  degrees, lit from the upper left at 45 degrees, same desaturated limited
  palette, chunky readable shapes, thick dark outline, no anti-aliasing, no text,
  no labels." — poi si taglia la griglia e si pixela ogni cella a 32x32.
- **varianti di un asset approvato**: allegare l'immagine e chiedere la modifica
  puntuale ("same room, same camera, same palette, now at night with only the
  desk lamp lit").
- **correzioni**: "remove the character, keep everything else identical" per
  ricavare il fondale pulito sotto un oggetto.

Debolezza: tendono a rendere tutto piu' pulito e piu' chiaro del richiesto. Nel
prompt insistere su "dark, low saturation, most of the image in shadow".

---

## Esempi completi

### Fondale: ufficio open space di notte

```
Wide establishing background for a point-and-click adventure game, side-on
diorama staging, empty open-plan office at night.
FOREGROUND: dark near-silhouette of an office chair and a partition wall at the
left edge, a hanging cable at the right edge.
MIDGROUND: two rows of desks receding toward the center, one monitor glowing,
a coffee mug, scattered papers, a filing cabinet with one drawer ajar.
BACKGROUND: glass partition and a dark corridor, an exit sign, a large window
with a distant city skyline.
LIGHT: key from overhead fluorescent tubes, cool, from above; cool ambient fill;
practical light from the single glowing monitor and the exit sign.
PALETTE: desaturated cool concrete greys, dark ink shadows, muted denim blues,
teal screen glow as the only accent.
<STYLE ANCHOR>
<NEGATIVE>
```
→ genera a 1280x720 → `pixelate.py --native 640x360 --palette master-modern.hex
--dither bayer4`

### Sprite: personaggio giocabile, posa neutra

```
Single character sprite for a pixel art adventure game, full body, standing
neutral idle pose, facing the viewer, feet flat on the ground, arms relaxed at
the sides. Adult woman in her thirties, short dark hair, rust-colored work jacket
over a grey shirt, dark jeans, worn sneakers, a canvas bag strap across the chest.
Centered on a plain flat magenta background, no shadow, no ground.
LIGHT: soft key from the upper right, cool ambient fill.
PALETTE: 20 colors maximum, desaturated, rust accent as the only saturated note.
Chunky readable silhouette, 1 pixel dark outline all around the figure, three
shading tones per material, crisp edges, no anti-aliasing, no gradients.
<NEGATIVE>, background, scenery, multiple characters, close-up, portrait
```
→ `pixelate.py --native 96x144 --alpha-threshold 128` (poi ritaglio a 64x96 e
rifinitura a mano; il magenta si converte in trasparenza)

### Icona inventario singola

```
Single inventory icon for a pixel art adventure game: a cracked smartphone,
screen off, seen from a three-quarter angle from above at 30 degrees, lit from
the upper left at 45 degrees, on a plain flat magenta background. Chunky
simplified shape, thick dark outline, three shading tones, 10 colors maximum,
desaturated palette, crisp hard edges, no anti-aliasing, no gradient, no text.
```
→ `pixelate.py --native 32x32 --alpha-threshold 128 --palette master-modern.hex`

---

## Coerenza fra centinaia di asset

Cinque strumenti, in ordine di efficacia:

1. **Immagine di ancoraggio**: il primo fondale approvato diventa il riferimento
   di stile (`--sref`, IPAdapter, allegato). Non cambiarlo mai a metà progetto.
2. **Palette master unica**, applicata via `pixelate.py` a ogni singolo asset.
   Questa da sola risolve il 70% dei problemi di coerenza.
3. **Key light dichiarata** per ogni scena, scritta nel JSON dell'asset.
4. **Generare in batch**: 4 fondali nella stessa sessione con lo stesso prompt di
   ancoraggio sono piu' coerenti di 4 fondali generati in giorni diversi.
5. **Style bible**: un PNG unico che affianca il fondale di riferimento, il
   personaggio principale, tre icone e la palette. Si guarda prima di ogni nuova
   sessione di produzione.
