"""
retroaudio — mini-DSP toolkit for 90s-flavoured point&click adventure audio.

Design goals:
  * No external assets, no network: everything is synthesised from scratch.
  * numpy + scipy only (scipy optional: falls back to one-pole filters).
  * Mono float32 in [-1, 1] is the internal currency; stereo is (N, 2).

Typical use:
    import retroaudio as ra
    door = ra.mix(ra.creak(), ra.thud(delay=0.9))
    door = ra.lofi_finish(door)
    ra.write_wav("out/sfx_door_wood_open.wav", door)
"""

from __future__ import annotations

import functools
import math
import os
import shutil
import subprocess

import numpy as np

try:
    from scipy import signal as _sig
    HAVE_SCIPY = True
except Exception:  # pragma: no cover
    HAVE_SCIPY = False

SR = 22050          # 90s-authentic default sample rate
EPS = 1e-12
rng = np.random.default_rng(1990)


def seed(n: int) -> None:
    """Make a whole batch reproducible. Always call this at the top of a generator script."""
    global rng
    rng = np.random.default_rng(n)


# ---------------------------------------------------------------- helpers

def n_samples(dur: float, sr: int = SR) -> int:
    return max(1, int(round(dur * sr)))


def timeline(dur: float, sr: int = SR) -> np.ndarray:
    return np.arange(n_samples(dur, sr), dtype=np.float64) / sr


def as_array(value, dur: float, sr: int = SR) -> np.ndarray:
    """Accept a scalar, a (start, end) tuple (exponential glide) or an array."""
    n = n_samples(dur, sr)
    if np.isscalar(value):
        return np.full(n, float(value))
    if isinstance(value, tuple) and len(value) == 2:
        a, b = float(value[0]), float(value[1])
        if a > 0 and b > 0:
            return np.exp(np.linspace(math.log(a), math.log(b), n))
        return np.linspace(a, b, n)
    arr = np.asarray(value, dtype=np.float64)
    if len(arr) == n:
        return arr
    return np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(arr)), arr)


def phase(freq, dur: float, sr: int = SR) -> np.ndarray:
    f = as_array(freq, dur, sr)
    return np.cumsum(2 * np.pi * f / sr)


def db(x: float) -> float:
    """dB -> linear gain."""
    return 10.0 ** (x / 20.0)


def _stereo_safe(fn):
    """Let mono-only DSP functions accept (N, 2) stereo by processing each channel."""
    @functools.wraps(fn)
    def wrapper(x, *args, **kwargs):
        arr = np.asarray(x, dtype=np.float64)
        if arr.ndim == 2:
            chans = [fn(arr[:, i], *args, **kwargs) for i in range(arr.shape[1])]
            n = min(len(c) for c in chans)
            return np.stack([np.asarray(c)[:n] for c in chans], axis=1)
        return fn(arr, *args, **kwargs)
    return wrapper


# ---------------------------------------------------------------- oscillators

def sine(freq, dur, sr=SR):
    return np.sin(phase(freq, dur, sr))


def saw(freq, dur, sr=SR):
    p = phase(freq, dur, sr)
    return 2.0 * ((p / (2 * np.pi)) % 1.0) - 1.0


def triangle(freq, dur, sr=SR):
    p = (phase(freq, dur, sr) / (2 * np.pi)) % 1.0
    return 4.0 * np.abs(p - 0.5) - 1.0


def pulse(freq, dur, duty=0.5, sr=SR):
    """Square / pulse wave. `duty` may be a scalar, (start, end) or an array (PWM)."""
    p = (phase(freq, dur, sr) / (2 * np.pi)) % 1.0
    d = np.clip(as_array(duty, dur, sr), 0.01, 0.99)
    return np.where(p < d, 1.0, -1.0)


square = pulse


