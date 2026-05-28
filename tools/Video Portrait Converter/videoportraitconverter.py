import subprocess
import os
from tkinter import Tk, filedialog, messagebox

def processar_video(input_path, output_path, resolucao):
    # Comando FFmpeg para redimensionar o vídeo para a resolução especificada
    command = [
        "ffmpeg", "-i", input_path, "-vf", f"scale={resolucao}",
        "-c:a", "copy", output_path
    ]
    
    # Executa o comando FFmpeg
    subprocess.run(command)

def processar_videos(videos_selecionados, pasta_saida):
    for video_path in videos_selecionados:
        # Extrai o nome do arquivo sem a extensão
        nome_video = os.path.splitext(os.path.basename(video_path))[0]

        # Cria uma pasta para o vídeo com base no nome
        pasta_video = os.path.join(pasta_saida, nome_video)
        os.makedirs(pasta_video, exist_ok=True)

        # Definindo a resolução de retrato (1080x1350)
        resolucao = "1080x1350"

        # Cria a versão retrato do vídeo
        output_video = os.path.join(pasta_video, f"{nome_video}_Retrato.mp4")
        try:
            processar_video(video_path, output_video, resolucao)
            print(f"Versão Retrato do vídeo criada com sucesso: {output_video}")
        except Exception as e:
            print(f"Erro ao processar Retrato para o vídeo {nome_video}: {e}")

def escolher_videos():
    # Cria a janela para selecionar os vídeos a serem processados
    root = Tk()
    root.withdraw()  # Oculta a janela principal
    arquivos = filedialog.askopenfilenames(
        title="Selecione os vídeos para processar", 
        filetypes=[("Arquivos de vídeo", "*.mp4;*.mov;*.avi;*.mkv")]
    )
    return arquivos

def selecionar_pasta_saida():
    # Cria a janela para selecionar a pasta de saída
    root = Tk()
    root.withdraw()  # Oculta a janela principal
    pasta_saida = filedialog.askdirectory(title="Selecione a pasta para salvar os vídeos processados")
    return pasta_saida

def main():
    # Solicita os vídeos a serem processados
    videos_selecionados = escolher_videos()
    if not videos_selecionados:
        messagebox.showerror("Erro", "Nenhum vídeo selecionado.")
        return

    # Solicita a pasta de saída
    pasta_saida = selecionar_pasta_saida()
    if not pasta_saida:
        messagebox.showerror("Erro", "Nenhuma pasta de saída selecionada.")
        return

    # Processa os vídeos selecionados e gera a versão retrato
    processar_videos(videos_selecionados, pasta_saida)
    messagebox.showinfo("Concluído", "Processamento de vídeos concluído!")

if __name__ == "__main__":
    main()
