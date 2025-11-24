# Simulador de Memória Paginada

Simulador de sistema de gerenciamento de memória paginada para Sistemas Operacionais.

## Como Usar

```bash
py main.py entrada.txt saida.txt
```

## Arquivo de Entrada

O arquivo `entrada.txt` contém endereços virtuais que serão usadados durante a execução. Podem ser usados valores hexadecimais e inteiros

## Arquivos do Projeto

- **`main.py`** - Programa principal
- **`MemoryConfig.py`** - Configurações do sistema (TLB, memória, segmentos)
- **`MemorySimulator.py`** - Coordena a simulação
- **`MMU.py`** - Unidade de gerenciamento de memória (MMU)
- **`TLB.py`** - Cache de traduções (Translation Lookaside Buffer)
- **`PageTableEntry.py`** - Tabela de páginas multi-nível (1, 2 ou 3 níveis)
- **`PhysicalMemory.py`** - Memória física com substituição LRU
- **`SegmentManager.py`** - Gerencia segmentos (.text, .data, .bss, .stack)
- **`AddressLoader.py`** - Gera e carrega endereços virtuais

## Funcionalidades

- **TLB** com política FIFO
- **Tabela de páginas** configurável (1-3 níveis)
- **Memória física** com substituição LRU
- **Segmentos** (.text, .data, .bss, .stack)
- **Traduções** endereço virtual → físico
- **Estatísticas** (page faults, TLB hits/misses)

## Saída

O arquivo `saida.txt` conterá:

- Configuração do sistema
- Traduções de cada endereço
- Estado da TLB e tabela de páginas
- Conteúdo da memória física
- Estatísticas de desempenho

## Requisitos

- Python 3.6+
