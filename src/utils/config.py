"""Configurações globais do aplicativo."""

SAMPLE_RATE = 44100
DURATION = 2  # segundos
WINDOW_SIZE = "800x600"

# Configurações de áudio
AUDIO_FILETYPES = [("Audio Files", "*.wav *.mp3 *.ogg")]
DEFAULT_FREQUENCY = 440  # Hz

# Configurações de visualização
PLOT_DPI = 100
PLOT_STYLE = 'dark_background'
COLORS = {
    'background': '#1c1c1c',
    'plot_background': '#2d2d2d',
    'original': '#00ff00',
    'processed': '#ff3366',
    'text': 'white',
    'grid': '#404040'
}
