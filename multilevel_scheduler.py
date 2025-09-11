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
    CINZA = '\033[90m'
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
        self.linhaTempoFilas = []  # Para rastrear as filas a cada momento

    def obterEstadoFilas(self):
        """Retorna o estado atual das filas para visualização"""
        estado = {
            'fila0': [p.nome for p in self.fila0],
            'fila1': [p.nome for p in self.fila1], 
            'fila2': [p.nome for p in self.fila2],
            'bloqueados': [p.nome for p in self.bloqueados],
            'executando': self.processoExecutando.nome if self.processoExecutando else None,
            'filaExecutando': self.processoExecutando.filaAtual if self.processoExecutando else None
        }
        return estado

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

    def mostrarEstadoFilas(self):
        """Mostra o estado atual de todas as filas de forma concisa"""
        fila0_str = f"F0[{','.join([p.nome for p in self.fila0])}]" if self.fila0 else "F0[]"
        fila1_str = f"F1[{','.join([p.nome for p in self.fila1])}]" if self.fila1 else "F1[]"
        fila2_str = f"F2[{','.join([p.nome for p in self.fila2])}]" if self.fila2 else "F2[]"
        bloq_str = f"B[{','.join([p.nome for p in self.bloqueados])}]" if self.bloqueados else "B[]"
        exec_str = f"▶{self.processoExecutando.nome}" if self.processoExecutando else "▶-"
        
        print(f"{Cores.CIANO}T{self.tempoAtual:2d}:{Cores.RESET} {fila0_str} {fila1_str} {fila2_str} {bloq_str} {exec_str}")

    def simulacao(self):
        print(f"{Cores.ROXO}{Cores.NEGRITO}=== Iniciando Simulação do Escalonador Multinível ==={Cores.RESET}")
        print(f"Quantum Fila 0: {self.quantumFila0}ms | Quantum Fila 1: {self.quantumFila1}ms | Fila 2: FCFS{Cores.RESET}")
        print(f"\n{Cores.AMARELO}{Cores.NEGRITO}--- ACOMPANHAMENTO DAS FILAS ---{Cores.RESET}")

        while (self.fila0 or self.fila1 or self.fila2 or
               self.bloqueados or self.processoExecutando):

            self.processarBloqueadosPorIo()

            # Mostrar estado das filas apenas nos primeiros momentos
            if self.tempoAtual < 5:
                self.mostrarEstadoFilas()

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
            
            # Capturar estado atual das filas
            estadoFilas = self.obterEstadoFilas()
            self.linhaTempoFilas.append(estadoFilas.copy())
            
            todosProcessos = (list(self.fila0) + list(self.fila1) + list(self.fila2) + 
                             self.bloqueados + self.finalizados)
            if self.processoExecutando:
                todosProcessos.append(self.processoExecutando)
                
            for p in todosProcessos:
                if not hasattr(p, 'linhaTempo'):
                    p.linhaTempo = []
                p.linhaTempo.append(p.status)
            
            self.tempoAtual += 1

        # Mostrar estado final das filas
        print(f"\n{Cores.CIANO}{Cores.NEGRITO}=== RESUMO FINAL DAS FILAS ==={Cores.RESET}")
        self.mostrarEstadoFilas()

        return self.linhaTempoCpu

    def mostrarEstadoFilas(self, mostrar_todos=False):
        """Mostra o estado das filas durante a execução"""
        print(f"\n{Cores.CIANO}{Cores.NEGRITO}=== ESTADO DAS FILAS DURANTE A EXECUÇÃO ==={Cores.RESET}")
        print(f"{Cores.AMARELO}Legenda: F0=Fila 0 (RR), F1=Fila 1 (RR), F2=Fila 2 (FCFS), B=Bloqueado, E=Executando{Cores.RESET}")
        print()
        
        # Cabeçalho melhorado
        print(f"{Cores.ROXO}{'T':>3} | {'Fila 0 (RR-' + str(self.quantumFila0) + 'ms)':>25} | {'Fila 1 (RR-' + str(self.quantumFila1) + 'ms)':>25} | {'Fila 2 (FCFS)':>15} | {'Bloqueados':>12} | {'Executando':>12}{Cores.RESET}")
        print(f"{Cores.ROXO}{'─' * 3}─┼─{'─' * 25}─┼─{'─' * 25}─┼─{'─' * 15}─┼─{'─' * 12}─┼─{'─' * 12}{Cores.RESET}")
        
        # Determinar quais momentos mostrar
        if mostrar_todos or len(self.linhaTempoFilas) <= 50:
            momentos_para_mostrar = range(len(self.linhaTempoFilas))
        else:
            # Mostrar primeiros 20, últimos 10, e alguns do meio
            momentos_para_mostrar = list(range(20)) + list(range(len(self.linhaTempoFilas)-10, len(self.linhaTempoFilas)))
            if len(self.linhaTempoFilas) > 60:
                meio = len(self.linhaTempoFilas) // 2
                momentos_para_mostrar.extend(range(meio-5, meio+5))
            momentos_para_mostrar = sorted(set(momentos_para_mostrar))
        
        ultimo_tempo = -1
        for t in momentos_para_mostrar:
            estado = self.linhaTempoFilas[t]
            
            # Adicionar linha de separação se houver gap
            if t - ultimo_tempo > 1 and ultimo_tempo != -1:
                print(f"{Cores.CINZA}{'...':>3} │ {'...':>25} │ {'...':>25} │ {'...':>15} │ {'...':>12} │ {'...':>12}{Cores.RESET}")
            
            # Formatar filas com cores diferentes
            fila0_str = f"{Cores.VERDE}{', '.join(estado['fila0'])}{Cores.RESET}" if estado['fila0'] else f"{Cores.CINZA}—{Cores.RESET}"
            fila1_str = f"{Cores.AMARELO}{', '.join(estado['fila1'])}{Cores.RESET}" if estado['fila1'] else f"{Cores.CINZA}—{Cores.RESET}"
            fila2_str = f"{Cores.AZUL}{', '.join(estado['fila2'])}{Cores.RESET}" if estado['fila2'] else f"{Cores.CINZA}—{Cores.RESET}"
            bloqueados_str = f"{Cores.VERMELHO}{', '.join(estado['bloqueados'])}{Cores.RESET}" if estado['bloqueados'] else f"{Cores.CINZA}—{Cores.RESET}"
            
            if estado['executando']:
                cor_executando = Cores.VERDE if estado['filaExecutando'] == 0 else Cores.AMARELO if estado['filaExecutando'] == 1 else Cores.AZUL
                executando_str = f"{cor_executando}{estado['executando']} (F{estado['filaExecutando']}){Cores.RESET}"
            else:
                executando_str = f"{Cores.CINZA}—{Cores.RESET}"
            
            print(f"{Cores.BRANCO}{t:3d}{Cores.RESET} │ {fila0_str:>25} │ {fila1_str:>25} │ {fila2_str:>15} │ {bloqueados_str:>12} │ {executando_str:>12}")
            ultimo_tempo = t
        
        if not mostrar_todos and len(self.linhaTempoFilas) > 50:
            print(f"\n{Cores.CINZA}Nota: Mostrando apenas momentos selecionados. Total de {len(self.linhaTempoFilas)} momentos.{Cores.RESET}")

    def detectarExecucaoSimultanea(self):
        """Detecta momentos em que processos estão rodando simultaneamente em filas diferentes"""
        momentosSimultaneos = []
        for t, estado in enumerate(self.linhaTempoFilas):
            processosAtivos = []
            
            # Contar processos em cada fila
            if estado['fila0']:
                processosAtivos.extend([(p, 0) for p in estado['fila0']])
            if estado['fila1']:
                processosAtivos.extend([(p, 1) for p in estado['fila1']])
            if estado['fila2']:
                processosAtivos.extend([(p, 2) for p in estado['fila2']])
            if estado['executando']:
                processosAtivos.append((estado['executando'], estado['filaExecutando']))
            
            # Verificar se há processos em filas diferentes
            filasAtivas = set([fila for _, fila in processosAtivos])
            if len(filasAtivas) > 1:
                momentosSimultaneos.append((t, processosAtivos, filasAtivas))
        
        if momentosSimultaneos:
            print(f"{Cores.VERDE}✓ Execução simultânea: {len(momentosSimultaneos)} momentos detectados{Cores.RESET}")
        else:
            print(f"{Cores.VERDE}✓ Nenhuma execução simultânea detectada{Cores.RESET}")

    def relatorio(self):
        print(f"\n{Cores.ROXO}{Cores.NEGRITO}===== RELATÓRIO DA SIMULAÇÃO ====={Cores.RESET}")

        # Análise de execução simultânea
        self.detectarExecucaoSimultanea()

        print(f"\n{Cores.AZUL}{Cores.NEGRITO}Tempo total de simulação: {self.tempoAtual}ms{Cores.RESET}")
