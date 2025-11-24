"""
Implementação simples de uma TLB (Translation Lookaside Buffer).
Segue o enunciado: FIFO, hits/misses e armazenamento de VPN -> frame.
"""

class TLB:
    def __init__(self, max_entries):
        self.max_entries = max_entries
        self.entries = []          # lista de (vpn, frame)
        self.hits = 0
        self.misses = 0

    def lookup(self, vpn):
        """
        Procura o VPN na TLB.
        Retorna o frame ou None.
        """
        for v, f in self.entries:
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
        self.entries = [(v, f) for (v, f) in self.entries if v != vpn]

        # substituir via FIFO
        if len(self.entries) >= self.max_entries:
            self.entries.pop(0)

        self.entries.append((vpn, frame))

    def invalidate(self, vpn):
        """Remove VPN da TLB (se existir)."""
        self.entries = [(v, f) for (v, f) in self.entries if v != vpn]

    def get_contents(self):
        return list(self.entries)

    def get_statistics(self):
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }

    def __str__(self):
        if not self.entries:
            return "TLB: vazia"
        lines = ["TLB:"]
        for v, f in self.entries:
            lines.append(f"  VPN {v} -> Frame {f}")
        return "\n".join(lines)
