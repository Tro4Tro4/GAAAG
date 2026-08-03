---
name: retro-adventure-audio
description: Generate a complete audio library for a 90s-style point-and-click graphic adventure — interaction SFX, footsteps, looping ambiences, music themes and stingers, UI sounds, and LucasArts-style mock-gibberish voice — as ready-to-ship WAV/OGG files with a manifest. Use this skill whenever the user asks for game sounds, sound effects, SFX, ambiences, retro or chiptune-adjacent game audio, UI clicks, placeholder voice, or a soundscape for a game, adventure, visual novel or pixel-art project, even if they don't say "90s" or "adventure". Also use it when they ask to synthesise audio from scratch in Python, or to expand or restyle an existing sound library made this way.
---

# Retro adventure audio

Everything is synthesised from scratch with numpy/scipy — no sample libraries, no
network, fully reproducible from a seed. The deliverable is a folder of WAV files (plus
OGG for loops), named consistently and described in a manifest the user can hand
straight to a developer.

The aesthetic target is **modern lo-fi with a retro flavour**: full-band synthesis,
then deliberately degraded — 22.05 kHz, bandlimited around 8 kHz, ~11-bit quantisation,
a whisper of tape drift and noise floor. It should sound like a beloved 1994 CD-ROM
remembered fondly, not like a broken 1994 CD-ROM.

## Workflow

**1. Establish the brief before generating anything.**
Ask only what you can't infer, in one round: the setting and mood (pirate port, gothic
manor, sci-fi station, noir city...), which categories are wanted, and roughly how many
assets. If the user is vague or says "surprise me", pick a setting, state your choice in
one line, and proceed — a concrete library invites better feedback than more questions.

**2. Plan the asset list explicitly.** Write out the filenames before writing code, so
the library has deliberate coverage instead of whatever the code happened to produce.
A representative small scene is ~20-30 assets; a full scene 40-60. Cover:
interaction SFX for the objects the player can touch, footsteps for the surfaces present,
2-4 ambience loops, one music bed plus 3-4 stingers, a UI set, and a couple of voice lines.

**3. Read `references/recipes.md`** for the categories in the brief. It has working
recipes for doors, thuds, metal, pickups, locks, liquids, magic, fire, glass, paper,
footsteps on five surfaces, six ambience types, music voices and stingers, UI, and mock
voice — plus a troubleshooting section. Read the sections you need, not the whole file.

**4. Write one generator script** (e.g. `generate_audio.py`) that imports
`scripts/retroaudio.py`, builds every asset, and registers them with `ra.Batch`. One
script means the user can tweak a parameter and re-render the whole library. Start it
with `ra.seed(<n>)` so the output is reproducible.

```python
import sys; sys.path.insert(0, ".claude/skills/retro-adventure-audio/scripts")
import retroaudio as ra

ra.seed(1994)
b = ra.Batch("assets/audio")   # in AGGGA i deliverable stanno nel progetto

door = ra.reverb(ra.mix(creak, latch, gains=[0.8, 0.5]), room=0.4, mix=0.22)
b.add("sfx", "door_wood_open", door, note="rising creak + latch click")

b.add("amb", "tavern", tavern, crossfade=1.5, note="crowd mumble, clinks, room tone")
b.add("ui", "click", click)

b.finish()   # writes the files, prints QA, generates manifest.md + manifest.json
```

`Batch.add` applies the lo-fi finishing chain, the right level target and loop
crossfade for the category, writes the file, prints a QA line and collects the manifest
row. Don't hand-roll that per file.

**5. Run the script, read the QA output, fix what it flags.** In AGGGA the finished
files go straight into `assets/audio/` and into git: da lì arrivano sul telefono con un
`git pull`, e non c'è nessuna cartella di output né `present_files`. Committa anche il
generatore, in `tools/`, perché il punto di questo modo di lavorare è che la libreria si
può rigenerare cambiando un parametro. Il `manifest.md` che `Batch.finish()` scrive va
accanto ai file. Descrivi la libreria in poche righe: la tabella è già nel manifest.

## Vincoli di AGGGA (leggere prima di generare)

Questa skill è generica; il progetto ha già un impianto audio e delle decisioni
registrate in `CLAUDE.md`. Queste sono quelle che la restringono.

- **`pip install numpy scipy`** prima di qualunque cosa: non sono installati
  nell'ambiente remoto, come Pillow e `gdtoolkit`.
- **Ci sono due riproduttori e due bus, non di più.** `AudioDirector` ha un posto
  per come suona la stanza e un posto per quello che è appena successo, e i bus
  sono `Music` e `Sound` in `default_bus_layout.tres`. Ne segue una cosa
  importante: **un'ambienza e una musica non possono suonare insieme oggi.** Le
  categorie `amb` e `mus` della skill competono per lo stesso riproduttore. Se
  servono entrambe, va rivista la decisione "due riproduttori e basta" — con una
  proposta e `registra-decisione`, non aggiungendo un nodo di nascosto.
- **Il loop non si dichiara, si fa a mano.** Il progetto riavvia la traccia sul
  segnale `finished` invece di affidarsi all'impostazione di import, perché
  quella dipende da un `.import` che scrive l'editor e da qui non è
  verificabile. Il crossfade cucito dentro il file da `ra.finish_loop()` resta
  quindi la cosa che rende la giuntura inudibile, ed è indispensabile. L'OGG non
  serve: il gioco carica i `.wav`.
