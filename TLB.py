"""
Implementação simples de uma TLB (Translation Lookaside Buffer).
Segue o enunciado: FIFO, hits/misses e armazenamento de VPN -> frame.
"""

class TLB:
    def __init__(self, max_entradas):
        self.max_entradas = max_entradas
        self.entradas = []          # lista de (vpn, frame)
        self.hits = 0
        self.misses = 0

    def lookup(self, vpn):
        """
        Procura o VPN na TLB.
        Retorna o frame ou None.
        """
        for v, f in self.entradas:
            if v == vpn:
                self.hits += 1
                return f

        self.misses += 1
        return None

    def insert(self, vpn, frame):
        """
        Insere uma nova tradução.
        Se já existe, atualiza posição.
        Se está cheia, remove o mais antigo (FIFO).
        """
        # remover caso já exista
        self.entradas = [(v, f) for (v, f) in self.entradas if v != vpn]

        # substituir via FIFO
        if len(self.entradas) >= self.max_entradas:
            self.entradas.pop(0)

        self.entradas.append((vpn, frame))

    def invalidate(self, vpn):
        """Remove VPN da TLB (se existir)."""
        self.entradas = [(v, f) for (v, f) in self.entradas if v != vpn]

    def get_contents(self):
        return list(self.entradas)

    def get_statistics(self):
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
