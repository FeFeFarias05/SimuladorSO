import time
import sys
from process import Processo
from multilevel_scheduler import EscalonadorMultinivel

def criarProcessosTeste(quantidade):
    processos = []
    
    for i in range(quantidade):
        if i % 4 == 0:
            processo = Processo(f'P{i:03d}', cpuBurst=2, tempoIo=3, tempoTotalCpu=8)
        elif i % 4 == 1:
            processo = Processo(f'P{i:03d}', cpuBurst=0, tempoIo=0, tempoTotalCpu=6)
        elif i % 4 == 2:
            processo = Processo(f'P{i:03d}', cpuBurst=0, tempoIo=0, tempoTotalCpu=12)
        else:
            processo = Processo(f'P{i:03d}', cpuBurst=1, tempoIo=2, tempoTotalCpu=10)
        
        processos.append(processo)
    
    return processos

def testeEscalabilidade(quantidadeProcessos, verbose=False):
    print(f"Teste com {quantidadeProcessos} processos")
    
    inicioCriacao = time.time()
    processos = criarProcessosTeste(quantidadeProcessos)
    tempoCriacao = time.time() - inicioCriacao
    
    escalonador = EscalonadorMultinivel(processos, quantumFila0=3, quantumFila1=11)
    
    inicioSimulacao = time.time()
    linhaTempoCpu = escalonador.simulacao()
    tempoSimulacao = time.time() - inicioSimulacao
    
    if verbose and quantidadeProcessos <= 10:
        escalonador.relatorio()
    
    processosPorSegundo = quantidadeProcessos / tempoSimulacao if tempoSimulacao > 0 else float('inf')
    
    return {
        'quantidade': quantidadeProcessos,
        'tempoCriacao': tempoCriacao,
        'tempoSimulacao': tempoSimulacao,
        'tempoTotalSimulado': escalonador.tempoAtual,
        'processosFinalizados': len(escalonador.finalizados),
        'performance': processosPorSegundo
    }

def testeProgressivo():
    print("Teste de escalabilidade progressiva")
    
    quantidades = [5, 10, 25, 50, 100, 250, 500, 1000, 2000, 3000]
    resultados = []
    
    for quantidade in quantidades:
        try:
            resultado = testeEscalabilidade(quantidade, verbose=(quantidade <= 10))
            resultados.append(resultado)
        except KeyboardInterrupt:
            print("Teste interrompido pelo usuário")
            break
        except Exception as e:
            print(f"Erro com {quantidade} processos: {e}")
            break
    
    print("\nRelatório de escalabilidade")
    print(f"{'Processos':<10} {'Criação(s)':<12} {'Simulação(s)':<13} {'Total Sim(ms)':<13} {'Perf(p/s)':<10}")
    print("-" * 60)
    
    for r in resultados:
        print(f"{r['quantidade']:<10} {r['tempoCriacao']:<12.4f} {r['tempoSimulacao']:<13.4f} "
              f"{r['tempoTotalSimulado']:<13} {r['performance']:<10.2f}")


def main():
    print("Teste de escalabilidade do escalonador multinível")
    
    if len(sys.argv) > 1:
        try:
            quantidade = int(sys.argv[1])
            testeEscalabilidade(quantidade, verbose=True)
        except ValueError:
            print("Erro: forneça um número válido de processos")
    else:
        testeProgressivo()

if __name__ == "__main__":
    main()
