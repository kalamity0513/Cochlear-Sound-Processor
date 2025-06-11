import numpy as np
'''
def apply_cis(fft_mags, freqs, fs, channels=16):
    nyquist = fs // 2
    channel_width = nyquist // channels
    ftm = np.zeros((channels, fft_mags.shape[0]))

    for ch in range(channels):
        band_start = ch * channel_width
        band_end = (ch + 1) * channel_width
        bin_idx = (freqs >= band_start) & (freqs < band_end)
        if np.any(bin_idx):
            ftm[ch, :] = np.max(fft_mags[:, bin_idx], axis=1)

    return ftm
'''
def apply_cis(fft_mags, freqs, fs, channels=16):
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
        
        # 🧠 CIS stimulates *all* channels—no selection!
        ftm[:, frame_idx] = ch_amps

    return ftm
