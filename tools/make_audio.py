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


if __name__ == "__main__":
    b = ra.Batch("assets/audio")

    # Interaction SFX get a slightly brighter, harder lo-fi chain than beds do:
    # a mechanism has to cut through whatever the room is humming.
    b.add("sfx", "lever_throw", lever_throw(),
          note="industrial lever thrown into its notch: scrape, seat, spring",
          cutoff=8800, bits=11, drive=1.7)

    b.finish()
