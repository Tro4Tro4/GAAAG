---
name: pixel-adventure-assets
description: Usa questa skill ogni volta che si tocca la grafica di AGGGA - disegnare, generare, modificare o verificare pixel art, sprite, fogli di animazione, cicli di camminata, sfondi di stanza, fondali, oggetti, icone di inventario, hotspot, cursori, HUD o elementi di interfaccia. Attivala anche per richieste generiche ("disegnami un personaggio", "serve lo sfondo della stanza", "fai le icone"), quando un'immagine generata con uno strumento esterno va misurata, ritagliata e portata nel progetto, quando si sceglie o si deriva una tavolozza, e quando un asset grafico va controllato prima di committarlo.
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
- **Griglia/risoluzione base** per elementi in pixel art: tipica 16x16, 32x32, 48x48, 64x64 px per personaggi/oggetti; per sfondi, in questo progetto le dimensioni della stanza: 320x180, o un multiplo della larghezza
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

Le librerie di appoggio sono due, e servono a cose diverse:

- `scripts/pixel_helpers.py` — **per disegnare**: canvas a griglia, outline,
  dithering, upscaling nearest-neighbor, composizione di sprite sheet.
- `scripts/pxlib.py` — **per misurare**: conversioni Oklab e HSV, lettura e
  scrittura di palette, quantizzazione. La usano `palette.py` e `qa_check.py`.

Importa la prima così:

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
- **Le librerie non sono installate di default** in questo ambiente:
  `pip install pillow numpy` prima di eseguire qualunque cosa. Pillow serve a
  disegnare, numpy a misurare (`palette.py`, `qa_check.py`). Nient'altro: il
  k-means è scritto a mano in venti righe apposta per non tirarsi dietro
  scikit-learn, che sono centinaia di megabyte da installare su un telefono.

## Step 4 — Deriva la tavolozza, non inventarla

Vale per qualunque cosa vada dentro una stanza che ha gia' uno sfondo. La
regola del progetto e' che la tavolozza dello sprite si **deriva** da quella
dello sfondo; `palette.py` la rende meccanica invece che a occhio, che e' dove
si sbaglia — due verdi diversi sembrano lo stesso verde finche' non stanno
accanto.

```bash
python .claude/skills/pixel-adventure-assets/scripts/palette.py \
    extract assets/backgrounds/bg_lobby.png -n 24 --out /tmp/lobby.hex
python .claude/skills/pixel-adventure-assets/scripts/palette.py \
    swatch /tmp/lobby.hex -o /tmp/lobby_swatch.png
```

Si disegna scegliendo da li'. Le tinte si possono schiarire e scurire — un
personaggio non e' fatto degli stessi colori del muro — ma restano nella
famiglia. Quanto si e' liberi lo dice `qa_check.py` allo Step 6.

## Step 5 — Nomina e organizza i file

Convenzione di naming utile per un motore di gioco:
- `char_<nome>_<animazione>_sheet.png` (es. `char_luca_walk_sheet.png`)
- `bg_<nome-scena>.png`
- `item_<nome-oggetto>.png`
- `ui_<elemento>.png`

Se generi più asset correlati (es. un intero set per una scena: sfondo + 2 oggetti + 1 personaggio), organizzali in una singola cartella di output prima di presentarli.

## Step 6 — Verifica prima di committare

`qa_check.py` controlla quello che in un PNG non si vede ma in gioco si'. Esce
con codice 1 se qualcosa fallisce, quindi si puo' mettere in uno script.
**Passaci ogni asset prima di committarlo**, come si fa gia' con `gdparse` per
gli script.

```bash
python .claude/skills/pixel-adventure-assets/scripts/qa_check.py \
    assets/sprites/char_lino_sheet.png --profile sheet \
    --palette-from assets/backgrounds/bg_lobby.png
```

