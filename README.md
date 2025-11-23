# Simulador de Gerência de Memória - Modular

Arquivos gerados:
- tlb.py: módulo da TLB (FIFO, entradas = 2^bits, bits cap 0..6 => 1..64 entradas)
- pagetable.py: módulo de tabela de páginas multi-nível (1..3)
- physmem.py: módulo de memória física (vetor inicializado com -1, LRU)
- segments.py: cálculo de segmentos (.text, .data, .stack, .bss)
- simulator.py: executável principal que produz **quatro** arquivos separados:
    - <prefix>_tlb.txt
    - <prefix>_pagetable.txt
    - <prefix>_physmem.txt
    - <prefix>_simulator.txt

Como testar (exemplo):
```
python simulator.py --tlb-bits 3 --virt-bits 16 --phys-bits 14 --page-bits 8 --pt-levels 2 --infile enderecos.txt --out-prefix out/test
```
Isso criará `out/test_tlb.txt`, `out/test_pagetable.txt`, `out/test_physmem.txt` e `out/test_simulator.txt` no diretório atual.

O arquivo `enderecos.txt` fornecido contém endereços de teste (decimais e hex).
