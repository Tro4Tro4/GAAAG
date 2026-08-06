"""Generates AGGGA's synthesised sounds. Run from the project root.

    pip install numpy scipy
    python tools/make_audio.py

Everything is built from scratch with numpy, so the library is reproducible from
the seed below and a parameter can be changed and the file re-rendered. That is
the whole reason this script is in the repository rather than in a scratch
folder, and it is the same rule the graphics generators follow: an asset nobody
knows how to redo is an asset that cannot be corrected.

The house sound is modern lo-fi with a retro flavour -- full-band synthesis, then
deliberately degraded to 22 kHz, bandlimited, roughly 11-bit. It should sound
like a fondly remembered 1994 CD-ROM, not a broken one.

Every sound is three layers, which is the rule that separates this from a test
tone: a transient that says what the material is, a body that says what the
object is, and a tail that says what the room is.

The four older files in assets/audio/ -- thud, ui_click, hum_low, hum_high -- are
placeholders from before this script and are not in its manifest: the manifest
describes what this script makes. Replacing them is the next useful job here, and
it costs nothing because their names can stay as the scenes already write them.

Two constraints from CLAUDE.md that shape what belongs here:

* there are two audio players and two buses, so an ambience and a music bed
  cannot sound together. Nothing in this file is an ambience for that reason;
* the game loops a track by restarting it on `finished` rather than by an import
  flag, so the crossfade stitched into the file by `finish_loop()` is what makes
  the seam inaudible. Loops must go through that, never through `loopify()`
  after the lo-fi chain.
"""
import sys

sys.path.insert(0, ".claude/skills/retro-adventure-audio/scripts")
import retroaudio as ra

ra.seed(1994)


def lever_throw():
    """An industrial lever thrown into its notch: travel, seat, spring.

    The order matters more than the ingredients. A lever does not go "clack" all
    at once -- it scrapes for a moment while the shaft moves, seats hard into the
    notch, and then the plate rings for a fraction of a second. Drop the scrape
    and it sounds like a hammer; drop the ring and it sounds like a door.
    """
    # The travel: metal sliding in a slot, brief and quiet. Bandpassed high so it
    # reads as a scrape rather than as a rumble, and it has to be *under* the
    # impact in level or the sound loses its point of attack.
    travel = (ra.bandpass(ra.noise(0.055, "white"), 1800, 7000)
              * ra.adsr(0.055, a=0.012, d=0.02, s=0.5, r=0.02) * 0.22)

    # The seat, which is the clack itself, and it is two things at once: a wide
    # transient for the contact and two resonators for the steel. The low one is
    # the lever's own plate, the high one the pin it lands on.
    contact = ra.bandpass(ra.noise(0.02, "white"), 700, 9000) * ra.decay(0.02, 0.004)
    plate = ra.resonator(contact, 235, q=16) * 1.1
    pin = ra.resonator(contact, 1180, q=22) * 0.55
    body = ra.mix(contact * 0.7, plate, pin)

    # The spring taking up the slack behind the notch: a short falling twang, the
    # detail that says the mechanism is sprung rather than merely heavy.
    spring = (ra.fm(760, ratio=1.5, index=(5.0, 0.6), dur=0.13)
              * ra.decay(0.13, 0.028) * 0.16)

    dry = ra.mix(travel,
                 ra.offset(body, 0.055),
                 ra.offset(spring, 0.075))

    # A small hard room: this is a machine room with steel walls, so a short
    # bright tail. Any more and the lever sounds like it is in a cathedral.
    wet = ra.reverb(dry, room=0.28, mix=0.20)

    # Trimmed on purpose. ra.reverb appends a tail of its own length regardless
    # of how short the dry source is, so left alone a 200 ms clack comes out as a
    # one-second file -- and a lever still ringing while the next caption is being
    # read is a lever in a cathedral. 400 ms is the impact plus a hint of room,
    # inside the 80-400 ms the spec gives interaction SFX.
    keep = ra.n_samples(0.40)
    return ra.fade(wet[:keep], fin=0.0, fout=0.07)