def noise(dur, kind="white", sr=SR):
    """kind: white | pink | brown | metal (inharmonic ring)."""
    n = n_samples(dur, sr)
    if kind == "white":
        return rng.uniform(-1, 1, n)
    if kind in ("pink", "brown"):
        spec = np.fft.rfft(rng.uniform(-1, 1, n))
        f = np.fft.rfftfreq(n, 1 / sr)
        f[0] = f[1] if len(f) > 1 else 1.0
        exp = 0.5 if kind == "pink" else 1.0
        out = np.fft.irfft(spec / (f ** exp), n)
        return normalize(out, -1.0)
    if kind == "metal":
        out = np.zeros(n)
        for f0 in rng.uniform(700, 5200, 9):
            out += sine(f0, dur, sr) * rng.uniform(0.4, 1.0) * decay(dur, rng.uniform(0.05, 0.4), sr=sr)
        return normalize(out, -1.0)
    raise ValueError(f"unknown noise kind: {kind}")


def fm(carrier, ratio=2.0, index=3.0, dur=1.0, sr=SR):
    """2-operator FM — the workhorse for bells, clangs, magic and metallic hits."""
    mod = np.sin(phase(np.asarray(as_array(carrier, dur, sr)) * ratio, dur, sr))
    idx = as_array(index, dur, sr)
    return np.sin(phase(carrier, dur, sr) + idx * mod)


# ---------------------------------------------------------------- envelopes

def adsr(dur, a=0.01, d=0.1, s=0.7, r=0.2, sr=SR):
    n = n_samples(dur, sr)
    na, nd, nr = (n_samples(x, sr) if x > 0 else 0 for x in (a, d, r))
    ns = max(0, n - na - nd - nr)
    parts = [
        np.linspace(0, 1, na, endpoint=False) if na else np.empty(0),
        np.linspace(1, s, nd, endpoint=False) if nd else np.empty(0),
        np.full(ns, s),
        np.linspace(s, 0, nr) if nr else np.empty(0),
    ]
    env = np.concatenate(parts)
    return np.resize(env, n) if len(env) != n else env


def decay(dur, tau=0.15, curve=1.0, sr=SR):
    """Percussive exponential decay. Smaller tau = snappier."""
    t = timeline(dur, sr)
    env = np.exp(-t / max(tau, 1e-4)) ** curve
    return env * np.minimum(1.0, t / 0.002 + 1e-9) if len(t) > 1 else env


def ramp(dur, start=0.0, end=1.0, sr=SR):
    return np.linspace(start, end, n_samples(dur, sr))


def fade(x, fin=0.005, fout=0.02, sr=SR):
    x = x.copy()
    ni, no = n_samples(fin, sr), n_samples(fout, sr)
    if ni > 1 and ni < len(x):
        _apply_gain(x, slice(0, ni), np.linspace(0, 1, ni))
    if no > 1 and no < len(x):
        _apply_gain(x, slice(len(x) - no, len(x)), np.linspace(1, 0, no))
    return x


def _apply_gain(x, sl, gain):
    if x.ndim == 1:
        x[sl] *= gain
    else:
        x[sl] *= gain[:, None]


# ---------------------------------------------------------------- filters

def _one_pole_lp(x, cutoff, sr=SR):
    """Time-varying one-pole low-pass. cutoff may be scalar/tuple/array (sweeps!)."""
    c = np.clip(as_array(cutoff, len(x) / sr, sr), 20.0, sr * 0.49)
    alpha = 1.0 - np.exp(-2 * np.pi * c / sr)
    out = np.empty_like(x, dtype=np.float64)
    y = 0.0
    for i in range(len(x)):
        y += alpha[i] * (x[i] - y)
        out[i] = y
    return out


@_stereo_safe
def lowpass(x, cutoff, q=0.707, sr=SR):
    """Static cutoff -> clean biquad. Array/tuple cutoff -> time-varying one-pole sweep."""
    if np.isscalar(cutoff) and HAVE_SCIPY:
        sos = _sig.butter(2, min(float(cutoff), sr * 0.49), "lowpass", fs=sr, output="sos")
        return _sig.sosfilt(sos, x)
    return _one_pole_lp(x, cutoff, sr)


