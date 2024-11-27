"""Processamento de áudio e efeitos."""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
import soundfile as sf
import sounddevice as sd
from pedalboard import Pedalboard

from ..utils.config import SAMPLE_RATE, DURATION

class AudioProcessor:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.duration = DURATION
        self.t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        self.board = Pedalboard([])
        self.reset_signals()

    def reset_signals(self):
        """Reinicia os sinais para o estado inicial."""
        self.frequency = 440
        self.test_signal = np.sin(2 * np.pi * self.frequency * self.t)
        self.processed_signal = self.test_signal.copy()

    def load_file(self, file_path):
        """Carrega um arquivo de áudio."""
        audio_data, _ = sf.read(file_path)
        
        # Converter para mono se for estéreo
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Normalizar
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Ajustar tamanho
        target_length = int(self.sample_rate * self.duration)
        if len(audio_data) > target_length:
            self.test_signal = audio_data[:target_length]
        else:
            self.test_signal = np.pad(audio_data, (0, target_length - len(audio_data)))

    def update_sine_wave(self, frequency):
        """Atualiza o sinal senoidal com nova frequência."""
        self.frequency = frequency
        self.test_signal = np.sin(2 * np.pi * self.frequency * self.t)

    def compute_spectrum(self, signal_data):
        """Calcula o espectro do sinal."""
        n = len(signal_data)
        yf = fft(signal_data)
        xf = fftfreq(n, 1 / self.sample_rate)
        return xf[:n//2], np.abs(yf[:n//2])

    def compute_spectrogram(self, signal_data):
        """Calcula o espectrograma do sinal."""
        return signal.spectrogram(
            signal_data,
            fs=self.sample_rate,
            nperseg=1024,
            noverlap=512,
            scaling='spectrum'
        )

    def play(self, signal_data):
        """Reproduz o áudio."""
        sd.stop()  # Para qualquer reprodução anterior
        sd.play(signal_data, self.sample_rate)

    def stop(self):
        """Para a reprodução."""
        sd.stop()
