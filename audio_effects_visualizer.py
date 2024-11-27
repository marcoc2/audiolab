import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pedalboard import Pedalboard, Chorus, Phaser, Delay
import sounddevice as sd
import soundfile as sf
from scipy.fft import fft, fftfreq

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        self.bind_mouse_wheel(canvas)
        
    def bind_mouse_wheel(self, widget):
        widget.bind('<Enter>', lambda e: widget.bind_all('<MouseWheel>', self._on_mousewheel))
        widget.bind('<Leave>', lambda e: widget.unbind_all('<MouseWheel>'))
        
    def _on_mousewheel(self, event):
        self.scrollable_frame.update_idletasks()
        canvas = self.winfo_children()[0]
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class AudioEffectsVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Effects Visualizer")
        
        # Configurar o redimensionamento da janela
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Criar frame principal com scrollbar
        self.main_scroll = ScrollableFrame(root)
        self.main_scroll.grid(row=0, column=0, sticky="nsew")
        
        # Frame principal dentro do scrollable frame
        self.main_frame = self.main_scroll.scrollable_frame
        
        # Configuração inicial
        self.sample_rate = 44100
        self.duration = 2
        self.t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
        self.frequency = 440
        
        # Gerar sinal de teste
        self.test_signal = np.sin(2 * np.pi * self.frequency * self.t)
        self.processed_signal = self.test_signal.copy()
        self.is_sine_wave = True
        
        # Configurar pedalboard
        self.board = Pedalboard([])
        
        # Criar interface
        self.setup_gui()
        
        # Ajustar tamanho inicial da janela
        self.root.update_idletasks()
        screen_height = self.root.winfo_screenheight()
        window_height = min(self.main_frame.winfo_reqheight(), screen_height * 0.9)
        self.root.geometry(f"800x{int(window_height)}")
        
    def setup_gui(self):
        # Frame para controles (lado esquerdo)
        controls_container = ttk.Frame(self.main_frame)
        controls_container.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        
        # Frame para gráficos (lado direito)
        graphs_container = ttk.Frame(self.main_frame)
        graphs_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # === Controles (Esquerda) ===
        # Input controls
        input_frame = ttk.LabelFrame(controls_container, text="Entrada de Áudio")
        input_frame.pack(fill="x", pady=5)
        
        # Frequência
        freq_frame = ttk.Frame(input_frame)
        freq_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(freq_frame, text="Freq (Hz):").pack(side="left")
        self.freq_var = tk.DoubleVar(value=440)
        self.freq_label = ttk.Label(freq_frame, text="440")
        self.freq_label.pack(side="right")
        
        def update_freq(val):
            self.freq_label.config(text=f"{float(val):.1f}")
            self.frequency = float(val)
            if self.is_sine_wave:
                self.update_sine_wave()
        
        freq_slider = ttk.Scale(input_frame, from_=20, to=2000, variable=self.freq_var,
                              orient="horizontal", command=update_freq)
        freq_slider.pack(fill="x", padx=5, pady=2)
        
        # Botões de arquivo
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill="x", padx=5, pady=2)
        ttk.Button(file_frame, text="Carregar Arquivo", 
                  command=self.load_audio_file).pack(side="left", padx=2)
        ttk.Button(file_frame, text="Usar Senoidal", 
                  command=self.use_sine_wave).pack(side="left", padx=2)
        
        # Efeitos
        effect_frame = ttk.LabelFrame(controls_container, text="Efeitos")
        effect_frame.pack(fill="x", pady=5)
        
        ttk.Label(effect_frame, text="Tipo:").pack(padx=5, pady=2)
        self.effect_var = tk.StringVar(value="none")
        effects = ttk.Combobox(effect_frame, textvariable=self.effect_var)
        effects['values'] = ('none', 'chorus', 'phaser', 'delay')
        effects.pack(padx=5, pady=2, fill="x")
        effects.bind('<<ComboboxSelected>>', self.update_effect)
        
        # Parâmetros
        self.params_frame = ttk.LabelFrame(controls_container, text="Parâmetros")
        self.params_frame.pack(fill="x", pady=5)
        
        # Botões de controle
        control_frame = ttk.LabelFrame(controls_container, text="Controles")
        control_frame.pack(fill="x", pady=5)
        
        ttk.Button(control_frame, text="Tocar Original", 
                  command=self.play_original).pack(fill="x", padx=5, pady=2)
        ttk.Button(control_frame, text="Tocar Processado", 
                  command=self.play_processed).pack(fill="x", padx=5, pady=2)
        ttk.Button(control_frame, text="Parar", 
                  command=self.stop_audio).pack(fill="x", padx=5, pady=2)
        
        # === Gráficos (Direita) ===
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(8, 8))
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def load_audio_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg")])
        if file_path:
            self.is_sine_wave = False
            audio_data, sample_rate = sf.read(file_path)
            # Converter para mono se for estéreo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            # Normalizar o áudio
            audio_data = audio_data / np.max(np.abs(audio_data))
            # Ajustar o tamanho para 2 segundos
            target_length = int(self.sample_rate * self.duration)
            if len(audio_data) > target_length:
                self.test_signal = audio_data[:target_length]
            else:
                self.test_signal = np.pad(audio_data, (0, target_length - len(audio_data)))
            self.update_visualization()

    def use_sine_wave(self):
        self.is_sine_wave = True
        self.update_sine_wave()

    def update_sine_wave(self):
        self.test_signal = np.sin(2 * np.pi * self.frequency * self.t)
        self.update_visualization()
        
    def update_effect(self, event=None):
        # Limpar parâmetros anteriores
        for widget in self.params_frame.winfo_children():
            widget.destroy()
            
        effect = self.effect_var.get()
        self.current_params = {}
        
        if effect == 'chorus':
            params = {
                'rate_hz': (0.1, 10, 1),
                'depth': (0.1, 1, 0.5),
                'centre_delay_ms': (1, 20, 7),
                'feedback': (0, 1, 0.1)
            }
        elif effect == 'phaser':
            params = {
                'rate_hz': (0.1, 10, 1),
                'depth': (0, 1, 0.5),
                'feedback': (0, 1, 0.1)
            }
        elif effect == 'delay':
            params = {
                'delay_seconds': (0.1, 1, 0.3),
                'feedback': (0, 1, 0.3),
                'mix': (0, 1, 0.5)
            }
        else:
            return
            
        # Criar sliders e labels para os parâmetros
        for i, (param, (min_val, max_val, default)) in enumerate(params.items()):
            param_frame = ttk.Frame(self.params_frame)
            param_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5)
            
            ttk.Label(param_frame, text=param).grid(row=0, column=0, padx=5)
            value_label = ttk.Label(param_frame, text=f"{default:.2f}")
            value_label.grid(row=0, column=2, padx=5)
            
            var = tk.DoubleVar(value=default)
            
            def update_value(val, label=value_label, v=var):
                label.config(text=f"{float(val):.2f}")
                self.update_visualization()
            
            slider = ttk.Scale(param_frame, from_=min_val, to=max_val, variable=var,
                             orient=tk.HORIZONTAL, length=200,
                             command=update_value)
            slider.grid(row=0, column=1, padx=5)
            
            self.current_params[param] = var
    
    def compute_spectrum(self, signal):
        n = len(signal)
        yf = fft(signal)
        xf = fftfreq(n, 1 / self.sample_rate)
        # Retornar apenas a primeira metade do espectro (frequências positivas)
        return xf[:n//2], np.abs(yf[:n//2])
    
    def apply_effect(self):
        effect = self.effect_var.get()
        if effect == 'none':
            self.processed_signal = self.test_signal.copy()
            return self.processed_signal
            
        self.board = Pedalboard([])
        params = {k: v.get() for k, v in self.current_params.items()}
        
        if effect == 'chorus':
            self.board.append(Chorus(**params))
        elif effect == 'phaser':
            self.board.append(Phaser(**params))
        elif effect == 'delay':
            self.board.append(Delay(**params))
            
        self.processed_signal = self.board(self.test_signal, self.sample_rate)
        return self.processed_signal
    
    def update_visualization(self):
        # Limpar gráficos
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        # Processar sinal
        processed_signal = self.apply_effect()
        
        # Calcular espectros
        xf_orig, yf_orig = self.compute_spectrum(self.test_signal)
        xf_proc, yf_proc = self.compute_spectrum(processed_signal)
        
        # Plotar formas de onda
        self.ax1.plot(self.t[:1000], self.test_signal[:1000], label='Original')
        self.ax1.set_title('Forma de Onda Original')
        self.ax1.set_xlabel('Tempo (s)')
        self.ax1.set_ylabel('Amplitude')
        self.ax1.grid(True)
        self.ax1.legend()
        
        self.ax2.plot(self.t[:1000], processed_signal[:1000], label='Processado', color='red')
        self.ax2.set_title('Forma de Onda Processada')
        self.ax2.set_xlabel('Tempo (s)')
        self.ax2.set_ylabel('Amplitude')
        self.ax2.grid(True)
        self.ax2.legend()
        
        # Plotar espectros
        self.ax3.plot(xf_orig[:5000], yf_orig[:5000], label='Original', alpha=0.5)
        self.ax3.plot(xf_proc[:5000], yf_proc[:5000], label='Processado', color='red', alpha=0.5)
        self.ax3.set_title('Espectro de Frequência')
        self.ax3.set_xlabel('Frequência (Hz)')
        self.ax3.set_ylabel('Magnitude')
        self.ax3.set_xscale('log')
        self.ax3.set_yscale('log')
        self.ax3.grid(True)
        self.ax3.legend()
        
        self.canvas.draw()

    def play_original(self):
        self.stop_audio()
        sd.play(self.test_signal, self.sample_rate)

    def play_processed(self):
        self.stop_audio()
        sd.play(self.processed_signal, self.sample_rate)

    def stop_audio(self):
        sd.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEffectsVisualizer(root)
    root.mainloop()