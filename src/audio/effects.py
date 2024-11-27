"""Gerenciamento de efeitos de áudio."""

from pedalboard import Pedalboard, Chorus, Phaser, Delay

class EffectsManager:
    def __init__(self):
        self.board = Pedalboard([])
        self.current_effect = None
        self.effect_params = {}
        
        # Definição dos parâmetros para cada efeito
        self.effects_config = {
            'chorus': {
                'class': Chorus,
                'params': {
                    'rate_hz': (0.1, 10, 1),      # (min, max, default)
                    'depth': (0.1, 1, 0.5),
                    'centre_delay_ms': (1, 20, 7),
                    'feedback': (0, 1, 0.1)
                }
            },
            'phaser': {
                'class': Phaser,
                'params': {
                    'rate_hz': (0.1, 10, 1),
                    'depth': (0, 1, 0.5),
                    'feedback': (0, 1, 0.1)
                }
            },
            'delay': {
                'class': Delay,
                'params': {
                    'delay_seconds': (0.1, 1, 0.3),
                    'feedback': (0, 1, 0.3),
                    'mix': (0, 1, 0.5)
                }
            }
        }

    def get_effect_params(self, effect_name):
        """Retorna os parâmetros configuráveis para um efeito."""
        if effect_name in self.effects_config:
            return self.effects_config[effect_name]['params']
        return {}

    def set_effect(self, effect_name, params=None):
        """Configura um novo efeito com os parâmetros especificados."""
        self.board = Pedalboard([])
        
        if effect_name == 'none' or effect_name not in self.effects_config:
            self.current_effect = None
            return
            
        effect_class = self.effects_config[effect_name]['class']
        effect_params = params or {
            name: default for name, (_, _, default) in 
            self.effects_config[effect_name]['params'].items()
        }
        
        self.board.append(effect_class(**effect_params))
        self.current_effect = effect_name
        self.effect_params = effect_params

    def process_audio(self, audio_data, sample_rate):
        """Processa o áudio com o efeito atual."""
        if self.current_effect is None:
            return audio_data
        return self.board(audio_data, sample_rate)

    def get_available_effects(self):
        """Retorna lista de efeitos disponíveis."""
        return ['none'] + list(self.effects_config.keys())
