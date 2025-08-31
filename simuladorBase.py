from collections import deque

def fifo(paginas, molduras):
    memoria = deque()
    falhas = 0

    for p in paginas:
        if p not in memoria:
            falhas += 1
            if len(memoria) < molduras:
                memoria.append(p)
            else:
                memoria.popleft()
                memoria.append(p)
    return falhas

def lru(paginas, molduras):
    memoria = []
    falhas = 0

    for p in paginas:
        if p not in memoria:
            falhas += 1
            if len(memoria) < molduras:
                memoria.append(p)
            else:
                memoria.pop(0)  # remove o menos usado
                memoria.append(p)
        else:
            # atualiza ordem de uso (o usado vai pro final)
            memoria.remove(p)
            memoria.append(p)
    return falhas

if __name__ == "__main__":
    # Lê dataset de um arquivo (um número por linha)
    with open("dataset.txt") as f:
        paginas = [int(x.strip()) for x in f if x.strip()]

    molduras = 3  # alterar conforme o teste

    falhas_fifo = fifo(paginas, molduras)
    falhas_lru = lru(paginas, molduras)

    print(f"FIFO - Falhas: {falhas_fifo} | Taxa: {falhas_fifo/len(paginas):.2%}")
    print(f"LRU  - Falhas: {falhas_lru} | Taxa: {falhas_lru/len(paginas):.2%}")
