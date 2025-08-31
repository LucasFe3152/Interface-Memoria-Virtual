import tkinter as tk
from collections import deque
import math

# Configuração dinâmica
TAMANHO_PAGINA = 4 * 1024  # 4 KB fixo
tabela_paginas = {}
quadros = deque()
proximo_quadro = 0

# Mem fisica - 32 kB, virtual - 64 kB
TAM_MEM_FISICA = 32 * 1024
TAM_MEM_VIRTUAL = 2 * TAM_MEM_FISICA
NUM_QUADROS = TAM_MEM_FISICA // TAMANHO_PAGINA
NUM_PAGINAS_VIRTUAIS = TAM_MEM_VIRTUAL // TAMANHO_PAGINA

memoria_atual = []

def carrega_memoria_paginas():
    arq_path = entry_arq_tabela.get().strip()
    pagina = 0
    arquivo = open(arq_path, 'r')
    linha = arquivo.readline()
    while linha != '':
        temp = linha.split(' ')
        if '\n' in temp[1]:
            temp[1] = temp[1].replace('\n', '')
        #memoria_atual.append(temp)
        quadro = int(temp[0].strip())
        valido = int(temp[1].strip())
        tabela_paginas[pagina] = {"quadro": quadro, "valido": valido}
        print(temp)
        linha = arquivo.readline()
        pagina += 1
    arquivo.close()
    atualizar_tabela()
    return memoria_atual
        
def get_dec(num):
    return int(str(num), 2)

def acessar_endereco():
    global proximo_quadro

    if NUM_QUADROS == 0:
        lbl_resultado.config(text="⚠ Configure a memória primeiro!")
        return

    try:
        endereco_virtual = int(entry_endereco.get(), 16)
    except ValueError:
        lbl_resultado.config(text="Erro: digite um valor hexadecimal (ex: 0x0A)")
        return

    pagina_virtual = endereco_virtual // TAMANHO_PAGINA
    deslocamento = endereco_virtual % TAMANHO_PAGINA

    if pagina_virtual >= NUM_PAGINAS_VIRTUAIS:
        lbl_resultado.config(text=f"Erro: endereço {hex(endereco_virtual)} fora da memória virtual!")
        return

    log = f"Endereço virtual {hex(endereco_virtual)}\n"
    log += f"Página virtual: {pagina_virtual}, Deslocamento: {deslocamento}\n"

    if pagina_virtual in tabela_paginas and tabela_paginas[pagina_virtual]["valido"] == 1:
        quadro = tabela_paginas[pagina_virtual]["quadro"]
        endereco_fisico = quadro * TAMANHO_PAGINA + deslocamento
        log += f"✅ HIT! Página {pagina_virtual} já está no quadro {get_dec(quadro)}.\n"
        log += f"Endereço físico: {hex(endereco_fisico)}"
    else:
        log += f"❌ PAGE FAULT! Página {pagina_virtual} não está na RAM.\n"
        if len(quadros) < NUM_QUADROS:
            quadro = proximo_quadro
            proximo_quadro += 1
        else:
            pagina_removida = quadros.popleft()
            quadro = tabela_paginas[pagina_removida]["quadro"]
            del tabela_paginas[pagina_removida]["quadro"]
            log += f"Substituindo página {pagina_removida} do quadro {get_dec(quadro)}.\n"

        tabela_paginas[pagina_virtual] = {"quadro": quadro, "valido": 1}
        quadros.append(pagina_virtual)
        endereco_fisico = quadro * TAMANHO_PAGINA + deslocamento
        log += f"Página {pagina_virtual} carregada no quadro {quadro}.\n"
        log += f"Endereço físico: {hex(endereco_fisico)}"

    atualizar_tabela()
    lbl_resultado.config(text=log)
    destacar_enderecos(endereco_virtual, endereco_fisico, pagina_virtual, quadro, deslocamento)


def atualizar_tabela():
    for widget in frame_tabela.winfo_children():
        widget.destroy()

    tk.Label(frame_tabela, text="Página", width=10, borderwidth=1, relief="solid").grid(row=0, column=0)
    tk.Label(frame_tabela, text="Quadro", width=10, borderwidth=1, relief="solid").grid(row=0, column=1)
    tk.Label(frame_tabela, text="Bit", width=10, borderwidth=1, relief="solid").grid(row=0, column=2)

    for pagina, dados in tabela_paginas.items():
        tk.Label(frame_tabela, text=str(pagina), width=10, borderwidth=1, relief="solid").grid(row=pagina+1, column=0)
        tk.Label(frame_tabela, text=get_bin(dados["quadro"]), width=10, borderwidth=1, relief="solid").grid(row=pagina+1, column=1)
        tk.Label(frame_tabela, text=str(dados["valido"]), width=10, borderwidth=1, relief="solid").grid(row=pagina+1, column=2)

