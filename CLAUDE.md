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
- **Arte**: pixel art retro, generata con strumenti AI esterni, poi
  importata/adattata nel progetto

## Vincolo IP — NON NEGOZIABILE
Nessun riferimento diretto a *Guida Galattica per Autostoppisti*: niente nomi
di personaggi (Arthur Dent, Ford Prefect, Marvin, Zaphod, Vogon...), niente
luoghi, niente citazioni o dialoghi originali del libro. L'ispirazione resta
sul **tono**: umorismo assurdo, burocrazia cosmica, fantascienza demenziale,
protagonista qualunque catapultato in situazioni incomprensibili.
Personaggi, nomi, luoghi e trama devono essere originali.

## Gameplay
- Punta-e-clicca classico con **verb-coin** a quattro posizioni fisse e un
  vocabolario chiuso di nove parole: Guarda / Prendi / Usa, Premi, Tira, Apri,
  Chiudi / Parla, Vai (camminare non è un verbo: si clicca il pavimento)
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
   icone, vocabolario di nove parole in quattro famiglie)*
2. Sistema personaggi multipli: switch *(fatto: autoload `GameState`, barra di
   cambio)*, stato indipendente per personaggio *(parziale: ognuno ha la sua
   posizione e la sua stanza; il resto arriverà con inventario e flag)*,
   multi-stanza *(fatto e **verificato sul dispositivo**: radice `Game`, due
   stanze collegate da una porta, cambiare personaggio porta nella sua stanza)*
3. Sistema inventario *(fatto e **verificato sul dispositivo**: un inventario
   per personaggio, pannello a comparsa, verbi sugli oggetti, combinazione fra
   oggetti, uso di un oggetto su un hotspot)*
4. Sistema dialoghi con condizioni
5. Prototipo verticale: 1 stanza, 2 personaggi, 1 puzzle cooperativo completo
6. Solo dopo il prototipo: scrittura della storia completa, capitoli,
   altre stanze, durata finale del gioco (ancora da stabilire)

