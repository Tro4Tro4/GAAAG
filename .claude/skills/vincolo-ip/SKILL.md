---
name: vincolo-ip
description: Verifica che i contenuti di AGGGA non contengano riferimenti alla Guida Galattica per Autostoppisti, distinguendo il tono ispirato (lecito) dal riferimento diretto o dal calco strutturale (vietato). Usa questa skill ogni volta che inventi o revisioni nomi di personaggi, nomi di luoghi, dialoghi, testi di hotspot, descrizioni di oggetti, nomi di file o asset, battute, elementi di trama o di ambientazione — anche quando l'utente non nomina esplicitamente il vincolo IP, e anche per una singola battuta. Usala anche prima di committare contenuti narrativi e quando l'utente chiede "controlla l'IP", "va bene questo nome?", "questo somiglia troppo?", "possiamo usare questa battuta?".
---

# Vincolo IP — AGGGA

AGGGA prende ispirazione dalla *Guida Galattica per Autostoppisti* **solo nel
tono**. Il vincolo è dichiarato non negoziabile in `CLAUDE.md`. Questa skill
serve a rispettarlo davvero, non solo a dichiararlo.

## Perché il vincolo esiste (e perché il grep non basta)

Il diritto d'autore non protegge un genere né un registro comico. Nessuno
possiede "fantascienza demenziale", "burocrazia cosmica" o "protagonista
qualunque travolto dagli eventi". Protegge l'**espressione specifica**: nomi
coniati, personaggi, luoghi, invenzioni, frasi, e la combinazione
riconoscibile di questi elementi.

Da qui discende la regola operativa: il pericolo non è la parola, è il
**riconoscimento**. Un lettore che conosce l'originale deve poter dire "questo
ha lo stesso spirito", mai "questo è quella cosa lì con i nomi cambiati".

Ne segue che la ricerca testuale dei nomi vietati è la parte *facile* e già
automatizzata. La parte che richiede giudizio — e dove le violazioni
realmente accadono — è il calco strutturale: nessun termine proibito, eppure
la scena è la stessa. Dedica lì la maggior parte dell'attenzione.

## Procedura

### 1. Controllo meccanico

```bash
.claude/skills/vincolo-ip/scripts/check-ip.sh              # tutto il repo
.claude/skills/vincolo-ip/scripts/check-ip.sh file1 file2  # file specifici
```

Esce con codice 1 se trova termini vietati, 0 altrimenti. Gli avvisi sui
termini ambigui non bloccano di proposito: sono spunti di valutazione, non
verdetti.

Lo script esclude `CLAUDE.md` e `README.md` — per enunciare il divieto devono
poter nominare l'opera — e la cartella della skill stessa, che contiene per
forza i termini che cerca.

Se stai valutando testo che non è ancora su disco (una battuta appena
proposta in conversazione), scrivilo in un file temporaneo nello scratchpad e
passalo allo script, oppure confronta a mano con
`references/termini-vietati.txt`.

### 2. Controllo strutturale

Qui serve leggere e pensare. Cerca gli echi elencati sotto: sono le forme in
cui l'originale sopravvive anche dopo aver cambiato tutti i nomi.

### 3. Referto

Riporta l'esito nel formato in fondo a questa skill.

## Gli echi strutturali da intercettare

Questi sono i calchi più probabili. Non sono vietati i temi generici a cui
somigliano: è vietata la **specificità dell'esecuzione**. Per ognuno indico
dove passa la linea.

**Il robot depresso.** Un androide malinconico che si lamenta della propria
esistenza come spalla comica è il singolo calco più facile da commettere in
un progetto di questo genere — e il più immediatamente riconoscibile.
Un'IA con un difetto caratteriale va benissimo; scegli un difetto diverso.
Un robot ossessionato dalle procedure, o entusiasta in modo inopportuno, o
convinto di essere in pensione, occupa la stessa funzione comica senza
essere quel personaggio.

**Il pesce traduttore.** Il concetto di traduzione universale è un tropo
libero e antichissimo. La creatura vivente che si infila nell'orecchio per
tradurre è l'esecuzione specifica dell'originale. Se serve un traduttore,
cambia il meccanismo *e* la collocazione corporea.

