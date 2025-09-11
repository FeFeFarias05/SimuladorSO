# Simulador de Escalonador Multinível com Feedback

Simulador de escalonamento de processos implementando o algoritmo Multinível com Feedback conforme especificação do trabalho de Sistemas Operacionais.

## 🎯 Algoritmo Implementado

**Escalonador Multinível com Feedback** - 3 filas:
- **Fila 0**: Round Robin (quantum 1-10ms) 
- **Fila 1**: Round Robin (quantum 11-20ms)
- **Fila 2**: FCFS

**Regras**:
- Todos os processos iniciam na Fila 0
- Quantum expirado → desce para fila inferior
- Após I/O → retorna para fila original
- Preempção: Fila 0 > Fila 1 > Fila 2

## 🚀 Como Executar

```bash
# Executar com arquivo JSON
python main.py examples/input_example.json

# Executar testes
python test_scheduler.py

# Teste de escalabilidade
python test_escalabilidade.py
```

## � Formato do JSON

```json
{
  "config": {
    "quantum_q0": 5,
    "quantum_q1": 15
  },
  "processes": [
    {
      "name": "P1",
      "cpu_burst": 2,
      "io_time": 4,
      "total_cpu_time": 10,
      "priority": 0
    }
  ]
}
```

##  Saída do Simulador

- **Linha do tempo da CPU**: Qual processo executou em cada momento
- **Estados dos processos**: R (Ready), E (Executando), B (Bloqueado), F (Finalizado)
- **Estatísticas**: Turnaround time, tempo de resposta
- **Log de eventos**: Movimentos entre filas, preempções, I/O

## 📁 Arquivos Principais

- `main.py` - Programa principal
- `process.py` - Classe Processo
- `multilevel_scheduler.py` - Escalonador multinível
- `test_scheduler.py` - Testes do sistema
- `test_escalabilidade.py` - Testes de performance
- `examples/input_example.json` - Exemplo de entrada
