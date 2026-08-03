---
name: pixelart-adventure
description: Produce asset di pixel art di livello professionale per un'avventura grafica punta-e-clicca in ambientazione contemporanea, a risoluzione nativa 640x360 con palette master coerente. Da usare ogni volta che si parla di fondali, backgrounds, sprite, personaggi, sprite sheet, cicli di camminata, icone di inventario, oggetti, HUD, interfaccia, cursori o font bitmap per un gioco in pixel art; ogni volta che si chiedono prompt per Midjourney, Flux, Stable Diffusion, ComfyUI, Gemini/Nano Banana o DALL-E per generare grafica di gioco; e ogni volta che un'immagine generata va convertita in vera pixel art, quantizzata su una palette, controllata o assemblata in uno sprite sheet. Usarla anche quando la richiesta e' generica ("fammi uno sfondo per il gioco", "serve lo sprite del protagonista", "genera le icone dell'inventario") perche' contiene le specifiche numeriche, il ricettario materiali e gli script di pipeline che garantiscono coerenza fra centinaia di asset.
---

# Pixel art per avventura grafica contemporanea

Skill di produzione: specifiche misurabili, prompt per i generatori, script di
conversione e controllo qualita'. L'obiettivo e' la coerenza da studio su
centinaia di asset, non la singola immagine fortunata.

## Le specifiche in una schermata

| Voce | Valore |
|---|---|
| Risoluzione nativa | **640 x 360** (16:9, scala a interi verso 720p/1080p/1440p) |
| Presentazione | **x3 nearest-neighbor** = 1920x1080 |
| Griglia | **8 px** base, 16 px architettonica |
| Palette | `assets/palettes/master-modern.hex`, **48 colori**, 9 rampe da 5 |
| Saturazione | tetto **HSV <= 50** per colore · **mediana 20-38 pesata sull'area** · max 12% dei pixel sopra S 50 |
| Valore | 8-88, **mediana di scena 25-40**, max 2 colori sopra V 80 |
| Colori per asset | fondale 32-48 · sprite 16-24 · icona max 12 |
| Rampe per asset | **max 5** |
| Altezza adulto | **72 px** in cella 64x96, ancoraggio bottom-center |
| Dithering | solo Bayer 2x2/4x4, solo superfici > 48x48 px, mai su sprite/icone |
| Anti-aliasing | solo manuale, max 1 px, **mai** sulla silhouette degli sprite |
| Contorni | selective outline; contorno completo 1 px solo su sprite e icone |

Un pixel logico = un pixel del file. Nessun asset viene mai salvato ingrandito.

## Come lavorare

### 1. Capire di che asset si tratta e leggere il riferimento giusto

| Richiesta | Leggere |
|---|---|
| fondale, ambiente, scena, location, livelli, walkmask, hotspot | `references/backgrounds.md` |
| personaggio, sprite, NPC, animazione, camminata, ritratto, sprite sheet | `references/characters.md` |
| oggetto, icona inventario, HUD, interfaccia, cursore, font, dialoghi | `references/objects-ui.md` |
| prompt, Midjourney, Flux, SD, ComfyUI, Gemini, DALL-E, coerenza fra asset | `references/prompting.md` |
| conversione, quantizzazione, QA, organizzazione file, engine | `references/pipeline.md` |
| dubbi su colore, luce, materiali, errori tipici | `references/style-spec.md` |

`references/style-spec.md` e' la fonte di verita' su colore, luce, contorni,
dithering, densita' di dettaglio e ricettario materiali. In caso di conflitto fra
file, vince quello.

### 2. Dichiarare le scelte prima di produrre

Per ogni asset nuovo, mettere per scritto **tre righe** e non cambiarle piu':

```
SOTTOPALETTE:  3 rampe dominanti + 1 accento + ink
KEY LIGHT:     direzione, angolo, temperatura
FUNZIONE:      cosa deve fare il giocatore guardando questa immagine
```

Sembra burocrazia ed e' invece il singolo intervento che piu' aumenta la
coerenza. La terza riga in particolare: un fondale di avventura grafica e'
design di livello, non un quadro. Se non si sa dove deve guardare il giocatore,
l'immagine verra' bella e inutilizzabile.

### 3. Generare, convertire, controllare

Il flusso completo e le ragioni di ogni passaggio sono in `references/pipeline.md`.
In breve:

