# Oggetti, icone inventario, HUD e font

## Oggetti in scena

Fanno parte del fondale e usano la **stessa sottopalette** e la **stessa key
light** della scena. Se un oggetto e' interattivo:

- +1 stop di contrasto rispetto all'intorno immediato
- tinta di 1 passo piu' calda o satura del contesto
- linea di occlusione ambientale 1-2 px dove appoggia
- ingombro >= 12x12 px nativi
- bordo di luce (rim light) 1 px sul lato verso la key

Se un oggetto va animato o rimosso (una porta che si apre, un oggetto raccolto),
va esportato **separato** con alpha e il fondale va dipinto **anche sotto**.
Dimenticarlo e' l'errore piu' fastidioso da scoprire in fase di integrazione.

## Icone inventario

Standard rigido, e' cio' che rende l'inventario un insieme invece di una raccolta:

| Voce | Valore |
|---|---|
| Canvas | **32 x 32** px |
| Contenuto utile | 26 x 26 centrato (3 px di aria per lato) |
| Angolo di vista | **3/4 dall'alto, 30 gradi**, identico per ogni oggetto |
| Luce | da **alto-sinistra a 45 gradi**, identica per ogni oggetto |
| Colori | max **12**, contorno 1 px `ink-2` completo |
| Ombra | offset 1 px in basso-destra, `ink-1`, solo sotto l'oggetto |
| Toni | 3 per materiale (ombra/base/luce), 4o solo se l'oggetto e' il fulcro di un enigma |

Un oggetto che a 26 px non e' riconoscibile va **stilizzato**, non rimpicciolito:
si esagerano i due tratti identificativi (la forma della lama, il colore del
tappo) e si eliminano tutti gli altri. Un cellulare a 26 px e' un rettangolo
scuro con 1 px di schermo `screen-4`: basta e leggerissimo.

Varianti per oggetti moderni ricorrenti: chiavi, cellulare, badge, chiavetta USB,
tazza, scontrino, cacciavite, torcia, medicinali, portafoglio, biglietto,
caricabatterie. Mantenere lo stesso angolo su tutti e dodici e' l'unico modo per
farli sembrare dello stesso gioco.

## HUD e interfaccia

Overlay a **640x360**, disegnato sopra la scena, margine di sicurezza 8 px.

- **Cornici 9-slice**: angoli 8x8 px, bordi ripetibili da 8 px. Bordo esterno
  1 px `ink-3`, bordo interno 1 px `ink-2`, riempimento `ink-1` all'85% di alpha
  (o dithering Bayer 2x2 se l'engine non supporta l'alpha parziale).
- **Box di dialogo**: altezza 72 px, ancorato in basso, testo con 8 px di padding.
  Nome del parlante in `tungsten-4`, battuta in `ink-5`.
- **Barra inventario**: celle da 40x40 con icona 32x32 centrata, 4 px di gap,
  cella selezionata = bordo `tungsten-4` di 1 px.
- **Cursore**: 16x16 px, hotspot a (1,1), contorno `ink-1` di 1 px con interno
  `ink-5` per essere visibile su qualsiasi fondale. Varianti verbo: guarda
  (occhio), usa (mano), parla (fumetto), esci (freccia).
- **Nessuna trasparenza sfumata, nessun blur, nessuna ombra morbida.** L'unico
  effetto ammesso e' un'ombra netta di 1-2 px offset.
- **Animazioni UI**: transizioni a scatti di 2-3 frame, non interpolazioni.
  L'interfaccia deve avere lo stesso "grano temporale" della grafica.

## Font

Bitmap, senza anti-aliasing, mai scalato a fattori non interi.

| Uso | Cap-height | Griglia glifo | Interlinea |
|---|---|---|---|
| Dialoghi | 10 px | 6x10 + 1 px di spaziatura | 14 px |
| UI / etichette | 8 px | 5x7 + 1 px | 11 px |
| Numeri / HUD | 8 px | 4x7 monospazio | 11 px |

Requisiti: set latino completo con **accenti italiani** (à è é ì ò ù) e
maiuscole accentate, virgolette basse « », apostrofo tipografico.
Verificare che gli accenti non escano dalla cella: a 10 px di cap-height serve
1 px di aria sopra, quindi la cella e' 12 px.

Scelte pratiche: usare un font bitmap con licenza esplicita per uso commerciale
(molti font pixel diffusi hanno licenze ambigue — **verificare sempre la licenza
prima di integrarlo**, non fidarsi delle raccolte "free"). In alternativa,
disegnare il set su misura: 96 glifi a 6x10 px sono circa una giornata di lavoro
e risolvono per sempre il problema della licenza e degli accenti.

Esportare come sprite sheet + descrittore delle metriche (BMFont `.fnt` o JSON
con kerning per coppia). Il kerning e' opzionale ma su `AV`, `To`, `r,` migliora
molto la resa.

## Deliverable

```
ui/
  frame_dialog.png     cornice 9-slice, 24x24 (3x3 celle da 8)
  frame_panel.png
  inv_cell.png         40x40
  cursor_look.png      16x16 RGBA
  cursor_use.png
  font_dialog.png      + font_dialog.json (metriche)
  font_ui.png          + font_ui.json
icons/
  key_apartment.png    32x32 RGBA
  phone_cracked.png
  ...
```

## QA

```bash
# icone: canvas esatto, alpha binaria, tetto di 12 colori
for f in icons/*.png; do
  python scripts/qa_check.py "$f" --native 32x32 --sprite --max-colors 12 \
      --palette assets/palettes/master-modern.hex || echo "PROBLEMA: $f"
done
```
