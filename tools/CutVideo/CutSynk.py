# CutSynk - Ferramenta de Corte Rápido de Vídeo (HubSynk)
# Baseado em VideoSynk_FFmpeg.py, adaptado para GUI com Tkinter.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import json
import threading
import re
import webbrowser
from pathlib import Path

# --- Style Configuration (Inspired by VcSynk.py) ---
BG_DARK = "#1e1e1e"
BG_MEDIUM = "#2b2b2b"
FG_LIGHT = "#ffffff"
COLOR_PRIMARY = "#2196F3"  # Azul
COLOR_SUCCESS = "#4CAF50"  # Verde
COLOR_ERROR = "#f44336"    # Vermelho
COLOR_ACCENT = "#FFC107"   # Amarelo (para seleção de arquivo)

# --- Text Strings ---
TITLE_WINDOW = "CutSynk - Ferramenta de Corte Rápido"
TITLE_MAIN = "CutSynk - Corte de Vídeo (FFmpeg)"
SELECT_FILE_BUTTON = "📁 Selecionar Arquivo de Vídeo"
CUT_BUTTON = "✂️ Cortar Vídeo"
STATUS_WAITING = "Pronto. Selecione um arquivo de vídeo."
STATUS_READY = "Arquivo carregado. Defina os tempos de corte."
STATUS_CUTTING = "Cortando vídeo... Por favor, aguarde."
STATUS_SUCCESS = "Corte concluído com sucesso!"
STATUS_ERROR = "ERRO: "
FOOTER_TEXT = "CutSynk é parte do ecossistema HubSynk."
HUB_LINK_TEXT = "Official HubSynk Tool - Visite nosso site"
HUB_LINK_URL = "https://hubsynk.pages.dev"

