import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import subprocess
import json
import shutil
import threading
import time


class AudioVideoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Áudio e Vídeo")
        self.root.geometry("950x750")
        self.root.configure(bg="#2b2b2b")
        
        self.current_file = None
        self.duration = 0
        self.batch_files = []
        self.is_playing = False
        self.current_position = 0
        self.player_process = None
        
        # Verificar se FFmpeg está instalado
        if not self.check_ffmpeg():
            msg = "FFmpeg não encontrado!\n\n"
            msg += "INSTALE O FFMPEG:\n\n"
            msg += "Windows:\n"
            msg += "1. Baixe: https://github.com/BtbN/FFmpeg-Builds/releases\n"
            msg += "2. Extraia e adicione a pasta 'bin' ao PATH\n\n"
            msg += "Linux: sudo apt install ffmpeg\n"
            msg += "Mac: brew install ffmpeg"
            messagebox.showerror("Erro - FFmpeg Necessário", msg)
            self.root.destroy()
            return
        
        self.setup_ui()
    
    def check_ffmpeg(self):
        """Verifica se FFmpeg e FFprobe estão disponíveis"""
        ffmpeg_found = shutil.which('ffmpeg') is not None
        ffprobe_found = shutil.which('ffprobe') is not None
        ffplay_found = shutil.which('ffplay') is not None
        return ffmpeg_found and ffprobe_found
    
    def get_media_info(self, filepath):
        """Obtém informações do arquivo de mídia usando ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                   encoding='utf-8', errors='ignore', check=True)
            if result.stdout:
                info = json.loads(result.stdout)
                duration = float(info['format']['duration'])
                return duration
            return 0
        except Exception as e:
            print(f"Erro ao obter info: {e}")
            return 0
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = tk.Label(main_frame, text="🎵 Editor de Áudio/Vídeo", 
                        font=("Arial", 24, "bold"), bg="#2b2b2b", fg="#ffffff")
        title.pack(pady=(0, 20))
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba 1: Arquivo Único
        self.single_frame = tk.Frame(self.notebook, bg="#3b3b3b")
        self.notebook.add(self.single_frame, text="Arquivo Único")
        self.setup_single_file_tab()
        
        # Aba 2: Conversão em Lote
        self.batch_frame = tk.Frame(self.notebook, bg="#3b3b3b")
        self.notebook.add(self.batch_frame, text="Conversão em Lote")
        self.setup_batch_tab()
    
    def setup_single_file_tab(self):
        # Botão para adicionar arquivo
        btn_frame = tk.Frame(self.single_frame, bg="#3b3b3b")
        btn_frame.pack(pady=15)
        
        add_btn = tk.Button(btn_frame, text="📁 Adicionar Arquivo", 
                           command=self.load_file, font=("Arial", 12),
                           bg="#4CAF50", fg="white", padx=20, pady=10,
                           cursor="hand2", relief=tk.FLAT)
        add_btn.pack()
        
        # Frame de informações do arquivo
        self.info_frame = tk.Frame(self.single_frame, bg="#3b3b3b")
        self.info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.file_label = tk.Label(self.info_frame, text="Nenhum arquivo carregado",
                                   font=("Arial", 10), bg="#3b3b3b", fg="#cccccc")
        self.file_label.pack()
        
        self.duration_label = tk.Label(self.info_frame, text="",
                                       font=("Arial", 10), bg="#3b3b3b", fg="#cccccc")
        self.duration_label.pack()
        
        # Player de áudio
        player_frame = tk.LabelFrame(self.single_frame, text="Player", 
                                    font=("Arial", 11, "bold"), bg="#3b3b3b", 
                                    fg="#ffffff", padx=10, pady=10)
        player_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Timeline interativa
        timeline_container = tk.Frame(player_frame, bg="#3b3b3b")
        timeline_container.pack(fill=tk.X, pady=10)
        
        self.timeline_canvas = tk.Canvas(timeline_container, height=80, bg="#555555",
                                        highlightthickness=0, cursor="crosshair")
        self.timeline_canvas.pack(fill=tk.X)
        self.timeline_canvas.bind("<Button-1>", self.on_timeline_click)
        self.timeline_canvas.bind("<B1-Motion>", self.on_timeline_drag)
        
        # Labels de posição
        position_frame = tk.Frame(player_frame, bg="#3b3b3b")
        position_frame.pack(fill=tk.X, pady=5)
        
        self.position_label = tk.Label(position_frame, text="00:00 / 00:00",
                                      font=("Arial", 10), bg="#3b3b3b", fg="#ffffff")
        self.position_label.pack()
        
        # Controles do player
        controls_frame = tk.Frame(player_frame, bg="#3b3b3b")
        controls_frame.pack(pady=10)
        
        self.play_btn = tk.Button(controls_frame, text="▶ Play", 
                                  command=self.toggle_play, font=("Arial", 11),
                                  bg="#2196F3", fg="white", padx=20, pady=5,
                                  cursor="hand2", relief=tk.FLAT, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_frame, text="⏹ Stop", 
                 command=self.stop_play, font=("Arial", 11),
                 bg="#f44336", fg="white", padx=20, pady=5,
                 cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_frame, text="📍 Marcar Início", 
                 command=self.mark_start, font=("Arial", 11),
                 bg="#FF9800", fg="white", padx=15, pady=5,
                 cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_frame, text="📍 Marcar Fim", 
                 command=self.mark_end, font=("Arial", 11),
                 bg="#FF9800", fg="white", padx=15, pady=5,
                 cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        # Controles de corte
        cut_frame = tk.LabelFrame(self.single_frame, text="Cortar Áudio", 
                                 font=("Arial", 11, "bold"), bg="#3b3b3b", 
                                 fg="#ffffff", padx=10, pady=10)
        cut_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Início
        start_frame = tk.Frame(cut_frame, bg="#3b3b3b")
        start_frame.pack(fill=tk.X, pady=5)
        tk.Label(start_frame, text="Início (segundos):", bg="#3b3b3b", 
                fg="#ffffff", width=15, anchor='w').pack(side=tk.LEFT)
        self.start_entry = tk.Entry(start_frame, width=12, font=("Arial", 10))
        self.start_entry.pack(side=tk.LEFT, padx=10)
        self.start_entry.insert(0, "0")
        
        # Fim
        end_frame = tk.Frame(cut_frame, bg="#3b3b3b")
        end_frame.pack(fill=tk.X, pady=5)
        tk.Label(end_frame, text="Fim (segundos):", bg="#3b3b3b", 
                fg="#ffffff", width=15, anchor='w').pack(side=tk.LEFT)
        self.end_entry = tk.Entry(end_frame, width=12, font=("Arial", 10))
        self.end_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Button(cut_frame, text="✂️ Cortar", command=self.cut_audio,
                 bg="#FF9800", fg="white", padx=15, pady=5,
                 cursor="hand2", relief=tk.FLAT).pack(pady=10)
        
        # Conversão
        convert_frame = tk.LabelFrame(self.single_frame, text="Converter Áudio", 
                                     font=("Arial", 11, "bold"), bg="#3b3b3b", 
                                     fg="#ffffff", padx=10, pady=10)
        convert_frame.pack(fill=tk.X, padx=20, pady=10)
        
        format_frame = tk.Frame(convert_frame, bg="#3b3b3b")
        format_frame.pack(pady=5)
        
        tk.Label(format_frame, text="Formato:", bg="#3b3b3b", 
                fg="#ffffff").pack(side=tk.LEFT)
        
        self.format_var = tk.StringVar(value="mp3")
        formats = ["mp3", "wav", "ogg", "flac", "aac", "m4a"]
        format_menu = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=formats, state="readonly", width=10)
        format_menu.pack(side=tk.LEFT, padx=10)
        
        tk.Button(convert_frame, text="🔄 Converter", command=self.convert_audio,
                 bg="#2196F3", fg="white", padx=15, pady=5,
                 cursor="hand2", relief=tk.FLAT).pack(pady=10)
    
    def setup_batch_tab(self):
        # Botões superiores
        btn_frame = tk.Frame(self.batch_frame, bg="#3b3b3b")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="➕ Adicionar Arquivos", 
                 command=self.add_batch_files, font=("Arial", 11),
                 bg="#4CAF50", fg="white", padx=15, pady=8,
                 cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🗑️ Limpar Lista", 
                 command=self.clear_batch_files, font=("Arial", 11),
                 bg="#f44336", fg="white", padx=15, pady=8,
                 cursor="hand2", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        # Lista de arquivos
        list_frame = tk.Frame(self.batch_frame, bg="#3b3b3b")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(list_frame, text="Arquivos na fila:", font=("Arial", 11, "bold"),
                bg="#3b3b3b", fg="#ffffff").pack(anchor=tk.W)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.batch_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       bg="#555555", fg="white", font=("Arial", 10),
                                       selectmode=tk.EXTENDED)
        self.batch_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.batch_listbox.yview)
        
        # Configurações de conversão
        config_frame = tk.LabelFrame(self.batch_frame, text="Configurações", 
                                    font=("Arial", 11, "bold"), bg="#3b3b3b", 
                                    fg="#ffffff", padx=10, pady=10)
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        format_frame = tk.Frame(config_frame, bg="#3b3b3b")
        format_frame.pack(pady=5)
        
        tk.Label(format_frame, text="Converter para:", bg="#3b3b3b", 
                fg="#ffffff", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.batch_format_var = tk.StringVar(value="mp3")
        formats = ["mp3", "wav", "ogg", "flac", "aac", "m4a"]
        ttk.Combobox(format_frame, textvariable=self.batch_format_var,
                    values=formats, state="readonly", width=10).pack(side=tk.LEFT, padx=10)
        
        # Botão de conversão em lote
        tk.Button(self.batch_frame, text="🚀 Converter Todos", 
                 command=self.batch_convert, font=("Arial", 12, "bold"),
                 bg="#2196F3", fg="white", padx=30, pady=10,
                 cursor="hand2", relief=tk.FLAT).pack(pady=20)
    
    def load_file(self):
        filetypes = (
            ("Todos os arquivos de mídia", "*.mp3 *.wav *.ogg *.flac *.m4a *.aac *.mp4 *.avi *.mov *.mkv *.webm *.wma"),
            ("Áudio", "*.mp3 *.wav *.ogg *.flac *.m4a *.aac *.wma"),
            ("Vídeo", "*.mp4 *.avi *.mov *.mkv *.webm"),
            ("Todos os arquivos", "*.*")
        )
        
        filepath = filedialog.askopenfilename(title="Selecione um arquivo", filetypes=filetypes)
        
        if filepath:
            self.stop_play()
            self.current_file = filepath
            
            try:
                self.duration = self.get_media_info(filepath)
                
                if self.duration == 0:
                    messagebox.showerror("Erro", "Não foi possível ler a duração do arquivo.")
                    return
                
                self.file_label.config(text=f"Arquivo: {Path(filepath).name}")
                self.duration_label.config(text=f"Duração: {self.format_time(self.duration)}")
                self.end_entry.delete(0, tk.END)
                self.end_entry.insert(0, f"{self.duration:.2f}")
                self.current_position = 0
                self.draw_timeline()
                self.play_btn.config(state=tk.NORMAL)
                
                messagebox.showinfo("Sucesso", "Arquivo carregado com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
    
    def draw_timeline(self):
        self.timeline_canvas.delete("all")
        width = self.timeline_canvas.winfo_width()
        if width <= 1:
            width = 700
        
        # Fundo da timeline
        self.timeline_canvas.create_rectangle(0, 25, width, 55, fill="#333333", outline="")
        
        # Área selecionada para corte
        if self.duration > 0:
            try:
                start = float(self.start_entry.get())
                end = float(self.end_entry.get())
                start_x = (start / self.duration) * width
                end_x = (end / self.duration) * width
                self.timeline_canvas.create_rectangle(start_x, 25, end_x, 55, 
                                                     fill="#4CAF50", outline="", 
                                                     stipple="gray50")
            except:
                pass
        
        # Barra de progresso
        self.timeline_canvas.create_rectangle(0, 25, width, 55, fill="", outline="#666666", width=2)
        
        # Marcadores de tempo
        if self.duration > 0:
            num_markers = min(10, max(5, int(self.duration / 10)))
            for i in range(num_markers + 1):
                x = (i / num_markers) * width
                time = (i / num_markers) * self.duration
                self.timeline_canvas.create_line(x, 55, x, 65, fill="white", width=1)
                self.timeline_canvas.create_text(x, 72, text=f"{int(time)}s", 
                                                fill="white", font=("Arial", 8))
            
            # Posição atual
            pos_x = (self.current_position / self.duration) * width
            self.timeline_canvas.create_line(pos_x, 20, pos_x, 60, fill="#FF5722", width=3)
            self.timeline_canvas.create_oval(pos_x-5, 37, pos_x+5, 43, fill="#FF5722", outline="")
    
    def on_timeline_click(self, event):
        if self.duration > 0:
            width = self.timeline_canvas.winfo_width()
            position = (event.x / width) * self.duration
            self.current_position = max(0, min(position, self.duration))
            self.draw_timeline()
            self.update_position_label()
    
    def on_timeline_drag(self, event):
        self.on_timeline_click(event)
    
    def toggle_play(self):
        if not self.current_file:
            return
        
        if self.is_playing:
            self.pause_play()
        else:
            self.start_play()
    
    def start_play(self):
        if not self.current_file:
            return
        
        self.is_playing = True
        self.play_btn.config(text="⏸ Pause")
        
        # Iniciar thread de reprodução
        threading.Thread(target=self.play_thread, daemon=True).start()
    
    def play_thread(self):
        try:
            # Usar FFplay para reproduzir áudio
            cmd = [
                'ffplay',
                '-nodisp',
                '-autoexit',
                '-ss', str(self.current_position),
                self.current_file
            ]
            
            self.player_process = subprocess.Popen(cmd, 
                                                   stdout=subprocess.DEVNULL,
                                                   stderr=subprocess.DEVNULL)
            
            start_time = time.time()
            start_pos = self.current_position
            
            while self.is_playing and self.player_process.poll() is None:
                elapsed = time.time() - start_time
                self.current_position = start_pos + elapsed
                
                if self.current_position >= self.duration:
                    self.current_position = self.duration
                    self.is_playing = False
                    break
                
                self.root.after(0, self.draw_timeline)
                self.root.after(0, self.update_position_label)
                time.sleep(0.1)
            
            self.is_playing = False
            self.root.after(0, lambda: self.play_btn.config(text="▶ Play"))
            
        except Exception as e:
            print(f"Erro na reprodução: {e}")
            self.is_playing = False
            self.root.after(0, lambda: self.play_btn.config(text="▶ Play"))
    
    def pause_play(self):
        self.is_playing = False
        if self.player_process:
            self.player_process.terminate()
        self.play_btn.config(text="▶ Play")
    
    def stop_play(self):
        self.is_playing = False
        if self.player_process:
            self.player_process.terminate()
            self.player_process = None
        self.current_position = 0
        self.play_btn.config(text="▶ Play")
        self.draw_timeline()
        self.update_position_label()
    
    def mark_start(self):
        if self.duration > 0:
            self.start_entry.delete(0, tk.END)
            self.start_entry.insert(0, f"{self.current_position:.2f}")
            self.draw_timeline()
    
    def mark_end(self):
        if self.duration > 0:
            self.end_entry.delete(0, tk.END)
            self.end_entry.insert(0, f"{self.current_position:.2f}")
            self.draw_timeline()
    
    def update_position_label(self):
        current = self.format_time(self.current_position)
        total = self.format_time(self.duration)
        self.position_label.config(text=f"{current} / {total}")
    
    def format_time(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def cut_audio(self):
        if not self.current_file:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro!")
            return
        
        try:
            start = float(self.start_entry.get())
            end = float(self.end_entry.get())
            
            if start >= end:
                messagebox.showerror("Erro", "O tempo de início deve ser menor que o fim!")
                return
            
            if start < 0 or end > self.duration:
                messagebox.showerror("Erro", f"Os valores devem estar entre 0 e {self.duration:.2f} segundos!")
                return
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[
                    ("MP3", "*.mp3"), 
                    ("WAV", "*.wav"), 
                    ("OGG", "*.ogg"),
                    ("FLAC", "*.flac"),
                    ("AAC", "*.aac"),
                    ("M4A", "*.m4a"),
                    ("Todos", "*.*")
                ]
            )
            
            if filepath:
                duration = end - start
                
                cmd = [
                    'ffmpeg',
                    '-i', self.current_file,
                    '-ss', str(start),
                    '-t', str(duration),
                    '-c', 'copy',
                    '-y',
                    filepath
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True,
                                       encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    messagebox.showinfo("Sucesso", f"Áudio cortado salvo em:\n{filepath}")
                else:
                    cmd = [
                        'ffmpeg',
                        '-i', self.current_file,
                        '-ss', str(start),
                        '-t', str(duration),
                        '-y',
                        filepath
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True,
                                           encoding='utf-8', errors='ignore')
                    
                    if result.returncode == 0:
                        messagebox.showinfo("Sucesso", f"Áudio cortado salvo em:\n{filepath}")
                    else:
                        messagebox.showerror("Erro", "Erro ao cortar áudio.")
                
        except ValueError:
            messagebox.showerror("Erro", "Digite valores numéricos válidos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cortar áudio:\n{str(e)}")
    
    def convert_audio(self):
        if not self.current_file:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro!")
            return
        
        try:
            output_format = self.format_var.get()
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=f".{output_format}",
                filetypes=[(output_format.upper(), f"*.{output_format}"), ("Todos", "*.*")]
            )
            
            if filepath:
                cmd = [
                    'ffmpeg',
                    '-i', self.current_file,
                    '-vn',
                    '-y',
                    filepath
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True,
                                       encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    messagebox.showinfo("Sucesso", f"Arquivo convertido para {output_format.upper()}:\n{filepath}")
                else:
                    messagebox.showerror("Erro", "Erro ao converter arquivo.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao converter:\n{str(e)}")
    
    def add_batch_files(self):
        filetypes = (
            ("Todos os arquivos de mídia", "*.mp3 *.wav *.ogg *.flac *.m4a *.aac *.mp4 *.avi *.mov *.mkv *.webm *.wma"),
            ("Áudio", "*.mp3 *.wav *.ogg *.flac *.m4a *.aac *.wma"),
            ("Vídeo", "*.mp4 *.avi *.mov *.mkv *.webm"),
            ("Todos os arquivos", "*.*")
        )
        
        files = filedialog.askopenfilenames(title="Selecione arquivos", filetypes=filetypes)
        
        for file in files:
            if file not in self.batch_files:
                self.batch_files.append(file)
                self.batch_listbox.insert(tk.END, Path(file).name)
    
    def clear_batch_files(self):
        self.batch_files.clear()
        self.batch_listbox.delete(0, tk.END)
    
    def batch_convert(self):
        if not self.batch_files:
            messagebox.showwarning("Aviso", "Adicione arquivos à lista primeiro!")
            return
        
        output_format = self.batch_format_var.get()
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        
        if not output_dir:
            return
        
        success_count = 0
        error_files = []
        
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Convertendo...")
        progress_window.geometry("450x150")
        progress_window.configure(bg="#2b2b2b")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        tk.Label(progress_window, text="Convertendo arquivos...", 
                font=("Arial", 12, "bold"), bg="#2b2b2b", fg="white").pack(pady=20)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, 
                                      maximum=len(self.batch_files), length=400)
        progress_bar.pack(pady=10)
        
        status_label = tk.Label(progress_window, text="", font=("Arial", 9),
                               bg="#2b2b2b", fg="#cccccc", wraplength=400)
        status_label.pack()
        
        for i, filepath in enumerate(self.batch_files):
            try:
                filename = Path(filepath).stem
                output_path = os.path.join(output_dir, f"{filename}.{output_format}")
                
                status_label.config(text=f"Convertendo: {Path(filepath).name}")
                progress_window.update()
                
                cmd = [
                    'ffmpeg',
                    '-i', filepath,
                    '-vn',
                    '-y',
                    output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True,
                                       encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    success_count += 1
                else:
                    error_files.append((Path(filepath).name, "Erro ao converter"))
                
            except Exception as e:
                error_files.append((Path(filepath).name, str(e)))
            
            progress_var.set(i + 1)
            progress_window.update()
        
        progress_window.destroy()
        
        result_msg = f"Conversão concluída!\n\n"
        result_msg += f"✓ {success_count} arquivo(s) convertido(s) com sucesso\n"
        
        if error_files:
            result_msg += f"✗ {len(error_files)} erro(s)\n\n"
            result_msg += "Arquivos com erro:\n"
            for fname, err in error_files[:5]:
                result_msg += f"- {fname}\n"
        
        messagebox.showinfo("Resultado", result_msg)
        
def main():
    root = tk.Tk()
    app = AudioVideoEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()