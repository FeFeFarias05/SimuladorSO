

from enum import Enum
from typing import Optional

class estados(Enum):

    pronto = "Pronto"
    executando = "Executando"
    bloqueado = "Bloqueado"
    finalizado = "Finalizado"

class Process:

    def __init__(self, nome: str, cpu_burst: int, io_time: int, 
                 total_cpu_time: int, priority: int):

        self.nome = nome
        self.cpu_burst = cpu_burst
        self.io_time = io_time
        self.total_cpu_time = total_cpu_time
        self.priority = priority
        self.state = estados.pronto
        self.current_queue = 0
        
        # Tempos para estatísticas
        self.arrival_time = 0
        self.start_time: Optional[int] = None
        self.finish_time: Optional[int] = None
        self.waiting_time = 0
        self.response_time: Optional[int] = None
        self.turnaround_time: Optional[int] = None
        
        # Controle de execução
        self.remaining_cpu_time = total_cpu_time
        self.current_burst_time = 0  # Tempo executado no burst atual
        self.remaining_io_time = 0   # Tempo restante de E/S
        self.context_switches = 0    # Número de trocas de contexto
        
    def needs_io(self) -> bool:
        return (self.current_burst_time >= self.cpu_burst and 
                self.remaining_cpu_time > 0 and 
                self.io_time > 0)
    
    def is_finished(self) -> bool:
        """
        Verifica se o processo terminou.
        
        Returns:
            True se não há mais tempo de CPU restante
        """
        return self.remaining_cpu_time <= 0
    
    def execute(self, time_slice: int) -> int:
        """
        Executa o processo por um período de tempo.
        
        Args:
            time_slice: Tempo máximo de execução
            
        Returns:
            Tempo efetivamente executado
        """
        if self.state != ProcessState.RUNNING:
            return 0
            
        # Calcula o tempo que pode executar
        time_to_run = min(
            time_slice,
            self.remaining_cpu_time,
            self.cpu_burst - self.current_burst_time
        )
        
        # Executa
        self.remaining_cpu_time -= time_to_run
        self.current_burst_time += time_to_run
        
        return time_to_run
    
    def start_io(self) -> None:
        """Inicia operação de E/S."""
        self.state = estados.bloqueado
        self.remaining_io_time = self.io_time
        self.current_burst_time = 0  # Reset para próximo burst
    
    def process_io(self, time_elapsed: int) -> bool:
        """
        Processa E/S por um período de tempo.
        
        Args:
            time_elapsed: Tempo decorrido
            
        Returns:
            True se a E/S foi concluída
        """
        if self.state != estados.bloqueado:
            return False
            
        self.remaining_io_time -= time_elapsed
        
        if self.remaining_io_time <= 0:
            self.state = estados.pronto
            self.remaining_io_time = 0
            return True
            
        return False
    
    def move_to_next_queue(self) -> None:
        """Move o processo para a próxima fila (downgrade)."""
        if self.current_queue < 2:
            self.current_queue += 1
            self.context_switches += 1
    
    def set_running(self, current_time: int) -> None:
        """
        Define o processo como executando.
        
        Args:
            current_time: Tempo atual do sistema
        """
        self.state = estados.executando

        # Registra o tempo de início se for a primeira vez
        if self.start_time is None:
            self.start_time = current_time
            self.response_time = current_time - self.arrival_time
    
    def set_finished(self, current_time: int) -> None:
        """
        Define o processo como finalizado.
        
        Args:
            current_time: Tempo atual do sistema
        """
        self.state = estados.finalizado
        self.finish_time = current_time
        self.turnaround_time = current_time - self.arrival_time
    
    def add_waiting_time(self, time: int) -> None:
        """Adiciona tempo de espera."""
        self.waiting_time += time
    
    def __str__(self) -> str:
        """Representação string do processo."""
        return (f"Process(name={self.name}, state={self.state.value}, "
                f"queue={self.current_queue}, remaining_cpu={self.remaining_cpu_time})")
    
    def __repr__(self) -> str:
        """Representação detalhada do processo."""
        return self.__str__()
