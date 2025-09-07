from __future__ import annotations

from typing import List, Dict

from .models import (
    ProcessRuntime,
    ProcessSpec,
    ProcessState,
    SchedulerConfig,
    SimulationInput,
    SimulationResult,
)
from .scheduler.mlfq import MLFQScheduler


class SimulationEngine:
    """Engine de simulação discreta por ticks de 1 ms.

    Implementa regras essenciais do MLFQ: prioridade entre filas, 
    quantum nas filas 0 e 1, FCFS na 2, E/S e estados.
    """

    def __init__(self, sim_input: SimulationInput):
        sim_input.validate()
        self.input = sim_input
        self.scheduler = MLFQScheduler(sim_input.config)
        self.time_ms: int = 0
        self.timeline: List[Dict[str, str]] = []

        # criar runtimes e admitir na fila 0 (ordenados por prioridade)
        ordered_specs = sorted(sim_input.processes, key=lambda p: p.priority)
        self.procs: List[ProcessRuntime] = [
            ProcessRuntime(
                spec=p,
                remaining_cpu_time=p.total_cpu_time,
                remaining_burst_time=p.cpu_burst,
            )
            for p in ordered_specs
        ]
        for pr in self.procs:
            self.scheduler.admit(pr)

    def _all_finished(self) -> bool:
        return all(p.state == ProcessState.FINISHED for p in self.procs)

    def _tick_blocked(self) -> None:
        for p in self.procs:
            if p.state == ProcessState.BLOCKED:
                if p.remaining_io_time > 0:
                    p.remaining_io_time -= 1
                if p.remaining_io_time == 0:
                    p.state = ProcessState.READY
                    p.remaining_burst_time = min(p.spec.cpu_burst, p.remaining_cpu_time)
                    self.scheduler.requeue_same_level(p)

    def _tick_ready_wait(self) -> None:
        for p in self.procs:
            p.on_tick_wait()

    def run(self, max_ticks: int = 10_000) -> SimulationResult:
        while not self._all_finished() and self.time_ms < max_ticks:
            self._tick_blocked()

            current = self.scheduler.pick_next()
            if current is None:
                # ocioso
                self.timeline.append({"t": str(self.time_ms), "event": "IDLE"})
                self.time_ms += 1
                continue

            # executar um timeslice
            quantum = self.scheduler.quantum_for(current)
            current.state = ProcessState.RUNNING
            if current.first_response_time is None:
                current.first_response_time = self.time_ms

            ran = 0
            while True:
                # um tick de CPU
                current.remaining_cpu_time -= 1
                current.remaining_burst_time -= 1
                ran += 1
                self.timeline.append({
                    "t": str(self.time_ms),
                    "run": current.spec.name,
                    "q": str(current.current_queue),
                })
                self.time_ms += 1
                self._tick_blocked()
                self._tick_ready_wait()

                if current.remaining_cpu_time == 0:
                    current.state = ProcessState.FINISHED
                    current.turnaround_time = self.time_ms
                    break

                if current.remaining_burst_time == 0:
                    # entra em E/S e volta ao fim da mesma fila
                    current.state = ProcessState.BLOCKED
                    current.remaining_io_time = current.spec.io_time
                    current.time_in_current_quantum = 0
                    break

                # verifica quantum para filas 0 e 1
                if quantum is not None:
                    if ran >= quantum:
                        current.state = ProcessState.READY
                        current.time_in_current_quantum = 0
                        self.scheduler.requeue_after_timeslice(current)
                        break
                # FCFS (fila 2): segue até burst fim ou terminar (verificado acima)

        # montar métricas simples
        metrics: Dict[str, Dict[str, int]] = {}
        for p in self.procs:
            metrics[p.spec.name] = {
                "waiting_time": p.waiting_time,
                "response_time": (p.first_response_time or 0),
                "turnaround_time": (p.turnaround_time or self.time_ms),
            }

        return SimulationResult(
            completed=self._all_finished(),
            timeline=self.timeline,
            metrics=metrics,
        )


