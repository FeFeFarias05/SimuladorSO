from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Optional

from ..models import (
    ProcessRuntime,
    SchedulerConfig,
)

class MLFQScheduler:
    """Esqueletro do Escalonador Multinível com Feedback (MLFQ).

    Implementa três filas de prioridade:
    - Fila 0: Round Robin com quantum_q0 (maior prioridade)
    - Fila 1: Round Robin com quantum_q1 (prioridade média)  
    - Fila 2: FCFS (menor prioridade)

    Processos começam na fila 0 e são rebaixados após esgotar o quantum.
    """

    HIGH_PRIORITY_QUEUE = 0
    MEDIUM_PRIORITY_QUEUE = 1
    LOW_PRIORITY_QUEUE = 2

    def __init__(self, config: SchedulerConfig):
        self.config = config
        self.queues: Dict[int, Deque[ProcessRuntime]] = {
            self.HIGH_PRIORITY_QUEUE: deque(),
            self.MEDIUM_PRIORITY_QUEUE: deque(),
            self.LOW_PRIORITY_QUEUE: deque(),
        }

    def admit(self, proc: ProcessRuntime) -> None:
        "Admite um processo na fila de maior prioridade."

        proc.current_queue = self.HIGH_PRIORITY_QUEUE
        self.queues[self.HIGH_PRIORITY_QUEUE].append(proc)

    def pick_next(self) -> Optional[ProcessRuntime]:
        "Seleciona o próximo processo para execução."
        # Verifica filas em ordem de prioridade (0 > 1 > 2)
        for queue_level in (self.HIGH_PRIORITY_QUEUE, self.MEDIUM_PRIORITY_QUEUE, self.LOW_PRIORITY_QUEUE):
            if self.queues[queue_level]:
                return self.queues[queue_level].popleft()
        return None

    def requeue_after_timeslice(self, proc: ProcessRuntime) -> None:
        "Reenfileira processo após esgotar o quantum (rebaixamento)."
        if proc.current_queue == self.HIGH_PRIORITY_QUEUE:
            # Rebaixa da fila 0 para fila 1
            proc.current_queue = self.MEDIUM_PRIORITY_QUEUE
            self.queues[self.MEDIUM_PRIORITY_QUEUE].append(proc)
        elif proc.current_queue == self.MEDIUM_PRIORITY_QUEUE:
            # Rebaixa da fila 1 para fila 2
            proc.current_queue = self.LOW_PRIORITY_QUEUE
            self.queues[self.LOW_PRIORITY_QUEUE].append(proc)
        else:
            # FCFS: volta ao fim da fila 2 (não há rebaixamento)
            self.queues[self.LOW_PRIORITY_QUEUE].append(proc)

    def requeue_same_level(self, proc: ProcessRuntime) -> None:
        "Reenfileira processo na mesma fila (após E/S)."
        self.queues[proc.current_queue].append(proc)

    def quantum_for(self, proc: ProcessRuntime) -> Optional[int]:
        "Retorna o quantum para o processo baseado na fila atual."

        if proc.current_queue == self.HIGH_PRIORITY_QUEUE:
            return self.config.quantum_q0
        elif proc.current_queue == self.MEDIUM_PRIORITY_QUEUE:
            return self.config.quantum_q1
        else:
            return None  # FCFS na fila 2


