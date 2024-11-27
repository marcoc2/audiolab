# Audio Effects Visualizer

Um visualizador interativo de efeitos de áudio desenvolvido em Python, que permite observar como diferentes efeitos (chorus, phaser, delay) afetam tanto a forma de onda quanto o espectro de frequência do som.

## Funcionalidades

- Gerador de onda senoidal com frequência ajustável
- Suporte para carregar arquivos de áudio (WAV, MP3, OGG)
- Efeitos de áudio disponíveis:
  - Chorus
  - Phaser
  - Delay
- Visualização em tempo real:
  - Forma de onda original
  - Forma de onda processada
  - Espectro de frequência comparativo
- Controles interativos para parâmetros dos efeitos
- Reprodução de áudio original e processado

## Requisitos

- Python 3.8+
- Bibliotecas Python listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/audio-effects-visualizer.git
cd audio-effects-visualizer
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute o programa:
```bash
python audio_effects_visualizer.py
```

2. Interface:
   - Use o slider de frequência para ajustar a onda senoidal
   - Carregue arquivos de áudio usando o botão "Carregar Arquivo"
   - Selecione diferentes efeitos no menu suspenso
   - Ajuste os parâmetros dos efeitos usando os sliders
   - Visualize as mudanças em tempo real nos gráficos
   - Use os botões de reprodução para ouvir o áudio original e processado

## Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.

## Agradecimentos

- [Pedalboard](https://github.com/spotify/pedalboard) - Biblioteca de efeitos de áudio da Spotify
- [Matplotlib](https://matplotlib.org/) - Biblioteca de visualização
- [NumPy](https://numpy.org/) - Processamento numérico
