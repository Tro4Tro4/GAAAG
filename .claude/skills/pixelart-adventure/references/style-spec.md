# Specifica di stile — pixel art da studio, ambientazione contemporanea

Questo file e' la fonte di verita'. Ogni numero qui dentro e' verificabile con
`scripts/qa_check.py`. Se un asset non rispetta questi valori, non e' pronto.

## Indice
1. Canvas e griglia
2. Palette e limiti colorimetrici
3. Luce, valore, gerarchia
4. Contorni (selout)
5. Dithering e anti-aliasing
6. Regole di cluster e leggibilita'
7. Densita' di dettaglio
8. Ricettario materiali (contemporaneo)
9. Errori tipici e come si vedono

---

## 1. Canvas e griglia

| Voce | Valore |
|---|---|
| Risoluzione nativa | **640 x 360** |
| Presentazione | x3 nearest-neighbor -> 1920x1080 (x2 -> 1280x720 per test) |
| Griglia base | **8 px** (640/8 = 80 celle, 360/8 = 45 celle: divisione esatta) |
| Griglia architettonica | 16 px per moduli murari, 40 px per interpiano |
| Linea d'orizzonte | 45-50% dell'altezza (y 162-180) |
| Fascia di calpestio | y 230-345 (il personaggio ha i piedi qui dentro) |
| Margine di sicurezza UI | 8 px per lato |

**Perche' 640x360**: e' 16:9 esatto, scala a interi verso 720p/1080p/1440p senza
mai produrre pixel rettangolari, e a questa densita' una testa umana occupa ~11 px,
abbastanza per un'espressione leggibile. Sotto i 400 px di larghezza le espressioni
sparirebbero, sopra gli 800 il costo di produzione a mano raddoppia senza guadagno
percepito.

Tutto si allinea alla griglia da 8 px: spigoli murari, battiscopa, davanzali,
piani dei mobili. La griglia e' cio' che distingue una scena costruita da un
render sfocato: l'occhio riconosce inconsciamente il ritmo modulare.

**Regola non negoziabile: un pixel logico = un pixel del file.** Nessun asset
viene mai salvato ingrandito. L'ingrandimento e' compito dell'engine, con
filtro nearest e camera su coordinate intere.

---

## 2. Palette e limiti colorimetrici

Palette master: `assets/palettes/master-modern.hex` — **48 colori** = 9 rampe da 5
valori + 3 riservati.

| Rampa | Uso |
|---|---|
| `ink` | neutri strutturali, contorni, primo piano in controluce |
| `concrete` | cemento, asfalto, intonaco, acciaio spazzolato, cielo diurno |
| `wood` | parquet, mobili, porte, cartone |
| `skin` | incarnati (per tutte le carnagioni: si sceglie lo stop di partenza) |
| `denim` | tessuti freddi, jeans, uniformi, notte |
| `foliage` | verde desaturato, piante, vegetazione urbana |
| `tungsten` | luce calda, lampade, ottone, finestre illuminate |
| `rust` | accenti caldi, ruggine, mattone, plastica rossa |
| `screen` | monitor, insegne, neon, vetro, riflessi freddi |

Riservati: nero puro **solo** per letterbox/vuoto; bianco puro **solo** per
specular puntuali (max 2 px per asset); magenta `FF00FF` come colorkey nei tool
che non gestiscono l'alpha.

### Limiti misurati

Questi non sono gusti, sono i numeri del linguaggio visivo scelto:

- **Saturazione HSV <= 50** su ogni colore di materiale. Mediana attesa 20-35.
- **Valore HSV** fra 8 e 88, con **mediana della scena fra 25 e 40**.
  Massimo 2 colori sopra V 80, e solo per fonti di luce.
- **Colori per fondale: 32-48**. Per sprite personaggio: **16-24**.
  Per icona inventario: **max 12**.
- **Massimo 5 rampe per singolo asset.** Oltre, l'immagine perde coesione:
  e' il motivo per cui la pixel art amatoriale sembra "sporca".

### Hue-shifting (la regola che fa la differenza)

Ogni rampa **ruota la tinta** salendo di valore: le ombre virano al freddo
(verso 210-250 gradi), le luci al caldo (verso 30-50 gradi). Questo imita luce
diretta calda + rimbalzo ambientale freddo. Una rampa che cambia solo
luminosita' mantenendo la tinta appare morta, di plastica.

Esempio, rampa `wood`:
`#24191A` -> `#422F2E` -> `#644C44` -> `#8C715E` -> `#B1A18B`
la tinta passa da 355 gradi (bruno freddo) a 34 gradi (ocra calda), mentre la
saturazione resta fra 21 e 33: bassa, come nel riferimento.

Per rigenerare la palette dopo una modifica alle rampe:
`python scripts/palette.py build --out assets/palettes`

### Sottopalette per scena

