import numpy as np

def vocoder(freqSamples, sampleLength, fs):
    """
    Recreates audible signals from a Frequency-Time Matrix (FTM) using sine wave carriers.
    """
    bw = int(fs / 2)  # Nyquist frequency
    channels = freqSamples.shape[0]

    # Carrier types
    carrierSine = 0
    carrierNoiseLinear = 1
    carrierNoiseRandom = 2
    carrierType = carrierSine

    # Get band info
    f = getBandInfo(fs)
    channelWidth = int(bw / channels)
    centreF = np.arange(0, bw, channelWidth)

    tmp = np.arange(0, sampleLength, 1 / fs)
    tc = np.zeros((1, tmp.shape[0]))
    tc[0, :] = tmp

    # Create carriers
    if carrierType == carrierSine:
        tmp = np.zeros((f[:, 0].shape[0], 1))
        tmp[:, 0] = f[:, 0]
        carrier = np.sin(2 * np.pi * tmp * tc)

    elif carrierType == carrierNoiseLinear:
        carrier = np.zeros((f.shape[0], tc.shape[1]))
        for n in range(carrier.shape[0]):
            fc = np.linspace(f[n, 1], f[n, 2], 10)
            temp = np.sum(np.sin(2 * np.pi * fc[:, None] * tc), axis=0)
            temp /= np.max(temp)
            carrier[n, :] = temp

    elif carrierType == carrierNoiseRandom:
        carrier = np.zeros((centreF.shape[0], tc.shape[1]))
        for n in range(carrier.shape[0]):
            fc = np.random.rand(10, 1) * (f[n, 2] - f[n, 1]) + f[n, 1]
            temp = np.sum(np.sin(2 * np.pi * fc * tc), axis=0)
            temp /= np.max(temp)
            carrier[n, :] = temp

    else:
        raise TypeError("Unknown carrier type")

    # Synthesise signal
    voc = []
    for n in range(freqSamples.shape[1]):
        sample = np.zeros(carrier.shape)
        for m in range(freqSamples.shape[0]):
            sample[m, :] = carrier[m, :] * freqSamples[m, n]
        voc += np.sum(sample, axis=0).tolist()

    result = np.array(voc)
    result /= np.max(np.abs(result))  # Normalize
    result *= 0.999  # Keep within WAV safe range
    return result


def getBandInfo(fs):
    """
    Returns a matrix describing the center frequency and band edges of each channel.
    """
    pts = 128
    firstBin = 3

    # Linear + logarithmic channel widths for 16 channels
    widths = [1, 1, 1, 2, 2, 2, 2, 2, 3, 4, 4, 5, 6, 7, 9, 11]
    channels = len(widths)
    channelWidth = fs / pts
    result = np.ndarray((channels, 4))

    for n in range(channels):
        center = channelWidth * (firstBin - 1 + (widths[n] - 1) / 2)
        result[n, 0] = center
        result[n, 1] = center - channelWidth * widths[n] / 2
        result[n, 2] = center + channelWidth * widths[n] / 2
        firstBin += widths[n]

    result[:, 3] = widths
    return result