"""
Memory Management Unit (MMU)
Responsável pela tradução de endereços virtuais para físicos
"""

from tlb import TLB
from page_table import PageTable
from physical_memory import PhysicalMemory
from segment_manager import SegmentManager


class AddressTranslation:
    """Resultado de uma tradução de endereço"""
    
    def __init__(self, virtual_addr, physical_addr, segment, vpn, frame, offset, 
                 tlb_hit, page_fault):
        self.virtual_addr = virtual_addr
        self.physical_addr = physical_addr
        self.segment = segment
        self.vpn = vpn
        self.frame = frame
        self.offset = offset
        self.tlb_hit = tlb_hit
        self.page_fault = page_fault
    
    def __str__(self):
        source = "TLB" if self.tlb_hit else "Page Table"
        fault = " [PAGE FAULT]" if self.page_fault else ""
        return (f"Virtual: {self.virtual_addr:#08x} -> Physical: {self.physical_addr:#08x} "
                f"| Segment: .{self.segment} | VPN: {self.vpn} -> Frame: {self.frame} "
                f"| Offset: {self.offset} | Source: {source}{fault}")


class MMU:
    """
    Memory Management Unit
    Coordena TLB, Tabela de Páginas e Memória Física para tradução de endereços
    """
    
    def __init__(self, config):
        """
        Inicializa a MMU
        
        Args:
            config: Objeto MemoryConfig com a configuração do sistema
        """
        self.config = config
        # TLB: passa número de entradas
        self.tlb = TLB(config.tlb_entries)
        self.page_table = PageTable(config)
        # PhysicalMemory agora deve suportar retorno do vpn evicto (ou None)
        self.physical_memory = PhysicalMemory(config.num_frames)
        self.segment_manager = SegmentManager(config)
        
        # Histórico de traduções
        self.translation_history = []
    
    def translate(self, virtual_address):
        """
        Traduz um endereço virtual para físico
        
        Args:
            virtual_address: Endereço virtual a traduzir
            
        Returns:
            Objeto AddressTranslation com resultado da tradução
        """
        # Verifica se o endereço é válido (pertence a algum segmento)
        segment = self.segment_manager.identify_segment(virtual_address)
        if segment is None:
            raise ValueError(f"Endereço virtual inválido: {virtual_address:#08x}")
        
        # Extrai VPN e offset do endereço virtual
        vpn = virtual_address >> self.config.offset_bits
        offset = virtual_address & ((1 << self.config.offset_bits) - 1)
        
        # Variáveis para rastrear o processo
        tlb_hit = False
        page_fault = False
        frame = None
        
        # 1. Tenta buscar na TLB
        frame = self.tlb.lookup(vpn)
        
        if frame is not None:
            # TLB hit!
            tlb_hit = True
            # Atualiza acesso na memória física
            self.physical_memory.update_access(frame)
        else:
            # TLB miss - consulta tabela de páginas
            frame = self.page_table.lookup(vpn)
            
            if frame == -1:
                # Page fault - precisa alocar nova moldura
                page_fault = True
                # IMPORTANT: passamos o VPN (não o endereço virtual)
                # Agora allocate_frame retorna (frame_index, evicted_vpn_or_None)
                frame, evicted_vpn = self.physical_memory.allocate_frame(vpn)
                
                # Se houve substituição, precisamos invalidar mapeamentos antigos
                if evicted_vpn is not None:
                    # Invalidar na page table e na TLB a entrada do VPN evicto
                    # (pode ser que o evicted_vpn já não esteja mapeado na page table, mas invalidate é idempotente)
                    self.page_table.invalidate(evicted_vpn)
                    try:
                        # alguns TLBs têm método invalidate; assumimos que existe
                        self.tlb.invalidate(evicted_vpn)
                    except AttributeError:
                        # se a TLB usar outra API, adapta aqui (por enquanto ignoramos)
                        pass
                
                # Atualiza tabela de páginas com o novo mapeamento vpn -> frame
                self.page_table.insert(vpn, frame)
            else:
                # Página já estava mapeada; atualiza LRU na memória física
                self.physical_memory.update_access(frame)
            
            # Adiciona tradução na TLB
            self.tlb.insert(vpn, frame)
        
        # Calcula endereço físico
        physical_address = (frame << self.config.offset_bits) | offset
        
        # Cria objeto de tradução
        translation = AddressTranslation(
            virtual_addr=virtual_address,
            physical_addr=physical_address,
            segment=segment,
            vpn=vpn,
            frame=frame,
            offset=offset,
            tlb_hit=tlb_hit,
            page_fault=page_fault
        )
        
        # Adiciona ao histórico
        self.translation_history.append(translation)
        
        return translation
    
    def translate_batch(self, virtual_addresses):
        """
        Traduz múltiplos endereços virtuais
        
        Args:
            virtual_addresses: Lista de endereços virtuais
            
        Returns:
            Lista de objetos AddressTranslation
        """
        translations = []
        for addr in virtual_addresses:
            try:
                translation = self.translate(addr)
                translations.append(translation)
            except ValueError as e:
                print(f"Erro: {e}")
        
        return translations
    
    def get_statistics(self):
        """
        Retorna estatísticas consolidadas da MMU
        
        Returns:
            Dicionário com estatísticas de todos os componentes
        """
        total_translations = len(self.translation_history)
        page_faults = sum(1 for t in self.translation_history if t.page_fault)
        
        return {
            'total_translations': total_translations,
            'page_faults': page_faults,
            'page_fault_rate': page_faults / total_translations if total_translations > 0 else 0,
            'tlb': self.tlb.get_statistics(),
            'physical_memory': self.physical_memory.get_statistics()
        }
    
    def get_state(self):
        """
        Retorna o estado atual de todos os componentes
        
        Returns:
            Dicionário com o estado da MMU
        """
        return {
            'tlb': self.tlb.to_dict(),
            'page_table': self.page_table.to_dict(),
            'physical_memory': self.physical_memory.to_dict(),
            'statistics': self.get_statistics()
        }
    
    def __str__(self):
        """Representação em string da MMU"""
        stats = self.get_statistics()
        result = [
            "=== Estado da MMU ===",
            "",
            str(self.tlb),
            "",
            str(self.page_table),
            "",
            str(self.physical_memory),
            "",
            "=== Estatísticas ===",
            f"Total de traduções: {stats['total_translations']}",
            f"Page faults: {stats['page_faults']} ({stats['page_fault_rate']:.2%})",
            f"TLB hits: {stats['tlb']['hits']} ({stats['tlb']['hit_rate']:.2%})",
            f"TLB misses: {stats['tlb']['misses']}",
        ]
        return "\n".join(result)
