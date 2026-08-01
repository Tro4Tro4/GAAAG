---
name: godot-gdscript
description: Convenzioni, pattern e trappole per scrivere GDScript in Godot 4 nel progetto AGGGA, con particolare attenzione a dove GDScript si comporta diversamente dal C#. Usa questa skill ogni volta che scrivi, modifichi o revisioni codice GDScript — script di nodi, segnali, accesso al scene tree, autoload, risorse, input, istanziazione di scene — e quando spieghi all'utente un concetto dell'engine. Usala anche quando l'utente chiede "come si fa in Godot", "perché non funziona questo nodo", "come collego questo segnale", "come faccio a passare dati tra scene", "in C# come si scriveva", o quando il codice proposto sarebbe corretto in C#/.NET ma in GDScript si rompe o non esiste (generics, interfacce, costruttori, riferimenti a nodi liberati).
---

# Godot 4 + GDScript — AGGGA

Chi scrive questo progetto è esperto di C#/.NET ma non di game engine né di
GDScript. Questa skill copre due cose: ciò che il C# ordinario non prepara ad
affrontare in un engine, e ciò che GDScript fa diversamente dal C#.

Il progetto è nato in C# ed è stato convertito a GDScript perché lo sviluppo
avviene sull'editor Godot per Android, che non supporta C# (vedi `CLAUDE.md`,
"Da C# a GDScript"). Il codice C# non esiste più nel repository, ma
l'aspettativa mentale di chi scrive resta quella: dove le due strade divergono,
**dillo esplicitamente** invece di lasciarlo scoprire a runtime.

## Il cambio di modello mentale

In .NET l'applicazione è un grafo di oggetti che *tu* costruisci e possiedi.
In Godot l'unità è il **nodo**, e l'engine possiede l'albero. I nodi vivono in
uno **scene tree**: una gerarchia che l'engine attraversa ogni frame per
disegnare, aggiornare e instradare l'input.

La conseguenza pratica, da cui discendono quasi tutte le trappole sotto: il
ciclo di vita di un oggetto non è più governato dal costruttore e dal garbage
collector, ma dall'ingresso e dall'uscita dall'albero.

Una **scena** (`.tscn`) è semplicemente un sottoalbero salvato su file e
riusabile — l'equivalente più vicino è un componente riutilizzabile, non una
"schermata".

Quando introduci per la prima volta uno di questi concetti in conversazione,
spiegalo: `CLAUDE.md` lo richiede esplicitamente.

## Cosa il C# aveva e GDScript non ha

Questa lista serve a non proporre soluzioni che non compilano. Non sono
mancanze da compensare con acrobazie: sono vincoli che portano a scrivere il
codice in un altro modo, di solito più semplice.

- **Niente generics.** Non esiste `Array<T>` parametrico nelle firme. Esiste
  `Array[Tipo]` come tipo di variabile (`var oggetti: Array[Hotspot] = []`),
  ma non si scrivono funzioni generiche.
- **Niente interfacce.** Il sostituto idiomatico è il **duck typing**
  controllato: `if oggetto.has_method("interagisci")`. Per un contratto più
  esplicito si usa una classe base con `class_name` e metodi vuoti da
  sovrascrivere.
- **Niente `private`/`public`.** La convenzione — non un vincolo del
  linguaggio — è l'underscore iniziale per ciò che è interno: `_is_walking`,
  `_stop_walking()`. Va rispettata perché è l'unico segnale disponibile.
- **Niente LINQ.** Ci sono `filter()`, `map()`, `reduce()`, `any()`, `all()`
  sugli array, e per il resto cicli `for` espliciti.
- **Niente `try`/`catch`.** Gli errori si prevengono con i controlli, non si
  catturano. Per le condizioni che non devono mai accadere c'è `assert()`,
  attivo solo nelle build di debug.
- **Tipizzazione statica opzionale e più debole.** `var x: int = 0` e
  `func f() -> void` funzionano e **vanno sempre usati** in questo progetto:
  danno errori in fase di parsing invece che a runtime, e rendono il codice
  leggibile a chi arriva dal C#. Ma non c'è un compilatore che verifichi tutto.

## Le trappole

### L'indentazione è sintassi

Blocchi definiti dall'indentazione, come in Python. Godot usa **tabulazioni**,
non spazi: mischiarle produce errori di parsing. Nessuna graffa, nessun
punto e virgola.

### `not x is Y` — scrivi la forma positiva

```gdscript
if not event is InputEventMouseButton:   # da evitare
	return

if event is InputEventMouseButton:       # preferibile
	var mouse_event: InputEventMouseButton = event
	...
```