Ogni fondale usa un **sottoinsieme** di 24-32 colori dalla master, non tutti i 48.
Scegliere 3 rampe dominanti + 1 di accento + `ink`. E' quello che da' a ogni
ambiente un'identita' cromatica pur mantenendo la coerenza globale: un garage
notturno usa `concrete`+`ink`+`denim`+`tungsten`, un ufficio al neon usa
`concrete`+`screen`+`ink`+`wood`.

---

## 3. Luce, valore, gerarchia

Tre luci, sempre:
1. **Key** — una sola direzione dominante, dichiarata in testa al lavoro
   (es. "da destra-alto, 30 gradi, tungsteno"). Definisce dove cadono le luci.
2. **Fill** — ambientale, freddo, 1-2 stop sotto la key, senza direzione netta.
3. **Practical** — la fonte visibile in scena (lampada, monitor, insegna, finestra).
   E' l'unico elemento autorizzato a occupare i valori sopra V 78.

### Gerarchia di valore per piani

| Piano | Valore HSV | Funzione |
|---|---|---|
| Primo piano (cornice) | 8-20 | incornicia, crea profondita', quasi silhouette |
| Piano di gioco | 25-45 | dove sta il personaggio e gli oggetti usabili |
| Fondo / architettura lontana | 40-60 | arretra |
| Fonte di luce | 65-88 | ancora lo sguardo |

Questa e' prospettiva aerea invertita rispetto al paesaggio: in interni il fondo
e' piu' chiaro perche' contiene l'apertura luminosa. Il primo piano scuro e' la
mossa piu' economica per ottenere profondita' in pixel art.

### Occlusione ambientale

Dove due piani si incontrano (muro/pavimento, mobile/muro, oggetto/piano) si
mette una linea di 1-2 px di uno stop piu' scura del piano ricevente. Senza
questo, gli oggetti sembrano incollati sopra lo sfondo.

---

## 4. Contorni (selout)

**Mai contorno nero uniforme.** Si usa il *selective outlining*: il contorno
esiste solo dove serve a separare due elementi, e il suo colore e' una versione
scurita del colore locale, non un nero unico.

- **Fondali**: contorni assenti o parziali. Gli elementi si separano per
  differenza di valore, non per linea. Contorno solo sugli oggetti interattivi.
- **Sprite personaggi**: contorno **completo di 1 px** su tutta la silhouette,
  colore `ink-1`/`ink-2` o il locale scurito di 2 stop. Serve perche' il
  personaggio deve restare leggibile passando davanti a qualunque fondale.
- **Icone inventario**: contorno completo di 1 px in `ink-2`, per staccare
  dall'interfaccia.
- Il contorno interno (fra braccio e torso, per esempio) e' 1 stop sotto il
  colore locale, **non** il colore del contorno esterno. Usare lo stesso scuro
  dentro e fuori appiattisce la figura.

---

## 5. Dithering e anti-aliasing

