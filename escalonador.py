from operator import attrgetter
from process import Processo
#versao alternativa
class Escalonador:
    def __init__(self, processos):
        self.ready = processos
        self.blocked = []
        self.exit = []
        self.tempo = 0
        self.intervalo = 1  # ms
        self.reordena()

    def escalona(self):
        """Seleciona o próximo processo a executar"""
        processo = next(
            (p for p in self.ready if p.credito > 0),
            None
        )

        if processo is None:
            self.calcula_credito()
            self.reordena()
            processo = next(
                (p for p in self.ready if p.credito > 0),
                None
            )

        if processo:
            processo.status = 'running'
            processo.credito -= 1

        return processo

    def calcula_credito(self):
        """Recalcula créditos de todos os processos"""
        for proc in self.ready + self.blocked:
            proc.credito = (proc.credito / 2) + proc.prioridade

    def reordena(self):
        """Reordena por crédito (decrescente)"""
        self.ready.sort(key=attrgetter("credito"), reverse=True)

    def processa_bloqueados(self, surto_cpu):
        """Atualiza processos bloqueados"""
        for p in self.blocked[:]:
            p.tempo_io -= self.intervalo
            if p.tempo_io <= 0:
                p.status = 'ready'
                p.cpu_burst, p.tempo_io = surto_cpu.get(p.nome, (0, 0))
                self.ready.append(p)
                self.blocked.remove(p)

    def processa_cpu(self, processo, surto_cpu):
        """Executa processamento de CPU e I/O de um processo"""
        if processo.tempo_io > 0 and processo.cpu_burst > 0:
            if processo.nome not in surto_cpu:
                surto_cpu[processo.nome] = (processo.cpu_burst, processo.tempo_io)
            processo.cpu_burst -= self.intervalo
            if processo.cpu_burst <= 0:
                processo.status = 'blocked'
                self.blocked.append(processo)
                self.ready.remove(processo)

        processo.tempo_total_cpu -= self.intervalo
        if processo.tempo_total_cpu <= 0:
            processo.status = 'exit'
            processo.tempo_fim = self.tempo + self.intervalo
            try:
                self.ready.remove(processo)
            except ValueError:
                self.blocked.remove(processo)
            self.exit.append(processo)

        if processo in self.ready:
            processo.status = 'ready'

    def executar_simulacao(self):
        """Loop principal da simulação"""
        cont = 0
        surto_cpu = {}
        linha_tempo_cpu = []

        while self.ready or self.blocked:
            self.processa_bloqueados(surto_cpu)
            processo = self.escalona()

            if processo is None:
                self.tempo += self.intervalo
                linha_tempo_cpu.append('-')
            else:
                self.processa_cpu(processo, surto_cpu)
                linha_tempo_cpu.append(processo.nome)
                self.tempo += self.intervalo

            for p in self.ready + self.blocked + self.exit:
                if not hasattr(p, "linha_tempo"):
                    p.linha_tempo = []
                p.linha_tempo.append(p.status)

            cont += 1

        return linha_tempo_cpu