@_stereo_safe
def highpass(x, cutoff, sr=SR):
    if HAVE_SCIPY:
        sos = _sig.butter(2, max(20.0, min(float(cutoff), sr * 0.49)), "highpass", fs=sr, output="sos")
        return _sig.sosfilt(sos, x)
    return x - _one_pole_lp(x, cutoff, sr)


@_stereo_safe
def bandpass(x, low, high, sr=SR):
    if HAVE_SCIPY:
        sos = _sig.butter(2, [max(20.0, low), min(high, sr * 0.49)], "bandpass", fs=sr, output="sos")
        return _sig.sosfilt(sos, x)
    return highpass(_one_pole_lp(x, high, sr), low, sr)


@_stereo_safe
def resonator(x, freq, q=12.0, sr=SR):
    """Narrow resonant peak — turns noise into pitched material (wind, whistles, pipes)."""
    if HAVE_SCIPY:
        b, a = _sig.iirpeak(min(freq, sr * 0.45), q, fs=sr)
        return _sig.lfilter(b, a, x)
    return bandpass(x, freq * 0.9, freq * 1.1, sr)


# ---------------------------------------------------------------- effects

@_stereo_safe
def bitcrush(x, bits=10, downsample=1):
    """The single most 'retro' move. bits 8-12 and downsample 1-3 stay musical."""
    y = np.asarray(x, dtype=np.float64)
    if downsample > 1:
        idx = (np.arange(len(y)) // downsample) * downsample
        y = y[np.clip(idx, 0, len(y) - 1)]
    levels = 2 ** (bits - 1)
    return np.round(y * levels) / levels


@_stereo_safe
def saturate(x, drive=2.0):
    return np.tanh(np.asarray(x) * drive) / np.tanh(drive)


@_stereo_safe
def delay(x, time=0.12, feedback=0.35, mix=0.3, sr=SR):
    d = n_samples(time, sr)
    out = np.asarray(x, dtype=np.float64).copy()
    tail = out.copy()
    for k in range(1, 8):
        g = feedback ** k
        if g < 0.001:
            break
        shifted = np.zeros_like(out)
        off = d * k
        if off >= len(out):
            break
        shifted[off:] = tail[: len(out) - off]
        out += shifted * g * mix
    return out


@_stereo_safe
def reverb(x, room=0.6, mix=0.28, sr=SR):
    """Schroeder-ish: 4 combs + 2 allpass. Cheap, and cheap is the aesthetic."""
    x = np.asarray(x, dtype=np.float64)
    pad = np.concatenate([x, np.zeros(n_samples(0.6 + room, sr))])
    wet = np.zeros_like(pad)
    for ms, g in zip((29.7, 37.1, 41.1, 43.7), (0.78, 0.75, 0.72, 0.70)):
        d = n_samples(ms / 1000.0 * (0.6 + room), sr)
        buf = np.zeros_like(pad)
        gg = g * (0.5 + room * 0.5)
        for k in range(1, 40):
            off, amp = d * k, gg ** k
            if off >= len(pad) or amp < 0.001:
                break
            buf[off:] += pad[: len(pad) - off] * amp
        wet += buf
    wet = _one_pole_lp(wet / 4.0, 4200, sr)
    return pad * (1 - mix) + wet * mix


@_stereo_safe
def chorus(x, rate=0.8, depth=0.004, mix=0.4, sr=SR):
    n = len(x)
    lfo = depth * sr * (0.5 + 0.5 * np.sin(2 * np.pi * rate * timeline(n / sr, sr)))
    idx = np.clip(np.arange(n) - lfo, 0, n - 1)
    return np.asarray(x) * (1 - mix) + np.interp(idx, np.arange(n), x) * mix


@_stereo_safe
def wobble(x, rate=0.6, depth=0.0035, sr=SR):
    """Tape/pitch drift. Tiny amounts (0.002-0.005) read as 'worn cassette', not as a bug."""
    n = len(x)
    drift = np.cumsum(np.sin(2 * np.pi * rate * timeline(n / sr, sr)) * depth)
    idx = np.clip(np.arange(n) + drift * sr * 0.01, 0, n - 1)
    return np.interp(idx, np.arange(n), x)


@_stereo_safe
def tremolo(x, rate=5.0, depth=0.3, sr=SR):
    lfo = 1.0 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * timeline(len(x) / sr, sr)))
    return np.asarray(x) * lfo


