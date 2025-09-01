import tkinter as tk
from collections import deque
import math

# Configuração dinâmica
TAMANHO_PAGINA = 4 * 1024  # 4 KB fixo
tabela_paginas = {}
quadros_ocupados = deque()  # Fila FIFO das páginas na RAM

# Mem fisica - 32 kB, virtual - 64 kB
TAM_MEM_FISICA = 32 * 1024
TAM_MEM_VIRTUAL = 2 * TAM_MEM_FISICA
NUM_QUADROS = 8  # Máximo de 8 quadros físicos
NUM_PAGINAS_VIRTUAIS = 16  # 16 páginas virtuais (0-15)

def carrega_memoria_paginas():
    """Carrega a tabela de páginas inicial do arquivo"""
    global tabela_paginas, quadros_ocupados
    
    arq_path = entry_arq_tabela.get().strip()
    if not arq_path:
        lbl_resultado.config(text="Erro: Selecione um arquivo primeiro!")
        return
    
    try:
        # Resetar estruturas
        tabela_paginas = {}
        quadros_ocupados = deque()
        
        with open(arq_path, 'r') as arquivo:
            pagina = 0
            for linha in arquivo:
                linha = linha.strip()
                if linha and pagina < NUM_PAGINAS_VIRTUAIS:
                    temp = linha.split()
                    if len(temp) >= 2:
                        # Converter quadro de binário para decimal
                        quadro = int(temp[0], 2)  # base 2 (binário)
                        valido = int(temp[1])
                        
                        # Validar se o quadro está dentro do limite
                        if quadro >= NUM_QUADROS and valido == 1:
                            lbl_resultado.config(text=f"Erro: Quadro {quadro} ({temp[0]} binário) inválido (máximo {NUM_QUADROS-1})")
                            return
                        
                        tabela_paginas[pagina] = {"quadro": quadro, "valido": valido}
                        
                        # Se a página está válida, adicionar à fila FIFO
                        if valido == 1:
                            quadros_ocupados.append(pagina)
                        
                        pagina += 1
        
        # Preencher páginas restantes se houver menos de 16 no arquivo
        while pagina < NUM_PAGINAS_VIRTUAIS:
            tabela_paginas[pagina] = {"quadro": 0, "valido": 0}
            pagina += 1
        
        atualizar_tabela()
        paginas_validas = sum(1 for p in tabela_paginas.values() if p["valido"] == 1)
        lbl_resultado.config(text=f"Tabela carregada: {len(tabela_paginas)} páginas virtuais, {paginas_validas} na RAM")
        
    except FileNotFoundError:
        lbl_resultado.config(text="Erro: Arquivo não encontrado!")
    except Exception as e:
        lbl_resultado.config(text=f"Erro ao carregar arquivo: {str(e)}")

def encontrar_quadro_livre():
    """Encontra um quadro livre que não está sendo usado"""
    quadros_usados = set()
    for pagina, dados in tabela_paginas.items():
        if dados["valido"] == 1:
            quadros_usados.add(dados["quadro"])
    
    for quadro in range(NUM_QUADROS):
        if quadro not in quadros_usados:
            return quadro
    return None