def get_bin(num):
    return str(num).zfill(3)
    
def destacar_enderecos(end_virtual, end_fisico, pagina_virtual, quadro, deslocamento):
    """
    Mostra endereço virtual e físico em hex, destacando:
    - Parte traduzida (página/quadro) em azul
    - Parte deslocamento em vermelho
    """
    hex_virtual = f"{end_virtual:#06x}"  # 0x0000 formato fixo
    hex_fisico = f"{end_fisico:#06x}"

    # Calcular tamanhos em dígitos
    pagina_hex = f"{pagina_virtual:x}"
    quadro_hex = f"{quadro:x}"
    desloc_hex = f"{deslocamento:x}"

    # Para simplificação: dividir string em 2 partes (prefixo traduzido, deslocamento)
    # Exemplo: 0x1A3C → 0x[1A] (azul) [3C] (vermelho)
    virt_prefix = hex_virtual[:-len(desloc_hex)] if desloc_hex != "0" else hex_virtual
    virt_suffix = hex_virtual[-len(desloc_hex):] if desloc_hex != "0" else ""

    fis_prefix = hex_fisico[:-len(desloc_hex)] if desloc_hex != "0" else hex_fisico
    fis_suffix = hex_fisico[-len(desloc_hex):] if desloc_hex != "0" else ""

    # Criar texto colorido no Tkinter
    txt_saida.config(state="normal")
    txt_saida.delete("1.0", tk.END)

    txt_saida.insert(tk.END, "Endereço Virtual: ")
    txt_saida.insert(tk.END, virt_prefix, "azul")
    txt_saida.insert(tk.END, virt_suffix, "vermelho")
    txt_saida.insert(tk.END, "\n")

    txt_saida.insert(tk.END, "Endereço Físico:  ")
    txt_saida.insert(tk.END, fis_prefix, "azul")
    txt_saida.insert(tk.END, fis_suffix, "vermelho")
    txt_saida.insert(tk.END, "\n")

    txt_saida.config(state="disabled")


# Interface Tkinter
root = tk.Tk()
root.title("Simulador de Paginação - FIFO")

# Frame principal (dividido em 2 colunas)
frame_principal = tk.Frame(root)
frame_principal.pack(fill="both", expand=True)

# Esquerda -> Endereços destacados
frame_esquerda = tk.Frame(frame_principal, bg="lightblue", width=600, height=2400)
frame_esquerda.grid(row=0, column=0, sticky="nswe")
frame_esquerda.pack_propagate(False)

# Centro -> Tabela de páginas
frame_centro = tk.Frame(frame_principal, bg="white", width=600, height=2400)
frame_centro.grid(row=0, column=1, sticky="nswe")
frame_centro.pack_propagate(False)


# Ajustar pesos das colunas (para expandirem bem)
frame_principal.grid_columnconfigure(0, weight=1)  # esquerda
frame_principal.grid_columnconfigure(1, weight=1)  # centro
frame_principal.grid_columnconfigure(2, weight=1)  # direita

tk.Label(frame_centro, text=f"Tamanho da página (KB): {TAMANHO_PAGINA//1024}").pack(pady=3)
tk.Label(frame_centro, text=f"Tamanho da memória física (KB): {TAM_MEM_FISICA//1024}").pack(pady=5)
tk.Label(frame_centro, text=f"Tamanho da memória virtual (KB): {TAM_MEM_VIRTUAL//1024}").pack(pady=4)

tk.Label(frame_centro, text="Digite arquivo da tabela:").pack(pady=5)
entry_arq_tabela = tk.Entry(frame_centro)
entry_arq_tabela.pack(pady=5)
btn_arq = tk.Button(frame_centro, text="Selecionar Arquivo", command=carrega_memoria_paginas)
btn_arq.pack(pady=5)


tk.Label(frame_centro, text="Digite endereço virtual (hex):").pack(pady=5)
entry_endereco = tk.Entry(frame_centro)
entry_endereco.pack(pady=5)

btn = tk.Button(frame_centro, text="Acessar Endereço", command=acessar_endereco)
btn.pack(pady=5)

lbl_resultado = tk.Label(frame_centro, text="Tabela de Páginas", bg="white", font=("Arial", 12, "bold"))
lbl_resultado.pack(pady=10)

frame_tabela = tk.Frame(frame_centro)
frame_tabela.pack(pady=10)

lbl_enderecos = tk.Label(frame_esquerda, text="Endereços (Virtual → Físico)", bg="lightblue", font=("Courier", 12))
lbl_enderecos.pack(pady=10)

txt_saida = tk.Text(frame_esquerda, height=4, width=40, font=("Consolas", 12))
txt_saida.tag_config("azul", foreground="blue")
txt_saida.tag_config("vermelho", foreground="red")
txt_saida.config(state="disabled")
txt_saida.pack(pady=10)


root.mainloop()
