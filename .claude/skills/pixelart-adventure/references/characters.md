# Personaggi e animazioni

## Scala e proporzioni (canvas 640x360)

| Soggetto | Altezza | Cella sprite | Teste |
|---|---|---|---|
| Adulto medio | **72 px** | 64x96 | ~6,5 |
| Adulto alto / imponente | 78 px | 64x96 | ~6,8 |
| Adolescente | 64 px | 64x96 | ~6,0 |
| Bambino (8-10 anni) | 52 px | 48x64 | ~5,0 |
| Anziano curvo | 66 px | 64x96 | ~6,2 |
| Personaggio seduto | 52 px | 64x96 | — |

La cella e' **piu' grande della figura**: il margine serve per gesti, capelli
mossi, oggetti in mano e per non ritagliare i frame estremi. Il personaggio e'
ancorato in **bottom-center**: il pixel di contatto dei piedi sta sull'ultima
riga della cella, sempre nello stesso punto, in ogni frame di ogni animazione.
Se questo punto oscilla, il personaggio "scivola".

### Anatomia a 72 px

```
y  0-11   testa (11 px; occhi 1-2 px, sopracciglia 1 px, bocca 2-3 px)
y 11-14   collo (3 px)
y 14-38   torso (24 px; spalle 22-24 px di larghezza)
y 38-46   bacino (8 px)
y 46-66   gambe (20 px)
y 66-72   piedi (6 px, il contatto e' l'ultima riga)
```

Proporzioni volutamente **leggermente stilizzate**: testa un po' piu' grande del
reale (6,5 teste invece di 7,5) perche' a questa risoluzione la faccia deve
poter esprimere. Mani a 4-5 px di diametro, altrimenti i gesti non leggono.

## Palette del personaggio

- 4-6 rampe, **16-24 colori totali**, mai piu'.
- Struttura: `skin` (3-4 toni) + capelli (3) + capo superiore (3) + capo inferiore
  (3) + calzature (2-3) + `ink` per il contorno.
- **Contorno 1 px completo** su tutta la silhouette, in `ink-1`/`ink-2` oppure nel
  colore locale scurito di 2 stop. E' cio' che rende lo sprite leggibile su
  qualunque fondale.
- Un colore di identita': ogni personaggio ha un accento cromatico riconoscibile
  a distanza (la giacca ruggine, la sciarpa teal). A 72 px il giocatore riconosce
  i personaggi dal colore, non dal viso.

**Test della silhouette**: riempi lo sprite di nero. Se non capisci chi e' e cosa
sta facendo, la posa va rifatta.

## Direzioni

Si autorano **tre** direzioni, la quarta e' speculare:
`s` (sud, verso lo spettatore) · `n` (nord, di spalle) · `e` (est) — `w` = `e`
specchiata.

Attenzione: se il personaggio ha un elemento asimmetrico (borsa a spalla,
cicatrice, orologio) lo specchio lo sposta di lato. Due opzioni: accettarlo, o
autorare anche `w`. Decidere all'inizio del progetto, non a meta'.

## Set di animazioni per un'avventura grafica

Set minimo giocabile (per direzione, salvo indicazione):

| Animazione | Frame | FPS | Loop | Note |
|---|---|---|---|---|
| `idle` | 4 | 6 | si | respiro: torace +1 px, spalle -1 px ogni 2 frame |
| `idle_blink` | 2 | 8 | no | innesco casuale ogni 3-6 s, solo direzione `s` |
| `walk` | 8 | 12 | si | vedi sotto |
| `talk` | 3 | 8 | si | 3 posizioni bocca; solo `s` ed `e` |
| `gesture` | 4 | 10 | no | mano che indica, per il dialogo |
| `pickup` | 6 | 10 | no | si abbassa, prende, si rialza; ultimo frame = primo di `idle` |
| `use` | 5 | 10 | no | braccio in avanti, tenuta sul frame 3 |
| `turn` | 2 | 12 | no | frame di transizione fra due direzioni; elimina lo scatto |
| `react` | 4 | 10 | no | sorpresa: spalle su, testa indietro di 1 px |
| `sit` / `stand` | 4 | 10 | no | necessarie prima di quanto pensi |