def acessar_endereco():
    """Processa o acesso a um endereço virtual"""
    global quadros_ocupados

    if not tabela_paginas:
        lbl_resultado.config(text="⚠ Carregue a tabela de páginas primeiro!")
        return

    try:
        endereco_virtual = int(entry_endereco.get(), 16)
    except ValueError:
        lbl_resultado.config(text="Erro: digite um valor hexadecimal (ex: 0x0A)")
        return

    pagina_virtual = endereco_virtual // TAMANHO_PAGINA
    deslocamento = endereco_virtual % TAMANHO_PAGINA

    if pagina_virtual >= NUM_PAGINAS_VIRTUAIS:
        lbl_resultado.config(text=f"Erro: endereço {hex(endereco_virtual)} fora da memória virtual!\nPáginas válidas: 0-{NUM_PAGINAS_VIRTUAIS-1}")
        return

    log = f"\n"
    log += f"Página virtual: {pagina_virtual}, Deslocamento: {deslocamento}\n"

    # Verificar se a página já está na memória física
    if tabela_paginas[pagina_virtual]["valido"] == 1:
        # HIT - página já está na RAM
        quadro = tabela_paginas[pagina_virtual]["quadro"]
        endereco_fisico = quadro * TAMANHO_PAGINA + deslocamento
        log += f"✅ HIT! Página {pagina_virtual} já está no quadro {quadro}.\n"
        log += f"Endereço físico: {hex(endereco_fisico)}"
    else:
        # PAGE FAULT - página não está na RAM
        log += f"❌ PAGE FAULT! Página {pagina_virtual} não está na RAM.\n"
        
        # Contar quantas páginas estão atualmente na RAM
        paginas_na_ram = sum(1 for dados in tabela_paginas.values() if dados["valido"] == 1)
        
        if paginas_na_ram < NUM_QUADROS:
            # Há espaço livre na RAM
            quadro = encontrar_quadro_livre()
            if quadro is None:
                lbl_resultado.config(text="Erro: Não foi possível encontrar quadro livre!")
                return
            log += f"Usando quadro livre {quadro}.\n"
        else:
            # RAM cheia - necessário substituir uma página (FIFO)
            if not quadros_ocupados:
                lbl_resultado.config(text="Erro: Nenhuma página para substituir!")
                return
                
            pagina_removida = quadros_ocupados.popleft()
            quadro = tabela_paginas[pagina_removida]["quadro"]
            
            # Invalidar a página removida
            tabela_paginas[pagina_removida]["valido"] = 0
            log += f"FIFO: Removendo página {pagina_removida} do quadro {quadro}.\n"

        # Carregar a nova página na RAM
        tabela_paginas[pagina_virtual]["quadro"] = quadro
        tabela_paginas[pagina_virtual]["valido"] = 1
        quadros_ocupados.append(pagina_virtual)
        
        endereco_fisico = quadro * TAMANHO_PAGINA + deslocamento
        log += f"Página {pagina_virtual} carregada no quadro {quadro}.\n"
        

    atualizar_tabela()
    lbl_resultado.config(text=log)
    destacar_enderecos(endereco_virtual, endereco_fisico, pagina_virtual, quadro, deslocamento)

def gerar_arquivo_exemplo():
    """Gera um arquivo de exemplo no formato correto"""
    arquivo_exemplo = """000 0
001 0
110 1
101 1
001 0
011 1
010 1
110 0
001 0
100 1
100 0
101 0
110 0
011 0
111 1
100 0"""
    
    try:
        with open("tabela_exemplo.txt", "w") as f:
            f.write(arquivo_exemplo)
        lbl_resultado.config(text="Arquivo 'tabela_exemplo.txt' gerado!\nFormato: quadro_binário validade")
        entry_arq_tabela.delete(0, tk.END)
        entry_arq_tabela.insert(0, "tabela_exemplo.txt")
    except Exception as e:
        lbl_resultado.config(text=f"Erro ao gerar arquivo: {str(e)}")

