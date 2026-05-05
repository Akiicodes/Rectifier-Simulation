import numpy as np

def generate_wave(frequency, amplitude, duration=0.1, sampling_rate=10000):
    """Generates a sinusoidal AC wave."""
    t = np.linspace(0, duration, int(sampling_rate * duration))
    v_in = amplitude * np.sin(2 * np.pi * frequency * t)
    return t, v_in

def half_wave_rectifier(v_in):
    """Simulates a half-wave rectifier by passing only positive half cycles."""
    return np.maximum(0, v_in)

def full_wave_rectifier(v_in):
    """Simulates a full-wave rectifier by passing positive and inverting negative half cycles."""
    return np.abs(v_in)
