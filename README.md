# Simulador de Sistema de Gerenciamento de Memória Paginada

## Descrição

Este projeto implementa um simulador completo de um sistema de gerenciamento de memória paginada de um sistema operacional. O simulador recebe uma sequência de endereços virtuais e apresenta os endereços físicos correspondentes, demonstrando o funcionamento da TLB (Translation Lookaside Buffer), tabela de páginas multi-nível e memória física com substituição LRU.

## Características Principais

- **TLB (Translation Lookaside Buffer)**: Cache de traduções com política de substituição FIFO
- **Tabela de Páginas Multi-nível**: Suporte para 1, 2 ou 3 níveis
- **Memória Física**: Alocação sob demanda com substituição LRU (Least Recently Used)
- **Segmentos de Memória**: `.text`, `.data`, `.bss` e `.stack`
- **Configuração Parametrizável**: Todos os tamanhos são configuráveis em potências de 2

## Estrutura do Projeto

```
.
├── config.py              # Configuração do sistema de memória
├── tlb.py                 # Implementação da TLB
├── page_table.py          # Tabela de páginas multi-nível
├── physical_memory.py     # Memória física com LRU
├── segment_manager.py     # Gerenciador de segmentos
├── mmu.py                 # Memory Management Unit
├── address_generator.py   # Gerador de endereços virtuais
├── simulator.py           # Coordenador da simulação
├── main.py                # Ponto de entrada do programa
└── README.md              # Este arquivo
```

## Requisitos

- Python 3.6 ou superior
- Nenhuma dependência externa (usa apenas biblioteca padrão)

## Instalação

Não é necessária instalação. Basta ter Python 3 instalado e clonar/baixar os arquivos.

## Uso

### Uso Básico

```bash
# Executar simulação com arquivo de entrada
python main.py -i enderecos.txt -o resultado.txt

# Gerar 100 endereços aleatórios e executar simulação
python main.py -g 100 -o resultado.txt
```

### Opções de Linha de Comando

#### Modo de Operação
- `-i, --input FILE`: Arquivo de entrada com endereços virtuais
- `-g, --generate N`: Gerar N endereços aleatórios

#### Arquivos de Saída
- `-o, --output FILE`: Arquivo de saída com resultados (padrão: `output.txt`)
- `--output-addresses FILE`: Arquivo para salvar endereços gerados (padrão: `addresses.txt`)
- `--json FILE`: Exportar estado final em JSON

#### Geração de Endereços
- `--generate-only`: Apenas gerar endereços sem executar simulação
- `--locality F`: Fator de localidade (0.0-1.0) para geração
- `--seed N`: Semente para geração aleatória

#### Configuração da TLB
- `--tlb-bits N`: Bits para número de entradas (padrão: 2 → 4 entradas)

#### Configuração da Memória
- `--virtual-bits N`: Bits para espaço virtual (padrão: 16 → 64KB)
- `--physical-bits N`: Bits para memória física (padrão: 14 → 16KB)
- `--page-bits N`: Bits para tamanho da página (padrão: 10 → 1KB)

#### Configuração dos Segmentos
- `--text-bits N`: Bits para segmento .text (padrão: 12 → 4KB)
- `--data-bits N`: Bits para segmento .data (padrão: 11 → 2KB)
- `--stack-bits N`: Bits para segmento .stack (padrão: 11 → 2KB)
- Segmento .bss é calculado automaticamente: (text + data + stack) × 3

#### Configuração da Tabela de Páginas
- `--page-table-levels {1,2,3}`: Número de níveis (padrão: 2)

#### Outras Opções
- `--show-config`: Mostrar configuração e sair
- `-q, --quiet`: Modo silencioso

### Exemplos de Uso

#### 1. Simulação Básica

```bash
# Gerar 50 endereços e simular
python main.py -g 50 -o resultado.txt
```

#### 2. Simulação com Localidade

```bash
# Gerar endereços com 80% de localidade temporal
python main.py -g 100 --locality 0.8 -o resultado_localidade.txt
```

#### 3. Configuração Personalizada

```bash
python main.py -g 200 -o saida.txt \
  --virtual-bits 18 \
  --physical-bits 16 \
  --page-bits 12 \
  --tlb-bits 3 \
  --page-table-levels 3
```

#### 4. Apenas Gerar Arquivo de Endereços

```bash
python main.py --generate-only -g 1000 --output-addresses meus_enderecos.txt
```

#### 5. Usar Arquivo de Entrada Próprio

```bash
python main.py -i meus_enderecos.txt -o resultado.txt --json estado.json
```

## Formato dos Arquivos

### Arquivo de Entrada (Endereços Virtuais)

Um endereço por linha, em decimal ou hexadecimal:

```
4096
8192
0x2000
16384
0x5000
```

### Arquivo de Saída

O arquivo de saída contém:

