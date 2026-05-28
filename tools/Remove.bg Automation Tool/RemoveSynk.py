import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from removebg import RemoveBg
from PIL import Image, ImageTk
import os
import threading

# --- Configurações Globais ---
SINGLE_INPUT_IMAGE_PATH = "" 
BATCH_INPUT_FOLDER_PATH = "" 
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png')

# --- Funções de Lógica ---

def update_status_single(text, color):
    """Função auxiliar para atualizar o status da aba Única."""
    lbl_single_status.config(text=text, fg=color)
    root.update()

def update_status_batch(text, color):
    """Função auxiliar para atualizar o status da aba Lote."""
    lbl_batch_status.config(text=text, fg=color)
    root.update()

def process_single_image(api_key, input_path):
    """Processa uma única imagem e salva no mesmo diretório."""
    
    update_status_single("Processando... Aguarde.", "orange")
    
    try:
        rmbg = RemoveBg(api_key, "single_error.log") 
        
        # A API salva automaticamente como [nome_original]_no_bg.png
        rmbg.remove_background_from_img_file(
            input_path, 
            size="auto"
        )

        # Calcula o caminho de saída gerado automaticamente
        base_name = os.path.basename(input_path)
        dir_name = os.path.dirname(input_path)
        name, _ = os.path.splitext(base_name)
        output_path = os.path.join(dir_name, f"{name}_no_bg.png")
        
        # Exibe a imagem processada
        try:
            img_out = Image.open(output_path)
            img_out.thumbnail((250, 250))
            img_tk_out = ImageTk.PhotoImage(img_out)
            lbl_image.config(image=img_tk_out)
            lbl_image.image = img_tk_out 
            
            messagebox.showinfo(
                "Sucesso!", 
                f"Fundo removido com sucesso!\nSalvo em: {output_path}"
            )
            update_status_single(f"Fundo removido. Salvo em: {os.path.basename(output_path)}", "green")
            
        except Exception:
            messagebox.showinfo(
                "Sucesso (Sem Pré-visualização)", 
                f"Fundo removido com sucesso, mas a pré-visualização falhou.\nSalvo em: {output_path}"
            )
            update_status_single(f"Fundo removido. Salvo em: {os.path.basename(output_path)}", "green")
            
    except Exception as e:
        messagebox.showerror("Erro da API", f"Ocorreu um erro: {e}")
        update_status_single("Erro ao processar a imagem.", "red")

# --- Lógica de Imagem Única (ABA 1) ---

def select_single_image():
    """Abre uma caixa de diálogo para selecionar o arquivo de imagem."""
    global SINGLE_INPUT_IMAGE_PATH
    
    file_path = filedialog.askopenfilename(
        title="Selecione a Imagem",
        filetypes=(("Arquivos de Imagem", "*.jpg;*.jpeg;*.png"), ("Todos os arquivos", "*.*"))
    )
    
    if file_path:
        SINGLE_INPUT_IMAGE_PATH = file_path
        
        update_status_single(f"Imagem Selecionada: {os.path.basename(file_path)}", "blue")
        
        try:
            img = Image.open(SINGLE_INPUT_IMAGE_PATH)
            img.thumbnail((250, 250)) 
            img_tk = ImageTk.PhotoImage(img)
            lbl_image.config(image=img_tk)
            lbl_image.image = img_tk 
        except Exception:
            lbl_image.config(text="Erro ao carregar pré-visualização.")
            lbl_image.image = None

def start_single_process():
    """Inicia o processamento da imagem única em uma thread separada."""
    api_key = entry_api_key.get()
    
    if not api_key or not SINGLE_INPUT_IMAGE_PATH:
        messagebox.showerror("Erro", "Por favor, insira a chave de API e selecione uma imagem.")
        return

    threading.Thread(target=process_single_image, args=(api_key, SINGLE_INPUT_IMAGE_PATH)).start()

# --- Lógica de Processamento em Lote (ABA 2) ---

def select_batch_input_folder():
    """Abre uma caixa de diálogo para selecionar a pasta de ENTRADA para o lote."""
    global BATCH_INPUT_FOLDER_PATH
    
    folder_path = filedialog.askdirectory(title="1. Selecione a PASTA DE ENTRADA (Lote)")
    
    if folder_path:
        BATCH_INPUT_FOLDER_PATH = folder_path
        # Mudado para tk.Label, portanto 'fg' funciona
        lbl_batch_input_folder.config(text=f"Pasta de Entrada: {os.path.basename(folder_path)}", fg="darkblue")

def process_batch_images_core(api_key, input_folder, output_folder):
    """Executa a lógica de processamento em lote."""
    
    total_processed = 0
    total_failed = 0
    
    try:
        rmbg = RemoveBg(api_key, "batch_error.log") 
        
        for filename in os.listdir(input_folder):
            if filename.lower().endswith(ALLOWED_EXTENSIONS):
                
                input_path = os.path.join(input_folder, filename)
                name, _ = os.path.splitext(filename)
                output_path = os.path.join(output_folder, f"{name}_no_bg.png")
                
                update_status_batch(f"Processando: {filename}...", "orange")
                
                try:
                    rmbg.remove_background_from_img_file(
                        input_path, 
                        size="auto",
                        output_path=output_path 
                    )
                    total_processed += 1
                except Exception:
                    total_failed += 1
                    
        # Fim do Loop
        messagebox.showinfo(
            "Lote Concluído!", 
            f"Processamento em lote finalizado.\nProcessados: {total_processed}\nFalhas: {total_failed}"
        )
        update_status_batch(f"Lote concluído. Sucesso: {total_processed}. Falhas: {total_failed}", "green")
            
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Ocorreu um erro no processamento: {e}")
        update_status_batch("ERRO CRÍTICO no Lote.", "red")
    
    # Reabilita o botão após o processamento
    btn_batch_process.config(state=tk.NORMAL)


