import tkinter as tk
from tkinter import messagebox

def calcular():
    try:
        # Obter valores inseridos pelo usuário
        nome = entry_nome.get()  # Pegar o nome inserido
        sexo = sexo_var.get()
        peso = float(entry_peso.get())
        altura = float(entry_altura.get())
        idade = int(entry_idade.get())

        # Verificar se os campos foram preenchidos corretamente
        if sexo not in ["M", "F"]:
            messagebox.showerror("Erro", "Por favor, selecione um sexo válido.")
            return

        # Calcular IMC
        imc = peso / (altura ** 2)

        # Classificação do IMC
        if imc < 18.5:
            categoria_imc = "Abaixo do peso"
            recomendacao = "É recomendado consultar um nutricionista para ganhar peso de forma saudável."
        elif 18.5 <= imc <= 24.9:
            categoria_imc = "Peso normal"
            recomendacao = "Parabéns! Continue mantendo um estilo de vida equilibrado e saudável."
        elif 25 <= imc <= 29.9:
            categoria_imc = "Sobrepeso"
            recomendacao = "Considere adotar uma dieta balanceada e praticar atividades físicas regularmente."
        else:
            categoria_imc = "Obesidade"
            recomendacao = "É importante procurar orientação médica e nutricional para melhorar sua saúde."

        # Calcular peso ideal (Fórmula de Lorentz)
        if sexo == 'M':
            peso_ideal = 50 + 0.91 * (altura * 100 - 152.4)
        else:
            peso_ideal = 45.5 + 0.91 * (altura * 100 - 152.4)

        # Exibir os resultados na interface
        resultado_texto.set(
            f"IMC: {imc:.2f} ({categoria_imc})\n"
            f"Peso Ideal: {peso_ideal:.2f} kg\n\n"
            f"Recomendação:\n{recomendacao}"
        )
        # Exibir o nome do usuário abaixo do resultado
        nome_resultado.set(f"Nome: {nome}")
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira valores válidos nos campos.")

def limpar():
    # Limpar todos os campos e o resultado
    entry_nome.delete(0, tk.END)
    entry_peso.delete(0, tk.END)
    entry_altura.delete(0, tk.END)
    entry_idade.delete(0, tk.END)
    sexo_var.set("")
    resultado_texto.set("")
    nome_resultado.set("")

def mostrar_tabela_imc():
    tabela_imc = (
        "Tabela do IMC:\n\n"
        "IMC Abaixo de 18.5: Abaixo do peso - Indica que a pessoa está abaixo do peso ideal e pode precisar ganhar peso.\n"
        "IMC de 18.5 - 24.9: Peso normal - Indica que a pessoa está dentro de um peso saudável e equilibrado.\n"
        "IMC de 25 - 29.9: Sobrepeso - A pessoa está acima do peso e pode precisar fazer ajustes na dieta e atividades físicas.\n"
        "IMC de 30 ou mais: Obesidade - A pessoa está em risco de problemas de saúde devido ao excesso de peso e pode precisar de um plano de emagrecimento."
    )
    messagebox.showinfo("Tabela do IMC", tabela_imc)

# Criar a janela principal
janela = tk.Tk()
janela.title("Calculadora de Peso Ideal e IMC")
janela.geometry("400x550")
janela.resizable(False, False)

# Título
titulo = tk.Label(janela, text="Calculadora de Peso Ideal e IMC", font=("Arial", 16, "bold"), fg="blue")
titulo.pack(pady=10)

# Nome
frame_nome = tk.Frame(janela)
frame_nome.pack(pady=5)
tk.Label(frame_nome, text="Nome:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
entry_nome = tk.Entry(frame_nome, font=("Arial", 12), width=20)
entry_nome.grid(row=0, column=1)

# Sexo
sexo_var = tk.StringVar()
frame_sexo = tk.Frame(janela)
frame_sexo.pack(pady=5)
tk.Label(frame_sexo, text="Sexo:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
tk.Radiobutton(frame_sexo, text="Masculino", variable=sexo_var, value="M", font=("Arial", 10)).grid(row=0, column=1)
tk.Radiobutton(frame_sexo, text="Feminino", variable=sexo_var, value="F", font=("Arial", 10)).grid(row=0, column=2)

# Peso
frame_peso = tk.Frame(janela)
frame_peso.pack(pady=5)
tk.Label(frame_peso, text="Peso (kg):", font=("Arial", 12)).grid(row=0, column=0, padx=5)
entry_peso = tk.Entry(frame_peso, font=("Arial", 12), width=10)
entry_peso.grid(row=0, column=1)

# Altura
frame_altura = tk.Frame(janela)
frame_altura.pack(pady=5)
tk.Label(frame_altura, text="Altura (m):", font=("Arial", 12)).grid(row=0, column=0, padx=5)
entry_altura = tk.Entry(frame_altura, font=("Arial", 12), width=10)
entry_altura.grid(row=0, column=1)

# Idade
frame_idade = tk.Frame(janela)
frame_idade.pack(pady=5)
tk.Label(frame_idade, text="Idade (anos):", font=("Arial", 12)).grid(row=0, column=0, padx=5)
entry_idade = tk.Entry(frame_idade, font=("Arial", 12), width=10)
entry_idade.grid(row=0, column=1)

# Botões
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=20)
btn_calcular = tk.Button(frame_botoes, text="Calcular", font=("Arial", 12), bg="green", fg="white", width=10, command=calcular)
btn_calcular.grid(row=0, column=0, padx=10)
btn_limpar = tk.Button(frame_botoes, text="Limpar", font=("Arial", 12), bg="red", fg="white", width=10, command=limpar)
btn_limpar.grid(row=0, column=1, padx=10)
btn_tabela_imc = tk.Button(frame_botoes, text="Ver Tabela IMC", font=("Arial", 12), bg="blue", fg="white", width=15, command=mostrar_tabela_imc)
btn_tabela_imc.grid(row=0, column=2, padx=10)

# Resultado
resultado_texto = tk.StringVar()
resultado_label = tk.Label(janela, textvariable=resultado_texto, font=("Arial", 12), fg="black", justify="left", wraplength=350)
resultado_label.pack(pady=10)

# Nome do usuário
nome_resultado = tk.StringVar()
nome_label = tk.Label(janela, textvariable=nome_resultado, font=("Arial", 12), fg="black", justify="left")
nome_label.pack(pady=10)

# Rodapé
rodape = tk.Label(janela, text="Desenvolvido por br.stampsynk.com", font=("Arial", 10), fg="gray")
rodape.pack(pady=10)

# Iniciar o loop da interface
janela.mainloop()
