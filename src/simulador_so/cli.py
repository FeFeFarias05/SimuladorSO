from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .models import SchedulerConfig, ProcessSpec, SimulationInput
from .engine import SimulationEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulador de Escalonador MLFQ (TP1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python -m simulador_so --input input.json
  python -m simulador_so --input input.json --verbose
        """
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Arquivo JSON com configuração e processos",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe timeline completa da simulação",
    )
    return parser.parse_args()


def load_json_file(path: str) -> dict:
    "Carrega e valida arquivo JSON."

    try:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        
        data = json.loads(file_path.read_text(encoding="utf-8"))
        
        # Validar estrutura básica
        if "config" not in data:
            raise KeyError("Campo 'config' não encontrado no JSON")
        if "processes" not in data:
            raise KeyError("Campo 'processes' não encontrado no JSON")
        
        return data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSON inválido em {path}: {e.msg}", e.doc, e.pos)


def create_scheduler_config(data: dict) -> SchedulerConfig:
    "Cria configuração do escalonador a partir dos dados JSON."
    config_data = data["config"]
    return SchedulerConfig(
        quantum_q0=config_data["quantum_q0"],
        quantum_q1=config_data["quantum_q1"],
    )


def create_processes(data: dict) -> list[ProcessSpec]:
    "Cria lista de processos a partir dos dados JSON."

    processes = []
    for i, proc_data in enumerate(data["processes"]):
        try:
            proc = ProcessSpec(
                name=proc_data["name"],
                cpu_burst=proc_data["cpu_burst"],
                io_time=proc_data["io_time"],
                total_cpu_time=proc_data["total_cpu_time"],
                priority=proc_data["priority"],
            )
            processes.append(proc)
        except KeyError as e:
            raise KeyError(f"Campo obrigatório ausente no processo {i+1}: {e}")
    
    return processes


def load_input(path: str) -> SimulationInput:
    "Carrega entrada da simulação a partir de arquivo JSON."
    
    data = load_json_file(path)
    config = create_scheduler_config(data)
    processes = create_processes(data)
    
    return SimulationInput(config=config, processes=processes)


def print_timeline(timeline: list[dict]) -> None:
    "Imprime a timeline da simulação."

    print("\n=== TIMELINE DA SIMULAÇÃO ===")
    for event in timeline:
        if "event" in event:
            print(f"t={event['t']}: {event['event']}")
        else:
            print(f"t={event['t']}: {event['run']} (fila {event['q']})")


def print_metrics(metrics: dict[str, dict[str, int]]) -> None:
    "Imprime as métricas de performance."

    print("\n=== MÉTRICAS DE PERFORMANCE ===")
    print(f"{'Processo':<12} {'Espera':>8} {'Resposta':>10} {'Turnaround':>12}")
    print("-" * 50)
    
    for name, m in sorted(metrics.items()):
        print(f"{name:<12} {m['waiting_time']:>8} {m['response_time']:>10} {m['turnaround_time']:>12}")


def print_summary(result) -> None:
    "Imprime resumo da simulação."
    
    print(f"\n=== RESUMO ===")
    print(f"Simulação concluída: {'Sim' if result.completed else 'Não'}")
    print(f"Trocas de contexto: {result.context_switches}")


def main() -> None:
    """Função principal do simulador."""
    try:
        args = parse_args()
        sim_input = load_input(args.input)
        
        print("=== SIMULADOR MLFQ ===")
        print(f"Arquivo de entrada: {args.input}")
        print(f"Processos: {len(sim_input.processes)}")
        print(f"Quantum Q0: {sim_input.config.quantum_q0}ms")
        print(f"Quantum Q1: {sim_input.config.quantum_q1}ms")
        
        engine = SimulationEngine(sim_input)
        result = engine.run()
        
        if args.verbose:
            print_timeline(result.timeline)
        
        print_metrics(result.metrics)
        print_summary(result)
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


