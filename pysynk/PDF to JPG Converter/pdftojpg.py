import os
from tkinter import Tk, filedialog
import fitz  # PyMuPDF

def convert_pdfs_to_jpg():
    # Inicializa a janela do Tkinter
    Tk().withdraw()

    # Selecionar múltiplos arquivos PDF
    file_paths = filedialog.askopenfilenames(
        title="Selecione os arquivos PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )

    # Verifica se foram selecionados arquivos
    if not file_paths:
        print("Nenhum arquivo selecionado.")
        return

    # Cria uma pasta de saída para salvar os JPGs
    output_folder = filedialog.askdirectory(
        title="Selecione a pasta para salvar os arquivos JPG"
    )
    if not output_folder:
        print("Nenhuma pasta selecionada.")
        return

    # Converte cada PDF em imagens JPG
    for pdf_file in file_paths:
        try:
            # Abre o PDF
            pdf_document = fitz.open(pdf_file)
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]

            # Converte cada página para imagem
            for page_number in range(len(pdf_document)):
                page = pdf_document[page_number]
                pix = page.get_pixmap(dpi=300)  # Define a qualidade da imagem (300 DPI)
                output_path = os.path.join(output_folder, f"{base_name}_page_{page_number+1}.jpg")
                pix.save(output_path)
                print(f"Página {page_number+1} de {base_name} salva como JPG em {output_path}.")
            
            pdf_document.close()
        except Exception as e:
            print(f"Erro ao converter {pdf_file}: {e}")

if __name__ == "__main__":
    convert_pdfs_to_jpg()
