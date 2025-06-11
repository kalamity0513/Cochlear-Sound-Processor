import numpy as np

def apply_f0f1f2(fft_mags, freqs, fs, channels=16):
    nyquist = fs // 2
    channel_width = nyquist // channels
    ftm = np.zeros((channels, fft_mags.shape[0]))

    for target_freq in [150, 500, 1500]:
        bin_idx = np.argmin(np.abs(freqs - target_freq))
        ch_idx = min(channels - 1, int(target_freq / channel_width))
        ftm[ch_idx, :] = fft_mags[:, bin_idx]

    return ftm