La forma negata mescola `not` e `is` in un punto dove la precedenza non è
ovvia a chi legge, e in questo progetto un `_unhandled_input` scritto così non
ha mai reagito ai click, senza che fosse evidente il perché. Preferisci il
ramo positivo con una variabile tipizzata: elimina l'ambiguità e ti dà
l'accesso statico alle proprietà della sottoclasse, che sull'`InputEvent` di
partenza non esistono.

Vale in generale: quando una condizione mescola operatori di tipo e operatori
logici, o metti le parentesi o riscrivila in positivo.

### I costruttori non servono per inizializzare

Godot costruisce l'oggetto, poi lo inserisce nell'albero, poi applica i valori
esportati dall'editor. In `_init()` i figli non esistono ancora e i valori
dell'editor non sono stati assegnati.

```gdscript
func _ready() -> void:
	# Qui i figli esistono e i valori @export sono stati applicati.
	pass
```

`_ready()` scatta una volta all'ingresso nell'albero. Nota l'ordine: **i figli
sono pronti prima dei genitori**, quindi un genitore può contare sui figli in
`_ready()`, mai il contrario.

### Un nodo liberato non è `null`

```gdscript
porta.queue_free()              # libera l'oggetto a fine frame
if porta != null:               # può essere ancora vero
if is_instance_valid(porta):    # corretto
```

`queue_free()` differisce a fine frame ed è quasi sempre la scelta giusta;
`free()` è immediato e pericoloso durante l'elaborazione.

### I percorsi stringa si rompono in silenzio

```gdscript
get_node("Visual/Body/Sprite")   # fragile
```

Basta rinominare o spostare un nodo nell'editor e il percorso salta a runtime,
senza che nulla lo segnali prima. Le alternative:

```gdscript
@onready var sprite: Sprite2D = $Visual/Sprite  # posizionale ma esplicito
@onready var sprite2: Sprite2D = %Sprite        # unique name, ovunque nella scena
@export var sprite3: Sprite2D                   # assegnato a mano nell'editor
```

`@onready` ritarda l'assegnazione a `_ready()`, che è l'unico momento in cui i
figli esistono davvero. Il prefisso `%` indica un *unique name*, da impostare
nella scena con `unique_name_in_owner = true`: sopravvive agli spostamenti del
nodo, ma deve essere unico per scena, quindi non serve per nodi ripetuti (due
hotspot con lo stesso figlio `ApproachPoint` non possono usarlo).

### Non usare `@export` per i riferimenti a nodi in questo progetto

È la scelta che la documentazione di Godot suggerisce, e nell'editor funziona.
Qui no, e la ragione è il modo in cui si lavora: le scene di AGGGA vengono
**scritte come testo**, non composte trascinando nodi nell'Inspector.

Un `@export` di tipo nodo si salva nel `.tscn` come `NodePath("Figlio")`, e la
conversione da percorso a nodo avviene durante l'istanziazione della scena.
Scrivendo quella riga a mano il collegamento **non risulta disponibile** quando
serve: in questo progetto un `@export var player: PlayerCharacter` con
`player = NodePath("Player")` nel file di scena è arrivato a `_ready()` come
`Nil`, con l'errore che compariva sulla riga successiva — quella che usava il
riferimento — invece che sulla dichiarazione.

Peggio: il sintomo può essere silenzioso. Se il riferimento serve solo dentro
un gestore di input, la scena parte, si vede tutto, e semplicemente nulla
reagisce al click.

Regola operativa: **i riferimenti a nodi si risolvono con `@onready`**.
`@export` resta ottimo per i valori — numeri, stringhe, booleani, colori, che
dal `.tscn` si applicano senza problemi.

### I segnali sono l'accoppiamento debole dell'engine

Un **segnale** è il meccanismo di notifica di Godot: l'equivalente concettuale
di un evento .NET. Serve a far comunicare un nodo con altri senza che li
conosca — la base per tenere separati i sistemi di AGGGA.

```gdscript
signal item_collected(item_id: String)

item_collected.emit(item_id)              # emissione
hotspot.item_collected.connect(_on_item_collected)   # sottoscrizione
```

Anche i segnali predefiniti funzionano così:

```gdscript
bottone.pressed.connect(_on_bottone_premuto)
```

Rispetto al C# sparisce tutto il rituale: niente suffisso `EventHandler`,
niente `SignalName`, niente `delegate`.

### `_process` viene chiamato ogni frame

Sessanta volte al secondo o più. Qualunque `get_node()` o ricerca per stringa
qui dentro si paga sessanta volte al secondo. Risolvi i riferimenti in
`_ready()` (o con `@onready`) e conservali in variabili.

