"""
Tabela de páginas com suporte a 1, 2 ou 3 níveis.
Implementação simples, seguindo exatamente o que o trabalho pede.
"""

class PageTableEntry:
    def __init__(self, config):
        self.config = config
        self.niveis = config.niveisTabelaPagina
        self.bitsPorNivel = config.bitsPorNivel
        self.tabela = {}



    def splitVpn(self, vpn):
        indices = []
        for bits in reversed(self.bitsPorNivel):
            mask = (1 << bits) - 1
            indices.append(vpn & mask)
            vpn >>= bits
        return list(reversed(indices))

    def buscar(self, vpn):
        if self.niveis == 1:
            entrada = self.tabela.get(vpn)
            if entrada and entrada["valid"]:
                return entrada["frame"]
            return -1
        
        indices = self.splitVpn(vpn)
        atual = self.tabela

        for i, idx in enumerate(indices):
            if idx not in atual:
                return -1

            if i == self.niveis - 1:
                entrada = atual[idx]
                if entrada.get("valid", False):
                    return entrada["frame"]
                return -1

            atual = atual[idx].get("next", {})

        return -1


    def inserir(self, vpn, frame):
        if self.niveis == 1:
            self.tabela[vpn] = {"valid": True, "frame": frame}
            return
        
        indices = self.splitVpn(vpn)
        atual = self.tabela

        for i, idx in enumerate(indices):
            if i == self.niveis - 1:
                atual[idx] = {"valid": True, "frame": frame}
            else:
                if idx not in atual:
                    atual[idx] = {"next": {}}
                atual = atual[idx]["next"]


    def remover(self, vpn):
        if self.niveis == 1:
            if vpn in self.tabela:
                self.tabela[vpn]["valid"] = False
                self.tabela[vpn]["frame"] = -1
            return
        
        indices = self.splitVpn(vpn)
        atual = self.tabela

        for i, idx in enumerate(indices):
            if idx not in atual:
                return

            if i == self.niveis - 1:
                atual[idx]["valid"] = False
                atual[idx]["frame"] = -1
            else:
                atual = atual[idx].get("next", {})

 
    def getMapeamentos(self):
        mapeamentos = []

        if self.niveis == 1:
            for vpn, entrada in self.tabela.items():
                if entrada.get("valid", False):
                    mapeamentos.append((vpn, entrada["frame"]))
            return sorted(mapeamentos)

        def caminhar(atual, level, acc):
            bits = self.bitsPorNivel[level]
            if level == self.niveis - 1:
                for idx, node in atual.items():
                    if node.get("valid", False):
                        vpn = (acc << bits) | idx
                        mapeamentos.append((vpn, node["frame"]))
            else:
                for idx, node in atual.items():
                    nxt = node.get("next")
                    if nxt is not None:
                        caminhar(nxt, level + 1, (acc << bits) | idx)

        caminhar(self.tabela, 0, 0)
        return sorted(mapeamentos)


    def __str__(self):
        lines = [f"Tabela de Páginas ({self.niveis} níveis)"]
        mapeamentos = self.getMapeamentos()
        if not mapeamentos:
            lines.append("  [vazia]")
        else:
            for vpn, frame in mapeamentos:
                lines.append(f"  VPN {vpn} -> Frame {frame}")
        return "\n".join(lines)
