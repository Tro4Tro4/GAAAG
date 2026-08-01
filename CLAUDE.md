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
- Punta-e-clicca classico con **verb-coin** (Cammina, Guarda, Prendi, Usa,
  Parla, ecc. — da finalizzare la lista esatta dei verbi)
- **Più personaggi giocabili**, switch libero tra loro
- Puzzle che richiedono collaborazione tra personaggi diversi in luoghi
  diversi (es. uno passa un oggetto attraverso una finestra, l'altro lo
  raccoglie dall'altro lato)
- Inventario: **da decidere** se condiviso tra personaggi o separato per
  ciascuno
- Dialoghi ad albero con condizioni legate a flag/stato di gioco

## Ordine di sviluppo previsto
1. Sistema base: movimento *(fatto e **verificato sul dispositivo**:
   click-to-walk con navmesh, l'ostacolo viene aggirato)*, stanze *(scena
   `Room` minima)*, hotspot cliccabili *(fatti: cammina fino all'oggetto e
   mostra la descrizione)*, verb-coin UI *(da fare)*
2. Sistema personaggi multipli: switch *(fatto: autoload `GameState`, barra di
   cambio, due personaggi nella stessa stanza)*, stato indipendente per
   personaggio *(parziale: ognuno ha la sua posizione; il resto arriverà con
   inventario e flag)*, multi-stanza *(da fare)*
3. Sistema inventario
4. Sistema dialoghi con condizioni
5. Prototipo verticale: 1 stanza, 2 personaggi, 1 puzzle cooperativo completo
6. Solo dopo il prototipo: scrittura della storia completa, capitoli,
   altre stanze, durata finale del gioco (ancora da stabilire)

## Struttura del progetto
```
project.godot        Configurazione progetto Godot (renderer, display)
icon.svg             Icona placeholder
scenes/              Scene Godot (.tscn), nomi in PascalCase
  rooms/TestRoom     Stanza di prova, scena di avvio del progetto
                     (navmesh, due hotspot, riga di testo)
  characters/Player  Personaggio giocabile (CharacterBody2D + NavigationAgent2D)
scripts/             Codice GDScript (.gd), nomi in snake_case,
                     rispecchia l'albero di scenes/
  autoload/          Stato che sopravvive alle scene (game_state.gd)
  ui/                Interfaccia (caption.gd, character_bar.gd)
assets/              sprites/ backgrounds/ audio/ fonts/
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
  (`emulate_mouse_from_touch`, ora dichiarato esplicitamente in
  `project.godot` invece di essere lasciato al default): un solo percorso di
  codice per desktop e mobile, e i nodi `Control` — quindi la futura verb-coin
  e l'inventario — continuano a rispondere al tocco senza codice dedicato.
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

## Decisioni ancora aperte
- **Multi-stanza**: come si caricano e scaricano le stanze, dove vivono i
  personaggi che non sono nella stanza mostrata, e come si conserva la loro
  posizione mentre la loro stanza non è caricata. Oggi i personaggi sono figli
  della stanza, il che va bene finché la stanza è una sola
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
- Inventario condiviso vs per personaggio
- Lista definitiva dei verbi nel verb-coin
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