1. **Configuração do Sistema**: Parâmetros utilizados
2. **Traduções de Endereços**: Cada tradução mostra:
   - Endereço virtual → Endereço físico
   - Segmento acessado
   - VPN → Frame
   - Offset
   - Se foi TLB hit ou miss
   - Se houve page fault
3. **Conteúdo da TLB**: Entradas atuais
4. **Conteúdo da Tabela de Páginas**: Todos os mapeamentos VPN → Frame
5. **Conteúdo da Memória Física**: Estado de cada moldura
6. **Estatísticas**: 
   - Total de traduções
   - Page faults e taxa
   - TLB hits/misses e taxa
   - Utilização da memória
   - Substituições de página

## Geração de Endereços

O simulador inclui um gerador de endereços com diferentes padrões:

```python
from config import MemoryConfig
from address_generator import AddressGenerator

config = MemoryConfig()
generator = AddressGenerator(config, seed=42)

# Sequência aleatória
addrs = generator.generate_sequence(100)

# Sequência com localidade
addrs = generator.generate_locality_sequence(100, locality_factor=0.8)

# Sequência sequencial
addrs = generator.generate_sequential_pattern('text', 50, stride=4)

# Salvar em arquivo
generator.save_to_file(addrs, "enderecos.txt")
```

## Uso como Biblioteca

Você também pode usar o simulador como biblioteca Python:

```python
from config import MemoryConfig
from simulator import MemorySimulator

# Criar configuração personalizada
config = MemoryConfig(
    tlb_entries_bits=3,      # 8 entradas na TLB
    virtual_addr_bits=20,     # 1MB espaço virtual
    physical_addr_bits=18,    # 256KB memória física
    page_size_bits=12,        # 4KB páginas
    page_table_levels=3       # 3 níveis
)

# Criar simulador
simulator = MemorySimulator(config)

# Executar simulação
simulator.run_simulation('entrada.txt', 'saida.txt')

# Exportar estado em JSON
simulator.export_state_json('estado.json')
```

## Detalhes de Implementação

### TLB (Translation Lookaside Buffer)
- Política de substituição: **FIFO** (First In, First Out)
- Armazena traduções VPN → Frame mais recentes
- Atualizada em cada acesso à memória

### Tabela de Páginas
- Suporta 1, 2 ou 3 níveis de hierarquia
- Inicializada com valores -1 (entradas livres)
- Preenchida sob demanda (apenas páginas acessadas)
- Bits divididos igualmente entre os níveis

### Memória Física
- Molduras inicializadas com -1 (livres)
- Alocação sob demanda
- Política de substituição: **LRU** (Least Recently Used)
- Rastreamento de timestamp de último acesso

### Segmentos de Memória
- `.text`: Código do programa
- `.data`: Dados inicializados
- `.bss`: Dados não inicializados (calculado como 3× a soma dos outros)
- `.stack`: Pilha (cresce do topo para baixo)

## Exemplo de Saída

```
================================================================================
SIMULADOR DE GERENCIAMENTO DE MEMÓRIA PAGINADA
Data: 23/11/2025 15:30:45
================================================================================

CONFIGURAÇÃO DO SISTEMA
--------------------------------------------------------------------------------
TLB:
  - Entradas: 4 (2 bits)

Memória:
  - Espaço Virtual: 65536 bytes (16 bits)
  - Memória Física: 16384 bytes (14 bits)
  - Tamanho da Página: 1024 bytes (10 bits)
  - Páginas Virtuais: 64
  - Molduras Físicas: 16

Segmentos:
  - .text: 4096 bytes [0 - 4,095]
  - .data: 2048 bytes [4,096 - 6,143]
  - .bss:  24576 bytes [6,144 - 30,719]
  - .stack: 2048 bytes [63,488 - 65,535]

Tabela de Páginas:
  - Níveis: 2
  - Bits por nível: [3, 3]

================================================================================
TRADUÇÕES DE ENDEREÇOS
================================================================================

[1] Virtual: 0x001000 -> Physical: 0x000000 | Segment: .text | VPN: 4 -> Frame: 0 | Offset: 0 | Source: Page Table [PAGE FAULT]
[2] Virtual: 0x002000 -> Physical: 0x000400 | Segment: .text | VPN: 8 -> Frame: 1 | Offset: 0 | Source: Page Table [PAGE FAULT]
...

================================================================================
ESTATÍSTICAS
================================================================================
Total de traduções:        50
Page Faults:               20 (40.00%)

TLB:
  Hits:                    30 (60.00%)
  Misses:                  20
  Entradas atuais:         4/4

Memória Física:
  Molduras totais:         16
  Molduras em uso:         15
  Molduras livres:         1
  Utilização:              93.75%
  Substituições de página: 5
```

## Autores

Projeto desenvolvido para a disciplina de Sistemas Operacionais.

## Licença

Este projeto é livre para uso educacional.