- **I due agganci sono dati, non codice.** `Room.music` è la traccia di una
  stanza, `Hotspot.sound` è il rumore che fa una cosa quando la tocchi.
  Aggiungere un suono al gioco è riempire un campo in un `.tscn`.
- **I nomi già in uso non seguono la convenzione della skill**: in
  `assets/audio/` ci sono `ui_click.wav`, `thud.wav`, `chime.wav`, `hum_low.wav`,
  `hum_high.wav`, e i loro percorsi sono scritti dentro le scene. Adottare
  `<categoria>_<nome>.wav` è giusto, ma **rinominare vuol dire modificare le
  scene nello stesso commit**, o il gioco resta muto senza dire perché.
- **`vox` non ha un posto nel gioco.** La voce del gioco è la `Caption`, e non
  c'è nessun sistema che sincronizzi un suono con una battuta. La voce finta
  stile LucasArts è una bella idea ma è una decisione di design da prendere,
  non un asset da aggiungere.
- **I cinque suoni attuali sono segnaposto** generati da uno script molto più
  rozzo di questa libreria. Sostituirli è il primo lavoro utile che questa skill
  può fare, ed è a costo zero perché i nomi dei file possono restare quelli.

## The spec

| | Sample rate | Channels | Peak target | Length | Format |
|---|---|---|---|---|---|
| Interaction SFX | 22050 | mono | -3 dB | 80-400 ms* | WAV |
| Footsteps | 22050 | mono | -3 dB | 60-200 ms | WAV |
| Ambience loops | 22050 | stereo | -3 dB (RMS ~-20) | 8-20 s | WAV + OGG |
| Music beds | 22050 | stereo | -4 dB | whole bars | WAV + OGG |
| Stingers | 22050 | mono | -3 dB | 1-2.5 s | WAV |
| UI | 22050 | mono | -6 dB | 20-120 ms | WAV |
| Mock voice | 22050 | mono | -6 dB | < 1.5 s | WAV |

Filenames are `<category>_<name>.wav`, lowercase snake_case, category from
`sfx | step | amb | mus | sting | ui | vox`. Name by function, not by how it was made:
`sfx_door_wood_open`, not `sfx_saw_resonator_thing`. Variants get a numeric suffix:
`step_stone_01` … `step_stone_04`.

\* Doors, mechanisms, pouring and other *processes* legitimately run to ~2 s; discrete
*impacts* do not. Note that `ra.reverb` appends its tail to the array, so the finished
length is longer than the dry source — check the QA output rather than the source length.

Mono for anything the engine will position in space — the engine pans it, and a
pre-panned SFX fights that. Stereo only for beds the player hears "everywhere".

## Two rules that decide whether this sounds professional

**Layer three things.** Transient + body + tail. A single oscillator through an envelope
always sounds like a test tone, no matter how clever the envelope is. The transient
carries the material, the body carries the identity, the tail carries the room.

**Variants for anything repeated.** Footsteps, clicks, coins, typing blips, sword hits:
3-5 variants with ±8% pitch, ±15% level and a fresh `ra.seed()` per variant. A single
footstep file is the most audible sign of amateur game audio there is.

## The house sound

`ra.lofi_finish()` is the last step on every asset and it's what makes the library
cohere. Vary it a little per family rather than using one preset everywhere — a uniform
chain flattens the whole library into one texture:

- Ambience, music: `cutoff=7000-8000`, `bits=11`, `drive=1.3`
- Interaction SFX: `cutoff=8000-9000`, `bits=11-12`, `drive=1.5-1.8`
- UI, voice: `cutoff=7000`, `bits=12`, `wobble_depth=0` — drift on a 30 ms click reads
  as a glitch, not as character
- Deliberately old/degraded diegetic sources (radio, phonograph, PA): `cutoff=3500`,
  `bits=8`, `downsample=2`, `drive=2.5`

For loops use `ra.finish_loop()`, never `loopify(lofi_finish(x))` — the docstring
explains why the order matters.

## QA gate

`ra.report()` (called for you by `Batch`) prints length, true peak, RMS and, for loops,
a seam figure. Before delivering, check:

- No loop flagged `CLICK` — raise the crossfade, or lengthen the source (it must be at
  least twice the crossfade).
- Levels land near the category target; ambiences should sit clearly below SFX in RMS,
  otherwise the bed will mask everything in-game.
- Lengths are in the ranges above. A 3-second door is a bug, not a choice.
- Repeated sounds actually have distinct variants — if two variants report identical
  length and peak, the seed didn't change.

## Reference

- `references/recipes.md` — the recipe book, organised by category, with troubleshooting.
- `scripts/retroaudio.py` — the DSP library. Run it directly (`python retroaudio.py`) for
  a self-test. Read its docstrings before inventing a helper: oscillators, FM, envelopes,
  time-varying filters, resonators, bitcrush, reverb/delay/chorus/tremolo, tape wobble,
  crackle, panning/widening, seamless looping, note names and a small sequencer, a formant
  mumble voice, WAV/OGG writing, and `Batch`.

Frequency, level and time arguments accept a scalar, a `(start, end)` tuple for an
exponential glide, or an array — so sweeps and pitch envelopes come for free:
`ra.sine((680, 1900), 0.09)` is a water drop.
