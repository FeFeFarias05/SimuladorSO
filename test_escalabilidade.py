import time
import sys
from process import Processo
from multilevel_scheduler import EscalonadorMultinivel

def criar_processos_teste(quantidade):
    processos = []
    
    for i in range(quantidade):
        if i % 4 == 0:
            processo = Processo(f'P{i:03d}', cpu_burst=2, tempo_io=3, tempo_total_cpu=8)
        elif i % 4 == 1:
            processo = Processo(f'P{i:03d}', cpu_burst=0, tempo_io=0, tempo_total_cpu=6)
        elif i % 4 == 2:
            processo = Processo(f'P{i:03d}', cpu_burst=0, tempo_io=0, tempo_total_cpu=12)
        else:
            processo = Processo(f'P{i:03d}', cpu_burst=1, tempo_io=2, tempo_total_cpu=10)
        
        processos.append(processo)
    
    return processos

def teste_escalabilidade(quantidade_processos, verbose=False):
    print(f"Teste com {quantidade_processos} processos")
    
    inicio_criacao = time.time()
    processos = criar_processos_teste(quantidade_processos)
    tempo_criacao = time.time() - inicio_criacao
    
    escalonador = EscalonadorMultinivel(processos, quantum_fila0=3, quantum_fila1=11)
    
    inicio_simulacao = time.time()
    linha_tempo_cpu = escalonador.executar_simulacao()
    tempo_simulacao = time.time() - inicio_simulacao
    
    if verbose and quantidade_processos <= 10:
        escalonador.gerar_relatorio()
    
    processos_por_segundo = quantidade_processos / tempo_simulacao if tempo_simulacao > 0 else float('inf')
    
    return {
        'quantidade': quantidade_processos,
        'tempo_criacao': tempo_criacao,
        'tempo_simulacao': tempo_simulacao,
        'tempo_total_simulado': escalonador.tempo_atual,
        'processos_finalizados': len(escalonador.finalizados),
        'performance': processos_por_segundo
    }

def teste_progressivo():
    print("Teste de escalabilidade progressiva")
    
    quantidades = [5, 10, 25, 50, 100, 250, 500, 1000, 2000, 3000]
    resultados = []
    
    for quantidade in quantidades:
        try:
            resultado = teste_escalabilidade(quantidade, verbose=(quantidade <= 10))
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
        print(f"{r['quantidade']:<10} {r['tempo_criacao']:<12.4f} {r['tempo_simulacao']:<13.4f} "
              f"{r['tempo_total_simulado']:<13} {r['performance']:<10.2f}")

def teste_memoria():
    import psutil
    import os
    
    print("Teste de uso de memória")
    
    processo_atual = psutil.Process(os.getpid())
    memoria_inicial = processo_atual.memory_info().rss / 1024 / 1024
    
    quantidade = 1000
    processos = criar_processos_teste(quantidade)
    
    memoria_pos_criacao = processo_atual.memory_info().rss / 1024 / 1024
    print(f"Memória inicial: {memoria_inicial:.2f} MB")
    print(f"Memória após criar {quantidade} processos: {memoria_pos_criacao:.2f} MB")
    print(f"Incremento: {memoria_pos_criacao - memoria_inicial:.2f} MB")
    print(f"Memória por processo: {(memoria_pos_criacao - memoria_inicial) / quantidade * 1024:.2f} KB")

def main():
    print("Teste de escalabilidade do escalonador multinível")
    
    if len(sys.argv) > 1:
        try:
            quantidade = int(sys.argv[1])
            teste_escalabilidade(quantidade, verbose=True)
        except ValueError:
            print("Erro: forneça um número válido de processos")
    else:
        teste_progressivo()
        teste_memoria()

if __name__ == "__main__":
    main()
