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
    #
    # The bands stop far lower than a first version had them -- 1400 and 1600
    # instead of 2200 and 2600 -- because reported from the device the steps came
    # out too loud and too sharp. See _soft() for the whole of what that meant.
    "wood":  dict(band=(120, 1350), tau=0.075, thump=104, ring=210),
    "stone": dict(band=(140, 1500), tau=0.050, thump=92, ring=None),
}

# What "softer" turned out to be, and it was four separate things, not a volume
# knob. Measured on the wood variant, before and after:
#
#                       loud & sharp      soft
#   peak                -12 dB            -17 dB
#   energy above 2 kHz  14.6 %            2.1 %
#   spectral centroid   925 Hz            328 Hz
#   attack              instant           9 ms
#
# The level was the easy half. The other three are what "incisive" meant:
#
# * the top of the noise band, which is where the tack of a hard sole lives;
# * the attack. A decay envelope starts at full amplitude on its first sample,
#   and that step *is* a click -- nine milliseconds of rise removes it without
#   making the step feel late;
# * the drive in the lo-fi chain, because saturation manufactures the very
#   harmonics that read as bite.
#
# And a warning found by overshooting: taken all the way down -- band at 900,
# cutoff at 4200 -- the centroid falls to 156 Hz and the step stops being a step.
# At four and a half a second a series of 150 Hz thumps is a rumble, not somebody
# walking. Soft is not the same as dull, and the distance between the two is
# about one octave of centroid.


# How much each variant is nudged, and one of these is not where you would
# expect. Level variation cannot live inside the audio: Batch normalises every
# file to the category's peak, so a gain applied to the array is scaled straight
# back out again. It was measured -- with the level baked in, the four stone
# variants came out at -30.6, -30.7, -30.7 and -30.7 dB RMS, which is one sound
# four times, which is the exact thing variants exist to avoid. So the level
# difference is asked of the *normaliser* instead, one peak target per variant.
#
# The pitch and length nudges do survive normalisation, and they matter more here
# than they did in the loud version: with the band heavily lowpassed there is far
# less noise left to tell the variants apart on its own.
STEP_PITCH = (0.91, 0.97, 1.03, 1.09)          # +/- 9% on band and thump
STEP_LENGTH = (1.00, 1.16, 0.92, 1.08)         # how long each one takes to die
STEP_PEAK = (-22.8, -21.6, -22.3, -21.9)       # +/- 0.6 dB, which normalising keeps


def footstep(surface, variant):
    p = SURFACES[surface]
    ra.seed(4000 + variant + (100 if surface == "wood" else 0))
    jitter = STEP_PITCH[variant - 1]
    tau = p["tau"] * STEP_LENGTH[variant - 1]
    dur = tau * 4

    # The scuff: filtered noise under a fast decay. On its own this is a "tss",
    # which is why the thump underneath it is what makes it a footfall.
    s = ra.bandpass(ra.noise(dur, "white"), p["band"][0] * jitter, p["band"][1])

    # An ADSR and not a decay, for the attack alone: a decay envelope is at full
    # amplitude on its first sample, and that vertical step is heard as a click on
    # top of the sound. The release is long relative to the decay so the step
    # tails off instead of stopping.
    s *= ra.adsr(dur, a=0.012, d=tau, s=0.18, r=tau * 1.6)

    if p["thump"]:
        # Louder relative to the scuff than it was: in a soft footfall the mass
        # of the person is the body of the sound and the scuff is only its edge.
        #
        # And the thump gets an attack of its own, which it did not have at first
        # and which was the whole of the impact that survived softening the scuff:
        # a decay envelope is at full amplitude on its first sample, so once the
        # thump had been made the loudest layer, *its* onset was the sharpest edge
        # in the sound. Fourteen milliseconds of rise takes the crest factor from
        # 15.7 to 14.2 dB and the centroid from 331 to 219 Hz at the same level --
        # which is to say it is the punch, not the volume.
        thump = ra.sine((p["thump"] * jitter, p["thump"] * 0.6), 0.14)
        thump *= ra.adsr(0.14, a=0.014, d=0.05, s=0.25, r=0.07)
        s = ra.mix(s, thump, gains=[1.0, 0.78])
    if p["ring"]:
        # Lower Q and less of it: at q=16 the board answered with a note, which
        # is charming once and a bell after four seconds of walking.
        s = ra.mix(s, ra.resonator(s, p["ring"] * jitter, q=9) * 0.20)

    return s


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

    # Twenty-odd decibels under the clack, and forced there. The category targets
    # -3 like any effect, which is right for something that happens once and wrong
    # for the sound the game makes most: at the same peak, walking across the
    # lobby is louder than solving the puzzle. A footstep is the most frequent and
    # least informative sound in the game and it has to sit under everything.
    #
    # The cutoff and the drive are the low end of the house range rather than the
    # high end, which is the opposite of what an interaction SFX gets: a mechanism
    # has to cut through, a footstep has to disappear into the floor.
    for surface in SURFACES:
        for variant in range(1, 5):
            b.add("step", f"{surface}_{variant:02d}", footstep(surface, variant),
                  note=f"soft footfall on {surface}, variant {variant} of 4",
                  cutoff=5000, bits=11, drive=1.00,
                  peak_db=STEP_PEAK[variant - 1])

    b.finish()
