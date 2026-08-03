---
name: pixel-adventure-assets
description: Genera asset grafici per avventure grafiche (point-and-click) - personaggi/sprite pixel art animati, sfondi di scena, oggetti/inventory item, ed elementi UI (dialoghi, cursori, finestre) - producendo file PNG e sprite sheet reali via codice Python/Pillow, non solo prompt testuali. Usa questa skill ogni volta che l'utente chiede di disegnare, creare o generare pixel art, sprite, walk cycle, sfondi di gioco, asset 2D per un'avventura grafica, un point-and-click, o un mix di stile pixel art retro con grafica 2D moderna (sfondi puliti/vettoriali/painterly abbinati a personaggi in pixel art). Attivala anche per richieste più generiche come "disegnami un personaggio in pixel art" o "crea uno sfondo per la mia scena di gioco", anche se non viene nominata esplicitamente la parola "skill".
---

# Pixel Adventure Assets

Skill per produrre asset grafici reali (file PNG/sprite sheet) per avventure grafiche in stile point-and-click, generati via codice (Pillow/PIL), non semplici prompt per generatori di immagini esterni.

Copre quattro famiglie di asset, spesso combinate nello stesso progetto:
1. **Personaggi/sprite animati** (idle, walk cycle, talk, pick-up, ecc.)
2. **Sfondi/scene** (ambientazioni statiche, con o senza layer di parallasse)
3. **Oggetti/inventory item** (icone raccoglibili, hotspot)
4. **UI** (finestre di dialogo, cursori, box inventario, bottoni)

Lo stile NON è fisso: va chiarito ogni volta con l'utente (vedi sotto), perché richieste diverse possono volere pixel art pura a bassa risoluzione, oppure un ibrido "personaggi pixel art su sfondi 2D moderni" (stile molto usato in avventure grafiche indie contemporanee, es. sfondi painterly/vettoriali ad alta risoluzione con sprite a griglia pixel sopra).

## Step 1 — Chiarisci i parametri di stile (se non già dati)

Prima di generare, se l'utente non li ha già specificati, stabilisci (anche assumendo default ragionevoli e dichiarandoli, senza bloccare il lavoro per domande inutili):

- **Tipo di asset**: personaggio/sprite, sfondo, oggetto, UI, o combinazione
- **Griglia/risoluzione base** per elementi in pixel art: tipica 16x16, 32x32, 48x48, 64x64 px per personaggi/oggetti; per sfondi, dimensioni scena tipiche 320x180, 384x216, 640x360 (poi scalate)
- **Palette**: numero di colori (es. 16, 32, palette storiche tipo NES/SNES/PICO-8) oppure palette libera se lo sfondo è "2D moderno"
- **Stile linea/contorno**: outline nero pieno, outline colorato (selective outlining), nessun contorno
- **Fattore di scala export**: upscaling nearest-neighbor (x4, x8...) per l'anteprima/uso finale, mantenendo i bordi netti
- **Ibrido pixel + moderno?**: se sì, vedi `references/hybrid-style-guide.md` per mantenere coerenza visiva tra sprite a bassa risoluzione e sfondi più ricchi

Se la richiesta è ambigua solo su un dettaglio marginale, scegli un default sensato, dichiaralo in una riga, e procedi.

## Step 2 — Consulta le reference tecniche

Prima di scrivere codice di disegno, leggi (se non già in contesto in questa sessione):
- `references/pixel-art-techniques.md` — palette, shading a rampe, dithering, outline selettivo, principi di animazione (contact/passing/high point per i walk cycle)
- `references/hybrid-style-guide.md` — solo se serve combinare pixel art con sfondi in stile 2D moderno/painterly

## Step 3 — Genera con Python + Pillow

Usa `scripts/pixel_helpers.py` come libreria di appoggio (funzioni per canvas a griglia, palette, outline, dithering, upscaling nearest-neighbor, composizione di sprite sheet). Importalo così:

```python
import sys
sys.path.insert(0, '.claude/skills/pixel-adventure-assets/scripts')
from pixel_helpers import PixelCanvas, build_spritesheet, upscale_nearest, apply_outline, ordered_dither
```

