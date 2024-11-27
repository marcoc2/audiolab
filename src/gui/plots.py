"""Gerenciamento de visualizações e gráficos."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ..utils.config import COLORS, PLOT_STYLE

class AudioVisualizer:
    def __init__(self, master):
        """Inicializa o visualizador de áudio."""
        plt.style.use(PLOT_STYLE)
        
        # Criar figura com tamanho relativo ao container
        self.fig = plt.figure(figsize=(10, 8))
        
        # Criar grid com espaço para colorbar
        gs = self.fig.add_gridspec(3, 2, width_ratios=[1, 0.05], height_ratios=[1, 1, 1])
        
        # Criar eixos principais
        self.ax1 = self.fig.add_subplot(gs[0, 0])
        self.ax2 = self.fig.add_subplot(gs[1, 0])
        self.ax3 = self.fig.add_subplot(gs[2, 0])
        
        # Criar eixo para colorbar
        self.cax = self.fig.add_subplot(gs[2, 1])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        
        # Configurar aparência inicial
        self.fig.set_facecolor(COLORS['background'])
        for ax in [self.ax1, self.ax2, self.ax3, self.cax]:
            ax.set_facecolor(COLORS['plot_background'])
            ax.tick_params(colors=COLORS['text'], which='both')
            for spine in ax.spines.values():
                spine.set_color(COLORS['text'])
        
        # Esconder eixo da colorbar inicialmente
        self.cax.set_visible(False)
        
        self.fig.tight_layout()
        self.current_colorbar = None
        self.resize_job = None

    def calculate_envelope(self, data, num_points=1000):
        """Calcula o envelope do sinal para visualização otimizada."""
        data_length = len(data)
        if data_length > num_points:
            segment_size = data_length // num_points
            envelope_max = np.zeros(num_points)
            envelope_min = np.zeros(num_points)
            
            for i in range(num_points):
                start = i * segment_size
                end = start + segment_size
                segment = data[start:end]
                envelope_max[i] = np.max(segment)
                envelope_min[i] = np.min(segment)
                
            return envelope_min, envelope_max
        return data, data

    def _plot_waveform(self, ax, t, env_min, env_max, title, color):
        """Plota uma forma de onda com envelope."""
        ax.fill_between(t, env_min, env_max, color=color, alpha=0.3)
        ax.plot(t, (env_min + env_max) / 2, color=color, linewidth=0.5, alpha=0.8)
        ax.set_title(f'Forma de Onda {title}', color=COLORS['text'], pad=10)
        ax.set_xlabel('Tempo (s)', color=COLORS['text'])
        ax.set_ylabel('Amplitude', color=COLORS['text'])
        ax.grid(True, alpha=0.2)
        ax.set_ylim(-1.1, 1.1)

    def _plot_spectrum(self, ax, spectrum_data):
        """Plota o espectro ou espectrograma."""
        ax.clear()
        self.cax.clear()
        
        if 'spectrogram' in spectrum_data:
            f, t, Sxx = spectrum_data['spectrogram']
            Sxx_db = 10 * np.log10(Sxx + 1e-10)
            img = ax.pcolormesh(t, f, Sxx_db, shading='gouraud', 
                              cmap='viridis', vmin=np.max(Sxx_db) - 60)
            
            # Usar o eixo dedicado para colorbar
            self.cax.set_visible(True)
            self.current_colorbar = self.fig.colorbar(img, cax=self.cax)
            self.current_colorbar.set_label('Intensidade (dB)', color=COLORS['text'])
            self.current_colorbar.ax.yaxis.set_tick_params(colors=COLORS['text'])
            ax.set_ylabel('Frequência (Hz)', color=COLORS['text'])
        else:
            self.cax.set_visible(False)
            xf, yf = spectrum_data['spectrum']
            ax.semilogy(xf[1:5000], yf[1:5000], color=COLORS['original'], 
                       alpha=0.5, label='Espectro')
            ax.legend(facecolor=COLORS['plot_background'], labelcolor=COLORS['text'])
            ax.set_ylabel('Magnitude', color=COLORS['text'])
        
        ax.set_title('Análise Espectral', color=COLORS['text'], pad=10)
        ax.set_xlabel('Tempo (s)' if 'spectrogram' in spectrum_data else 'Frequência (Hz)', 
                     color=COLORS['text'])
        ax.grid(True, alpha=0.2)

    def update_plots(self, t, original_signal, processed_signal, spectrum_data):
        """Atualiza todos os plots com novos dados."""
        # Calcular envelopes
        if len(original_signal) > 1000:
            t_points = np.linspace(0, t[-1], 1000)
            env_min_orig, env_max_orig = self.calculate_envelope(original_signal)
            env_min_proc, env_max_proc = self.calculate_envelope(processed_signal)
        else:
            t_points = t
            env_min_orig = env_max_orig = original_signal
            env_min_proc = env_max_proc = processed_signal

        # Limpar plots anteriores
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        # Plot 1: Forma de onda original
        self._plot_waveform(self.ax1, t_points, env_min_orig, env_max_orig, 
                           'Original', COLORS['original'])
        
        # Plot 2: Forma de onda processada
        self._plot_waveform(self.ax2, t_points, env_min_proc, env_max_proc, 
                           'Processada', COLORS['processed'])
        
        # Plot 3: Espectro ou Espectrograma
        self._plot_spectrum(self.ax3, spectrum_data)
        
        # Ajustar layout e desenhar
        self.fig.tight_layout()
        self.canvas.draw()

    def on_resize(self, event):
        """Manipula o evento de redimensionamento."""
        if self.resize_job is not None:
            self.canvas.get_tk_widget().after_cancel(self.resize_job)
        self.resize_job = self.canvas.get_tk_widget().after(100, lambda: self._do_resize(event))

    def _do_resize(self, event):
        """Executa o redimensionamento após delay."""
        w = event.width / self.fig.dpi
        h = event.height / self.fig.dpi
        
        if w > 0 and h > 0:
            self.fig.set_size_inches(w, h, forward=True)
            self.fig.tight_layout()
            self.canvas.draw()
        
        self.resize_job = None