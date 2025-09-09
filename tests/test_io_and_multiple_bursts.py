from simulador_so.models import SchedulerConfig, ProcessSpec, SimulationInput
from simulador_so.engine import SimulationEngine

def test_io_and_multiple_bursts():
    config = SchedulerConfig(quantum_q0=3, quantum_q1=15)
    processes = [
        ProcessSpec(name="P1", cpu_burst=2, io_time=3, total_cpu_time=6, priority=1),
        ProcessSpec(name="P2", cpu_burst=4, io_time=2, total_cpu_time=8, priority=2),
    ]
    sim_input = SimulationInput(config=config, processes=processes)
    engine = SimulationEngine(sim_input)
    result = engine.run()
    assert result.completed
    assert "P1" in result.metrics
    assert "P2" in result.metrics
    # Verifica se turnaround é maior que total_cpu_time (devido à E/S)
    assert result.metrics["P1"]["turnaround_time"] > 6
    assert result.metrics["P2"]["turnaround_time"] > 8