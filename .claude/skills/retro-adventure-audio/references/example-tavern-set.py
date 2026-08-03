"""Esempio funzionante, non materiale di AGGGA.

E' il set che l'autore della skill ha usato per la demo (una taverna di porto,
26 asset). Sta qui come riferimento di come si scrive un generatore intero: la
stratificazione dei suoni, le varianti dei passi, le ambienze, la musica in
battute, gli stinger e la voce finta. I suoni che produce non c'entrano niente
con questo gioco: non eseguirlo dentro assets/.

Il manifest che ne esce e' in example-manifest.md, accanto a questo file.
"""
import sys
sys.path.insert(0, ".claude/skills/retro-adventure-audio/scripts")
import retroaudio as ra

ra.seed(1994)
b = ra.Batch("/tmp/tavern-demo")   # esempio: non e' materiale di AGGGA

# ---------------------------------------------------------------- SFX
creak = ra.saw((140, 310), 1.1) * 0.5
creak = ra.resonator(creak, 240, q=14) + ra.resonator(creak, 430, q=18) * 0.4
creak *= ra.tremolo(ra.adsr(1.1, .12, .2, .7, .35), rate=11, depth=.55)
latch = ra.offset(ra.noise(.06, "metal") * ra.decay(.06, .012), 1.0)
b.add("sfx", "door_tavern_open", ra.reverb(ra.mix(creak, latch, gains=[.8, .5]), .4, .22),
      note="rising creak + latch", cutoff=8500, drive=1.6)

creak_c = ra.saw((300, 130), 0.8) * 0.5
creak_c = ra.resonator(creak_c, 240, q=14) * ra.adsr(0.8, .05, .2, .7, .3)
slam = ra.offset(ra.mix(ra.sine((120, 45), .3) * ra.decay(.3, .07),
                        ra.lowpass(ra.noise(.2, "brown"), (2000, 300)) * ra.decay(.2, .04),
                        gains=[1, .7]), 0.7)
b.add("sfx", "door_tavern_close", ra.reverb(ra.mix(creak_c, slam, gains=[.5, 1.0]), .4, .2),
      note="falling creak + slam", cutoff=8500, drive=1.7)

b.add("sfx", "mug_set_down", ra.mix(
    ra.resonator(ra.noise(.12, "white"), 380, q=10) * ra.decay(.12, .03),
    ra.sine((200, 130), .1) * ra.decay(.1, .025), gains=[.7, .6]), note="wood table")

b.add("sfx", "coins_drop", ra.mix(*[
    ra.offset(ra.fm(f, 3.9, (8, 1), .5) * ra.decay(.5, .10), ra.rng.uniform(0, .18))
    for f in (1750, 2100, 2550, 3050)]), note="4 coins, scattered")

b.add("sfx", "bottle_break", ra.mix(
    ra.highpass(ra.noise(.35, "white"), 2500) * ra.decay(.35, .05),
    *[ra.offset(ra.fm(f, 4.5, 8, .4) * ra.decay(.4, .06), ra.rng.uniform(0, .12))
      for f in (1800, 2400, 3100, 4200)]), note="glass shatter")

b.add("sfx", "map_unroll", (lambda p: p * ra.adsr(.45, .03, .1, .6, .2)
                            * (.5 + .5 * ra.sine(19, .45)))(
      ra.bandpass(ra.noise(.45, "white"), 1600, 8000)), note="parchment")

b.add("sfx", "chest_open", ra.reverb(ra.mix(
    ra.resonator(ra.saw((90, 190), .7), 300, q=12) * ra.adsr(.7, .08, .2, .6, .3) * .6,
    ra.offset(ra.fm(1400, 2.1, 5, .12) * ra.decay(.12, .02), .6)), .5, .25), note="hinge + latch")

pick = ra.mix(ra.seq([("e5", .5), ("b5", .5)], bpm=210),
              ra.noise(.05, "white") * ra.decay(.05, .008) * .25)
