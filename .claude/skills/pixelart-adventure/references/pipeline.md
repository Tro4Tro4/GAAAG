# Pipeline di produzione

## Vista d'insieme

```
blockout (a mano, 640x360)
   ↓  nearest x2
generazione AI (1280x720, 4-8 varianti)
   ↓  selezione
pixelate.py  → griglia nativa + palette master + dithering controllato
   ↓
qa_check.py  → blocca risoluzione, colori, AA, alpha, limiti di stile
   ↓
rifinitura a mano (Aseprite / Photoshop) → checklist sotto
   ↓
export per livelli (bg, fg, light, walk) + JSON
   ↓
qa_check.py di nuovo + prova in engine con lo sprite del personaggio
```

Il passaggio di rifinitura a mano **non e' opzionale** se l'obiettivo e' la
qualita' da studio. Lo script porta l'immagine dentro le specifiche; il
passaggio manuale la porta dentro il gioco. Su un fondale sono 45-90 minuti.

## Comandi

```bash
# palette master (una volta per progetto)
python scripts/palette.py build --out assets/palettes

# fondale: da render 1280x720 a nativo 640x360
python scripts/pixelate.py render/office_01.png -o out/office_night_bg \
    --native 640x360 --palette assets/palettes/master-modern.hex \
    --dither bayer4 --preview 3

# sprite o icona: alpha binaria obbligatoria
python scripts/pixelate.py render/icon_phone.png -o out/icons/phone \
    --native 32x32 --palette assets/palettes/master-modern.hex \
    --alpha-threshold 128 --preview 6

# controllo qualita' (esce 1 se qualcosa fallisce: usabile in uno script di build)
python scripts/qa_check.py out/office_night_bg.png --native 640x360 \
    --palette assets/palettes/master-modern.hex --grid 8

# sprite sheet dai frame
python scripts/spritesheet.py frames/hero -o out/hero --cell 64x96 \
    --anchor bottom-center --fps 12

# quanti colori usa un riferimento? (analisi)
python scripts/palette.py extract riferimento.png -n 32 --out analisi.hex
```

### Scelte dei parametri di `pixelate.py`

- `--resample box` (default) media i pixel: e' la scelta giusta quasi sempre,
  perche' non introduce ringing come `lanczos`.
- `--resample lanczos` solo se il render ha dettagli fini che il box impasta;
  produce piu' mezzi toni, quindi va sempre accompagnato dalla quantizzazione.
- `--dither none` per sprite, icone, UI. **Sempre.**
- `--dither bayer4` per fondali con grandi superfici; `bayer2` se il risultato
  sembra rumoroso; `--dither-strength 0.3` per un dithering piu' discreto.
- `--alpha-threshold 128` obbligatorio per qualunque asset con trasparenza.

## Checklist di rifinitura manuale

Da eseguire nell'ordine, sul file nativo, a zoom 400-800%:

1. **Silhouette e piani** — il primo piano e' abbastanza scuro? I tre piani si
   leggono socchiudendo gli occhi?
2. **Pixel orfani** — cercare i pixel isolati introdotti dal downscale e fonderli
   nei cluster vicini.
3. **Spigoli architettonici** — ridisegnare a mano ogni spigolo lungo: il
   downscale li rende irregolari. Devono essere linee di 1 px pulite, allineate
   alla griglia da 8 px.
4. **Occlusione ambientale** — aggiungere la linea 1-2 px dove i piani si
   incontrano. L'AI la sbaglia quasi sempre.
5. **Jaggies** — correggere le diagonali con passi incoerenti (3-1-3-1 → 2-2-2-2).
6. **Bordi di luce** — 1 px sul lato verso la key sugli oggetti interattivi.
7. **Testi e simboli** — cancellare qualunque scritta generata (sara' sempre
   illeggibile) e ridisegnarla con il font bitmap del progetto.
8. **Volti e mani** — sugli sprite, ridisegnarli sempre a mano. Sono i due punti
   dove l'occhio umano e' piu' intollerante.
9. **Aree di riposo** — se tutto e' dettagliato, appiattire deliberatamente il
   25% dell'immagine.
10. **Prova finale** — visualizzare a x1 su schermo intero e a x3, con lo sprite
    del personaggio in 5 posizioni. Se il personaggio si perde, correggere il
    fondale, non il personaggio.

## Organizzazione dei file

```
progetto/
  assets/palettes/master-modern.hex
  reference/style-bible.png          fondale + personaggio + icone + palette
  blockout/                          i blockout dipinti a mano
  render/                            output grezzi dei generatori (non versionati)
  out/
    bg/    <scena>_bg.png  _fg.png  _light.png  _walk.png  <scena>.json
    sprites/  <pg>.png  <pg>.json
    icons/    <oggetto>.png
    ui/       cornici, cursori, font
  scripts/                           i quattro script della skill
```

Versionare `blockout/`, `out/`, `assets/`. **Non** versionare `render/`: sono
gigabyte di scarti.

## Build e controllo continuo

Uno script di verifica che gira su tutta la cartella prima di ogni consegna:

```bash
#!/usr/bin/env bash
set -u
PAL=assets/palettes/master-modern.hex
fail=0
for f in out/bg/*_bg.png; do
  python scripts/qa_check.py "$f" --native 640x360 --palette $PAL --grid 8 \
    >/dev/null || { echo "FONDALE: $f"; fail=1; }
done
for f in out/bg/*_fg.png out/bg/*_light.png; do
  [ -e "$f" ] || continue
  python scripts/qa_check.py "$f" --native 640x360 --sprite --palette $PAL \
    >/dev/null || { echo "OVERLAY: $f"; fail=1; }
done
for f in out/icons/*.png; do
  python scripts/qa_check.py "$f" --native 32x32 --sprite --max-colors 12 \
    --palette $PAL >/dev/null || { echo "ICONA: $f"; fail=1; }
done
exit $fail
```

## Note per l'engine

- Filtro texture **nearest**, mipmap disattivate.
- Camera e posizione degli sprite arrotondate a **pixel nativi interi** ogni
  frame. Il movimento a coordinate frazionarie e' la causa numero uno di
  sfarfallio.
- Risoluzione di rendering interna 640x360, upscale a intero verso la finestra;
  se la finestra non e' un multiplo esatto, aggiungere bande nere invece di
  scalare a fattori frazionari.
- Se serve una scalatura del personaggio con la profondita', limitarla
  all'82-100% e arrotondare l'altezza risultante a pixel interi.
- Font renderizzati alla dimensione nativa, mai scalati.
