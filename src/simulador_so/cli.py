from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import SchedulerConfig, ProcessSpec, SimulationInput
from .engine import SimulationEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulador de Escalonador MLFQ (TP1)",
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Arquivo JSON com config e processos",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe timeline completa",
    )
    return parser.parse_args()


def load_input(path: str) -> SimulationInput:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    cfg = SchedulerConfig(
        quantum_q0=data["config"]["quantum_q0"],
        quantum_q1=data["config"]["quantum_q1"],
    )
    procs = [
        ProcessSpec(
            name=p["name"],
            cpu_burst=p["cpu_burst"],
            io_time=p["io_time"],
            total_cpu_time=p["total_cpu_time"],
            priority=p["priority"],
        )
        for p in data["processes"]
    ]
    return SimulationInput(config=cfg, processes=procs)


def main() -> None:
    args = parse_args()
    sim_input = load_input(args.input)
    engine = SimulationEngine(sim_input)
    result = engine.run()

    print("completed:", result.completed)
    if args.verbose:
        for e in result.timeline:
            print(e)
    print("metrics:")
    print(f"{'Processo':<10} {'Espera':>7} {'Resposta':>9} {'Turnaround':>11}")
    for name, m in result.metrics.items():
        print(f"{name:<10} {m['waiting_time']:>7} {m['response_time']:>9} {m['turnaround_time']:>11}")
    print(f"Trocas de contexto: {result.context_switches}")

if __name__ == "__main__":
    main()


