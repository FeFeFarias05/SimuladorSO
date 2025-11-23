"""
Memória Física com política de substituição LRU
"""

import time

class PhysicalMemory:
    """
    Representa a memória física com molduras (frames)
    Implementa política de substituição LRU (Least Recently Used)
    """
    
    def __init__(self, num_frames):
        """
        Inicializa a memória física
        
        Args:
            num_frames: Número de molduras disponíveis
        """
        self.num_frames = num_frames
        # Inicializa todas as molduras com -1 (livres)
        self.frames = [-1] * num_frames
        # Armazena o timestamp de último acesso para cada moldura
        self.last_access = [0] * num_frames
        # Contador global para timestamps
        self.access_counter = 0
        
        # Estatísticas
        self.page_faults = 0
        self.page_replacements = 0
    
    def allocate_frame(self, virtual_address):
        """
        Aloca uma moldura para um endereço virtual
        
        Args:
            virtual_address: Endereço virtual a ser mapeado
            
        Returns:
            Tupla (frame_number, was_replacement)
        """
        self.access_counter += 1
        
        # Procura uma moldura livre
        for i in range(self.num_frames):
            if self.frames[i] == -1:
                self.frames[i] = virtual_address
                self.last_access[i] = self.access_counter
                self.page_faults += 1
                return (i, False)
        
        # Memória lotada - usa LRU para substituir
        lru_frame = self._find_lru_frame()
        self.frames[lru_frame] = virtual_address
        self.last_access[lru_frame] = self.access_counter
        self.page_faults += 1
        self.page_replacements += 1
        return (lru_frame, True)
    
    def update_access(self, frame):
        """
        Atualiza o timestamp de acesso de uma moldura
        
        Args:
            frame: Número da moldura acessada
        """
        self.access_counter += 1
        if 0 <= frame < self.num_frames:
            self.last_access[frame] = self.access_counter
    
    def _find_lru_frame(self):
        """
        Encontra a moldura menos recentemente usada
        
        Returns:
            Índice da moldura LRU
        """
        min_access = min(self.last_access)
        return self.last_access.index(min_access)
    
    def get_frame_address(self, frame):
        """
        Retorna o endereço virtual armazenado em uma moldura
        
        Args:
            frame: Número da moldura
            
        Returns:
            Endereço virtual ou -1 se a moldura estiver livre
        """
        if 0 <= frame < self.num_frames:
            return self.frames[frame]
        return -1
    
    def free_frame(self, frame):
        """
        Libera uma moldura
        
        Args:
            frame: Número da moldura a liberar
        """
        if 0 <= frame < self.num_frames:
            self.frames[frame] = -1
            self.last_access[frame] = 0
    
    def is_full(self):
        """
        Verifica se a memória está cheia
        
        Returns:
            True se todas as molduras estão ocupadas
        """
        return all(frame != -1 for frame in self.frames)
    
    def get_used_frames(self):
        """
        Retorna o número de molduras em uso
        
        Returns:
            Número de molduras ocupadas
        """
        return sum(1 for frame in self.frames if frame != -1)
    
    def get_statistics(self):
        """
        Retorna estatísticas da memória física
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            'total_frames': self.num_frames,
            'used_frames': self.get_used_frames(),
            'free_frames': self.num_frames - self.get_used_frames(),
            'page_faults': self.page_faults,
            'page_replacements': self.page_replacements,
            'utilization': self.get_used_frames() / self.num_frames
        }
    
    def get_contents(self):
        """
        Retorna o conteúdo de todas as molduras
        
        Returns:
            Lista de tuplas (frame_number, address, last_access)
        """
        contents = []
        for i in range(self.num_frames):
            contents.append((i, self.frames[i], self.last_access[i]))
        return contents
    
    def __str__(self):
        """Representação em string da memória física"""
        result = [f"Memória Física ({self.get_used_frames()}/{self.num_frames} molduras em uso):"]
        
        for i, addr in enumerate(self.frames):
            if addr != -1:
                result.append(f"  Frame {i}: Endereço Virtual {addr} (acesso: {self.last_access[i]})")
            else:
                result.append(f"  Frame {i}: [livre]")
        
        return "\n".join(result)
    
    def to_dict(self):
        """
        Converte a memória física para dicionário
        
        Returns:
            Dicionário representando a memória
        """
        return {
            'frames': self.frames.copy(),
            'last_access': self.last_access.copy(),
            'statistics': self.get_statistics()
        }