| Profilo | Per cosa | Cosa guarda in piu' |
|---|---|---|
| `sheet` | foglio personaggio | griglia 96x396, **piedi ancorati al fondo di ogni cella**, celle attese non vuote, bob solo nelle camminate |
| `sprite` | prop, oggetto, `StateVisual` | alpha binaria, altezza entro la figura intera |
| `shadow` | ombra di contatto | alpha a pochi livelli invece che binaria |
| `background` | sfondo di stanza | `.png`, altezza 216, larghezza multipla di 384 |

Su tutti: formato del file, **un pixel = un pixel** (intercetta lo sprite
disegnato grande e rimpicciolito), numero di colori, e con `--palette-from` la
parentela con la tavolozza della stanza.

Due controlli meritano una parola perche' hanno trovato cose che l'occhio non
trova:

- **Piedi ancorati.** In ogni cella l'ultima riga di pixel opachi deve essere
  l'ultima riga della cella. Un frame con i piedi un pixel piu' su fa
  sobbalzare il personaggio a ogni passo, e guardando il PNG da fermo non si
  vede niente.
- **Tavolozza derivata.** La distanza si misura in Oklab, dove la distanza
  euclidea approssima la differenza percepita. La soglia (0,16) non e' di
  gusto: e' misurata sugli asset gia' approvati contro dei colori volutamente
  estranei, e i numeri stanno in testa a `qa_check.py`. Se cambia lo sfondo di
  riferimento va rimisurata.

Quando un controllo fallisce, la prima domanda e' **se ha ragione lo strumento
o l'asset**: durante la taratura entrambi i falsi positivi trovati (il
contorno che sfora di 1 px, l'ombra semitrasparente per scelta) erano difetti
del controllo, non del disegno. Verifica prima di correggere il PNG.

## Vincoli di AGGGA (leggere prima di disegnare qualunque cosa)

Questa skill è generica; il progetto ha già preso decisioni che la restringono.
Sono in `CLAUDE.md`, e queste sono quelle che toccano la grafica.

- **Risoluzione base 320×180**, finestra 4× = 1280×720. Un personaggio a figura intera in
  scena è alto **40 unità di gioco** — decisione presa guardando 27, 40 e 54
  affiancate, registrata in `CLAUDE.md`. Uno sprite si disegna quindi su una
  griglia alta 40 px (tipicamente 24×40 o 32×40) e si usa a scala 1:1 nel gioco,
  non si scala: il gioco disegna già a bassa risoluzione.
- **Il filtro texture del progetto è `Nearest`** (`default_texture_filter=0` in
  `project.godot`). I PNG vanno esportati alla dimensione logica vera, senza
  upscaling: se ne serve uno ingrandito per mostrarlo all'utente, è
  un'anteprima, non l'asset.
- **Lo stile del progetto è quello ibrido** descritto in
  `references/hybrid-style-guide.md`: **personaggi, oggetti e figure degli
  hotspot in pixel art netta, sfondi dipinti a piena risoluzione.** È una
  decisione presa e registrata in `CLAUDE.md`, non una proposta. Le sette icone
  dei verbi, che sono SVG, non sono più un'eccezione: sono lo strato morbido,
  come gli sfondi.
- **La regola che tiene insieme i due strati: un pixel di texture è un'unità di
  gioco.** Un personaggio alto 40 unità si disegna alto 40 pixel e si usa a
  `scale = 1`. Ogni pixel di texture diventa così esattamente
  *fattore-di-finestra* pixel veri, che è sempre un intero, quindi sempre un
  blocco netto. **Non disegnare un personaggio più grande per poi rimpicciolirlo
  in scena**: a 0,5 di scala su uno schermo 5× un pixel diventa 2,5 pixel veri e
  alcuni escono grandi il doppio degli altri. È l'errore che questa guida chiama
  "fattori non interi", visto dal lato di questo progetto.
