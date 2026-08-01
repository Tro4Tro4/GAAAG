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
3. Premi **Play** (F5): parte la scena `scenes/Main.tscn`, che al momento
   mostra solo un placeholder e conferma che la pipeline C# funziona.

## Struttura
```
project.godot        Configurazione progetto Godot
Aggga.csproj/.sln    Progetto e solution C#
icon.svg             Icona placeholder
scenes/              Scene Godot (.tscn)
scripts/             Codice C#
assets/              Sprite, sfondi, audio, font
```
