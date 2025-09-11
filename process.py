class Processo:
    def __init__(self, nome, cpuBurst, tempoIo, tempoTotalCpu, ordem=0, prioridade=0):
        self.nome = nome
        self.cpuBurstOriginal = cpuBurst
        self.cpuBurstAtual = cpuBurst
        self.tempoIoOriginal = 0 if tempoIo == "-" else tempoIo
        self.tempoIoRestante = self.tempoIoOriginal
        self.tempoTotalCpu = tempoTotalCpu
        self.tempoCpuRestante = tempoTotalCpu
        self.ordem = ordem
        self.prioridade = prioridade
        
        self.status = 'ready'
        
        self.filaAtual = 0
        self.quantumRestante = 0
        
        self.tempoChegada = 0
        self.tempoInicio = None
        self.tempoFim = None
        self.linhaTempo = []

        self.emIo = False
        self.cpuBurstsSalvos = []

    def resetarCpuBurst(self):
        if self.cpuBurstsSalvos:
            self.cpuBurstAtual = self.cpuBurstsSalvos.pop(0)
        else:
            self.cpuBurstAtual = self.cpuBurstOriginal

    def salvarCpuBurst(self):
        if self.cpuBurstAtual > 0:
            self.cpuBurstsSalvos.append(self.cpuBurstAtual)

    def __str__(self):
        return f"Processo: {self.nome}, Fila: {self.filaAtual}, Status: {self.status}, CPU Restante: {self.tempoCpuRestante}ms"