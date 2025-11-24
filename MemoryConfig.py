"""
Arquivo de configuração do simulador de memória paginada.

Aqui ficam apenas os valores que definem o tamanho dos espaços,
quantidade de páginas, tamanho de segmentos, etc.
"""

from Colors import Colors

class MemoryConfig:
    def __init__(
        self,
        numeroEntradaTLB=2,     # número de entradas da TLB = 2^n
        tamanhoEspacoVirtual=16,   # tamanho do espaço virtual
        tamanhoMemoriaFisica=14,  # tamanho da memória física
        tamanhoPagina=10,      # tamanho da página
        tamanhoSegText=12,      # tamanho do .text
        tamanhoSegData=11,      # tamanho do .data
        tamanhoSegStack=11,     # tamanho do .stack
        niveisTabelaPagina=2     # níveis da tabela de páginas
    ):
        # validações simples
        if tamanhoMemoriaFisica > tamanhoEspacoVirtual:
            raise ValueError("Memória física não pode ser maior que o espaço virtual.")

        if niveisTabelaPagina not in [1, 2, 3]:
            raise ValueError("A tabela de páginas deve ter 1, 2 ou 3 níveis.")

        # ------------------
        # CONFIGURAÇÃO DA TLB
        # ------------------
        self.numeroEntradaTLB = numeroEntradaTLB
        self.tlb_entradas = 2 ** numeroEntradaTLB

        # ------------------
        # CONFIGURAÇÃO DA MEMÓRIA
        # ------------------
        self.tamanhoEspacoVirtual = tamanhoEspacoVirtual
        self.tamanhoMemoriaFisica = tamanhoMemoriaFisica
        self.tamanhoPagina = tamanhoPagina

        self.virtual_addr_space = 2 ** tamanhoEspacoVirtual
        self.physical_memory_size = 2 ** tamanhoMemoriaFisica
        self.page_size = 2 ** tamanhoPagina

        # cálculo de páginas/molduras
        self.num_virtual_pages = self.virtual_addr_space // self.page_size
        self.num_frames = self.physical_memory_size // self.page_size

        # separação do endereço virtual
        self.offset_bits = tamanhoPagina
        self.vpn_bits = tamanhoEspacoVirtual - tamanhoPagina

        # ------------------
        # SEGMENTOS
        # ------------------
        self.tamText = 2 ** tamanhoSegText
        self.tamData = 2 ** tamanhoSegData
        self.tamStack = 2 ** tamanhoSegStack

        # o .bss é calculado com base nos outros segmentos (PDF)
        # aqui escolhi somar tudo (simples)
        self.tamBss = self.tamText + self.tamData + self.tamStack

        # ------------------
        # TABELA DE PÁGINAS
        # ------------------
        self.niveisTabelaPagina = niveisTabelaPagina
        self.calc_bits_per_level()

    def calc_bits_per_level(self):
        """Define quantos bits vão para cada nível da tabela."""
        if self.niveisTabelaPagina == 1:
            self.bits_per_level = [self.vpn_bits]
        elif self.niveisTabelaPagina == 2:
            metade = self.vpn_bits // 2
            self.bits_per_level = [metade, self.vpn_bits - metade]
        else:
            p1 = self.vpn_bits // 3
            p2 = self.vpn_bits // 3
            p3 = self.vpn_bits - p1 - p2
            self.bits_per_level = [p1, p2, p3]

    def get_segment_boundaries(self):
        """Retorna os intervalos de memória ocupados por cada segmento."""

        inicioText = 0
        finalText = self.tamText - 1

        inicioData = finalText + 1
        finalData = inicioData + self.tamData - 1

        inicioBss = finalData + 1
        finalBss = inicioBss + self.tamBss - 1

        # stack cresce para baixo
        finalStack = self.virtual_addr_space - 1
        inicioStack = finalStack - self.tamStack + 1

        return {
            "text": (inicioText, finalText),
            "data": (inicioData, finalData),
            "bss":  (inicioBss, finalBss),
            "stack": (inicioStack, finalStack)
        }

    def __str__(self):
        seg = self.get_segment_boundaries()

        return f"""
    {Colors.BOLD_MAGENTA}=== Configuração de Memória ==={Colors.RESET}

    {Colors.BOLD_MAGENTA}TLB:{Colors.RESET}
        Entradas: {self.tlb_entradas}

    {Colors.BOLD_MAGENTA}Memória:{Colors.RESET} 
    Espaço virtual: {self.virtual_addr_space} bytes
    Memória física: {self.physical_memory_size} bytes
    Página: {self.page_size} bytes

    {Colors.BOLD_MAGENTA}Segmentos:{Colors.RESET}
    .text  = {self.tamText} bytes  ({seg['text'][0]} até {seg['text'][1]})
    .data  = {self.tamData} bytes  ({seg['data'][0]} até {seg['data'][1]})
    .bss   = {self.tamBss} bytes   ({seg['bss'][0]} até {seg['bss'][1]})
    .stack = {self.tamStack} bytes ({seg['stack'][0]} até {seg['stack'][1]})

    {Colors.BOLD_MAGENTA}Tabela de páginas:{Colors.RESET}
    Níveis: {self.niveisTabelaPagina}
    Bits por nível: {self.bits_per_level}
"""
