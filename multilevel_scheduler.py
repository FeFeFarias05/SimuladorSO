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
    def __init__(self, processos, quantumFila0=5, quantumFila1=15):
        
        if not (1 <= quantumFila0 <= 10):
            raise ValueError(f"Quantum da Fila 0 deve estar entre 1-10ms. Valor fornecido: {quantumFila0}ms")
        if not (11 <= quantumFila1 <= 20):
            raise ValueError(f"Quantum da Fila 1 deve estar entre 11-20ms. Valor fornecido: {quantumFila1}ms")
            
        self.quantumFila0 = quantumFila0 
        self.quantumFila1 = quantumFila1

        self.fila0 = deque()  # quantum pequeno
        self.fila1 = deque()  # quantum maior
        self.fila2 = deque()  # FCFS

        self.bloqueados = []
        self.finalizados = []
        
        self.tempoAtual = 0
        self.processoExecutando = None
        self.quantumRestante = 0
        
        processosOrdenados = sorted(processos, key=lambda p: p.prioridade)
        for processo in processosOrdenados:
            processo.filaAtual = 0
            processo.status = 'ready'
            self.fila0.append(processo)
        
        self.linhaTempoCpu = []
        self.logExecucao = []

    def obterProximoProcesso(self):
        if self.fila0:
            processo = self.fila0.popleft()
            processo.quantumRestante = self.quantumFila0
            return processo

        if self.fila1:
            processo = self.fila1.popleft()
            processo.quantumRestante = self.quantumFila1
            return processo

        if self.fila2:
            processo = self.fila2.popleft()
            processo.quantumRestante = float('inf')
            return processo
            
        return None

    def moverProcessoParaFilaInferior(self, processo):
        if processo.filaAtual == 0:
            processo.filaAtual = 1
            self.fila1.append(processo)
            self.logExecucao.append(f"T{self.tempoAtual}: Processo {processo.nome} movido para Fila 1 (quantum expirado)")
        elif processo.filaAtual == 1:
            processo.filaAtual = 3  
            self.fila2.append(processo)
            self.logExecucao.append(f"T{self.tempoAtual}: Processo {processo.nome} movido para Fila 3 (quantum expirado)")

    def retornarProcessoFilaOriginalAposBloqueado(self, processo):
        processo.status = 'ready'
        
        if processo.filaAtual == 0:
            self.fila0.append(processo)
        elif processo.filaAtual == 1:
            self.fila1.append(processo)  
        elif processo.filaAtual == 2:
            self.fila2.append(processo)
        self.logExecucao.append(f"T{self.tempoAtual}: Processo {processo.nome} retornou do I/O para Fila {processo.filaAtual}")

    def processarBloqueadosPorIo(self):
        for processo in self.bloqueados[:]:
            processo.tempoIoRestante -= 1
            if processo.tempoIoRestante <= 0:
                processo.resetarCpuBurst()
                self.bloqueados.remove(processo)
                self.retornarProcessoFilaOriginalAposBloqueado(processo)

    def executarProcesso(self, processo):
        if processo.tempoInicio is None:
            processo.tempoInicio = self.tempoAtual
            
        processo.status = 'running'
        
        if processo.cpuBurstAtual > 0:
            processo.cpuBurstAtual -= 1
            
        processo.tempoCpuRestante -= 1
        processo.quantumRestante -= 1
        
        if processo.tempoCpuRestante <= 0:
            processo.status = 'finished'
            processo.tempoFim = self.tempoAtual + 1
            self.finalizados.append(processo)
            self.logExecucao.append(f"T{self.tempoAtual}: Processo {processo.nome} FINALIZADO")
            return 'finished'
        
        if processo.cpuBurstAtual <= 0 and processo.tempoIoOriginal > 0:
            processo.salvarCpuBurst()
            processo.status = 'blocked'
            processo.tempoIoRestante = processo.tempoIoOriginal
            self.bloqueados.append(processo)
            self.logExecucao.append(f"T{self.tempoAtual}: Processo {processo.nome} BLOQUEADO para I/O")
            return 'blocked'
        
        if processo.quantumRestante <= 0:
            processo.status = 'ready'
            self.moverProcessoParaFilaInferior(processo)
            return 'quantum_expired'
            
        return 'running'

    def verificarPreempcao(self, processoAtual):
        
        if processoAtual is None:
            return False
            
        if self.fila0 and processoAtual.filaAtual != 0:
            return True
            
        if self.fila1 and processoAtual.filaAtual == 3:
            return True
            
        return False

    def executarSimulacao(self):
        print(f"{Cores.ROXO}{Cores.NEGRITO}=== Iniciando Simulação do Escalonador Multinível ==={Cores.RESET}")
        print(f"Quantum Fila 0: {self.quantumFila0}ms{Cores.RESET}")
        print(f"Quantum Fila 1: {self.quantumFila1}ms{Cores.RESET}")
        print(f"Fila 3: FCFS{Cores.RESET}")

        while (self.fila0 or self.fila1 or self.fila2 or
               self.bloqueados or self.processoExecutando):

            self.processarBloqueadosPorIo()

            if self.verificarPreempcao(self.processoExecutando):
                if self.processoExecutando:
                    if self.processoExecutando.filaAtual == 0:
                        self.fila0.appendleft(self.processoExecutando)
                    elif self.processoExecutando.filaAtual == 1:
                        self.fila1.appendleft(self.processoExecutando)
                    else:
                        self.fila2.appendleft(self.processoExecutando)

                    self.processoExecutando.status = 'ready'
                    self.logExecucao.append(f"T{self.tempoAtual}: Processo {self.processoExecutando.nome} PREEMPTADO")
                
                self.processoExecutando = None
            
            if self.processoExecutando is None:
                self.processoExecutando = self.obterProximoProcesso()
            
            if self.processoExecutando: 
                nomeProcesso = self.processoExecutando.nome
                resultado = self.executarProcesso(self.processoExecutando)
                
                if resultado in ['finished', 'blocked', 'quantum_expired']:
                    self.processoExecutando = None
                    
                self.linhaTempoCpu.append(nomeProcesso)
            else:
                self.linhaTempoCpu.append('-')
            
            todosProcessos = (list(self.fila0) + list(self.fila1) + list(self.fila2) + 
                             self.bloqueados + self.finalizados)
            if self.processoExecutando:
                todosProcessos.append(self.processoExecutando)
                
            for p in todosProcessos:
                if not hasattr(p, 'linhaTempo'):
                    p.linhaTempo = []
                p.linhaTempo.append(p.status)
            
            self.tempoAtual += 1

        print(f"{Cores.VERDE}{Cores.NEGRITO}=== Simulação Concluída ==={Cores.RESET}")
        print(f"{Cores.ROXO}=" * 30 + Cores.RESET)

        return self.linhaTempoCpu

    def gerarRelatorio(self):
        print("\n")
        print("\n")

        print(f"{Cores.ROXO}{Cores.NEGRITO}===== RELATÓRIO DA SIMULAÇÃO ====={Cores.RESET}")

        print(f"\n{Cores.AMARELO}{Cores.NEGRITO}--- Linha do tempo da CPU ---{Cores.RESET}")
        print("Tempo: " + " ".join([f"{i:>2}" for i in range(len(self.linhaTempoCpu))]))
        print("CPU:   " + " ".join([f"{nome:>2}" for nome in self.linhaTempoCpu]))
        
        print(f"\n{Cores.AMARELO}{Cores.NEGRITO}--- Linha do tempo dos estados dos processos ---{Cores.RESET}")
        estadoFormatado = {
            'ready': 'R',
            'running': 'E', 
            'blocked': f'{Cores.VERMELHO}B{Cores.RESET}',
            'finished': f'{Cores.VERDE}F{Cores.RESET}'
        }
        
        for p in sorted(self.finalizados, key=lambda x: x.nome):
            while len(p.linhaTempo) < len(self.linhaTempoCpu):
                p.linhaTempo.append('finished')
                
            linha = " ".join([f"{estadoFormatado.get(s, '?'):>2}" for s in p.linhaTempo])
            print(f"{Cores.BRANCO}{p.nome}:{Cores.RESET}   {linha}")


        print(f"\n{Cores.AMARELO}{Cores.NEGRITO}--- Estatísticas ---{Cores.RESET}")
        for p in sorted(self.finalizados, key=lambda x: x.nome):
            turnaround = p.tempoFim if p.tempoFim else self.tempoAtual
            tempoResposta = p.tempoInicio if p.tempoInicio else 0
            print(f"{Cores.BRANCO}{p.nome}:{Cores.RESET} {Cores.VERDE}Turnaround={turnaround}ms{Cores.RESET}, {Cores.CIANO}Tempo de Resposta={tempoResposta}ms{Cores.RESET}")
        
        print(f"\n{Cores.AMARELO}{Cores.NEGRITO}--- Atividade dos processos durante a execução ---{Cores.RESET}")
        for log in self.logExecucao[-20:]:
            print(f"{log}")

        print(f"\n{Cores.AZUL}{Cores.NEGRITO}Tempo total de simulação: {self.tempoAtual}ms{Cores.RESET}")
