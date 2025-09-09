from process import Processo
from metrics import Metrics
from validator import validar_quantum

class Escalonador:
    def __init__(self, processos, quantum_0=5, quantum_1=15, verbose=False):
        validar_quantum(quantum_0, quantum_1)
        self.bloqueados = []
        self.terminados = []
        self.tempo = 0
        self.intervalo = 1  # 1 ms
        self.processos = sorted(processos, key=lambda x: x.prioridade)  # Ordena por prioridade
        self.quantum_0 = quantum_0
        self.quantum_1 = quantum_1
        self.verbose = verbose
        self.metrics = Metrics()
        self.context_switches = 0

    def log(self, msg):
        if self.verbose:
            print(msg)

    def escalona(self):
        # Prioridade: processos prontos na fila 0, depois fila 1, depois fila 2
        for proc in self.processos:
            if proc.status in ('ready', 'running'):
                return proc
        return None

    def processa_blocked(self):
        for blocked in self.bloqueados[:]:
            blocked.tempo_io -= self.intervalo
            self.log(f"Processo {blocked.nome} bloqueado por I/O: {blocked.tempo_io}")
            if blocked.tempo_io <= 0:
                blocked.status = 'ready'
                self.processos.append(blocked)
                self.bloqueados.remove(blocked)
                self.log(f"Processo {blocked.nome} desbloqueado")

    def executar_simulacao(self):
        cont = 0
        linha_tempo_cpu = []

        while self.processos or self.bloqueados:
            self.log(f"Execução {cont}")
            self.processa_blocked()

            if self.processos:
                proc = self.escalona()
                if proc is None:
                    self.tempo += self.intervalo
                    linha_tempo_cpu.append('-')
                    continue

                self.context_switches += 1
                proc.status = 'running'
                if proc.tempo_inicio is None:
                    proc.tempo_inicio = self.tempo

                # Métrica de resposta
                if proc.nome not in self.metrics.tempos_resposta:
                    self.metrics.registrar_resposta(proc, self.tempo)

                # Quantum por fila (simples: prioridade baixa = quantum maior)
                if proc.fila == 0:
                    quantum = self.quantum_0
                elif proc.fila == 1:
                    quantum = self.quantum_1
                else:
                    quantum = proc.cpu_burst  # FCFS

                tempo_exec = min(quantum, proc.cpu_burst, proc.tempo_total_cpu)
                self.log(f"{self.tempo}ms: Processo {proc.nome} executando na Fila {proc.fila} por {tempo_exec}ms")

                self.tempo += tempo_exec
                proc.cpu_burst -= tempo_exec
                proc.tempo_total_cpu -= tempo_exec

                # Atualiza espera dos outros processos
                for p in self.processos:
                    if p != proc and p.status == 'ready':
                        p.tempo_espera += tempo_exec

                linha_tempo_cpu.append(proc.nome)

                # Verifica término
                if proc.tempo_total_cpu <= 0:
                    proc.status = 'exit'
                    proc.tempo_fim = self.tempo
                    self.metrics.registrar_turnaround(proc, proc.tempo_fim)
                    self.terminados.append(proc)
                    self.processos.remove(proc)
                    self.log(f"{self.tempo}ms: Processo {proc.nome} finalizado")
                    continue

                # Verifica E/S
                if proc.cpu_burst == 0 and proc.tempo_total_cpu > 0:
                    proc.status = 'blocked'
                    proc.tempo_io = proc.io_time
                    proc.cpu_burst = proc.cpu_burst_original
                    self.bloqueados.append(proc)
                    self.processos.remove(proc)
                    self.log(f"{self.tempo}ms: Processo {proc.nome} foi para E/S por {proc.io_time}ms")
                    continue

                # Quantum estourado, desce de fila
                if tempo_exec == quantum and proc.fila < 2:
                    proc.fila += 1
                    proc.status = 'ready'
                    self.log(f"{self.tempo}ms: Processo {proc.nome} desceu para Fila {proc.fila}")
                else:
                    proc.status = 'ready'

                cont += 1
            else:
                # Só bloqueados, avança tempo
                self.tempo += self.intervalo
                linha_tempo_cpu.append('-')

        self.metrics.context_switches = self.context_switches
        self.gerar_relatorio(linha_tempo_cpu)

    def gerar_relatorio(self, linha_tempo_cpu):
        # Marca estado final para todos
        for p in self.terminados:
            while len(p.linha_tempo) < len(linha_tempo_cpu):
                p.linha_tempo.append('exit')

        print("\n--- Linha do Tempo da CPU ---")
        print("Tempo: ", " ".join([f"{i:>2}" for i in range(len(linha_tempo_cpu))]))
        print("CPU:   ", " ".join([f"{nome:>2}" for nome in linha_tempo_cpu]))

        print("\n--- Linha do Tempo dos Processos ---")
        estado_formatado = {
            'ready': 'R',
            'running': 'r',
            'blocked': 'B',
            'exit': 'E'
        }
        for p in sorted(self.terminados, key=lambda x: x.nome):
            linha = " ".join(estado_formatado.get(s, '?') for s in p.linha_tempo)
            print(f"{p.nome}: {linha}")

        print("\nLegenda: \nR: Ready, r: Running, B: Blocked, E: Exit")

        print("\n--- Métricas ---")
        for p in sorted(self.terminados, key=lambda x: x.nome):
            espera = self.metrics.tempos_espera.get(p.nome, 0)
            resposta = self.metrics.tempos_resposta.get(p.nome, 0)
            turnaround = self.metrics.tempos_turnaround.get(p.nome, 0)
            print(f"{p.nome}: Espera={espera}ms, Resposta={resposta}ms, Turnaround={turnaround}ms")
        print(f"Trocas de contexto: {self.metrics.context_switches}")

    def __str__(self):
        return f'Processos: {self.processos}'
