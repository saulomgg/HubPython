import csv
import tkinter as tk
from tkinter import filedialog

# Função para selecionar o arquivo CSV
def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    arquivo = filedialog.askopenfilename(title="Selecione o arquivo CSV", filetypes=[("CSV Files", "*.csv")])
    return arquivo

# Função principal para adicionar "plastico" ao nome e salvar o arquivo
def adicionar_plastico():
    # Solicita ao usuário que selecione o arquivo de entrada
    input_file = selecionar_arquivo()
    
    if not input_file:
        print("Nenhum arquivo selecionado. O processo será cancelado.")
        return
    
    # Define o arquivo de saída
    output_file = 'output.csv'  # O arquivo de saída será gerado no mesmo diretório
    
    # Abre o arquivo de entrada para leitura
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        
        # Abre o arquivo de saída para escrita
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            
            # Percorre todas as linhas do arquivo de entrada
            for row in reader:
                # Adiciona "plastico" antes do nome (primeira coluna)
                row[0] = 'Consumidor ' + row[0]
                # Escreve a linha modificada no arquivo de saída
                writer.writerow(row)
    
    print(f"Processo concluído. Arquivo gerado: {output_file}")

# Chama a função principal
adicionar_plastico()
