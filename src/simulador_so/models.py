from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict


class ProcessState(Enum):
    """Estados possíveis de um processo durante a simulação."""
    READY = auto()
    RUNNING = auto()
    BLOCKED = auto()
    FINISHED = auto()


@dataclass
class ProcessSpec:
    name: str
    cpu_burst: int
    io_time: int
    total_cpu_time: int
    priority: int

    def validate(self) -> None:
        """Valida os dados do processo."""
        if not self.name or not self.name.strip():
            raise ValueError("Nome do processo não pode estar vazio")
        
        if self.cpu_burst < 0:
            raise ValueError(f"cpu_burst deve ser >= 0, recebido: {self.cpu_burst}")
        if self.io_time < 0:
            raise ValueError(f"io_time deve ser >= 0, recebido: {self.io_time}")
        if self.total_cpu_time < 0:
            raise ValueError(f"total_cpu_time deve ser >= 0, recebido: {self.total_cpu_time}")
        
        if self.cpu_burst == 0 and self.total_cpu_time > 0:
            raise ValueError("Processo com cpu_burst=0 mas total_cpu_time>0 é inválido")


@dataclass
class SchedulerConfig:
    """
        quantum_q0: Quantum da fila 0 (1-10 ms)
        quantum_q1: Quantum da fila 1 (11-20 ms)
    """
    quantum_q0: int
    quantum_q1: int

    def validate(self) -> None:
        """Valida os parâmetros do escalonador."""
        if not (1 <= self.quantum_q0 <= 10):
            raise ValueError(f"quantum_q0 deve estar entre 1 e 10 ms, recebido: {self.quantum_q0}")
        if not (11 <= self.quantum_q1 <= 20):
            raise ValueError(f"quantum_q1 deve estar entre 11 e 20 ms, recebido: {self.quantum_q1}")


@dataclass
class ProcessRuntime:
    spec: ProcessSpec
    remaining_cpu_time: int
    remaining_burst_time: int
    state: ProcessState = ProcessState.READY
    current_queue: int = 0
    remaining_io_time: int = 0

    # Métricas de performance
    first_response_time: Optional[int] = None
    waiting_time: int = 0
    turnaround_time: Optional[int] = None


@dataclass
class SimulationInput:
    config: SchedulerConfig
    processes: List[ProcessSpec]

    def validate(self) -> None:
        """Valida a entrada da simulação."""
        if not self.processes:
            raise ValueError("Lista de processos não pode estar vazia")
        
        # Verificar nomes únicos
        names = [p.name for p in self.processes]
        if len(names) != len(set(names)):
            raise ValueError("Nomes de processos devem ser únicos")
        
        self.config.validate()
        for p in self.processes:
            p.validate()


@dataclass
class SimulationResult:
    completed: bool
    timeline: List[Dict[str, str]] = field(default_factory=list)
    metrics: Dict[str, Dict[str, int]] = field(default_factory=dict)
    context_switches: int = 0


