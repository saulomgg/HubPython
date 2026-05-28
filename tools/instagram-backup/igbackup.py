"""
Instagram Post Downloader - Stampsynk Edition

Developed by saulomg2 - https://stampsynk.com

This program allows users to download all posts from a public Instagram profile using Instaloader.
It provides a simple graphical interface with Tkinter, where users can enter a profile username,
select a destination folder, and start the download process.

Features:
- Downloads all posts from a specified Instagram profile.
- Saves files to a user-selected directory.
- Displays error messages for invalid inputs.
- Includes quick access buttons to open an Instagram profile and a website.

Note:
- This tool works only for public profiles unless logged in with valid credentials.
- Instagram's policies should be respected when using this tool.

For more tools and automation solutions, visit: https://stampsynk.com
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import instaloader
import webbrowser

def baixar_perfil():
    # Obtém o nome do perfil inserido pelo usuário
    perfil = entry_perfil.get().strip()
    if not perfil:
        messagebox.showerror("Erro", "Por favor, digite o @ do perfil.")
        return
    
    # Abre o diálogo para selecionar a pasta de destino
    pasta_destino = filedialog.askdirectory(title="Selecione a pasta para salvar o perfil")
    if not pasta_destino:
        messagebox.showerror("Erro", "Por favor, selecione uma pasta de destino.")
        return

    try:
        # Instância do Instaloader
        loader = instaloader.Instaloader()
        loader.dirname_pattern = f"{pasta_destino}/{{target}}"

        # Baixa as postagens do perfil
        profile = instaloader.Profile.from_username(loader.context, perfil)
        messagebox.showinfo("Baixando", f"Baixando postagens de @{perfil}...")
        for post in profile.get_posts():
            loader.download_post(post, target=perfil)
        
        messagebox.showinfo("Concluído", f"Download de @{perfil} concluído!")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Função para abrir o link do Instagram
def abrir_instagram():
    webbrowser.open("https://www.instagram.com/saulomg2/")

# Função para abrir o link do site
def abrir_site():
    webbrowser.open("https://stampsynk.com")

# Configurações da interface gráfica
app = tk.Tk()
app.title("Baixar Postagens do Instagram")
app.geometry("500x300")
app.resizable(False, False)

# Rótulo
label_perfil = tk.Label(app, text="Digite o @ do perfil:", font=("Arial", 12))
label_perfil.pack(pady=10)

# Entrada para o nome do perfil
entry_perfil = tk.Entry(app, font=("Arial", 12), width=30)
entry_perfil.pack(pady=5)

# Botão para iniciar o download
btn_download = tk.Button(app, text="Download", font=("Arial", 12), command=baixar_perfil)
btn_download.pack(pady=20)

# Links de Instagram e site
label_links = tk.Label(app, text="Links rápidos:", font=("Arial", 12, 'italic'))
label_links.pack(pady=5)

btn_instagram = tk.Button(app, text="Instagram", font=("Arial", 12), command=abrir_instagram)
btn_instagram.pack(pady=5)

btn_site = tk.Button(app, text="Visitar o Site", font=("Arial", 12), command=abrir_site)
btn_site.pack(pady=5)

# Executa o aplicativo
app.mainloop()
