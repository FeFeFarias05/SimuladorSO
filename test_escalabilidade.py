"""
Teste de Escalabilidade do Escalonador Multinível
Testa o comportamento com diferentes quantidades de processos
"""

import time
import sys
from process import Processo
from multilevel_scheduler import EscalonadorMultinivel

def criar_processos_teste(quantidade):
    """Cria uma quantidade específica de processos para teste"""
    processos = []
    
    for i in range(quantidade):
        # Varia os tipos de processos
        if i % 4 == 0:
            # Processo com I/O
            processo = Processo(f'P{i:03d}', cpu_burst=2, tempo_io=3, tempo_total_cpu=8)
        elif i % 4 == 1:
            # Processo CPU-intensivo curto
            processo = Processo(f'P{i:03d}', cpu_burst=0, tempo_io=0, tempo_total_cpu=6)
        elif i % 4 == 2:
            # Processo CPU-intensivo médio
            processo = Processo(f'P{i:03d}', cpu_burst=0, tempo_io=0, tempo_total_cpu=12)
        else:
            # Processo misto
            processo = Processo(f'P{i:03d}', cpu_burst=1, tempo_io=2, tempo_total_cpu=10)
        
        processos.append(processo)
    
    return processos

def teste_escalabilidade(quantidade_processos, verbose=False):
    """Testa o escalonador com uma quantidade específica de processos"""
    print(f"\nTESTE COM {quantidade_processos} PROCESSOS")
    print("=" * 50)
    
    # Cria processos
    inicio_criacao = time.time()
    processos = criar_processos_teste(quantidade_processos)
    tempo_criacao = time.time() - inicio_criacao
    
    print(f"Tempo para criar {quantidade_processos} processos: {tempo_criacao:.4f}s")
    
    # Executa simulação
    escalonador = EscalonadorMultinivel(processos, quantum_fila0=3, quantum_fila1=11)
    
    inicio_simulacao = time.time()
    linha_tempo_cpu = escalonador.executar_simulacao()
    tempo_simulacao = time.time() - inicio_simulacao
    
    print(f"Tempo de simulação: {tempo_simulacao:.4f}s")
    print(f"Tempo total simulado: {escalonador.tempo_atual}ms")
    print(f"Processos finalizados: {len(escalonador.finalizados)}")
    
    if verbose and quantidade_processos <= 10:
        escalonador.gerar_relatorio()
    
    # Estatísticas de performance
    processos_por_segundo = quantidade_processos / tempo_simulacao if tempo_simulacao > 0 else float('inf')
    print(f"Performance: {processos_por_segundo:.2f} processos/segundo")
    
    return {
        'quantidade': quantidade_processos,
        'tempo_criacao': tempo_criacao,
        'tempo_simulacao': tempo_simulacao,
        'tempo_total_simulado': escalonador.tempo_atual,
        'processos_finalizados': len(escalonador.finalizados),
        'performance': processos_por_segundo
    }

def teste_progressivo():
    """Testa com quantidades crescentes de processos"""
    print("TESTE DE ESCALABILIDADE PROGRESSIVA")
    print("=" * 60)
    
    quantidades = [5, 10, 25, 50, 100, 250, 500, 1000, 2000, 3000]
    resultados = []
    
    for quantidade in quantidades:
        try:
            resultado = teste_escalabilidade(quantidade, verbose=(quantidade <= 10))
            resultados.append(resultado)
        except KeyboardInterrupt:
            print("\nTeste interrompido pelo usuário")
            break
        except Exception as e:
            print(f"Erro com {quantidade} processos: {e}")
            break
    
    # Relatório final
    print("\nRELATÓRIO DE ESCALABILIDADE")
    print("=" * 60)
    print(f"{'Processos':<10} {'Criação(s)':<12} {'Simulação(s)':<13} {'Total Sim(ms)':<13} {'Perf(p/s)':<10}")
    print("-" * 60)
    
    for r in resultados:
        print(f"{r['quantidade']:<10} {r['tempo_criacao']:<12.4f} {r['tempo_simulacao']:<13.4f} "
              f"{r['tempo_total_simulado']:<13} {r['performance']:<10.2f}")

def teste_memoria():
    """Testa uso de memória com muitos processos"""
    import psutil
    import os
    
    print("\nTESTE DE USO DE MEMÓRIA")
    print("=" * 50)
    
    processo_atual = psutil.Process(os.getpid())
    memoria_inicial = processo_atual.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Memória inicial: {memoria_inicial:.2f} MB")
    
    # Cria muitos processos
    quantidade = 1000
    processos = criar_processos_teste(quantidade)
    
    memoria_pos_criacao = processo_atual.memory_info().rss / 1024 / 1024
    print(f"Memória após criar {quantidade} processos: {memoria_pos_criacao:.2f} MB")
    print(f"Incremento: {memoria_pos_criacao - memoria_inicial:.2f} MB")
    print(f"Memória por processo: {(memoria_pos_criacao - memoria_inicial) / quantidade * 1024:.2f} KB")

def main():
    """Função principal"""
    print("TESTE DE ESCALABILIDADE DO ESCALONADOR MULTINÍVEL")
    print("=" * 60)
    print("Este teste avalia a capacidade do algoritmo de lidar com")
    print("diferentes quantidades de processos.")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Teste com quantidade específica
        try:
            quantidade = int(sys.argv[1])
            teste_escalabilidade(quantidade, verbose=True)
        except ValueError:
            print("Erro: Forneça um número válido de processos")
    else:
        # Teste progressivo
        teste_progressivo()
        teste_memoria()
    
    print("\nCONCLUSÃO:")
    print("O algoritmo pode teoricamente lidar com qualquer quantidade de processos,")
    print("limitado apenas pela memória disponível e tempo de processamento.")

if __name__ == "__main__":
    main()
