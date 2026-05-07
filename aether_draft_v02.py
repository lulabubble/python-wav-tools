"""
Aether Engine v0.2 — Emergent Audio Synthesis Engine
====================================================
Compact Python engine for procedural audio generation.
Designed for Suno-style prompt-to-music workflows.

UPDATE PROCEDURE:
1. New version → compute SHA-256 of the file
2. Communicate hash to all users (separate from file)
3. If modifying current version: mark as DRAFT in filename
4. No draft → create new version

Core modules:
    L()  — Lorenz attractor chaos generator
    W()  — Walsh-Hadamard rhythm patterns
    F()  — Formant filter bank (3-band resonator)
    V()  — Voice/synth generator with vibrato
    E()  — ADSR-like envelope
    D()  — Multi-tap delay
    M()  — Stereo master (normalize + soft-clip)
    Wf() — WAV file writer with Android path detection

Usage:
    import aether_engine as ae
    import numpy as np
    np.random.seed(42)
    n = ae.N(5)
    x, y, z = ae.L(n)
    f = 220 + 80 * x
    ph = np.cumsum(2 * np.pi * f / ae.S)
    sig = np.sin(ph)
    sig = ae.F(sig, 800, 1200, 2500)
    L = sig * 0.7
    R = np.roll(sig, int(ae.S * 0.01)) * 0.7
    L = ae.D(L, [int(ae.S*0.08), int(ae.S*0.13)], [0.3, 0.2])
    R = ae.D(R, [int(ae.S*0.08), int(ae.S*0.13)], [0.3, 0.2])
    ae.Wf("output.wav", L, R)

License: MIT
"""

import numpy as np
import wave
import os

S = 44100


def N(dur):
    return int(S * dur)


def L(n_samples, dt=0.001, sigma=10, rho=28, beta=8/3):
    x, y, z = 0.1, 0.0, 0.0
    spm = max(1, int(1.0 / (S * dt)))
    n_phys = n_samples * spm
    lx = np.zeros(n_phys)
    ly = np.zeros(n_phys)
    lz = np.zeros(n_phys)
    for i in range(n_phys):
        lx[i], ly[i], lz[i] = x, y, z
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        x += dx * dt
        y += dy * dt
        z += dz * dt
    return lx[::spm][:n_samples], ly[::spm][:n_samples], lz[::spm][:n_samples]


def W(row_idx):
    H = np.array([
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, -1, 1, -1, 1, -1, 1, -1],
        [1, 1, -1, -1, 1, 1, -1, -1],
        [1, -1, -1, 1, 1, -1, -1, 1],
        [1, 1, 1, 1, -1, -1, -1, -1],
        [1, -1, 1, -1, -1, 1, -1, 1],
        [1, 1, -1, -1, -1, -1, 1, 1],
        [1, -1, -1, 1, -1, 1, 1, -1]
    ])
    return (H[row_idx % 8] + 1) // 2


def F(signal, f1, f2, f3):
    def _resonator(sig, fc, bw):
        r = np.exp(-np.pi * bw / S)
        c = np.cos(2 * np.pi * fc / S)
        y1 = y2 = 0.0
        out = np.zeros_like(sig)
        for i in range(len(sig)):
            y0 = (1 - r) * sig[i] + 2 * r * c * y1 - r * r * y2
            out[i] = y0
            y2, y1 = y1, y0
        return out
    return _resonator(_resonator(_resonator(signal, f1, 90), f2, 130), f3, 200)


def V(dur, f0, fm_rate, aspiration=0):
    n = N(dur)
    t = np.arange(n) / S
    f = f0 * (1 + 0.06 * np.sin(2 * np.pi * fm_rate * t))
    ph = np.cumsum(2 * np.pi * f / S)
    harmonics = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    noise = 1 + aspiration * np.random.randn(n)
    return harmonics * noise


def E(signal, attack=0.02, release=0.03):
    n = len(signal)
    env = np.ones(n)
    at = int(S * attack)
    rt = int(S * release)
    if at > 0:
        env[:at] = np.linspace(0, 1, at) ** 2
    if rt > 0 and n - rt > at:
        env[-rt:] = np.linspace(1, 0, rt) ** 2
    return signal * env


def D(signal, delays, decays):
    out = signal.copy()
    for d, dec in zip(delays, decays):
        if d < len(signal):
            out[d:] += signal[:-d] * dec
    return out


def M(left, right):
    stereo = np.column_stack((left, right))
    stereo -= np.mean(stereo, axis=0)
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo /= peak / 0.92
    return np.tanh(stereo * 1.2) * 0.95


def Wf(path, left, right):
    out_path = path if os.path.isdir("/storage/emulated/0/Download") else f"/mnt/agents/output/{os.path.basename(path)}"
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    except PermissionError:
        pass
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(S)
        audio = (M(left, right) * 32767).astype(np.int16)
        w.writeframes(audio.tobytes())
    print(f"Saved: {out_path}")
