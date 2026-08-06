# AGGGA — Avventura Grafica Punta-e-Clicca

## Cos'è
Avventura grafica punta-e-clicca stile anni '90 (LucasArts), con cambio di
personaggio controllabile stile *Day of the Tentacle* / *Maniac Mansion*.
Storia originale, ambientazione fantascientifica assurda/comica ispirata
nello **spirito** (non nei contenuti) a *Guida Galattica per Autostoppisti*.

## Stack tecnico
- **Engine**: Godot 4.x (build standard, non .NET)
- **Linguaggio**: GDScript
- **Ambiente di sviluppo**: editor Godot per **Android** — è l'unica macchina
  disponibile allo sviluppatore, e da questo discende la scelta del linguaggio
- **Piattaforme target**: PC (Win/Mac/Linux) + mobile (Android/iOS)
- **Arte**: stile ibrido — personaggi, oggetti e hotspot in **pixel art** netta
  disegnata via codice, sfondi **a piena risoluzione** (1920×1080 `.webp`,
  tinte piatte e contorno scuro, filtro lineare) generati con strumenti esterni
  e poi misurati e adattati nel progetto

## Vincolo IP — NON NEGOZIABILE
Nessun riferimento diretto a *Guida Galattica per Autostoppisti*: niente nomi
di personaggi (Arthur Dent, Ford Prefect, Marvin, Zaphod, Vogon...), niente
luoghi, niente citazioni o dialoghi originali del libro. L'ispirazione resta
sul **tono**: umorismo assurdo, burocrazia cosmica, fantascienza demenziale,
protagonista qualunque catapultato in situazioni incomprensibili.
Personaggi, nomi, luoghi e trama devono essere originali.

## Gameplay
- Punta-e-clicca classico con **verb-coin** a ventaglio — solo i verbi che
  l'oggetto offre, compattati a partire da sinistra — e un vocabolario chiuso di
  sette parole in quattro famiglie: Guarda / Prendi / Usa, Apri, Chiudi /
  Parla, Vai (camminare non è un verbo: si clicca il pavimento)
