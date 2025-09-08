from process import Processo

class Escalonador:
    def __init__(self, processos):
        self.bloqueados = []
        self.terminados = []
        self.tempo = 0
        self.intervalo = 1  # 1 ms
        self.processos = processos
        self.processos.sort(key=lambda x: x.credito, reverse=True) # ordena por crédito inicialmente

    def escalona(self):
        processo = next((processo for processo in self.processos 
                        if (processo.status == 'ready' or processo.status == 'running') 
                        and processo.credito > 0), None)
        
        if processo is None:
            self.calcula_credito()
            self.reordena()
            processo = next((processo for processo in self.processos 
                            if (processo.status == 'ready' or processo.status == 'running') 
                            and processo.credito > 0), None)
        
        if processo:
            processo.status = 'running'
            processo.credito -= 1
        
        return processo
        
    def calcula_credito(self):
        """Função para o cálculo de créditos em caso de empate de prioridade"""
        for proc in self.processos:
            proc.credito = (proc.credito / 2) + proc.prioridade

        for proc in self.blocked:
            proc.credito = (proc.credito / 2) + proc.prioridade

    def reordena(self):
        """Reordena os processos por crédito em ordem decrescente"""
        self.processos.sort(key=lambda x: x.credito, reverse=True)
        return

    def processa_blocked(self, surto_cpu):
        """Processa os processos bloqueados por I/O"""
        if len(self.blocked) > 0:
            # processa syscalls
            for blocked in self.blocked[:]:  # cópia da lista para evitar problemas de modificação durante iteração
                print(f"Processo {blocked.nome} bloqueado por I/O: {blocked.tempo_io}")
                blocked.tempo_io -= self.intervalo
                if blocked.tempo_io == 0:
                    print(f"Processo {blocked.nome} desbloqueado")
                    blocked.status = 'ready'
                    blocked.cpu_burst = surto_cpu.get(blocked.nome, [0, 0])[0]
                    blocked.tempo_io = surto_cpu.get(blocked.nome, [0, 0])[1]
                    self.processos.append(blocked)
                    self.blocked.remove(blocked)

    def executar_simulacao(self):
        """Executa a simulação completa do escalonamento"""
        cont = 0
        surto_cpu = {}
        linha_tempo_cpu = []

        while self.processos or self.blocked:
            print(f"Execução {cont}")
            
            # Processa processos bloqueados
            self.processa_blocked(surto_cpu)

            # Escala um processo se houver algum disponível
            if self.processos:
                proces = self.escalona()
                if proces is None:
                    break
                    
                # Marca estado de todos os processos
                for p in [*self.processos, *self.blocked, *self.exit]:
                    p.linha_tempo.append(p.status)
                linha_tempo_cpu.append(proces.nome)
                
                print(f"Processo em execução: {proces.nome}")
                self.tempo += self.intervalo
                
                if proces.tempo_inicio is None:
                    proces.tempo_inicio = self.tempo

                # Processamento do CPU burst e I/O
                if proces.tempo_io > 0 and proces.cpu_burst > 0:
                    if surto_cpu.get(proces.nome) is None:
                        surto_cpu[proces.nome] = [proces.cpu_burst, proces.tempo_io]
                    
                    proces.cpu_burst -= self.intervalo
                    print(f"Processo {proces.nome} CPU Burst: {proces.cpu_burst}")
                    
                    if proces.cpu_burst == 0:
                        # bloqueia o processo
                        print(f"Processo {proces.nome} bloqueado por I/O: {proces.tempo_io}")
                        proces.status = 'blocked'
                        self.blocked.append(proces)
                        self.processos.remove(proces)
                
                # Reduz tempo total de CPU
                print(f"Processo {proces.nome} Tempo total de CPU: {proces.tempo_total_cpu}")
                proces.tempo_total_cpu -= self.intervalo
                
                # Verifica se o processo terminou
                if proces.tempo_total_cpu <= 0:
                    print(f"Processo {proces.nome} finalizado")
                    proces.status = 'exit'
                    proces.tempo_fim = self.tempo + self.intervalo
                    try:
                        self.processos.remove(proces)
                    except ValueError:
                        self.blocked.remove(proces)
                    self.exit.append(proces)
                
                # Define status como ready se ainda estiver na lista de processos
                if proces in self.processos:
                    proces.status = 'ready'
                    
                print(f"Fim da execução {cont} - Tempo: {self.tempo}ms")
                cont += 1
            else:
                # Se não há processos prontos, só avança o tempo para os bloqueados
                if self.blocked:
                    self.tempo += self.intervalo
                    linha_tempo_cpu.append('-')
                    for p in [*self.processos, *self.blocked, *self.exit]:
                        p.linha_tempo.append(p.status)

        return linha_tempo_cpu

    def gerar_relatorio(self, linha_tempo_cpu):
        """Gera o relatório final da simulação"""
        # Marca estado final para todos
        for p in self.exit:
            while len(p.linha_tempo) < len(linha_tempo_cpu):
                p.linha_tempo.append('exit')

        # Gera relatório final
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
        
        for p in sorted(self.exit, key=lambda x: x.nome):
            linha = " ".join(estado_formatado.get(s, '?') for s in p.linha_tempo)
            print(f"{p.nome}: {linha}")

        print("\nLegenda: \n")
        print("R: Ready, r: Running, B: Blocked, E: Exit")

        print("\n--- Turnaround Time ---")
        for p in sorted(self.exit, key=lambda x: x.nome):
            turnaround = p.tempo_fim  # assumindo chegada em t=0
            print(f"{p.nome}: {turnaround}ms")

    def __str__(self):
        return f'Processos: {self.processos}'
