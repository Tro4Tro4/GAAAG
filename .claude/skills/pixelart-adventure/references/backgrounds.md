# Fondali e ambienti

## Regia dell'inquadratura

Impostazione fissa dello stile: **camera frontale, quasi ortogonale, a
"diorama"**. La profondita' nasce dalla sovrapposizione di piani e dal contrasto
di valore, non dalla prospettiva forzata.

- **Punto di fuga** unico, centrale, entro il 10% dalla mezzeria orizzontale.
- **Orizzonte** a y 162-180 (45-50%).
- Prospettiva visibile **solo nel pavimento**: le pareti si leggono come piani
  frontali, gli spigoli laterali rientrano di 20-40 px.
- Nessuna inclinazione di camera, nessuna lente grandangolare. Lo stile deve
  sembrare la sezione di un palcoscenico.

## I cinque livelli

Autorare sempre per livelli separati, anche se poi si esporta appiattito: e' cio'
che permette al personaggio di camminare *dentro* la scena e non davanti a una
cartolina.

| Livello | Contenuto | Valore | File |
|---|---|---|---|
| **L0 fondo** | esterno, cielo, apertura luminosa, stanza adiacente | 45-88 | dentro `_bg` |
| **L1 architettura lontana** | pareti di fondo, finestre, porte, quadri | 35-55 | dentro `_bg` |
| **L2 palcoscenico** | pareti laterali, pavimento, arredo fisso | 25-45 | dentro `_bg` |
| **L3 oggetti di gioco** | interattivi, arredo mobile | 25-50 | dentro `_bg` (+ maschere singole se animati) |
| **L4 primo piano** | cornice: stipiti, colonne, piante, sedie di spalle | 8-20 | `_fg` PNG con alpha |

## Composizione

- La **fascia centrale-bassa** (x 200-440, y 250-345) resta libera: e' dove sta il
  personaggio quasi sempre. Nessun dettaglio importante li'.
- Il **primo piano** (L4) occupa dal 15% al 25% dell'area, tipicamente in colonne
  ai lati e/o una fascia in basso. Serve a tre cose insieme: profondita',
  incorniciare l'azione, nascondere i tagli della scena.
- **Linee guida**: pavimento, cornicioni, cavi, tubi e mensole convergono verso
  il punto interattivo principale. In una avventura grafica la composizione e'
  design di livello: dice al giocatore dove guardare.
- **Regola dei tre pesi**: un punto focale forte, due secondari, il resto e'
  contesto. Se ci sono quattro punti forti la scena non ha piu' un soggetto.
- **Punti interattivi**: 3-6 per schermata. Uno solo e' una schermata sprecata,
  oltre sei diventa un cerca-oggetti.

## Fascia di calpestio e walkmask

La zona percorribile e' un poligono, non tutta la scena. Va prodotta come
immagine separata alla stessa risoluzione nativa:

- `_walk.png`: bianco = percorribile, nero = bloccato. Nessun anti-aliasing.
- Facoltativo `_scale.png`: gradiente verticale in scala di grigi che l'engine usa
  per scalare il personaggio con la profondita'. Con camera quasi ortogonale la
  variazione e' contenuta: **da 100% a y 345 fino a 82% a y 230**. Scalare oltre
  rompe la griglia di pixel.
- Le soglie di uscita (porte, scale, bordi schermo) vanno annotate nel JSON con
  un rettangolo e la destinazione.

## Illuminazione della scena

Dichiarare **prima di iniziare** tre righe, e non cambiarle piu':

```
KEY:       da destra-alto, 30 gradi, tungsteno (rampa tungsten)
FILL:      ambientale freddo, 2 stop sotto (rampa denim/concrete bassi)
PRACTICAL: plafoniera a soffitto x2 + insegna al neon fuori finestra (screen alti)
```

Se serve un passaggio giorno/notte, si autora **un solo fondale** piu' un
`_light.png` additivo (rampe `tungsten`/`screen` su nero) che l'engine somma in
blending additivo. E' molto piu' economico di due fondali e resta coerente.

## Locations contemporanee — repertorio con angolo consigliato

| Ambiente | Rampe | Key light | Nota di staging |
|---|---|---|---|
| Appartamento, salotto | wood, concrete, tungsten, ink | lampada da terra, calda, da sinistra | divano di spalle in L4, TV accesa come practical |
| Ufficio open space, notte | concrete, screen, ink, denim | neon a soffitto, freddo, dall'alto | file di scrivanie in fuga, un solo monitor accesso |
| Garage / officina | ink, rust, concrete, tungsten | lampada da lavoro appesa, calda, dal centro | serranda in fondo semichiusa, attrezzi appesi come texture |
| Metropolitana, banchina | concrete, ink, screen, rust | neon lineari, freddi, dall'alto | galleria buia come punto di fuga, cartelloni come accenti |
| Minimarket notturno | screen, concrete, rust, tungsten | neon bianco freddo, uniforme | scaffali paralleli in L2, vetrina in L1 con notte fuori |
| Parcheggio esterno, notte | ink, concrete, tungsten | lampione arancione singolo, da destra | asfalto umido che riflette, auto in L4 come cornice |
| Corridoio ospedale | concrete, screen, ink | plafoniere fredde, dall'alto in fuga | simmetria forte, punto di fuga esatto al centro |
| Bar / locale | wood, tungsten, rust, ink | luci calde a sospensione, basse | bancone che taglia in diagonale, bottiglie retroilluminate |
| Tetto / balcone, notte | ink, denim, screen, tungsten | skyline come practical, dal fondo | cielo = la superficie piu' chiara; parapetto in L4 |
| Archivio / magazzino | wood, concrete, ink, tungsten | lucernario, calda, dall'alto a fascio | scaffalature in fuga, pulviscolo nel fascio (cluster 1 px, 3% densita') |

## Deliverable per fondale

```
bg_<location>_<variante>/
  <nome>_bg.png       640x360 opaco, il fondale
  <nome>_fg.png       640x360 RGBA, il primo piano L4 (alpha binaria)
  <nome>_light.png    640x360 opzionale, passaggio luci additivo
  <nome>_walk.png     640x360 bianco/nero, area percorribile
  <nome>_scale.png    640x360 opzionale, scala di profondita'
  <nome>.json         hotspot, uscite, sottopalette usata, key light
```

Schema del JSON:

```json
{
  "name": "office_night",
  "native": [640, 360],
  "key_light": "neon a soffitto, freddo, dall'alto",
  "subpalette": ["concrete", "screen", "ink", "denim"],
  "walk_scale": {"y_near": 345, "y_far": 230, "scale_near": 1.0, "scale_far": 0.82},
  "hotspots": [
    {"id": "desk_monitor", "rect": [352, 176, 40, 32], "verbs": ["look", "use"]},
    {"id": "drawer",       "rect": [312, 232, 24, 16], "verbs": ["look", "open"]}
  ],
  "exits": [
    {"id": "to_corridor", "rect": [16, 200, 40, 120], "target": "corridor_night"}
  ]
}
```

## Verifica finale

```bash
python scripts/qa_check.py out/office_night_bg.png --native 640x360 \
    --palette assets/palettes/master-modern.hex --grid 8
python scripts/qa_check.py out/office_night_fg.png --native 640x360 --sprite \
    --palette assets/palettes/master-modern.hex
```

Poi il controllo che nessuno script puo' fare: mettere lo sprite del personaggio
nei quattro angoli e al centro dell'area percorribile e verificare che resti
leggibile in tutti e cinque i punti.
