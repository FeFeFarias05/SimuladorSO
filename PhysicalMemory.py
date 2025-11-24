"""
Memória Física com política de substituição LRU
Agora armazena o VPN, conforme exigido pelo trabalho.
"""

class PhysicalMemory:
    """
    Representa a memória física com molduras (frames)
    Implementa política de substituição LRU (Least Recently Used)
    Armazena **VPN**, não endereços virtuais completos
    """
    
    def __init__(self, num_frames):
        """
        Inicializa a memória física
        
        Args:
            num_frames: Número de molduras disponíveis
        """
        self.num_frames = num_frames
        
        # Cada entrada contém o VPN que está mapeado ali, ou -1 se livre
        self.frames = [-1] * num_frames
        
        # Timestamp de último acesso
        self.last_access = [0] * num_frames
        
        # Contador global
        self.access_counter = 0
        
        # Estatísticas
        self.page_faults = 0
        self.page_replacements = 0
    
    def allocate_frame(self, vpn):
        """
        Aloca uma moldura para um VPN
        
        Args:
            vpn: Número da página virtual
            
        Returns:
            (frame_number, was_replacement)
        """
        self.access_counter += 1
        
        # Procurar moldura livre
        for i in range(self.num_frames):
            if self.frames[i] == -1:
                self.frames[i] = vpn
                self.last_access[i] = self.access_counter
                self.page_faults += 1
                return (i, False)
        
        # Memória cheia → substituir via LRU
        lru_frame = self._find_lru_frame()
        self.frames[lru_frame] = vpn
        self.last_access[lru_frame] = self.access_counter
        
        self.page_faults += 1
        self.page_replacements += 1
        
        return (lru_frame, True)
    
    def update_access(self, frame):
        """
        Atualiza o timestamp de acesso de uma moldura
        """
        self.access_counter += 1
        self.last_access[frame] = self.access_counter
    
    def _find_lru_frame(self):
        """
        Encontra a moldura menos recentemente usada
        """
        min_access = min(self.last_access)
        return self.last_access.index(min_access)
    
    def get_frame_vpn(self, frame):
        """
        Retorna o VPN armazenado em uma moldura
        """
        if 0 <= frame < self.num_frames:
            return self.frames[frame]
        return -1
    
    def free_frame(self, frame):
        """
        Libera uma moldura (para mapeamentos futuros)
        """
        if 0 <= frame < self.num_frames:
            self.frames[frame] = -1
            self.last_access[frame] = 0
    
    def is_full(self):
        return all(v != -1 for v in self.frames)
    
    def get_used_frames(self):
        return sum(1 for v in self.frames if v != -1)
    
    def get_statistics(self):
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
        Retorna (frame_index, vpn, last_access)
        """
        return [
            (i, self.frames[i], self.last_access[i])
            for i in range(self.num_frames)
        ]
    
    def __str__(self):
        lines = []
        lines.append(f"Memória Física ({self.get_used_frames()}/{self.num_frames} usadas):")
        
        for i in range(self.num_frames):
            vpn = self.frames[i]
            if vpn != -1:
                lines.append(f"  Frame {i}: VPN {vpn} (último acesso: {self.last_access[i]})")
            else:
                lines.append(f"  Frame {i}: [livre]")
        
        return "\n".join(lines)
    
    def to_dict(self):
        return {
            'frames': self.frames.copy(),
            'last_access': self.last_access.copy(),
            'statistics': self.get_statistics()
        }
