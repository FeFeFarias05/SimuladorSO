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

        self.tempo_restante_burst = cpu_burst
        self.tempo_restante_total = tempo_total_cpu
        self.tempo_bloqueado = 0
        self.tempo_espera = 0
        self.tempo_resposta = None
        self.tempo_finalizacao = None
        self.tempo_primeira_resposta = None
        self.fila_atual = 0
        
    def __str__(self):
        return f"Processo: {self.nome}, CPU Burst: {self.cpu_burst}, Tempo I/O: {self.tempo_io}, Tempo Total CPU: {self.tempo_total_cpu}, Ordem: {self.ordem}, Prioridade: {self.prioridade}, Crédito: {self.credito}, Status: {self.status}"