Totale approssimativo: **~110 frame** per un personaggio giocabile completo,
~30 per un NPC secondario (idle + talk + una direzione di walk).

Ritratti per il dialogo: canvas **96x96** (busto), 24-32 colori, 3 varianti di
espressione (neutra, tesa, sorpresa) + 3 posizioni bocca animabili.

## Il ciclo di camminata, in dettaglio

8 frame = 2 passi. Sequenza canonica:

```
frame 0  contact      piede avanti appoggia, gamba dietro estesa, bacino basso
frame 1  down         massima compressione, bacino -1 px, ginocchio flesso
frame 2  pass         gamba libera passa accanto, bacino risale
frame 3  up           massima estensione, bacino +1 px, punta in spinta
frame 4-7            come 0-3 con le gambe invertite
```

Regole che fanno la differenza fra "cammina" e "striscia":

- **Bob del bacino: esattamente +-1 px.** A 72 px, 2 px sono un salto.
- **La testa non si muove piu' di 1 px in verticale** e **0 px in orizzontale**.
  L'occhio segue la testa: se oscilla, il personaggio sembra ubriaco.
- **Braccia in controfase** rispetto alle gambe. Sempre. Anche se il braccio e'
  largo 3 px.
- **Velocita' e passo devono corrispondere**: se il personaggio avanza a 40 px/s
  nativi a 12 fps, sono 3,33 px per frame. Arrotondare a **numeri interi di px
  per frame** (3 o 4) ed allineare la lunghezza del passo disegnato: altrimenti i
  piedi slittano sul pavimento. Formula: `px_per_frame = velocita_px_s / fps`,
  poi `lunghezza_passo_disegnata = px_per_frame * 4`.
- **Mai sub-pixel**: la posizione dello sprite nell'engine va arrotondata a pixel
  nativi interi ogni frame. Il movimento fluido a coordinate frazionarie produce
  sfarfallio, che e' il segnale piu' immediato di pixel art fatta male.

## Ombra a terra

Sprite separato, non disegnato dentro il personaggio: ellisse **24x8 px** in
`ink-1`, applicata dall'engine in moltiplicazione al 45%, oppure dithered Bayer
2x2 se l'engine non supporta il blending. Si schiaccia e si sposta con il bob
del bacino (larghezza -2 px sul frame `down`). Senza ombra il personaggio
galleggia; e' l'aggiunta con il miglior rapporto costo/beneficio dell'intero
pipeline.

## Produzione con un generatore AI

I generatori non producono cicli di animazione coerenti: la figura cambia
proporzioni fra un frame e l'altro. Il flusso che funziona:

1. Generare **una sola posa neutra** (idle, direzione `s`) e rifinirla a mano
   fino a considerarla definitiva. Questo diventa il **modello di riferimento**.
2. Da quella posa ricavare le altre pose con image-to-image / character reference
   a peso alto, **una per volta**, e correggere a mano ogni frame.
3. Le animazioni brevi (`walk`, `idle`) conviene **animarle a mano** partendo
   dallo sprite base: 8 frame di camminata a 72 px sono un lavoro da poche ore
   ed e' l'unico modo per avere un bob di 1 px controllato.
4. Generare un **character sheet** (3 direzioni + 2 espressioni su una griglia)
   come immagine unica aiuta molto la coerenza: si ritaglia dopo.

Il confine pratico: **l'AI e' brava sul fondale, mediocre sullo sprite, inutile
sull'animazione.** Impostare le aspettative su questo evita giorni buttati.

## Assemblaggio

```bash
# i frame vanno nominati <anim>_<dir>_<nn>.png
python scripts/spritesheet.py frames/hero -o out/hero --cell 64x96 \
    --anchor bottom-center --fps 12 --preview 3

# QA su ogni frame prima di comporre
for f in frames/hero/*.png; do
  python scripts/qa_check.py "$f" --sprite --max-colors 24 \
      --palette assets/palettes/master-modern.hex || echo "PROBLEMA: $f"
done
```
