"""
Arquivo de configuração do simulador de memória paginada.

Aqui ficam apenas os valores que definem o tamanho dos espaços,
quantidade de páginas, tamanho de segmentos, etc.
"""

from Colors import Colors

class MemoryConfig:
    def __init__(
        self,
        tlb_entries_bits=2,     # número de entradas da TLB = 2^n
        virtual_addr_bits=16,   # tamanho do espaço virtual
        physical_addr_bits=14,  # tamanho da memória física
        page_size_bits=10,      # tamanho da página
        text_size_bits=12,      # tamanho do .text
        data_size_bits=11,      # tamanho do .data
        stack_size_bits=11,     # tamanho do .stack
        page_table_levels=2     # níveis da tabela de páginas
    ):
        # validações simples
        if physical_addr_bits > virtual_addr_bits:
            raise ValueError("Memória física não pode ser maior que o espaço virtual.")

        if page_table_levels not in [1, 2, 3]:
            raise ValueError("A tabela de páginas deve ter 1, 2 ou 3 níveis.")

        # ------------------
        # CONFIGURAÇÃO DA TLB
        # ------------------
        self.tlb_entries_bits = tlb_entries_bits
        self.tlb_entries = 2 ** tlb_entries_bits

        # ------------------
        # CONFIGURAÇÃO DA MEMÓRIA
        # ------------------
        self.virtual_addr_bits = virtual_addr_bits
        self.physical_addr_bits = physical_addr_bits
        self.page_size_bits = page_size_bits

        self.virtual_addr_space = 2 ** virtual_addr_bits
        self.physical_memory_size = 2 ** physical_addr_bits
        self.page_size = 2 ** page_size_bits

        # cálculo de páginas/molduras
        self.num_virtual_pages = self.virtual_addr_space // self.page_size
        self.num_frames = self.physical_memory_size // self.page_size

        # separação do endereço virtual
        self.offset_bits = page_size_bits
        self.vpn_bits = virtual_addr_bits - page_size_bits

        # ------------------
        # SEGMENTOS
        # ------------------
        self.text_size = 2 ** text_size_bits
        self.data_size = 2 ** data_size_bits
        self.stack_size = 2 ** stack_size_bits

        # o .bss é calculado com base nos outros segmentos (PDF)
        # aqui escolhi somar tudo (simples)
        self.bss_size = self.text_size + self.data_size + self.stack_size

        # ------------------
        # TABELA DE PÁGINAS
        # ------------------
        self.page_table_levels = page_table_levels
        self._calc_bits_per_level()

    def _calc_bits_per_level(self):
        """Define quantos bits vão para cada nível da tabela."""
        if self.page_table_levels == 1:
            self.bits_per_level = [self.vpn_bits]
        elif self.page_table_levels == 2:
            metade = self.vpn_bits // 2
            self.bits_per_level = [metade, self.vpn_bits - metade]
        else:
            p1 = self.vpn_bits // 3
            p2 = self.vpn_bits // 3
            p3 = self.vpn_bits - p1 - p2
            self.bits_per_level = [p1, p2, p3]

    def get_segment_boundaries(self):
        """Retorna os intervalos de memória ocupados por cada segmento."""

        text_start = 0
        text_end = self.text_size - 1

        data_start = text_end + 1
        data_end = data_start + self.data_size - 1

        bss_start = data_end + 1
        bss_end = bss_start + self.bss_size - 1

        # stack cresce para baixo
        stack_end = self.virtual_addr_space - 1
        stack_start = stack_end - self.stack_size + 1

        return {
            "text": (text_start, text_end),
            "data": (data_start, data_end),
            "bss":  (bss_start, bss_end),
            "stack": (stack_start, stack_end)
        }

    def __str__(self):
        seg = self.get_segment_boundaries()

        return f"""
    {Colors.BOLD_MAGENTA}=== Configuração de Memória ==={Colors.RESET}

    {Colors.BOLD_MAGENTA}TLB:{Colors.RESET}
        Entradas: {self.tlb_entries}

    {Colors.BOLD_MAGENTA}Memória:{Colors.RESET} 
    Espaço virtual: {self.virtual_addr_space} bytes
    Memória física: {self.physical_memory_size} bytes
    Página: {self.page_size} bytes

    {Colors.BOLD_MAGENTA}Segmentos:{Colors.RESET}
    .text  = {self.text_size} bytes  ({seg['text'][0]} até {seg['text'][1]})
    .data  = {self.data_size} bytes  ({seg['data'][0]} até {seg['data'][1]})
    .bss   = {self.bss_size} bytes   ({seg['bss'][0]} até {seg['bss'][1]})
    .stack = {self.stack_size} bytes ({seg['stack'][0]} até {seg['stack'][1]})

    {Colors.BOLD_MAGENTA}Tabela de páginas:{Colors.RESET}
    Níveis: {self.page_table_levels}
    Bits por nível: {self.bits_per_level}
"""