- **Più personaggi giocabili**, switch libero tra loro
- Puzzle che richiedono collaborazione tra personaggi diversi in luoghi
  diversi (es. uno passa un oggetto attraverso una finestra, l'altro lo
  raccoglie dall'altro lato)
- Inventario **separato per personaggio**, e gli oggetti passano da uno
  all'altro solo attraverso punti di passaggio collocati nelle stanze
- Ne segue un vincolo per la storia: i personaggi devono stare
  **strutturalmente separati**, non solo trovarsi in stanze diverse per caso
- Dialoghi ad albero con condizioni legate a flag/stato di gioco

## Ordine di sviluppo previsto
1. Sistema base: movimento *(fatto e **verificato sul dispositivo**:
   click-to-walk con navmesh, l'ostacolo viene aggirato)*, stanze *(scena
   `Room` minima)*, hotspot cliccabili *(fatti: cammina fino all'oggetto e
   mostra la descrizione)*, verb-coin UI *(fatta e **verificata sul
   dispositivo**: premi-trascina-rilascia con scelta per direzione, badge con
   icone, vocabolario di sette parole in quattro famiglie, ventaglio compattato
   da sinistra)*
2. Sistema personaggi multipli: switch *(fatto: autoload `GameState`, barra di
   cambio)*, stato indipendente per personaggio *(parziale: ognuno ha la sua
   posizione e la sua stanza; il resto arriverà con inventario e flag)*,
   multi-stanza *(fatto e **verificato sul dispositivo**: radice `Game`, due
   stanze collegate da una porta, cambiare personaggio porta nella sua stanza)*
3. Sistema inventario *(fatto e **verificato sul dispositivo**: un inventario
   per personaggio, pannello a comparsa, verbi sugli oggetti, combinazione fra
   oggetti, uso di un oggetto su un hotspot)*
4. Sistema dialoghi con condizioni *(fatto: `Conditions`, la persistenza dello
   stato di stanza — `present_if` e varianti degli hotspot — e i dialoghi ad
   albero, con risorse `.tres`, pannello modale di opzioni e caption tinta di
   chi parla)*
5. Prototipo verticale *(fatto: tre stanze, due personaggi separati per
   autorizzazione, un enigma cooperativo completo — vedi "Il prototipo
   verticale" fra le decisioni)*
6. Solo dopo il prototipo: scrittura della storia completa, capitoli,
   altre stanze, durata finale del gioco (ancora da stabilire)

Fuori sequenza, e fatto tutto fra il punto 4 e il punto 5 per completare
l'ossatura prima di costruirci sopra: **salvataggio e caricamento**,
**localizzazione** (italiano e inglese), **guscio** (titolo, pausa,
impostazioni), **transizioni**, **direzione e stati** dei personaggi,
**profondità**, **telecamera**, **audio** e **sequenze scriptate**. Il
salvataggio è venuto per primo perché era l'unica parte il cui costo cresce a
ogni sistema aggiunto; la localizzazione subito dopo perché toccava tutto, e
farla dopo avrebbe voluto dire riscrivere il resto.

## Struttura del progetto
```
project.godot        Configurazione progetto Godot (renderer, display, autoload)
default_bus_layout   I due bus audio, Music e Sound
icon.svg             Icona placeholder
scenes/              Scene Godot (.tscn), nomi in PascalCase
  Main               Scena di avvio: personaggi, telecamera, audio, sequenze e
                     UI, e ospita la stanza corrente in RoomContainer
  rooms/Lobby        Prototipo: l'atrio dove comincia Nora, con sfondo dipinto
  rooms/Tubes        Prototipo: il corridoio dei tubi, largo due schermate
  rooms/Station      Prototipo: la postazione dove sta Cesare
  characters/Player  Personaggio giocabile (CharacterBody2D + NavigationAgent2D)
scripts/             Codice GDScript (.gd), nomi in snake_case,
                     rispecchia l'albero di scenes/
  game.gd            Scambia le stanze e collega tutto il resto
  conditions.gd      Grammatica delle condizioni ("solo se..."), soli metodi
                     statici — condivisa fra stanze, dialoghi e presenze
  save_game.gd       Scrive e rilegge una partita, soli metodi statici
  game_camera.gd     Insegue il personaggio dentro i limiti della stanza
  audio_director.gd  Musica di stanza ed effetti, due riproduttori
  autoload/          game_state.gd (una partita), settings.gd (lingua, volumi)
  rooms/             room.gd, hotspot.gd, hotspot_variant.gd, state_visual.gd,
                     door_hotspot.gd, pickup_hotspot.gd, passage_hotspot.gd
  characters/        player_character.gd — cammina, guarda, tiene le tasche
  items/             inventory_item.gd, item_combination.gd,
                     combination_book.gd, item_catalogue.gd — dati, non nodi
  dialogue/          dialogue.gd, dialogue_line.gd, dialogue_option.gd — dati;
                     dialogue_runner.gd tiene il segno in una conversazione
  sequence/          sequence.gd, sequence_step.gd — dati;
                     sequence_runner.gd mette in scena, con await
  text/              locale_texts.gd — una lingua, chiave per chiave
  ui/                caption.gd, character_bar.gd, verb_coin.gd,
                     inventory_panel.gd, dialogue_panel.gd, menu_panel.gd,
                     settings_panel.gd, title_screen.gd, fade.gd
resources/           Risorse di dati (.tres), niente scene e niente codice
  items/             Un file per oggetto — quattro, quelli che il prototipo sa
                     mettere in mano — più combinations.tres con le ricette e
                     catalogue.tres con l'elenco di tutti gli oggetti
  characters/        Un .tres di SpriteFrames per personaggio, scritto da tools/
  dialogues/         Un file per conversazione
  sequences/         Un file per scena scriptata
  text/              it.tres e en.tres — tutte le frasi del gioco
tools/               Script che producono asset, da eseguire dalla radice
  make_lobby_pixel_background.py  Lo sfondo dell'atrio, disegnato a 320x180
  make_lobby_props.py       Bacheca, portamoduli e sedie dell'atrio
  make_tubes_pixel_background.py    Il corridoio, disegnato a 640x180
  make_station_pixel_background.py La postazione, disegnata a 320x180
  make_station_props.py     Consolle, leva, sportello di servizio e registro
  make_tubes_props.py       Oblo', targhetta, punto d'imbuco, capsula, battenti
  make_item_icons.py        Le quattro icone d'inventario, 12x12
  make_character_sheets.py  I fogli dei personaggi e i loro SpriteFrames
assets/              sprites/ backgrounds/ audio/ fonts/
  backgrounds/       Uno sfondo per stanza, pixel art .png alle misure della
                     stanza, a scala 1 e filtro Nearest: 320x180 l'atrio e la
                     postazione, 640x180 il corridoio
  ui/                Le sette icone dei verbi, in SVG
  audio/             Cinque suoni segnaposto generati da uno script
```

## Decisioni prese (e perché)
- **Godot** invece di Ren'Py/AGS/Visionaire: è gratuito, esporta su tutte le
  piattaforme target, ottimo supporto 2D nativo (non è un motore 3D adattato).
  La parte di questa decisione che riguardava il **linguaggio C#** è stata
  **superata** — vedi "Da C# a GDScript" in fondo all'elenco. Il motivo di
  allora era il riuso dell'esperienza .NET dello sviluppatore, ed era valido:
  è caduta la premessa, non il ragionamento.
- **Sistema a personaggi multipli** invece di singolo protagonista: scelta
  esplicita di gameplay ispirata a Day of the Tentacle, guida il design
  degli altri sistemi (inventario, stato, dialoghi)
- **Storia dopo il prototipo tecnico**, non prima: con il cambio personaggio
  la trama deve incastrarsi con vincoli di design (chi può fare cosa, dove,
  quando); più efficiente validare il sistema prima di scrivere capitoli
- **Scaffold iniziale del progetto** (fondamenta tecniche, nessuna logica di
  gioco ancora). Scelte e alternative scartate:
  - **Renderer `gl_compatibility`** invece di Forward+/Mobile: è l'unico
    che gira in modo affidabile su PC + mobile + web ed è più che
    sufficiente per un 2D pixel art. Forward+ è pensato per 3D/desktop
    high-end; Mobile è un intermedio non necessario qui.
  - **Texture filter `Nearest` (default_texture_filter=0)**: pixel netti,
    niente sfocatura in upscaling — indispensabile per pixel art. L'alternativa
    (Linear) sfoca i pixel ed è pensata per arte ad alta risoluzione.
  - **Risoluzione base 384×216 (16:9), finestra 3× = 1152×648** con
    `stretch/mode = canvas_items` e `aspect = keep`: si disegna a bassa
    risoluzione "retro" e si scala in modo pulito mantenendo il rapporto.
    Valori facilmente modificabili; scelti come default ragionevole, non
    definitivi. **Decisione superata** — vedi "Da 384×216 a 320×180" in fondo
    all'elenco. Le due parti che non sono cadute sono `canvas_items` e
    `aspect = keep`, e la previsione che i valori fossero provvisori era giusta.
  - *(Decadute con il passaggio a GDScript: la scelta di `.NET 8 / net8.0` come
    runtime e del nome assembly/namespace `Aggga`. I file `Aggga.csproj/.sln`
    non esistono più.)*
- **Movimento con `NavigationRegion2D` + `NavigationAgent2D`** (il pathfinding
  nativo di Godot) invece di soluzioni scritte a mano: la zona calpestabile si
  disegna nell'editor come poligono con eventuali "buchi" per gli ostacoli, e
  l'engine calcola il percorso. Il personaggio aggira gli ostacoli e non taglia
  gli angoli delle stanze concave senza che il codice se ne occupi: lo script
  del personaggio si limita a sterzare verso il prossimo vertice del percorso.
  - **Area calpestabile + movimento diretto** (poligono pavimento, si cammina
    in linea retta verso il click): l'alternativa più economica, una cinquantina
    di righe e nessun concetto nuovo dell'engine — sarebbe bastata per una
    stanza rettangolare vuota. Scartata perché cede alla prima stanza non
    convessa o con un oggetto in mezzo: il personaggio attraversa gli ostacoli
    e taglia gli angoli. Il costo aggiuntivo della navigazione nativa è di poche
    righe, molto meno di quanto costerebbe rifare il movimento più avanti.
  - **Walkbox stile SCUMM** (box convessi + grafo di adiacenza, come nei
    LucasArts originali): è la soluzione più fedele al genere e regala la scala
    per profondità, perché ogni box può portarsi dietro il proprio fattore di
    scala. Scartata per il costo: è tutto da costruire a mano, tooling di
    authoring incluso, prima che qualcosa si muova sullo schermo. La scala per
    profondità si può ottenere separatamente con una curva Y→scala, senza
    legarla al sistema di movimento.
  - Nota: da rivedere se emergesse il bisogno di regole di percorribilità che
    la navmesh non esprime (zone attraversabili solo da un personaggio,
    passaggi che si aprono con un flag di gioco). Sono modellabili anche con la
    navigazione nativa, ma se diventassero la norma e non l'eccezione, il grafo
    esplicito dei walkbox tornerebbe competitivo.
- **La stanza gestisce il click, il personaggio non lo conosce**: `Room`
  intercetta il click in `_UnhandledInput`, lo proietta sul punto più vicino
  della navmesh e chiama `WalkTo()` sul personaggio. Il personaggio non sa
  nulla di mouse né di stanze: è ciò che permetterà a verb-coin, inventario e
  dialoghi di consumare il click prima del pavimento, e allo stesso
  personaggio di essere pilotato da una cutscene invece che dal giocatore.
  - **Input gestito dal personaggio**: più immediato da scrivere (un solo
    script invece di due) e con un nodo in meno da collegare. Scartato perché
    con più personaggi giocabili ognuno reagirebbe al click, e servirebbe
    comunque un arbitro che decida quale: quell'arbitro è la stanza.
- **Da C# a GDScript** (revoca della scelta di linguaggio iniziale): l'unica
  macchina su cui lo sviluppatore può lavorare è un telefono Android. L'editor
  Godot per Android esiste ed è pienamente funzionante, ma è la build standard
  dell'engine: **non supporta C#**, e una versione .NET dell'editor Android non
  esiste né è prevista. Il PC aziendale non consente installazioni e non c'è un
  computer personale. La scelta non era quindi tra due linguaggi, ma tra
  GDScript e l'impossibilità di sviluppare.
  - **Restare su C#**: conserva il riuso dell'esperienza .NET, la sicurezza del
    compilatore (generics, interfacce, tipizzazione forte) e il tooling di
    Visual Studio/Rider — vantaggi reali, non trascurabili. Scartata perché
    richiede un editor .NET su desktop, che non è disponibile e non si prevede
    lo diventi.
  - Momento della conversione: fatta con **due script e ~110 righe** in tutto.
    Le scene, la navmesh e ogni altra decisione architetturale sono rimaste
    invariate: sono cambiati solo il riferimento allo script e i nomi delle
    proprietà esportate. Convertire più avanti, con verb-coin, inventario e
    dialoghi già scritti, sarebbe costato ordini di grandezza in più.
  - Effetto collaterale positivo sul metodo di lavoro: senza passo di
    compilazione e con l'editor sul dispositivo dello sviluppatore, il codice
    può finalmente essere **eseguito e verificato**. Con C# nessuno dei due
    lati poteva farlo, e ogni modifica restava non testata.
  - Nota: da rivedere solo se lo sviluppatore ottenesse una macchina desktop e
    il progetto fosse ancora abbastanza piccolo da rendere sensata la
    riconversione — condizione che smette di valere in fretta.
- **Il gioco ascolta solo eventi mouse, il tocco lo converte l'engine**
  (`emulate_mouse_from_touch`, attivo per impostazione predefinita): un solo
  percorso di codice per desktop e mobile, e i nodi `Control` — quindi la
  futura verb-coin e l'inventario — continuano a rispondere al tocco senza
  codice dedicato. La dipendenza è dichiarata **qui e non in `project.godot`**
  perché Godot non scrive i valori uguali al default: provato a metterlo
  esplicitamente, l'editor lo cancella alla prima apertura. Se un giorno
  qualcuno lo disattivasse, il gioco smetterebbe di rispondere al tocco senza
  che nulla nel codice lo spieghi.
  - **Gestire anche `InputEventScreenTouch`**: sembra la scelta più corretta
    per un gioco mobile, ed è stata provata sul dispositivo. Scartata perché
    con l'emulazione attiva **ogni tocco arriva due volte**, una come mouse e
    una come touch: verificato nell'output di esecuzione. Oggi significa solo
    ordinare due volte la stessa camminata, ma con gli hotspot vorrebbe dire
    eseguire ogni verbo due volte. Disattivare l'emulazione per evitarlo
    costerebbe il funzionamento al tocco di tutta la UI.
  - Conseguenza da non dimenticare: l'emulazione copre il click, **non
    l'hover**. Su mobile il passaggio del puntatore non esiste, e la verb-coin
    non può basarsi su di esso. È un vincolo di design della verb-coin, non un
    dettaglio implementativo.
- **Hotspot come `Area2D` interrogata dalla stanza**, non come nodo che
  intercetta il proprio click: al click la stanza chiede al motore fisico cosa
  c'è sotto il punto e decide lei se è un hotspot o pavimento. La priorità tra
  i due è scritta in un punto solo, ed è coerente con la decisione già presa
  che la stanza sia l'arbitro del click — necessaria perché la verb-coin dovrà
  inserirsi *tra* il click e l'azione.
  - **Ogni `Area2D` gestisce il proprio click** (segnale `input_event`): è la
    via che Godot offre e costa meno codice. Scartata per due motivi: l'ordine
    con cui l'engine smista input e picking fisico non è verificabile
    nell'ambiente di sviluppo remoto, e con più hotspot sovrapposti servirebbe
    comunque un arbitro esterno che decida quale vince.
  - **Solo geometria, niente fisica** (rettangolo esportato più test
    matematico): nessun concetto nuovo dell'engine e comportamento del tutto
    prevedibile. Scartata perché le forme si modificherebbero digitando numeri
    nell'Inspector invece che trascinando maniglie nell'editor, e lo sviluppo
    avviene su telefono.
- **Hotspot come dati più segnale**, non uno script per oggetto: nome,
  descrizione e punto di avvicinamento sono proprietà esportate, e
  `interacted` permette a chi serve di agganciarsi. La porta con un
  comportamento speciale avrà il suo script, la cassa no.
  - **Uno script per ogni hotspot**: massima libertà. Scartata perché la
    stragrande maggioranza degli oggetti di un punta-e-clicca deve solo
    mostrare una descrizione, e un file per oggetto diventa ingestibile molto
    prima che il gioco sia interessante.
- **Punto di avvicinamento esplicito su ogni hotspot** (`Marker2D` figlio):
  non si cammina *dentro* l'oggetto, ci si ferma davanti. Serve anche per una
  ragione tecnica, non solo estetica: un hotspot su un muro — una porta — sta
  fuori dalla navmesh, quindi la sua posizione non è una destinazione valida.
- **I riferimenti a nodi si risolvono con `@onready`, non con `@export`**: le
  scene di questo progetto si scrivono come testo, non si compongono
  trascinando nodi nell'editor, e un `@export` di tipo nodo salvato a mano come
  `NodePath` non risulta collegato quando serve. Verificato sul dispositivo:
  `player` è arrivato a `_ready()` come `Nil`, e in precedenza lo stesso
  problema si era presentato come "il click non fa niente", perché il
  riferimento mancante veniva usato solo dentro il gestore di input.
  - **`@export` assegnato a mano nell'editor**: è la via che Godot documenta,
    sopravvive agli spostamenti del nodo e tiene il collegamento fuori dal
    codice. Scartata perché richiederebbe allo sviluppatore di ricollegare a
    mano ogni riferimento nell'Inspector, su telefono, ogni volta che una
    scena viene scritta o rigenerata da qui.
  - `@export` resta la scelta giusta per i **valori** — numeri, stringhe,
    booleani: quelli dal file di scena si applicano senza problemi.
- **L'azione in sospeso viene sovrascritta da ogni nuovo click**: la stanza
  ricorda quale hotspot sta raggiungendo e la consuma all'arrivo. Cliccare
  altrove a metà strada annulla l'azione invece di lasciarla scattare quando
  si arriva. L'alternativa (`await destination_reached` dentro il gestore del
  click) è più corta da scrivere ma lascia in vita la vecchia attesa, che si
  risveglia alla fine della camminata successiva ed esegue l'azione sbagliata.
- **Stato dei personaggi in un autoload `GameState`**: chi è il personaggio
  attivo, e in futuro inventario e flag, vivono fuori dalle scene. È la
  risposta al punto che era rimasto aperto ("come la stanza individua il
  personaggio attivo"): la stanza non nomina più un figlio, chiede a
  `GameState` e si riaggancia al segnale `active_character_changed`. Il motivo
  è che le stanze verranno caricate e scaricate, e ciò che il giocatore sta
  controllando non deve sparire con esse.
  - **Nodo `Game` esplicito sopra le stanze**, che possiede i personaggi e
    passa i riferimenti verso il basso: niente stato globale, dipendenze
    dichiarate, più facile da seguire leggendo. Scartata perché introduce
    subito un livello di scena in più, e perché ogni sistema successivo
    (inventario, dialoghi, flag) dovrebbe ripetere lo stesso cablaggio —
    ricostruendo di fatto un singleton con più passaggi.
  - **Gruppo di nodi più un flag "attivo"**: nessun concetto nuovo. Scartata
    perché il flag deve comunque vivere da qualche parte, e nella stanza si
    perderebbe al cambio stanza: rimanda il problema invece di risolverlo.
  - Costo accettato consapevolmente: un autoload è raggiungibile da ovunque, e
    tutto ciò che può fare lo può fare qualunque script. Va tenuto **di soli
    dati**, non di comportamento, o diventa il posto dove finisce tutto.
- **I personaggi si registrano da soli** in `_ready()` e si tolgono in
  `_exit_tree()`; il primo che arriva prende il controllo. L'alternativa — un
  elenco configurato a mano da qualche parte — andrebbe tenuta allineata alle
  scene e divergerebbe alla prima modifica.
- **La barra di cambio personaggio si costruisce a runtime** dall'elenco di
  `GameState`, invece di essere disegnata nella scena: segue il numero di
  personaggi che una stanza ha davvero, e non esiste una seconda lista da
  mantenere sincronizzata. Essendo fatta di nodi `Control`, consuma i propri
  click prima che arrivino alla stanza — che è precisamente il motivo per cui
  la stanza ascolta `_unhandled_input` e non `_input`.
- **Cambiare personaggio annulla l'azione in sospeso**: la commissione era di
  chi stava camminando, e passare il controllo non passa la commissione.
- **Verb-coin con tre verbi: Guarda, Usa, Parla** — il set della *Maledizione
  di Monkey Island*. "Prendi" sta dentro "Usa", e camminare non è un verbo: si
  clicca il pavimento. Chiude il punto che era rimasto aperto sulla lista dei
  verbi. **Decisione superata** — vedi "Da tre verbi a quattro" in fondo
  all'elenco: il costo che questa voce indicava è reale, ed è stato accettato. Meno verbi significa anche meno testi da scrivere per ogni oggetto,
  che è il costo vero di questa scelta e si paga a ogni hotspot del gioco.
  - **Quattro verbi, con "Prendi" separato**: distingue raccogliere da
    azionare, cosa che il giocatore a volte apprezza. Scartata perché aggiunge
    un testo per oggetto e restringe gli spicchi da toccare.
  - **Barra SCUMM a nove verbi** (*Monkey Island* 1 e 2): la più evocativa del
    genere. Scartata perché mangerebbe un terzo di uno schermo 384×216 e su
    telefono i bersagli diventerebbero minuscoli.
- **La moneta si usa con due tocchi**, non con premi-trascina-rilascia: un
  tocco sull'oggetto la apre, un tocco su un verbo lo esegue, un tocco altrove
  annulla. Si costruisce con normali nodi `Control`, perdona gli errori e non
  richiede di seguire il dito. **Decisione superata** — vedi "Da due tocchi a
  premi-trascina-rilascia" in fondo all'elenco. Il ragionamento resta valido
  nei costi che indicava: sono stati accettati, non smentiti.
  - **Premi, trascina, rilascia** (il gesto originale di *Full Throttle*): più
    rapido una volta imparato e più fedele all'originale. Scartato perché va
    scritto a mano — tracciamento del dito e riconoscimento dello spicchio al
    rilascio — e su un telefono il dito copre proprio ciò che deve scegliere.
  - Correzione a una nota precedente: l'assenza di hover su mobile **non** era
    un ostacolo per la verb-coin, che nell'originale si basava sul
    trascinamento e non sul passaggio del puntatore. Quel vincolo colpisce la
    barra SCUMM e la riga "Usa X con Y" che segue il cursore, non questo
    sistema.
- **La moneta copre l'intero schermo mentre è aperta**: così si mangia ogni
  click che non finisce su un verbo, e un tocco a vuoto la chiude invece di
  ordinare una camminata sotto il menù aperto.
- **Un verbo senza testo risponde con un rifiuto generico** invece di restare
  muto: in un punta-e-clicca la maggior parte degli oggetti rifiuta la maggior
  parte dei verbi, e scrivere tre testi per ogni hotspot sarebbe insostenibile.
  Il silenzio, invece, si legge come un bug.
- **Multi-stanza: radice `Game` persistente, stanze scambiate come figli, i
  personaggi non sono più figli della stanza.** Chiude la decisione che era
  rimasta aperta. `Main.tscn` è la scena di avvio e contiene tre cose che
  sopravvivono al cambio stanza: `RoomContainer` (vuoto, ci entra la stanza
  corrente), `Characters` (tutti i personaggi giocabili, istanziati una volta
  per l'intera partita) e `UI` (un `CanvasLayer` con caption, verb-coin e barra
  di cambio). Una stanza torna a essere solo ciò che una stanza deve essere:
  sfondo, hotspot, navmesh, punti d'ingresso.
  Il criterio che ha deciso non è il caricamento delle stanze — su quello ogni
  alternativa se la cava — ma il fatto che questa è l'unica in cui **la vita
  dei personaggi si stacca dalla vita delle stanze**. Da lì discende tutto il
  resto: il roster non si svuota mai, quindi la barra continua a offrire chi
  sta altrove (presupposto dello switch stile Day of the Tentacle); la
  posizione di chi non è in scena non va salvata da nessuna parte, perché è la
  `position` di un nodo che continua a esistere; e `GameState` non cambia di
  una riga.
  - **`change_scene_to_file()` + posizioni serializzate in `GameState`**: è la
    via che Godot documenta e mostra in ogni tutorial, una chiamata sola e
    zero infrastruttura. Scartata perché ogni personaggio andrebbe istanziato
    in ogni stanza in cui *potrebbe* trovarsi, con quelli di troppo che si
    cancellano da soli all'avvio — la scena mente su chi c'è e la verità sta
    altrove. In più la UI andrebbe replicata in ogni stanza, e il cambio scena
    è differito a fine frame: il codice dopo la chiamata gira ancora nella
    vecchia stanza.
  - **Tutte le stanze caricate insieme, si mostra e si nasconde**: fa sparire
    del tutto il problema della persistenza — niente si scarica, quindi niente
    va conservato — ed è l'implementazione più corta in assoluto. Scartata per
    la navigazione: **tutti i `NavigationRegion2D` presenti nell'albero
    confluiscono nella stessa navigation map** del `World2D`, quindi con due
    stanze disegnate alle stesse coordinate `map_get_closest_point()` può
    restituire un punto del pavimento dell'altra stanza. Se ne esce dando a
    ogni stanza una mappa propria (codice non ovvio) o distanziando le stanze
    in coordinate globali (un'altra decisione da prendere). Si aggiunge che
    `visible = false` non ferma `_physics_process`.
  - **Stanze istanziate una volta e staccate/riattaccate all'albero**
    (`remove_child()` senza `queue_free()`): conserverebbe ogni stato senza
    salvarne nessuno, e il ritorno in una stanza già visitata sarebbe
    istantaneo. Scartata perché `_enter_tree()`/`_exit_tree()` scattano a ogni
    scambio, non una volta sola: la registrazione dei personaggi andrebbe
    disfatta comunque, pagando la complessità di questa per riottenere ciò che
    la scelta adottata ha per costruzione. Resta valida come ottimizzazione
    *sopra* la soluzione attuale, se un giorno ricaricare una stanza risultasse
    lento.
  - Il nodo `Game` **non è** la risurrezione dell'alternativa scartata più
    sopra, sotto "Stato dei personaggi in un autoload": quella era `Game` come
    *proprietario dello stato*, e quel giudizio resta. Qui `Game` non possiede
    niente — personaggio attivo, inventario e flag restano in `GameState`. È
    solo il punto dell'albero dove le stanze si attaccano e la UI non muore.
  - **Cambiare personaggio porta alla sua stanza** (come in Day of the
    Tentacle). Ne segue che la stanza mostrata non è uno stato a sé: è sempre
    `active_character.current_room`, e non esiste una seconda variabile da
    tenere allineata.
  - **Ogni personaggio porta il proprio `current_room`** (percorso della scena)
    e chi non è nella stanza mostrata viene nascosto *e* messo in
    `PROCESS_MODE_DISABLED`: nascondere e basta non basta, perché la
    visibilità non ferma `_physics_process` e un personaggio invisibile
    continuerebbe a camminare su una navmesh non più caricata.
  - **La stanza non conosce più l'interfaccia**: emette `wants_to_say` e
    `hotspot_activated`, e `Game` li collega a caption e verb-coin. Prima li
    prendeva con `$Caption` perché erano suoi figli; ora vivono più in alto.
    Conseguenza da ricordare: **una stanza non è più eseguibile da sola** — non
    ha personaggi né UI. La scena su cui premere Play è `Main.tscn`.
  - **I punti d'ingresso sono `Marker2D` sotto un nodo `EntryPoints`**, e la
    porta nomina quello di destinazione (`target_entry`) invece di indicare
    coordinate. Il punto d'arrivo si trascina nell'editor, nella stanza a cui
    appartiene, invece di essere digitato come coppia di numeri — la stessa
    ragione per cui le forme degli hotspot sono `CollisionShape2D`.
  - **`Hotspot.interact()` riceve anche il personaggio**, e `interacted` lo
    porta nel segnale: con più personaggi giocabili "chi l'ha fatto" è metà
    della risposta. La porta deve spostare chi l'ha aperta, e raccogliere un
    oggetto dovrà metterlo nelle mani di qualcuno.
  - **`DoorHotspot` è il primo hotspot con uno script proprio**, ed è la
    conferma della decisione "hotspot come dati più segnale": due valori
    esportati e una riga di codice per la porta, niente per la cassa.
- **Da due tocchi a premi-trascina-rilascia** (revoca della scelta di
  interazione della verb-coin): si preme sull'oggetto, si tiene premuto, si
  scivola sul verbo, si solleva. Sollevare altrove annulla. È il gesto
  originale di *Full Throttle*, ed è **un gesto solo** invece di due tocchi
  separati con uno stato in mezzo.
  Non è caduta nessuna premessa tecnica: i costi che la decisione precedente
  aveva individuato erano corretti e sono stati accettati consapevolmente.
  - **Costo accettato: il dito copre lo spicchio.** A 384×216 un verbo è
    34×13 pixel, e durante il gesto il dito resta sullo schermo. La risposta
    è la selezione per direzione descritta sotto, più lo spicchio che si
    illumina — il riscontro c'è anche quando il testo non si vede.
  - **Costo accettato: un tocco secco non fa più niente.** Premere e
    rilasciare senza spostarsi apre e richiude la moneta. È inerente al gesto,
    non un difetto dell'implementazione.
  - **Si sceglie per direzione, non per rettangolo**: conta *dove* si è
    spostato il dito rispetto al punto in cui la moneta si è aperta, non cosa
    si trova sotto di esso. I verbi distano una cinquantina di gradi l'uno
    dall'altro e ne accettano 50 ciascuno, quindi non c'è un bordo da mancare
    né un buco tra gli spicchi in cui cadere; sotto 12 pixel di spostamento non
    si sceglie niente, e il cono che punta verso il basso non appartiene a
    nessun verbo, così trascinare in giù e sollevare è il modo di dire di no.
    La selezione per rettangolo, provata per prima, era **imprecisa sul
    dispositivo**: è stata la misura che mancava per prendere questa
    decisione, non un ripensamento a tavolino.
  - **Sollevando si esegue lo spicchio illuminato**, non quello sotto il punto
    di rilascio: in un gesto continuo lo stato è ciò che l'interfaccia sta
    mostrando, e il rilascio lo conferma — non è l'occasione per ricalcolarlo.
    Il primo tentativo rifaceva il test di posizione al sollevamento.
  - **Le posizioni si leggono da `event.position` e non si convertono.** È il
    bug che è costato più tempo di tutti: `make_input_local()` sembra la cosa
    giusta da fare in un `Control`, ma un evento arriva **già** espresso nello
    spazio 384×216, e riconvertirlo lo divide per il fattore di scala dello
    schermo — cinque, su un telefono. Il risultato non è un errore di qualche
    pixel: la direzione del gesto punta sempre in alto a sinistra, quindi
    vince sempre il primo verbo. Diagnosi sbagliata lungo la strada: il
    sintomo era stato attribuito al polpastrello che rotola al sollevamento,
    che è un fenomeno reale ma non era questo.
  - **`Button` non sta nella dimensione che gli chiedi**: un `Control` rifiuta
    di essere più piccolo del suo contenuto, quindi un bottone richiesto
    34×13 esce più alto una volta che font e margini del tema hanno detto la
    loro. Le posizioni si calcolano leggendo `size` a cose fatte, mai la
    costante richiesta, o il disegnato e il calcolato divergono in silenzio.
  - **Conseguenza tecnica non ovvia: il gesto si legge a mano in `_input()`**,
    non attraverso i segnali dei `Button`. È obbligato. La pressione che apre
    la moneta viene consumata dalla stanza **mentre la moneta è ancora
    invisibile**, quindi Godot non registra mai la moneta come il `Control`
    che sta trascinando (`gui.mouse_focus` resta vuoto) e il rilascio finale
    verrebbe instradato altrove. Leggere gli eventi grezzi e fare da sé il
    test sui rettangoli aggira del tutto la questione. I `Button` restano
    quindi come sola grafica: `MOUSE_FILTER_IGNORE`, e l'illuminazione si
    ottiene con `toggle_mode` più `button_pressed`, senza una seconda serie
    di disegni da mantenere.
  - Nota: il gesto dipende dal fatto che l'emulazione del mouse converta il
    trascinamento del dito (`InputEventScreenDrag`) in `InputEventMouseMotion`.
    Lo fa, ma è la stessa impostazione predefinita già annotata più sopra: se
    qualcuno la disattivasse, oggi si perderebbe anche la scelta del verbo,
    non solo il tocco.

- **Inventario separato per personaggio**, non condiviso. Chiude il punto che
  era rimasto aperto. Il motivo è che l'inventario condiviso renderebbe inutile
  metà del sistema costruito fin qui: i personaggi sopravvivono alle stanze
  perché uno possa stare di là mentre l'altro sta di qua, ma se le loro tasche
  sono le stesse la distanza fra loro smette di essere un ostacolo, e l'esempio
  di puzzle scritto in cima a questo file — uno passa un oggetto attraverso una
  finestra, l'altro lo raccoglie — non è più un puzzle.
  - **Inventario condiviso**: azzera l'attrito. Il giocatore non deve mai
    ricordare chi ha cosa né tornare indietro con la persona giusta, e la UI è
    una lista sola. Va anche detto che **non** ucciderebbe la cooperazione in
    generale: "uno tiene giù la leva mentre l'altro passa" funziona lo stesso.
    Scartato perché uccide la sottofamiglia degli enigmi *di trasporto*, che è
    proprio quella che il progetto cita come esempio.
  - **Ibrido** (fondo comune più oggetti personali): recupera entrambi.
    Rimandato perché richiede di comunicare al giocatore quale oggetto è di
    quale tipo — una regola in più da imparare prima di poter ragionare — e non
    c'è ancora abbastanza gioco per sapere se serva.
  - Costo accettato, e da pagare in fase di scrittura e non nel codice: se il
    giocatore dovesse continuamente cambiare personaggio e camminare per
    spostare oggetti, la difficoltà si sposterebbe dalla trovata alla
    logistica. La risposta è **rendere lo scambio raro e interessante** — un
    passaggio fisico che sia esso stesso l'enigma, non un comando di menù.
  - Nota: da rivalutare verso l'ibrido se in scrittura emergesse che troppi
    oggetti vogliono viaggiare liberi.
- **Flag di gioco in `GameState`, solo alzabili**: `is_raised()` e
  `raise_flag()`, un insieme di nomi. È il minimo che l'inventario rende
  obbligatorio — una stanza viene ricostruita dal suo file ogni volta che ci si
  torna, quindi senza flag una cassa svuotata si riempirebbe di nuovo e lo
  stesso oggetto si potrebbe prendere due volte. Non è ancora il sistema
  completo che servirà ai dialoghi: è la parte che quello estenderà.
  - **Interruttori a due vie** invece di flag a senso unico: più generali.
    Scartati perché ciò che può tornare indietro è *stato*, e lo stato
    appartiene a chi lo possiede; un insieme globale di cose già accadute non
    ha bisogno di poterle disfare, e non poterlo fare è metà della garanzia.
  - Il flag di "già preso" **non si scrive a mano**: `PickupHotspot` lo ricava
    dall'id dell'oggetto (`taken:<id>`). Un campo in meno da riempire e uno in
    meno da tenere allineato.
- **La frase "Usa X con Y" si costruisce in due tocchi separati**, non con un
  trascinamento: si preme l'oggetto nell'inventario, si sceglie Usa con la
  verb-coin di sempre, l'oggetto **resta in mano**, si chiude il pannello e si
  tocca il bersaglio. Mentre qualcosa è in mano la verb-coin non si apre più
  sugli hotspot: metà della frase è già scritta e il tocco fornisce l'altra
  metà.
  - **Trascinare l'oggetto dall'inventario sul bersaglio**: un gesto solo,
    coerente con la verb-coin. Scartato perché costringerebbe l'inventario a
    essere sempre visibile — non si può trascinare su un bersaglio che sta
    sotto il pannello — e su uno schermo alto 216 pixel una striscia permanente
    costa un decimo dell'altezza per qualcosa che si guarda di rado.
  - Ne segue che l'oggetto in mano deve restare visibile quando il pannello è
    chiuso: lo mostra il **bottone dello zaino**, che ne prende il nome. È
    l'unico posto sempre presente sullo schermo.
  - Toccare il pavimento con qualcosa in mano **rimette via l'oggetto e non fa
    camminare nessuno**: annullare deve poter essere un gesto solo, o disdire
    la frase manderebbe prima il personaggio dall'altra parte della stanza.
  - Un oggetto rifiutato dal bersaglio viene comunque rimesso via: un tentativo
    fallito è pur sempre un tentativo finito, e lasciarlo in mano farebbe
    ripetere lo stesso errore al tocco successivo.
- **La verb-coin sugli oggetti dell'inventario ha gli stessi verbi** della
  verb-coin sugli hotspot, e quelli che non hanno senso su un oggetto già in
  mano — Prendi e Parla — rispondono con il rifiuto generico. Un elenco
  di verbi variabile richiederebbe alla moneta di ricostruirsi ogni volta e al
  giocatore di leggere prima di scegliere, mentre la scelta per direzione vive
  proprio sul fatto che le tre posizioni siano sempre le stesse.
- **Le ricette stanno in un libro solo** (`combinations.tres`), non sugli
  oggetti che coinvolgono. Se un oggetto portasse le proprie ricette, le due
  classi si nominerebbero a vicenda e il progetto dipenderebbe da come GDScript
  risolve un riferimento ciclico — cosa che probabilmente fa, ma che non è
  verificabile dalla macchina di sviluppo. In più, quando una combinazione non
  funziona c'è un posto solo dove guardare.
- **Un hotspot accetta un solo oggetto**, dichiarato come dato
  (`accepted_item`, `accepted_text`, `consumes_accepted_item`,
  `accepted_flag`). È la stessa scelta già presa per i verbi: il caso
  serratura-e-chiave si esprime come dato, e qualunque cosa più complicata è un
  hotspot con uno script suo.
- **Le voci dell'inventario si leggono in `_input()` come nella verb-coin**, e
  i `Button` degli slot sono `MOUSE_FILTER_IGNORE`. Non è solo coerenza: un
  `Button` si annuncia al **rilascio**, e qui il gesto della verb-coin deve
  partire dalla **pressione** — quando il dito si alza è troppo tardi per
  cominciare a trascinare.

- **Da tre verbi a quattro: Guarda, Prendi, Usa, Parla** (revoca della scelta
  sul set di verbi). Il motivo è che "Usa" che significa anche "prendi" è
  ambiguo esattamente dove il giocatore ha più bisogno di chiarezza: davanti a
  un oggetto raccoglibile non sa se sta per infilarselo in tasca o azionarlo, e
  lo scopre solo dopo. Con "Prendi" separato, ogni verbo dice una cosa sola.
  Nessuna premessa è caduta: il costo che la decisione precedente aveva
  individuato — un testo in più da scrivere per ogni hotspot, e spicchi più
  stretti da colpire — è reale, e viene pagato consapevolmente.
  - **Costo accettato: un testo in più per oggetto.** Ogni hotspot ha ora
    quattro campi invece di tre, e il rifiuto generico ne copre la maggior
    parte. Su un gioco intero è il costo vero di questa scelta, e si paga in
    fase di scrittura.
  - **Costo accettato: spicchi più vicini.** Da 81° a una cinquantina, con 50°
    di tolleranza per ciascuno. Resta più largo del divario che li separa,
    quindi non nascono buchi, ma il gesto è meno grossolano di prima.
  - **I quattro spicchi stanno tutti nella metà superiore**, a sinistra,
    alto-sinistra, alto-destra, destra. Scartata la disposizione a croce con
    un verbo *sotto* il punto toccato: sarebbe la più larga da colpire (90°
    l'uno dall'altro) ma metterebbe uno spicchio sotto il dito, che quindi non
    si vedrebbe illuminare — e toglierebbe il cono verso il basso, che oggi è
    il modo di annullare.
  - Conseguenza da ricordare: **non c'è niente dritto in alto.** Con un numero
    pari di spicchi disposti simmetricamente il vertice è sempre un confine.
    Si mira ai bottoni, che sono visibili, quindi non è un problema — ma
    spingere esattamente in su non è un gesto definito.
  - **`PickupHotspot` risponde a Prendi e non più a Usa**, ed è la ragione per
    cui questa decisione andava presa adesso e non dopo: ogni hotspot
    raccoglibile scritto da qui in avanti avrebbe avuto il testo nel campo
    sbagliato.

- **Gli oggetti passano da un personaggio all'altro solo attraverso punti di
  passaggio collocati** — una fessura, una finestra, un tubo — e mai
  direttamente. Chiude il punto che era rimasto aperto. Due `PassageHotspot`
  in due stanze che condividono un `cache_id` sono i due capi della stessa
  fessura: quello che uno imbuca, l'altro lo ritira dall'altra parte.
  Il motivo è che un meccanismo di trasferimento sempre disponibile non
  risolve gli enigmi di trasporto, li **elimina**. Se il giocatore ha comunque
  un modo di passare un oggetto, "chi ha cosa" smette di essere un ostacolo e
  diventa una pratica da sbrigare: l'inventario separato tornerebbe a essere
  un inventario condiviso con più passi. Qui invece la domanda non è mai "come
  glielo do" ma "**da dove** può passare, e cosa ci passa", e le proprietà del
  passaggio diventano vincoli di enigma gratuiti — sotto la porta passa solo
  qualcosa di piatto, nel tubo solo qualcosa che rotola.
  - **Consegna a mano** (usa l'oggetto sull'altro personaggio presente nella
    stanza): ovvia, non va spiegata, ed evita la scena assurda di due che si
    guardano senza potersi passare una chiave inglese. Costa poco. Scartata
    perché si autodistrugge: o i due **possono** trovarsi nella stessa stanza,
    e allora ogni enigma di trasporto si scioglie portandoli lì; oppure **non
    possono**, e allora quel codice non si attiva mai. Dannosa o inutile, e nel
    mezzo c'è solo il caso peggiore, in cui a volte si può e a volte no e il
    giocatore non sa quale regola valga dove.
  - **Un congegno fisso unico** stile cessi temporali di Day of the Tentacle:
    il trasferimento è sempre possibile, quindi nessun blocco inspiegabile, e
    il congegno diventa un elemento riconoscibile con la sua gag. Scartato
    perché, saputo dov'è, il trasferimento torna a essere un comando: cammini,
    usi, cambi personaggio, cammini. Costo in logistica, zero in trovata. È
    anche la soluzione meno originale disponibile. Nota: **è lo stesso codice
    della scelta adottata** — la differenza fra le due non è implementativa,
    è quanti passaggi ci sono e se sono sempre raggiungibili.
  - **Posare l'oggetto per terra** e farlo raccogliere a chiunque passi: la più
    generale di tutte, e regala il "lo lascio qui per dopo". Scartata perché
    costringe a decidere subito la persistenza dello stato di una stanza, che
    è ancora aperta, e perché ha lo stesso difetto della consegna a mano senza
    averne la naturalezza: "posa" sarebbe un quinto verbo.
  - **Nessun trasferimento**, con la cooperazione affidata solo alle azioni
    simultanee (uno tiene la leva, l'altro passa): scelta legittima e a costo
    zero. Scartata perché butta via l'esempio che il progetto cita come proprio
    e con esso metà del vocabolario del genere.
  - **Conseguenza accettata, ed è una richiesta alla storia che ancora non
    esiste**: i personaggi devono stare *strutturalmente* separati — piani
    diversi, lati opposti di una barriera, momenti diversi — non semplicemente
    trovarsi in stanze diverse. Se possono riunirsi quando vogliono, questa
    decisione non regge e conviene il congegno fisso. In Day of the Tentacle
    sono tre epoche, e non è colore: è ciò che rende sensato il resto.
  - Regalo collaterale: un passaggio con **un capo solo** è un nascondiglio.
    "Lascio qui il badge per dopo" funziona senza una riga in più.
  - I `cache_id` sono il secondo pezzo di stato persistente in `GameState`
    dopo i flag. Un oggetto imbucato non è in nessun inventario e in nessuna
    stanza: esiste solo lì in mezzo, ed è per questo che gli serve una casa
    che sopravviva allo scarico delle stanze.

- **Le parole sulla verb-coin cambiano con l'oggetto, le posizioni no.** Ogni
  hotspot può ribattezzare uno spicchio — la porta dice "Vai" e "Apri", la
  fessura dice "Ritira" — ma lo spicchio resta nella sua direzione e chiama lo
  stesso verbo. Cambia il vocabolario, non la geometria. **Superata due volte**
  — da "Vocabolario chiuso di nove parole" (le parole non sono più stringhe
  libere per hotspot) e poi da "Il ventaglio si compatta a partire da sinistra",
  in fondo all'elenco, che toglie anche la metà che qui era il punto: le
  posizioni non sono più fisse.
  Il motivo è che la scelta per direzione vive sul fatto che le quattro
  posizioni siano sempre le stesse: si mira senza leggere. Un elenco variabile
  in numero o in ordine trasformerebbe un gesto in un menù da consultare, con
  il dito sopra metà delle voci — cioè annullerebbe la ragione per cui il
  premi-trascina-rilascia è stato scelto.
  - **Spegnere gli spicchi che non si applicano** a questo oggetto: il
    giocatore vedrebbe a colpo d'occhio cosa è possibile. Scartata due volte.
    Per prima cosa in un punta-e-clicca quasi ogni oggetto rifiuta quasi ogni
    verbo, quindi si vedrebbe grigio quasi sempre e la moneta sembrerebbe
    rotta. Soprattutto, **rivelerebbe le soluzioni**: se "Apri" si accende solo
    sulle porte che si aprono davvero, il giocatore smette di provare e comincia
    a leggere il menù. In un LucasArts "Usa" era generico apposta — tentare
    *era* il gioco.
  - **Cambiare l'insieme degli spicchi** (la porta ne mostra tre, la macchina
    cinque): è il massimo dell'espressività ed è quello che si chiede
    d'istinto. Scartata perché è esattamente ciò che rompe il gesto.
  - Distinzione che regge e che vale come regola di scrittura: **un'etichetta
    che riflette uno stato visibile** (Apri/Chiudi su una porta che vedi
    com'è) non rivela niente; **uno spicchio che compare o sparisce in base a
    uno stato nascosto** rivela tutto.
  - Effetto collaterale utile: le quattro parole erano costanti dentro
    `verb_coin.gd`, che è il posto peggiore dove trovarle il giorno in cui si
    decide la lingua dei testi. Ora il default è lì e tutto il resto è dato.
  - Vincolo pratico: a font 8 uno spicchio tiene sì e no otto caratteri. Se
    servissero parole lunghe, la via è far scrivere la frase intera alla
    caption in alto mentre si trascina — proposta e messa da parte, non serve
    finché le etichette restano corte.
- **Il tocco secco esegue l'azione ovvia dell'oggetto** invece di non fare
  niente: premere e sollevare senza spostarsi esegue il `default_verb`
  dell'hotspot, che è Guarda quasi sempre e Vai sulle porte. Recupera un gesto
  che la decisione sul premi-trascina-rilascia aveva accettato di perdere.
  Annullare resta il cono verso il basso, che continua a esistere.
  - Distinguere il tocco secco dal trascinamento finito nel vuoto richiede di
    ricordare **se il dito è mai uscito dalla zona morta**, non solo dove si
    trova al rilascio: sono due esiti diversi che al momento del sollevamento
    si assomigliano.
  - Costo accettato: un tocco per sbaglio adesso *fa* qualcosa. È piccolo
    perché l'azione ovvia è per definizione quella innocua — e su una porta,
    attraversarla è precisamente ciò che il giocatore voleva.
- **Stato a due vie in `GameState`, accanto ai flag**: `is_on()` e
  `set_switch()`. I flag registrano che qualcosa è successo e non può
  disaccadere; una porta invece va avanti e indietro, e senza un posto dove
  ricordarlo si richiuderebbe da sola ogni volta che si esce dalla stanza.
  Non contraddice la decisione sui flag a senso unico, la completa: le due
  cose sono tenute separate proprio perché non poter disfare un flag è metà
  della sua utilità. È anche il primo pezzo della persistenza di stanza, che
  resta una decisione aperta.
  - **Un `bool` locale sulla porta**, non persistente: mezza riga, e la porta
    si richiude da sola al ritorno nella stanza. Scartata perché è una
    funzionalità che si dimentica, e "a seconda dello stato" senza stato non
    vuol dire niente.
  - **I due capi della stessa porta condividono lo `state_id`**, così aprirla
    da un lato la apre anche dall'altro. È la stessa idea del `cache_id` dei
    passaggi.

- **Gli spicchi della moneta sono badge tondi con un'icona, non parole**, e la
  parola contestuale la scrive la caption in alto mentre si trascina. Un'icona
  si legge in un colpo d'occhio e non va tradotta, ma può dire solo il verbo
  generico; il nome che *quell'oggetto* dà a quel verbo — "Apri" invece di
  "Usa" — va quindi dove c'è spazio e dove il dito non arriva mai.
  Le due cose insieme risolvono due problemi che si tenevano in ostaggio a
  vicenda: l'icona dà il riconoscimento immediato della posizione, la caption
  toglie il limite degli otto caratteri che un'etichetta disegnata sullo
  spicchio aveva.
  - **Un'icona per ogni verbo contestuale** (una per "Apri", una per "Ritira",
    una per "Svita"): sarebbe la soluzione più diretta. Scartata perché è una
    richiesta d'arte senza fine, e perché metà dei verbi che si vogliono
    scrivere non ha un disegno ovvio — "Raddrizza" non si illustra.
  - **Tenere le parole sugli spicchi**: nessun lavoro e nessun asset.
    Scartata perché a font 8 uno spicchio tiene sì e no otto caratteri, e
    perché durante il gesto il dito ne copre metà: la parola c'era ma non si
    leggeva quando serviva.
  - **Le icone sono SVG e non pixel art.** Un badge è ventiquattro unità di
    gioco, ma con `stretch/mode = canvas_items` il disegno avviene alla
    risoluzione reale della finestra, non a 384×216: su un telefono quelle
    ventiquattro unità sono più di cento pixel veri. Un'icona disegnata a
    ventiquattro pixel sarebbe l'unica cosa sgranata dello schermo.
  - Ne segue una conseguenza tecnica che vale la pena ricordare: il progetto
    imposta il filtro texture su `Nearest` per tutta la pixel art, e su queste
    quattro va sovrascritto a `TEXTURE_FILTER_LINEAR` sul nodo, o il vettore
    arriva con i bordi a scaletta e tanto valeva disegnarlo a mano.
  - **Se le icone non si caricano la moneta torna alle parole**, con un avviso.
    Un'immagine che manca deve costare le immagini, non il gioco.
  - La disposizione non cambia: stesse quattro direzioni, stessi angoli. I
    badge sono più piccoli delle etichette che sostituiscono, quindi la moneta
    occupa meno schermo di prima.

- **Vocabolario chiuso di nove parole in quattro famiglie**, invece di
  etichette libere scritte oggetto per oggetto: **Guarda**; **Prendi**;
  **Usa, Premi, Tira, Apri, Chiudi**; **Parla, Vai**. Ogni famiglia ha una
  posizione fissa sulla moneta, e una parola non cambia mai direzione.
  **Parzialmente superata due volte** — da "Da nove parole a sette", che porta
  l'elenco a sette togliendo Premi e Tira, e da "Il ventaglio si compatta a
  partire da sinistra", che toglie le posizioni fisse. Le **famiglie** restano, e
  restano l'unità di cui si parla: quello che cambia è che il loro ordine
  decide la sequenza del ventaglio invece di quattro direzioni sullo schermo.
  Nove parole che il giocatore impara una volta valgono più di parole inventate
  di volta in volta: con l'elenco chiuso il vocabolario diventa qualcosa che si
  possiede e si applica, invece di qualcosa da leggere a ogni oggetto. E il
  principio della decisione precedente regge intatto — quello che varia è
  *quale parola della famiglia* è in scena, mai dove la famiglia sta.
  - **Verificato che le famiglie non vadano in conflitto**: nessun oggetto
    sensato ne vuole due della stessa famiglia insieme. Una porta non ha
    nessuno con cui parlare, una persona non è un posto dove andare — per
    questo Parla e Vai possono condividere una casella senza pestarsi i piedi.
  - **Le caselle vuote non si disegnano.** Prima ero contrario a nascondere gli
    spicchi, ma l'obiezione era un'altra: che uno spicchio comparendo e
    sparendo *in base a uno stato nascosto* rivelasse le soluzioni. Qui
    l'insieme è una **proprietà statica dell'oggetto** — una porta ha sempre
    Apri, che sia chiusa a chiave o no — e solo *quale* parola sta nella
    casella segue lo stato **visibile**. È la linea da tenere anche in
    scrittura: riflettere ciò che si vede sì, annunciare ciò che funziona no.
  - **"Dai" è stato tolto dall'elenco** ed è rimasto solo come frase: dare un
    oggetto a qualcuno è già "usa l'oggetto su di lui", e uno spicchio "Dai"
    non sarebbe mai raggiungibile — quando hai qualcosa in mano la moneta non
    si apre più. Scartate: farlo aprire l'inventario (un secondo percorso per
    la stessa cosa) e farlo sostituire "Prendi" nella casella della mano
    (elegante, ma una regola in più da capire).
  - **L'icona segue la parola, non la posizione**: sulla porta la casella di
    destra mostra una freccia, su una persona un fumetto. Si vede a colpo
    d'occhio che quella porta è un posto e non un interlocutore.
  - Ricaduta pratica: **il vocabolario sta tutto in una tabella sola** dentro
    `verb_coin.gd`, parola e icona per verbo. È il posto da cui partire il
    giorno in cui si decide la lingua dei testi — non c'è una parola di verbo
    da nessun'altra parte.
  - Conseguenza per gli hotspot: i testi passano da uno per verbo a **uno per
    famiglia** (`look_text`, `hand_text`, `act_text`, `reach_text`). Quattro
    campi come prima, ma reggono un elenco più lungo di quattro parole — nove
    allora, sette da quando Premi e Tira sono stati eliminati.

- **Le icone dei verbi sono cartoon a colori**, non sagome bianche:
  riempimenti piatti e vivaci, contorno scuro spesso, un solo tocco di luce
  per icona, e una tavolozza condivisa così che si leggano come un insieme e
  non come disegni scollegati. Il motivo è che su un badge di ventiquattro
  unità, con il dito lì accanto e mezzo secondo di gesto, **il colore arriva
  prima della forma**: il giallo del vano di "Apri" si distingue ancora prima
  di essere riconosciuto come una porta, mentre due sagome dello stesso bianco
  vanno confrontate. Il vocabolario è chiuso e le posizioni sono fisse, quindi
  il giocatore impara i colori una volta e poi mira senza leggere — che è
  esattamente ciò su cui il premi-trascina-rilascia vive.
  - **Sagome bianche monocromatiche** (com'erano): un colore solo, nessuna
    tavolozza da mantenere, contrasto garantito su qualunque fondo e nessun
    rischio di stonare con la pixel art che arriverà. Vantaggi veri. Scartate
    perché buttano via il canale d'informazione più rapido che l'interfaccia
    ha a disposizione, proprio nel punto in cui il tempo di lettura conta.
  - **Contorno chiaro tipo adesivo** (un anello panna attorno a ogni sagoma):
    farebbe staccare le icone da qualunque fondo, badge compreso. Scartato
    perché a questa dimensione un anello in più per forma impasta i dettagli
    interni — e non serve, dato che il badge scuro è sempre lì sotto.
  - Il contorno è scuro (`#2b2135`) e quasi indistinguibile dal fondo del
    badge: la silhouette la porta il riempimento chiaro, e il contorno lavora
    **dentro** l'icona, a separare le parti. È il motivo per cui ogni
    riempimento deve restare chiaro — un'icona in tinte scure sparirebbe.
  - Vincolo per le icone future: stessa tavolozza, stesso spessore di
    contorno, e massa del disegno entro un raggio di circa 11 unità dal
    centro, o gli angoli spuntano fuori dal badge tondo.
  - **Un'icona fatta di più parti che devono leggersi come una sola sagoma si
    disegna due volte**: prima tutte le parti con riempimento *e* contorno
    scuri, che allargandole le fonde in un'unica silhouette, poi le stesse
    parti in colore sopra, senza contorno. Ne resta un contorno continuo e
    nessuna giunzione interna. È il modo di ottenere l'unione di forme senza
    operazioni booleane, che l'SVG non ha. La mano di "Prendi" è nata così
    dopo che tre tentativi a rettangoli affiancati erano rimasti illeggibili:
    le dita si vedevano incollate al palmo invece di uscirne.
  - Corollario di quella tecnica, e vale per qualunque cosa abbia dita o
    rebbi: **le parti vanno attaccate alla base e divaricate in punta**. Il
    contorno che allarga le forme chiude i vuoti stretti, quindi due parti
    parallele si fondono per tutta la lunghezza e diventano una macchia. È
    l'apertura a ventaglio a scavare le valli che si vedono.
- **Le icone si vettorizzano da immagini di riferimento, non si disegnano a
  mano** (revoca del modo di produrle, non dello stile: cartoon a colori,
  contorno scuro spesso e tinte piatte restano). Tutte quante — Guarda,
  Prendi, Usa, Apri, Chiudi, Parla, Vai — sono il tracciamento di immagini
  scelte dallo sviluppatore.
  Il motivo è misurato, non teorico: la sola mano di "Prendi" ha richiesto
  sei tentativi disegnati (palmo aperto, guanto, pugno, mano dall'alto, mano
  protesa, mano con oggetto), tutti scartati, e ha funzionato al primo colpo
  partendo da un'immagine. A ventiquattro unità la differenza tra una forma
  riconoscibile e una macchia è di frazioni di unità, e l'occhio perdona meno
  dove il soggetto è familiare — una mano, una bocca, un occhio.
  Tutte e sette vengono da immagini: Guarda un occhio, Prendi un palmo aperto,
  Usa un ingranaggio, Apri e Chiudi la stessa porta, Parla una bocca, Vai due
  piedi che camminano.
  - **Continuare a disegnare a mano**: file da mezzo kilobyte, geometria
    leggibile e modificabile spostando un numero, tavolozza garantita.
    Vantaggi reali, ed è il motivo per cui Vai è rimasta così. Scartato per
    le altre otto perché il costo non sta nel disegnare, sta nell'*avvicinarsi*:
    ogni giro richiede di guardare il risultato sul badge e ricominciare, e su
    soggetti familiari i giri non convergono.
  - **Tenere le immagini come PNG** invece di tracciarle: nessuna perdita di
    dettaglio e nessun passaggio in più. Scartato perché il badge si disegna
    alla risoluzione reale della finestra, non a 384×216: un raster andrebbe
    esportato per la scala peggiore e resterebbe l'unica cosa morbida dello
    schermo. Il tracciato scala come il resto.
  - Come si toglie lo sfondo, che è la parte non ovvia: **per colore, e con
    due eccezioni che si contraddicono**. Il buco centrale di un ingranaggio
    è azzurro come il fondo e deve diventare trasparente, quindi non basta
    togliere ciò che è connesso al bordo; il bianco della sclera di un occhio
    non è azzurro e deve restare, quindi non si può togliere tutto il chiaro.
    La regola che regge entrambi: trasparente ciò che è azzurro, poi si tiene
    la sola componente connessa più grande — che butta via la cornice del
    riquadro e le stelline decorative senza nominarle.
  - **L'ingombro nel badge va calcolato, non stimato**: si misura il raggio
    massimo dei pixel opachi dal centro e si scala perché stia all'85% del
    semilato. Senza questo passaggio le punte (dita, pollice, spigoli)
    attraversano il bordo illuminato, e il tracciamento non ha modo di
    saperlo da sé. È l'unica cosa che l'automatismo non sa fare.
  - **Un'immagine può mostrare il soggetto e non il verbo**, e allora il
    rimedio è chiedere un'altra immagine, non aggiustarla. Imparato su un
    riferimento che era un dorso di mano e nient'altro: composto a mano
    (tagliato al polso, girato verso il basso, posato su un pulsante
    disegnato) funzionava, ma è stato sostituito appena arrivata un'immagine
    che il gesto lo mostrava già. La regola che resta: **serve il bersaglio,
    non solo la parte del corpo**. Una mano che preme senza qualcosa sotto non
    è distinguibile da una mano.
  - **Apri e Chiudi vengono dalla stessa immagine**: il battente della porta
    aperta è raddrizzato dentro il vano con una trasformazione prospettica, e
    traversa e soglia sono ricostruite ripetendo una colonna di telaio, perché
    nell'originale il battente le copre. Non sono due disegni che si
    somigliano, è la stessa porta in due stati — che è la ragione per cui le
    due parole condividono una casella.
  - Conseguenze da sapere: i file pesano dai 15 ai 50 kilobyte invece di
    mezzo, hanno `viewBox` 512 invece di 24, e i loro tracciati **non si
    modificano a mano** — per cambiare un'icona si rifà il passaggio
    dall'immagine. Il contorno non è più il `#2b2135` comune ma quello del
    riferimento, diverso per ognuna: su un badge scuro non si distinguono, ma
    se il badge diventasse chiaro andrebbero allineati tutti.
  - Costo accettato: la **tavolozza condivisa non è più garantita**. Ogni
    icona porta le tinte della propria immagine, e a tenerle insieme oggi c'è
    solo il fatto che i riferimenti sono nati dallo stesso generatore. Se un
    domani un'icona arrivasse da un'immagine con altri colori, stonerebbe — e
    il rimedio è ridurne le tinte a quelle delle altre, non ridisegnarla.
  - **Un soggetto molto più alto che largo va ritagliato, non rimpicciolito**:
    il badge è tondo, quindi un'immagine allungata ci entra inscritta nella
    diagonale e diventa minuscola. I piedi di "Vai" sono tagliati alle
    caviglie — a figura intera erano due strisce, ai soli piedi due blocchi
    irriconoscibili. Il taglio giusto sta in mezzo e si trova guardando le
    varianti alla dimensione vera, non ragionandoci.
  - Nota metodo, e vale per il prossimo giro: le icone si giudicano **a 120
    pixel**, che è quanto è grande un badge su un telefono (ventiquattro unità
    a 5×). Ingrandite sembrano tutte buone; a quella dimensione due terzi dei
    tentativi cadono.
  - Nota: da rivedere se il badge diventasse chiaro. Il contorno scuro regge,
    ma i riferimenti sono tutti in gamma pelle e panna, quindi su un fondo
    chiaro perderebbero contrasto tutti insieme, non uno o due.

- **Da nove parole a sette: Premi e Tira sono eliminati** (revoca parziale del
  vocabolario chiuso, non del suo principio: famiglie e posizioni fisse
  restano — le posizioni fisse solo fino a "Il ventaglio si compatta a partire
  da sinistra", più sotto, e restano **Guarda**; **Prendi**; **Usa, Apri, Chiudi**;
  **Parla, Vai**). Le due parole stavano nella stessa famiglia di Usa, quindi
  **non compravano una posizione sulla moneta**: qualunque cosa facessero, la
  facevano dalla stessa casella e con lo stesso gesto di Usa. Il costo invece
  era per oggetto — due parole in più da imparare, e per lo scrittore la
  domanda "questa leva si tira o si usa?" a ogni hotspot, che è una scelta
  senza risposta giusta e quindi senza informazione per il giocatore. Quel che
  l'oggetto fa quando lo usi è affare del testo, non del verbo.
  - **Tenerle**: distinguono azioni fisicamente diverse, e in un enigma
    meccanico "tira" contro "premi" può essere la soluzione. Vantaggio reale, e
    il motivo per cui c'erano. Scartate perché quella distinzione, se un giorno
    servisse, si esprime meglio come *due hotspot* — la leva e il pulsante sono
    oggetti diversi — che come due parole sullo stesso oggetto.
  - Conseguenza tecnica da non ripetere a vuoto: gli `@export` di tipo enum
    sono salvati nelle scene **come interi**, quindi togliere due valori in
    mezzo all'elenco fa slittare tutti quelli dopo. Le due stanze avevano
    `reach_verb = 9` per Vai e `reach_verb = 8` per Parla, che senza intervento
    sarebbero diventati un verbo inesistente e Chiudi. Chi tocca l'enum
    aggiorna le scene nello stesso commit, o il gioco cambia comportamento in
    silenzio.
  - I due hotspot che li usavano passano a Usa e **si tengono i loro testi**:
    il distributore diceva già "Premi i pulsanti uno dopo l'altro" e il
    cartello "Tiri il cartello verso di te". È la prova del ragionamento —
    l'azione precisa era nel testo anche quando il verbo la nominava.
  - Le due icone (mano sul pulsante, pugno con la corda) sono cancellate dal
    progetto. Restano nella cronologia di git se un giorno le due parole
    tornassero.

- **Una condizione è una stringa con un prefisso**, non una risorsa tipizzata:
  `taken:sticker`, `!on:hallway_door`, `has:screwdriver`, `in:wall_slot`,
  `who:Player2`. Senza prefisso è il nome di un flag. Una lista di condizioni è
  un **AND**, e per un OR si scrive la voce due volte.
  La grammatica sta tutta in `Conditions`, una classe di soli metodi statici —
  GDScript non ha classi statiche, ma una classe che non si istanzia mai è
  l'equivalente idiomatico. Non sta in `GameState` perché quello è tenuto di
  soli dati, com'è scritto più sopra.
  Il motivo della forma a stringa è che in questo progetto **un flag è già una
  stringa dappertutto**: `accepted_flag`, `state_id`, `cache_id` sono tutti
  `StringName` scritti a mano, e `PickupHotspot` costruisce `taken:<id>` da sé.
  La forma tipizzata comprerebbe sicurezza su un caso su sei e la pagherebbe con
  un blocco di sotto-risorsa su tutti e sei, in un progetto dove le scene si
  scrivono come testo.
  - **Risorsa `Condition` con enum e parametri tipizzati**: un riferimento a
    `InventoryItem` si rompe rumorosamente se rinomini l'oggetto, e l'editor
    saprebbe cosa offrirti. Vantaggi veri. Scartata per la verbosità: le
    condizioni saranno centinaia e ognuna costerebbe otto righe, contro una.
  - **Espressioni valutate con la classe `Expression` di Godot**: un campo solo
    e sintassi arbitraria. Scartata perché è la strada che porta ad avere un
    mini-linguaggio non documentato che fallisce a runtime.
  - **Costo accettato, e non aggirabile: un refuso non viene segnalato.**
    `taken:stiker` è una condizione perfettamente ben formata su un flag che
    nessuno alzerà mai, e `hass:key` pure. L'unico controllo possibile è
    sull'argomento vuoto (`on:`), che è sempre uno sbaglio; distinguere un nome
    sbagliato da un nome non ancora alzato non si può, con nessuna delle tre
    alternative.
  - Nota: da rivedere verso la risorsa tipizzata se un giorno esistesse un
    editor di condizioni, o se i refusi diventassero una fonte reale di tempo
    perso invece di un rischio teorico.

- **Persistenza dello stato di stanza: `present_if` e le varianti sull'hotspot**
  — chiude il punto che era rimasto aperto. Ogni `Hotspot` porta due cose nuove:
  un elenco di condizioni che devono valere perché sia lì (`present_if`) e un
  elenco di `HotspotVariant`, ognuna con le proprie condizioni e i propri quattro
  testi, che prendono il posto dei suoi mentre reggono. `GameState` guadagna
  `switch_changed`, gemello di `flag_raised`.
  Il motivo di metterlo **sull'hotspot** e non altrove è che l'oggetto che varia
  è l'unico che sa di variare, e ogni hotspot lo eredita gratis senza uno script.
  - **Un nodo `RoomRules` nella stanza**, con una tabella "se flag X → nascondi
    il nodo Y": tutta la variazione di una stanza si leggerebbe in un punto solo,
    che è un pregio reale. Scartata perché le regole nominerebbero i nodi per
    percorso, e i percorsi stringa si rompono in silenzio quando un nodo viene
    rinominato — esattamente ciò che il progetto ha già deciso di evitare per i
    riferimenti.
  - **Uno script per ogni hotspot che varia**: zero concetti nuovi, massima
    libertà, ed è ciò che si stava già facendo. Scartata perché "cambia dopo che
    è successo X" sarà la variazione più comune del gioco, e la decisione
    "hotspot come dati più segnale" esiste proprio per non scrivere un file per
    oggetto.
  - **Le varianti si valutano quando si fa la domanda, non quando la stanza si
    costruisce.** Se si calcolassero all'ingresso, aprire una porta e poi
    guardarla darebbe la descrizione della porta ancora chiusa.
  - **Le varianti cambiano i testi, mai quali verbi ci sono.** È la regola già
    scritta più sopra: una parola può seguire uno stato **visibile**, ma uno
    spicchio che compare solo quando funzionerebbe rivelerebbe la soluzione. Un
    oggetto le cui parole devono davvero cambiare è un hotspot con uno script,
    come `DoorHotspot`.
  - **Un hotspot assente viene nascosto e smette di rispondere, non liberato**
    (`collision_layer` a zero, differito perché un flag può essere alzato dentro
    un passo di fisica). Così può tornare quando le condizioni si girano — cosa
    che `queue_free()` rendeva impossibile. Ne segue una convenzione per le
    stanze: **la figura di un hotspot va messa come suo figlio**, o resterebbe
    visibile mentre nulla risponde.
  - `PickupHotspot` perde il suo `_ready()` e il suo `queue_free()`: sparisce
    perché alza il flag, come qualunque altro. Si tiene `taken_text`, che è la
    scorciatoia per una variante su `taken:<id>` — due campi invece di un blocco,
    e il flag lo ricava dall'oggetto.
  - Limite noto e accettato: la presenza si ricalcola all'ingresso nella stanza,
    a ogni flag, a ogni interruttore e al cambio di personaggio, **non** quando
    qualcuno prende o posa un oggetto. Un `has:` in `present_if` sarebbe quindi
    in ritardo. Non è un problema oggi perché "dipende da cosa hai in tasca"
    appartiene alle varianti e ai dialoghi, che si valutano alla domanda.

- **Dialoghi: risorse `.tres` per il modello, elenco di opzioni in basso per la
  UI.** Una conversazione è un insieme di nodi; ogni nodo è una battuta più un
  elenco di opzioni; ogni opzione ha testo, condizioni, effetti e dove porta.
  - **File di testo con un formato minimo e un parser** (~150 righe): una
    conversazione si leggerebbe come un copione, compatta e diffabile, ed è il
    contenuto che crescerà di più. Vantaggio reale. **Rimandata, non scartata**:
    il runtime consuma risorse, quindi un parser testo→risorsa si aggiunge dopo
    senza toccarne una riga. Sceglierlo adesso significherebbe sceglierlo prima
    di aver scritto un solo dialogo vero.
  - **Dizionari GDScript dentro un `.gd`**: nessun parser e i refusi di forma li
    prende `gdparse`. Scartata perché mette il contenuto dentro i file di codice
    e non ha nessun tipo.
  - **Un albero di nodi nella scena**: visibile nell'editor. Scartata perché un
    dialogo non è spaziale, è dato, e le scene diventerebbero enormi.
  - **UI: opzioni a raggiera come la verb-coin.** Sarebbe la scelta coerente col
    gesto. Scartata perché le opzioni sono frasi, non icone, e oltre quattro non
    ci stanno: la moneta vive su un vocabolario chiuso e fisso, un dialogo è
    l'esatto contrario.
  - **UI: opzioni sospese vicino al personaggio.** Più bella e non coprirebbe la
    scena con un pannello. Scartata perché a 384×216 le frasi si accavallano.
  - Costo accettato: l'elenco in basso mangia il terzo inferiore dello schermo,
    ma solo mentre si parla. Le battute passano dalla `Caption` che esiste già, e
    chi parla si distingue col colore; il testo sospeso sopra la testa è
    lucidatura da fare dopo.
  - Conseguenza: mentre un dialogo è aperto **la stanza smette di ascoltare** —
    niente camminate, niente verb-coin, niente cambio personaggio. È un `Control`
    a schermo pieno, la stessa tecnica che la moneta usa già.
  - Scritte in implementazione, le regole che il modello ha dovuto darsi:
  - **Il primo elemento dell'elenco è l'inizio**, invece di un campo che nomina
    la battuta d'apertura: un campo in meno da tenere allineato quando si
    riordinano le battute.
  - **Rispondere e andare altrove si escludono.** Un'opzione che resta dov'è dice
    il proprio `reply`; una che porta a un'altra battuta fa dire a quella il suo
    `says`. Scriverli entrambi è un errore e viene segnalato, perché sulla
    caption ce n'è posto per uno solo. Ne segue che l'elenco di argomenti — il
    caso più comune del genere — costa una battuta sola con tante opzioni,
    invece di una battuta per argomento.
  - **Niente interruttore "chiedibile una volta sola".** Si esprime già con due
    campi che ci sono comunque: `conditions = ["!chiesto_x"]` più
    `raises = ["chiesto_x"]`. Un flag dedicato andrebbe ricavato dalla posizione
    dell'opzione nell'elenco o dal suo testo, e cambiano entrambi quando si
    riscrive una conversazione — cioè esattamente quando un "una volta sola" non
    deve azzerarsi di nascosto.
  - **Una battuta che non offre niente di dicibile chiude la conversazione.** Il
    campo `ends` serve quindi solo al congedo esplicito messo accanto ad altre
    opzioni ancora valide.
  - **Il pannello è modale ingoiando i click**, non spegnendo i sistemi uno per
    uno: la stanza ascolta in `_unhandled_input`, quindi un evento marcato come
    gestito nel pannello non la raggiunge mai. Barra dei personaggi e zaino
    vengono nascosti perché sarebbero comunque bottoni morti, e un bottone morto
    è peggio di un bottone assente.
  - **Chi parla è un colore, non un nome**: la caption è la stessa che usano il
    narratore e gli oggetti, e `Dialogue.speaker_color` la tinge. Le battute
    dell'interlocutore restano finché non si sceglie — svanissero, porterebbero
    via la domanda mentre il giocatore legge le risposte — mentre la frase del
    giocatore non viene ripetuta da nessuna parte: è scritta sul bottone che ha
    appena premuto.
  - **Parlare è un dato dell'hotspot, non un `TalkHotspot`**: chi ha qualcosa da
    dire non ha comportamento speciale, ha solo `dialogue`. Un hotspot che offre
    Parla *senza* un dialogo resta valido e utile — è il modo in cui un oggetto
    risponde all'idea di essere interpellato con una battuta sola.

- **La caption va a capo e resta a schermo in proporzione a quanto è lunga.**
  Due difetti trovati provando i dialoghi sul dispositivo, non a tavolino: una
  battuta lunga usciva dai bordi dello schermo, e spariva prima di essere stata
  letta. Ora il `Label` è alto quattro righe con `autowrap_mode`, e la durata è
  `max(minimo, caratteri × secondi_per_carattere)`.
  - **Una durata fissa più lunga**: mezza riga di modifica. Scartata perché il
    problema non è la lentezza in assoluto — la stessa caption dice "Guarda" e
    una frase di cento caratteri, e una durata che va bene per la seconda lascia
    la prima ferma sullo schermo per un'eternità.
  - **Il minimo è un pavimento, non una base**: una frase lunga non si prende il
    minimo *in più* del suo tempo di lettura, ci mette semplicemente più del
    minimo a essere letta. Sommarli dava otto secondi per una riga sola.
  - **Avanzamento a click invece che a tempo** (si tocca per proseguire): è quel
    che fanno molti del genere e toglie del tutto il problema della durata.
    Scartato per ora perché la caption è usata anche per cose che non sono
    battute — il rifiuto generico, la parola sotto il dito durante il gesto —
    e un tocco obbligatorio su quelle sarebbe un impaccio. Da riconsiderare
    quando i dialoghi saranno lunghi davvero.
  - I due valori sono `@export` sul nodo `Caption` in `Main.tscn`: il giorno in
    cui esisterà una schermata di impostazioni, "velocità dei testi" sono questi
    due numeri in un posto solo e non una ricerca nel codice.

- **Il ventaglio si compatta a partire da sinistra** (revoca delle posizioni
  fisse sulla verb-coin, che erano il cuore di due decisioni più sopra). Si
  disegnano solo i verbi che l'oggetto offre davvero: il primo a sinistra del
  punto toccato, gli altri a ventaglio verso l'alto e verso destra, 60° l'uno
  dall'altro e senza buchi in mezzo. L'ordine di riempimento è quello delle
  famiglie nel loro ordine di sempre — guardare, poi le mani, poi cosa gli fai,
  poi dove porta o chi è — quindi **un oggetto che offre tutti e quattro i verbi
  ha esattamente il disegno di prima**, e cambiano solo quelli che prima
  mostravano dei vuoti.
  Il motivo è che le caselle vuote non si leggevano come "questo oggetto non fa
  quella cosa": si leggevano come una moneta rotta, e lasciavano direzioni morte
  in mezzo al gesto.
  - **Tenere le posizioni fisse con i buchi** (com'era): è la scelta che regge
    "si mira senza leggere", ed era un vantaggio reale — con l'elenco chiuso il
    giocatore imparava una volta dove sta ogni famiglia e non doveva più
    guardare. Scartata perché quel vantaggio si paga su *ogni* oggetto, e la
    maggioranza degli oggetti usa due o tre famiglie su quattro: il caso raro
    era pieno, il caso normale era bucato.
  - **Distribuire i verbi presenti su tutto il semicerchio** (due verbi a 180°
    l'uno dall'altro, tre a 90°): darebbe i bersagli più larghi possibili.
    Scartata perché un verbo finirebbe in una direzione diversa a seconda di
    quanti ce ne sono, mentre così **l'i-esimo spicchio è sempre allo stesso
    angolo**: il primo è sempre a sinistra, il secondo sempre in alto a
    sinistra. Si perde la memoria della famiglia, non si perde ogni memoria.
  - **Ventaglio da destra invece che da sinistra**: identico per costo, ed è
    come è stato scritto la prima volta. L'argomento a favore era che la mano
    che tiene il telefono copre più facilmente il lato da cui il ventaglio
    parte. Scartato perché partire da sinistra tiene **Guarda al suo posto di
    sempre** — è il verbo più usato del gioco e l'unico che ogni oggetto offre,
    quindi è quello che vale la pena non spostare mai. Da destra, Guarda era il
    solo che finiva in una posizione diversa a ogni oggetto.
  - Costo accettato, ed è quello che le decisioni precedenti temevano: **una
    parola non sta più sempre nello stesso posto.** Parla è a destra su un
    oggetto con quattro verbi e in alto a sinistra su uno che offre solo Guarda
    e Parla. La scelta resta per direzione e i badge restano visibili, quindi il
    gesto non cambia — ma va guardato più di prima, almeno finché non ci si
    abitua.
  - Il costo però **non tocca Guarda**, ed è il regalo di questa direzione:
    Guarda è il primo della fila e ogni oggetto lo offre, quindi è sempre il
    badge di sinistra. Il verbo più usato del gioco resta l'unico che si può
    ancora tirare senza guardare.
  - Effetto collaterale tecnico: il passo passa da ~50° a 60°, cioè i bersagli
    sono più distanti fra loro di prima e non più vicini. La tolleranza resta 50°
    perché non è un confine — vince il badge più vicino — ma è la distanza oltre
    la quale il dito non punta più a niente, ed è ciò che tiene libero il cono
    verso il basso per annullare.
  - Le posizioni non sono più una tabella di quattro offset ma un calcolo su
    seno e coseno: una tabella dovrebbe avere una riga per ogni *numero* di
    verbi in scena, non per ogni verbo.

- **Salvataggio: `ConfigFile` in `user://`, oggetti nominati per `id` tramite un
  catalogo, e ogni pezzo che si serializza da sé.** Fatto prima del prototipo e
  fuori sequenza, perché è l'unica parte dell'ossatura il cui costo cresce a
  ogni sistema aggiunto: oggi lo stato di una partita sta in due posti soli — i
  tre dizionari di `GameState`, e inventario/stanza/posizione su ogni
  personaggio — e la domanda "cos'è esattamente lo stato di una partita" ha una
  risposta netta che fra sei sistemi non avrebbe più.
  Quale stanza è sullo schermo **non** si salva: è `active_character.current_room`,
  come già deciso. E una partita non può essere salvata a metà conversazione,
  perché il pannello dei dialoghi ingoia i click e il menù è irraggiungibile —
  un vincolo che arriva gratis dalla modalità del pannello invece che da un
  controllo scritto apposta.
  - **Oggetti per percorso del file** invece che per `id`: zero infrastruttura,
    nessun catalogo da tenere in step. Scartata perché spostare o rinominare un
    `.tres` romperebbe ogni salvataggio in silenzio, e il commento su
    `InventoryItem.id` prometteva già il contrario — *"a saved flag refers to
    the id, not to the file"*.
  - **Scansione della cartella `resources/items/`** invece del catalogo: niente
    da mantenere a mano, ed è la soluzione più pulita sulla carta. Scartata
    perché in un progetto **esportato** Godot converte le risorse e i nomi su
    disco smettono di essere quelli che si vedono qui — ed è esattamente il tipo
    di cosa che da questa macchina non si può verificare.
  - **JSON** invece di `ConfigFile`: universale e leggibile. Scartato perché
    trasforma ogni numero in `float` e perde i tipi di Godot: ogni `Vector2`
    andrebbe smontato in due numeri e rimontato, e ogni conversione evitata è
    una conversione che non può sbagliare. `ConfigFile` è testo leggibile lo
    stesso, che è ciò che conta per debuggare da un telefono.
  - **Dump binario (`store_var`)**: compatto e senza conversioni. Scartato
    perché un salvataggio che non si può aprire e guardare non si può debuggare,
    e qui la macchina di sviluppo e il dispositivo di prova sono lo stesso
    telefono.
  - **Una `SaveGame` che sa tutto** e legge dentro gli altri: meno file.
    Scartata perché andrebbe a frugare in campi con l'underscore davanti, che in
    GDScript non è un divieto ma è l'unico segnale di intenzione che esiste.
    Così invece `GameState` e `PlayerCharacter` espongono `capture()`/`restore()`
    dei propri dati — serializzare sé stessi è *essere* i dati, non fare
    qualcosa al mondo, quindi la regola che tiene il comportamento fuori
    dall'autoload regge.
  - **Versione che rifiuta invece di migrare**: un file di versione diversa non
    si legge. Durante lo sviluppo i salvataggi sono usa e getta, e una
    migrazione scritta alla cieca è peggio di un rifiuto onesto.
  - **La versione copre anche la geometria delle stanze**, non solo la forma del
    file: si alza quando una navmesh si sposta. Una posizione salvata ha senso
    solo contro il pavimento su cui stava, e chi si ritrova fuori dalla mesh non
    ottiene percorso — un agente senza percorso restituisce la propria posizione
    come prossimo angolo, quindi il personaggio resta fermo per sempre e ogni
    tocco successivo non fa niente. È un soft lock, e un soft lock vale una
    versione. Scartato **lasciarli caricabili** (il file si legge ancora, quindi
    "tecnicamente" va bene: ma il sintomo è il gioco bloccato senza spiegazione,
    che è il caso peggiore di tutti) e scartata la **migrazione delle posizioni**
    verso il punto calpestabile più vicino, che è indovinare dove uno *voleva*
    stare mentre lo stesso salvataggio porta anche flag e oggetti di un mondo di
    prima. Il rimedio automatico resta comunque in `room.gd`, per chi si trovi
    fuori mesh per qualunque altra ragione.
  - **Chi offre di caricare chiede `is_loadable()` e non `exists()`**: da quando
    la versione può rifiutare un file, esserci e potersi leggere hanno smesso di
    essere la stessa cosa, e "Continua" tornerebbe a essere la voce che risponde
    «non c'è niente che io sappia leggere» — cioè proprio quello che la decisione
    su Continua voleva evitare. Per la stessa ragione `newest_slot()` considera
    solo gli slot leggibili: altrimenti sceglierebbe il file più recente proprio
    perché è il più recente fra quelli che non si possono aprire.
  - **Caricare non emette `flag_raised` uno per uno**: caricare non è cento cose
    che accadono, è un mondo diverso. La stanza viene buttata via e ricostruita,
    e i suoi hotspot si ricalcolano da soli salendo — che è più semplice e dà
    lo stesso risultato.
  - **"Nuova partita" ricarica la scena** invece di rimettere a posto ogni
    personaggio a mano: dove uno comincia è scritto in `Main.tscn` e in nessun
    altro posto, quindi ricaricare è l'unico modo che non può sbagliare.
    `GameState` sopravvive al ricaricamento, ed è per questo che va svuotato
    prima.

- **Salvataggio automatico in uno slot suo, all'attraversare una porta.** Due
  slot separati (`manual` e `auto`) e non uno: camminare attraverso una porta
  non deve poter sovrascrivere una partita che qualcuno ha scelto di tenere.
  - **Il momento in cui scatta** è il cambio stanza, e nient'altro. Non
    all'avvio, che sovrascriverebbe proprio il checkpoint che l'automatico
    esiste per conservare; non al cambio personaggio, dove non è successo
    niente. Attraversare una porta è l'unico momento che è insieme un
    cambiamento vero e un posto naturale a cui tornare.
  - **Caricamento automatico all'avvio**: scartato. Toglierebbe il bisogno del
    menù, ma renderebbe impossibile ricominciare puliti senza cancellare un
    file a mano — e in fase di sviluppo si riparte da capo venti volte al
    giorno.
  - Aggiunto anche su `NOTIFICATION_APPLICATION_PAUSED`, perché su un telefono
    un gioco non si chiude, si scarta con il pollice. **Non verificabile da
    qui**: se quella notifica non arrivasse, l'automatico al cambio stanza
    regge da solo.

- **Un pannello "Menù" come primo pezzo del guscio.** Non c'è ancora una
  schermata iniziale né una pausa, e il bottone accanto allo zaino esiste perché
  un salvataggio che nessuno può chiedere non è verificabile. È costruito per
  diventare il menù di pausa e non per essere buttato: le voci sono una tabella,
  e le impostazioni saranno un'altra riga.

- **Localizzazione: chiavi nelle scene, testi in `resources/text/`.** Chiude il
  punto che era rimasto aperto sulla lingua. Dove c'era una frase adesso c'è una
  chiave (`ROOM_TEST_CRATE_LOOK`), e le frasi stanno tutte in un `.tres` per
  lingua — oggi italiano e inglese. Chi traduce è **l'interfaccia**: hotspot,
  oggetti, dialoghi e sequenze restituiscono chiavi, e caption, pannelli e
  bottoni chiamano `tr()` nel momento in cui scrivono.
  - **Il CSV importato di Godot**, che è la via documentata: scartato perché i
    `.translation` che ne escono non esistono finché qualcuno non apre il
    progetto, e vanno registrati in `project.godot`, che l'editor riscrive
    quando vuole. Sono due cose da cui questo progetto è già stato morso. Un
    `.tres` invece è una risorsa come tutte le altre — esportata, caricata con
    `load()`, testo in un diff, nessun passo di import fra lo scriverla e
    l'eseguirla — e diventa comunque una vera `Translation` nel
    `TranslationServer`, quindi `tr()` funziona ovunque.
  - **Tenere l'italiano come sorgente** e tradurre italiano→inglese: le scene
    sarebbero rimaste leggibili da sole, che è un vantaggio reale. Scartata
    perché correggere un accento scollegherebbe la traduzione, e il sintomo
    sarebbe silenzioso — in inglese ricomparirebbe la frase italiana.
  - Costo accettato: **una stanza non si legge più aprendo il suo `.tscn`**.
    Vale meno di quanto sembri perché quei file li scrive Claude, non lo
    sviluppatore, e in cambio tutta la scrittura del gioco finisce in due file.
  - L'unica riga assemblata invece che cercata è quella del passaggio
    (`"Prendi %s."` più i nomi): traduce da sé, perché quel che ne esce è già
    una frase e `tr()` su una frase la restituisce.
  - **`Settings` è il secondo autoload**, separato da `GameState`: caricare una
    partita non deve cambiare la lingua, e cominciarne una nuova non deve
    azzerare le impostazioni. È anche l'unico posto che gira prima di ogni
    scena, che è dove le lingue vanno installate. Senza file di impostazioni
    segue la lingua del sistema se il gioco la parla, altrimenti l'italiano.
  - Verifica che sostituisce quella che l'engine non può fare da qui: uno script
    controlla che le due lingue abbiano le stesse chiavi e che ogni chiave usata
    esista. Da rifare a ogni testo aggiunto.

- **Il guscio: schermata iniziale come sovrapposizione, pausa, impostazioni.**
  Chiude il punto che era rimasto aperto. Il titolo **non è una scena a sé**: è
  un `Control` sopra il gioco già in funzione. `Main.tscn` parte come sempre, la
  prima stanza viene costruita sotto, e il titolo sta sopra finché non si
  sceglie.
  - **Una scena di titolo separata**, che è come si fa di solito: scartata
    perché "Continua" dovrebbe avviare una partita e *poi* dirle cosa diventare,
    cioè passare stato attraverso un cambio di scena. Così invece il salvataggio
    si carica in un gioco già in piedi, e resta vera la decisione che `Main.tscn`
    è l'unica scena su cui premere Play.
  - **Continua compare solo se c'è qualcosa da continuare**, e apre il più
    recente fra manuale e automatico — a pari merito il manuale, perché se sono
    stati scritti nello stesso secondo quello scelto è quello inteso. Una voce
    che risponde "non c'è niente da caricare" è peggio di una voce che non c'è.
  - **Nuova partita dalla pausa dice al titolo di non richiedere**, con una
    `static var` che sopravvive al ricaricamento della scena. Non è stato del
    gioco né un'impostazione: è un'istruzione dalla scena che se ne va a quella
    che arriva, e viene consumata all'arrivo.
  - Le impostazioni sono **un pannello e non una schermata** perché servono da
    due posti, il titolo e la pausa, e un pannello si mette sopra entrambi senza
    che nessuno dei due lo sappia.
  - **Ogni lingua si scrive come si chiama da sé**, mai tradotta: "Italiano"
    scritto in inglese non serve a chi cerca l'italiano.
  - **I volumi sono bottoni che dicono a quanto sono**, e avanzano di un quinto
    a ogni tocco. Scartato il cursore: centottanta pixel di cursore sono un
    bersaglio peggiore di un bottone, per un pollice.

- **Transizione al nero fra le stanze.** Non è decorazione, fa due lavori.
  Senza, lo scambio è un fotogramma in cui una stanza viene sostituita da
  un'altra, e l'occhio lo legge come un difetto invece che come un andare da
  qualche parte. E lo scambio finisce dentro una callback di tween, che è tempo
  di idle — cioè esattamente il motivo per cui prima era differito: una porta si
  usa alla fine di una camminata, una camminata finisce dentro un passo di
  fisica, e lì dentro non si può consegnare al server fisico un nuovo insieme di
  forme. **La dissolvenza sostituisce il `call_deferred`.**
  - Ci passa anche il caricamento di una partita, e lì il motivo è più forte
    ancora: la stanza a schermo era costruita per un mondo che non esiste più.
  - Lo stesso nodo, reso visibile ma trasparente, è ciò che blocca lo schermo
    durante una scena scriptata: un `Control` visibile mangia il click nella
    fase GUI, che precede l'`_unhandled_input` della stanza.

- **Direzione e stati dei personaggi, e avvicinamento da più lati.** Chiude il
  punto che era rimasto aperto sull'avvicinamento, che aspettava proprio le
  direzioni. Un personaggio sa dove guarda (quattro direzioni) e cosa sta
  facendo (fermo, cammina, parla). La direzione si ricava dalla velocità mentre
  si cammina e **si conserva quando ci si ferma**, perché chi è andato a sinistra
  sta ancora guardando a sinistra. Arrivando a un hotspot ci si gira verso.
  - **Quattro direzioni e non otto**: è quello che contiene un foglio di sprite
    di questo genere, e una camminata in diagonale in una stanza di questa
    dimensione finisce prima che qualcuno l'abbia letta.
  - **Costruito prima che esista l'arte**, con i poligoni segnaposto che
    reagiscono. Il sobbalzo e il naso che cambia lato non sono il punto e
    spariranno: il punto è che direzione e stato esistono, si ricavano da quello
    che il personaggio fa davvero, e guidano qualcosa di visibile.
    `_refresh_visual()` è l'unica funzione che cambierà il giorno degli sprite.
  - **Avvicinamento: un `ApproachPoint` solo resta il posto dove sei destinato a
    stare** — davanti a una porta, a destra di una leva — e arrivarci dal lato
    sbagliato vuol dire fare il giro, che nei LucasArts era spesso il punto: si
    arriva in un posto noto, rivolti in un verso noto, perché l'animazione
    torni. Un gruppo `ApproachPoints` con più marker è per le cose raggiungibili
    da ogni lato, e **vince il più vicino a chi cammina**.
  - **Dove sta, si ricava da una regola e non a occhio**, e la regola è nata dopo
    averli trovati tutti sbagliati insieme: le distanze erano ereditate dal
    layout di prima del cambio di risoluzione, e otto punti su quattordici
    lasciavano il personaggio 17-32 unità troppo indietro — la leva della
    postazione arrivava a 46, cioè più di una figura di distanza da una cosa che
    si deve afferrare. La regola, misurata sulle mani (che stanno una ventina di
    unità sopra i piedi):
    - **cosa appesa al muro** → i piedi il più vicino al muro che la navmesh
      consenta, il suo limite superiore più due. Le mani cadono così al bordo
      basso dell'oggetto;
    - **cosa appoggiata al pavimento** → i piedi sei o otto unità davanti al suo
      bordo vicino;
    - **porta** → una quindicina di unità davanti alla soglia: ci si sta davanti,
      non ci si schiaccia contro.
    Il controllo che la verifica in un colpo solo è la distanza fra le mani e il
    bordo basso dell'oggetto: dentro ±10 va bene, oltre significa che il
    personaggio parla a un oggetto che non tocca.
  - **Il personaggio che copre in parte quello che usa non è un difetto**: nei
    LucasArts ci si mette davanti alle cose, l'informazione sta nella caption, e
    uno spostamento laterale per non coprire l'oggetto si legge come rivolgersi
    altrove. Ma "in parte" ha una soglia, e si misura: la quota dell'oggetto che
    il corpo (17×40) copre stando al punto di avvicinamento. **Sopra il 50% si
    sposta di lato, sotto no.** Misurati i quattordici hotspot del prototipo,
    dodici stanno fra 0 e 49% e due sforavano — il punto d'imbuco del corridoio
    al 58% e la capsula all'85%, che sparivano dietro chi li usa. Quei due hanno
    un offset orizzontale di venti unità, gli altri no.
  - Ne segue una nota sull'ordine in cui si lavora: **abbassare un oggetto
    all'altezza di una mano lo mette all'altezza del corpo**, quindi la
    correzione della portata e quella dell'occlusione vanno fatte insieme. Il
    punto d'imbuco è passato dal non essere raggiungibile al non essere visibile
    nello stesso commit, e l'ho scoperto solo guardando il render.
  - Scartate le altre due opzioni che erano in elenco: il punto calpestabile più
    vicino all'oggetto (niente controllo su dove ci si ferma, e la navmesh non
    sa cosa sia "davanti") e il raggio entro cui non si cammina affatto (rende
    l'azione a distanza, che è precisamente ciò che il camminare comunica).

- **Profondità: Y-sorting acceso, e scala per altezza come due numeri.** Chiude
  il punto che era rimasto aperto. Y-sorting su `Game`, `RoomContainer`,
  `Characters` e sulle stanze: in Godot 4 un nodo ordinato per Y assorbe nel
  proprio ordinamento i figli che a loro volta lo hanno acceso, quindi oggetti
  di stanza e personaggi si ordinano insieme **pur non essendo parenti**. È
  l'unico modo di ottenerlo senza toccare la decisione per cui i personaggi non
  sono figli della stanza.
  - **Convenzione che ne segue, e va ricordata**: il nodo di un oggetto sta dove
    l'oggetto **tocca il pavimento**, non al suo centro, perché l'ordinamento
    guarda la Y del nodo e non l'estensione di quel che disegna.
  - **Due altezze e due misure con una retta in mezzo**, non una curva Y→scala e
    non la scala per walkbox: è tutto quello che serve a un pavimento piatto
    visto da un angolo solo, e una curva sarebbe un editor in più da usare su un
    telefono. Lasciata a 1 e 1 una stanza non ha prospettiva, quindi è opt-in e
    nessuna stanza esistente è cambiata.
  - **La stanza possiede i numeri, il personaggio li applica a sé**: non essendo
    figlio della stanza, la stanza non avrebbe niente da afferrare.
  - **Si scala solo la figura, mai il nodo**: forma di collisione e agente di
    navigazione dicono quanto è grande il personaggio *come cosa nella stanza*,
    la prospettiva dice quanto sembra grande.

- **Telecamera: una sola, accanto ai personaggi, recintata dalla stanza.**
  Chiude il punto che era rimasto aperto. Le si dice chi guardare e quanto è
  grande la stanza, e si tiene dentro la seconda inseguendo il primo.
  - **Una `Camera2D` dentro ogni stanza**: scartata per lo stesso motivo per cui
    i personaggi non ci stanno — le stanze vengono buttate via, e una telecamera
    ricostruita a ogni porta ricomincia da capo il suo inseguimento.
  - **Figlia del personaggio attivo**: sarebbe gratis e seguirebbe da sé.
    Scartata perché al cambio personaggio andrebbe riappesa altrove, e
    riparentare nodi è la classe di operazioni che questo progetto ha evitato
    ovunque.
  - **Una stanza grande quanto lo schermo esce esattamente dov'era**: i limiti
    non lasciano spazio, quindi nessuna stanza esistente va toccata e
    `room_size` ha per default una schermata.
  - Niente si è rotto perché niente doveva rompersi: la stanza distingueva già
    le coordinate del mondo da quelle dello schermo, e la UI sta già su un
    `CanvasLayer`. Erano state scritte così per oggi.
  - **Scatta invece di scivolare** al cambio stanza o personaggio: attraversare
    mezza stanza per raggiungere qualcuno già fermo lì si legge come una
    telecamera che si è persa.

- **Audio: due riproduttori, due bus, e il suono come dato.** Chiude il punto
  che era rimasto aperto. Uno per come suona la stanza, uno per quello che è
  appena successo — un'avventura di questo tipo non ha mai più di questo in
  corso insieme, e un pool di voci sarebbe infrastruttura comprata contro un
  bisogno che nessuno ha.
  - Stanno **accanto ai personaggi**, non dentro una stanza: una musica che si
    ferma e riparte a ogni porta sarebbe peggio di nessuna musica. La musica si
    richiede a ogni apertura di stanza ed è il direttore a sapere che la stessa
    musica due volte non è un motivo per ricominciarla.
  - **La stanza non suona: emette `wants_to_play`** e Game collega, come già per
    quello che vuole dire. Chi fa rumore sopravvive alla stanza, e la stanza non
    ha mai avuto il permesso di conoscere niente che le sopravviva.
  - **Il loop è fatto a mano** riavviando alla fine, invece che con
    l'impostazione di import: se un `.wav` esca dall'importatore con il loop
    acceso dipende da un `.import` che scrive l'editor, e da qui non è
    verificabile.
  - **Il silenzio si ottiene mutando il bus**, non abbassandolo: `linear_to_db(0)`
    è meno infinito, e un bus a meno infinito non è silenzioso in modo
    affidabile.
  - I cinque suoni in `assets/audio/` sono **segnaposto generati da uno script**
    — clic, tonfo, carillon, due ronzii. Servono a far sentire l'impianto invece
    che a farlo credere; sostituirli è sostituire dei file.

- **Sequenze scriptate: un elenco chiuso di passi, eseguito con `await`.** Fino
  a ora il gioco sapeva dire "è successo qualcosa" — una riga, un flag, un
  oggetto che cambia mano — ma non sapeva dire "**e poi**". Un enigma la cui
  risposta è giusta e il cui esito è una frase in un riquadro si legge come se
  non fosse successo granché, e l'esito è la parte per cui il giocatore ha
  lavorato.
  - **Nove tipi di passo e non un linguaggio**: dire, aspettare, camminare,
    girarsi, un suono, alzare un flag, girare un interruttore, dare, togliere.
    Chiusi come il vocabolario dei verbi e per lo stesso motivo: una sequenza
    che può fare qualunque cosa è uno script, e uno script per oggetto è quello
    che questo progetto ha passato la vita a evitare. Chi vuole di più ha ancora
    un hotspot con uno script suo.
  - **Niente diramazioni e niente condizioni dentro una scena**: una scena che
    deve decidere sono due scene e un hotspot che sceglie.
  - **Il runner è un `Node`**, a differenza di quello dei dialoghi: una
    conversazione aspetta il giocatore, una scena aspetta il tempo e la fine di
    una camminata, e aspettare vuole un albero.
  - **Scritto con `await` e non come macchina a stati con un indice**: il senso
    di una sequenza è che si legge nell'ordine in cui accade, e `await` è
    l'unica cosa in GDScript che permetta di scrivere il codice in quell'ordine.
  - **Quanto resta a schermo una battuta lo chiede alla caption** invece di
    indovinarlo, così una scena tiene il passo della velocità di lettura scelta
    e non di un numero scritto dentro di sé.
  - Chiuso anche un buco: **un'opzione di dialogo sa girare un interruttore e
    togliere un oggetto**, non solo alzare un flag e darne uno. Una conversazione
    che può chiudere a chiave una porta ma non aprirla è metà di uno strumento.
    Si toglie prima di dare, così uno scambio non lascia nessuno con tutte e due
    le cose in mano.

- **Il prototipo verticale: due personaggi separati da un regolamento, non da un
  muro.** Chiude il punto 5. La premessa in una riga: una piccola ditta che
  certifica che le cose funzionano deve collaudare una posta pneumatica, e la
  posta pneumatica e' ostruita.
  - **Nora**, ispettrice: puo' andare ovunque e presentare reclami come membro
    del pubblico, ma **non puo' toccare l'impianto sotto collaudo**, perche'
    toccarlo invalida il collaudo.
  - **Cesare**, manovratore: puo' azionare qualunque cosa, ma **non puo'
    lasciare la postazione** e, essendo personale interno, non e' pubblico.
  - **La separazione non e' una barriera fisica**, ed e' la parte su cui ho
    lavorato di piu'. L'attrattore documentato in `.claude/skills/narratore/`
    dice che due agenti indipendenti, con questo brief, mettono entrambi il
    secondo personaggio dietro un vetro o una serranda e fanno passare un
    documento attraverso. Qui la separazione e' di **autorizzazione**: nessuno
    dei due e' bloccato da qualcosa che si vede, sono bloccati da cosa gli e'
    permesso — e i due divieti sono complementari per costruzione.
  - **Asse del potere invertito**: chi ha il tesserino e puo' entrare ovunque e'
    la piu' impotente delle due, perche' non puo' toccare niente. Il default
    sarebbe stato il contrario.
  - **Scala piccola, non apparato infinito**: una ditta che sta per perdere
    l'accreditamento, non un'istituzione sconfinata. La commedia viene dal fatto
    che il sistema e' *insufficiente*, non che e' onnipotente.
  - **Direzioni scartate**: la garanzia in scadenza su un oggetto enorme, da
    restituire nell'imballo originale (buona, ma il secondo personaggio
    giocabile non nasceva da se'); e la coda diventata un luogo abitato, con chi
    e' in testa che non puo' muoversi (fresca, ma la separazione "chi ha il
    posto non si muove" e' la stessa idea del funzionario immobilizzato, cioe'
    l'attrattore con un altro cappello).
  - **Il meccanismo di trasferimento e' il soggetto del gioco.** I punti di
    passaggio erano una decisione tecnica presa mesi fa; qui il tubo *e'* la
    cosa da collaudare, e l'enigma e' che il canale attraverso cui si passano
    gli oggetti e' rotto. Non si tratta di far passare qualcosa attraverso la
    barriera: si tratta di convincere la barriera a sbloccarsi da sola.
  - L'enigma completo: Nora prende un modulo di reclamo, legge la sezione
    dall'oblo', stacca la targhetta (segnaletica, non impianto), la appiccica
    sul modulo, e lo imbuca dal punto **pubblico** — la linea di ritorno e'
    libera. Cesare lo ritira, lo protocolla, e ora la leva d'inversione ha un
    motivo. La linea gira al contrario e la capsula ostruita esce dalla parte di
    Nora. Dentro c'e' il rinnovo dell'accreditamento della loro ditta, spedito
    tre anni fa: il motivo per cui stanno per chiudere era fermo nel tubo che
    gli hanno chiesto di collaudare.
  - **Nomi e ambientazione restano provvisori** e costano due righe cambiarli:
    grazie alla localizzazione, un nome e' una chiave in `it.tres` e `en.tres` e
    da nessun'altra parte. La storia completa resta il punto 6.
  - Le tre vecchie stanze di prova sono state tenute a lungo perche' erano
    superficie gia' verificata, e buttarla via non era una decisione mia. Sono
    state cancellate quando lo sviluppatore l'ha chiesto — vedi "Si cancella
    tutto quello che non e' raggiungibile" in fondo all'elenco.

- **`StateVisual`: la scenografia reagisce allo stato, senza essere cliccabile.**
  Un `Node2D` che si mostra solo mentre le sue condizioni reggono — la
  controparte di `present_if` per le cose che il gioco disegna e nessuno tocca.
  Nasce da un difetto trovato provando il prototipo: lo stato della porta
  (`state_id`) c'era e nessuno lo vedeva.
  - **Un hotspot senza verbi** al posto di questo: nessun codice nuovo, ed è
    come era fatto lo spiffero nella stanza di prova di allora, poi cancellata.
    Scartato perché un
    hotspot risponde ai click, e una lama di luce distesa sul pavimento davanti a
    una porta sta esattamente dove il giocatore tocca per andarci: la
    scenografia che reagisce al mondo non deve anche competere per il tocco.
  - **Niente `call_deferred` qui**, a differenza dell'hotspot: non c'è nessuna
    forma da consegnare al server fisico, solo una visibilità, e quella si può
    cambiare in qualunque momento.
  - **Le due facce della stessa porta si mostrano in modo diverso**, ed era una
    scelta di scrittura visiva più che tecnica: dall'atrio si vedeva **solo la
    luce sul pavimento**, dal corridoio **il battente aperto o chiuso**. Una
    porta si guarda da due lati e i due lati non hanno le stesse informazioni da
    dare — il lato in ombra racconta la luce dell'altro.
    **Superata per metà**: la luce resta e funziona, ma non basta da sola.
    Nell'atrio il battente era dipinto **chiuso nel fondale**, quindi con la porta
    aperta si vedeva la luce uscire da una porta chiusa: l'immagine contraddiceva
    lo stato. Adesso anche l'atrio ha i due battenti come sprite, come il
    corridoio, e il fondale dipinge solo telaio e vano — quelli non cambiano mai.
    La regola generale che ne resta, e vale per qualunque cosa abbia stati:
    **un fondale può raccontare una conseguenza, non può stare al posto della
    cosa che cambia.** La luce sul pavimento era una conseguenza ben scelta e
    l'ho tenuta; il battente era la cosa che cambia, e quella non si dipinge.

- **Stile ibrido: personaggi in pixel art su sfondi dipinti ad alta risoluzione**
  (revoca della scelta per cui tutta l'arte del progetto è pixel art). Gli sfondi
  diventano immagini a piena risoluzione, morbide e con gradienti; personaggi,
  oggetti e figure degli hotspot restano pixel art netta.
  La notizia tecnica è che **il progetto lo supportava già, e non per caso**:
  `stretch/mode = canvas_items` fa avvenire il disegno alla risoluzione reale
  della finestra e non a 384×216, `default_texture_filter` è `Nearest` per la
  pixel art, e le sette icone dei verbi hanno da mesi un override a `Linear` sul
  nodo. Lo stile ibrido è quella stessa struttura estesa agli sfondi: non c'è
  niente da cambiare nell'engine, c'è da fissare delle regole.
  - **Restare interamente in pixel art**: coerenza garantita, una sola tavolozza,
    file da pochi kilobyte, e nessuna delle regole qui sotto da ricordare.
    Vantaggi reali, ed è quello che il progetto aveva deciso. Scartata perché
    è una scelta estetica dello sviluppatore, che ha visto le due strade e
    preferisce questa. Non è caduta una premessa tecnica: è cambiato il gusto,
    che su una decisione estetica è il criterio giusto.
  - **La regola che tiene tutto insieme: un pixel di texture è un'unità di
    gioco.** Un personaggio alto 40 unità si disegna alto 40 pixel e si usa a
    `scale = 1`. Così ogni pixel della texture diventa esattamente
    *fattore-di-finestra* pixel veri sullo schermo — sempre un numero intero, e
    quindi sempre un blocco netto. Disegnarlo più grande e rimpicciolirlo in
    scena è la cosa che rompe la pixel art: a 0,5 di scala su uno schermo 5× un
    pixel di texture diventa 2,5 pixel veri, e alcuni pixel escono grandi il
    doppio degli altri.
  - **Gli sfondi si disegnano a 1920×1080 e si usano a `scale = 0.2`**, con
    `texture_filter` a `Linear` sul nodo. 1920×1080 è esattamente 5× la
    risoluzione base, quindi su un telefono alto 1080 lo sfondo è 1:1 e non viene
    né ingrandito né rimpicciolito; sulla finestra desktop 3× viene ridotto di
    poco, che è precisamente il caso per cui esiste il filtro lineare. Una stanza
    larga il doppio vuole uno sfondo largo il doppio: il corridoio dei tubi
    sarebbe 3840×1080.
  - **`Nearest` resta il default globale** e `Linear` resta un override sul nodo,
    non il contrario. Gli sfondi sono uno per stanza, gli sprite sono decine:
    l'eccezione va messa sulla minoranza.
  - **Una tavolozza madre e una sola direzione di luce** per stanza, condivise
    fra sfondo e sprite. È la parte che decide se i due stili convivono o
    litigano, e non è una regola tecnica ma di produzione: la tavolozza ridotta
    del personaggio si deriva da quella dello sfondo, non si inventa a parte.
  - **Un'ombra di contatto sotto i piedi.** Uno sprite netto appoggiato su uno
    sfondo morbido galleggia; una macchia ovale sfumata sotto i piedi lo ancora.
    Va come figlio del nodo `Visual` del personaggio, disegnata prima del corpo.
  - Effetto collaterale che mi fa piacere: **le icone dei verbi smettono di
    essere un'eccezione.** Erano l'unica arte non-pixel del progetto e avevano
    bisogno di un paragrafo per giustificarsi; adesso sono semplicemente lo
    strato morbido, come gli sfondi.
  - Costo accettato: **i file pesano.** Uno sfondo 1920×1080 sta fra uno e tre
    megabyte, e una stanza larga il doppio ne pesa il doppio. Con una dozzina di
    stanze si parla di decine di megabyte in un repository che si tira su un
    telefono. È accettabile, ma va saputo prima e non dopo.
  - Le tre stanze del prototipo restano fatte di `Polygon2D` piatti finché non
    esiste arte vera: sostituirli con delle texture che non ci sono ancora
    romperebbe il prototipo senza guadagnare niente.

- **Un personaggio a figura intera è alto 40 unità di gioco**, non 26. Chiude il
  punto che era rimasto aperto sull'altezza. Scelto guardando le tre altezze
  affiancate nella stessa stanza, che è l'unico modo di giudicarlo: il numero da
  solo non dice niente, il confronto sì. A 216 unità di schermo un personaggio
  occupava quindi il 18,5% dell'altezza, e la stanza gli stava sopra per due
  volte e mezzo. Le 40 unità non sono cambiate, ma lo schermo sì: da quando la
  base è 320×180 la stessa figura occupa il **22,2%**. Il numero scelto qui
  regge, quello derivato no — ed è la ragione per cui la voce sulla risoluzione
  in fondo all'elenco non ha richiesto di ridisegnare un solo sprite.
  - **27 unità** (l'altezza dei segnaposto di allora): la stanza respira e ci sta
    più scenografia. Scartata perché a quella misura il personaggio è appena più
    alto di una sedia, e in un genere dove si guarda il personaggio camminare per
    metà del tempo è troppo poco per leggerne pose e direzione.
  - **54 unità**, la proporzione LucasArts classica: la più espressiva delle tre,
    e la più adatta a uno sprite con vera animazione. Scartata perché a un quarto
    dell'altezza dello schermo la stanza diventa un interno stretto, e questo
    gioco ha già un corridoio largo due schermate in cui la telecamera scorre.
  - Ricadute già applicate: la figura segnaposto in `Player.tscn` è ridisegnata
    alle stesse proporzioni, la capsula di collisione è scalata con lei
    (raggio 5, altezza 30) e `NOSE_OFFSET` passa da 4 a 6. `agent_radius` delle
    navmesh resta 4: è la distanza dagli ostacoli, e le stanze sono rettangoli
    vuoti.
  - Conseguenza per la skill grafica: la sua sezione "Vincoli di AGGGA" diceva
    26 unità ed è aggiornata. Uno sprite si disegna alto **40 pixel** e si usa a
    `scale = 1`.

- **Cosa sta nello sfondo dipinto e cosa resta uno sprite**, ed è una regola con
  un criterio, non un elenco. Nello sfondo va ciò che è **fermo, muto e sempre
  dietro**: muro, pavimento, battiscopa, telaio della porta, sporco e usura.
  Restano sprite separati tre categorie, ognuna per una ragione diversa e
  verificabile:
  - **Quello che cambia con lo stato del gioco** — la lama di luce sotto la
    porta, il battente aperto o chiuso. È il `StateVisual`, e per definizione non
    può essere dipinto in un'immagine sola. L'esperimento ha aggiunto un motivo
    che non avevo previsto: la luce si legge **meglio** con un bordo netto che
    sfumata, perché è informazione di gioco e non atmosfera. Quindi non solo va
    fuori dallo sfondo, va fuori *e* disegnata dura.
  - **Quello che si ordina in Y** — le sedie stanno a metà pavimento, e un
    personaggio ci passa davanti e dietro. Dipinte nello sfondo, chi ci sta
    dietro le calpesterebbe. Il criterio è meccanico: se il nodo sta dentro la
    navmesh, è uno sprite.
  - **Quello che porta scritte** — bacheca del regolamento e portamoduli. Nessun
    generatore di immagini scrive parole leggibili, e qui le scritte sono
    l'enigma. Restano pixel art con il testo disegnato, appoggiata su una chiazza
    di muro che il prompt chiede esplicitamente di lasciare nuda.
  - Le cose ferme e appese in alto — sopra la linea del pavimento — potrebbero
    stare nello sfondo senza rompere niente, perché il personaggio ci passa
    sempre davanti. Non lo faccio lo stesso: sono hotspot, e un hotspot la cui
    figura è dipinta nello sfondo non può più cambiare aspetto il giorno in cui
    servisse. Il guadagno sarebbe un'immagine più ricca, il costo una decisione
    irreversibile per stanza.

- **Gli sfondi si producono da un'immagine esterna, non disegnandoli per
  codice.** Chiude il punto che era rimasto aperto. È la stessa via delle sette
  icone dei verbi: l'immagine la genera lo sviluppatore con uno strumento
  esterno, e da qui viene misurata, ripulita e portata alla dimensione giusta.
  Il criterio non è stato il gusto ma il confronto: l'atrio disegnato per codice
  e l'atrio generato stanno affiancati nella cronologia di questa sessione, e il
  secondo ha una ricchezza — intonaco scrostato, aloni di umido, venature del
  legno — che per codice sarebbe costata giorni e sarebbe comunque venuta
  geometrica.
  - **Disegno per codice con Pillow** (la via che la skill propone per prima):
    coerente per costruzione, file da 12 kB, e ogni elemento modificabile
    spostando un numero. Vantaggi reali, e restano validi **per gli sprite**, che
    infatti si continuano a disegnare così. Scartata per gli sfondi perché il
    costo non sta nel disegnare ma nell'avvicinarsi: la versione dipinta per
    codice ha richiesto due giri completi ed è arrivata a "accettabile", non a
    "è questa".
  - **Lo stile che ne esce non è painterly ma a tinte piatte con contorno
    scuro**, ed è meglio così: condivide il linguaggio del contorno con la pixel
    art invece di contrastarlo. È una correzione alla voce sullo stile ibrido —
    "sfondi dipinti a piena risoluzione" resta vero sulla risoluzione e sul
    filtro, ma la resa è cartoon a tinte piatte, non pittorica.
  - **Il generatore ignora le percentuali e rispetta i rapporti.** Il primo
    tentativo aveva la linea del pavimento al 68% invece che al 51%, e
    soprattutto una porta alta 119 unità con la maniglia sedici unità sopra la
    testa di Nora: l'immagine era disegnata per un personaggio alto il doppio.
    La correzione che ha funzionato non è stata ripetere le percentuali ma
    chiedere una modifica in rapporto — "la porta alta un terzo del muro" — e
    farla fare al generatore sulla propria immagine, che ripara l'intonaco molto
    meglio di qualunque interpolazione fatta da qui.
  - **Ne segue una regola di metodo: la scala si verifica mettendo il
    personaggio dentro l'immagine**, non guardandola. A occhio l'atrio sembrava
    giusto; è bastato comporci Nora a 40 unità perché il problema diventasse
    ovvio. La misura che lo rivela in un colpo solo è **l'altezza della
    maniglia**.
  - **E una seconda: quando esiste arte vera, comanda l'arte.** La linea del
    pavimento è rimasta al 68% e si è spostata la navmesh, invece di ritagliare
    l'immagine. Il blockout esisteva per reggere finché non c'era niente da
    guardare.

- **Gli sfondi si salvano in `.webp`, non in `.png`.** Chiude il punto che era
  rimasto aperto sul peso del repository. Misurato sull'atrio: PNG 1934 kB,
  WebP a qualità 92 **91 kB**, cioè ventuno volte meno, con una differenza
  massima di 10 livelli su 255 e media di 1,0 — su un'immagine a tinte piatte
  non c'è niente da vedere. Con una dozzina di stanze si passa da venticinque
  megabyte a uno, su un repository che si clona da un telefono.
  - **Accettare il PNG**: nessuna decisione da prendere e nessuna perdita.
    Scartato per il solo numero qui sopra.
  - **Scendere di risoluzione**: costa nitidezza su tutti i dispositivi per
    risparmiare meno di quanto risparmi la compressione. Scartata.
  - **Gli sprite restano PNG**: sono da 200 byte l'uno e la pixel art vuole
    l'esattezza pixel per pixel. La compressione con perdita si applica allo
    strato morbido, che è dove sta il peso.

- **`tools/` per gli script che producono asset.** Uno per famiglia:
  `make_lobby_background.py` prende l'immagine esterna e ne fa la texture,
  `make_lobby_props.py` disegna bacheca, portamoduli e sedie. Stanno nel
  repository e non nello scratchpad perché un asset che nessuno sa rifare è un
  asset che non si può correggere.
  - **L'immagine sorgente non si committa**, come già per i riferimenti delle
    icone dei verbi: è materiale dello sviluppatore, pesa quanto l'asset, e lo
    script la prende come argomento.
  - Nello script stanno anche **le misure prese sull'immagine** — linea del
    pavimento a 146, porta 36×58 centrata a 313 — perché sono ciò che lega
    l'immagine alla scena, e un'immagine nuova va confrontata con quelle.

- **Il foglio dei personaggi: nove animazioni, tre direzioni disegnate, la
  quarta specchiata.** Chiude il punto che era rimasto aperto sull'arte dei
  personaggi. Le animazioni si chiamano `<stato>_<direzione>` con gli stati
  `idle`, `walk`, `talk` e le direzioni `down`, `side`, `up`; `walk` ha quattro
  fotogrammi, `talk` due, `idle` uno. `_refresh_visual()` è diventato quello che
  era stato progettato per diventare: compone un nome e lo passa a un
  `AnimatedSprite2D`.
  - **Il sinistra è il destra ribaltato** (`flip_h`), quindi un personaggio costa
    tre disegni e non quattro. Regge finché niente nel personaggio è asimmetrico:
    una borsa a tracolla o una benda su un occhio farebbero saltare il trucco, ed
    è un vincolo di design dei personaggi, non un dettaglio tecnico.
  - **Quattro fotogrammi per la camminata e non sei o otto**: contatto, passaggio,
    contatto opposto, passaggio, con il corpo che si alza di un pixel sui
    passaggi. È il ciclo "arcade" che la skill descrive, e a 40 unità di altezza
    la differenza con un ciclo completo non si vede. Otto fotogrammi
    raddoppierebbero il disegno per una lettura che lo schermo non ha.
  - **L'idle è un fotogramma solo**, per ora. Un respiro a due fotogrammi si
    aggiunge dopo senza toccare niente: è una riga nella tabella delle animazioni.
  - **Frontale e di spalle non hanno un "avanti" dove andare**, quindi il passo lì
    non è una falcata ma un piede sollevato di un pixel. Provato prima ad
    allargare le gambe, e veniva un personaggio che camminava a gambe larghe.
  - **La direzione della luce dello sprite è quella della stanza** — dall'alto e
    un po' da sinistra, come il neon dell'atrio. È la regola già registrata sulla
    tavolozza madre, applicata all'ombreggiatura invece che ai colori.
  - **Ogni personaggio è la stessa scena con un foglio diverso**, passato come
    `@export var frames: SpriteFrames` sull'istanza. `body_color` sparisce: serviva
    a distinguere due poligoni. Un personaggio nuovo costa una risorsa, non un
    nodo.
  - **Lo `SpriteFrames` .tres lo scrive lo stesso script che disegna il foglio**,
    perché le coordinate delle celle sono la stessa informazione due volte e
    scriverle a mano vuol dire vederle divergere.
  - **L'ombra di contatto è un nodo separato sotto `Visual`**, non dipinta dentro
    i fotogrammi: dipinta dentro salirebbe e scenderebbe con il sobbalzo della
    camminata, e un'ombra che rimbalza col personaggio è peggio di nessuna ombra.
    È pixel art a due livelli di trasparenza e non una macchia sfumata, perché con
    il filtro `Nearest` una sfumatura sarebbe l'unica cosa morbida dello sprite.

- **Nora diventa Lino**, ed è un ragazzo: capelli biondi, occhi chiari, cappellino.
  Costa quello che la localizzazione aveva promesso costasse — una chiave in
  `it.tres` e `en.tres`, il nome del nodo in `Main.tscn` e nient'altro — con
  l'unica eccezione di un participio: *"la porta da cui sei entrata"* è diventato
  *"entrato"*. Il resto dei testi del prototipo era già neutro, non per fortuna ma
  perché parlano di oggetti e non di chi guarda.
  - I nomi restano provvisori come già scritto: la storia completa è il punto 6, e
    finché è aperta un nome è una chiave in due file.
  - **Cesare ha un foglio anche lui**, ma è una prima passata a colori diversi e
    senza cappello: serviva a non lasciare un personaggio disegnato e uno fatto di
    poligoni. Si ridisegna cambiando un dizionario, quando sarà descritto.

- **Una sola skill grafica, con la verifica automatica degli asset dentro.**
  Le skill grafiche erano due — `pixel-adventure-assets`, adattata al progetto, e
  `pixelart-adventure`, aggiunta il 3 agosto e mai adattata — e portavano numeri
  incompatibili: 640×360 contro 384×216, personaggio alto 72 px contro 40, celle
  64×96 contro 24×44, palette master fissa contro tavolozza madre per stanza. Il
  commit che aggiungeva la seconda lo diceva apertamente (*"la decisione sulla
  risoluzione di base che questa specifica implica non è ancora presa"*), ma da
  allora quella decisione è stata presa nella direzione opposta, e l'elenco delle
  skill in fondo a questo file non l'ha mai nominata. Resta `pixel-adventure-assets`,
  che eredita da quella rimossa i due strumenti che qui servono davvero.
  Il motivo di consolidare invece di tenerle entrambe è che una skill si sceglie
  da sola, in base alla propria `description`, e quella rimossa era scritta per
  attivarsi anche sulle richieste generiche (*"fammi uno sfondo per il gioco"*).
  Due skill in disaccordo sui numeri non sono ridondanza: sono un sorteggio, e
  l'esito sbagliato produce asset inutilizzabili con notevole sicurezza di sé.
  - **Tenerle entrambe e scegliere di volta in volta**: nessun lavoro, e la
    seconda ha materiale di qualità — la quantizzazione in Oklab e il controllo
    automatico non esistevano da questa parte. Scartata perché la scelta non la
    fa chi conosce il progetto: la fa l'attivazione automatica, prima che
    qualcuno legga i numeri.
  - **Adattare `pixelart-adventure` al posto dell'altra**: i suoi script sono più
    completi e ha 1000 righe di reference sul colore e sui materiali. Scartata
    perché la sua specifica è un sistema coerente costruito su 640×360 e su una
    palette fissa: adattarla voleva dire riscriverne le premesse e tenere le
    conclusioni, cioè fidarsi di numeri che non discendono più da niente.
  - **Cosa è stato salvato**: `pxlib.py` (Oklab, HSV, I/O palette) invariato;
    `palette.py` ridotto a estrazione e swatch; `qa_check.py` riscritto sui
    numeri del progetto. Scartati `pixelate.py` e `spritesheet.py`: il primo
    converte un render in pixel art nativa, che è la pipeline che il progetto ha
    già respinto per gli sfondi; il secondo è meno di quello che fa già
    `tools/make_character_sheets.py`, che scrive il foglio **e** lo `SpriteFrames`
    in un colpo solo. Le 1000 righe di reference restano in git.
  - **`palette.py` non usa scikit-learn**: il k-means è venti righe di numpy. Una
    dipendenza da centinaia di megabyte per un algoritmo di quella misura non si
    installa su un telefono, che è la macchina dove le skill devono funzionare.
  - **Le soglie sono misurate, non prese da una guida.** La distanza oltre la
    quale un colore non appartiene più alla tavolozza della stanza è 0,16 in
    Oklab perché sull'atrio gli asset già approvati arrivano al massimo a 0,129
    (Lino) e dei colori volutamente estranei stanno a 0,23-0,27: la soglia sta nel
    vuoto in mezzo. La prima soglia che avevo scritto a occhio era 0,10, e
    **avrebbe bocciato Lino**. Va rimisurata se cambia lo sfondo di riferimento.
  - **Tarare i controlli ha trovato due volte un difetto nel controllo e non
    nell'asset**: il contorno scuro sta fuori dalla figura, quindi un corpo alto
    40 misura 41 righe di pixel; e l'ombra di contatto è semitrasparente per
    decisione registrata, non per sbaglio. Ne segue la regola scritta nella
    skill: quando un controllo fallisce, prima si stabilisce **se ha ragione lo
    strumento o l'asset**.
  - Il controllo che vale più di tutti è **l'ancoraggio dei piedi**: in ogni cella
    l'ultima riga di pixel opachi deve essere l'ultima riga della cella, o il
    personaggio sobbalza a ogni passo. È un difetto che nel PNG fermo non si vede
    e in gioco non si smette di vedere.
  - Nota: da rivedere se il progetto adottasse una palette fissa di gioco invece
    di una tavolozza per stanza — allora il controllo di parentela diventerebbe
    aderenza a una lista, che è più semplice e più severo.

- **Le icone d'inventario sono 12×12 e affiancano il nome, non lo sostituiscono.**
  La misura non è estetica: lo slot è alto 16 unità (`SLOT_MINIMUM_SIZE` in
  `inventory_panel.gd`) e un `Button` ci aggiunge il padding del tema, quindi
  qualunque cosa più grande spinge lo slot fuori forma — è la stessa trappola
  già registrata per la verb-coin, *"`Button` non sta nella dimensione che gli
  chiedi"*. A dodici pixel un disegno dice "carta" o "metallo" a colpo d'occhio
  e non dirà mai *quale* modulo: quella parte la fa il nome, ed è il motivo per
  cui le due cose stanno accanto invece che l'una al posto dell'altra.
  - **Icone da sole, senza nome**: è come funziona l'inventario di quasi tutti i
    punta-e-clicca, e libererebbe la larghezza dello slot. Scartata perché qui
    tre oggetti su otto sono fogli di carta e due sono pulsanti: a dodici pixel
    la differenza fra il Modulo 12-B e il modulo di reclamo non si disegna, e
    un inventario in cui due voci sono indistinguibili è peggio di uno testuale.
  - **Icone più grandi, allargando lo slot**: si vedrebbero meglio. Scartata
    perché il pannello è già tre colonne su uno schermo alto 216, e crescere in
    altezza costa righe visibili — cioè costa proprio la cosa che l'inventario
    deve mostrare.
  - **`Button.icon` invece di un nodo dedicato**: un `Button` disegna da sé
    l'icona a sinistra del testo, quindi lo slot non guadagna né un figlio né un
    secondo layout da tenere allineato. Ed è **retrocompatibile per
    costruzione**: un oggetto con `icon` nullo mostra il solo nome, esattamente
    come prima che l'arte esistesse.
  - **Le coppie si disegnano come "stesso oggetto, dopo"**: il reclamo compilato
    è il modulo vuoto più lo smalto della targhetta dentro il riquadro, e il
    pulsante etichettato è il pulsante più la fascia dell'adesivo. Non sono due
    disegni che si somigliano, è lo stesso disegno in due stati — la stessa
    regola già usata per Apri e Chiudi fra le icone dei verbi. Se il giocatore
    non vede che l'enigma è avanzato, l'icona ha fallito anche se è bella.
  - **L'ocra è l'unica nota calda del gioco** e viene dai capelli di Lino, non
    da fuori: la tavolozza dell'atrio è tutta fredda, e un giallo preso altrove
    sarebbe stato respinto dal controllo di parentela. Le tre icone che lo usano
    sono infatti le più lontane misurate (0,11 contro una soglia di 0,16).
  - Nota: da rivedere se un oggetto avesse bisogno di essere riconosciuto
    **senza** leggere, per esempio in una sequenza a tempo. Allora la domanda
    non sarebbe più la dimensione dell'icona ma se quell'oggetto meriti una
    forma propria invece di essere il quinto foglio di carta.

- **Tutto in pixel art: anche gli sfondi** (revoca dello stile ibrido). Gli
  sfondi tornano a essere pixel art disegnata alle dimensioni della stanza —
  allora 384×216 per l'atrio e 768×216 per il corridoio, oggi 320×180 e 640×180
  dopo il cambio di risoluzione base — usata a `scale = 1` con il
  filtro `Nearest`, come ogni altro asset. Cadono il `.webp` a 1920×1080, la
  scala 0,2 e l'override a `Linear` sul nodo.
  Il motivo è quello che la voce sullo stile ibrido aveva messo per iscritto
  come proprio costo: *"uno sprite netto appoggiato su uno sfondo morbido
  galleggia"*. La contromisura registrata allora era l'ombra di contatto, e non
  è bastata: con lo sfondo dipinto davanti agli occhi lo stacco fra i due
  materiali resta il primo elemento che si nota. È una decisione estetica dello
  sviluppatore, ed è il criterio giusto per prenderla — la stessa ragione per
  cui lo stile ibrido era stato adottato.
  - **Restare sull'ibrido**: gli sfondi generati hanno una ricchezza che il
    codice non raggiunge — intonaco scrostato, aloni di umido, venature del
    legno — e quel giudizio, misurato a suo tempo mettendo le due versioni
    affiancate, resta vero. Scartato perché il confronto di allora era fra due
    *sfondi*, e la domanda giusta è come sta lo sfondo **accanto al
    personaggio**.
  - **Pixel art solo dove il personaggio passa**, tenendo dipinto il resto:
    non regge, perché il personaggio attraversa tutta la stanza.
  - Ricadute tecniche, tutte in direzione della semplificazione: un pixel di
    texture è di nuovo un'unità di gioco **ovunque**, `Nearest` non ha più
    eccezioni fuori dalle icone dei verbi, e l'atrio passa da 96 kB a **9 kB**.
    Il vincolo sul peso del repository che aveva imposto il `.webp` sparisce.
  - **Il costo vero si sposta sul tempo di disegno**, e va saputo: l'atrio ha
    richiesto quattro giri, e i primi tre sono finiti nel cestino per motivi
    che vale la pena non ripetere.
  - **Il dithering va ai bordi delle bande, mai su tutta la superficie.** Un
    gradiente dithered per intero, a questa risoluzione, si legge come una
    zanzariera. La forma giusta è quantizzare in fasce piatte e mescolare solo
    la striscia dove due fasce si toccano — è il parametro `width` di
    `banded()`.
  - **Non aggiungere rumore casuale a un campo prima di quantizzarlo.** Vicino
    a un confine di fascia il rumore sparge pixel isolati per tutta la sua
    ampiezza, e quello si legge come sporco, non come grana. Se una superficie
    deve avere grana, gliela si dà **in forme** — scrostature, macchie, crepe.
  - **Un pavimento visto di fronte non ha un punto di fuga laterale.** Il primo
    tentativo faceva passare ogni fuga per un punto di fuga e ne usciva una
    raggiera: quella costruzione vale per un pavimento visto d'angolo. Qui le
    fughe sono orizzontali e si infittiscono verso il fondo, e basta.
  - **Le macchie di umidità sono più chiare del muro, non più scure.** Disegnate
    scure diventano crateri; una macchia su intonaco dipinto slava il colore.
  - Conseguenza da ricordare per chi disegna: **quello che sta nello sfondo non
    vede gli sprite che gli finiranno davanti**. Il quadro elettrico dell'atrio
    è nato sotto la bacheca e ha dovuto traslocare — le zone occupate dagli
    hotspot vanno tenute libere e annotate nello script.
  - Nota: da rivedere solo se lo sviluppatore cambiasse di nuovo gusto. Non c'è
    una premessa tecnica che possa cadere, perché non è una decisione tecnica.

- **Da 384×216 a 320×180** (revoca della risoluzione base scelta nello scaffold).
  Lo schermo si stringe di un quinto e il personaggio passa dal 18,5% al **22,2%**
  dell'altezza, senza che venga ridisegnato un solo sprite: lo zoom si ottiene
  mostrando *meno stanza*, non ingrandendo le cose. Finestra desktop 4× = 1280×720.
  Il motivo è una misura riportata dal dispositivo: tutto sembrava lontano e lo
  schermo vuoto. Ed è la decisione da prendere adesso e non dopo, perché è
  l'unica il cui costo cresce con ogni stanza aggiunta — con tre stanze è un
  ritaglio, con venti è una riscrittura. Lo stesso argomento della versione del
  salvataggio.
  - **`Camera2D.zoom` invece della risoluzione base**: è quello che si chiede
    d'istinto, ed è una riga. Scartato perché rompe la regola portante: il
    fattore di scala è `altezza finestra / altezza base` e deve venire intero, o
    alcuni pixel escono più grandi di altri. Uno `zoom = 1.2` dà 6 su un telefono
    alto 1080 (nitido) ma 3,6 sulla finestra desktop (non nitido): sarebbe una
    scommessa per dispositivo. E siccome 216 / 1,2 = 180, **zoom 1,2 e base
    320×180 producono gli stessi pixel** — la differenza è che con lo zoom
    `room_size`, i limiti della telecamera e ogni numero di layout continuerebbero
    a descrivere una vista larga 384 che nessuno vede, e la proprietà per cui
    l'atrio è "esattamente una schermata, quindi la telecamera non ha dove
    andare" smetterebbe di essere vera in silenzio.
  - **240×135** (personaggio al 29,6%): il passo successivo disponibile.
    Scartato perché è oltre il 25% "LucasArts classico" che la voce sull'altezza
    dei personaggi aveva già rifiutato come troppo stretto, e mostrerebbe 240
    unità di una stanza larga 384.
  - **Non è un continuo, sono tre valori.** Le sole risoluzioni 16:9 che dividono
    1080 esattamente sono 216 (5×), 180 (6×) e 135 (8×). Qualunque valore
    intermedio dà un fattore non intero.
  - Regalo collaterale non cercato: **180 divide esattamente 720, 1080, 1440 e
    2160**, mentre 216 era nitido solo su 1080p e 4K (720/216 = 3,33 e
    1440/216 = 6,67). Il gioco è nitido su più schermi di prima, non su meno.
  - **La premessa da cui la domanda era partita era sbagliata**, e vale
    registrarla: con `canvas_items` e `aspect = keep` il gioco riempie sempre
    tutto lo schermo, quindi una base più piccola **non** dà "un effetto gigante
    su uno schermo grande". Dà pixel più grossi — 12 pixel veri per pixel di
    texture su 4K invece di 10 — e meno mondo inquadrato. Il costo è quello, non
    la dimensione della finestra.
  - **Il criterio che ha reso la modifica affrontabile**: quello che è
    dimensionato sul personaggio o sul dito non cambia, quello che è ancorato
    allo schermo sì. Quindi restano identici porta, prop, sedie, badge della
    verb-coin, altezza degli slot e font; cambiano estensioni delle stanze,
    posizioni e contenitori della UI. Effetto secondario gradito: badge e testi
    sono ora relativamente **più grandi**, quindi più facili da colpire e da
    leggere — un badge passa da 120 a 144 pixel veri su un telefono.
  - **L'atrio è stato ricomposto e non riscalato**, perché per 5/6 nessuna
    coordinata resta intera, e la pixel art vuole interi. Ne è stato approfittato
    per abbassare la linea del pavimento dal 63% al **60%**: la fascia di muro
    nudo sopra i prop era la parte più vuota dell'immagine, e abbassarla
    restituisce al pavimento la profondità calpestabile che l'inquadratura più
    stretta aveva tolto.
  - **Il corridoio è stato ricampionato, non ridisegnato**: le sue due immagini
    sorgente non stanno nel repository, per la decisione già registrata, quindi
    da 3840×1080 sono passate a 3200×900 con Lanczos. È materiale dipinto,
    morbido, che vive già sotto filtro lineare — l'unica cosa del progetto per
    cui un ricampionamento è lecito. Resta da rifare in pixel art.
  - **Le tre stanze di prova ritirate sono state riscalate meccanicamente**, non
    ricomposte: un fondale largo 384 in un mondo largo 320 farebbe scorrere la
    telecamera in verticale, e lasciarcelo era una mina. Erano blockout di
    `Polygon2D` senza composizione da salvare. Sono state cancellate poco dopo,
    quindi quel lavoro è durato due commit — e va bene così: la scelta di
    tenerle o no era dello sviluppatore, e finché erano lì dovevano essere
    coerenti.
  - Costo accettato: **si vede meno stanza**, 320 unità invece di 384. È
    esattamente ciò che si stava comprando.
  - Costo accettato e ancora da pagare: **il vuoto non è risolto**. Tre oggetti
    su un muro non riempiono una stanza a nessuna risoluzione, e il confronto
    fatto prima di decidere lo mostrava anche a 240×135. La risposta è arredare,
    che è additivo e non tocca nessuna geometria.
  - Nota: da rivedere solo se un giorno il gioco volesse stanze molto più larghe
    dello schermo, dove vedere meno mondo pesa più che vedere il personaggio
    grande.

- **Il corridoio in pixel art, e niente parallasse.** Chiude il punto che era
  rimasto aperto sui layer di parallasse, che quello stesso punto voleva deciso
  *prima* di dipingere. Il corridoio diventa un'immagine sola, 640×180, a scala 1
  e filtro Nearest come l'atrio; cadono i due piani dipinti a 3200×900, il
  `Parallax2D` e gli override a `Linear`. Il progetto torna a non avere nessun
  `Parallax2D`, che è la condizione in cui la decisione aperta lo descriveva.
  - **La tavolozza è stata presa dai prop, non imposta ai prop.** L'acciaio
    verde-grigio e l'ottone oliva sono quelli di `make_tubes_props.py`, che a
    loro volta li aveva campionati dallo sfondo dipinto ora ritirato. È il verso
    giusto: oblò, targhetta, punto d'imbuco e capsula sono arte già approvata e
    già in gioco, quindi costa meno far appartenere il muro nuovo a loro che
    ridisegnare quattro sprite per farli appartenere a un muro nuovo. Nessuno
    dei quattro è stato toccato, e misurano da 0,04 a 0,06 contro una soglia di
    0,16.
  - **Il parallasse è stato scartato, non rimandato**, e per una ragione tecnica
    che vale per qualunque stanza futura: un layer che si muove a una frazione
    della telecamera si trova a coordinate frazionarie, e con filtro `Nearest`
    la griglia di campionamento slitta — i pixel del fondo *strisciano* mentre
    la telecamera scorre. Il rimedio è agganciare il layer a unità intere, che
    scambia lo strisciamento con uno scatto: a `scroll_scale` 0,85 il fondo
    salterebbe di un'unità ogni sette di telecamera, cioè sei pixel veri di
    strappo. Nessuna delle due è gratis.
  - E soprattutto **non comprerebbe niente qui**: il generatore dei piani
    dipinti annotava già che i tubi *devono* stare sul piano di gioco, perché
    oblò, targhetta e punto d'imbuco sono hotspot inchiodati a coordinate fisse.
    Quindi al parallasse resterebbe il solo muro di fondo — una parete piatta,
    che è esattamente la cosa che guadagna meno da un layer separato. Costo
    certo, vantaggio nullo.
  - **La profondità la porta il disegno invece del movimento**: tre lampade a
    soffitto invece di una, distanti 224 unità, così nessuna schermata ne
    contiene due. Camminare da una all'altra è ciò che fa sentire la lunghezza,
    e ha il vantaggio di funzionare anche da fermi.
  - **I due battenti diventano sprite**, perché la porta ha due stati e uno
    `StateVisual` deve poterli scambiare — e perché un rettangolo di tinta unita
    in mezzo a pixel art ombreggiata si legge come un buco nel disegno. Il
    telaio invece è dipinto nel fondale: quello non cambia mai. Il corridoio non
    ha più nessun `Polygon2D`.
  - **Anche di qua la soglia era fuori posto**, 34 unità sotto la linea del
    pavimento: lo stesso difetto già corretto sull'altra faccia della stessa
    porta. È la seconda volta, quindi la regola è ora scritta nella skill.
  - Ricaduta sul peso: i due `.webp` da 137 e 140 kB diventano un `.png` da
    **6 kB**, e con essi sparisce l'ultimo asset con perdita del progetto.
  - **Nota di metodo, misurata**: il corridoio è venuto più pulito dell'atrio —
    6% di pixel isolati contro 17% — perché il suo bandeggio usa strisce di
    transizione strette (`width=0.18`) e quello dell'atrio usava il valore di
    default. L'atrio è stato riportato allo stesso numero e scende al 10%. La
    regola "il dithering va ai bordi delle fasce" era già registrata: l'atrio
    semplicemente non la rispettava, e il confronto fra due stanze l'ha reso
    visibile come un'immagine sola non faceva.

- **La postazione smette di essere un blockout**, ed è l'ultima stanza a farlo.
  Aveva quattro `Polygon2D` piatti al posto di muro, pavimento, battiscopa e
  mensola, e altri quattro al posto dei suoi oggetti. Adesso ha un fondale a
  320×180 e quattro sprite; **non ha più nessun `Polygon2D`**, come il corridoio.
  - **Ogni sprite è esattamente il rettangolo del poligono che sostituisce**, e
    con l'unica eccezione della leva sta allo stesso offset. Non è pigrizia: le
    geometrie degli hotspot sono già verificate contro la navmesh, quindi il modo
    più sicuro di cambiare il disegno è non muovere niente altro.
  - **L'eccezione è la leva, allargata da 16×40 a 20×44** per riempire la propria
    forma di collisione invece di starci dentro. Disegnata più stretta si leggeva
    come un graffio sul muro: una leva ha bisogno della sua piastra a settore per
    essere una leva, e la piastra vuole tutta la larghezza che l'hotspot già
    dichiara.
  - **La tavolozza è quella del corridoio**, ed è una scelta di finzione oltre che
    di colore: la postazione manovra la linea pneumatica, quindi è lo stesso
    impianto, lo stesso acciaio, lo stesso ottone oliva. Il tubo entra dal muro di
    sinistra e finisce nello sportello di servizio, così i due si leggono come una
    cosa sola invece di due che stanno vicine.
  - **L'ambra è l'unica nota calda della stanza, e viene spesa dove serve**: lo
    schermo della consolle, la sua lampada, la spia della leva. In un ambiente
    tutto freddo il caldo è il canale più rapido per dire dove si lavora — cioè
    dove sta l'enigma. È la stessa logica dell'ocra nell'atrio, dove era l'unica
    nota calda e veniva dai capelli di Lino.
  - **La mensola resta dipinta nel fondale**, il registro no. Il criterio è quello
    già registrato: la mensola non cambia mai e nessuno la tocca, il registro è un
    hotspot e deve poter cambiare aspetto.
  - **Lo schema della linea appeso al muro non ha lettere.** Nessuna scritta è
    promettibile a questa dimensione, e quello che va letto sta nei testi
    dell'hotspot; il quadro dà solo linee e spinotti, cioè dice *cosa* è la stanza
    senza dover essere leggibile.
  - Un guadagno che non era l'obiettivo: `bg_station.png` sta in **6 kB** e la
    stanza ha 17 colori, quindi il prototipo intero — tre stanze, sedici prop,
    otto icone, due fogli personaggio — pesa meno di uno solo dei vecchi sfondi
    dipinti.
  - I due generatori degli sfondi dipinti, `make_lobby_background.py` e
    `make_tubes_background.py`, sono rimasti morti per un commit e poi
    cancellati, insieme a tutto il resto del non raggiungibile.

- **Si cancella tutto quello che non è raggiungibile**, e "raggiungibile" ha una
  definizione operativa e non un'opinione: si parte da `project.godot` — scena
  principale, autoload, icona — si segue ogni `res://` in modo transitivo, e per
  gli script anche il riferimento per `class_name`, che non passa da un percorso.
  Quello che resta fuori non esiste per il gioco. Sono usciti **sedici file**.
  - **Tre stanze**: `TestRoom`, `Hallway`, `LongHall`. Erano tenute perché erano
    superficie già verificata, e la voce che le teneva diceva "si cancellano
    quando vuoi": è stato chiesto.
  - **Due generatori morti**, quelli degli sfondi dipinti, che producevano file
    che non esistono più.
  - **Un dialogo, una sequenza, un suono**: il funzionario, il distributore e il
    carillon, che vivevano solo nelle stanze ritirate.
  - **E la parte che non si vedeva a occhio: quattro oggetti d'inventario.**
    Togliendo quelle stanze, `sticker`, `button`, `labelled_button` e `form`
    diventano **non ottenibili** — nessuna stanza, nessun dialogo e nessuna
    sequenza li mette più in mano, e la ricetta adesivo+pulsante non è più
    raggiungibile. Il catalogo li teneva in vita artificialmente, perché serve a
    risolvere gli id di un salvataggio e quindi nomina tutti gli oggetti: cercare
    i riferimenti non basta, va calcolato **cosa il gioco sa dare**, chiudendo
    anche sulle ricette. Via loro sono uscite quattro icone e settantuno chiavi di
    testo.
  - **Il criterio che ha protetto `tools/`**: quegli script non sono raggiungibili
    da `project.godot` per costruzione — non lo sono mai stati — e cancellarli
    perché "non usati" sarebbe stato leggere lo strumento sbagliato. Restano
    perché la decisione registrata dice che un asset che nessuno sa rifare è un
    asset che non si può correggere. Sono stati tolti i due che rifacevano
    qualcosa che non c'è più, che è un'altra cosa.
  - **Ogni sistema conserva almeno un esempio vivo**, ed è la verifica che rende
    il taglio sicuro invece che solo pulito: combinazioni sì
    (modulo + targhetta = reclamo), dialoghi sì (la consolle), sequenze sì (la
    leva), punti di passaggio sì (imbuco pubblico e sportello di servizio, che
    condividono il `cache_id`). Non è stato cancellato nessun sistema, solo la
    sua seconda copia.
  - **La versione del salvataggio passa a 3.** Una partita che nomina una stanza
    che non esiste più carica in un `RoomContainer` vuoto: nessuna regione di
    navigazione, quindi nessuno cammina. È lo stesso soft lock che la versione 2
    rifiutava per la geometria spostata, per un'altra strada.
  - Il conto finale, che è il motivo per cui vale la pena: **109 chiavi di testo
    invece di 180**, quattro oggetti invece di otto, tre stanze invece di sei. Da
    qui in avanti la scrittura della storia riguarda solo cose che esistono.
  - Nota di metodo: il controllo di raggiungibilità è uno script di venti righe e
    va rifatto quando si taglia, non tenuto. Ma la sua conclusione va verificata
    in tre modi che restano — ogni `res://` risolve, le due lingue hanno le stesse
    chiavi e ogni chiave è usata, `gdparse` passa — e sono i tre controlli che
    hanno detto che il taglio era completo e non eccessivo.

## Decisioni ancora aperte
- **Formato di scrittura dei dialoghi**: il runtime consuma risorse `.tres`, ma
  resta da vedere se scriverle a mano regga quando le conversazioni saranno vere
  e lunghe. L'alternativa è un file di testo in formato copione con un parser
  che produce le stesse risorse — si aggiunge senza toccare il runtime, quindi
  la decisione si prende con in mano il primo dialogo vero e non prima. Lo
  stesso vale per le sequenze, che hanno lo stesso problema in piccolo
- **La scala per profondità contro la pixel art**, ed è il vero conflitto aperto
  dallo stile ibrido. La prospettiva delle stanze scala la figura del personaggio
  di un fattore continuo (nell'atrio da 0,85 a 1,05), e questo rompe la regola per
  cui un pixel di texture è un'unità di gioco: a 0,85 su uno schermo 5× un pixel
  di texture diventa 4,25 pixel veri, quindi alcuni escono 4 e altri 5.
  **Ora c'è lo sprite per giudicare, e la prova è fatta**: l'irregolarità si vede,
  e si vede peggio dove meno serve — sul viso, dove un occhio esce largo quattro
  pixel e l'altro cinque, che l'occhio umano legge come asimmetria della faccia e
  non come rumore. Resta da guardarla **sul dispositivo e in movimento**, perché
  un personaggio che cammina cambia scala di continuo e potrebbe nasconderla.
  La mia raccomandazione, da confermare guardandola: **nell'atrio metterla a 1 e
  1**. Un intervallo del 24% su 60 unità di pavimento non si legge come
  prospettiva, quindi oggi si pagano artefatti visibili per un effetto invisibile;
  la funzione resta, e si accende nelle stanze con un pavimento davvero profondo.
  Nota sulla via di mezzo: **quantizzare a pochi gradini non risolve**, perché il
  fattore intero dipende anche dalla dimensione della finestra — 0,8 è esatto a 5×
  e non lo è a 3×. Cambiarla resta una funzione sola (`_depth_scale()`)
- **Ambienza e musica insieme, o no**: `AudioDirector` ha due riproduttori, e le
  categorie `amb` e `mus` della skill audio competono per lo stesso. In
  un'avventura una stanza vuole spesso un tappeto ambientale *sotto* un tema.
  Terzo riproduttore — che revoca la decisione "due riproduttori e basta" — o si
  rinuncia a una delle due
- **Suono dei passi**: il gioco cammina sempre, è l'azione più frequente che ha, e
  non fa alcun rumore. Servono un suono per superficie sulla stanza e un aggancio
  nel personaggio che lo faccia scattare a cadenza. È il sistema nuovo più
  impattante che le skill mettono sul tavolo, e il più udibile
- **Se il gioco ha una voce**: `vox` non ha un posto perché la voce è la
  `Caption`. Un borbottio stile LucasArts sincronizzato con la battuta vorrebbe
  un campo su `Dialogue` e qualcosa che lo faccia partire, e cambierebbe il
  carattere del gioco più di quanto sembri. Legata a questa, in piccolo: il
  *text blip* della skill richiede che la caption scriva a scorrimento invece di
  apparire tutta insieme
- **Più slot di salvataggio**: oggi sono due, uno manuale e uno automatico. Se
  servano slot numerati si saprà quando il gioco sarà lungo abbastanza da voler
  tornare indietro di un capitolo e non di una stanza
- Durata finale del gioco (valutare dopo il prototipo)
- **Storia completa** (punto 6): premessa, personaggi, ambientazione e capitoli
  oltre il prototipo. Il prototipo ha fissato *un* incastro che funziona — la
  separazione per autorizzazione — ma non la storia: nomi, luogo e trama sono
  ancora tutti da decidere, e ora si puo' farlo sapendo quali vincoli di design
  la trama deve rispettare
- Nome del progetto

## Comportamento di Claude Code su questo progetto
- **Lingua conversazione**: italiano. **Lingua codice**: inglese per nomi di
  classi/metodi/variabili e commenti (convenzione standard, resta comunque
  leggibile e coerente col resto dell'ecosistema Godot)
- Questo è il primo progetto di game dev dello sviluppatore (esperto in
  C#/.NET ma non in game engine né in GDScript): spiegare i concetti specifici
  di Godot (signal, scene tree, node, autoload, ecc.) la prima volta che
  vengono introdotti, senza darli per scontati. Dove GDScript si comporta
  diversamente dal C#, dirlo esplicitamente invece di lasciarlo scoprire
- Lo sviluppo avviene su **telefono Android**: preferire modifiche che si
  possano verificare premendo Play, ed evitare di scaricare sullo sviluppatore
  editing manuale lungo nell'editor quando si può esprimere la stessa cosa nel
  file di scena
- **Allineare `main` a ogni push**: dopo aver pushato il branch di lavoro,
  portare `main` allo stesso commit (fast-forward) e pushare anche quello,
  senza chiedere. Deciso dopo che un `main` rimasto indietro ha fatto provare
  sul dispositivo una versione vecchia del gioco per parecchi giri, con i
  sintomi attribuiti al codice nuovo invece che al codice mancante
- **Chiudere l'editor Godot prima di `git pull`**, e guardare `git status
  --short` prima di tirare. Godot riscrive da sé alcuni `.tres` quando apre il
  progetto, quindi un pull trova modifiche locali che nessuno ha scritto; e se
  l'editor viene ucciso mentre salva — scartato col pollice, o dall'OOM killer —
  il cancella-e-riscrivi si ferma a metà e il file resta assente. Su
  `/storage/emulated/0` il livello FUSE può poi restare in uno stato in cui
  l'elenco della cartella non vede quel file ma la ricerca per nome sì: git
  prova a rimuoverlo prima di riscriverlo, il sistema risponde `No such file or
  directory`, e `pull`, `restore` e `reset --hard` si fermano tutti nello stesso
  punto. Il riavvio del telefono non lo scioglie, e dallo spazio utente non c'è
  comando che lo sistemi.
  - **Non usare `git reset --hard` per uscirne**: scrive il working tree e *poi*
    l'indice, quindi fallendo sui file fantasma lascia il clone spaccato in due
    — contenuto nuovo nei file, `HEAD` vecchio — e da lì ogni pull elenca mezzo
    repository come modifica locale. È il comando che ha trasformato due file
    bloccati in una cartella da buttare.
  - **La via corta è riclonare** in una cartella nuova e importare il progetto
    da lì: un comando, contro sei giri di riparazione che non hanno funzionato.
    In quei `.tres` non c'è mai una riga scritta dallo sviluppatore — la verità
    di quei file sta nel repository, quindi non c'è niente da salvare.
  - Due attriti dell'ambiente che si incontrano riclonando: la memoria condivisa
    riporta ogni file come proprietà di un uid fisso, quindi git rifiuta il clone
    nuovo con `detected dubious ownership` finché il percorso non è in
    `safe.directory` (o `'*'`, ragionevole su un telefono a utente singolo); e
    non permette di rinominare directory, quindi la cartella rotta non si sposta
    — si neutralizza cancellandole `project.godot`, così l'editor non la propone
    più nella lista progetti, e si elimina dall'app Files invece che dalla shell.
- **Skill disponibili**, e sono **sei**: `godot-gdscript` (convenzioni e trappole
  di GDScript), `narratore` (materiale narrativo, con l'attrattore documentato),
  `registra-decisione` (questa sezione), `vincolo-ip` (controllo IP),
  `pixel-adventure-assets` (pixel art, sprite, sfondi e verifica degli asset) e
  `retro-adventure-audio` (suoni, ambienze, musica e stinger via numpy/scipy).
  Le ultime due sono generiche e arrivano da fuori: ognuna ha una sezione
  "Vincoli di AGGGA" che la lega a questo progetto, e va letta **prima** di
  produrre qualcosa — è lì che stanno la risoluzione, il filtro texture, i due
  soli riproduttori audio e i nomi dei file già in uso.
  **Chi aggiunge una skill aggiorna questo elenco nello stesso commit**: una
  skill che c'è nel repository ma non qui si attiva lo stesso, perché a
  sceglierla è la sua `description` e non questa lista. È così che
  `pixelart-adventure` è rimasta per giorni a contraddire i numeri del progetto
  senza che l'elenco lo dicesse
- **Le librerie delle skill non sono installate nell'ambiente remoto**:
  `pip install pillow numpy` per la grafica, `pip install numpy scipy` per
  l'audio, come si fa già con `gdtoolkit`
- **Ogni asset grafico passa da `qa_check.py` prima del commit**, come ogni
  `.gd` passa da `gdparse`: `python .claude/skills/pixel-adventure-assets/
  scripts/qa_check.py <file> --profile sheet|sprite|shadow|background
  [--palette-from <sfondo>]`. Esce con 1 se qualcosa fallisce
- **Godot non è installato nell'ambiente remoto, ma un parser GDScript sì**:
  `pip install gdtoolkit` mette a disposizione `gdparse`, che legge la
  sintassi di un `.gd` senza bisogno dell'engine. Installalo e passaci ogni
  script toccato prima di committare — costa qualche secondo ed evita di
  spedire allo sviluppatore un errore di sintassi che scoprirebbe premendo
  Play. Non verifica i tipi né i nomi: solo la forma
- Prima di implementare scelte architetturali importanti (es. come gestire
  lo stato dei personaggi, come strutturare i dialoghi), proporre alternative
  con pro/contro e motivare la scelta consigliata, non eseguire e basta
- Chiedere conferma esplicita prima di modifiche strutturali grosse o che
  toccano più sistemi contemporaneamente
- Rispettare rigidamente il vincolo IP sopra: nessun riferimento diretto a
  Guida Galattica per Autostoppisti in codice, commenti, asset o dialoghi
- Ogni decisione di design/architettura rilevante va registrata in questo
  file (sezione "Decisioni prese"), incluse le alternative scartate e il
  perché — non solo il risultato finale
