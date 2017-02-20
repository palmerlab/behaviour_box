from __future__ import division
import numpy as np

def band_limited_noise(min_freq, max_freq, samples=1024, samplerate=1):

    '''
    Generates noise within a particular band of frequencies
    '''

    freqs = np.abs(np.fft.fftfreq(samples, float(1)/samplerate))
    f = np.zeros(samples)
    idx = np.where(np.logical_and(freqs>=min_freq, freqs<=max_freq))[0]
    f[idx] = 1
    return fftnoise(f)

def fftnoise(f):
    '''?? filter used in band_limited_noise'''
    f = np.array(f, dtype='complex')
    Np = (len(f) - 1) // 2
    phases = np.random.rand(Np) * 2 * np.pi
    phases = np.cos(phases) + 1j * np.sin(phases)
    f[1:Np+1] *= phases
    f[-1:-1-Np:-1] = np.conj(f[1:Np+1])
    return np.fft.ifft(f).real