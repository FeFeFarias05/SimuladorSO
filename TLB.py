class TLB:
    def __init__(self, max_entradas):
        self.max_entradas = max_entradas
        self.entradas = []       
        self.hits = 0
        self.misses = 0

    def buscarVPN(self, vpn):
        for v, f in self.entradas:
            if v == vpn:
                self.hits += 1
                return f

        self.misses += 1
        return None

    def inserir(self, vpn, frame):
        self.entradas = [(v, f) for (v, f) in self.entradas if v != vpn]

        if len(self.entradas) >= self.max_entradas:
            self.entradas.pop(0)

        self.entradas.append((vpn, frame))

    def remover(self, vpn):
        self.entradas = [(v, f) for (v, f) in self.entradas if v != vpn]

    def getEntradasTLB(self):
        return list(self.entradas)

    def getEstatisticas(self):
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }

    def __str__(self):
        if not self.entradas:
            return "TLB: vazia"
        lines = ["TLB:"]
        for v, f in self.entradas:
            lines.append(f"  VPN {v} -> Frame {f}")
        return "\n".join(lines)
