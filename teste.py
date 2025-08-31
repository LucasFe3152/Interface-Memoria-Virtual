def gera_memoria_paginas(arq_out):
    from random import randint
    mem_out = []
    with open(arq_out, 'w') as arquivo:
        bits_1 = 0
        for _ in range(16):
            bit = randint(0,1)
            if bits_1 < 8 and bit == 1:
                bits_1 += 1
            else:
                bit = 0
            temp = f'{randint(0,1)}{randint(0,1)}{randint(0,1)}'
            while temp in mem_out and bit == 1:
                temp = f'{randint(0,1)}{randint(0,1)}{randint(0,1)}'
            mem_out.append(temp)
            temp = f'{temp} {bit}\n'
            print(temp)
            arquivo.write(temp)
    print(mem_out)

gera_memoria_paginas('teste_memoria.txt')