- **Anche gli sfondi sono pixel art**, e la regola qui sopra vale per loro senza
  eccezioni: si disegnano alle dimensioni della stanza — 320×180 per una stanza
  di una schermata, 640×180 per il corridoio largo due — e in scena vanno su uno
  `Sprite2D` a `scale = 1`, `centered = false`, posizione (0, 0) e nessun
  override di filtro. Erano 1920×1080 a `scale = 0.2` con filtro `Linear`
  finché erano dipinti: quella strada è stata revocata perché uno sprite netto
  appoggiato su un fondo morbido galleggia, e l'ombra di contatto non è bastata
  a rimediare.
- **`Nearest` senza eccezioni**, adesso: nel progetto l'unico override a
  `Linear` che resta è sulle sette icone dei verbi, che sono SVG.
- **Il dithering va ai bordi delle fasce, mai su tutta la superficie.** A questa
  risoluzione un gradiente dithered per intero si legge come una zanzariera: si
  quantizza in fasce piatte e si mescola solo la striscia dove due si toccano.
  E **niente rumore casuale prima di quantizzare** — vicino a un confine sparge
  pixel isolati e si legge come sporco. La grana si dà in forme: scrostature,
  macchie, crepe.
- **Una porta in un muro visto di fronte incontra il pavimento dove lo incontra
  il muro.** Disegnata con la soglia più in basso, il telaio si chiude sotto il
  battiscopa e copre il pavimento vicino: smette di essere un'apertura e diventa
  un armadietto appoggiato davanti. Vale per qualunque apertura nel fondale, ed è
  stato sbagliato due volte sulle due facce della stessa porta: **si controlla
  ogni volta**, e la verifica è che la soglia valga esattamente `FLOOR_Y`.
- **La striscia di dithering fra due fasce va tenuta stretta**: `width=0.18` e non
  il default. Con una pozza di luce, il cui gradiente è lento, una striscia larga
  copre decine di unità e si legge come sporco invece che come transizione.
  Misurabile: contando i pixel diversi da entrambi i vicini orizzontali, un
  fondale sano sta sotto il 10%.
- **Un fondale può raccontare una conseguenza, non può stare al posto della cosa
  che cambia.** La lama di luce sul pavimento davanti a una porta aperta è una
  conseguenza e sta bene dipinta; il battente è la cosa che cambia e va disegnato
  come sprite, in due stati. Dipinto chiuso nel fondale, dà una porta chiusa da
  cui esce la luce.
- **Quello che si deve toccare va disegnato dove una mano arriva.** Le mani di un
  personaggio alto 40 stanno una ventina di unità sopra i suoi piedi, e i piedi
  non possono salire sopra il limite della navmesh: quindi un oggetto con cui si
  interagisce non può stare più di una decina di unità sopra `linea_pavimento − 20`.
  Più in alto è scenografia, e va bene solo se il verbo è Guarda. È la stessa
  verifica dell'altezza della maniglia, applicata a fessure, sportelli e leve.
- **Le zone che un fondale lascia libere per uno sprite tengono fuori i
  *dispositivi*, non la superficie.** La regola "un elemento dipinto dietro uno
  sprite è una collisione che il fondale non vede arrivare" vale per una cosa
  appesa al muro che finirebbe nascosta — non per il muro, il tubo o il pavimento
  su cui lo sprite è montato. Soppressa anche la superficie, attorno a una sagoma
  rotonda resta un **rettangolo di fondo nudo** che si legge come un bordo
  incollato addosso. In pratica: la base va disegnata sempre (assegnazione
  diretta), e solo i dettagli aggiunti passano dal filtro.
- **Un'ombra di contatto si ricava dall'alpha dello sprite, non dal suo
  rettangolo.** Disegnata sul rettangolo sporge oltre la sagoma e diventa proprio
  il bordo che doveva togliere. Se l'alpha non è disponibile, meglio nessuna
  ombra: il contorno scuro che ogni sprite porta già fa da separazione.
- **Un layer di parallasse in pixel art striscia.** Si muove a una frazione della
  telecamera, quindi finisce a coordinate frazionarie e con `Nearest` la griglia
  di campionamento slitta. Agganciarlo a unità intere scambia lo strisciamento
  con uno scatto. Il progetto non ne usa: la profondità la porta il disegno.