def capsule_land_far():
    """The capsule arriving at the far end: a thud heard through a wall.

    The text dictates this one -- SEQ_LEVER_END is "poi silenzio, e un tonfo
    lontano dalla parte dell'atrio" -- so what has to be synthesised is not a
    thud but *distance*. Distance is almost entirely the absence of high
    frequencies and the presence of a tail: a wall and forty metres of corridor
    eat the transient, which is the crack of the impact, and leave the body,
    which is its mass. Built close and then filtered, rather than built quiet:
    a quiet close thud sounds small, not far.
    """
    # The mass landing in a brass tray: a falling sub and a soft broadband body.
    sub = ra.sine((96, 38), 0.45) * ra.decay(0.45, 0.11)
    body = ra.lowpass(ra.noise(0.28, "brown"), (1200, 240)) * ra.decay(0.28, 0.06)
    # It has come a long way and it is dented: it settles rather than stopping.
    settle = ra.mix(*[
        ra.offset(ra.lowpass(ra.noise(0.05, "brown"), 700)
                  * ra.decay(0.05, 0.012) * g, s)
        for g, s in ((0.30, 0.13), (0.18, 0.22), (0.10, 0.29))
    ])
    dry = ra.mix(sub, body, settle, gains=[1.0, 0.55, 0.5])

    # The wall. One lowpass at 900 Hz is what turns this from "a thud" into "a
    # thud somewhere else", and the long wet reverb is the corridor it crossed.
    far = ra.lowpass(dry, 900)
    wet = ra.reverb(far, room=0.72, mix=0.42)
    keep = ra.n_samples(0.85)
    return ra.fade(wet[:keep], fin=0.0, fout=0.16)


# --------------------------------------------------------------- footsteps ----
# Two surfaces, because the prototype has two floors: the lobby is drawn as
# boards and the corridor and the station as concrete slabs.
#
# Four variants each, and that is not decoration. A single footstep file played
# four and a half times a second is the most audible sign of amateur game audio
# there is: the ear locks onto the repetition within two steps and stops hearing
# a person walking. What breaks the lock is small differences in pitch, level and
# noise -- so each variant gets its own seed, not just its own gain.
SURFACES = {
    # band: where the scuff of the sole lives. tau: how fast it dies -- wood
    # rings on a little, stone stops. thump: the mass of the person landing.
    # ring: the resonance of the floor itself, which stone does not have.
    "wood":  dict(band=(150, 2200), tau=0.070, thump=110, ring=230),
    "stone": dict(band=(180, 2600), tau=0.045, thump=95, ring=None),
}


def footstep(surface, variant):
    p = SURFACES[surface]
    ra.seed(4000 + variant + (100 if surface == "wood" else 0))
    jitter = 1.0 + (variant - 2) * 0.05
    dur = p["tau"] * 4

    # The scuff: filtered noise under a fast decay. On its own this is a "tss",
    # which is why the thump underneath it is what makes it a footfall.
    s = ra.bandpass(ra.noise(dur, "white"), p["band"][0] * jitter, p["band"][1])
    s *= ra.decay(dur, p["tau"])

    if p["thump"]:
        s = ra.mix(s, ra.sine((p["thump"] * jitter, p["thump"] * 0.6), 0.12)
                   * ra.decay(0.12, 0.03), gains=[1.0, 0.5])
    if p["ring"]:
        s = ra.mix(s, ra.resonator(s, p["ring"] * jitter, q=16) * 0.4)

    return s * (0.85 + 0.15 * (variant % 3))


if __name__ == "__main__":
    b = ra.Batch("assets/audio")

    # Interaction SFX get a slightly brighter, harder lo-fi chain than beds do:
    # a mechanism has to cut through whatever the room is humming.
    b.add("sfx", "lever_throw", lever_throw(),
          note="industrial lever thrown into its notch: scrape, seat, spring",
          cutoff=8800, bits=11, drive=1.7)

    # Longer and duller than the lever on purpose: it is far away, and the lo-fi
    # chain must not brighten back what the wall took out.
    # Longer, duller *and quieter* than the lever. The -3 dB the sfx category
    # targets is right for something happening in front of you and wrong for
    # something happening two rooms away: at the same peak as the clack this
    # arrives like a door slamming next door, not like a thud down the corridor.
    # It is the one case where the category default fights what the sound is for.
    b.add("sfx", "capsule_land_far", capsule_land_far(),
          note="the capsule arriving at the far end, heard through a wall",
          cutoff=6000, bits=11, drive=1.3, peak_db=-8.0)

    # Twelve decibels under the clack, and forced there. The category targets -3
    # like any effect, which is right for something that happens once and wrong
    # for the sound the game makes most: at the same peak, walking across the
    # lobby is louder than solving the puzzle. A footstep is the most frequent
    # and least informative sound in the game and it has to sit under everything.
    for surface in SURFACES:
        for variant in range(1, 5):
            b.add("step", f"{surface}_{variant:02d}", footstep(surface, variant),
                  note=f"footfall on {surface}, variant {variant} of 4",
                  cutoff=7600, bits=11, drive=1.4, peak_db=-12.0)

    b.finish()
