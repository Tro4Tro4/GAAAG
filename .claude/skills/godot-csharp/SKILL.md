---
name: godot-csharp
description: Convenzioni, pattern e trappole per scrivere codice C# in Godot 4 nel progetto AGGGA. Usa questa skill ogni volta che scrivi, modifichi o revisioni codice C# che tocca Godot — script di nodi, segnali, accesso al scene tree, autoload, risorse, input, istanziazione di scene — e quando spieghi all'utente un concetto dell'engine. Usala anche quando l'utente chiede "come si fa in Godot", "perché non funziona questo nodo", "come collego questo segnale", "come faccio a passare dati tra scene", o quando il codice C# proposto compila in .NET ma userebbe pattern che in Godot si rompono (costruttori, campi statici, System.Collections nei membri esportati, riferimenti a nodi liberati).
---

# Godot 4 + C# — AGGGA

Chi scrive questo progetto è esperto di C#/.NET ma non di game engine.
Questa skill copre ciò che il C# ordinario non prepara ad affrontare.

## Il cambio di modello mentale

In .NET l'applicazione è un grafo di oggetti che *tu* costruisci e possiedi.
In Godot l'unità è il **nodo**, e l'engine possiede l'albero. I nodi vivono in
uno **scene tree**: una gerarchia che l'engine attraversa ogni frame per
disegnare, aggiornare e instradare l'input.

La conseguenza pratica, da cui discendono quasi tutte le trappole sotto: il
ciclo di vita di un oggetto non è più governato dal costruttore e dal garbage
collector, ma dall'ingresso e dall'uscita dall'albero. Un nodo C# è un guscio
gestito attorno a un oggetto nativo; i due possono morire in momenti diversi.

Una **scena** (`.tscn`) è semplicemente un sottoalbero salvato su file e
riusabile — l'equivalente più vicino è un componente riutilizzabile, non una
"schermata".

Quando introduci per la prima volta uno di questi concetti in conversazione,
spiegalo: `CLAUDE.md` lo richiede esplicitamente, e sono concetti che non si
deducono dall'esperienza .NET.

## Le trappole

### `partial` è obbligatorio

```csharp
public partial class PlayerCharacter : CharacterBody2D { }
```

Un source generator produce codice di supporto per ogni classe-nodo. Senza
`partial` la compilazione fallisce con un errore che non nomina la causa
reale. È il primo inciampo di chiunque arrivi da .NET.

### I costruttori non servono per inizializzare

Godot costruisce l'oggetto C#, poi lo inserisce nell'albero, poi applica i
valori esportati dall'editor. Nel costruttore i figli non esistono ancora e i
valori dell'editor non sono stati assegnati.

```csharp
public override void _Ready()
{
    // Qui i figli esistono e i valori [Export] sono stati applicati.
}
```

`_Ready()` scatta una volta all'ingresso nell'albero. Nota l'ordine: **i figli
sono pronti prima dei genitori**, quindi un genitore può contare sui figli in
`_Ready()`, mai il contrario.

### Un nodo liberato non è `null`

```csharp
_door.QueueFree();          // libera l'oggetto nativo a fine frame
if (_door != null) { }      // vero: il guscio C# esiste ancora
if (IsInstanceValid(_door)) // corretto
```

Il riferimento C# sopravvive all'oggetto nativo. Usare il nodo dopo la
liberazione produce un errore a runtime, non una `NullReferenceException`
riconoscibile. `QueueFree()` differisce a fine frame ed è quasi sempre la
scelta giusta; `Free()` è immediato e pericoloso durante l'elaborazione.

### I percorsi stringa si rompono in silenzio

```csharp
GetNode<Sprite2D>("Visual/Body/Sprite")   // fragile
```

Basta rinominare o spostare un nodo nell'editor e il percorso salta a runtime,
senza che il compilatore dica nulla. Due alternative migliori, in ordine di
preferenza:

```csharp
[Export] private Sprite2D _sprite = null!;   // assegnato nell'editor
private Sprite2D _sprite2 => GetNode<Sprite2D>("%Sprite"); // nome univoco
```

`[Export]` espone il campo nell'Inspector: il collegamento è dichiarato una
volta e sopravvive agli spostamenti. Il prefisso `%` indica un *unique name*,
impostato nell'editor, valido ovunque nella scena a prescindere dalla
posizione.

### I segnali sono l'accoppiamento debole dell'engine

Un **segnale** è il meccanismo di notifica di Godot: l'equivalente concettuale
di un evento .NET, ma dichiarato in modo che anche l'editor lo veda. Serve a
far comunicare un nodo con altri senza che li conosca — la base per tenere
separati i sistemi di AGGGA.

Dichiarazione: il nome del delegate **deve** terminare con `EventHandler`, e
il segnale si userà senza quel suffisso.

```csharp
[Signal] public delegate void ItemCollectedEventHandler(string itemId);

// Emissione: SignalName evita le stringhe a mano libera.
EmitSignal(SignalName.ItemCollected, itemId);

// Sottoscrizione: sintassi eventi C# standard.
_hotspot.ItemCollected += OnItemCollected;
```

