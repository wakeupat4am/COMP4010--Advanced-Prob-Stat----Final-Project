"""
Generate 20 synthetic mono 16-bit / 16 kHz WAV clips (~3 s each).

Layout:
  noise_01.wav ... noise_10.wav   -> ambient-noise-like (close to Gaussian)
  music_01.wav ... music_10.wav   -> music-like (peaky / sub-Gaussian-tailed)

Run once to populate this folder. Re-running is deterministic (fixed seed).
"""

import os
import wave
import struct
import numpy as np

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 16000           # sampling rate (Hz)
DUR = 3.0            # seconds
N = int(SR * DUR)    # samples per clip
DTYPE_MAX = 32767    # 16-bit signed PCM

rng = np.random.default_rng(20260511)


def to_pcm16(x: np.ndarray) -> bytes:
    """Normalize float array to ~0.7 peak and pack as little-endian int16 bytes."""
    peak = np.max(np.abs(x))
    if peak < 1e-12:
        peak = 1.0
    x = 0.7 * x / peak
    x = np.clip(x, -1.0, 1.0)
    pcm = (x * DTYPE_MAX).astype(np.int16)
    return pcm.tobytes()


def write_wav(path: str, samples: np.ndarray, sr: int = SR) -> None:
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)        # 16-bit
        w.setframerate(sr)
        w.writeframes(to_pcm16(samples))


# ---------------------------------------------------------------------------
# Ambient-noise generators (amplitude distribution close to Gaussian)
# ---------------------------------------------------------------------------

def white_noise(n: int) -> np.ndarray:
    return rng.standard_normal(n)


def pink_noise(n: int) -> np.ndarray:
    """1/f pink noise via spectral shaping of white Gaussian noise."""
    x = rng.standard_normal(n)
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    freqs[0] = 1.0
    X = X / np.sqrt(freqs)
    y = np.fft.irfft(X, n=n)
    # demean and renormalize variance
    y = y - y.mean()
    y = y / (y.std() + 1e-12)
    return y


def brown_noise(n: int) -> np.ndarray:
    """1/f^2 brown(ian) noise via spectral shaping."""
    x = rng.standard_normal(n)
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    freqs[0] = 1.0
    X = X / freqs
    y = np.fft.irfft(X, n=n)
    y = y - y.mean()
    y = y / (y.std() + 1e-12)
    return y


def fan_like(n: int) -> np.ndarray:
    """Band-limited noise modulated by a slow envelope (fan / HVAC hum)."""
    base = pink_noise(n)
    t = np.arange(n) / SR
    # slow low-freq amplitude wobble
    env = 1.0 + 0.15 * np.sin(2 * np.pi * 0.7 * t + rng.uniform(0, 2 * np.pi))
    # subtle 50/60 Hz hum + harmonic
    hum = 0.05 * np.sin(2 * np.pi * 60 * t) + 0.02 * np.sin(2 * np.pi * 120 * t)
    return env * base + hum


NOISE_RECIPES = [
    ("white",     lambda: white_noise(N)),
    ("pink",      lambda: pink_noise(N)),
    ("brown",     lambda: brown_noise(N)),
    ("fan",       lambda: fan_like(N)),
    ("white2",    lambda: 0.8 * white_noise(N) + 0.2 * pink_noise(N)),
    ("pink2",     lambda: pink_noise(N) + 0.1 * white_noise(N)),
    ("traffic",   lambda: brown_noise(N) + 0.3 * pink_noise(N)),
    ("room",      lambda: 0.6 * pink_noise(N) + 0.4 * white_noise(N)),
    ("ac",        lambda: fan_like(N) + 0.1 * white_noise(N)),
    ("street",    lambda: brown_noise(N) + 0.2 * white_noise(N)),
]


# ---------------------------------------------------------------------------
# Music-like generators (peaked-at-zero amplitude distribution, super-Gaussian)
# ---------------------------------------------------------------------------

# A simple pentatonic-ish scale (Hz) so the clips sound musical-ish
SCALE_HZ = np.array([220.0, 246.94, 277.18, 329.63, 369.99, 440.0, 493.88, 554.37])