def atualizar_tabela():
    """Atualiza a exibição da tabela de páginas"""
    # Limpar tabela atual
    for widget in frame_tabela.winfo_children():
        widget.destroy()
        
    LARG_TABELA = 15
    TAM_FONTE_TABELA = 11

    # Cabeçalho
    tk.Label(frame_tabela, text="Página", width=LARG_TABELA, borderwidth=1, relief="solid", bg="lightgray", font=("Arial", TAM_FONTE_TABELA, "bold")).grid(row=0, column=0)
    tk.Label(frame_tabela, text="Quadro", width=LARG_TABELA, borderwidth=1, relief="solid", bg="lightgray", font=("Arial", TAM_FONTE_TABELA, "bold")).grid(row=0, column=1)
    tk.Label(frame_tabela, text="Válido", width=LARG_TABELA, borderwidth=1, relief="solid", bg="lightgray", font=("Arial", TAM_FONTE_TABELA, "bold")).grid(row=0, column=2)

    # Dados da tabela - mostrar todas as 16 páginas virtuais
    for pagina in range(NUM_PAGINAS_VIRTUAIS):
        if pagina in tabela_paginas:
            dados = tabela_paginas[pagina]
            
            # Cores diferentes para páginas válidas e inválidas
            color = "lightgreen" if dados["valido"] == 1 else "lightcoral"
            
            tk.Label(frame_tabela, text=str(pagina), width=LARG_TABELA, borderwidth=1, 
                    relief="solid", bg=color, font=("Arial", TAM_FONTE_TABELA)).grid(row=pagina+1, column=0)
            
            quadro_texto = f"{dados['quadro']} ({bin(dados['quadro'])[2:].zfill(3)})" if dados["valido"] == 1 else "-"
            tk.Label(frame_tabela, text=quadro_texto, width=LARG_TABELA, borderwidth=1, 
                    relief="solid", bg=color, font=("Arial", TAM_FONTE_TABELA)).grid(row=pagina+1, column=1)
            
            tk.Label(frame_tabela, text=str(dados["valido"]), width=LARG_TABELA, borderwidth=1, 
                    relief="solid", bg=color, font=("Arial", TAM_FONTE_TABELA)).grid(row=pagina+1, column=2)
        else:
            # Página não carregada ainda
            tk.Label(frame_tabela, text=str(pagina), width=LARG_TABELA, borderwidth=1, 
                    relief="solid", bg="lightgray", font=("Arial", TAM_FONTE_TABELA)).grid(row=pagina+1, column=0)
            tk.Label(frame_tabela, text="-", width=LARG_TABELA, borderwidth=1, 
                    relief="solid", bg="lightgray", font=("Arial", TAM_FONTE_TABELA)).grid(row=pagina+1, column=1)
            tk.Label(frame_tabela, text="0", width=LARG_TABELA, borderwidth=1, 
                    relief="solid", bg="lightgray", font=("Arial", TAM_FONTE_TABELA)).grid(row=pagina+1, column=2)

def destacar_enderecos(end_virtual, end_fisico, pagina_virtual, quadro, deslocamento):
    """Mostra endereços virtual e físico com destaque por cores"""
    txt_saida.config(state="normal")
    txt_saida.delete("1.0", tk.END)

    # Converter para hexadecimal
    hex_virtual = f"{end_virtual:04x}".upper()
    hex_fisico = f"{end_fisico:04x}".upper()
    
    # Para páginas de 4KB, temos 12 bits de deslocamento (3 dígitos hex)
    digitos_deslocamento = 3
    
    # Separar página/quadro do deslocamento
    if len(hex_virtual) > digitos_deslocamento:
        virt_pagina = hex_virtual[:-digitos_deslocamento]
        virt_desloc = hex_virtual[-digitos_deslocamento:]
    else:
        virt_pagina = "0"
        virt_desloc = hex_virtual.zfill(digitos_deslocamento)
        
    if len(hex_fisico) > digitos_deslocamento:
        fis_quadro = hex_fisico[:-digitos_deslocamento]
        fis_desloc = hex_fisico[-digitos_deslocamento:]
    else:
        fis_quadro = "0"
        fis_desloc = hex_fisico.zfill(digitos_deslocamento)

    # Exibir endereços com cores
    txt_saida.insert(tk.END, "Endereço Virtual:  0x")
    txt_saida.insert(tk.END, virt_pagina, "azul")
    txt_saida.insert(tk.END, virt_desloc, "vermelho")
    txt_saida.insert(tk.END, f"  (Página {pagina_virtual})\n")

    txt_saida.insert(tk.END, "Endereço Físico:   0x")
    txt_saida.insert(tk.END, fis_quadro, "azul")
    txt_saida.insert(tk.END, fis_desloc, "vermelho")
    txt_saida.insert(tk.END, f"  (Quadro {quadro})\n\n")
    
    # Informações binarias para melhor entendimento
    txt_saida.insert(tk.END, f"Página {pagina_virtual} → Quadro {quadro}\n")
    txt_saida.insert(tk.END, f"Deslocamento: {deslocamento} bytes\n\n")
    
    txt_saida.insert(tk.END, "Legenda:\n")
    txt_saida.insert(tk.END, "Azul", "azul")
    txt_saida.insert(tk.END, " = Index | ")
    txt_saida.insert(tk.END, "Vermelho", "vermelho")
    txt_saida.insert(tk.END, " = Deslocamento")

    txt_saida.config(state="disabled")

# Interface Tkinter
root = tk.Tk()
root.title("Simulador de Paginação FIFO - 16 Páginas Virtuais, 8 Quadros Físicos")

# Frame principal
frame_principal = tk.Frame(root)
frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

