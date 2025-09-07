from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Optional

from ..models import (
    ProcessRuntime,
    ProcessState,
    SchedulerConfig,
)


class MLFQScheduler:
    """Esqueletro do Escalonador Multinível com Feedback (MLFQ).

    Filas:
      - 0: Round Robin (quantum_q0)
      - 1: Round Robin (quantum_q1)
      - 2: FCFS
    """

    def __init__(self, config: SchedulerConfig):
        self.config = config
        self.queues: Dict[int, Deque[ProcessRuntime]] = {
            0: deque(),
            1: deque(),
            2: deque(),
        }

    def admit(self, proc: ProcessRuntime) -> None:
        proc.current_queue = 0
        self.queues[0].append(proc)

    def has_ready(self) -> bool:
        return any(len(q) > 0 for q in self.queues.values())

    def pick_next(self) -> Optional[ProcessRuntime]:
        for level in (0, 1, 2):
            if self.queues[level]:
                proc = self.queues[level].popleft()
                return proc
        return None

    def requeue_after_timeslice(self, proc: ProcessRuntime) -> None:
        if proc.current_queue == 0:
            proc.current_queue = 1
            self.queues[1].append(proc)
        elif proc.current_queue == 1:
            proc.current_queue = 2
            self.queues[2].append(proc)
        else:
            # FCFS: volta ao fim da fila 2
            self.queues[2].append(proc)

    def requeue_same_level(self, proc: ProcessRuntime) -> None:
        self.queues[proc.current_queue].append(proc)

    def quantum_for(self, proc: ProcessRuntime) -> Optional[int]:
        if proc.current_queue == 0:
            return self.config.quantum_q0
        if proc.current_queue == 1:
            return self.config.quantum_q1
        return None  # FCFS


