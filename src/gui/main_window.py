"""Interface principal do aplicativo."""

import tkinter as tk
from tkinter import ttk, filedialog

from ..utils.config import WINDOW_SIZE, AUDIO_FILETYPES, DEFAULT_FREQUENCY
from .plots import AudioVisualizer

class MainWindow:
    def __init__(self, master, audio_processor, effects_manager):
        self.master = master
        self.audio_processor = audio_processor
        self.effects_manager = effects_manager
        
        # Configurar janela principal
        self.master.title("Audio Effects Visualizer")
        self.master.geometry(WINDOW_SIZE)
        
        # Configurar grid
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
        # Frame principal
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Criar interface
        self.setup_gui()
        
    def setup_gui(self):
        """Configura a interface gráfica."""
        # Frame de controles (esquerda)
        controls = ttk.Frame(self.main_frame)
        controls.grid(row=0, column=0, sticky="ns", padx=5)
        
        # Frame de plots (direita, expansível)
        plots = ttk.Frame(self.main_frame)
        plots.grid(row=0, column=1, sticky="nsew", padx=5)
        plots.grid_rowconfigure(0, weight=1)
        plots.grid_columnconfigure(0, weight=1)
        
        # Configurar visualizador
        self.visualizer = AudioVisualizer(plots)
        
        # Seção de entrada de áudio
        self._setup_input_section(controls)
        
        # Seção de efeitos
        self._setup_effects_section(controls)
        
        # Seção de controles de playback
        self._setup_playback_section(controls)
        
        # Primeira atualização
        self.update_visualization()
        
    def _setup_input_section(self, parent):
        """Configura a seção de entrada de áudio."""
        input_frame = ttk.LabelFrame(parent, text="Entrada de Áudio")
        input_frame.pack(fill="x", pady=5)
        
        # Controle de frequência
        freq_frame = ttk.Frame(input_frame)
        freq_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(freq_frame, text="Freq (Hz):").pack(side="left")
        self.freq_var = tk.DoubleVar(value=DEFAULT_FREQUENCY)
        self.freq_label = ttk.Label(freq_frame, text=str(DEFAULT_FREQUENCY))
        self.freq_label.pack(side="right")
        
        freq_slider = ttk.Scale(
            input_frame,
            from_=20,
            to=2000,
            variable=self.freq_var,
            orient="horizontal",
            command=self._on_frequency_change
        )
        freq_slider.pack(fill="x", padx=5, pady=2)
        
        # Botões de fonte de áudio
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Button(
            btn_frame,
            text="Carregar Arquivo",
            command=self._load_audio_file
        ).pack(side="left", padx=2)
        
        ttk.Button(
            btn_frame,
            text="Usar Senoidal",
            command=self._use_sine_wave
        ).pack(side="left", padx=2)
        
    def _setup_effects_section(self, parent):
        """Configura a seção de efeitos."""
        effect_frame = ttk.LabelFrame(parent, text="Efeitos")
        effect_frame.pack(fill="x", pady=5)
        
        # Seletor de efeito
        ttk.Label(effect_frame, text="Tipo:").pack(padx=5, pady=2)
        self.effect_var = tk.StringVar(value="none")
        effects = ttk.Combobox(
            effect_frame,
            textvariable=self.effect_var,
            values=self.effects_manager.get_available_effects()
        )
        effects.pack(padx=5, pady=2, fill="x")
        effects.bind('<<ComboboxSelected>>', self._on_effect_change)
        
        # Frame para parâmetros de efeitos
        self.params_frame = ttk.Frame(effect_frame)
        self.params_frame.pack(fill="x", pady=5)
        
    def _setup_playback_section(self, parent):
        """Configura a seção de controles de playback."""
        control_frame = ttk.LabelFrame(parent, text="Controles")
        control_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            control_frame,
            text="Tocar Original",
            command=self._play_original
        ).pack(fill="x", padx=5, pady=2)
        
        ttk.Button(
            control_frame,
            text="Tocar Processado",
            command=self._play_processed
        ).pack(fill="x", padx=5, pady=2)
        
        ttk.Button(
            control_frame,
            text="Parar",
            command=self._stop_playback
        ).pack(fill="x", padx=5, pady=2)
        
    def _on_frequency_change(self, value):
        """Callback para mudança de frequência."""
        freq = float(value)
        self.freq_label.config(text=f"{freq:.1f}")
        self.audio_processor.update_sine_wave(freq)
        self.update_visualization()
        
    def _on_effect_change(self, event=None):
        """Callback para mudança de efeito."""
        effect = self.effect_var.get()
        self._update_effect_params(effect)
        self.update_visualization()
        
    def _update_effect_params(self, effect_name):
        """Atualiza os controles de parâmetros do efeito."""
        # Limpar parâmetros anteriores
        for widget in self.params_frame.winfo_children():
            widget.destroy()
            
        # Obter novos parâmetros
        params = self.effects_manager.get_effect_params(effect_name)
        self.param_vars = {}
        
        # Criar controles para cada parâmetro
        for param, (min_val, max_val, default) in params.items():
            frame = ttk.Frame(self.params_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=param).pack(side="left", padx=5)
            value_label = ttk.Label(frame, text=f"{default:.2f}")
            value_label.pack(side="right", padx=5)
            
            var = tk.DoubleVar(value=default)
            self.param_vars[param] = var
            
            def make_callback(label, v):
                return lambda val: self._on_param_change(val, label, v)
            
            slider = ttk.Scale(
                frame,
                from_=min_val,
                to=max_val,
                variable=var,
                orient="horizontal",
                command=make_callback(value_label, var)
            )
            slider.pack(fill="x", padx=5)
            
        # Atualizar efeito
        if effect_name != 'none':
            params = {name: var.get() for name, var in self.param_vars.items()}
            self.effects_manager.set_effect(effect_name, params)
            
    def _on_param_change(self, value, label, var):
        """Callback para mudança de parâmetro de efeito."""
        value = float(value)
        label.config(text=f"{value:.2f}")
        
        # Atualizar efeito e visualização
        effect = self.effect_var.get()
        if effect != 'none':
            params = {name: v.get() for name, v in self.param_vars.items()}
            self.effects_manager.set_effect(effect, params)
            self.update_visualization()
            
    def _load_audio_file(self):
        """Carrega um arquivo de áudio."""
        file_path = filedialog.askopenfilename(filetypes=AUDIO_FILETYPES)
        if file_path:
            self.audio_processor.load_file(file_path)
            self.update_visualization()
            
    def _use_sine_wave(self):
        """Volta para o gerador de onda senoidal."""
        self.audio_processor.update_sine_wave(self.freq_var.get())
        self.update_visualization()
        
    def _play_original(self):
        """Reproduz o áudio original."""
        self.audio_processor.play(self.audio_processor.test_signal)
        
    def _play_processed(self):
        """Reproduz o áudio processado."""
        self.audio_processor.play(self.audio_processor.processed_signal)
        
    def _stop_playback(self):
        """Para a reprodução."""
        self.audio_processor.stop()
        
    def update_visualization(self):
        """Atualiza a visualização."""
        # Processar áudio
        self.audio_processor.processed_signal = self.effects_manager.process_audio(
            self.audio_processor.test_signal,
            self.audio_processor.sample_rate
        )
        
        # Calcular dados para visualização
        if len(self.audio_processor.test_signal) > 1000:
            spectrum_data = {
                'spectrogram': self.audio_processor.compute_spectrogram(self.audio_processor.processed_signal)
            }
        else:
            spectrum_data = {
                'spectrum': self.audio_processor.compute_spectrum(self.audio_processor.processed_signal)
            }
            
        # Atualizar plots
        self.visualizer.update_plots(
            self.audio_processor.t,
            self.audio_processor.test_signal,
            self.audio_processor.processed_signal,
            spectrum_data
        )
