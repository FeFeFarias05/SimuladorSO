"""
Módulo que implementa o escalonador multinível com feedback (MLFQ).
"""

from typing import List, Dict, Any, Optional
from collections import deque
from process import Process, ProcessState

class MLFQScheduler:
    """
    Implementa um escalonador multinível com feedback (MLFQ) com 3 filas:
    - Fila 0: Round Robin (quantum 1-10ms)
    - Fila 1: Round Robin (quantum 11-20ms) 
    - Fila 2: FCFS (sem preempção)
    """
    
    def __init__(self, quantum_q0: int = 5, quantum_q1: int = 15):
        """
        Inicializa o escalonador.
        
        Args:
            quantum_q0: Quantum da fila 0 (1-10ms)
            quantum_q1: Quantum da fila 1 (11-20ms)
        """
        # Validação dos parâmetros
        if not (1 <= quantum_q0 <= 10):
            raise ValueError("Quantum da fila 0 deve estar entre 1 e 10ms")
        if not (11 <= quantum_q1 <= 20):
            raise ValueError("Quantum da fila 1 deve estar entre 11 e 20ms")
            
        self.quantum_q0 = quantum_q0
        self.quantum_q1 = quantum_q1
        
        # Filas de processos prontos
        self.ready_queues: List[deque] = [deque(), deque(), deque()]
        
        # Lista de processos bloqueados
        self.blocked_processes: List[Process] = []
        
        # Processo atualmente em execução
        self.running_process: Optional[Process] = None
        
        # Estatísticas
        self.current_time = 0
        self.total_context_switches = 0
        self.finished_processes: List[Process] = []
        
        # Log de eventos
        self.events_log: List[Dict[str, Any]] = []
        
    def add_process(self, process: Process) -> None:
        """
        Adiciona um processo ao sistema (sempre na fila 0).
        
        Args:
            process: Processo a ser adicionado
        """
        process.arrival_time = self.current_time
        process.current_queue = 0
        process.state = ProcessState.READY
        
        # Adiciona na fila 0 ordenado por prioridade (menor primeiro)
        inserted = False
        for i, p in enumerate(self.ready_queues[0]):
            if process.priority < p.priority:
                self.ready_queues[0].insert(i, process)
                inserted = True
                break
        
        if not inserted:
            self.ready_queues[0].append(process)
            
        self._log_event("ARRIVED", process, f"Adicionado na fila 0")
    
    def _get_next_process(self) -> Optional[Process]:
        """
        Seleciona o próximo processo a ser executado.
        Prioridade: Fila 0 > Fila 1 > Fila 2
        
        Returns:
            Próximo processo ou None se não houver processos prontos
        """
        for queue_idx, queue in enumerate(self.ready_queues):
            if queue:
                process = queue.popleft()
                return process
        return None
    
    def _get_quantum(self, queue_level: int) -> Optional[int]:
        """
        Retorna o quantum para a fila especificada.
        
        Args:
            queue_level: Nível da fila (0, 1, ou 2)
            
        Returns:
            Quantum em ms ou None para FCFS (fila 2)
        """
        if queue_level == 0:
            return self.quantum_q0
        elif queue_level == 1:
            return self.quantum_q1
        else:  # Fila 2 - FCFS
            return None
    
    def _preempt_current_process(self, reason: str) -> None:
        """
        Interrompe o processo atual.
        
        Args:
            reason: Motivo da preempção
        """
        if self.running_process:
            self.running_process.state = ProcessState.READY
            self._log_event("PREEMPTED", self.running_process, reason)
            self.running_process = None
            self.total_context_switches += 1
    
    def _schedule_next_process(self) -> None:
        """Escalona o próximo processo para execução."""
        if self.running_process is None:
            next_process = self._get_next_process()
            if next_process:
                self.running_process = next_process
                self.running_process.set_running(self.current_time)
                self._log_event("SCHEDULED", next_process, 
                              f"Iniciado na fila {next_process.current_queue}")
    
    def _process_io_operations(self, time_elapsed: int) -> None:
        """
        Processa operações de E/S em andamento.
        
        Args:
            time_elapsed: Tempo decorrido
        """
        completed_io = []
        
        for process in self.blocked_processes:
            if process.process_io(time_elapsed):
                completed_io.append(process)
                
        # Remove processos que completaram E/S e os recoloca na fila
        for process in completed_io:
            self.blocked_processes.remove(process)
            self.ready_queues[process.current_queue].append(process)
            self._log_event("IO_COMPLETED", process, 
                          f"Retornou para fila {process.current_queue}")
    
    def _update_waiting_times(self, time_elapsed: int) -> None:
        """
        Atualiza tempos de espera dos processos.
        
        Args:
            time_elapsed: Tempo decorrido
        """
        # Processos nas filas prontas
        for queue in self.ready_queues:
            for process in queue:
                process.add_waiting_time(time_elapsed)
    
    def _log_event(self, event_type: str, process: Process, description: str) -> None:
        """
        Registra um evento no log.
        
        Args:
            event_type: Tipo do evento
            process: Processo envolvido
            description: Descrição do evento
        """
        event = {
            'time': self.current_time,
            'type': event_type,
            'process': process.name,
            'queue': process.current_queue,
            'description': description
        }
        self.events_log.append(event)
    
    def step(self) -> bool:
        """
        Executa um passo da simulação.
        
        Returns:
            True se ainda há processos para executar, False caso contrário
        """
        time_slice = 1  # Granularidade de 1ms
        
        # Processa E/S
        self._process_io_operations(time_slice)
        
        # Escalona próximo processo se necessário
        self._schedule_next_process()
        
        # Executa processo atual
        if self.running_process:
            quantum = self._get_quantum(self.running_process.current_queue)
            
            # Determina tempo de execução
            if quantum is None:  # FCFS - executa até E/S ou finalização
                exec_time = min(time_slice, self.running_process.remaining_cpu_time)
                if self.running_process.needs_io():
                    exec_time = min(exec_time, 
                                  self.running_process.cpu_burst - 
                                  self.running_process.current_burst_time)
            else:  # Round Robin
                exec_time = min(time_slice, quantum)
            
            # Executa o processo
            executed_time = self.running_process.execute(exec_time)
            
            # Verifica se o processo terminou
            if self.running_process.is_finished():
                self.running_process.set_finished(self.current_time + executed_time)
                self.finished_processes.append(self.running_process)
                self._log_event("FINISHED", self.running_process, "Processo finalizado")
                self.running_process = None
                self.total_context_switches += 1
                
            # Verifica se precisa fazer E/S
            elif self.running_process.needs_io():
                self.running_process.start_io()
                self.blocked_processes.append(self.running_process)
                self._log_event("IO_STARTED", self.running_process, 
                              f"Iniciou E/S por {self.running_process.io_time}ms")
                self.running_process = None
                self.total_context_switches += 1
                
            # Verifica se esgotou o quantum (apenas para filas 0 e 1)
            elif (quantum is not None and executed_time >= quantum and 
                  not self.running_process.is_finished()):
                
                # Move para próxima fila se não for a última
                if self.running_process.current_queue < 2:
                    old_queue = self.running_process.current_queue
                    self.running_process.move_to_next_queue()
                    self._log_event("QUEUE_DOWNGRADE", self.running_process,
                                  f"Movido da fila {old_queue} para fila {self.running_process.current_queue}")
                
                # Recoloca na fila apropriada
                self.ready_queues[self.running_process.current_queue].append(self.running_process)
                self._preempt_current_process("Quantum esgotado")
        
        # Atualiza tempos de espera
        self._update_waiting_times(time_slice)
        
        # Avança o tempo
        self.current_time += time_slice
        
        # Verifica se ainda há processos para executar
        has_processes = (
            self.running_process is not None or
            any(queue for queue in self.ready_queues) or
            self.blocked_processes
        )
        
        return has_processes
    
    def run_simulation(self, processes: List[Process]) -> Dict[str, Any]:
        """
        Executa a simulação completa.
        
        Args:
            processes: Lista de processos a serem executados
            
        Returns:
            Dicionário com resultados da simulação
        """
        # Adiciona todos os processos
        for process in processes:
            self.add_process(process)
        
        # Executa simulação
        while self.step():
            pass  # Continue até todos os processos terminarem
        
        # Calcula estatísticas
        return self._calculate_statistics()
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """
        Calcula estatísticas da simulação.
        
        Returns:
            Dicionário com estatísticas
        """
        if not self.finished_processes:
            return {}
        
        # Estatísticas por processo
        process_stats = []
        total_waiting = 0
        total_turnaround = 0
        total_response = 0
        
        for process in self.finished_processes:
            stats = {
                'name': process.name,
                'waiting_time': process.waiting_time,
                'turnaround_time': process.turnaround_time,
                'response_time': process.response_time,
                'context_switches': process.context_switches
            }
            process_stats.append(stats)
            
            total_waiting += process.waiting_time
            total_turnaround += process.turnaround_time or 0
            total_response += process.response_time or 0
        
        num_processes = len(self.finished_processes)
        
        return {
            'total_time': self.current_time,
            'total_context_switches': self.total_context_switches,
            'average_waiting_time': total_waiting / num_processes,
            'average_turnaround_time': total_turnaround / num_processes,
            'average_response_time': total_response / num_processes,
            'process_statistics': process_stats,
            'events_log': self.events_log
        }
