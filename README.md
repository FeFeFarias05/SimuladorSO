# Simulador de Escalonamento MLFQ

Um simulador de escalonamento de processos implementando o algoritmo **Multilevel Feedback Queue (MLFQ)** para sistemas operacionais.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Formato de Entrada](#-formato-de-entrada)
- [Arquitetura](#-arquitetura)
- [Desenvolvimento](#-desenvolvimento)

## 🎯 Visão Geral

Este simulador implementa um escalonador multinível com feedback (MLFQ) composto por **três filas de prioridade**:

- **Fila 0**: Round Robin com quantum configurável (1-10ms) - **Maior prioridade**
- **Fila 1**: Round Robin com quantum configurável (11-20ms) - **Prioridade média**
- **Fila 2**: FCFS (First-Come, First-Served) - **Menor prioridade**

### Características Principais

- ✅ **Simulação determinística** por ticks de 1ms
- ✅ **Gerenciamento de E/S** com estados bloqueado/desbloqueado
- ✅ **Feedback automático** entre filas
- ✅ **Métricas de performance** (tempo de espera, resposta, turnaround)
- ✅ **Interface CLI** com opções verbosas
- ✅ **Testes automatizados**

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Instalação Local

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd SimuladorSO

# Instale em modo de desenvolvimento
pip install -e .

# Ou execute diretamente
python -m src.simulador_so.cli --help
```

## 💻 Uso

### Comando Básico

```bash
python -m src.simulador_so.cli --input <arquivo.json>
```

**Opções:**
- `--input`: Arquivo JSON com configuração e processos (obrigatório)
- `--verbose`: Exibe timeline completa da simulação

### Exemplo de Execução

```bash
# Execução básica
python -m src.simulador_so.cli --input examples/input_example.json

# Execução com timeline detalhada
python -m src.simulador_so.cli --input examples/input_example.json --verbose
```

## 📄 Formato de Entrada

O simulador aceita arquivos JSON com a seguinte estrutura:

```json
{
  "config": {
    "quantum_q0": 5,
    "quantum_q1": 15
  },
  "processes": [
    {
      "name": "P1",
      "cpu_burst": 4,
      "io_time": 8,
      "total_cpu_time": 12,
      "priority": 0
    }
  ]
}
```

## 🏗️ Arquitetura

### Estrutura do Projeto

```
SimuladorSO/
├── src/simulador_so/
│   ├── __init__.py          # Pacote principal
│   ├── cli.py              # Interface de linha de comando
│   ├── engine.py           # Engine de simulação
│   ├── models.py           # Modelos de dados
│   └── scheduler/
│       └── mlfq.py         # Implementação do MLFQ
├── tests/                  # Testes automatizados
├── examples/               # Exemplos de entrada
├── pyproject.toml         # Configuração do projeto
└── README.md              # Este arquivo
```

### Componentes Principais

- **`CLI`**: Interface de linha de comando com validação robusta
- **`SimulationEngine`**: Motor de simulação discreta por ticks
- **`MLFQScheduler`**: Implementação do algoritmo MLFQ
- **`Models`**: Estruturas de dados e validações

### Algoritmo MLFQ

1. **Admissão**: Todos os processos começam na Fila 0
2. **Prioridade**: Fila 0 > Fila 1 > Fila 2
3. **Round Robin**: Filas 0 e 1 usam quantum configurável
4. **FCFS**: Fila 2 executa até completar ou E/S
5. **Feedback**: Processos descem de fila ao esgotar quantum
6. **E/S**: Processos bloqueados retornam ao fim da mesma fila

## 🧪 Desenvolvimento

### Executar Testes

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Executar com cobertura
python -m pytest tests/ --cov=src/simulador_so
```

### Estrutura de Testes

- `test_smoke.py`: Teste básico de funcionamento
- `test_io_and_multiple_bursts.py`: Teste com E/S e múltiplos bursts

### Validação de Código

```bash
# Verificar linting
python -m flake8 src/

# Verificar tipos
python -m mypy src/
```

## 📈 Métricas de Performance

O simulador calcula as seguintes métricas:

- **Tempo de Espera**: Tempo total na fila de prontos
- **Tempo de Resposta**: Tempo até primeira execução
- **Tempo de Turnaround**: Tempo total de execução
- **Trocas de Contexto**: Número de mudanças de processo

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# Definir timeout máximo (padrão: 10000 ticks)
export MLFQ_MAX_TICKS=5000

# Habilitar debug
export MLFQ_DEBUG=1
```

**Desenvolvido para o TP1 de Sistemas Operacionais**
