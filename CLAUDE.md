# AGGGA — Avventura Grafica Punta-e-Clicca

## Cos'è
Avventura grafica punta-e-clicca stile anni '90 (LucasArts), con cambio di
personaggio controllabile stile *Day of the Tentacle* / *Maniac Mansion*.
Storia originale, ambientazione fantascientifica assurda/comica ispirata
nello **spirito** ( nei contenuti) a *Guida Galattica per Autostoppisti*.

## Stack tecnico
- **Engine**: Godot 4.x
- **Linguaggio**: C# (Mono)
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
1. Sistema base: movimento, stanze, hotspot cliccabili, verb-coin UI
2. Sistema personaggi multipli: switch, stato indipendente per personaggio
3. Sistema inventario
4. Sistema dialoghi con condizioni
5. Prototipo verticale: 1 stanza, 2 personaggi, 1 puzzle cooperativo completo
6. Solo dopo il prototipo: scrittura della storia completa, capitoli,
   altre stanze, durata finale del gioco (ancora da stabilire)

## Struttura del progetto
```
project.godot        Configurazione progetto Godot (renderer, display, dotnet)
Aggga.csproj/.sln    Progetto e solution C# (.NET 8, RootNamespace = Aggga)
icon.svg             Icona placeholder
scenes/              Scene Godot (.tscn) — es. Main.tscn (scena di avvio)
scripts/             Codice C# — es. Main.cs
assets/              sprites/ backgrounds/ audio/ fonts/
```

## Decisioni prese (e perché)
- **Godot + C#** invece di Ren'Py/AGS/Visionaire: lo sviluppatore ha
  esperienza pregressa in C# (.NET/ASP.NET Core), riuso di competenze;
  Godot è gratuito, esporta su tutte le piattaforme target, ottimo supporto
  2D nativo (non è un motore 3D adattato)
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
  - **.NET 8 / `net8.0`**: runtime LTS supportato da Godot 4.3.
  - **Nome assembly/namespace `Aggga`**: provvisorio (il nome del progetto è
    tra le decisioni aperte); rinominabile in fretta.
  - Nota: nell'ambiente di sviluppo remoto non erano installati `dotnet` né
    `godot`, quindi lo scaffold non è stato build-testato lì. Va aperto in
    Godot (versione .NET) per la prima verifica.

## Decisioni ancora aperte
- Durata finale del gioco (valutare dopo il prototipo)
- Inventario condiviso vs per personaggio
- Lista definitiva dei verbi nel verb-coin
- Nome del progetto, dei personaggi, ambientazione specifica

## Comportamento di Claude Code su questo progetto
- **Lingua conversazione**: italiano. **Lingua codice**: inglese per nomi di
  classi/metodi/variabili e commenti (convenzione standard, resta comunque
  leggibile e coerente col resto dell'ecosistema Godot/C#)
- Questo è il primo progetto di game dev dello sviluppatore (esperto in
  C#/.NET ma non in game engine): spiegare i concetti specifici di Godot
  (signal, scene tree, node, autoload, ecc.) la prima volta che vengono
  introdotti, senza darli per scontati
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
