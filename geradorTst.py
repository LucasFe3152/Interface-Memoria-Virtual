import random

def gerar_sequencial(num_paginas=10, tamanho=30):
    """Gera acessos sequenciais: 0,1,2,... repetindo."""
    seq = []
    for i in range(tamanho):
        seq.append(i % num_paginas)
    return seq

def gerar_aleatorio(num_paginas=10, tamanho=30):
    """Gera acessos totalmente aleatórios."""
    return [random.randint(0, num_paginas-1) for _ in range(tamanho)]

def gerar_localidade(num_paginas=20, tamanho=30, janela=5):
    """
    Gera acessos com localidade:
    - Escolhe um bloco de páginas pequeno (ex.: 5 páginas).
    - Fica acessando só ele por um tempo.
    - Depois troca para outro bloco.
    """
    seq = []
    i = 0
    while i < tamanho:
        inicio = random.randint(0, num_paginas-janela)
        bloco = list(range(inicio, inicio+janela))
        for _ in range(janela*2):  # repete algumas vezes
            seq.append(random.choice(bloco))
            i += 1
            if i >= tamanho:
                break
    return seq

if __name__ == "__main__":
    print("Sequencial:", gerar_sequencial())
    print("Aleatório:", gerar_aleatorio())
    print("Localidade:", gerar_localidade())
