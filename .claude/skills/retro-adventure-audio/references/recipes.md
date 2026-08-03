# Recipe book

Copy-paste starting points, not gospel. Every recipe assumes `import retroaudio as ra`
and ends with `ra.lofi_finish(...)` applied by the caller (see SKILL.md).

Read only the section you need.

- [1. Principles that matter more than the recipes](#1-principles)
- [2. Object & interaction SFX](#2-object--interaction-sfx)
- [3. Footsteps](#3-footsteps)
- [4. Ambience loops](#4-ambience-loops)
- [5. Music: themes, beds, stingers](#5-music-themes-beds-stingers)
- [6. UI](#6-ui)
- [7. Mock voice](#7-mock-voice)
- [8. Troubleshooting](#8-troubleshooting)

---

## 1. Principles

**Layer three things.** Nearly every convincing SFX is *transient + body + tail*:
a click/thud for the attack, a pitched or noise body for the material, a decay or
reverb tail for the space. One layer alone always sounds like a test tone.

**Material lives in the filter, not the oscillator.** Wood = resonators at 180-400 Hz
with fast decay. Metal = inharmonic partials or FM with a high index and long tail.
Stone = filtered brown noise, almost no ring. Cloth/paper = bandpassed white noise,
20-80 ms. Glass = FM ratio around 3.5-7 plus a bright noise burst.

**Reach for pitch envelopes.** A falling pitch reads as "heavy / landing / closing";
a rising one as "success / opening / powering up". `ra.fm(carrier=(800, 120), ...)`
does more storytelling than any amount of EQ.

**Randomise variants, never duplicate.** Any sound that fires more than a few times per
scene (footsteps, clicks, coins, typing) needs 3-5 variants with ±8% pitch, ±15%
level and a fresh noise seed. Repetition is the loudest tell of cheap audio.

**Keep it short.** 90s adventures were tight: interaction SFX 80-400 ms, UI 40-120 ms,
stingers 1-2.5 s. Long sounds fight the dialogue.

---

## 2. Object & interaction SFX

### Wooden door, opening (creak)
```python
creak_pitch = (140, 310)                       # rising = opening; reverse for closing
body = ra.saw(creak_pitch, 1.1) * 0.5
body = ra.resonator(body, 240, q=14) + ra.resonator(body, 430, q=18) * 0.4
body *= ra.tremolo(ra.adsr(1.1, 0.12, 0.2, 0.7, 0.35), rate=11, depth=0.55)
latch = ra.offset(ra.noise(0.06, "metal") * ra.decay(0.06, 0.012), 1.0)
door = ra.reverb(ra.mix(body, latch, gains=[0.8, 0.5]), room=0.4, mix=0.22)
```

### Heavy thud / body fall / stone slab
```python
thud = ra.mix(
    ra.sine((110, 42), 0.45) * ra.decay(0.45, 0.10),          # sub
    ra.lowpass(ra.noise(0.25, "brown"), (1800, 300)) * ra.decay(0.25, 0.05),
    gains=[1.0, 0.6],
)
```

### Metal clang / key ring / armour
```python
clang = ra.mix(*[
    ra.fm(f, ratio=r, index=(9, 1.5), dur=0.9) * ra.decay(0.9, d)
    for f, r, d in [(520, 3.7, 0.30), (770, 5.1, 0.22), (1240, 2.3, 0.14)]
])
clang = ra.reverb(clang, room=0.7, mix=0.3)
```

### Pick-up / inventory add (the sound the player hears most — make it pleasant)
```python
pick = ra.mix(
    ra.seq([("e5", 0.5), ("b5", 0.5)], bpm=210),               # small rising 5th
    ra.noise(0.05, "white") * ra.decay(0.05, 0.008) * 0.25,
)
```

### Lock, latch, mechanism (three-stage: insert, turn, click)
```python
lock = ra.mix(
    ra.bandpass(ra.noise(0.14, "white"), 900, 5000) * ra.decay(0.14, 0.03) * 0.5,
    ra.offset(ra.bandpass(ra.noise(0.10, "white"), 1200, 6000) * ra.decay(0.10, 0.02), 0.20),
    ra.offset(ra.fm(1500, 2.0, 4, 0.09) * ra.decay(0.09, 0.012), 0.42),
)
```

### Liquid: pour, potion, drip
```python
# drip: a fast rising pitch on a sine is the whole trick
drip = ra.sine((680, 1900), 0.09) * ra.decay(0.09, 0.02)
stream = ra.bandpass(ra.noise(1.4, "white"), 700, 4500) * ra.adsr(1.4, .15, .2, .8, .3) * 0.4
bubbles = [ra.offset(ra.sine((500 + i * 90, 1500), 0.06) * ra.decay(0.06, 0.015) * 0.3,
                     0.1 + i * 0.11) for i in range(9)]
pour = ra.mix(stream, *bubbles)     # ra.mix pads layers of different length
```

### Magic / puzzle solved shimmer
```python
shimmer = ra.mix(*[
    ra.offset(ra.fm(ra.note(n) * 4, 1.01, (5, 0.5), 1.2) * ra.decay(1.2, 0.35), i * 0.06)
    for i, n in enumerate(["c5", "e5", "g5", "b5", "d6"])
])
shimmer = ra.chorus(ra.reverb(shimmer, 0.85, 0.4), rate=0.5, depth=0.006)
```

### Fire, torch (loopable)
```python
fire = ra.lowpass(ra.noise(8.0, "brown"), 1100) * 0.5
fire *= 0.7 + 0.3 * ra.sine(0.7, 8.0)                          # slow breathing
fire += ra.crackle(8.0, density=40, level=0.09)                # spits
# finish with: b.add("amb", "fire_torch", fire, crossfade=1.0)
```

### Glass break
```python
glass = ra.mix(
    ra.highpass(ra.noise(0.35, "white"), 2500) * ra.decay(0.35, 0.05),
    *[ra.offset(ra.fm(f, 4.5, 8, 0.4) * ra.decay(0.4, 0.06), ra.rng.uniform(0, 0.12))
      for f in (1800, 2400, 3100, 4200)],
)
```

### Paper, scroll, cloth
```python
paper = ra.bandpass(ra.noise(0.30, "white"), 1800, 8000)
paper *= ra.adsr(0.30, 0.02, 0.06, 0.5, 0.15) * (0.5 + 0.5 * ra.sine(24, 0.30))
```

---

## 3. Footsteps

One function, four surfaces, always 4+ variants. This pattern generalises to any
"many variants" family.

```python
SURFACES = {
    "stone":  dict(band=(180, 2600), tau=0.045, thump=95,  ring=None),
    "wood":   dict(band=(150, 2200), tau=0.070, thump=110, ring=230),
    "gravel": dict(band=(700, 7000), tau=0.090, thump=None, ring=None),
    "grass":  dict(band=(900, 5000), tau=0.055, thump=None, ring=None),
    "metal":  dict(band=(300, 6000), tau=0.120, thump=130, ring=740),
}

def step(surface, variant):
    p = SURFACES[surface]
    ra.seed(4000 + variant)                        # different noise per variant
    jitter = 1.0 + (variant - 2) * 0.05            # +/- pitch spread
    dur = p["tau"] * 4
    s = ra.bandpass(ra.noise(dur, "white"), p["band"][0] * jitter, p["band"][1])
    s *= ra.decay(dur, p["tau"])
    if p["thump"]:
        s = ra.mix(s, ra.sine((p["thump"] * jitter, p["thump"] * 0.6), 0.12)
                   * ra.decay(0.12, 0.03), gains=[1.0, 0.5])
    if p["ring"]:
        s = ra.mix(s, ra.resonator(s, p["ring"] * jitter, q=16) * 0.4)
    if surface == "gravel":                        # scatter of small grains
        s = ra.mix(s, *[ra.offset(ra.highpass(ra.noise(0.02, "white"), 3000)
                                  * ra.decay(0.02, 0.004) * 0.3,
                                  ra.rng.uniform(0.01, 0.09)) for _ in range(6)])
    return s * (0.85 + 0.15 * (variant % 3))       # level variation
```

---

## 4. Ambience loops

Build 8-20 s of raw material and hand it to `b.add("amb", ...)` — `Batch` applies the
lo-fi chain and the crossfade in the correct order. Never call `loopify` yourself before
finishing: `ra.finish_loop` exists precisely because the order matters.

Layer recipe: **bed** (filtered noise) + **movement** (slow LFOs / sweeps) +
**events** (sparse one-shots panned wide) + **glue** (crackle, faint hum).

### Wind, exterior
```python
bed = ra.lowpass(ra.noise(14.0, "brown"), (300, 700)) * 0.6
gust = ra.resonator(ra.noise(14.0, "pink"), 520, q=6) * (0.3 + 0.7 * abs(ra.sine(0.09, 14.0)))
amb = ra.widen(ra.mix(bed, gust, ra.crackle(14.0, 6, 0.02)), 0.02)   # Batch loops it
```

### Tavern / market (crowd from mumbles is the trick)
```python
crowd = ra.mix(*[
    ra.pan(ra.offset(ra.lowpass(ra.mumble("ba-da-bo-de", pitch=ra.rng.uniform(90, 190)), 1400)
                     * 0.18, ra.rng.uniform(0, 15.0)), ra.rng.uniform(-0.9, 0.9))
    for _ in range(14)
])
room = ra.widen(ra.lowpass(ra.noise(16.0, "pink"), 900) * 0.25, 0.03)
clinks = ra.mix(*[ra.pan(ra.offset(ra.fm(2100, 3.2, 5, 0.25) * ra.decay(0.25, 0.05) * 0.15,
                                   ra.rng.uniform(0, 15.0)), ra.rng.uniform(-0.7, 0.7))
                  for _ in range(7)])
amb = ra.reverb(ra.mix(crowd, room, clinks), 0.8, 0.3)
```

### Rain (+ optional thunder)
```python
rain = ra.bandpass(ra.noise(15.0, "white"), 800, 9000) * 0.35
rain += ra.lowpass(ra.noise(15.0, "brown"), 400) * 0.25            # distant rumble
drops = ra.mix(*[ra.pan(ra.offset(ra.sine((900, 2200), 0.05) * ra.decay(0.05, 0.012) * 0.2,
                                  ra.rng.uniform(0, 14.0)), ra.rng.uniform(-1, 1))
                 for _ in range(30)])
amb = ra.mix(ra.widen(rain, 0.025), drops)      # widen BEFORE mixing panned layers
```

### Cave / dungeon (sparse, wet, mostly silence)
```python
bed = ra.lowpass(ra.noise(18.0, "brown"), 260) * 0.4
drips = ra.mix(*[ra.pan(ra.offset(ra.reverb(ra.sine((700, 2000), 0.08)
                                            * ra.decay(0.08, 0.02), 0.95, 0.55) * 0.5,
                                  ra.rng.uniform(0, 16.0)), ra.rng.uniform(-0.8, 0.8))
                 for _ in range(6)])
amb = ra.mix(ra.widen(bed, 0.04), drips, ra.hum(18.0, 42, 0.004))
```

### Machinery / ship / airlock
```python
mach = ra.mix(
    ra.pulse((58, 58), 12.0, duty=0.3) * 0.18,                    # motor
    ra.lowpass(ra.noise(12.0, "brown"), 500) * 0.3,               # air
    ra.resonator(ra.noise(12.0, "pink"), 1350, q=20) * 0.12,      # whine
)
mach = ra.tremolo(mach, rate=3.1, depth=0.25)
amb = ra.widen(mach, 0.015)
```

---

## 5. Music: themes, beds, stingers

Two or three voices maximum. Everything is a variation on: **pad/bass** for harmony,
**lead** for melody, **arp** for motion. Use `ra.seq` with a custom `voice=`.

### Voices
```python
def pad(f, d):
    v = ra.saw(f, d) * 0.4 + ra.saw(f * 1.005, d) * 0.4 + ra.sine(f / 2, d) * 0.3
    return ra.lowpass(v, 1500, sr=ra.SR) * ra.adsr(d, 0.25, 0.3, 0.7, 0.4)

def lead(f, d):
    v = ra.pulse(f * (1 + 0.006 * ra.sine(5.2, d)), d, duty=0.30)
    return ra.lowpass(v, 3400) * ra.adsr(d, 0.01, 0.06, 0.65, min(0.2, d * .4))

def bass(f, d):
    return ra.lowpass(ra.pulse(f, d, 0.5) * 0.7 + ra.sine(f / 2, d) * 0.5, 900) \
           * ra.adsr(d, 0.005, 0.08, 0.55, 0.08)

def bell(f, d):
    return ra.fm(f, 3.01, (7, 0.4), d) * ra.decay(d, d * 0.28)
```

### Loopable theme bed (aim for a whole number of bars so it loops musically)
```python
BPM = 88
melody = ra.seq([("e4",1),("g4",1),("a4",2),(None,.5),("g4",.5),("e4",1),("d4",2)],
                bpm=BPM, voice=lead)
bassline = ra.seq([("a2",2),("a2",2),("f2",2),("g2",2)], bpm=BPM, voice=bass)
pads = ra.seq([("a3",4),("f3",4)], bpm=BPM, voice=pad)
theme = ra.mix(melody, bassline, pads, gains=[0.55, 0.45, 0.30])
theme = ra.widen(ra.reverb(theme, 0.6, 0.25), 0.014)
```

Loop length in seconds = `bars * 4 * 60 / BPM`. Trim the bed to exactly that before
handing it to `Batch`, or the loop will drift out of time on every repeat.

### Stingers (short, unmistakable, mixed 3 dB above the music bed)
```python
success = ra.reverb(ra.seq([("c5",.5),("e5",.5),("g5",.5),("c6",1.5)], bpm=150, voice=bell), 0.7, .35)
failure = ra.reverb(ra.seq([("g3",.75),("f#3",.75),("c3",2)], bpm=110, voice=pad), 0.6, .3)
mystery = ra.chorus(ra.mix(ra.chord(["d4","f4","a4","c5"], 2.5, voice=pad),
                           ra.seq([(None,1),("b4",1.5)], bpm=90, voice=bell)), depth=0.007)
danger  = ra.tremolo(ra.mix(ra.seq([("c3",4)], bpm=90, voice=bass),
                            ra.seq([("c#4",4)], bpm=90, voice=pad)), rate=7, depth=0.4)
```

---

## 6. UI

Keep UI dry (little or no reverb), short, and quieter than SFX — around -6 dBFS peak.
Disable drift: `ra.lofi_finish(x, wobble_depth=0)`.

```python
click   = ra.mix(ra.noise(0.03, "white") * ra.decay(0.03, 0.004),
                 ra.sine(1800, 0.03) * ra.decay(0.03, 0.006), gains=[0.5, 0.6])
hover   = ra.sine((1200, 1500), 0.05) * ra.decay(0.05, 0.015) * 0.5
confirm = ra.seq([("c5", .5), ("g5", .5)], bpm=260)
cancel  = ra.seq([("g4", .5), ("c4", .5)], bpm=260)
error   = ra.saturate(ra.pulse(150, 0.18, 0.4) * ra.decay(0.18, 0.06), 3.0)
open_m  = ra.bandpass(ra.noise(0.18, "white"), 600, 4000) * ra.ramp(0.18, 0.2, 1.0) * ra.decay(0.18, 0.09)
close_m = open_m[::-1].copy()
blip    = ra.pulse(920, 0.022, 0.25) * ra.decay(0.022, 0.006) * 0.4   # per-character text
```

A text-crawl blip is played dozens of times per line: give it 4 variants at
±5% pitch or it becomes torture.

---

## 7. Mock voice

`ra.mumble()` is a formant synth: syllables are dash-separated, a trailing `?` makes
the contour rise. Match syllable count to the real line's rhythm, keep lines under
1.5 s, and give each character a fixed `pitch` and `speed` so they stay recognisable.

```python
CAST = {
    "hero":     dict(pitch=135, speed=1.0),
    "sidekick": dict(pitch=205, speed=1.25),
    "villain":  dict(pitch=88,  speed=0.8),
    "shopkeep": dict(pitch=160, speed=1.1),
}

def line(character, syllables, mood="neutral"):
    p = dict(CAST[character])
    if mood == "question":  syllables = syllables.rstrip("?") + "?"
    if mood == "angry":     p["pitch"] *= 1.12; p["speed"] *= 1.2
    if mood == "sad":       p["pitch"] *= 0.9;  p["speed"] *= 0.8
    v = ra.mumble(syllables, **p)
    return ra.reverb(ra.lowpass(v, 3400), room=0.3, mix=0.12)   # a little room, never wet
```

Deliver mock voice as `vox_<character>_<lineid>.wav` and note in the manifest that it
is placeholder gibberish for timing, not final dialogue.

---

## 8. Troubleshooting

**Sounds thin / like a test tone.** Missing a layer. Add a transient (noise burst,
2-10 ms decay) and a tail (short reverb).

**Loop clicks.** Raise the `crossfade` and make sure the source is longer than twice it.
If you called `loopify` before `lofi_finish`, that alone is the bug — use `finish_loop`
(or `Batch`) so the filters and drift are applied before the join.

**Everything sounds the same.** The lo-fi chain is doing too much: vary `cutoff`
(6.5-9 kHz), `bits` (9-12) and `drive` (1.2-2.0) per family instead of using one preset.

**Harsh / fizzy.** Lower `cutoff`, drop `drive`, and set `downsample=1` — aliasing from
decimation is the usual culprit.

**Too quiet in-engine.** Normalise per family, not per file: peaks at -3 dB (SFX),
-6 dB (UI, voice), -12 to -14 dB RMS (ambience beds), -9 dB (music).

**Clipping after mixing layers.** `ra.mix(..., gains=[...])` with the sum of gains near
1.0, then a single `normalize` at the end. Never normalise twice mid-chain.