def crackle(dur, density=14.0, level=0.05, sr=SR):
    """Vinyl / dusty-CD-ROM crackle. Great glue for ambiences."""
    n = n_samples(dur, sr)
    out = np.zeros(n)
    for _ in range(int(density * dur)):
        i = rng.integers(0, n)
        ln = min(n - i, n_samples(rng.uniform(0.0005, 0.003), sr))
        out[i:i + ln] += rng.uniform(-1, 1, ln) * np.linspace(1, 0, ln)
    return out * level


def noise_floor(dur, level=0.004, sr=SR):
    return highpass(noise(dur, "pink", sr), 60, sr) * level


def hum(dur, freq=50.0, level=0.006, sr=SR):
    return (sine(freq, dur, sr) + 0.4 * sine(freq * 2, dur, sr)) * level


# ---------------------------------------------------------------- mixing / layout

def pad_to(x, n):
    x = np.asarray(x, dtype=np.float64)
    if len(x) >= n:
        return x[:n] if x.ndim == 1 else x[:n, :]
    shape = (n - len(x),) if x.ndim == 1 else (n - len(x), x.shape[1])
    return np.concatenate([x, np.zeros(shape)])


def offset(x, seconds, sr=SR):
    """Shift a layer later in time (returns a longer array)."""
    return np.concatenate([np.zeros(n_samples(seconds, sr)), np.asarray(x, dtype=np.float64)])


def mix(*layers, gains=None):
    """Sum layers of any length. gains is an optional list of linear gains."""
    layers = [np.asarray(l, dtype=np.float64) for l in layers]
    n = max(len(l) for l in layers)
    stereo = any(l.ndim == 2 for l in layers)
    out = np.zeros((n, 2) if stereo else n)
    for i, l in enumerate(layers):
        g = 1.0 if gains is None else gains[i]
        if stereo and l.ndim == 1:
            l = np.stack([l, l], axis=1)
        out += pad_to(l, n) * g
    return out


def pan(x, pos=0.0):
    """pos: -1 hard left .. +1 hard right. Constant-power law."""
    x = np.asarray(x, dtype=np.float64)
    ang = (np.clip(pos, -1, 1) + 1) * math.pi / 4
    return np.stack([x * math.cos(ang), x * math.sin(ang)], axis=1)


def widen(x, spread=0.012, sr=SR):
    """
    Haas-style width for ambiences and music beds. Accepts mono (mono -> stereo) or
    stereo (delays the right channel a touch further). Apply it BEFORE mixing in
    already-panned layers, otherwise you widen material that is already placed.
    """
    x = np.asarray(x, dtype=np.float64)
    d = n_samples(spread, sr)
    if x.ndim == 2:
        right = x[:, 1] if d >= len(x) else np.concatenate([np.zeros(d), x[:-d, 1]])
        return np.stack([x[:, 0], right * 0.96], axis=1)
    right = x if d >= len(x) else np.concatenate([np.zeros(d), x[:-d]])
    return np.stack([x, right * 0.92], axis=1)


def normalize(x, peak_db=-3.0):
    x = np.asarray(x, dtype=np.float64)
    peak = np.max(np.abs(x)) + EPS
    return x * (db(peak_db) / peak)


