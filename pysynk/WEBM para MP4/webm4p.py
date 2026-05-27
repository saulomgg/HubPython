import tkinter as tk
from tkinter import filedialog
import os

def converter_lote():
    arquivos = filedialog.askopenfilenames(filetypes=[("WEBM files", "*.webm")])
    
    for arquivo in arquivos:
        saida = arquivo.replace(".webm", "_insta.mp4")
        
        comando = f'ffmpeg -i "{arquivo}" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -preset fast -crf 23 -c:a aac "{saida}"'
        
        os.system(comando)
        print("Convertido:", saida)

app = tk.Tk()
app.title("WEBM para MP4 (Instagram)")

btn = tk.Button(app, text="Selecionar vídeos", command=converter_lote)
btn.pack(padx=20, pady=20)

app.mainloop()