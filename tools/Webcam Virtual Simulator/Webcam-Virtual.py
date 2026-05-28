#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de Webcam Virtual
Permite carregar imagens ou vídeos e transmiti-los como uma webcam virtual
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
from PIL import Image, ImageTk
import threading
import os
import pyvirtualcam
import numpy as np



class WebcamSimulator:
    def __init__(self, root):
        self.selected_camera_device = tk.StringVar(value="") # Não precisamos de uma lista pré-preenchida, o usuário pode digitar ou selecionar um padrão
        self.resolutions = ["640x480", "1280x720", "1920x1080", "1024x1024"]
        self.selected_resolution = tk.StringVar(value="1920x1080") # Definir um valor padrão

        self.root = root
        self.root.title("Simulador de Webcam Virtual")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variáveis de controle
        self.media_path = None
        self.media_type = None  # 'image' ou 'video'
        self.is_streaming = False
        self.loop_enabled = tk.BooleanVar(value=True)
        self.video_capture = None
        self.virtual_cam = None
        self.stream_thread = None
        
        # Configurar interface
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface gráfica"""
        # Frame superior - Controles
        control_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botão para carregar mídia
        self.load_button = tk.Button(
            control_frame, 
            text="📁 Carregar Mídia", 
            command=self.load_media,
            font=("Arial", 11),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        # Checkbox para loop
        self.loop_checkbox = tk.Checkbutton(
            control_frame,
            text="Loop de Vídeo",
            variable=self.loop_enabled,
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.loop_checkbox.pack(side=tk.LEFT, padx=15)

        # Dropdown para seleção de resolução
        resolution_label = tk.Label(control_frame, text="Resolução:", font=("Arial", 10), bg="#f0f0f0")
        resolution_label.pack(side=tk.LEFT, padx=(5, 0))
        self.resolution_menu = ttk.Combobox(control_frame, textvariable=self.selected_resolution, values=self.resolutions, state="readonly", width=10)
        self.resolution_menu.pack(side=tk.LEFT, padx=5)
        self.resolution_menu.bind("<<ComboboxSelected>>", self.update_resolution)

        # Campo para entrada manual do dispositivo de câmera virtual (ou deixar em branco para padrão)
        camera_label = tk.Label(control_frame, text="Dispositivo Câmera Virtual (opcional):", font=("Arial", 10), bg="#f0f0f0")
        camera_label.pack(side=tk.LEFT, padx=(15, 0))
        self.camera_entry = tk.Entry(control_frame, textvariable=self.selected_camera_device, width=25)
        self.camera_entry.pack(side=tk.LEFT, padx=5)
        self.selected_camera_device.set("") # Deixar em branco para o padrão do pyvirtualcam
        
        # Botão para iniciar streaming
        self.start_button = tk.Button(
            control_frame,
            text="▶ Iniciar Webcam Virtual",
            command=self.start_streaming,
            font=("Arial", 11),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Botão para parar streaming
        self.stop_button = tk.Button(
            control_frame,
            text="⏹ Parar Webcam Virtual",
            command=self.stop_streaming,
            font=("Arial", 11),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Frame de informações
        info_frame = tk.Frame(self.root, bg="#e0e0e0", pady=5)
        info_frame.pack(fill=tk.X, padx=10)
        
        self.info_label = tk.Label(
            info_frame,
            text="Nenhuma mídia carregada",
            font=("Arial", 9),
            bg="#e0e0e0",
            fg="#333"
        )
        self.info_label.pack()
        
        # Frame de preview
        preview_frame = tk.Frame(self.root, bg="#000000")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.preview_label = tk.Label(
            preview_frame,
            text="Preview da Mídia",
            bg="#000000",
            fg="#ffffff",
            font=("Arial", 14)
        )
        self.preview_label.pack(expand=True)
        
        # Frame de status
        status_frame = tk.Frame(self.root, bg="#f0f0f0", pady=5)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: Aguardando...",
            font=("Arial", 9, "italic"),
            bg="#f0f0f0",
            fg="#666"
        )
        self.status_label.pack(anchor=tk.W, padx=5)

        # Adicionar um label para exibir informações da câmera virtual
        self.cam_info_label = tk.Label(
            status_frame,
            text="Câmera: Não iniciada",
            font=("Arial", 9, "italic"),
            bg="#f0f0f0",
            fg="#666"
        )
        self.cam_info_label.pack(anchor=tk.W, padx=5)

        
    def load_media(self):
        """Abre diálogo para selecionar arquivo de mídia"""
        filetypes = [
            ("Todos os formatos suportados", "*.png *.jpg *.jpeg *.bmp *.mp4 *.avi *.mov *.mkv"),
            ("Imagens", "*.png *.jpg *.jpeg *.bmp"),
            ("Vídeos", "*.mp4 *.avi *.mov *.mkv"),
            ("Todos os arquivos", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Selecione uma imagem ou vídeo",
            filetypes=filetypes
        )
        
        if filepath:
            self.media_path = filepath
            self.detect_media_type()
            self.show_preview()
            self.start_button.config(state=tk.NORMAL)
            
    def detect_media_type(self):
        """Detecta se o arquivo é imagem ou vídeo"""
        ext = os.path.splitext(self.media_path)[1].lower()
        image_extensions = [".png", ".jpg", ".jpeg", ".bmp"]
        video_extensions = [".mp4", ".avi", ".mov", ".mkv"]
        
        if ext in image_extensions:
            self.media_type = 'image'
            self.info_label.config(text=f"Imagem carregada: {os.path.basename(self.media_path)}")
        elif ext in video_extensions:
            self.media_type = 'video'
            self.info_label.config(text=f"Vídeo carregado: {os.path.basename(self.media_path)}")
        else:
            self.media_type = None
            messagebox.showerror("Erro", "Formato de arquivo não suportado!")
            
    def update_resolution(self, event=None):
        width, height = map(int, self.selected_resolution.get().split('x'))
        print(f"Resolução selecionada: {width}x{height}")



    def show_preview(self):
        """Exibe preview da mídia na interface"""
        if self.media_type == 'image':
            # Carregar e exibir imagem
            img = cv2.imread(self.media_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.display_frame(img)
            
        elif self.media_type == 'video':
            # Carregar e exibir primeiro frame do vídeo
            cap = cv2.VideoCapture(self.media_path)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.display_frame(frame)
            cap.release()
            
    def display_frame(self, frame):
        """Exibe um frame no preview"""
        # Redimensionar frame para caber no preview
        height, width = frame.shape[:2]
        max_width = 780
        max_height = 400
        
        scale = min(max_width / width, max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        frame_resized = cv2.resize(frame, (new_width, new_height))
        
        # Converter para formato do Tkinter
        img = Image.fromarray(frame_resized)
        img_tk = ImageTk.PhotoImage(image=img)
        
        self.preview_label.config(image=img_tk, text="")
        self.preview_label.image = img_tk
        
    def start_streaming(self):
        """Inicia o streaming para a webcam virtual"""
        if self.is_streaming:
            return
            
        self.is_streaming = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Streaming ativo", fg="#4CAF50")
        # A atualização do cam_info_label será feita após a inicialização da câmera no thread worker.
        
        # Iniciar thread de streaming
        self.stream_thread = threading.Thread(target=self.stream_worker, daemon=True)
        self.stream_thread.start()
        
    def stop_streaming(self):
        """Para o streaming da webcam virtual"""
        self.is_streaming = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Streaming parado", fg="#f44336")
        self.cam_info_label.config(text="Câmera: Não iniciada")
        
        # Limpar recursos
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
            
        if self.virtual_cam:
            self.virtual_cam.close()
            self.virtual_cam = None
            
    def stream_worker(self):
        """Worker thread para streaming de mídia"""
        try:
            if self.media_type == 'image':
                self.stream_image()
            elif self.media_type == 'video':
                self.stream_video()
        except Exception as e:
            self.is_streaming = False
            messagebox.showerror("Erro no Streaming", f"Ocorreu um erro: {str(e)}")
            self.root.after(0, self.stop_streaming)
            
    def stream_image(self):
        """Transmite uma imagem estática para a webcam virtual"""
        img = cv2.imread(self.media_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Obter resolução selecionada
        width_cam, height_cam = map(int, self.selected_resolution.get().split("x"))

        # Redimensionar imagem para a resolução da câmera virtual
        img_resized = cv2.resize(img, (width_cam, height_cam))
        
        # Criar câmera virtual com as dimensões e dispositivo selecionados
        device_path = self.selected_camera_device.get() if self.selected_camera_device.get() else None
        with pyvirtualcam.Camera(width=width_cam, height=height_cam, fps=30, device=device_path) as cam:
            self.virtual_cam = cam
            print(f'Webcam virtual iniciada: {cam.device}')
            self.root.after(0, lambda: self.cam_info_label.config(text=f"Câmera: {self.virtual_cam.device} | Resolução: {self.virtual_cam.width}x{self.virtual_cam.height} | FPS: {self.virtual_cam.fps}"))
            
            while self.is_streaming:
                cam.send(img_resized)
                cam.sleep_until_next_frame()
                
    def stream_video(self):
        """Transmite um vídeo para a webcam virtual"""
        self.video_capture = cv2.VideoCapture(self.media_path)
        
        # Obter propriedades do vídeo
        width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
        
        if fps == 0:
            fps = 30

        # Obter resolução selecionada
        width_cam, height_cam = map(int, self.selected_resolution.get().split("x"))

        # Criar câmera virtual com as dimensões e dispositivo selecionados
        device_path = self.selected_camera_device.get() if self.selected_camera_device.get() else None
        with pyvirtualcam.Camera(width=width_cam, height=height_cam, fps=fps, device=device_path) as cam:
            self.virtual_cam = cam
            print(f'Webcam virtual iniciada: {cam.device}')
            self.root.after(0, lambda: self.cam_info_label.config(text=f"Câmera: {self.virtual_cam.device} | Resolução: {self.virtual_cam.width}x{self.virtual_cam.height} | FPS: {self.virtual_cam.fps}"))
            
            while self.is_streaming:
                ret, frame = self.video_capture.read()
                
                if not ret:
                    # Se o vídeo terminou
                    if self.loop_enabled.get():
                        # Reiniciar vídeo se loop estiver ativado
                        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        # Parar streaming se loop estiver desativado
                        break
                        
                # Converter BGR para RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Redimensionar frame para a resolução da câmera virtual
                frame_resized = cv2.resize(frame, (width_cam, height_cam))
                
                # Enviar frame para câmera virtual
                cam.send(frame_resized)
                cam.sleep_until_next_frame()
                
        # Streaming terminou
        self.root.after(0, self.stop_streaming)


def main():
    root = tk.Tk()
    app = WebcamSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()