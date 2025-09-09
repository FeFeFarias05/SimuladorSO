def validar_quantum(quantum_0, quantum_1):
    if not (1 <= quantum_0 <= 10):
        raise ValueError("Quantum da Fila 0 deve ser entre 1 e 10 ms")
    if not (11 <= quantum_1 <= 20):
        raise ValueError("Quantum da Fila 1 deve ser entre 11 e 20 ms")