# Esquerda -> Endereços destacados
frame_esquerda = tk.Frame(frame_principal, bg="lightblue", width=300)
frame_esquerda.grid(row=0, column=0, sticky="nsew", padx=(0,5))
frame_esquerda.pack_propagate(False)

# Centro -> Controles
frame_centro = tk.Frame(frame_principal, bg="white", width=300)
frame_centro.grid(row=0, column=1, sticky="nsew", padx=5)
frame_centro.pack_propagate(False)

# Direita -> Tabela
frame_direita = tk.Frame(frame_principal, bg="lightyellow", width=350)
frame_direita.grid(row=0, column=2, sticky="nsew", padx=(5,0))
frame_direita.pack_propagate(False)

# Configurar pesos
frame_principal.grid_columnconfigure(0, weight=2)
frame_principal.grid_columnconfigure(1, weight=2)
frame_principal.grid_columnconfigure(2, weight=1)
frame_principal.grid_rowconfigure(0, weight=1)

# === PAINEL ESQUERDO - ENDEREÇOS ===
lbl_enderecos = tk.Label(frame_esquerda, text="Tradução de Endereços", 
                        bg="lightblue", font=("Arial", 14, "bold"))
lbl_enderecos.pack(pady=10)

txt_saida = tk.Text(frame_esquerda, height=12, width=45, font=("Courier", 11))
txt_saida.tag_config("azul", foreground="blue", font=("Courier", 10, "bold"))
txt_saida.tag_config("vermelho", foreground="red", font=("Courier", 10, "bold"))
txt_saida.config(state="disabled")
txt_saida.pack(pady=10, padx=10)

# === PAINEL CENTRO - CONTROLES ===
# Informações do sistema
info_frame = tk.Frame(frame_centro)
info_frame.pack(pady=10)

tk.Label(info_frame, text=f"Configuração do Sistema", font=("Arial", 12, "bold")).pack()
tk.Label(info_frame, text=f"Páginas virtuais: {NUM_PAGINAS_VIRTUAIS} (64 KB)").pack()
tk.Label(info_frame, text=f"Quadros físicos: {NUM_QUADROS} (32 KB)").pack()
tk.Label(info_frame, text=f"Tamanho da página: {TAMANHO_PAGINA//1024} KB").pack()
tk.Label(info_frame, text=f"Formato arquivo: quadro_binário validade").pack()

# Botão para gerar arquivo exemplo
btn_exemplo = tk.Button(frame_centro, text="Gerar Arquivo Exemplo", command=gerar_arquivo_exemplo, bg="lightcyan")
btn_exemplo.pack(pady=10)

# Controles de arquivo
tk.Label(frame_centro, text="Arquivo da tabela de páginas:").pack(pady=(10,5))
entry_arq_tabela = tk.Entry(frame_centro, width=25)
entry_arq_tabela.pack(pady=5)
btn_arq = tk.Button(frame_centro, text="Carregar Tabela", command=carrega_memoria_paginas, bg="lightyellow")
btn_arq.pack(pady=5)

# Controles de endereço
tk.Label(frame_centro, text="Endereço virtual (hex):").pack(pady=(20,5))
entry_endereco = tk.Entry(frame_centro, width=15)
entry_endereco.pack(pady=5)

btn = tk.Button(frame_centro, text="Acessar Endereço", command=acessar_endereco, bg="lightgreen")
btn.pack(pady=10)

# Resultado
lbl_resultado = tk.Label(frame_centro, text="Clique em 'Gerar Arquivo Exemplo' para começar", 
                        bg="white", font=("Arial", 10), wraplength=280, justify="left")
lbl_resultado.pack(pady=10)

# === PAINEL DIREITA - TABELA ===
tk.Label(frame_direita, text="Tabela de Páginas", bg="lightyellow", font=("Arial", 12, "bold")).pack(pady=10)

# Frame com scrollbar para a tabela
canvas = tk.Canvas(frame_direita, bg="lightyellow")
scrollbar = tk.Scrollbar(frame_direita, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

frame_tabela = scrollable_frame

canvas.pack(side="left", fill="both", expand=True, padx=5)
scrollbar.pack(side="right", fill="y")

# Bind Enter para acessar endereço
entry_endereco.bind('<Return>', lambda e: acessar_endereco())

# Inicializar tabela vazia
atualizar_tabela()

root.mainloop()