- **Nello sfondo va solo ciò che è fermo, muto e sempre dietro**: muro,
  pavimento, battiscopa, telaio della porta, sporco e usura. Restano sprite
  separati tre categorie — quello che cambia con lo stato del gioco (la luce
  sotto una porta: è un `StateVisual`, e va disegnata con il **bordo netto**,
  perché è informazione e non atmosfera), quello che si ordina in Y (se il nodo
  sta dentro la navmesh, un personaggio ci passa dietro), e quello che porta
  scritte (i testi contano per gli enigmi e vanno disegnati, non generati). La
  regola completa, con i motivi, è in `CLAUDE.md`.
- **Una tavolozza madre e una sola direzione di luce per stanza**, condivise fra
  sfondo e sprite: la tavolozza ridotta del personaggio si **deriva** da quella
  dello sfondo, non si inventa a parte. È la parte che decide se i due stili
  convivono o litigano. Non è più una regola da applicare a occhio: `palette.py`
  la estrae (Step 4) e `qa_check.py --palette-from` verifica che lo sprite non
  se ne sia allontanato (Step 6).
- **Ombra di contatto sotto i piedi** dei personaggi: uno sprite netto su uno
  sfondo morbido galleggia. Va come figlio del nodo `Visual`, disegnata prima del
  corpo.
- **Conflitto noto e ancora aperto**: la prospettiva delle stanze scala la figura
  del personaggio di un fattore continuo (`depth_top_scale`/`depth_bottom_scale`,
  oggi 0,78–1,1), e questo rompe la regola "un pixel di texture, un'unità". Sta
  in "Decisioni ancora aperte" di `CLAUDE.md` e si decide guardando il primo
  sprite vero sul dispositivo. Fino ad allora: **disegna a 1:1 e non
  preoccuparti della scala**, ma sappi che è lì.
- **Il nodo di un oggetto sta dove l'oggetto tocca il pavimento**, non al suo
  centro: l'Y-sorting guarda la Y del nodo. Uno sprite di scena va quindi
  disegnato con l'origine ai piedi, e la figura va messa come **figlio**
  dell'hotspot, non come fratello.
- **I personaggi hanno quattro direzioni** (giù, sinistra, destra, su) e tre
  stati (fermo, cammina, parla). `PlayerCharacter._refresh_visual()` ne compone
  il nome dell'animazione e lo passa all'`AnimatedSprite2D`.
- **Il formato del foglio è deciso e implementato**: nove animazioni chiamate
  `<stato>_<direzione>` con gli stati `idle`, `walk`, `talk` e le direzioni
  `down`, `side`, `up`; `walk` ha quattro fotogrammi, `talk` due, `idle` uno.
  Il sinistra è il destra ribaltato con `flip_h`, quindi **niente di asimmetrico
  addosso a un personaggio**. Celle 24×44, corpo alto 40 con i piedi sull'ultima
  riga. Non disegnare un foglio a mano: `tools/make_character_sheets.py` lo
  produce **e scrive lo `SpriteFrames`**, e le due cose devono restare una sola.
- **Vincolo IP**: i contenuti visivi non fanno eccezione. Prima di committare
  arte con soggetti riconoscibili, passa dalla skill `vincolo-ip`.

## Note di qualità

- Pixel art vera: niente anti-aliasing automatico di libreria sui bordi dei pixel logici; i bordi devono restare netti. L'anti-aliasing "manuale" (pixel intermedi mirati) è una tecnica valida descritta nella reference, ma va applicato deliberatamente, non lasciato al resize automatico.
- Quando fai upscaling per l'anteprima, usa sempre nearest-neighbor (mai bilinear/bicubic), altrimenti si perde l'effetto pixel art.
- Mantieni una palette coerente fra asset dello stesso set (stesso personaggio/scena), per evitare che elementi sembrino "attaccati" da progetti diversi.
