"""
Tabela de páginas com suporte a 1, 2 ou 3 níveis.
Implementação simples, seguindo exatamente o que o trabalho pede.
"""

class PageTableEntry:
    def __init__(self, config):
        self.config = config
        self.levels = config.niveisTabelaPagina
        self.bitsPorNivel = config.bitsPorNivel

        # Estrutura inicial da tabela
        if self.levels == 1:
            # vetor simples de VPN -> frame
            self.table = {}
        else:
            # dicionário que aponta para outros níveis
            self.table = {}

    # ------------------------------------------
    # Calcula índices por nível a partir do VPN
    # ------------------------------------------
    def split_vpn(self, vpn):
        indices = []
        for bits in reversed(self.bitsPorNivel):
            mask = (1 << bits) - 1
            indices.append(vpn & mask)
            vpn >>= bits
        return list(reversed(indices))

    # ------------------------------------------
    # Buscar frame
    # ------------------------------------------
    def lookup(self, vpn):
        if self.levels == 1:
            entry = self.table.get(vpn)
            if entry and entry["valid"]:
                return entry["frame"]
            return -1
        
        # Multi-nível
        indices = self.split_vpn(vpn)
        current = self.table

        for i, idx in enumerate(indices):
            if idx not in current:
                return -1

            if i == self.levels - 1:
                entry = current[idx]
                if entry.get("valid", False):
                    return entry["frame"]
                return -1

            # avançar nível
            current = current[idx].get("next", {})

        return -1

    # ------------------------------------------
    # Inserir novo mapeamento VPN -> Frame
    # ------------------------------------------
    def inserir(self, vpn, frame):
        if self.levels == 1:
            self.table[vpn] = {"valid": True, "frame": frame}
            return
        
        indices = self.split_vpn(vpn)
        current = self.table

        for i, idx in enumerate(indices):
            if i == self.levels - 1:
                current[idx] = {"valid": True, "frame": frame}
            else:
                if idx not in current:
                    current[idx] = {"next": {}}
                current = current[idx]["next"]

    # ------------------------------------------
    # Invalidar VPN
    # ------------------------------------------
    def remover(self, vpn):
        if self.levels == 1:
            if vpn in self.table:
                self.table[vpn]["valid"] = False
                self.table[vpn]["frame"] = -1
            return
        
        indices = self.split_vpn(vpn)
        current = self.table

        for i, idx in enumerate(indices):
            if idx not in current:
                return

            if i == self.levels - 1:
                current[idx]["valid"] = False
                current[idx]["frame"] = -1
            else:
                current = current[idx].get("next", {})

    # ------------------------------------------
    # Listar todos os mapeamentos válidos
    # ------------------------------------------
    def get_all_mappings(self):
        mappings = []

        if self.levels == 1:
            for vpn, entry in self.table.items():
                if entry.get("valid", False):
                    mappings.append((vpn, entry["frame"]))
            return sorted(mappings)

        # recursão: current = dict do nível atual, level índice (0..levels-1), acc é VPN parcial
        def walk(current, level, acc):
            bits = self.bitsPorNivel[level]
            if level == self.levels - 1:
                # último nível: cada chave é índice do último nível e tem 'valid'/'frame'
                for idx, node in current.items():
                    if node.get("valid", False):
                        vpn = (acc << bits) | idx
                        mappings.append((vpn, node["frame"]))
            else:
                # nível intermediário
                for idx, node in current.items():
                    nxt = node.get("next")
                    if nxt is not None:
                        walk(nxt, level + 1, (acc << bits) | idx)

        walk(self.table, 0, 0)
        return sorted(mappings)


    def __str__(self):
        lines = [f"Tabela de Páginas ({self.levels} níveis)"]
        mappings = self.get_all_mappings()
        if not mappings:
            lines.append("  [vazia]")
        else:
            for vpn, frame in mappings:
                lines.append(f"  VPN {vpn} -> Frame {frame}")
        return "\n".join(lines)
