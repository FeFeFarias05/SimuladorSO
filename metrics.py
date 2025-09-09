class Metrics:
    def __init__(self):
        self.context_switches = 0
        self.tempos_espera = {}
        self.tempos_resposta = {}
        self.tempos_turnaround = {}

    def registrar_espera(self, processo, tempo):
        self.tempos_espera[processo.name] = tempo

    def registrar_resposta(self, processo, tempo):
        self.tempos_resposta[processo.name] = tempo

    def registrar_turnaround(self, processo, tempo):
        self.tempos_turnaround[processo.name] = tempo