**La demolizione planetaria per opere pubbliche.** La Terra rasa al suolo per
far posto a un'infrastruttura di transito, con preavviso burocratico
beffardo, è la premessa dell'originale, non un tropo generico. La burocrazia
cosmica indifferente resta disponibile: applicala a un'altra pratica
amministrativa — un cambio di residenza, un collaudo, una riclassificazione
catastale, un rinnovo di licenza.

**La guida che narra a voci.** Un'enciclopedia galattica che interrompe la
storia con definizioni ironiche è *la* trovata dell'originale, quella che dà
il titolo all'opera. Evita l'espediente narrativo in sé, non solo il nome.

**Il numero-risposta.** Il 42 come esito di un calcolo cosmico, o come
mistero irrisolto, o come battuta. Come valore ordinario (una coordinata, un
contatore, una dimensione in pixel) è irrilevante: nessuno possiede un
numero. È il *ruolo* che lo rende una citazione.

**L'asciugamano-talismano.** Come oggetto di scena è un asciugamano. Come
simbolo dell'esploratore galattico previdente, è una citazione.

**La poesia come tortura.** Una razza burocratica che infligge i propri versi
ai prigionieri. Anche cambiando razza e versi, la scena resta riconoscibile.

**Il protagonista in vestaglia.** L'uomo comune inglese strappato di casa in
accappatoio o vestaglia la mattina presto. Il protagonista qualunque è
consentito e anzi previsto dal progetto: cambia il quadro d'apertura.

**La propulsione per improbabilità.** Un motore che funziona rendendo
probabili eventi assurdi.

Questa lista non è esaustiva. Il criterio generale la estende: se stai per
scrivere qualcosa e ti viene in mente l'originale mentre lo scrivi, quello è
il segnale. Non ignorarlo perché i nomi sono diversi.

## Come valutare i termini ambigui

Per ogni avviso prodotto dallo script, una sola domanda:

> Questa parola sta facendo il suo lavoro ordinario, o sta portando con sé
> l'originale?

Esempi di ragionamento:

- `42` nella riga `Position = new Vector2(42, 108);` → coordinata. Nessun
  problema, non serve nemmeno menzionarlo nel referto.
- `42` in `"Il calcolatore ronzò per secoli e rispose: quarantadue."` →
  citazione. Da cambiare.
- `asciugamano` in una stanza-bagno tra gli oggetti raccoglibili → scenografia.
  Va bene.
- `asciugamano` in `"Non partire mai senza."` → citazione. Da cambiare.
- `guida` in `"guida il design degli altri sistemi"` → verbo. Irrilevante.
- `guida` come nome di un'entità che spiega l'universo al giocatore → calco
  strutturale, il più grave della lista.

Il buon senso è consentito ed è anzi il punto: segnalare tutto con lo stesso
peso equivale a non segnalare niente.

## Cosa fare quando trovi una violazione

Non limitarti a segnalare: **proponi una sostituzione originale**. Una
segnalazione senza alternativa blocca il lavoro e verrà aggirata.

Nel proporre, mantieni la funzione narrativa e cambia l'esecuzione. Se il
nome vietato era un burocrate ostile, serve comunque un burocrate ostile: dagli
un nome inventato con una fonetica propria e coerente con il resto di AGGGA.

Verifica anche che l'invenzione non sia un anagramma trasparente o una
storpiatura di un termine vietato (`Vogoni` → `Vogorni` non risolve niente:
peggiora, perché dichiara la consapevolezza dell'originale).

## Formato del referto

Usa questa struttura, adattandola in lunghezza a quanto hai esaminato:

```
## Controllo vincolo IP

**Ambito**: <cosa hai esaminato>

**Termini vietati**: <nessuno | elenco con file:riga>

**Echi strutturali**: <nessuno | descrizione di ciascuno e perché>

**Ambigui valutati**: <solo quelli su cui c'era davvero un dubbio,
con la conclusione>

**Esito**: <conforme | da correggere>

<se da correggere: elenco delle sostituzioni proposte>
```

Quando è tutto pulito, sii breve: due righe bastano. Il referto lungo serve
quando c'è qualcosa da decidere.

## Un avvertimento sul falso senso di sicurezza

Lo script che passa non significa "conforme". Significa solo che non
compaiono i nomi propri dell'originale — la parte più facile del vincolo.
Un testo può superare il controllo automatico ed essere comunque un calco
integrale. Non chiudere mai una verifica citando solo l'esito dello script.
