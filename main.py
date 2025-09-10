
from process import Processo
from multilevel_scheduler import EscalonadorMultinivel
import json
import sys

def carregar_processos_json(arquivo):
    """Carrega processos de um arquivo JSON"""
    try:
        with open(arquivo, 'r') as f:
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
        
        return processos, quantum_fila0, quantum_fila1
        
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo} não encontrado")
        return None, None, None
    except Exception as e:
        print(f"Erro ao processar JSON: {e}")
        return None, None, None

def exemplo_basico():
    """Exemplo básico demonstrando o escalonador multinível"""
    print("🔥 EXEMPLO BÁSICO - ESCALONADOR MULTINÍVEL COM FEEDBACK")
    print("=" * 60)
    
    # Cria processos que demonstram bem o algoritmo
    processos = [
        Processo('A', 2, 3, 8),   # Processo com I/O
        Processo('B', 0, 0, 15),  # Processo CPU-intensivo (vai para fila 3)
        Processo('C', 1, 2, 6),   # Processo balanceado
        Processo('D', 0, 0, 4),   # Processo curto
    ]
    
    print("PROCESSOS:")
    for p in processos:
        io_info = f"I/O: {p.tempo_io_original}ms" if p.tempo_io_original > 0 else "Sem I/O"
        print(f"  {p.nome}: CPU Burst={p.cpu_burst_original}ms, {io_info}, Total CPU={p.tempo_total_cpu}ms")
    
    # Executa com quantums padrão da especificação
    escalonador = EscalonadorMultinivel(processos, quantum_fila0=5, quantum_fila1=15)
    escalonador.executar_simulacao()
    escalonador.gerar_relatorio()

def exemplo_quantum_pequeno():
    """Exemplo com quantum pequeno para mostrar movimento entre filas"""
    print("\n🚀 EXEMPLO COM QUANTUM PEQUENO - DEMONSTRA MOVIMENTO ENTRE FILAS")
    print("=" * 60)
    
    processos = [
        Processo('X', 0, 0, 12),  # Processo que vai percorrer todas as filas
        Processo('Y', 0, 0, 8),   # Outro processo CPU-intensivo
    ]
    
    print("PROCESSOS:")
    for p in processos:
        print(f"  {p.nome}: Total CPU={p.tempo_total_cpu}ms (sem I/O)")
    
    # Quantum muito pequeno para demonstrar movimento
    escalonador = EscalonadorMultinivel(processos, quantum_fila0=2, quantum_fila1=4)
    escalonador.executar_simulacao()
    escalonador.gerar_relatorio()

def exemplo_preempcao():
    """Exemplo demonstrando preempção entre filas"""
    print("\n⚡ EXEMPLO DE PREEMPÇÃO - PRIORIDADE ENTRE FILAS")
    print("=" * 60)
    
    processos = [
        Processo('Low', 0, 0, 20),  # Processo que vai para fila 3
        Processo('High', 2, 5, 6),  # Processo que vai fazer I/O e retornar para fila 0
    ]
    
    print("PROCESSOS:")
    print("  Low: Processo longo que será movido para fila 3")
    print("  High: Processo com I/O que voltará para fila 0 e preemptará Low")
    
    escalonador = EscalonadorMultinivel(processos, quantum_fila0=3, quantum_fila1=6)
    escalonador.executar_simulacao()
    escalonador.gerar_relatorio()

def main():
    """Função principal"""
    print("🎯 SIMULADOR DE ESCALONADOR MULTINÍVEL COM FEEDBACK")
    print("📋 Implementação conforme especificação do trabalho")
    print("=" * 60)
    print("ESPECIFICAÇÕES:")
    print("• Fila 0: Round Robin (quantum 1-10ms)")
    print("• Fila 1: Round Robin (quantum 11-20ms)")
    print("• Fila 3: FCFS (First Come First Served)")
    print("• Todos os processos iniciam na Fila 0")
    print("• Processos com quantum expirado descem de fila")
    print("• Processos que voltam do I/O retornam à fila original")
    print("• Preempção: Fila 0 > Fila 1 > Fila 3")
    print("=" * 60)
    
    # Verifica se foi passado arquivo JSON como argumento
    if len(sys.argv) > 1:
        arquivo_json = sys.argv[1]
        print(f"\n📂 CARREGANDO PROCESSOS DE: {arquivo_json}")
        
        processos, q0, q1 = carregar_processos_json(arquivo_json)
        if processos:
            escalonador = EscalonadorMultinivel(processos, q0, q1)
            escalonador.executar_simulacao()
            escalonador.gerar_relatorio()
        return
    
    # Executa exemplos demonstrativos
    exemplo_basico()
    exemplo_quantum_pequeno() 
    exemplo_preempcao()
    
    print("\n✅ SIMULAÇÃO CONCLUÍDA!")
    print("💡 Para usar arquivo JSON: python main.py examples/input_example.json")

if __name__ == "__main__":
    main()
