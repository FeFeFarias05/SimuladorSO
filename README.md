# Simulador de Escalonador Multinível com Feedback

Este projeto implementa um simulador para escalonamento de processos em um sistema operacional hipotético, seguindo as especificações do trabalho de Sistemas Operacionais.

## 📋 Especificações Implementadas

### Algoritmo de Escalonamento
- **Escalonador Multinível com Feedback** com 3 filas
- **Fila 0**: Round Robin (quantum de 1ms a 10ms)
- **Fila 1**: Round Robin (quantum de 11ms a 20ms)  
- **Fila 3**: FCFS (First Come First Served)

### Regras de Funcionamento
1. **Todos os processos iniciam na Fila 0**
2. **Movimento entre filas**: Processos que não terminam no quantum são movidos para a fila inferior
3. **Retorno do I/O**: Processos que voltam do I/O retornam à fila original
4. **Prioridade das filas**: Fila 0 > Fila 1 > Fila 3
5. **Preempção**: Filas superiores sempre preemptam filas inferiores

### Estados dos Processos
- **Ready**: Pronto para execução
- **Running**: Em execução
- **Blocked**: Bloqueado por I/O
- **Finished**: Finalizado

## 🚀 Como Executar

### Execução Básica
```bash
python main.py
```
Executa exemplos demonstrativos que mostram o funcionamento do escalonador.

### Execução com Arquivo JSON
```bash
python main.py examples/input_example.json
```

### Execução dos Testes
```bash
python test_scheduler.py
```

## 📁 Estrutura do Projeto

```
SimuladorSO/
├── main.py                    # Programa principal com exemplos
├── process.py                 # Classe Processo
├── multilevel_scheduler.py    # Escalonador multinível
├── test_scheduler.py          # Testes do sistema
├── examples/
│   └── input_example.json     # Exemplo de entrada em JSON
├── scheduler.py               # [DEPRECATED] Escalonador antigo
└── escalonador.py            # [DEPRECATED] Escalonador antigo
```

## 📄 Formato do Arquivo JSON

```json
{
  "config": {
    "quantum_q0": 5,    // Quantum da Fila 0 (1-10ms)
    "quantum_q1": 15    // Quantum da Fila 1 (11-20ms)
  },
  "processes": [
    {
      "name": "P1",
      "cpu_burst": 2,         // Tempo de CPU burst em ms
      "io_time": 4,           // Tempo de I/O em ms (0 = sem I/O)
      "total_cpu_time": 10,   // Tempo total de CPU necessário
      "priority": 0           // Prioridade inicial (não usado no multinível)
    }
  ]
}
```

## 🔧 Parâmetros da Classe Processo

```python
Processo(nome, cpu_burst, tempo_io, tempo_total_cpu, ordem=0, prioridade=0)
```

- **nome**: Identificador do processo
- **cpu_burst**: Tempo de execução antes do I/O (0 = sem I/O)
- **tempo_io**: Tempo de bloqueio por I/O (0 = sem I/O)
- **tempo_total_cpu**: Tempo total de CPU necessário para completar
- **ordem**: Ordem de chegada (opcional)
- **prioridade**: Prioridade inicial (opcional, não usado no multinível)

## 📊 Saída do Simulador

### Linha do Tempo da CPU
Mostra qual processo estava executando em cada momento.

### Linha do Tempo dos Processos
Mostra o estado de cada processo ao longo do tempo:
- **R**: Ready (Pronto)
- **E**: Executing (Executando)
- **B**: Blocked (Bloqueado por I/O)
- **F**: Finished (Finalizado)

### Estatísticas
- **Turnaround Time**: Tempo total desde chegada até finalização
- **Tempo de Resposta**: Tempo até primeira execução

### Log de Execução
Registra eventos importantes como movimento entre filas, preempções, etc.

## 🎯 Exemplos de Uso

### Exemplo 1: Processo com I/O
```python
# Processo que faz I/O e retorna para Fila 0
processo = Processo('A', cpu_burst=2, tempo_io=3, tempo_total_cpu=8)
```

### Exemplo 2: Processo CPU-intensivo
```python
# Processo que será movido pelas filas até chegar na Fila 2 (FCFS)
processo = Processo('B', cpu_burst=0, tempo_io=0, tempo_total_cpu=20)
```

## 🔍 Casos de Teste Implementados

1. **Teste Básico**: Mistura de processos com e sem I/O
2. **Teste com Quantum Pequeno**: Demonstra movimento entre filas
3. **Teste de Preempção**: Mostra prioridade entre filas
4. **Teste com JSON**: Carregamento de configuração externa
5. **Casos Extremos**: Quantums muito pequenos, processos longos

## ✅ Conformidade com a Especificação

- ✅ Escalonador multinível com feedback (3 filas)
- ✅ Fila 0: Round Robin com quantum 1-10ms
- ✅ Fila 1: Round Robin com quantum 11-20ms
- ✅ Fila 2: FCFS
- ✅ Todos os processos iniciam na Fila 0
- ✅ Movimento para fila inferior quando quantum expira
- ✅ Retorno à Fila 0 após I/O
- ✅ Preempção baseada na prioridade das filas
- ✅ Estados: Ready, Running, Blocked, Finished

## 🐛 Observações

- Os arquivos `scheduler.py` e `escalonador.py` são da implementação anterior (baseada em créditos) e foram mantidos para referência
- O novo sistema está implementado em `multilevel_scheduler.py`
- Use `main.py` para demonstrações completas do funcionamento