b.add("sfx", "item_pickup", pick, note="rising 5th, inventory add")

b.add("sfx", "lantern_light", ra.mix(
    ra.bandpass(ra.noise(.1, "white"), 2000, 9000) * ra.decay(.1, .02),
    ra.offset(ra.lowpass(ra.noise(.5, "brown"), 1200) * ra.adsr(.5, .05, .15, .5, .25) * .5, .08)),
    note="strike + whoosh")

# ---------------------------------------------------------------- footsteps
SURF = {"wood": dict(band=(150, 2200), tau=.070, thump=110, ring=230),
        "stone": dict(band=(180, 2600), tau=.045, thump=95, ring=None)}
for surf, p in SURF.items():
    for v in range(1, 5):
        ra.seed(4000 + v * 17 + len(surf))
        j = 1.0 + (v - 2) * .05
        d = p["tau"] * 4
        s = ra.bandpass(ra.noise(d, "white"), p["band"][0] * j, p["band"][1]) * ra.decay(d, p["tau"])
        s = ra.mix(s, ra.sine((p["thump"] * j, p["thump"] * .6), .12) * ra.decay(.12, .03), gains=[1, .5])
        if p["ring"]:
            s = ra.mix(s, ra.resonator(s, p["ring"] * j, q=16) * .4)
        b.add("step", f"{surf}_{v:02d}", s * (.85 + .15 * (v % 3)), note=f"{surf} variant {v}")
ra.seed(1994)

# ---------------------------------------------------------------- ambiences
crowd = ra.mix(*[ra.pan(ra.offset(ra.lowpass(ra.mumble("ba-da-bo-de", pitch=ra.rng.uniform(90, 190)), 1400) * .18,
                                  ra.rng.uniform(0, 15.)), ra.rng.uniform(-.9, .9)) for _ in range(14)])
room = ra.widen(ra.lowpass(ra.noise(16.0, "pink"), 900) * .25, .03)
clinks = ra.mix(*[ra.pan(ra.offset(ra.fm(2100, 3.2, 5, .25) * ra.decay(.25, .05) * .15,
                                   ra.rng.uniform(0, 15.)), ra.rng.uniform(-.7, .7)) for _ in range(7)])
b.add("amb", "tavern_interior", ra.reverb(ra.mix(crowd, room, clinks), .8, .3),
      crossfade=1.5, note="crowd mumble, room tone, mug clinks", cutoff=7200)

harbour = ra.mix(ra.widen(ra.lowpass(ra.noise(15.0, "brown"), (280, 620)) * .55, .025),
                 ra.mix(*[ra.pan(ra.offset(ra.bandpass(ra.noise(1.6, "white"), 500, 4000)
                                           * ra.adsr(1.6, .5, .4, .5, .6) * .3,
                                           i * 3.0 + ra.rng.uniform(0, .8)), ra.rng.uniform(-.6, .6))
                          for i in range(5)]),
                 ra.mix(*[ra.pan(ra.offset(ra.resonator(ra.noise(.5, "pink"), 1250, 8)
                                           * ra.decay(.5, .12) * .12, ra.rng.uniform(0, 14.)),
                                 ra.rng.uniform(-1, 1)) for _ in range(4)]))
b.add("amb", "harbour_night", harbour, crossfade=1.3, note="wind bed, waves, gull cries", cutoff=7000)

fire = ra.lowpass(ra.noise(9.0, "brown"), 1100) * .5
fire *= .7 + .3 * ra.sine(.7, 9.0)
fire += ra.crackle(9.0, density=40, level=.09)
b.add("amb", "fireplace", ra.widen(fire, .012), crossfade=1.0, note="hearth, breathing + spits")

# ---------------------------------------------------------------- music
def pad(f, d):
    v = ra.saw(f, d) * .4 + ra.saw(f * 1.005, d) * .4 + ra.sine(f / 2, d) * .3
    return ra.lowpass(v, 1500) * ra.adsr(d, .25, .3, .7, .4)
