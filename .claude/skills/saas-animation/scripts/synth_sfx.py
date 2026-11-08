# Makes a small free sound kit from scratch if there's no sound library: whooshes, pops, ticks, soft hits, risers and an air bed. They aren't as rich as a real library, but nothing is downloaded and it costs nothing. Usage: python3 synth_sfx.py <folder>, then pass that folder to mix.py with --lib.
import numpy as np, sys, os, wave
from scipy.signal import butter, sosfilt
SR = 48000
def save(name, x, folder):
    x = x / (np.abs(x).max() + 1e-9) * 0.9; s = np.stack([x, np.roll(x, 12)], 1); w = wave.open(os.path.join(folder, name + '.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((s * 32767).astype(np.int16).tobytes()); w.close()
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)
def band(x, lo, hi): return sosfilt(butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos'), x)
def tone(f, n, f2=None): ph = 2 * np.pi * np.cumsum(np.linspace(f, f2 or f, n)) / SR; return np.sin(ph)
def whoosh(dur, lo, hi, seed):
    n = int(dur * SR); rng = np.random.default_rng(seed); x = rng.standard_normal(n); b = np.zeros(n); seg = 256
    for i in range(0, n - seg, seg): u = i / n; f = lo + (hi - lo) * np.sin(np.pi * u); b[i:i + seg * 2] += band(x[i:i + seg * 2], max(f * 0.6, 40), min(f * 1.4, 20000)) * np.hanning(min(seg * 2, n - i))
    return b * np.sin(np.pi * np.arange(n) / n) ** 2
def main(folder):
    os.makedirs(folder, exist_ok=True); rng = np.random.default_rng(1)
    for i, (d, lo, hi) in enumerate([(0.35, 500, 5000), (0.6, 300, 3500), (1.0, 200, 2500)]): save(f'Synth Whoosh {i + 1}', whoosh(d, lo, hi, i), folder)
    n = int(0.18 * SR); save('Synth Pop', tone(620, n, 180) * env(n, 0.002, 0.035), folder); save('Synth Tick', band(rng.standard_normal(n // 3), 2500, 9000) * env(n // 3, 0.0005, 0.006) + tone(1800, n // 3) * env(n // 3, 0.0005, 0.01) * 0.5, folder)
    n = int(0.9 * SR); save('Synth Soft Hit', tone(120, n, 42) * env(n, 0.002, 0.2), folder); save('Synth Shutter', band(rng.standard_normal(int(0.08 * SR)), 1500, 8000) * env(int(0.08 * SR), 0.001, 0.015), folder)
    n = int(2.5 * SR); u = np.arange(n) / n; save('Synth Riser', (band(rng.standard_normal(n), 800, 7000) * 0.5 + tone(110, n, 440) * 0.5) * u ** 2.5, folder)
    n = int(4 * SR); save('Synth Air Bed', band(rng.standard_normal(n), 1200, 9000) * np.minimum(np.minimum(np.arange(n), n - np.arange(n)) / (0.5 * SR), 1), folder); print('Wrote the sound kit to', folder)
main(sys.argv[1])