**Dithering** — solo Bayer ordinato (2x2 o 4x4), mai casuale, mai Floyd-Steinberg
in produzione (il rumore non e' controllabile e rovina il tiling):
- consentito: gradienti su superfici ampie e piatte (muri, cieli, pavimenti,
  aloni di luce) — aree > 48x48 px
- vietato: dentro gli sprite dei personaggi, su oggetti < 32 px, sulle icone
- il dithering va **nella direzione della transizione**, non a caso, e occupa
  al massimo il 20% dell'area della superficie

**Anti-aliasing** — solo manuale, mai automatico:
- massimo 1 px di tono intermedio, e solo su diagonali con pendenza piu' dolce
  di 1:2 e su curve
- **vietato sulla silhouette esterna degli sprite**: deve restare tagliente,
  altrimenti in movimento sfarfalla
- vietato sul testo dei font bitmap

L'output di un generatore AI e' pieno di anti-aliasing involontario. E' esattamente
il motivo per cui `scripts/pixelate.py` quantizza sempre sulla palette: la
quantizzazione in Oklab collassa i mezzi toni parassiti sul colore piu' vicino.

---

## 6. Regole di cluster e leggibilita'

- **Nessun pixel orfano**: un pixel isolato di un colore che non appare nei
  vicini e' rumore. Cluster minimo 2 px, salvo specular intenzionale.
- **Jaggies**: le scalette di una diagonale devono avere passi coerenti
  (3-3-3 o 4-2-4-2). Sequenze tipo 3-1-3-1 leggono come errore.
- **Banding**: due rampe adiacenti non devono creare fasce parallele di
  spessore identico su grandi superfici; variare lo spessore o rompere con
  dithering.
- **Contrasto personaggio/fondo**: nel punto in cui il personaggio cammina, il
  suo valore medio deve differire dal fondale locale di **almeno 25 punti V**.
  Se il fondale e' medio, il personaggio va scurito o schiarito localmente:
  in alternativa si scurisce quella zona di fondale.
- **Test della silhouette**: riempi lo sprite di nero pieno. Se non riconosci
  chi e' e cosa sta facendo, la posa e' sbagliata. Nessuna quantita' di
  dettaglio interno recupera una silhouette illeggibile.
- **Punti interattivi**: ogni oggetto usabile deve avere ingombro >= 12x12 px
  nativi (36x36 a schermo x3), +1 stop di contrasto rispetto all'intorno e una
  tinta leggermente piu' calda o piu' satura del contesto. E' il modo per
  segnalare l'interattivita' senza sovrapporre icone.

---

## 7. Densita' di dettaglio

Il budget di dettaglio non e' uniforme. Distribuzione target su un fondale:

- **fascia di interesse** (y 140-250, altezza occhi/mani): **60%** del dettaglio
- pavimento e soffitto: 15% ciascuno
- primo piano: 10%, quasi solo silhouette

Aree di riposo: almeno il 25% dell'immagine deve essere superficie relativamente
piatta (2-3 colori). Senza zone calme l'occhio non trova il soggetto. E' l'errore
piu' comune nella pixel art generata da AI: dettaglio uniforme e ipnotico su
tutto il fotogramma, che risulta illeggibile in gioco.

---

## 8. Ricettario materiali (contemporaneo)

Ogni voce: rampa da usare, numero di toni, trattamento.

| Materiale | Rampa | Toni | Trattamento |
|---|---|---|---|
| Cemento a vista | `concrete` | 3 | macchie a cluster irregolari, no texture regolare; giunti di getto ogni 40 px |
| Intonaco dipinto | `concrete`/`wood` | 2 | quasi piatto, un solo gradiente verticale con Bayer 4x4 |
| Asfalto | `ink`+`concrete` | 3 | grana a cluster da 2-3 px, densita' 8%; pozzanghere = 2 px di `screen` speculare |
| Vetro (finestra) | `screen` | 3 | non trasparente: 2 fasce diagonali di riflesso + 1 px di bordo chiaro |
| Acciaio spazzolato | `concrete` | 4 | strisce orizzontali di 1 px alternate, solo 2 stop di differenza |
| Monitor accesso | `screen` alti | 3 | bordo 1 px chiarissimo, alone 3 px sul muro dietro, contenuto astratto |
| Neon / insegna | `screen`/`rust` alti | 3 | tubo 2 px + alone 2 px + riflesso sul suolo umido |
| Laminato / IKEA | `wood` medi | 2 | piatto, bordo chiaro 1 px in alto, nessuna venatura sotto i 32 px |
| Parquet | `wood` | 3 | doghe da 8x40 px, sfalsate, variazione di 1 stop fra doghe adiacenti |
| Moquette d'ufficio | `concrete`/`foliage` | 2 | dithering Bayer 2x2 al 15%, nessun bordo |
| Plastica lucida | qualsiasi | 3 | specular duro 1-2 px senza sfumatura, contorno scuro |
| Tessuto / felpa | `denim`/`rust` | 3 | pieghe come tratti di 3-5 px che convergono ai punti di tensione |
| Pelle umana | `skin` | 3-4 | il 4o tono solo su naso/fronte/pomelli; ombra sotto il mento sempre |
| Metallo cromato | `ink`+`concrete`+1 chiaro | 4 | inversione netta di valore a meta', senza toni intermedi |
| Fogliame | `foliage` | 3 | ciuffi a cluster di 3-6 px, mai foglie singole; scuro in basso |
| Carta / documenti | `ink` alti | 2 | bordo 1 px scuro, mai bianco puro (usa `ink-5`) |

---

## 9. Errori tipici e come si vedono

| Sintomo | Causa | Rimedio |
|---|---|---|
| Sembra un JPEG sfocato ingrandito | asset salvato ingrandito, oppure resize LANCZOS | rigenerare con `pixelate.py --resample box`, `qa_check.py` rileva i blocchi |
| Colori "sabbiosi", immagine sporca | troppi colori, mezzi toni AI residui | riquantizzare sulla palette; controllare il numero di colori |
| Tutto ugualmente interessante, non si capisce dove andare | densita' di dettaglio uniforme | scurire e semplificare il primo piano, aggiungere aree di riposo |
| Personaggio "incollato" sopra il fondale | manca l'occlusione ambientale e l'ombra a terra | linea AO 1-2 px + blob d'ombra separato |
| Personaggio invisibile in alcune zone | contrasto di valore < 25 V | scurire localmente il fondale o rinforzare il contorno |
| Rampe morte, aspetto di plastica | nessun hue-shift | rigenerare le rampe con `palette.py build` |
| Sfarfallio in movimento | anti-aliasing sulla silhouette, alpha non binaria, posizione a coordinate frazionarie | `pixelate.py --alpha-threshold 128`; snap a pixel interi nell'engine |
| Ambienti che sembrano di giochi diversi | sottopalette scelte senza criterio, key light incoerente | dichiarare key light e 4 rampe prima di iniziare ogni fondale |
