"""
Versão Otimizada do Escalonador Multinível
Melhorias de performance para lidar com muitos processos
"""

from process import Processo
from collections import deque
import heapq

class EscalonadorMultinivelOtimizado:
    def __init__(self, processos, quantum_fila0=5, quantum_fila1=15):
        # Configuração dos quantums
        self.quantum_fila0 = quantum_fila0
        self.quantum_fila1 = quantum_fila1
        
        # As três filas do escalonador multinível
        self.fila0 = deque()
        self.fila1 = deque()
        self.fila2 = deque()
        
        # OTIMIZAÇÃO: Usa heap para processos bloqueados ordenados por tempo de desbloqueio
        self.processos_bloqueados_heap = []  # (tempo_desbloqueio, id_unico, processo)
        self.contador_id = 0  # Para garantir unicidade no heap
        self.finalizados = []
        
        # Controle de tempo
        self.tempo_atual = 0
        self.processo_executando = None
        
        # Inicializa todos os processos na fila 0
        for processo in processos:
            processo.fila_atual = 0
            processo.status = 'ready'
            self.fila0.append(processo)
        
        # Log simplificado para melhor performance
        self.linha_tempo_cpu = []
        self.eventos_importantes = []

    def obter_proximo_processo(self):
        """Seleciona o próximo processo seguindo a prioridade das filas"""
        if self.fila0:
            processo = self.fila0.popleft()
            processo.quantum_restante = self.quantum_fila0
            return processo
        
        if self.fila1:
            processo = self.fila1.popleft()
            processo.quantum_restante = self.quantum_fila1
            return processo
            
        if self.fila2:
            processo = self.fila2.popleft()
            processo.quantum_restante = float('inf')
            return processo
            
        return None

    def mover_processo_para_fila_inferior(self, processo):
        """Move processo para fila de menor prioridade"""
        if processo.fila_atual == 0:
            processo.fila_atual = 1
            self.fila1.append(processo)
        elif processo.fila_atual == 1:
            processo.fila_atual = 2  
            self.fila2.append(processo)

    def retornar_processo_fila0(self, processo):
        """Retorna processo para fila 0 quando volta do I/O"""
        processo.fila_atual = 0
        processo.status = 'ready'
        self.fila0.append(processo)

    def processar_bloqueados_otimizado(self):
        """
        OTIMIZAÇÃO: Processa apenas processos que devem desbloquear no tempo atual
        Usa heap para eficiência O(log n) em vez de O(n)
        """
        while (self.processos_bloqueados_heap and 
               self.processos_bloqueados_heap[0][0] <= self.tempo_atual):
            
            tempo_desbloqueio, id_unico, processo = heapq.heappop(self.processos_bloqueados_heap)
            processo.resetar_cpu_burst()
            self.retornar_processo_fila0(processo)

    def executar_processo(self, processo):
        """Executa um processo por 1ms"""
        if processo.tempo_inicio is None:
            processo.tempo_inicio = self.tempo_atual
            
        processo.status = 'running'
        
        # Processa CPU
        if processo.cpu_burst_atual > 0:
            processo.cpu_burst_atual -= 1
            
        processo.tempo_cpu_restante -= 1
        processo.quantum_restante -= 1
        
        # Verifica se o processo terminou completamente
        if processo.tempo_cpu_restante <= 0:
            processo.status = 'finished'
            processo.tempo_fim = self.tempo_atual + 1
            self.finalizados.append(processo)
            return 'finished'
        
        # Verifica se CPU burst terminou (vai para I/O)
        if processo.cpu_burst_atual <= 0 and processo.tempo_io_original > 0:
            processo.salvar_cpu_burst()
            processo.status = 'blocked'
            processo.tempo_io_restante = processo.tempo_io_original
            
            # OTIMIZAÇÃO: Adiciona ao heap com tempo de desbloqueio e ID único
            tempo_desbloqueio = self.tempo_atual + processo.tempo_io_original
            self.contador_id += 1
            heapq.heappush(self.processos_bloqueados_heap, 
                          (tempo_desbloqueio, self.contador_id, processo))
            return 'blocked'
        
        # Verifica se quantum expirou
        if processo.quantum_restante <= 0:
            processo.status = 'ready'
            self.mover_processo_para_fila_inferior(processo)
            return 'quantum_expired'
            
        return 'running'

    def verificar_preempcao(self, processo_atual):
        """Verifica necessidade de preempção"""
        if processo_atual is None:
            return False
            
        if self.fila0 and processo_atual.fila_atual != 0:
            return True
            
        if self.fila1 and processo_atual.fila_atual == 2:
            return True
            
        return False

    def executar_simulacao(self):
        """
        OTIMIZAÇÃO: Simulação com log mínimo para melhor performance
        """
        print("=== SIMULAÇÃO OTIMIZADA INICIADA ===")
        print(f"Quantum Fila 0: {self.quantum_fila0}ms, Fila 1: {self.quantum_fila1}ms")
        
        while (self.fila0 or self.fila1 or self.fila2 or 
               self.processos_bloqueados_heap or self.processo_executando):
            
            # OTIMIZAÇÃO: Processa bloqueados com heap
            self.processar_bloqueados_otimizado()
            
            # Verifica preempção
            if self.verificar_preempcao(self.processo_executando):
                if self.processo_executando:
                    if self.processo_executando.fila_atual == 0:
                        self.fila0.appendleft(self.processo_executando)
                    elif self.processo_executando.fila_atual == 1:
                        self.fila1.appendleft(self.processo_executando)
                    else:
                        self.fila2.appendleft(self.processo_executando)
                    
                    self.processo_executando.status = 'ready'
                
                self.processo_executando = None
            
            # Escalona novo processo se necessário
            if self.processo_executando is None:
                self.processo_executando = self.obter_proximo_processo()
            
            # Executa processo atual
            if self.processo_executando:
                nome_processo = self.processo_executando.nome
                resultado = self.executar_processo(self.processo_executando)
                
                if resultado in ['finished', 'blocked', 'quantum_expired']:
                    self.processo_executando = None
                    
                # OTIMIZAÇÃO: Log simplificado
                if len(self.linha_tempo_cpu) < 1000:  # Log apenas primeiros 1000ms
                    self.linha_tempo_cpu.append(nome_processo)
            else:
                if len(self.linha_tempo_cpu) < 1000:
                    self.linha_tempo_cpu.append('-')
            
            self.tempo_atual += 1
        
        print("=== SIMULAÇÃO CONCLUÍDA ===")
        return self.linha_tempo_cpu

    def gerar_relatorio_simplificado(self):
        """Relatório simplificado para melhor performance"""
        print(f"\n📊 RELATÓRIO SIMPLIFICADO")
        print("=" * 50)
        print(f"⏱️  Tempo total de simulação: {self.tempo_atual}ms")
        print(f"📈 Processos finalizados: {len(self.finalizados)}")
        
        if len(self.linha_tempo_cpu) <= 100:
            print(f"\n--- LINHA DO TEMPO DA CPU (primeiros {len(self.linha_tempo_cpu)}ms) ---")
            print("Tempo: " + " ".join([f"{i:>2}" for i in range(len(self.linha_tempo_cpu))]))
            print("CPU:   " + " ".join([f"{nome:>2}" for nome in self.linha_tempo_cpu]))
        
        # Estatísticas básicas
        if self.finalizados:
            turnarounds = [p.tempo_fim for p in self.finalizados if p.tempo_fim]
            if turnarounds:
                print(f"\n📊 Turnaround médio: {sum(turnarounds)/len(turnarounds):.2f}ms")
                print(f"📊 Turnaround mínimo: {min(turnarounds)}ms")
                print(f"📊 Turnaround máximo: {max(turnarounds)}ms")
        
        print(f"\n💾 Estruturas de dados:")
        print(f"   Fila 0: {len(self.fila0)} processos")
        print(f"   Fila 1: {len(self.fila1)} processos") 
        print(f"   Fila 2: {len(self.fila2)} processos")
        print(f"   Bloqueados: {len(self.processos_bloqueados_heap)} processos")
