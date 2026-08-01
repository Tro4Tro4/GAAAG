# AGGGA

Avventura grafica punta-e-clicca in stile anni '90 (LucasArts), con più
personaggi giocabili. Motore **Godot 4.x**, linguaggio **GDScript**.

Le decisioni di design/architettura e le convenzioni di progetto sono
documentate in [`CLAUDE.md`](./CLAUDE.md).

## Requisiti
Basta Godot 4.3+, **build standard** (non la versione .NET: il progetto non
usa C#).

- **Su Android**: app *Godot Engine* dal Play Store — è l'ambiente di sviluppo
  principale di questo progetto.
- **Su desktop**: [godotengine.org/download](https://godotengine.org/download).
  Non richiede installazione, è un archivio da estrarre.

## Come avviare
1. Apri Godot e importa il progetto selezionando il file `project.godot`.
2. Godot genera `.godot/` e i file `.import` al primo import.
3. Premi **Play** (F5): parte `scenes/rooms/TestRoom.tscn`.

Clicca sul pavimento per far camminare il personaggio. La cassa al centro
viene aggirata: è un buco nella navmesh della stanza, non un controllo scritto
a mano.

Per vedere la zona calpestabile e il percorso calcolato mentre giochi:
**Debug → Visible Navigation**.

## Struttura
```
project.godot        Configurazione progetto Godot
icon.svg             Icona placeholder
scenes/rooms/        Stanze di gioco (TestRoom = scena di avvio)
scenes/characters/   Personaggi (Player)
scripts/             Codice GDScript, rispecchia l'albero di scenes/
assets/              Sprite, sfondi, audio, font
```

Convenzione di nomi: scene `.tscn` in `PascalCase`, script `.gd` in
`snake_case` — è lo standard dell'ecosistema Godot.