class CutSynkApp:
    def __init__(self, root):
        self.root = root
        self.root.title(TITLE_WINDOW)
        self.root.geometry("600x450")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        # Variáveis de estado
        self.input_file = None
        self.video_duration = None
        self.is_cutting = False

        # Variáveis Tkinter
        self.file_info_var = tk.StringVar(value="Nenhum arquivo selecionado")
        self.duration_info_var = tk.StringVar(value="Duração Total: --:--:--.---")
        self.start_time_var = tk.StringVar(value="00:00:00.000")
        self.end_time_var = tk.StringVar(value="00:00:00.000")
        self.status_var = tk.StringVar(value=STATUS_WAITING)

        # Configuração da UI
        self.setup_ui()
        self.check_ffmpeg_on_start()

    def check_ffmpeg_on_start(self):
        """Verifica se FFmpeg/FFprobe estão acessíveis no PATH."""
        if not self.check_ffmpeg():
            messagebox.showerror("Erro de Dependência", "FFmpeg/FFprobe não encontrado. Certifique-se de que estão instalados e no PATH.")
            self.root.destroy()
            return

    def check_ffmpeg(self):
        """Função auxiliar para verificar a presença de FFmpeg."""
        return subprocess.run(['ffmpeg', '-version'], capture_output=True).returncode == 0

    def setup_ui(self):
        # Configuração de Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG_MEDIUM)
        style.configure('TLabel', background=BG_MEDIUM, foreground=FG_LIGHT)
        style.configure('TButton', background=COLOR_PRIMARY, foreground=FG_LIGHT, font=('Arial', 10, 'bold'))
        style.map('TButton', background=[('active', COLOR_PRIMARY)])
        style.configure('Accent.TButton', background=COLOR_ACCENT, foreground=BG_DARK)
        style.map('Accent.TButton', background=[('active', COLOR_ACCENT)])
        style.configure('Status.TLabel', background=BG_MEDIUM, foreground=FG_LIGHT, font=('Arial', 10, 'italic'))

        # Frame Principal
        main_frame = tk.Frame(self.root, bg=BG_MEDIUM, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # A. Cabeçalho
        title = tk.Label(main_frame, text=TITLE_MAIN, 
                         font=("Arial", 16, "bold"), bg=BG_MEDIUM, fg=FG_LIGHT)
        title.pack(pady=(0, 15))
        
        # B. Seleção de Arquivo
        file_frame = tk.Frame(main_frame, bg=BG_MEDIUM)
        file_frame.pack(fill=tk.X, pady=10)
        
        self.select_button = ttk.Button(file_frame, text=SELECT_FILE_BUTTON, 
                                        command=self.select_file, style='Accent.TButton')
        self.select_button.pack(side=tk.LEFT)
        
        self.file_label = tk.Label(file_frame, textvariable=self.file_info_var,
                                        font=("Arial", 10), bg=BG_MEDIUM, fg="#cccccc", anchor='w')
        self.file_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.duration_label = tk.Label(main_frame, textvariable=self.duration_info_var,
                                        font=("Arial", 10, "bold"), bg=BG_MEDIUM, fg=COLOR_SUCCESS, anchor='w')
        self.duration_label.pack(fill=tk.X, pady=(0, 15))

        # C. Parâmetros de Corte
        cut_frame = tk.Frame(main_frame, bg=BG_MEDIUM)
        cut_frame.pack(fill=tk.X, pady=10)

        # Tempo de Início
        tk.Label(cut_frame, text="Tempo de INÍCIO (HH:MM:SS.mmm ou Segundos):", 
                 font=("Arial", 10), bg=BG_MEDIUM, fg=FG_LIGHT).grid(row=0, column=0, sticky='w', pady=5)
        self.start_entry = ttk.Entry(cut_frame, textvariable=self.start_time_var, width=25)
        self.start_entry.grid(row=0, column=1, sticky='e', padx=10)

        # Tempo de Fim
        tk.Label(cut_frame, text="Tempo de FIM (HH:MM:SS.mmm ou Segundos):", 
                 font=("Arial", 10), bg=BG_MEDIUM, fg=FG_LIGHT).grid(row=1, column=0, sticky='w', pady=5)
        self.end_entry = ttk.Entry(cut_frame, textvariable=self.end_time_var, width=25)
        self.end_entry.grid(row=1, column=1, sticky='e', padx=10)

        # Botão de Corte
        self.cut_button = ttk.Button(main_frame, text=CUT_BUTTON, 
                                     command=self.start_cut_thread, style='TButton', state=tk.DISABLED)
        self.cut_button.pack(pady=20)

        # D. Status
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, style='Status.TLabel')
        self.status_label.pack(fill=tk.X, pady=(5, 10))

        # E. Rodapé
        footer_frame = tk.Frame(self.root, bg=BG_DARK)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 5))
        
        tk.Label(footer_frame, text=FOOTER_TEXT, 
                 font=("Arial", 8), bg=BG_DARK, fg="#888888").pack(side=tk.LEFT, padx=10)
        
        hub_link = tk.Label(footer_frame, text=HUB_LINK_TEXT, 
                            font=("Arial", 8, "underline"), fg=COLOR_PRIMARY, bg=BG_DARK, cursor="hand2")
        hub_link.pack(side=tk.RIGHT, padx=10)
        hub_link.bind("<Button-1>", lambda e: webbrowser.open_new(HUB_LINK_URL))

    # --- Funções de Utilitário ---

    def format_time(self, seconds):
        """Converte segundos em formato HH:MM:SS.mmm"""
        if seconds is None:
            return "00:00:00.000"
        s = float(seconds)
        ms = int((s - int(s)) * 1000)
        s = int(s)
        h = s // 3600
        s %= 3600
        m = s // 60
        s %= 60
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

    def time_to_seconds(self, time_str):
        """Converte string de tempo (HH:MM:SS.mmm ou Segundos) para segundos float."""
        try:
            # Tenta converter diretamente para float (se for segundos)
            return float(time_str)
        except ValueError:
            # Se não for float, tenta o formato HH:MM:SS.mmm
            parts = re.split(r'[:.]', time_str)
            if len(parts) == 4:
                h, m, s, ms = map(int, parts)
                return h * 3600 + m * 60 + s + ms / 1000.0
            elif len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
            else:
                raise ValueError("Formato de tempo inválido.")

    def get_video_duration(self, input_path):
        """Obtém a duração do vídeo usando ffprobe."""
        try:
            command = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                input_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            return duration
        except Exception as e:
            self.status_var.set(f"{STATUS_ERROR} Não foi possível obter a duração do vídeo. {e}")
            return None

    # --- Funções de Ação da GUI ---

    def select_file(self):
        """Abre a caixa de diálogo para selecionar o arquivo de vídeo."""
        filetypes = [("Arquivos de Vídeo", "*.mp4 *.avi *.mov *.mkv"), ("Todos os Arquivos", "*.*")]
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo de vídeo para cortar",
            filetypes=filetypes
        )
        
        if filepath:
            self.input_file = filepath
            self.file_info_var.set(os.path.basename(filepath))
            self.status_var.set("Calculando duração...")
            self.root.update() # Força a atualização da UI

            # Obtém a duração em uma thread para não travar a UI
            threading.Thread(target=self._load_duration).start()
        else:
            self.input_file = None
            self.video_duration = None
            self.file_info_var.set("Nenhum arquivo selecionado")
            self.duration_info_var.set("Duração Total: --:--:--.---")
            self.status_var.set(STATUS_WAITING)
            self.cut_button.config(state=tk.DISABLED)

    def _load_duration(self):
        """Função executada em thread para carregar a duração do vídeo."""
        duration = self.get_video_duration(self.input_file)
        
        if duration is not None:
            self.video_duration = duration
            formatted_duration = self.format_time(duration)
            self.duration_info_var.set(f"Duração Total: {formatted_duration}")
            self.status_var.set(STATUS_READY)
            self.end_time_var.set(formatted_duration) # Preenche o tempo final com a duração total
            self.cut_button.config(state=tk.NORMAL)
        else:
            self.video_duration = None
            self.duration_info_var.set("Duração Total: ERRO")
            self.cut_button.config(state=tk.DISABLED)

    def start_cut_thread(self):
        """Inicia o processo de corte em uma thread separada."""
        if self.is_cutting:
            return

        try:
            start_time_sec = self.time_to_seconds(self.start_time_var.get())
            end_time_sec = self.time_to_seconds(self.end_time_var.get())
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Formato de tempo inválido: {e}")
            return

        if self.input_file is None or self.video_duration is None:
            messagebox.showerror("Erro", "Selecione um arquivo de vídeo primeiro.")
            return

        if not (0 <= start_time_sec < end_time_sec <= self.video_duration + 0.001): # Tolerância para float
            messagebox.showerror("Erro de Tempo", 
                                 f"Tempos de corte inválidos.\nInício: {self.format_time(start_time_sec)}\nFim: {self.format_time(end_time_sec)}\nDuração Máxima: {self.format_time(self.video_duration)}")
            return

        # Seleção do arquivo de saída
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        default_name = f"{base_name}_cut_{int(start_time_sec)}-{int(end_time_sec)}.mp4"
        
        output_file = filedialog.asksaveasfilename(
            title="Salvar o vídeo cortado como...",
            defaultextension=".mp4",
            initialfile=default_name,
            filetypes=[("Arquivo MP4", "*.mp4")]
        )

        if not output_file:
            self.status_var.set("Operação de salvar cancelada.")
            return

        self.is_cutting = True
        self.cut_button.config(state=tk.DISABLED, text=STATUS_CUTTING)
        self.status_label.config(foreground=COLOR_ACCENT)
        self.status_var.set(STATUS_CUTTING)
        
        # Inicia o corte em uma thread
        threading.Thread(target=self._cut_video_segment, args=(self.input_file, start_time_sec, end_time_sec, output_file)).start()

    def _cut_video_segment(self, input_path, start_time, end_time, output_path):
        """Executa o corte de vídeo usando FFmpeg."""
        try:
            duration = end_time - start_time
            
            # Comando FFmpeg para corte rápido (-c copy)
            command = [
                "ffmpeg",
                "-i", input_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-c", "copy",
                output_path
            ]

            subprocess.run(command, capture_output=True, text=True, check=True)

            # Sucesso
            self.status_label.config(foreground=COLOR_SUCCESS)
            self.status_var.set(STATUS_SUCCESS)
            messagebox.showinfo("Sucesso", f"Corte de vídeo concluído!\nArquivo salvo em: {output_path}")

        except subprocess.CalledProcessError as e:
            # Erro do FFmpeg
            error_msg = f"Erro durante o corte (FFmpeg retornou erro).\nDetalhes: {e.stderr.strip()}"
            self.status_label.config(foreground=COLOR_ERROR)
            self.status_var.set(f"{STATUS_ERROR} {error_msg}")
            messagebox.showerror("Erro de Corte", error_msg)
        except FileNotFoundError:
            # Erro de dependência (embora já checado, é bom ter)
            error_msg = "FFmpeg não encontrado. Certifique-se de que está no PATH."
            self.status_label.config(foreground=COLOR_ERROR)
            self.status_var.set(f"{STATUS_ERROR} {error_msg}")
            messagebox.showerror("Erro de Dependência", error_msg)
        except Exception as e:
            # Outros erros
            error_msg = f"Ocorreu um erro inesperado: {e}"
            self.status_label.config(foreground=COLOR_ERROR)
            self.status_var.set(f"{STATUS_ERROR} {error_msg}")
            messagebox.showerror("Erro Inesperado", error_msg)
        finally:
            self.is_cutting = False
            self.cut_button.config(state=tk.NORMAL, text=CUT_BUTTON)
            if self.status_var.get() == STATUS_CUTTING:
                 self.status_var.set(STATUS_READY) # Volta ao estado pronto se não houve erro

if __name__ == "__main__":
    root = tk.Tk()
    app = CutSynkApp(root)
    root.mainloop()