Per un punta-e-clicca la maggior parte della logica è a eventi, non a frame:
se ti trovi a scrivere molto codice in `_process`, probabilmente andava in un
segnale.

### Parametri inutilizzati e avvisi

Godot segnala i parametri non usati. Il prefisso underscore li zittisce, ed è
la convenzione corretta quando la firma è imposta dall'engine:

```gdscript
func _physics_process(_delta: float) -> void:
```

## Convenzioni del progetto

**Lingua**: nomi e commenti in inglese, come stabilito in `CLAUDE.md`. Le
conversazioni restano in italiano.

**Nomenclatura**: `snake_case` per funzioni e variabili, `PascalCase` per i
`class_name`, `SCREAMING_SNAKE_CASE` per le costanti, underscore iniziale per
ciò che è interno. È la convenzione ufficiale di Godot e differisce da quella
C#: non riportare `PascalCase` sui metodi per abitudine.

**File**: gli script `.gd` in `snake_case` (`player_character.gd`), le scene
`.tscn` in `PascalCase` (`TestRoom.tscn`). È la convenzione dell'ecosistema.

**Struttura**: `scripts/` rispecchia `scenes/`. Uno script per nodo che ha
comportamento; i nodi puramente strutturali non ne hanno bisogno.

**Tipi**: sempre espliciti, sia sulle variabili sia sui valori di ritorno.
Non è obbligatorio nel linguaggio, è una regola di questo progetto.

**Documentazione**: `##` sopra una dichiarazione diventa documentazione visibile
nell'editor; `#` è un commento ordinario.

## Pattern che serviranno in AGGGA

### Stato globale: autoload

Un **autoload** (o singleton) è una scena o uno script che Godot carica
all'avvio e tiene vivo per tutta la partita, fuori dalle scene ordinarie. È il
posto giusto per lo stato che sopravvive al cambio di stanza: flag di gioco,
inventario, personaggio attivo.

Si registra in *Project Settings → Autoload*, e da lì il nome scelto è
raggiungibile globalmente come una variabile:

```gdscript
GameState.active_character = player
```

Comodo, ma è accoppiamento globale: `CLAUDE.md` chiede di proporre le
alternative prima di introdurne uno.

### Istanziare una scena da codice

```gdscript
@export var item_scene: PackedScene

var item := item_scene.instantiate()
add_child(item)
```

Una `PackedScene` è la scena non ancora istanziata — il progetto, non
l'edificio. Finché non fai `add_child()`, il nodo esiste ma è fuori
dall'albero: non viene disegnato e `_ready()` non è ancora scattato.

### Input: pensare da subito al touch

AGGGA ha come target anche mobile, e un punta-e-clicca è fatto di click.

```gdscript
func _unhandled_input(event: InputEvent) -> void:
	if not event is InputEventMouseButton:
		return
	if not event.pressed or event.button_index != MOUSE_BUTTON_LEFT:
		return
```

Usa `_unhandled_input` e non `_input` per l'input di gioco: così l'interfaccia
(verb-coin, inventario) intercetta ciò che le compete prima che arrivi alla
stanza, ed eviti che un click su un bottone finisca anche sullo sfondo.

Sul touch, Godot può emulare il mouse (*Project Settings → Input Devices →
Pointing → Emulate Mouse From Touch*). Funziona per il click semplice, ma non
copre l'assenza di hover — su mobile non esiste il passaggio del puntatore.
È un vincolo di design da tenere presente per la verb-coin, non un dettaglio
implementativo: va deciso quando si progetterà quel sistema. Vale doppio ora
che lo sviluppo stesso avviene su un telefono.

### Attendere senza bloccare

```gdscript
await get_tree().create_timer(1.5).timeout
await character.destination_reached
```

`await` esiste anche in GDScript e funziona sui segnali: la seconda riga è
esattamente il mattone su cui si costruirà "cammina fino all'hotspot, poi
esegui il verbo". Non esistono thread da gestire; non usare cicli di attesa,
bloccano il frame e congelano il gioco.

## Prima di dire "fatto"

GDScript non ha passo di compilazione: si salva e si preme Play. È il
vantaggio pratico più grande della conversione, e cambia cosa significa
"verificato".

In questo ambiente remoto **Godot non è installato**: il codice non può essere
eseguito qui. Ma può essere eseguito dallo sviluppatore, sul telefono, subito.
Quando proponi una modifica, dì esplicitamente cosa dovrebbe vedere premendo
Play — è la verifica vera, e adesso è a portata di mano.
