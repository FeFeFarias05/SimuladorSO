# Sistemas Operacionais — TP1
## Simulador de Escalonador de Processos (MLFQ)

Este projeto implementa um **simulador de escalonamento de processos** para um sistema operacional hipotético, utilizando um **escalonador multinível com feedback (MLFQ)** composto por **três filas**. A proposta e as regras foram extraídas do enunciado do trabalho prático (TP1) da disciplina de Sistemas Operacionais.

> **Resumo do MLFQ**
> - Todos os processos são **admitidos na Fila 0**.
> - **Fila 0:** Round Robin (quantum **1–10 ms**).
> - **Fila 1:** Round Robin (quantum **11–20 ms**).
> - **Fila 2 (terceira fila):** **FCFS** (sem preempção; executa o processo até o fim).
> - **Prioridade entre filas:** a Fila 0 sempre é atendida antes da Fila 1; a Fila 2 só executa quando as duas anteriores estão vazias.
> - **Feedback:** se o processo **não concluir** na Fila 0, **desce** para a Fila 1; se **não concluir** na Fila 1, **desce** para a Fila 2.
> - **E/S (I/O):** ao solicitar E/S, o processo sai de execução, fica **Bloqueado** pelo tempo de E/S e retorna ao **fim da mesma fila** em que estava.
> - **Estados possíveis:** **Pronto**, **Executando**, **Bloqueado**, **Finalizado**.

> **Observação sobre a nomenclatura das filas**
> O enunciado refere-se à “Fila 3” (terceira fila) para o algoritmo FCFS. Aqui, nomeamos as filas por índice **0, 1 e 2**, sendo **Fila 2** a terceira fila (FCFS), preservando a intenção do texto original.

---

## Objetivos
- Simular a execução de **qualquer número de processos** admitidos previamente.
- Respeitar as **regras do MLFQ** quanto a quantuns, queda de fila e prioridade de atendimento.
- Reproduzir o comportamento de **E/S** e estados de processo.
- Exibir a **saída em modo texto** no terminal, de forma clara e auditável.

## Parâmetros do Escalonador
- **Quantum Fila 0:** inteiro entre **1 e 10 ms**.
- **Quantum Fila 1:** inteiro entre **11 e 20 ms**.
- **Fila 2:** FCFS (sem quantum).

## Parâmetros de Cada Processo
- `name` — Nome do processo.
- `cpu_burst` — Tempo de **surto de CPU** antes de uma E/S (ms).
- `io_time` — Tempo **bloqueado** devido à E/S (ms).
- `total_cpu_time` — Tempo total de CPU necessário (ms). Pode envolver múltiplos ciclos `CPU → E/S → CPU`.
- `priority` — Inteiro em que **menor valor = maior prioridade** (usado **apenas** para ordenar **inicialmente** os processos **na Fila 0**).

### Regras Operacionais
1. **Admissão:** todos os processos entram na **Fila 0**, ordenados por `priority` (menor primeiro).
2. **Despacho por fila:** sempre escolher a **fila mais alta** que não esteja vazia (0 → 1 → 2).
3. **Round Robin (Fila 0 e 1):** executar por no máximo `quantum` ou até:
   - o processo **consumir o burst** (`cpu_burst`) → faz **E/S** por `io_time` e retorna ao **fim da fila atual**;
   - o processo **consumir `total_cpu_time`** → **Finalizado**;
   - ao **estourar o quantum** sem finalizar → **descer** para a próxima fila.
4. **FCFS (Fila 2):** executar o processo até:
   - **E/S** (volta ao **fim da Fila 2** após `io_time`); ou
   - **Finalizar** (`total_cpu_time` zerado).

## Boas Práticas e Critérios de Qualidade
- **Programação modular** e separação clara de responsabilidades.
- **Determinismo** do simulador (mesmo input → mesma saída).
- **Testes automatizados** (unitários e de integração).
- **Logs claros** e opção de **verbose**.
- **Documentação** de parâmetros e decisões de projeto.
- **Validação de entrada** (intervalos de quantum, valores ≥ 0, etc.).

## Entrega e Apresentação
- **Entrega via Moodle** em arquivo **`.tar.gz` ou `.zip`** contendo:
- **código-fonte** e instruções de execução;
- **arquivo texto** com **nomes completos** dos integrantes.
- **Apenas um integrante** deve submeter.
- **Grupos de 3 ou 5 integrantes**.
- **Data de entrega:** **11/09**.
- **Apresentações:** **11/09** e **16/09** (ordem por sorteio na primeira data).

---

### Checklist Rápido
- [ ] Respeita quantuns e prioridade entre filas?
- [ ] Move corretamente entre filas ao estourar quantum?
- [ ] Trata E/S e retorno ao final da **mesma fila**?
- [ ] Ordena Fila 0 inicialmente por `priority` (menor = maior prioridade)?
- [ ] Exporta métricas úteis (espera, resposta, turn-around, trocas de contexto)?
- [ ] Saída em **modo texto** clara e reproduzível?
- [ ] Testes cobrindo cenários típicos e de borda?

---

**Referência:** Enunciado do TP1 de Sistemas Operacionais (resumo incluído neste README).