def lead(f, d):
    v = ra.pulse(f * (1 + .006 * ra.sine(5.2, d)), d, duty=.30)
    return ra.lowpass(v, 3400) * ra.adsr(d, .01, .06, .65, min(.2, d * .4))
def bass(f, d):
    return ra.lowpass(ra.pulse(f, d, .5) * .7 + ra.sine(f / 2, d) * .5, 900) * ra.adsr(d, .005, .08, .55, .08)
def bell(f, d):
    return ra.fm(f, 3.01, (7, .4), d) * ra.decay(d, d * .28)

BPM = 84
BARS = 4
melody = ra.seq([("e4", 1), ("g4", 1), ("a4", 2), (None, .5), ("g4", .5), ("e4", 1), ("d4", 2)], bpm=BPM, voice=lead)
bassline = ra.seq([("a2", 2), ("a2", 2), ("f2", 2), ("g2", 2)], bpm=BPM, voice=bass)
pads = ra.seq([("a3", 4), ("f3", 4)], bpm=BPM, voice=pad)
theme = ra.mix(melody, bassline, pads, gains=[.55, .45, .30])
theme = theme[: ra.n_samples(BARS * 4 * 60 / BPM)]          # exact bar count
b.add("mus", "tavern_theme", ra.widen(ra.reverb(theme, .6, .25), .014),
      crossfade=.5, note=f"{BARS} bars @ {BPM} bpm, lead+bass+pad")

b.add("sting", "puzzle_solved", ra.reverb(ra.seq([("c5", .5), ("e5", .5), ("g5", .5), ("c6", 1.5)],
                                                bpm=150, voice=bell), .7, .35), note="success")
b.add("sting", "wrong_move", ra.reverb(ra.seq([("g3", .75), ("f#3", .75), ("c3", 2)],
                                              bpm=110, voice=pad), .6, .3), note="failure")
b.add("sting", "discovery", ra.chorus(ra.mix(ra.chord(["d4", "f4", "a4", "c5"], 2.5, voice=pad),
                                             ra.seq([(None, 1), ("b4", 1.5)], bpm=90, voice=bell)),
                                      depth=.007), note="mystery / clue found")

# ---------------------------------------------------------------- UI
b.add("ui", "click", ra.mix(ra.noise(.03, "white") * ra.decay(.03, .004),
                            ra.sine(1800, .03) * ra.decay(.03, .006), gains=[.5, .6]))
b.add("ui", "hover", ra.sine((1200, 1500), .05) * ra.decay(.05, .015) * .5)
b.add("ui", "verb_confirm", ra.seq([("c5", .5), ("g5", .5)], bpm=260))
b.add("ui", "error", ra.saturate(ra.pulse(150, .18, .4) * ra.decay(.18, .06), 3.0))
for v in range(1, 4):
    ra.seed(700 + v)
    b.add("ui", f"text_blip_{v:02d}", ra.pulse(920 * (1 + (v - 2) * .05), .022, .25)
          * ra.decay(.022, .006) * .4, note=f"text crawl variant {v}")
ra.seed(1994)

# ---------------------------------------------------------------- voice
CAST = {"hero": dict(pitch=135, speed=1.0), "barkeep": dict(pitch=160, speed=1.1)}
def line(who, syl):
    return ra.reverb(ra.lowpass(ra.mumble(syl, **CAST[who]), 3400), room=.3, mix=.12)
b.add("vox", "hero_01", line("hero", "da-be-mo-ta"), note="placeholder: neutral remark")
b.add("vox", "hero_02", line("hero", "wa-de-lu-ba-do?"), note="placeholder: question")
b.add("vox", "barkeep_01", line("barkeep", "bo-de-ra-mi-to"), note="placeholder: greeting")

b.finish()
