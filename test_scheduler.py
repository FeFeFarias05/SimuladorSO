from process import Processo
from multilevel_scheduler import EscalonadorMultinivel
import json

def main():
    """Função principal para testes do escalonador multinível"""
    
    print("=== TESTE DO ESCALONADOR MULTINÍVEL COM FEEDBACK ===\n")
    
    A = Processo('A', 2, 5, 6, 1, 0)  # CPU burst 2ms, I/O 5ms, total 6ms
    B = Processo('B', 3, 10, 6, 2, 0)  # CPU burst 3ms, I/O 10ms, total 6ms
    C = Processo('C', 0, 0, 14, 3, 0)   # Sem I/O, total 14ms
    D = Processo('D', 0, 0, 10, 4, 0)   # Sem I/O, total 10ms

    processos = [A, B, C, D]
    
    quantum_fila0 = 5
    quantum_fila1 = 15 
    
    escalonador = EscalonadorMultinivel(processos, quantum_fila0, quantum_fila1)

    linha_tempo_cpu = escalonador.executar_simulacao()

    escalonador.gerar_relatorio()

def teste_com_json():
    """Teste usando arquivo JSON"""
    print("\n=== TESTE COM ARQUIVO JSON ===\n")
    
    try:
        with open('examples/input_example.json', 'r') as f:
            data = json.load(f)
        
        config = data.get('config', {})
        quantum_fila0 = config.get('quantum_q0', 5)
        quantum_fila1 = config.get('quantum_q1', 15)
        
        processos = []
        for i, proc_data in enumerate(data['processes']):
            processo = Processo(
                nome=proc_data['name'],
                cpu_burst=proc_data['cpu_burst'],
                tempo_io=proc_data['io_time'],
                tempo_total_cpu=proc_data['total_cpu_time'],
                ordem=i,
                prioridade=proc_data.get('priority', 0)
            )
            processos.append(processo)
        
        escalonador = EscalonadorMultinivel(processos, quantum_fila0, quantum_fila1)
        escalonador.executar_simulacao()
        escalonador.gerar_relatorio()
        
    except FileNotFoundError:
        print("Arquivo examples/input_example.json não encontrado")
    except Exception as e:
        print(f"Erro ao processar JSON: {e}")

def teste_casos_extremos():
    """Teste com casos extremos"""
    print("\n=== TESTE COM CASOS EXTREMOS ===\n")
    
    processos = [
        Processo('P1', 1, 0, 20, 1, 0),
        Processo('P2', 0, 0, 5, 2, 0),
        Processo('P3', 2, 3, 12, 3, 0),
    ]
    
    escalonador = EscalonadorMultinivel(processos, quantum_fila0=1, quantum_fila1=10)
    escalonador.executar_simulacao()
    escalonador.gerar_relatorio()

if __name__ == "__main__":
    main()
    
    teste_com_json()
    
    teste_casos_extremos()