def loopify(x, crossfade=0.25, sr=SR):
    """Return a seamlessly looping version: the tail is crossfaded onto the head."""
    x = np.asarray(x, dtype=np.float64)
    c = min(n_samples(crossfade, sr), len(x) // 2 - 1)
    out = x[: len(x) - c].copy()
    up = np.linspace(0, 1, c)
    head, tail = x[:c], x[len(x) - c:]
    if x.ndim == 1:
        out[:c] = head * up + tail * (1 - up)
    else:
        out[:c] = head * up[:, None] + tail * (1 - up)[:, None]
    return out


# ---------------------------------------------------------------- notes & music

_SEMI = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


def note(name: str) -> float:
    """'a4' -> 440.0. Accepts 'c#3', 'eb5', rests as None handled by seq()."""
    s = name.strip().lower()
    semi = _SEMI[s[0]]
    i = 1
    while i < len(s) and s[i] in "#b":
        semi += 1 if s[i] == "#" else -1
        i += 1
    octv = int(s[i:])
    return 440.0 * 2 ** ((semi - 9 + (octv - 4) * 12) / 12)


def seq(pattern, bpm=96, voice=None, sr=SR, gap=0.0):
    """
    pattern: list of (note_or_None, beats) — None is a rest.
    voice(freq, dur) -> mono array. Defaults to a soft pulse lead.
    """
    if voice is None:
        def voice(f, d):
            v = pulse(f, d, duty=0.35, sr=sr) * 0.5 + triangle(f, d, sr) * 0.5
            return lowpass(v, 3200, sr=sr) * adsr(d, 0.008, 0.05, 0.6, min(0.25, d * 0.5), sr=sr)
    spb = 60.0 / bpm
    chunks = []
    for nt, beats in pattern:
        d = beats * spb
        chunks.append(np.zeros(n_samples(d, sr)) if nt is None
                      else pad_to(voice(note(nt), max(0.02, d - gap)), n_samples(d, sr)))
    return np.concatenate(chunks) if chunks else np.zeros(1)


def chord(names, dur, voice=None, sr=SR):
    return mix(*[seq([(n, 1)], bpm=60.0 / dur, voice=voice, sr=sr) for n in names],
               gains=[1.0 / len(names)] * len(names))


# ---------------------------------------------------------------- mock voice

VOWELS = {  # (F1, F2, F3) in Hz — neutral adult-ish formants
    "a": (730, 1090, 2440), "e": (530, 1840, 2480), "i": (390, 1990, 2550),
    "o": (570, 840, 2410), "u": (440, 1020, 2240),
}


def mumble(syllables="da-be-do", pitch=150.0, contour=(1.0, 0.85), speed=1.0, sr=SR):
    """
    LucasArts-style gibberish voice: formant-filtered pulse train, one syllable per token.
    syllables: dash-separated, e.g. 'ba-da-bu?'. Use a trailing '?' for a rising contour.
    """
    tokens = [s for s in syllables.replace("?", "").split("-") if s]
    rising = syllables.strip().endswith("?")
    if rising:
        contour = (0.9, 1.25)
    out = []
    for k, tok in enumerate(tokens):
        vw = next((c for c in reversed(tok) if c in VOWELS), "a")
        d = rng.uniform(0.11, 0.19) / max(speed, 0.1)
        pos = k / max(1, len(tokens) - 1)
        f0 = pitch * (contour[0] + (contour[1] - contour[0]) * pos)
        f0 *= rng.uniform(0.97, 1.03)
        glottal = pulse(f0 * (1 + 0.012 * sine(5.5, d, sr)), d, duty=0.18, sr=sr)
        src = glottal * 0.85 + noise(d, "white", sr) * 0.05
        f1, f2, f3 = VOWELS[vw]
        v = (resonator(src, f1, 9, sr) * 1.0
             + resonator(src, f2, 11, sr) * 0.55
             + resonator(src, f3, 13, sr) * 0.22)
        v = lowpass(v, 3600, sr=sr) * adsr(d, 0.02, 0.04, 0.8, 0.05, sr=sr)
        out.append(normalize(v, -6.0))
        if tok != tokens[-1]:
            out.append(np.zeros(n_samples(rng.uniform(0.02, 0.05), sr)))
    return np.concatenate(out) if out else np.zeros(1)


# ---------------------------------------------------------------- master chain

def lofi_finish(x, bits=11, downsample=1, cutoff=7800, drive=1.4,
                wobble_depth=0.0025, floor=0.0035, peak_db=-3.0, sr=SR):
    """
    The house sound: bandlimit -> gentle saturation -> quantise -> drift -> noise floor.
    Run this LAST on every asset so the whole library sits in one sonic world.
    Bypass `wobble_depth` (=0) on short UI clicks, where drift is audible as a glitch.
    """
    x = np.asarray(x, dtype=np.float64)
    stereo = x.ndim == 2
    chans = [x[:, i] for i in range(2)] if stereo else [x]
    done = []
    for ch in chans:
        y = lowpass(ch, cutoff, sr=sr)
        y = highpass(y, 45, sr=sr)
        y = saturate(y, drive)
        if wobble_depth:
            y = wobble(y, rate=0.55, depth=wobble_depth, sr=sr)
        y = bitcrush(y, bits=bits, downsample=downsample)
        if floor:
            y = y + noise_floor(len(y) / sr, floor, sr)
        done.append(y)
    out = np.stack(done, axis=1) if stereo else done[0]
    return normalize(out, peak_db)


def finish_loop(x, crossfade=1.0, sr=SR, **kwargs):
    """
    The only correct way to finish a looping asset: colour FIRST, crossfade LAST.
    Doing it the other way round audibly breaks the seam, because the IIR filters and
    the tape drift inside lofi_finish start from a zero state and warm up over the
    first few dozen milliseconds — so the head no longer matches the tail.
    """
    peak_db = kwargs.get("peak_db", -3.0)
    return normalize(loopify(lofi_finish(x, sr=sr, **kwargs), crossfade, sr), peak_db)


# ---------------------------------------------------------------- I/O & QA

def write_wav(path, x, sr=SR, bit_depth=16):
    """16-bit PCM WAV, mono or stereo. Creates parent dirs. Returns the path."""
    import wave
    x = np.asarray(x, dtype=np.float64)
    x = np.clip(x, -1.0, 1.0)
    data = (x * 32767.0).astype("<i2")
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(2 if x.ndim == 2 else 1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())
    return path


def to_ogg(wav_path, quality=4, keep_wav=True):
    """Convert to .ogg via ffmpeg (engine-friendly for loops/music). Returns path or None."""
    if not shutil.which("ffmpeg"):
        return None
    out = os.path.splitext(wav_path)[0] + ".ogg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                    "-c:a", "libvorbis", "-q:a", str(quality), out], check=True)
    if not keep_wav:
        os.remove(wav_path)
    return out


def report(x, sr=SR, label="", loop=False):
    """
    QA gate before delivery: duration, true peak, RMS, and (for loops) seam quality.

    The seam figure is the jump between last and first sample divided by the signal's
    typical sample-to-sample movement (95th percentile). Below ~3 the join hides inside
    the material's own motion and is inaudible; above ~3 you will hear a click.
    An absolute sample difference is a bad test here — dense noise moves a lot between
    any two neighbouring samples, so a "large" jump can be perfectly transparent.
    """
    x = np.asarray(x, dtype=np.float64)
    mono = x.mean(axis=1) if x.ndim == 2 else x
    peak = float(np.max(np.abs(x)) + EPS)
    rms = float(np.sqrt(np.mean(mono ** 2)) + EPS)
    info = {"dur": len(mono) / sr, "peak_db": 20 * math.log10(peak),
            "rms_db": 20 * math.log10(rms), "channels": 2 if x.ndim == 2 else 1}
    line = (f"{label:<32} {info['dur']:6.2f}s  {'st' if info['channels'] == 2 else 'mo'}  "
            f"peak {info['peak_db']:6.1f} dB  rms {info['rms_db']:6.1f} dB")
    if loop:
        step_ref = float(np.percentile(np.abs(np.diff(mono)), 95) + EPS)
        info["seam"] = float(abs(mono[0] - mono[-1]) / step_ref)
        line += f"  seam {info['seam']:5.2f}"
        if info["seam"] > 3.0:
            line += "   <-- CLICK: raise the crossfade"
    print(line)
    return info


CATEGORIES = {           # category -> (peak_db, is_loop_by_default, drift)
    "sfx":   (-3.0, False, True),
    "step":  (-3.0, False, True),
    "amb":   (-3.0, True, True),
    "mus":   (-4.0, True, True),
    "sting": (-3.0, False, True),
    "ui":    (-6.0, False, False),
    "vox":   (-6.0, False, False),
}


class Batch:
    """
    Renders a whole asset library with consistent naming, finishing and QA.

    b = Batch("/mnt/user-data/outputs/audio")
    b.add("sfx", "door_wood_open", door, note="creak + latch, 2.1s")
    b.add("amb", "tavern", amb, crossfade=1.5)
    b.finish()          # writes files + manifest.md + manifest.json

    Files land as <category>_<name>.wav. Loops also get an .ogg when ffmpeg is present,
    because engines stream compressed loops but want uncompressed one-shots.
    """

    def __init__(self, outdir, sr=SR, ogg_for_loops=True):
        self.outdir = outdir
        self.sr = sr
        self.ogg_for_loops = ogg_for_loops
        self.rows = []
        os.makedirs(outdir, exist_ok=True)

    def add(self, category, name, audio, note="", loop=None, crossfade=1.0,
            finish=True, **finish_kwargs):
        if category not in CATEGORIES:
            raise ValueError(f"category must be one of {sorted(CATEGORIES)}")
        peak_db, loop_default, drift = CATEGORIES[category]
        loop = loop_default if loop is None else loop
        finish_kwargs.setdefault("peak_db", peak_db)
        if not drift:
            finish_kwargs.setdefault("wobble_depth", 0.0)
        if finish:
            audio = (finish_loop(audio, crossfade, sr=self.sr, **finish_kwargs) if loop
                     else lofi_finish(audio, sr=self.sr, **finish_kwargs))
        fname = f"{category}_{name}.wav"
        path = write_wav(os.path.join(self.outdir, fname), audio, self.sr)
        info = report(audio, self.sr, label=fname, loop=loop)
        if loop and self.ogg_for_loops:
            to_ogg(path)
        self.rows.append({"file": fname, "category": category, "name": name,
                          "loop": loop, "note": note, **info})
        return path

    def finish(self):
        import json
        with open(os.path.join(self.outdir, "manifest.json"), "w") as f:
            json.dump({"sample_rate": self.sr, "assets": self.rows}, f, indent=2)
        lines = ["# Audio manifest", "",
                 f"{len(self.rows)} assets - {self.sr} Hz, 16-bit PCM WAV", "",
                 "| File | Category | Loop | Length | Peak | Notes |",
                 "|---|---|---|---|---|---|"]
        for r in self.rows:
            lines.append(f"| `{r['file']}` | {r['category']} | {'yes' if r['loop'] else 'no'} "
                         f"| {r['dur']:.2f}s | {r['peak_db']:.1f} dB | {r['note']} |")
        flagged = [r for r in self.rows if r.get("seam", 0) > 3.0]
        if flagged:
            lines += ["", "**Loops needing a longer crossfade:** "
                      + ", ".join(f"`{r['file']}`" for r in flagged)]
        path = os.path.join(self.outdir, "manifest.md")
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"\n{len(self.rows)} assets -> {self.outdir}")
        return path


if __name__ == "__main__":
    seed(7)
    out = "/tmp/retroaudio_selftest"
    hit = mix(noise(0.35, "metal") * decay(0.35, 0.09),
              fm(180, 1.5, 6, 0.3) * decay(0.3, 0.06))
    report(lofi_finish(hit), label="selftest/hit")
    amb = widen(lowpass(noise(6.0, "brown"), (400, 900)) * 0.6 + crackle(6.0))
    report(finish_loop(amb, 0.8), label="selftest/ambience-loop", loop=True)
    tune = seq([("a3", 1), ("c4", 1), ("e4", 1), (None, 0.5), ("d4", 1.5)], bpm=104)
    report(lofi_finish(reverb(tune, 0.5, 0.25)), label="selftest/music")
    report(lofi_finish(mumble("wa-da-be-du?"), wobble_depth=0), label="selftest/mumble")
    p = write_wav(f"{out}/hit.wav", lofi_finish(hit))
    print("wrote", p, "ogg:", to_ogg(p))