Anche i segnali predefiniti funzionano così:

```csharp
_button.Pressed += OnButtonPressed;
```

### `delta` è `double`, i vettori sono `float`

```csharp
public override void _Process(double delta)
{
    Position += _velocity * (float)delta;   // il cast serve
}
```

Piccolo attrito ricorrente, ma è la causa di errori di compilazione che
sembrano assurdi la prima volta.

### Le collezioni .NET non attraversano il confine

Per i membri esportati o passati all'engine servono i tipi di Godot:

```csharp
using Godot.Collections;

[Export] public Array<NodePath> Waypoints { get; set; } = new();
```

`List<T>` e `Dictionary<K,V>` di .NET vanno benissimo **all'interno** della
logica C#: non usarli solo dove l'engine deve leggerli o serializzarli.

### `_Process` viene chiamato ogni frame

Sessanta volte al secondo o più. Qualunque allocazione, `GetNode`, o ricerca
per stringa qui dentro si paga sessanta volte al secondo. Risolvi i
riferimenti in `_Ready()` e conservali in campi.

Per un punta-e-clicca la maggior parte della logica è a eventi, non a frame:
se ti trovi a scrivere molto codice in `_Process`, probabilmente andava in un
segnale.

## Convenzioni del progetto

**Lingua**: nomi ed commenti in inglese, come stabilito in `CLAUDE.md`. Le
conversazioni restano in italiano.

**Nomenclatura**: `PascalCase` per classi, metodi e proprietà; `_camelCase`
per i campi privati. Gli override dell'engine mantengono l'underscore iniziale
(`_Ready`, `_Process`, `_Input`): è la convenzione di Godot e segnala a colpo
d'occhio che li chiama l'engine, non il tuo codice.

**Struttura**: `scripts/` rispecchia `scenes/`. Uno script per nodo che ha
comportamento; i nodi puramente strutturali non ne hanno bisogno.

**Namespace**: `Aggga`, con eventuali sottospazi per sistema
(`Aggga.Dialogue`, `Aggga.Inventory`) quando i sistemi esisteranno.

## Pattern che serviranno in AGGGA

### Stato globale: autoload

Un **autoload** (o singleton) è una scena o uno script che Godot carica
all'avvio e tiene vivo per tutta la partita, fuori dalle scene ordinarie. È il
posto giusto per lo stato che sopravvive al cambio di stanza: flag di gioco,
inventario, personaggio attivo.

Si registra in *Project Settings → Autoload* e si raggiunge così:

```csharp
var state = GetNode<GameState>("/root/GameState");
```

Da valutare quando servirà: esporre un accessore statico tipizzato per
evitare il percorso stringa sparso ovunque. È una decisione architetturale, e
`CLAUDE.md` chiede di proporla con alternative prima di implementarla.

### Istanziare una scena da codice

```csharp
[Export] private PackedScene _itemScene = null!;

var item = _itemScene.Instantiate<PickupItem>();
AddChild(item);
```

Una `PackedScene` è la scena non ancora istanziata — il progetto, non
l'edificio. Finché non fai `AddChild`, il nodo esiste ma è fuori dall'albero:
non viene disegnato e `_Ready()` non è ancora scattato.

### Input: pensare da subito al touch

AGGGA ha come target anche mobile, e un punta-e-clicca è fatto di click.

```csharp
public override void _UnhandledInput(InputEvent @event)
{
    if (@event is InputEventMouseButton { Pressed: true } mb) { }
}
```

Usa `_UnhandledInput` e non `_Input` per l'input di gioco: così l'interfaccia
(verb-coin, inventario) intercetta ciò che le compete prima che arrivi alla
stanza, ed eviti che un click su un bottone finisca anche sullo sfondo.

Sul touch, Godot può emulare il mouse (*Project Settings → Input Devices →
Pointing → Emulate Mouse From Touch*). Funziona per il click semplice, ma non
copre l'assenza di hover — su mobile non esiste il passaggio del puntatore.
È un vincolo di design da tenere presente per la verb-coin, non un dettaglio
implementativo: va deciso quando si progetterà quel sistema.

### Attendere senza bloccare

```csharp
await ToSignal(GetTree().CreateTimer(1.5), SceneTreeTimer.SignalName.Timeout);
```

Evita `async void` e `Thread.Sleep`: il primo nasconde le eccezioni, il
secondo blocca il frame e congela il gioco.

## Prima di dire "fatto"

Il codice C# va **ricompilato** perché Godot lo veda: l'editor non ricarica gli
script al volo come farebbe con GDScript. Se una modifica sembra non avere
effetto, il primo sospetto è una build non eseguita.

In questo ambiente remoto `dotnet` e `godot` non sono installati: il codice non
può essere compilato né eseguito qui. Quando proponi modifiche, dillo
esplicitamente invece di lasciar intendere che siano state verificate — la
prova sta nell'aprire il progetto in Godot.
