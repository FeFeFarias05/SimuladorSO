from process import Processo

def teste_metodos_separados():
    """Teste focado apenas nos diferentes métodos de criação de processos"""
    print("=== Testando criação de processos com parâmetros individuais ===\n")
    
    # Criando processos com parâmetros individuais
    processo1 = Processo('P1', 5, 3, 15, 1, 2)
    print(f"Processo 1: {processo1}\n")
    
    processo2 = Processo('P2', 8, 4, 20, 2, 1)
    print(f"Processo 2: {processo2}\n")
    
    processo3 = Processo('P3', 10, "-", 25, 3, 3)  # Teste com tempo_io = "-"
    print(f"Processo 3 (sem I/O): {processo3}\n")

if __name__ == "__main__":
    teste_metodos_separados()