```bash
# una volta per progetto
python scripts/palette.py build --out assets/palettes

# blockout a mano (640x360) -> generazione a 1280x720 -> conversione
python scripts/pixelate.py render/scena.png -o out/bg/scena_bg \
    --native 640x360 --palette assets/palettes/master-modern.hex \
    --dither bayer4 --preview 3

# controllo: esce 1 se qualcosa non rispetta le specifiche
python scripts/qa_check.py out/bg/scena_bg.png --native 640x360 \
    --palette assets/palettes/master-modern.hex --grid 8
```

**Non chiedere mai al generatore la pixel art finale a 640x360.** I modelli di
diffusione non allineano i pixel a una griglia: producono immagini che
*assomigliano* a pixel art. Si chiede un'illustrazione a palette limitata e
contrasto netto a 2x o 3x, poi `pixelate.py` impone griglia e palette. Il
dettaglio e' in `references/prompting.md`, incluso il blocco di ancoraggio dello
stile e i negativi da copiare invariati.

### 4. Rifinire a mano

Lo script porta l'immagine dentro le specifiche; la rifinitura la porta dentro il
gioco. Sono 45-90 minuti per fondale e non sono opzionali: spigoli
architettonici, occlusione ambientale, pixel orfani, jaggies, volti e mani.
Checklist ordinata in `references/pipeline.md`.

Aspettative realistiche da comunicare subito: **l'AI e' brava sui fondali,
mediocre sugli sprite, inutile sull'animazione.** Un ciclo di camminata a 72 px
si anima a mano.

## Script

Tutti in `scripts/`, richiedono `numpy` e `Pillow` (`palette.py extract` richiede
anche `scikit-learn`). Ognuno risponde a `--help`.

| Script | Cosa fa |
|---|---|
| `palette.py` | `build` genera la palette master con hue-shifting · `extract` ricava una palette da un'immagine · `swatch` esporta un PNG di controllo |
| `pixelate.py` | render AI → pixel art nativa reale: crop al rapporto esatto, downscale BOX, quantizzazione in Oklab sulla palette, dithering Bayer opzionale, anteprima nearest |
| `qa_check.py` | verifica risoluzione, griglia, upscale mascherati, numero di colori, colori fuori palette, residui di anti-aliasing, alpha binaria, limiti di saturazione e valore. Esce 1 se qualcosa fallisce: usabile in uno script di build |
| `spritesheet.py` | assembla i frame in uno sheet a griglia fissa con ancoraggio coerente + JSON dei metadati per l'engine |

La quantizzazione usa **Oklab** e non sRGB perche' in Oklab la distanza
euclidea approssima la differenza percepita: le ombre non si impastano e le
tinte non slittano.

## Deliverable attesi

**Fondale**: `_bg.png` · `_fg.png` (primo piano con alpha) · `_walk.png`
(area percorribile) · `_light.png` opzionale · `.json` con hotspot, uscite,
sottopalette e key light.

**Personaggio**: sprite sheet a griglia + JSON delle animazioni + ritratti 96x96
+ sprite d'ombra separato.

**Icone**: 32x32 RGBA, alpha binaria, max 12 colori, angolo di vista e direzione
di luce identici su tutta la collezione.

**UI**: cornici 9-slice a 8 px, cursori 16x16, font bitmap + metriche.

## Cosa non fare

- Salvare asset ingranditi (`qa_check.py` lo rileva dai blocchi ripetuti).
- Superare le 5 rampe per asset: e' la causa principale dell'aspetto "sporco".
- Usare nero puro per i contorni: si usa `ink-1`/`ink-2` o il locale scurito.
- Rampe senza hue-shift: risultano morte, di plastica.
- Dithering dentro gli sprite o su oggetti piccoli.
- Anti-aliasing sulla silhouette esterna di uno sprite: sfarfalla in movimento.
- Muovere gli sprite a coordinate frazionarie nell'engine.
- Riempire tutto di dettaglio: serve almeno il 25% di superficie calma o l'occhio
  non trova il soggetto.

## Una nota sui riferimenti visivi

Uno stile grafico non e' protetto da copyright, i singoli asset si'. Quando si
parte da uno screenshot di un gioco esistente, si usa per **derivare specifiche
numeriche** (numero di colori, limiti di saturazione, staging, densita' di
dettaglio) e si autora una palette e un repertorio propri — che e' esattamente
cosa fa questa skill. Non si ricalcano ne' si rigenerano i suoi asset,
personaggi o ambienti.