def adsr(n: int, attack=0.05, decay=0.1, sustain=0.7, release=0.2) -> np.ndarray:
    """Per-note ADSR envelope (length = n samples)."""
    a = int(n * attack)
    d = int(n * decay)
    r = int(n * release)
    s = n - a - d - r
    if s < 0:
        s = 0
        r = n - a - d
    env = np.concatenate([
        np.linspace(0, 1, a, endpoint=False),
        np.linspace(1, sustain, d, endpoint=False),
        np.full(s, sustain),
        np.linspace(sustain, 0, r, endpoint=True),
    ])
    if env.size < n:
        env = np.pad(env, (0, n - env.size))
    return env[:n]


def harmonic_tone(freq: float, n: int, n_harm: int = 5) -> np.ndarray:
    """Sum of decaying harmonics — gives a richer-than-sine timbre."""
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k in range(1, n_harm + 1):
        amp = 1.0 / k
        phase = rng.uniform(0, 2 * np.pi)
        y += amp * np.sin(2 * np.pi * k * freq * t + phase)
    return y


def melody(n: int, n_notes: int = 8, n_harm: int = 5) -> np.ndarray:
    """Sequence of harmonic notes with ADSR envelopes -> peaky amplitude pdf."""
    seg = n // n_notes
    out = np.zeros(n)
    for i in range(n_notes):
        f = float(rng.choice(SCALE_HZ))
        tone = harmonic_tone(f, seg, n_harm=n_harm)
        tone = tone * adsr(seg)
        out[i * seg:(i + 1) * seg] += tone
    return out


def chord(n: int, n_notes: int = 3, n_harm: int = 4) -> np.ndarray:
    """A sustained chord with slow tremolo."""
    freqs = rng.choice(SCALE_HZ, size=n_notes, replace=False)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        y += harmonic_tone(float(f), n, n_harm=n_harm)
    trem = 1.0 + 0.3 * np.sin(2 * np.pi * 4.0 * t)   # 4 Hz vibrato-ish
    fade = adsr(n, attack=0.1, decay=0.1, sustain=0.85, release=0.15)
    return y * trem * fade


def singing_like(n: int) -> np.ndarray:
    """Pitched tone with vibrato + formant-ish low-pass shaping."""
    t = np.arange(n) / SR
    base_f = float(rng.choice(SCALE_HZ[:5]))
    vib = 5.0 * np.sin(2 * np.pi * 5.5 * t)          # ~5.5 Hz vibrato
    inst_freq = base_f + vib
    phase = 2 * np.pi * np.cumsum(inst_freq) / SR
    y = np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    y = y * adsr(n, attack=0.08, decay=0.1, sustain=0.8, release=0.15)
    return y


MUSIC_RECIPES = [
    ("melody8",   lambda: melody(N, n_notes=8, n_harm=5)),
    ("melody6",   lambda: melody(N, n_notes=6, n_harm=6)),
    ("melody12",  lambda: melody(N, n_notes=12, n_harm=4)),
    ("chord3",    lambda: chord(N, n_notes=3, n_harm=5)),
    ("chord4",    lambda: chord(N, n_notes=4, n_harm=4)),
    ("sing",      lambda: singing_like(N)),
    ("sing+mel",  lambda: 0.6 * singing_like(N) + 0.4 * melody(N, n_notes=8)),
    ("mel+chord", lambda: 0.5 * melody(N, n_notes=8) + 0.5 * chord(N, n_notes=3)),
    ("guitar",    lambda: melody(N, n_notes=10, n_harm=7)),
    ("piano",     lambda: melody(N, n_notes=4, n_harm=8)),
]


# ---------------------------------------------------------------------------
# Write all 20 files
# ---------------------------------------------------------------------------

def main() -> None:
    for i, (tag, gen) in enumerate(NOISE_RECIPES, start=1):
        path = os.path.join(OUT_DIR, f"noise_{i:02d}.wav")
        write_wav(path, gen())
        print(f"  wrote {os.path.basename(path)}  [{tag}]")

    for i, (tag, gen) in enumerate(MUSIC_RECIPES, start=1):
        path = os.path.join(OUT_DIR, f"music_{i:02d}.wav")
        write_wav(path, gen())
        print(f"  wrote {os.path.basename(path)}  [{tag}]")


if __name__ == "__main__":
    main()
