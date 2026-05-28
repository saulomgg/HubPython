# Audio Generator v0.1 - Developed by saulomg2, featured on stampsynk.com
# This program generates binaural beats using customizable frequencies, waveforms, and optional background sounds.
# Users can adjust stereo panning, volume, and playback settings for a personalized audio experience.
# Built with Tkinter for UI, Pydub for audio processing, and Pygame for real-time preview.

import os
from tkinter import Tk, Label, Button, StringVar, OptionMenu, IntVar, Entry, filedialog, Scale, Checkbutton
from pydub import AudioSegment
from pydub.generators import Sine, Square, Triangle, WhiteNoise
import pygame
import io

# Tipos de ondas disponíveis
wave_types = {
    "Senoidal": Sine,
    "Quadrada": Square,
    "Triangular": Triangle,
    "Ruído Branco": WhiteNoise
}

# Estado do áudio
audio_playing = False  # Variável que controla o estado do áudio (tocado ou pausado)

# Função para escolher o diretório de saída
def escolher_diretorio():
    pasta = filedialog.askdirectory(title="Escolha o diretório para salvar o áudio")
    return pasta

# Função para escolher o arquivo de som de fundo
def escolher_som_fundo():
    arquivo_som_fundo = filedialog.askopenfilename(title="Escolha o arquivo de som de fundo")
    return arquivo_som_fundo

# Função para criar o áudio
def criar_audio():
    try:
        freq_esquerdo = int(var_frequencia_esquerdo.get())
        freq_direito = int(var_frequencia_direito.get())
    except ValueError:
        status_label.config(text="Digite uma frequência válida.")
        return

    # Validar as frequências
    if freq_esquerdo < 0 or freq_direito < 0:
        status_label.config(text="Frequência não pode ser negativa.")
        return

    # Diferença de Frequência
    diff = abs(freq_esquerdo - freq_direito)

    if diff == 0:
        status_label.config(text="A frequência dos canais não pode ser igual.")
        return

    onda_esquerdo = wave_types[var_onda_esquerdo.get()]
    onda_direito = wave_types[var_onda_direito.get()]
    som_fundo = var_som_fundo.get()
    duracao = int(var_duracao.get()) * 1000  # Converter para milissegundos
    nome_audio = var_nome_audio.get()
    diretorio = escolher_diretorio()

    if not diretorio:
        status_label.config(text="Nenhum diretório selecionado.")
        return

    if not nome_audio:
        status_label.config(text="Digite um nome para o arquivo.")
        return

    # Gerar ondas para os canais esquerdo e direito
    print("Gerando áudio...")

    left_tone = onda_esquerdo(freq_esquerdo).to_audio_segment(duration=duracao)
    right_tone = onda_direito(freq_direito).to_audio_segment(duration=duracao)

    # Ajustar volume de cada canal
    left_tone = left_tone + var_volume_esquerdo.get()
    right_tone = right_tone + var_volume_direito.get()

    # Criar o efeito de movimento do som (panning)
    panned_audio = AudioSegment.silent(duration=duracao)  # Áudio silencioso para trabalhar os efeitos

    # Aplicar panning dinâmico
    panned_left = left_tone.pan(-1)  # Canal esquerdo no extremo esquerdo
    panned_right = right_tone.pan(1)  # Canal direito no extremo direito
    panned_audio = panned_left.overlay(panned_right)

    # Inverter estéreo, se necessário
    if var_inverter_estereo.get():
        left_tone, right_tone = right_tone, left_tone

    # Combinar os canais em estéreo
    binaural_audio = AudioSegment.from_mono_audiosegments(left_tone, right_tone)

    # Adicionar som de fundo
    if som_fundo != "Nenhum":
        try:
            background = AudioSegment.from_file(som_fundo)
            background = background - 10

            repeat_count = duracao // len(background) + 1
            background_repeated = background * repeat_count
            background_repeated = background_repeated[:duracao]

            binaural_audio = binaural_audio.overlay(background_repeated)
        except FileNotFoundError:
            status_label.config(text="Arquivo de som de fundo não encontrado.")
            return

    # Salvar o arquivo
    output_file = os.path.join(diretorio, f"{nome_audio}.mp3")
    binaural_audio.export(output_file, format="mp3", bitrate="192k")
    status_label.config(text=f"Áudio gerado com sucesso: {output_file}")

