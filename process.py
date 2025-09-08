class Processo:
    def __init__(self, nome, cpu_burst, tempo_io, tempo_total_cpu, ordem, prioridade):
        self.nome = nome
        self.cpu_burst = cpu_burst
        self.tempo_io = 0 if tempo_io == "-" else tempo_io
        self.tempo_total_cpu = tempo_total_cpu
        self.ordem = ordem
        self.prioridade = prioridade
        self.credito = prioridade  # inicializa o crédito com a prioridade
        self.status = 'pronto'

    def __str__(self):
        return f"Processo: {self.nome}, CPU Burst: {self.cpu_burst}, Tempo I/O: {self.tempo_io}, Tempo Total CPU: {self.tempo_total_cpu}, Ordem: {self.ordem}, Prioridade: {self.prioridade}, Crédito: {self.credito}, Status: {self.status}"