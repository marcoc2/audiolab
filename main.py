"""Ponto de entrada do programa."""

import tkinter as tk
from src.audio.processor import AudioProcessor
from src.audio.effects import EffectsManager
from src.gui.main_window import MainWindow

def main():
    # Criar instâncias dos componentes principais
    audio_processor = AudioProcessor()
    effects_manager = EffectsManager()
    
    # Criar janela principal
    root = tk.Tk()
    app = MainWindow(root, audio_processor, effects_manager)
    
    # Iniciar loop principal
    root.mainloop()

if __name__ == "__main__":
    main()