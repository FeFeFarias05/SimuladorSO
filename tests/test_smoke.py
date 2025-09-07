from simulador_so.models import SchedulerConfig, ProcessSpec, SimulationInput
from simulador_so.engine import SimulationEngine


def test_smoke_run():
    cfg = SchedulerConfig(quantum_q0=5, quantum_q1=15)
    procs = [
        ProcessSpec(name="P1", cpu_burst=3, io_time=5, total_cpu_time=6, priority=0),
        ProcessSpec(name="P2", cpu_burst=4, io_time=3, total_cpu_time=4, priority=1),
    ]
    sim_in = SimulationInput(config=cfg, processes=procs)
    engine = SimulationEngine(sim_in)
    result = engine.run(max_ticks=1000)
    assert result.completed is True
    assert "P1" in result.metrics and "P2" in result.metrics


