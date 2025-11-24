"""
MMU - Memory Management Unit
Faz a tradução de endereços virtuais para endereços físicos.
"""

from TLB import TLB
from PageTableEntry import PageTableEntry
from PhysicalMemory import PhysicalMemory
from SegmentManager import SegmentManager


class AddressTranslation:
    """Armazena as informações de uma tradução feita pela MMU."""

    def __init__(self, virtual_addr, physical_addr, segment,
        vpn, frame, offset, tlb_hit, page_fault):
        self.virtual_addr = virtual_addr
        self.physical_addr = physical_addr
        self.segment = segment
        self.vpn = vpn
        self.frame = frame
        self.offset = offset
        self.tlb_hit = tlb_hit
        self.page_fault = page_fault

    def __str__(self):
        origem = "TLB" if self.tlb_hit else "Page Table"
        pf = " [PAGE FAULT]" if self.page_fault else ""
        return (f"Virtual: {self.virtual_addr:#08x} -> Physical: {self.physical_addr:#08x} "
                f"| Segmento: .{self.segment} | VPN: {self.vpn} -> Frame: {self.frame} "
                f"| Offset: {self.offset} | Origem: {origem}{pf}")


class MMU:
    """MMU que coordena TLB, tabela de páginas e memória física."""

    def __init__(self, config):
        self.config = config
        self.tlb = TLB(config.tlb_entries)
        self.page_table = PageTableEntry(config)
        self.physical_memory = PhysicalMemory(config.num_frames)
        self.segment_mgr = SegmentManager(config)
        self.translations = []   # simples lista de histórico

    def translate(self, virtual_address):
        """Executa a tradução de um único endereço."""

        # Verifica segmento
        seg = self.segment_mgr.identify_segment(virtual_address)
        if seg is None:
            raise ValueError(f"Endereço fora dos segmentos: {virtual_address:#08x}")

        # Calcula VPN e offset
        offset_mask = (1 << self.config.offset_bits) - 1
        vpn = virtual_address >> self.config.offset_bits
        offset = virtual_address & offset_mask

        # Passo 1: TLB
        frame = self.tlb.lookup(vpn)
        tlb_hit = frame is not None
        page_fault = False

        if frame is None:
            # Passo 2: Tabela de páginas
            frame = self.page_table.lookup(vpn)

            if frame == -1:
                # Page fault: precisa alocar uma moldura
                page_fault = True
                frame, evicted_vpn = self.physical_memory.allocate_frame(vpn)

                # Se substituiu página, remove mapeamentos antigos
                if evicted_vpn is not None:
                    self.page_table.invalidate(evicted_vpn)
                    self.tlb.invalidate(evicted_vpn)

                # Cria mapeamento novo
                self.page_table.insert(vpn, frame)
            else:
                self.physical_memory.update_access(frame)

            # Atualiza TLB
            self.tlb.insert(vpn, frame)
        else:
            # TLB hit → atualiza LRU na memória
            self.physical_memory.update_access(frame)

        # Endereço físico
        physical_addr = (frame << self.config.offset_bits) | offset

        # Monta resultado
        t = AddressTranslation(
            virtual_addr=virtual_address,
            physical_addr=physical_addr,
            segment=seg,
            vpn=vpn,
            frame=frame,
            offset=offset,
            tlb_hit=tlb_hit,
            page_fault=page_fault
        )

        self.translations.append(t)
        return t

    def translate_batch(self, addrs):
        """Traduz vários endereços."""
        result = []
        for a in addrs:
            try:
                result.append(self.translate(a))
            except ValueError:
                # Se o endereço for inválido, apenas ignora
                pass
        return result

    def get_statistics(self):
        """Retorna estatísticas simples da MMU."""
        total = len(self.translations)
        faults = sum(1 for t in self.translations if t.page_fault)

        return {
            "total_translations": total,
            "page_faults": faults,
            "page_fault_rate": (faults / total) if total > 0 else 0,
            "tlb": self.tlb.get_statistics(),
            "physical_memory": self.physical_memory.get_statistics()
        }
