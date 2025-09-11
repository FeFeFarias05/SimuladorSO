
from process import Processo
from multilevel_scheduler import EscalonadorMultinivel
import json
import sys

# Classe para cores no terminal
class Cores:
    AZUL = '\033[94m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    ROXO = '\033[95m'
    CIANO = '\033[96m'
    BRANCO = '\033[97m'
    NEGRITO = '\033[1m'
    RESET = '\033[0m'

def carregarProcessosJson(arquivo):
    try:
        with open(arquivo, 'r') as f:
            data = json.load(f)
        
        config = data.get('config', {})
        quantumFila0 = config.get('quantum_q0', 5)
        quantumFila1 = config.get('quantum_q1', 15)
        
        processos = []
        for i, procData in enumerate(data['processes']):
            processo = Processo(
                nome=procData['name'],
                cpuBurst=procData['cpu_burst'],
                tempoIo=procData['io_time'],
                tempoTotalCpu=procData['total_cpu_time'],
                ordem=i,
                prioridade=procData.get('priority', 0)
            )
            processos.append(processo)
        
        return processos, quantumFila0, quantumFila1
        
    except FileNotFoundError:
        print(f"{Cores.VERMELHO}Erro: Arquivo {arquivo} não encontrado{Cores.RESET}")
        return None, None, None
    except Exception as e:
        print(f"{Cores.VERMELHO}Erro ao processar JSON: {e}{Cores.RESET}")
        return None, None, None

def main():
    print(f"{Cores.ROXO}{Cores.NEGRITO}========= Bem-vindo ao Simulador de Escalonador Multinível ========={Cores.RESET}")
    print(f"{Cores.AMARELO}{Cores.NEGRITO}>>>Regras da implementação<<<{Cores.RESET}")
    print("• Fila 0: Round Robin (quantum 1-10ms)")
    print("• Fila 1: Round Robin (quantum 11-20ms)")
    print("• Fila 3: FCFS (First Come First Served)/o processo roda até terminar sem ser preemptado")
    print("• Todos os processos iniciam na Fila 0")
    print("• Processos com quantum expirado descem de fila")
    print("• Processos que voltam do I/O retornam à fila original")
    print(f"{Cores.VERMELHO}• Preempção: {Cores.RESET} Fila 0 > Fila 1 > Fila 3")
    print(f"{Cores.ROXO}=" * 60 + Cores.RESET)
    
    if len(sys.argv) > 1:
        arquivoJson = sys.argv[1]
        print("\n")
        print(f"\n{Cores.VERDE}{Cores.NEGRITO}CARREGANDO PROCESSOS DE: {arquivoJson}{Cores.RESET}")
        print("\n")

        processos, q0, q1 = carregarProcessosJson(arquivoJson)
        if processos:
            escalonador = EscalonadorMultinivel(processos, quantumFila0=q0, quantumFila1=q1)
            escalonador.simulacao()
            escalonador.relatorio()
        else:
            print(f"{Cores.VERMELHO}Erro ao carregar processos. Verifique o arquivo JSON.{Cores.RESET}")
    else:
        print(f"\n{Cores.VERMELHO}{Cores.NEGRITO}ERRO: Arquivo JSON é obrigatório!{Cores.RESET}")
        

if __name__ == "__main__":
    main()