# Função para pré-visualizar o áudio diretamente
def preview_audio():
    global audio_playing

    try:
        freq_esquerdo = int(var_frequencia_esquerdo.get())
        freq_direito = int(var_frequencia_direito.get())
    except ValueError:
        status_label.config(text="Digite uma frequência válida.")
        return

    # Gerar o áudio como na criação
    onda_esquerdo = wave_types[var_onda_esquerdo.get()]
    onda_direito = wave_types[var_onda_direito.get()]
    som_fundo = var_som_fundo.get()
    duracao = int(var_duracao.get()) * 1000  # Converter para milissegundos

    left_tone = onda_esquerdo(freq_esquerdo).to_audio_segment(duration=duracao)
    right_tone = onda_direito(freq_direito).to_audio_segment(duration=duracao)

    # Ajustar volume de cada canal
    left_tone = left_tone + var_volume_esquerdo.get()
    right_tone = right_tone + var_volume_direito.get()

    # Criar o efeito de movimento do som (panning)
    panned_audio = AudioSegment.silent(duration=duracao)  # Áudio silencioso para trabalhar os efeitos

    # Aplicar panning dinâmico
    panned_left = left_tone.pan(-1)  # Canal esquerdo no extremo esquerdo
    panned_right = right_tone.pan(1)  # Canal direito no extremo direito
    panned_audio = panned_left.overlay(panned_right)

    # Adicionar som de fundo
    if som_fundo != "Nenhum":
        try:
            background = AudioSegment.from_file(som_fundo)
            background = background - 10

            repeat_count = duracao // len(background) + 1
            background_repeated = background * repeat_count
            background_repeated = background_repeated[:duracao]

            panned_audio = panned_audio.overlay(background_repeated)
        except FileNotFoundError:
            status_label.config(text="Arquivo de som de fundo não encontrado.")
            return

    # Reproduzir o áudio gerado diretamente na memória
    panned_audio = panned_audio.set_frame_rate(44100)
    panned_audio = panned_audio.set_channels(2)

    # Converte o áudio para um formato que o pygame pode tocar
    audio_data = io.BytesIO()
    panned_audio.export(audio_data, format="wav")
    audio_data.seek(0)  # Voltar ao início do arquivo para leitura

    # Inicializar o mixer do pygame
    pygame.mixer.init(frequency=44100)
    pygame.mixer.music.load(audio_data)

    # Verifica o estado do áudio
    if audio_playing:
        pygame.mixer.music.pause()  # Pausa o áudio
        play_button.config(text="Play")  # Atualiza o texto do botão para Play
        audio_playing = False  # Atualiza o estado do áudio
    else:
        pygame.mixer.music.play()  # Toca o áudio
        play_button.config(text="Pause")  # Atualiza o texto do botão para Pause
        audio_playing = True  # Atualiza o estado do áudio

# Interface gráfica
root = Tk()
root.title("Gerador de Áudio Binaural")
root.geometry("400x600")

# Frequências para o canal esquerdo
Label(root, text="Frequência Canal Esquerdo (em Hz):").pack()
var_frequencia_esquerdo = StringVar(root)
var_frequencia_esquerdo.set("440")  # Valor padrão
Entry(root, textvariable=var_frequencia_esquerdo).pack()

# Tipo de onda para o canal esquerdo
Label(root, text="Onda Canal Esquerdo:").pack()
var_onda_esquerdo = StringVar(root)
var_onda_esquerdo.set("Senoidal")  # Valor padrão
OptionMenu(root, var_onda_esquerdo, *wave_types.keys()).pack()

# Frequências para o canal direito
Label(root, text="Frequência Canal Direito (em Hz):").pack()
var_frequencia_direito = StringVar(root)
var_frequencia_direito.set("440")  # Valor padrão
Entry(root, textvariable=var_frequencia_direito).pack()

# Tipo de onda para o canal direito
Label(root, text="Onda Canal Direito:").pack()
var_onda_direito = StringVar(root)
var_onda_direito.set("Senoidal")  # Valor padrão
OptionMenu(root, var_onda_direito, *wave_types.keys()).pack()

# Som de fundo
Label(root, text="Som de Fundo:").pack()
var_som_fundo = StringVar(root)
var_som_fundo.set("Nenhum")  # Valor padrão
Button(root, text="Escolher Arquivo de Som de Fundo", command=lambda: var_som_fundo.set(escolher_som_fundo())).pack()

# Duração do áudio
Label(root, text="Duração (segundos):").pack()
var_duracao = IntVar(root)
var_duracao.set(30)  # Valor padrão
Entry(root, textvariable=var_duracao).pack()

# Volume
Label(root, text="Volume Canal Esquerdo:").pack()
var_volume_esquerdo = IntVar(root)
var_volume_esquerdo.set(0)  # Valor padrão
Scale(root, from_=-20, to=20, orient="horizontal", variable=var_volume_esquerdo).pack()

Label(root, text="Volume Canal Direito:").pack()
var_volume_direito = IntVar(root)
var_volume_direito.set(0)  # Valor padrão
Scale(root, from_=-20, to=20, orient="horizontal", variable=var_volume_direito).pack()

# Inverter Estéreo
var_inverter_estereo = IntVar(root)
Checkbutton(root, text="Inverter Estéreo", variable=var_inverter_estereo).pack()

# Nome do arquivo
Label(root, text="Nome do Áudio:").pack()
var_nome_audio = StringVar(root)
var_nome_audio.set("audio_binaural")  # Valor padrão
Entry(root, textvariable=var_nome_audio).pack()

# Botão para criar o áudio
Button(root, text="Gerar Áudio", command=criar_audio).pack()

# Botão de Play/Pause
play_button = Button(root, text="Play", command=preview_audio)
play_button.pack()

# Status da criação
status_label = Label(root, text="")
status_label.pack()

root.mainloop()
