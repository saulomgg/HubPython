"""
Instagram Multi-Link Video Downloader v0.1  
This program allows users to download multiple Instagram video links efficiently.  
Developed by Saulomg2  
Website: https://stampsynk.com  
Instagram: https://www.instagram.com/saulomg2/  
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp

def adicionar_link():
    """Adiciona o link inserido à lista de links para download."""
    link = entry_link.get().strip()
    if not link:
        messagebox.showerror("Erro", "Por favor, insira o link do vídeo.")
        return

    # Adiciona o link à lista exibida
    listbox_links.insert(tk.END, link)
    entry_link.delete(0, tk.END)

def remover_link():
    """Remove o link selecionado na lista."""
    selecionado = listbox_links.curselection()
    if selecionado:
        listbox_links.delete(selecionado)

def baixar_videos():
    """Faz o download de todos os links da lista."""
    btn_download.config(state=tk.DISABLED)  # Desativa o botão para evitar cliques repetidos
    pasta_destino = filedialog.askdirectory(title="Selecione a pasta para salvar os vídeos")
    if not pasta_destino:
        messagebox.showerror("Erro", "Por favor, selecione uma pasta de destino.")
        btn_download.config(state=tk.NORMAL)  # Reativa o botão
        return

    links = listbox_links.get(0, tk.END)
    if not links:
        messagebox.showerror("Erro", "Por favor, adicione pelo menos um link.")
        btn_download.config(state=tk.NORMAL)  # Reativa o botão
        return

    try:
        # Configurações do yt-dlp
        ydl_opts = {
            'outtmpl': f"{pasta_destino}/%(title)s.%(ext)s",
            'format': 'bestvideo+bestaudio/best',
        }

        for i, link in enumerate(links, start=1):
            print(f"Baixando {i}/{len(links)}: {link}")  # Log no terminal
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

        messagebox.showinfo("Concluído", "Todos os downloads foram concluídos!")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    finally:
        btn_download.config(state=tk.NORMAL)  # Reativa o botão ao final

# Configuração da interface gráfica
app = tk.Tk()
app.title("Baixar Vídeos do Instagram")
app.geometry("500x450")
app.resizable(False, False)

# Rótulo e entrada de link
label_link = tk.Label(app, text="Cole o link do vídeo:", font=("Arial", 12))
label_link.pack(pady=10)

entry_link = tk.Entry(app, font=("Arial", 12), width=40)
entry_link.pack(pady=5)

# Botões para adicionar e remover links
frame_buttons = tk.Frame(app)
frame_buttons.pack(pady=5)

btn_add = tk.Button(frame_buttons, text="Adicionar Link", font=("Arial", 12), command=adicionar_link)
btn_add.pack(side=tk.LEFT, padx=10)

btn_remove = tk.Button(frame_buttons, text="Remover Selecionado", font=("Arial", 12), command=remover_link)
btn_remove.pack(side=tk.LEFT, padx=10)

# Lista de links
listbox_links = tk.Listbox(app, font=("Arial", 12), width=50, height=10)
listbox_links.pack(pady=10)

# Botão para iniciar o download
btn_download = tk.Button(app, text="Baixar Todos os Links", font=("Arial", 12), command=baixar_videos)
btn_download.pack(pady=20)

# Créditos
frame_credits = tk.Frame(app)
frame_credits.pack(side=tk.BOTTOM, pady=10)

credit_instagram = tk.Label(frame_credits, text="Desenvolvido por Saulomg2", font=("Arial", 10), fg="blue", cursor="hand2")
credit_instagram.pack(side=tk.LEFT, padx=5)
credit_stampsynk = tk.Label(frame_credits, text="stampsynk.com", font=("Arial", 10), fg="blue", cursor="hand2")
credit_stampsynk.pack(side=tk.LEFT, padx=5)

# Funções para abrir links
def abrir_instagram(event):
    import webbrowser
    webbrowser.open("https://www.instagram.com/saulomg2/")

def abrir_stampsynk(event):
    import webbrowser
    webbrowser.open("https://stampsynk.com")

# Associar eventos aos links
credit_instagram.bind("<Button-1>", abrir_instagram)
credit_stampsynk.bind("<Button-1>", abrir_stampsynk)

# Executa o aplicativo
app.mainloop()
