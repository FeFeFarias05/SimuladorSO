from TLB import TLB
from PageTableEntry import PageTableEntry
from PhysicalMemory import PhysicalMemory
from SegmentManager import SegmentManager


class AddressTranslation:
    def __init__(self, enderecoVirtual, enderecoFisico, segmento,
        vpn, frame, offset, tlbHit, pageFault):
        self.enderecoVirtual = enderecoVirtual
        self.enderecoFisico = enderecoFisico
        self.segmento = segmento
        self.vpn = vpn
        self.frame = frame
        self.offset = offset
        self.tlbHit = tlbHit
        self.pageFault = pageFault

    def __str__(self):
        origem = "TLB" if self.tlbHit else "Page Table"
        pf = " [PAGE FAULT]" if self.pageFault else ""
        return (f"Virtual: {self.enderecoVirtual:#08x} -> Physical: {self.enderecoFisico:#08x} "
                f"| Segmento: .{self.segmento} | VPN: {self.vpn} -> Frame: {self.frame} "
                f"| Offset: {self.offset} | Origem: {origem}{pf}")


class MMU:
    def __init__(self, config):
        self.config = config
        self.tlb = TLB(config.tlb_entradas)
        self.tabelaPaginas = PageTableEntry(config)
        self.memoriaFisica = PhysicalMemory(config.numFrames)
        self.gerenciadorSegmentos = SegmentManager(config)
        self.traducoes = []  

    def traduzir(self, enderecoVirtual):
        seg = self.gerenciadorSegmentos.identificarSegmento(enderecoVirtual)
        if seg is None:
            raise ValueError(f"Endereço fora dos segmentos: {enderecoVirtual:#08x}")

        offsetMask = (1 << self.config.offsetBits) - 1
        vpn = enderecoVirtual >> self.config.offsetBits
        offset = enderecoVirtual & offsetMask

        frame = self.tlb.buscarVPN(vpn)
        tlbHit = frame is not None
        pageFault = False

        if frame is None:
            frame = self.tabelaPaginas.buscar(vpn)

            if frame == -1:
                pageFault = True
                frame, vpnRemovido = self.memoriaFisica.alocarFrame(vpn)

                if vpnRemovido is not None:
                    self.tabelaPaginas.remover(vpnRemovido)
                    self.tlb.remover(vpnRemovido)

                self.tabelaPaginas.inserir(vpn, frame)
            else:
                self.memoriaFisica.atualizarAcesso(frame)

            self.tlb.inserir(vpn, frame)
        else:
            self.memoriaFisica.atualizarAcesso(frame)

        enderecoFisico = (frame << self.config.offsetBits) | offset

        traducao = AddressTranslation(
            enderecoVirtual=enderecoVirtual,
            enderecoFisico=enderecoFisico,
            segmento=seg,
            vpn=vpn,
            frame=frame,
            offset=offset,
            tlbHit=tlbHit,
            pageFault=pageFault
        )

        self.traducoes.append(traducao)
        return traducao

    def traduzirLote(self, enderecos):
        """Traduz vários endereços."""
        resultado = []
        for endereco in enderecos:
            try:
                resultado.append(self.traduzir(endereco))
            except ValueError:
                pass
        return resultado

    def getEstatisticas(self):
        """Retorna estatísticas simples da MMU."""
        total = len(self.traducoes)
        faults = sum(1 for traducao in self.traducoes if traducao.pageFault)

        return {
            "totalTraducoes": total,
            "pageFaults": faults,
            "taxaPageFault": (faults / total) if total > 0 else 0,
            "tlb": self.tlb.getEstatisticas(),
            "memoriaFisica": self.memoriaFisica.getEstatisticas()
        }
