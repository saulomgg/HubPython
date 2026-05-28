"""
Image to PDF Converter - Developed by saulomg2 | stampsynk.com

This program allows users to select multiple images and convert them into individual PDF files.
Main features:
- Add images in various formats (JPG, PNG, JPEG, GIF, BMP, WEBP)
- Remove selected images before conversion
- Choose an output folder to save the generated PDFs
- Convert each image to a PDF while maintaining the original aspect ratio
- User-friendly graphical interface using Tkinter

Developed by saulomg2 | stampsynk.com
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from fpdf import FPDF
from PIL import Image
import os

# Variáveis globais
images = []  # Lista para armazenar imagens selecionadas
output_folder = ""  # Variável para armazenar a pasta de saída

def add_image():
    global images
    file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.gif;*.bmp;*.webp")])

    if file_paths:
        images.extend(file_paths)
        update_image_listbox()

def delete_selected_image():
    global images
    selected_indices = listbox_images.curselection()

    if selected_indices:
        selected_indices = [int(index) for index in selected_indices]
        images = [image for i, image in enumerate(images) if i not in selected_indices]
        update_image_listbox()

def update_image_listbox():
    listbox_images.delete(0, tk.END)
    for image in images:
        listbox_images.insert(tk.END, image)

def create_pdf(image_path):
    pdf = FPDF()
    pdf.add_page()

    try:
        image = Image.open(image_path)
        width, height = image.size
        aspect_ratio = width / height

        # Ajuste a largura da imagem para caber na página (retire o valor de 180 se não quiser escala)
        new_width = 180
        new_height = new_width / aspect_ratio

        pdf.image(image_path, x=10, y=10, w=new_width, h=new_height)
        
        # Obter o nome base do arquivo de imagem (sem extensão)
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Construir o nome do arquivo PDF com base no nome da imagem original
        pdf_file = os.path.join(output_folder, f"{image_name}.pdf")

        pdf.output(pdf_file)
    except Exception as e:
        error_message = f"Erro ao processar o arquivo {image_path}: {str(e)}"
        messagebox.showerror("Erro", error_message)

def convert_to_pdf():
    global images, output_folder
    if not images:
        messagebox.showwarning("Aviso", "Selecione pelo menos uma imagem.")
        return

    if not output_folder:
        messagebox.showwarning("Aviso", "Selecione a pasta de saída.")
        return

    images_to_convert = images[:]  # Copiar a lista de imagens para evitar alterações durante a conversão
    for image_path in images_to_convert:
        try:
            create_pdf(image_path)
        except Exception:
            error_message = f"Arquivo {image_path} não é um arquivo válido. Ele será excluído."
            messagebox.showerror("Erro", error_message)
            images.remove(image_path)

    if images:
        images.clear()
        update_image_listbox()
        messagebox.showinfo("Concluído", "Conversão Completa.")

# Função para selecionar a pasta de saída
def select_output_folder():
    global output_folder
    output_folder = filedialog.askdirectory(title="Selecione a pasta de saída")
    if output_folder:
        label_output_folder.config(text=f"Pasta de saída selecionada: {output_folder}")

# Configuração da janela principal
root = tk.Tk()
root.title("Image to PDF Converter")

# Configurar a estrutura visual com uma grade
frame = ttk.Frame(root, padding=10)
frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Botão para adicionar imagens
btn_add_image = ttk.Button(frame, text="Adicionar Imagem(s)", command=add_image)
btn_add_image.grid(row=0, column=0, padx=5, pady=5)

# Botão (ícone "X" em vermelho) para excluir imagens selecionadas
btn_delete_image = ttk.Button(frame, text="Excluir Arquivo", command=delete_selected_image)
btn_delete_image.grid(row=1, column=0, padx=5, pady=5)

# Botão para selecionar a pasta de saída
btn_select_output_folder = ttk.Button(frame, text="Selecionar Pasta de Saída", command=select_output_folder)
btn_select_output_folder.grid(row=2, column=0, padx=5, pady=5)

# Lista para exibir as imagens selecionadas
listbox_images = tk.Listbox(frame, selectmode=tk.MULTIPLE, width=50, height=10)
listbox_images.grid(row=3, column=0, padx=5, pady=5)

# Botão para converter imagens em PDF
btn_convert_to_pdf = ttk.Button(frame, text="Converter para PDF", command=convert_to_pdf)
btn_convert_to_pdf.grid(row=4, column=0, padx=5, pady=5)

# Rótulo para exibir a pasta de saída selecionada
label_output_folder = ttk.Label(frame, text="Selecione a pasta de saída")
label_output_folder.grid(row=5, column=0, padx=5, pady=5)

root.mainloop()