def start_batch_process():
    """Inicia o processamento em lote e pede a pasta de saída."""
    
    api_key = entry_api_key.get()
    
    if not api_key or not BATCH_INPUT_FOLDER_PATH:
        messagebox.showerror("Erro", "Por favor, insira a chave de API e selecione a pasta de entrada.")
        return

    # Pergunta pela Pasta de Saída
    output_folder = filedialog.askdirectory(title="2. Selecione a PASTA DE SAÍDA (Onde Salvar os Resultados)")
    
    if not output_folder:
        messagebox.showwarning("Atenção", "Processamento cancelado. Nenhuma pasta de saída selecionada.")
        return

    # Desabilita o botão para evitar cliques múltiplos
    btn_batch_process.config(state=tk.DISABLED)
    update_status_batch("INICIANDO processamento em segundo plano...", "blue")
    
    # Cria a pasta de saída se necessário
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Inicia a função de processamento em uma thread
    threading.Thread(target=process_batch_images_core, args=(api_key, BATCH_INPUT_FOLDER_PATH, output_folder)).start()


# --- Configuração da Interface (Tkinter) ---

root = tk.Tk()
root.title("Remove.bg Automation Tool")
root.geometry("600x650") 
root.resizable(False, False)

# Configuração de Estilos (para botões e outros widgets TTK)
style = ttk.Style()
style.theme_use('clam') 
style.configure('Process.TButton', font=('Arial', 12, 'bold'), foreground='white', background='green')
style.configure('Batch.TButton', font=('Arial', 12, 'bold'), foreground='white', background='#FFA500') # Laranja

# --- Estrutura Comum (Chave de API) ---

frame_api = ttk.Frame(root, padding="10")
frame_api.pack(fill='x', pady=10)

ttk.Label(frame_api, text="Chave de API (remove.bg):", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
entry_api_key = ttk.Entry(frame_api, width=50, show="*") 
entry_api_key.pack(side=tk.LEFT, padx=10)

# --- Notebook (Abas) ---

notebook = ttk.Notebook(root)
notebook.pack(pady=10, padx=10, fill='both', expand=True)

# ----------------------------------------------------
# 📌 ABA 1: IMAGEM ÚNICA 
# ----------------------------------------------------

tab_single = ttk.Frame(notebook, padding="10")
notebook.add(tab_single, text='  Imagem Única  ')

# Botão Selecionar Imagem
btn_select = ttk.Button(tab_single, text="1. Selecionar Imagem", command=select_single_image)
btn_select.pack(pady=10)

# Rótulo de Status (AGORA É tk.Label)
lbl_single_status = tk.Label(tab_single, text="Nenhuma imagem selecionada.", fg="blue")
lbl_single_status.pack(pady=5)

# Área de Visualização da Imagem
lbl_image = ttk.Label(tab_single, text="Pré-visualização (250x250)", relief="solid", padding=5, width=30)
lbl_image.pack(pady=10)

# Botão de Processamento
btn_process_single = ttk.Button(tab_single, text="2. REMOVER FUNDO E SALVAR", command=start_single_process, style='Process.TButton')
btn_process_single.pack(pady=20)


# ----------------------------------------------------
# 📌 ABA 2: PROCESSAMENTO EM LOTE
# ----------------------------------------------------

tab_batch = ttk.Frame(notebook, padding="10")
notebook.add(tab_batch, text='  Processamento em Lote  ')

# Botão Selecionar Pasta de Entrada
btn_batch_input = ttk.Button(tab_batch, text="1. Selecionar PASTA DE ENTRADA (Lote)", command=select_batch_input_folder)
btn_batch_input.pack(pady=10)

# Rótulo da Pasta de Entrada (AGORA É tk.Label)
lbl_batch_input_folder = tk.Label(tab_batch, text="Pasta de Entrada: Nenhuma selecionada.", fg="darkblue")
lbl_batch_input_folder.pack(pady=5)

# Botão de Processamento em Lote (Pede a pasta de saída ao ser clicado)
btn_batch_process = ttk.Button(tab_batch, text="2. INICIAR LOTE (Pede a Pasta de Saída)", command=start_batch_process, style='Batch.TButton')
btn_batch_process.pack(pady=30)

# Rótulo de Status do Lote (AGORA É tk.Label)
lbl_batch_status = tk.Label(tab_batch, text="Pronto para iniciar o processamento em lote.", fg="red", font=('Arial', 10, 'italic'))
lbl_batch_status.pack(pady=5)

# Iniciar o loop principal da interface
root.mainloop()