"""
Memória Física com política LRU.
Armazena o VPN correspondente em cada moldura.
"""

class PhysicalMemory:
    def __init__(self, numFrames):
        self.numFrames = numFrames

        # Cada frame guarda o VPN que está lá dentro, ou -1 se livre
        self.frames = [-1] * numFrames

        # Tempo de último acesso (para LRU)
        self.last_access = [0] * numFrames

        # Contador global de acessos
        self.access_counter = 0

        # Estatísticas
        self.pageFaults = 0
        self.page_replacements = 0

    def allocate_frame(self, vpn):
        """
        Coloca uma página dentro de uma moldura.
        Se houver substituição LRU, devolve o VPN que saiu.
        """

        self.access_counter += 1

        # Procura moldura livre primeiro
        for i in range(self.numFrames):
            if self.frames[i] == -1:
                self.frames[i] = vpn
                self.last_access[i] = self.access_counter
                self.pageFaults += 1
                return i, None   # nenhuma página foi expulsa

        # Se chegou aqui, memória cheia → precisa substituir
        lru_frame = self.find_lru_frame()
        evicted_vpn = self.frames[lru_frame]

        self.frames[lru_frame] = vpn
        self.last_access[lru_frame] = self.access_counter

        self.pageFaults += 1
        self.page_replacements += 1

        return lru_frame, evicted_vpn   # devolve VPN expulso

    def update_access(self, frame):
        self.access_counter += 1
        self.last_access[frame] = self.access_counter

    def find_lru_frame(self):
        """Retorna o índice da moldura menos recentemente acessada."""
        menor = min(self.last_access)
        return self.last_access.index(menor)

    def get_frame_vpn(self, frame):
        if 0 <= frame < self.numFrames:
            return self.frames[frame]
        return -1

    def get_used_frames(self):
        return sum(1 for v in self.frames if v != -1)

    def getEstatisticas(self):
        used = self.get_used_frames()
        return {
            "total_frames": self.numFrames,
            "used_frames": used,
            "free_frames": self.numFrames - used,
            "pageFaults": self.pageFaults,
            "page_replacements": self.page_replacements,
            "utilization": used / self.numFrames
        }

    def get_contents(self):
        return [(i, self.frames[i], self.last_access[i])
                for i in range(self.numFrames)]

    def __str__(self):
        out = [f"Memória Física ({self.get_used_frames()}/{self.numFrames} usadas):"]
        for i in range(self.numFrames):
            vpn = self.frames[i]
            if vpn == -1:
                out.append(f"  Frame {i}: [livre]")
            else:
                out.append(f"  Frame {i}: VPN {vpn} (último acesso: {self.last_access[i]})")
        return "\n".join(out)
