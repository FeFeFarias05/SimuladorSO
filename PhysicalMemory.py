
class PhysicalMemory:
    def __init__(self, numFrames):
        self.numFrames = numFrames

        self.frames = [-1] * numFrames

        self.ultimoAcesso = [0] * numFrames

        self.contadorAcessos = 0

        # Estatísticas
        self.pageFaults = 0
        self.page_replacements = 0

    def alocarFrame(self, vpn):
        self.contadorAcessos += 1

        for i in range(self.numFrames):
            if self.frames[i] == -1:
                self.frames[i] = vpn
                self.ultimoAcesso[i] = self.contadorAcessos
                self.pageFaults += 1
                return i, None  

        lruFrame = self.acharLRUFrame()
        evictedVpn = self.frames[lruFrame]

        self.frames[lruFrame] = vpn
        self.ultimoAcesso[lruFrame] = self.contadorAcessos

        self.pageFaults += 1
        self.page_replacements += 1

        return lruFrame, evictedVpn  

    def atualizarAcesso(self, frame):
        self.contadorAcessos += 1
        self.ultimoAcesso[frame] = self.contadorAcessos

    def acharLRUFrame(self):
        menor = min(self.ultimoAcesso)
        return self.ultimoAcesso.index(menor)

    def getFrameVpn(self, frame):
        if 0 <= frame < self.numFrames:
            return self.frames[frame]
        return -1

    def getFramesUsados(self):
        return sum(1 for v in self.frames if v != -1)

    def getEstatisticas(self):
        used = self.getFramesUsados()
        return {
            "total_frames": self.numFrames,
            "used_frames": used,
            "free_frames": self.numFrames - used,
            "pageFaults": self.pageFaults,
            "page_replacements": self.page_replacements,
            "utilization": used / self.numFrames
        }

    def getConteudo(self):
        return [(i, self.frames[i], self.ultimoAcesso[i])
                for i in range(self.numFrames)]

    def __str__(self):
        out = [f"Memória Física ({self.getFramesUsados()}/{self.numFrames} usadas):"]
        for i in range(self.numFrames):
            vpn = self.frames[i]
            if vpn == -1:
                out.append(f"  Frame {i}: [livre]")
            else:
                out.append(f"  Frame {i}: VPN {vpn} (último acesso: {self.ultimoAcesso[i]})")
        return "\n".join(out)
