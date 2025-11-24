"""
Configuração do Simulador de Gerenciamento de Memória Paginada
"""

class MemoryConfig:
    """Classe para configurar os parâmetros do sistema de memória"""
    
    def __init__(self, 
        tlb_entries_bits=2,        # 2^2 = 4 entradas na TLB
        virtual_addr_bits=16,       # 2^16 = 64KB espaço virtual
        physical_addr_bits=14,      # 2^14 = 16KB memória física
        page_size_bits=10,          # 2^10 = 1KB páginas
        text_size_bits=12,          # 2^12 = 4KB segmento .text
        data_size_bits=11,          # 2^11 = 2KB segmento .data
        stack_size_bits=11,         # 2^11 = 2KB segmento .stack
        page_table_levels=2):       # Número de níveis da tabela de páginas
        
        # Validações
        if physical_addr_bits > virtual_addr_bits:
            raise ValueError("Memória física não pode ser maior que espaço virtual")
        
        if page_table_levels not in [1, 2, 3]:
            raise ValueError("Número de níveis da tabela deve ser 1, 2 ou 3")
        
        # Configuração da TLB
        self.tlb_entries_bits = tlb_entries_bits
        self.tlb_entries = 2 ** tlb_entries_bits
        
        # Configuração da memória
        self.virtual_addr_bits = virtual_addr_bits
        self.physical_addr_bits = physical_addr_bits
        self.page_size_bits = page_size_bits
        
        self.virtual_addr_space = 2 ** virtual_addr_bits
        self.physical_memory_size = 2 ** physical_addr_bits
        self.page_size = 2 ** page_size_bits
        
        # Número de páginas e molduras
        self.num_virtual_pages = self.virtual_addr_space // self.page_size
        self.num_frames = self.physical_memory_size // self.page_size
        
        # Bits para offset, número da página virtual e frame
        self.offset_bits = page_size_bits
        self.vpn_bits = virtual_addr_bits - page_size_bits
        self.frame_bits = physical_addr_bits - page_size_bits
        
        # Configuração dos segmentos
        self.text_size_bits = text_size_bits
        self.data_size_bits = data_size_bits
        self.stack_size_bits = stack_size_bits
        
        self.text_size = 2 ** text_size_bits
        self.data_size = 2 ** data_size_bits
        self.stack_size = 2 ** stack_size_bits
        
        # Segmento .bss calculado: tamanho total dos outros segmentos * 3
        self.bss_size = (self.text_size + self.data_size + self.stack_size) * 3
        
        # 🔥 Ajuste obrigatório do PDF:
        # O bss nunca pode ultrapassar o espaço virtual disponível.
        total_used_no_bss = self.text_size + self.data_size + self.stack_size
        remaining_space = max(0, self.virtual_addr_space - total_used_no_bss)
        self.bss_size = min(self.bss_size, remaining_space)
        
        # Configuração da tabela de páginas
        self.page_table_levels = page_table_levels
        
        # Cálculo dos bits por nível da tabela de páginas
        self._calculate_page_table_structure()
        
        # 🔥 Checagem opcional (mas segura):
        # Verifica se os segmentos não se sobrepõem
        self._validate_segment_layout()

    def _calculate_page_table_structure(self):
        """Calcula a estrutura da tabela de páginas multi-nível"""
        if self.page_table_levels == 1:
            self.bits_per_level = [self.vpn_bits]
        elif self.page_table_levels == 2:
            bits_level1 = self.vpn_bits // 2
            bits_level2 = self.vpn_bits - bits_level1
            self.bits_per_level = [bits_level1, bits_level2]
        else:  # 3 níveis
            bits_level1 = self.vpn_bits // 3
            bits_level2 = self.vpn_bits // 3
            bits_level3 = self.vpn_bits - bits_level1 - bits_level2
            self.bits_per_level = [bits_level1, bits_level2, bits_level3]
    
    def get_segment_boundaries(self):
        """Retorna os limites de cada segmento no espaço de endereços virtuais"""
        text_start = 0
        text_end = self.text_size - 1
        
        data_start = self.text_size
        data_end = data_start + self.data_size - 1
        
        bss_start = data_end + 1
        bss_end = bss_start + self.bss_size - 1
        
        # Stack cresce do topo para baixo
        stack_end = self.virtual_addr_space - 1
        stack_start = stack_end - self.stack_size + 1
        
        return {
            'text': (text_start, text_end),
            'data': (data_start, data_end),
            'bss': (bss_start, bss_end),
            'stack': (stack_start, stack_end)
        }

    def _validate_segment_layout(self):
        """Verifica se os segmentos estão dentro do espaço virtual e não se sobrepõem"""
        seg = self.get_segment_boundaries()
        
        # Verificar se .bss ultrapassou o topo da stack
        if seg['bss'][1] >= seg['stack'][0]:
            raise ValueError("Segmentos .bss e .stack estão se sobrepondo. Ajuste os tamanhos.")
        
        # Garantir que todos estão dentro do espaço virtual
        for name, (start, end) in seg.items():
            if start < 0 or end >= self.virtual_addr_space:
                raise ValueError(f"Segmento {name} está fora do espaço virtual permitido.")
    
    def __str__(self):
        """Representação em string da configuração"""
        boundaries = self.get_segment_boundaries()
        return f"""
=== Configuração do Sistema de Memória ===

TLB:
  - Entradas: {self.tlb_entries} ({self.tlb_entries_bits} bits)

Memória:
  - Espaço Virtual: {self.virtual_addr_space} bytes ({self.virtual_addr_bits} bits)
  - Memória Física: {self.physical_memory_size} bytes ({self.physical_addr_bits} bits)
  - Tamanho da Página: {self.page_size} bytes ({self.page_size_bits} bits)
  - Páginas Virtuais: {self.num_virtual_pages}
  - Molduras Físicas: {self.num_frames}

Segmentos:
  - .text:  {self.text_size} bytes [{boundaries['text'][0]:,} - {boundaries['text'][1]:,}]
  - .data:  {self.data_size} bytes [{boundaries['data'][0]:,} - {boundaries['data'][1]:,}]
  - .bss:   {self.bss_size} bytes [{boundaries['bss'][0]:,} - {boundaries['bss'][1]:,}]
  - .stack: {self.stack_size} bytes [{boundaries['stack'][0]:,} - {boundaries['stack'][1]:,}]

Tabela de Páginas:
  - Níveis: {self.page_table_levels}
  - Bits por nível: {self.bits_per_level}
"""