Linee guida di codice:
- Disegna sempre su una griglia di pixel logici (es. 32x32) usando `PixelCanvas`, non free-hand ad alta risoluzione: ogni "pixel" logico deve corrispondere a un blocco netto nell'immagine finale.
- Per le animazioni, genera un frame per volta come funzione parametrica (es. `draw_walk_frame(canvas, frame_index)`), poi componi con `build_spritesheet` in una griglia (righe = animazioni, colonne = frame), salvando sia lo sprite sheet unico sia i singoli frame se utile per l'integrazione in un motore (Godot, Unity, ecc.).
- Per gli sfondi "2D moderni", puoi lavorare a risoluzione piena (niente griglia pixel rigida), usando forme piatte, gradienti, layer multipli per il parallasse; se vanno abbinati a sprite in pixel art, applica la palette/color grading finale coerente (vedi hybrid guide) così i due stili non stonano.
- Esporta sempre come PNG con canale alpha (trasparenza) per sprite/oggetti/UI, così sono pronti per l'uso in un motore di gioco.
- I deliverable finali vanno **dentro il progetto**, non in una cartella di
  output: `assets/sprites/`, `assets/backgrounds/`, `assets/ui/`. Da lì entrano
  in git e arrivano sul telefono dello sviluppatore con un `git pull`. I file di
  lavoro e le prove scartate vanno nella cartella scratchpad della sessione, e
  non si committano.
- **Pillow non è installato di default** in questo ambiente: `pip install pillow`
  prima di eseguire qualunque cosa.

## Step 4 — Nomina e organizza i file

Convenzione di naming utile per un motore di gioco:
- `char_<nome>_<animazione>_sheet.png` (es. `char_luca_walk_sheet.png`)
- `bg_<nome-scena>.png`
- `item_<nome-oggetto>.png`
- `ui_<elemento>.png`

Se generi più asset correlati (es. un intero set per una scena: sfondo + 2 oggetti + 1 personaggio), organizzali in una singola cartella di output prima di presentarli.

## Vincoli di AGGGA (leggere prima di disegnare qualunque cosa)

Questa skill è generica; il progetto ha già preso decisioni che la restringono.
Sono in `CLAUDE.md`, e queste sono quelle che toccano la grafica.

- **Risoluzione base 384×216**, finestra 3×. Un personaggio a figura intera in
  scena è alto **circa 26 unità di gioco** — è la dimensione dei segnaposto
  attuali. Uno sprite disegnato su griglia 32×32 o 32×48 è quindi da usare a
  scala 1:1 nel gioco, non da scalare: il gioco disegna già a bassa risoluzione.
- **Il filtro texture del progetto è `Nearest`** (`default_texture_filter=0` in
  `project.godot`). I PNG vanno esportati alla dimensione logica vera, senza
  upscaling: se ne serve uno ingrandito per mostrarlo all'utente, è
  un'anteprima, non l'asset.
- **L'arte del progetto è pixel art.** L'unica eccezione registrata sono le
  sette icone dei verbi, che sono SVG per una ragione tecnica precisa (un badge
  di 24 unità viene disegnato a più di cento pixel veri su un telefono). Lo
  **stile ibrido** descritto in `references/hybrid-style-guide.md` —
  personaggi pixel su sfondi painterly ad alta risoluzione — **contraddice
  quella decisione**: si può proporre, ma va discusso con lo sviluppatore e
  registrato con la skill `registra-decisione`, non adottato di iniziativa.
- **Il nodo di un oggetto sta dove l'oggetto tocca il pavimento**, non al suo
  centro: l'Y-sorting guarda la Y del nodo. Uno sprite di scena va quindi
  disegnato con l'origine ai piedi, e la figura va messa come **figlio**
  dell'hotspot, non come fratello.
- **I personaggi hanno quattro direzioni** (giù, sinistra, destra, su) e tre
  stati (fermo, cammina, parla). Il codice che li consumerà esiste già ed è
  `PlayerCharacter._refresh_visual()`: oggi muove dei poligoni, e il giorno
  degli sprite diventa un nome passato a un `AnimatedSprite2D`.
- **Il formato del foglio è una decisione ancora aperta** (quante pose per
  direzione, se l'idle è animato): sta in "Decisioni ancora aperte" di
  `CLAUDE.md`. Prima di produrre un foglio definitivo va chiusa — con una
  proposta, non a caso.
- **Vincolo IP**: i contenuti visivi non fanno eccezione. Prima di committare
  arte con soggetti riconoscibili, passa dalla skill `vincolo-ip`.

## Note di qualità

- Pixel art vera: niente anti-aliasing automatico di libreria sui bordi dei pixel logici; i bordi devono restare netti. L'anti-aliasing "manuale" (pixel intermedi mirati) è una tecnica valida descritta nella reference, ma va applicato deliberatamente, non lasciato al resize automatico.
- Quando fai upscaling per l'anteprima, usa sempre nearest-neighbor (mai bilinear/bicubic), altrimenti si perde l'effetto pixel art.
- Mantieni una palette coerente fra asset dello stesso set (stesso personaggio/scena), per evitare che elementi sembrino "attaccati" da progetti diversi.