## Struttura del progetto
```
project.godot        Configurazione progetto Godot (renderer, display)
icon.svg             Icona placeholder
scenes/              Scene Godot (.tscn), nomi in PascalCase
  Main               Scena di avvio: contiene i personaggi e la UI, e ospita
                     la stanza corrente in RoomContainer
  rooms/TestRoom     Stanza di prova (navmesh, cassa, porta per il corridoio)
  rooms/Hallway      Seconda stanza (distributore, cartello, porta di ritorno)
  characters/Player  Personaggio giocabile (CharacterBody2D + NavigationAgent2D)
scripts/             Codice GDScript (.gd), nomi in snake_case,
                     rispecchia l'albero di scenes/
  game.gd            Scambia le stanze e collega stanza, personaggi e UI
  autoload/          Stato che sopravvive alle scene (game_state.gd)
  rooms/             room.gd, hotspot.gd, door_hotspot.gd, pickup_hotspot.gd,
                     passage_hotspot.gd
  items/             inventory_item.gd, item_combination.gd,
                     combination_book.gd — dati, non nodi
  ui/                Interfaccia (caption.gd, character_bar.gd, verb_coin.gd,
                     inventory_panel.gd)
resources/           Risorse di dati (.tres), niente scene e niente codice
  items/             Un file per oggetto, più combinations.tres con le ricette
assets/              sprites/ backgrounds/ audio/ fonts/
  ui/                Le nove icone dei verbi, in SVG — l'unica arte del
                     progetto che non è pixel art
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
    definitivi.
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
  stesso verbo. Cambia il vocabolario, non la geometria. **Parzialmente
  superata** — vedi "Vocabolario chiuso di nove parole" in fondo all'elenco:
  il principio (parole variabili, posizioni fisse) è confermato, ma le parole
  non sono più stringhe libere per hotspot.
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
    campi come prima, ma reggono nove parole invece di quattro.

- **Le nove icone dei verbi sono cartoon a colori**, non sagome bianche:
  riempimenti piatti e vivaci, contorno scuro spesso, un solo tocco di luce
  per icona, e una tavolozza condivisa dalle nove così che si leggano come un
  insieme e non come nove disegni scollegati. Il motivo è che su un badge di
  ventiquattro unità, con il dito lì accanto e mezzo secondo di gesto, **il
  colore arriva prima della forma**: il rosso del pulsante di "Premi" e il
  giallo del vano di "Apri" si distinguono ancora prima di essere riconosciuti
  come disegni, mentre due sagome dello stesso bianco vanno confrontate. Il
  vocabolario è chiuso e le posizioni sono fisse, quindi il giocatore impara
  nove colori una volta e poi mira senza leggere — che è esattamente ciò su
  cui il premi-trascina-rilascia vive.
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
  contorno scuro spesso e tinte piatte restano). Otto delle nove — Guarda,
  Prendi, Usa, Premi, Tira, Apri, Chiudi, Parla — sono il tracciamento di
  immagini scelte dallo sviluppatore; solo Vai è ancora disegnata a mano.
  Il motivo è misurato, non teorico: la sola mano di "Prendi" ha richiesto
  sei tentativi disegnati (palmo aperto, guanto, pugno, mano dall'alto, mano
  protesa, mano con oggetto), tutti scartati, e ha funzionato al primo colpo
  partendo da un'immagine. A ventiquattro unità la differenza tra una forma
  riconoscibile e una macchia è di frazioni di unità, e l'occhio perdona meno
  dove il soggetto è familiare — una mano, una bocca, un occhio.
  Tutte e nove vengono da immagini: Guarda un occhio, Prendi un palmo aperto,
  Usa un ingranaggio, Premi una mano che schiaccia un pulsante, Tira un pugno
  che tira una corda, Apri e Chiudi la stessa porta, Parla una bocca, Vai due
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
    rimedio è chiedere un'altra immagine, non aggiustarla. Il primo
    riferimento per Premi era un dorso di mano e nient'altro: l'ho composto a
    mano — tagliato al polso perpendicolarmente all'asse dell'avambraccio,
    girato verso il basso e posato su un pulsante disegnato — e funzionava,
    ma è stato sostituito appena arrivata un'immagine che il gesto lo mostrava
    già. La regola che resta: **serve il bersaglio, non solo la mano**. Una
    mano che preme senza qualcosa sotto non è distinguibile da una mano.
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
  - Nota: da rivedere se il badge diventasse chiaro. Il contorno scuro
    regge, ma il panna dell'occhio e del fumetto perderebbe contrasto e
    andrebbero ripensati due riempimenti su nove.

## Decisioni ancora aperte
- **Telecamera**: oggi ogni stanza è esattamente grande quanto lo schermo
  (384×216) e non c'è nessuna `Camera2D`. Serve deciderlo prima di disegnare
  una stanza più larga. Il codice è già pronto per l'eventualità: la stanza
  distingue le coordinate del mondo da quelle dello schermo quando apre la
  verb-coin, e la UI sta su un `CanvasLayer` che la telecamera non muove
- **Persistenza dello stato di una stanza, oltre al "già preso"**: i flag di
  `GameState` coprono ora ciò che l'inventario richiedeva — un oggetto raccolto
  resta raccolto anche uscendo e rientrando. Restano scoperti i cambiamenti che
  non riguardano un oggetto: una porta che si è aperta, una leva abbassata, un
  hotspot che deve cambiare descrizione. Il meccanismo c'è già (`accepted_flag`
  viene alzato ma oggi nessuno lo legge); manca la parte che fa reagire una
  stanza ai flag mentre si ricostruisce. Da progettare insieme ai dialoghi, che
  useranno gli stessi flag come condizioni
- Profondità: se e come scalare il personaggio in base alla Y (curva Y→scala)
  e come ordinare il disegno rispetto agli oggetti della stanza (Y-sorting)
- Avvicinamento agli hotspot da più lati: oggi il punto di avvicinamento è
  uno solo, quindi arrivando dal lato opposto il personaggio gira attorno
  all'oggetto. Nei LucasArts era spesso voluto — si arriva in un punto noto,
  rivolti in una direzione nota, perché l'animazione dell'azione torni — ma per
  un oggetto accessibile da tutti i lati è innaturale. Opzioni: più marker con
  scelta del più vicino; nessun marker e punto calpestabile più vicino
  all'oggetto; raggio di interazione entro cui non si cammina affatto. Da
  decidere quando esisteranno animazioni direzionali e stanze vere: si innesta
  tutto in `get_approach_position()` e non blocca nessun altro sistema
- **Lingua dei testi di gioco** (descrizioni, dialoghi, nomi visibili): ora
  sono in italiano come segnaposto, ma non è una decisione presa. Da valutare
  insieme all'eventuale localizzazione, che in Godot conviene impostare prima
  di avere testo sparso nelle scene
- Durata finale del gioco (valutare dopo il prototipo)
- Nome del progetto, dei personaggi, ambientazione specifica

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
