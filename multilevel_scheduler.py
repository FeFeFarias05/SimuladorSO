from process import Processo
from collections import deque

class EscalonadorMultinivel:
    def __init__(self, processos, quantum_fila0=5, quantum_fila1=15):
        
        # Validação dos quantums conforme especificação
        if not (1 <= quantum_fila0 <= 10):
            raise ValueError(f"Quantum da Fila 0 deve estar entre 1-10ms. Valor fornecido: {quantum_fila0}ms")
        if not (11 <= quantum_fila1 <= 20):
            raise ValueError(f"Quantum da Fila 1 deve estar entre 11-20ms. Valor fornecido: {quantum_fila1}ms")
            
        # Configuração dos quantums
        self.quantum_fila0 = quantum_fila0 
        self.quantum_fila1 = quantum_fila1
        
        self.fila0 = deque()  # Round Robin com quantum pequeno
        self.fila1 = deque()  # Round Robin com quantum maior
        self.fila2 = deque()  # FCFS
        
        # Processos bloqueados e finalizados
        self.bloqueados = []
        self.finalizados = []
        
        # Controle de tempo
        self.tempo_atual = 0
        self.processo_executando = None
        self.quantum_restante = 0
        
        # Inicializa todos os processos na fila 0, ordenados por prioridade
        processos_ordenados = sorted(processos, key=lambda p: p.prioridade)
        for processo in processos_ordenados:
            processo.fila_atual = 0
            processo.status = 'ready'
            self.fila0.append(processo)
        
        # Log da execução
        self.linha_tempo_cpu = []
        self.log_execucao = []

    def obter_proximo_processo(self):
        """
        Seleciona o próximo processo seguindo a prioridade das filas:
        1. Fila 0 (maior prioridade)
        2. Fila 1 (prioridade média) 
        3. Fila 2 (menor prioridade)
        """
        # Prioridade 1: Fila 0 (quantum pequeno)
        if self.fila0:
            processo = self.fila0.popleft()
            processo.quantum_restante = self.quantum_fila0
            return processo
        
        # Prioridade 2: Fila 1 (quantum maior)  
        if self.fila1:
            processo = self.fila1.popleft()
            processo.quantum_restante = self.quantum_fila1
            return processo

        # Prioridade 3: Fila 2 (FCFS - sem quantum)
        if self.fila2:
            processo = self.fila2.popleft()
            processo.quantum_restante = float('inf')  # FCFS executa até terminar ou bloquear
            return processo
            
        return None

    def mover_processo_para_fila_inferior(self, processo):
        """Move processo para fila de menor prioridade quando quantum expira"""
        if processo.fila_atual == 0:
            processo.fila_atual = 1
            self.fila1.append(processo)
            self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} movido para Fila 1 (quantum expirado)")
        elif processo.fila_atual == 1:
            processo.fila_atual = 3  
            self.fila2.append(processo)
            self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} movido para Fila 3 (quantum expirado)")
        # Fila 3 é FCFS, não move para lugar algum

    def retornar_processo_fila_original(self, processo):
        """Retorna processo para a fila onde estava quando foi bloqueado"""
        processo.status = 'ready'
        
        if processo.fila_atual == 0:
            self.fila0.append(processo)
        elif processo.fila_atual == 1:
            self.fila1.append(processo)  
        elif processo.fila_atual == 2:
            self.fila2.append(processo)
        self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} retornou do I/O para Fila {processo.fila_atual}")

    def processar_bloqueados(self):
        """Processa processos bloqueados por I/O"""
        for processo in self.bloqueados[:]:
            processo.tempo_io_restante -= 1
            if processo.tempo_io_restante <= 0:
                # Processo terminou I/O, volta para a fila onde estava
                processo.resetar_cpu_burst()
                self.bloqueados.remove(processo)
                self.retornar_processo_fila_original(processo)

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
            self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} FINALIZADO")
            return 'finished'
        
        # Verifica se CPU burst terminou (vai para I/O)
        if processo.cpu_burst_atual <= 0 and processo.tempo_io_original > 0:
            processo.salvar_cpu_burst()
            processo.status = 'blocked'
            processo.tempo_io_restante = processo.tempo_io_original
            self.bloqueados.append(processo)
            self.log_execucao.append(f"T{self.tempo_atual}: Processo {processo.nome} BLOQUEADO para I/O")
            return 'blocked'
        
        # Verifica se quantum expirou
        if processo.quantum_restante <= 0:
            processo.status = 'ready'
            self.mover_processo_para_fila_inferior(processo)
            return 'quantum_expired'
            
        return 'running'

    def verificar_preempcao(self, processo_atual):
        """
        Verifica se há necessidade de preempção:
        - Fila 0 sempre preempta Filas 1 e 2
        - Fila 1 sempre preempta Fila 2
        """
        if processo_atual is None:
            return False
            
        # Se há processos na fila 0 e processo atual não é da fila 0
        if self.fila0 and processo_atual.fila_atual != 0:
            return True
            
        # Se há processos na fila 1 e processo atual é da fila 3
        if self.fila1 and processo_atual.fila_atual == 3:
            return True
            
        return False

    def executar_simulacao(self):
        """Executa a simulação completa do escalonador multinível"""
        print("=== INICIANDO SIMULAÇÃO DO ESCALONADOR MULTINÍVEL COM FEEDBACK ===")
        print(f"Quantum Fila 0: {self.quantum_fila0}ms")
        print(f"Quantum Fila 1: {self.quantum_fila1}ms")
        print(f"Fila 3: FCFS (sem quantum)")
        print("=" * 60)

        while (self.fila0 or self.fila1 or self.fila2 or
               self.bloqueados or self.processo_executando):
            
            # Processa processos bloqueados por I/O
            self.processar_bloqueados()
            
            # Verifica preempção
            if self.verificar_preempcao(self.processo_executando):
                if self.processo_executando:
                    # Retorna processo atual para sua fila
                    if self.processo_executando.fila_atual == 0:
                        self.fila0.appendleft(self.processo_executando)
                    elif self.processo_executando.fila_atual == 1:
                        self.fila1.appendleft(self.processo_executando)
                    else:
                        self.fila2.appendleft(self.processo_executando)

                    self.processo_executando.status = 'ready'
                    self.log_execucao.append(f"T{self.tempo_atual}: Processo {self.processo_executando.nome} PREEMPTADO")
                
                self.processo_executando = None
            
            # Se não há processo executando, escalona um novo
            if self.processo_executando is None:
                self.processo_executando = self.obter_proximo_processo()
            
            # Executa processo atual
            if self.processo_executando:
                nome_processo = self.processo_executando.nome
                resultado = self.executar_processo(self.processo_executando)
                
                if resultado in ['finished', 'blocked', 'quantum_expired']:
                    self.processo_executando = None
                    
                self.linha_tempo_cpu.append(nome_processo)
            else:
                # CPU ociosa
                self.linha_tempo_cpu.append('-')
            
            # Atualiza linha do tempo de todos os processos
            todos_processos = (list(self.fila0) + list(self.fila1) + list(self.fila2) + 
                             self.bloqueados + self.finalizados)
            if self.processo_executando:
                todos_processos.append(self.processo_executando)
                
            for p in todos_processos:
                if not hasattr(p, 'linha_tempo'):
                    p.linha_tempo = []
                p.linha_tempo.append(p.status)
            
            self.tempo_atual += 1
        
        print("=== SIMULAÇÃO CONCLUÍDA ===")
        return self.linha_tempo_cpu

    def gerar_relatorio(self):
        """Gera relatório completo da simulação"""
        print("\n" + "="*60)
        print("RELATÓRIO DA SIMULAÇÃO")
        print("="*60)
        
        # Linha do tempo da CPU
        print("\n--- LINHA DO TEMPO DA CPU ---")
        print("Tempo: " + " ".join([f"{i:>2}" for i in range(len(self.linha_tempo_cpu))]))
        print("CPU:   " + " ".join([f"{nome:>2}" for nome in self.linha_tempo_cpu]))
        
        # Linha do tempo dos processos
        print("\n--- LINHA DO TEMPO DOS PROCESSOS ---")
        estado_formatado = {
            'ready': 'R',
            'running': 'E', 
            'blocked': 'B',
            'finished': 'F'
        }
        
        for p in sorted(self.finalizados, key=lambda x: x.nome):
            # Completa a linha do tempo se necessário
            while len(p.linha_tempo) < len(self.linha_tempo_cpu):
                p.linha_tempo.append('finished')
                
            linha = " ".join([f"{estado_formatado.get(s, '?'):>2}" for s in p.linha_tempo])
            print(f"{p.nome}:   {linha}")
        
        print("\nLegenda: R=Ready, E=Executando, B=Bloqueado, F=Finalizado")
        
        # Estatísticas
        print("\n--- ESTATÍSTICAS ---")
        for p in sorted(self.finalizados, key=lambda x: x.nome):
            turnaround = p.tempo_fim if p.tempo_fim else self.tempo_atual
            tempo_resposta = p.tempo_inicio if p.tempo_inicio else 0
            print(f"{p.nome}: Turnaround={turnaround}ms, Tempo de Resposta={tempo_resposta}ms")
        
        # Log de execução
        print("\n--- LOG DE EXECUÇÃO ---")
        for log in self.log_execucao[-20:]:
            print(log)
        
        print(f"\nTempo total de simulação: {self.tempo_atual}ms")
