import numpy as np

def apply_ace(fft_mags, freqs, fs, channels=16, N=2):
    nyquist = fs // 2
    channel_width = nyquist // channels
    ftm = np.zeros((channels, fft_mags.shape[0]))

    for frame_idx in range(fft_mags.shape[0]):
        ch_amps = np.zeros(channels)
        for ch in range(channels):
            band_start = ch * channel_width
            band_end = (ch + 1) * channel_width
            bin_idx = (freqs >= band_start) & (freqs < band_end)
            if np.any(bin_idx):
                ch_amps[ch] = np.max(fft_mags[frame_idx, bin_idx])
        top_ch = np.argsort(ch_amps)[-N:]
        ftm[:, frame_idx] = 0
        ftm[top_ch, frame_idx] = ch_amps[top_ch]

    return ftm


