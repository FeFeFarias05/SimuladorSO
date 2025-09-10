class Processo:
    def __init__(self, nome, cpu_burst, tempo_io, tempo_total_cpu, ordem=0, prioridade=0):
        self.nome = nome
        self.cpu_burst_original = cpu_burst
        self.cpu_burst_atual = cpu_burst  # CPU burst atual (pode ser interrompido)
        self.tempo_io_original = 0 if tempo_io == "-" else tempo_io
        self.tempo_io_restante = self.tempo_io_original
        self.tempo_total_cpu = tempo_total_cpu
        self.tempo_cpu_restante = tempo_total_cpu
        self.ordem = ordem
        self.prioridade = prioridade
        
        # Estados: 'ready', 'running', 'blocked', 'finished'
        self.status = 'ready'
        
        # Controle do escalonador multinível
        self.fila_atual = 0
        self.quantum_restante = 0
        
        # Estatísticas
        self.tempo_chegada = 0
        self.tempo_inicio = None
        self.tempo_fim = None
        self.linha_tempo = []
        
        # Controle de I/O
        self.em_io = False
        self.cpu_bursts_salvos = []  # Para salvar CPU bursts quando vai para I/O

    def resetar_cpu_burst(self):
        """Reseta o CPU burst quando o processo retorna do I/O"""
        if self.cpu_bursts_salvos:
            self.cpu_burst_atual = self.cpu_bursts_salvos.pop(0)
        else:
            self.cpu_burst_atual = self.cpu_burst_original

    def salvar_cpu_burst(self):
        """Salva o estado atual do CPU burst antes de ir para I/O"""
        if self.cpu_burst_atual > 0:
            self.cpu_bursts_salvos.append(self.cpu_burst_atual)

    def __str__(self):
        return f"Processo: {self.nome}, Fila: {self.fila_atual}, Status: {self.status}, CPU Restante: {self.tempo_cpu_restante}ms"