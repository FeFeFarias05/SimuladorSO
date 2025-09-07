from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict


class ProcessState(Enum):
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
        if not self.name:
            raise ValueError("name vazio")
        if self.cpu_burst < 0 or self.io_time < 0 or self.total_cpu_time < 0:
            raise ValueError("valores devem ser >= 0")


@dataclass
class SchedulerConfig:
    quantum_q0: int
    quantum_q1: int

    def validate(self) -> None:
        if not (1 <= self.quantum_q0 <= 10):
            raise ValueError("quantum_q0 deve estar entre 1 e 10 ms")
        if not (11 <= self.quantum_q1 <= 20):
            raise ValueError("quantum_q1 deve estar entre 11 e 20 ms")


@dataclass
class ProcessRuntime:
    spec: ProcessSpec
    remaining_cpu_time: int
    remaining_burst_time: int
    state: ProcessState = ProcessState.READY
    current_queue: int = 0
    time_in_current_quantum: int = 0
    remaining_io_time: int = 0

    # métricas
    first_response_time: Optional[int] = None
    waiting_time: int = 0
    turnaround_time: Optional[int] = None

    def on_tick_wait(self) -> None:
        if self.state == ProcessState.READY:
            self.waiting_time += 1


@dataclass
class SimulationInput:
    config: SchedulerConfig
    processes: List[ProcessSpec]

    def validate(self) -> None:
        self.config.validate()
        for p in self.processes:
            p.validate()


@dataclass
class SimulationResult:
    completed: bool
    timeline: List[Dict[str, str]] = field(default_factory=list)
    metrics: Dict[str, Dict[str, int]] = field(default_factory=dict)


