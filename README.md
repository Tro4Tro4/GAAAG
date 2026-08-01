# AGGGA

Avventura grafica punta-e-clicca in stile anni '90 (LucasArts), con più
personaggi giocabili. Motore **Godot 4.x**, linguaggio **C# (.NET 8)**.

Le decisioni di design/architettura e le convenzioni di progetto sono
documentate in [`CLAUDE.md`](./CLAUDE.md).

## Requisiti
- [Godot 4.3+ — versione **.NET / Mono**](https://godotengine.org/download)
- [.NET SDK 8.0+](https://dotnet.microsoft.com/download)

## Come avviare
1. Apri Godot (versione .NET) e importa la cartella del progetto
   (seleziona il file `project.godot`).
2. Godot genera `.godot/` e i file `.import` al primo import.
3. Premi **Play** (F5): parte `scenes/rooms/TestRoom.tscn`. Clicca sul
   pavimento per far camminare il personaggio; la cassa al centro viene
   aggirata perché è un buco nella navmesh della stanza.

Se qualcosa non parte, `scenes/Main.tscn` è rimasta come smoke test minimo
dello scaffold: aprila ed eseguila (F6) per isolare un problema di pipeline
C# da un problema della stanza.

Per vedere il percorso calcolato e la zona calpestabile mentre giochi:
**Debug → Visible Navigation**.

## Struttura
```
project.godot        Configurazione progetto Godot
Aggga.csproj/.sln    Progetto e solution C#
icon.svg             Icona placeholder
scenes/rooms/        Stanze di gioco (TestRoom = scena di avvio)
scenes/characters/   Personaggi (Player)
scripts/             Codice C#, rispecchia l'albero di scenes/
assets/              Sprite, sfondi, audio, font
```
