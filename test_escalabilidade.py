from simulador.processo import Processo
from simulador.mlfq import MLFQ

def test_ordem_fila_0():
    p1 = Processo("A", 5, 10, 20, 2)
    p2 = Processo("B", 5, 10, 20, 1)
    p3 = Processo("C", 5, 10, 20, 0)
    mlfq = MLFQ([p1, p2, p3], 5, 15)
    assert mlfq.filas[0][0].name == "C"
    assert mlfq.filas[0][1].name == "B"
    assert mlfq.filas[0][2].name == "A"

def test_desce_fila():
    p = Processo("A", 20, 10, 40, 0)
    mlfq = MLFQ([p], 5, 15)
    mlfq.run()
    assert p.estado == "Finalizado"

def test_io_retorna_mesma_fila():
    p = Processo("A", 5, 10, 20, 0)
    mlfq = MLFQ([p], 5, 15)
    mlfq.run()
    assert p.estado == "Finalizado"