from process import Processo
from collections import deque

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

class EscalonadorMultinivel:
    def __init__(self, processos, quantum_fila0=5, quantum_fila1=15):
        
        if not (1 <= quantum_fila0 <= 10):
            raise ValueError(f"Quantum da Fila 0 deve estar entre 1-10ms. Valor fornecido: {quantum_fila0}ms")
        if not (11 <= quantum_fila1 <= 20):
            raise ValueError(f"Quantum da Fila 1 deve estar entre 11-20ms. Valor fornecido: {quantum_fila1}ms")
            
        self.quantum_fila0 = quantum_fila0 
        self.quantum_fila1 = quantum_fila1
        
        self.fila0 = deque()  # quantum pequeno
        self.fila1 = deque()  # quantum maior
        self.fila2 = deque()  # FCFS
        
        self.bloqueados = []
        self.finalizados = []
        
        self.tempo_atual = 0
        self.processo_executando = None
        self.quantum_restante = 0
        
        processos_ordenados = sorted(processos, key=lambda p: p.prioridade)
        for processo in processos_ordenados:
            processo.fila_atual = 0
            processo.status = 'ready'
            self.fila0.append(processo)
        
        self.linha_tempo_cpu = []
        self.log_execucao = []

    def obter_proximo_processo(self):
        if self.fila0: #quantum menor
            processo = self.fila0.popleft()
            processo.quantum_restante = self.quantum_fila0
            return processo

        if self.fila1: #quantum maior
            processo = self.fila1.popleft()
            processo.quantum_restante = self.quantum_fila1
            return processo

        if self.fila2: #FCFS
            processo = self.fila2.popleft()
            processo.quantum_restante = float('inf')
            return processo
            
        return None

    def mover_processo_para_fila_inferior(self, processo):
        if processo.fila_atual == 0:
            processo.fila_atual = 1
            self.fila1.append(processo)
            self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} movido para Fila 1 (quantum expirado)")
        elif processo.fila_atual == 1:
            processo.fila_atual = 3  
            self.fila2.append(processo)
            self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} movido para Fila 3 (quantum expirado)")

    def retornar_processo_fila_original_apos_bloquado(self, processo):
        processo.status = 'ready'
        
        if processo.fila_atual == 0:
            self.fila0.append(processo)
        elif processo.fila_atual == 1:
            self.fila1.append(processo)  
        elif processo.fila_atual == 2:
            self.fila2.append(processo)
        self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} retornou do I/O para Fila {processo.fila_atual}")

    def processar_bloqueados_por_io(self):
        for processo in self.bloqueados[:]:
            processo.tempo_io_restante -= 1
            if processo.tempo_io_restante <= 0:
                processo.resetar_cpu_burst()
                self.bloqueados.remove(processo)
                self.retornar_processo_fila_original_apos_bloquado(processo)

    def executar_processo(self, processo):
        if processo.tempo_inicio is None:
            processo.tempo_inicio = self.tempo_atual
            
        processo.status = 'running'
        
        if processo.cpu_burst_atual > 0:
            processo.cpu_burst_atual -= 1
            
        processo.tempo_cpu_restante -= 1
        processo.quantum_restante -= 1
        
        if processo.tempo_cpu_restante <= 0:
            processo.status = 'finished'
            processo.tempo_fim = self.tempo_atual + 1
            self.finalizados.append(processo)
            self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} FINALIZADO")
            return 'finished'
        
        if processo.cpu_burst_atual <= 0 and processo.tempo_io_original > 0:
            processo.salvar_cpu_burst()
            processo.status = 'blocked'
            processo.tempo_io_restante = processo.tempo_io_original
            self.bloqueados.append(processo)
            self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} BLOQUEADO para I/O")
            return 'blocked'
        
        if processo.quantum_restante <= 0:
            processo.status = 'ready'
            self.mover_processo_para_fila_inferior(processo)
            return 'quantum_expired'
            
        return 'running'

    def verificar_preempcao(self, processo_atual):
        
        if processo_atual is None:
            return False
            
        if self.fila0 and processo_atual.fila_atual != 0:
            return True
            
        if self.fila1 and processo_atual.fila_atual == 3:
            return True
            
        return False

    def executar_simulacao(self):
        print(f"{Cores.ROXO}{Cores.NEGRITO}=== Iniciando Simulação do Escalonador Multinível ==={Cores.RESET}")
        print(f"Quantum Fila 0: {self.quantum_fila0}ms{Cores.RESET}")
        print(f"Quantum Fila 1: {self.quantum_fila1}ms{Cores.RESET}")
        print(f"Fila 3: FCFS{Cores.RESET}")

        while (self.fila0 or self.fila1 or self.fila2 or
               self.bloqueados or self.processo_executando): #processos estão rodando

            self.processar_bloqueados_por_io()

            if self.verificar_preempcao(self.processo_executando):
                if self.processo_executando:
                    if self.processo_executando.fila_atual == 0:
                        self.fila0.appendleft(self.processo_executando)
                    elif self.processo_executando.fila_atual == 1:
                        self.fila1.appendleft(self.processo_executando)
                    else:
                        self.fila2.appendleft(self.processo_executando)

                    self.processo_executando.status = 'ready'
                    self.log_execucao.append(f"T{self.tempo_atual}: Processo {self.processo_executando.nome} PREEMPTADO")
                
                self.processo_executando = None
            
            if self.processo_executando is None:
                self.processo_executando = self.obter_proximo_processo()
            
            if self.processo_executando: 
                nome_processo = self.processo_executando.nome
                resultado = self.executar_processo(self.processo_executando)
                
                if resultado in ['finished', 'blocked', 'quantum_expired']:
                    self.processo_executando = None
                    
                self.linha_tempo_cpu.append(nome_processo)
            else:
                # CPU ociosa
                self.linha_tempo_cpu.append('-')
            
            todos_processos = (list(self.fila0) + list(self.fila1) + list(self.fila2) + 
                             self.bloqueados + self.finalizados)
            if self.processo_executando:
                todos_processos.append(self.processo_executando)
                
            for p in todos_processos:
                if not hasattr(p, 'linha_tempo'): #print bonitinho com todos os processos
                    p.linha_tempo = []
                p.linha_tempo.append(p.status)
            
            self.tempo_atual += 1

        print(f"{Cores.VERDE}{Cores.NEGRITO}=== Simulação Concluída ==={Cores.RESET}")
        print(f"{Cores.ROXO}=" * 30 + Cores.RESET)

        return self.linha_tempo_cpu

    def gerar_relatorio(self):
        print("\n")
        print("\n")

        print(f"{Cores.ROXO}{Cores.NEGRITO}===== RELATÓRIO DA SIMULAÇÃO ====={Cores.RESET}")

        print(f"\n{Cores.AMARELO}{Cores.NEGRITO}--- Linha do tempo da CPU ---{Cores.RESET}")
        print("Tempo: " + " ".join([f"{i:>2}" for i in range(len(self.linha_tempo_cpu))]))
        print("CPU:   " + " ".join([f"{nome:>2}" for nome in self.linha_tempo_cpu]))
        
        print(f"\n{Cores.AMARELO}{Cores.NEGRITO}--- Linha do tempo dos estados dos processos ---{Cores.RESET}")
        estado_formatado = {
            'ready': 'R',
            'running': 'E', 
            'blocked': f'{Cores.VERMELHO}B{Cores.RESET}',
            'finished': f'{Cores.VERDE}F{Cores.RESET}'
        }
        
        for p in sorted(self.finalizados, key=lambda x: x.nome):
            while len(p.linha_tempo) < len(self.linha_tempo_cpu):
                p.linha_tempo.append('finished')
                
            linha = " ".join([f"{estado_formatado.get(s, '?'):>2}" for s in p.linha_tempo])
            print(f"{Cores.BRANCO}{p.nome}:{Cores.RESET}   {linha}")


        print(f"\n{Cores.AMARELO}{Cores.NEGRITO}--- Estatísticas ---{Cores.RESET}")
        for p in sorted(self.finalizados, key=lambda x: x.nome):
            turnaround = p.tempo_fim if p.tempo_fim else self.tempo_atual
            tempo_resposta = p.tempo_inicio if p.tempo_inicio else 0
            print(f"{Cores.BRANCO}{p.nome}:{Cores.RESET} {Cores.VERDE}Turnaround={turnaround}ms{Cores.RESET}, {Cores.CIANO}Tempo de Resposta={tempo_resposta}ms{Cores.RESET}")
        
        print(f"\n{Cores.AMARELO}{Cores.NEGRITO}--- Atividade dos processos durante a execução ---{Cores.RESET}")
        for log in self.log_execucao[-20:]:
            print(f"{log}")

        print(f"\n{Cores.AZUL}{Cores.NEGRITO}Tempo total de simulação: {self.tempo_atual}ms{Cores.RESET}")
