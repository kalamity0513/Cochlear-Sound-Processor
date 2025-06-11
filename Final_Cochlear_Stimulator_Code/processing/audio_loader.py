import numpy as np
import soundfile as sf
from scipy.signal import resample
from scipy.signal.windows import hann 
from processing.strategy_f0f1f2 import apply_f0f1f2
from processing.strategy_cis import apply_cis
from processing.strategy_ace import apply_ace
import pandas as pd

def load_and_process_audio(wav_file, strategy_name, fs_target=16000):
    x, fs = sf.read(wav_file)

    if x.ndim == 2:
        print("Dimension Reduction")
        x = np.mean(x, axis=1)

    if fs != fs_target:
        x = resample(x, int(len(x) * fs_target / fs))
        fs = fs_target

    # x = x / np.max(np.abs(x)) if np.max(np.abs(x)) > 0 else x

    epoch_ms = 2
    overlap_ms = 6
    samples_per_epoch = int(epoch_ms * fs / 1000)
    overlap_samples = int(overlap_ms * fs / 1000)
    step = samples_per_epoch
    padded_len = (len(x) // step + 1) * step
    padded = np.zeros(padded_len)
    padded[:len(x)] = x

    num_frames = (padded_len - overlap_samples) // step
    frames = np.zeros((num_frames, samples_per_epoch))
    for i in range(num_frames):
        start = i * step
        frames[i, :] = padded[start: start + samples_per_epoch] * hann(samples_per_epoch)

    fft_mags = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(frames.shape[1], 1 / fs)

    if strategy_name == "F0F1F2":
        ftm = apply_f0f1f2(fft_mags, freqs, fs)
    elif strategy_name == "CIS":
        ftm = apply_cis(fft_mags, freqs, fs)
    elif strategy_name == "ACE":
        ftm = apply_ace(fft_mags, freqs, fs)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    ftm = np.clip(ftm / np.max(ftm) * 1024, 0, 1024)
    return x, fs, ftm

def compress_ftm_dB(ftm, c_level=1024, dynamic_range_db=10, save_path=None):
    amax = c_level
    amin = amax / (10**(dynamic_range_db / 20))  # e.g., 1024 / 3.162 ≈ 324
    
    # Apply compression: values below amin are zeroed, others are scaled
    ftm_compressed = np.clip(ftm, amin, amax)
    ftm_compressed = (ftm_compressed - amin) / (amax - amin) * amax
    ftm_compressed[ftm < amin] = 0  # explicitly zero anything below threshold

    # Save to CSV: 16 rows, 1 column per 2 ms epoch
    if save_path:
        pd.DataFrame(ftm_compressed).to_csv(save_path, index=False, header=False)

    return ftm_compressed


def load_and_process_audio2(wav_file, strategy_name, fs_target=16000):
    x, fs = sf.read(wav_file)

    # Convert to mono if stereo
    if x.ndim == 2:
        x = np.mean(x, axis=1)

    # Resample if needed
    if fs < 4000 or fs > 64000:
        raise ValueError("Sampling frequency out of supported range (4–64 kHz).")
    if fs != fs_target:
        x = resample(x, int(len(x) * fs_target / fs))
        fs = fs_target

    # Framing parameters: 6 ms Hann window, 2 ms step
    window_ms = 6
    step_ms = 2
    samples_per_window = int(window_ms * fs / 1000)
    step_samples = int(step_ms * fs / 1000)

    num_frames = (len(x) - samples_per_window) // step_samples + 1
    frames = np.zeros((num_frames, samples_per_window))
    window = hann(samples_per_window)

    for i in range(num_frames):
        start = i * step_samples
        frames[i, :] = x[start:start + samples_per_window] * window

    fft_mags = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(frames.shape[1], 1 / fs)

    # Apply the chosen strategy
    if strategy_name == "F0F1F2":
        ftm = apply_f0f1f2(fft_mags, freqs, fs)
    elif strategy_name == "CIS":
        ftm = apply_cis(fft_mags, freqs, fs)
    elif strategy_name == "ACE":
        ftm = apply_ace(fft_mags, freqs, fs)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    # Normalize to 10 dB dynamic range
    amax = 1024
    amin = amax / (10**(10 / 20))  # ~323
    ftm = np.clip(ftm, amin, amax)
    ftm = np.round(ftm).astype(int)

    return x, fs, ftm
