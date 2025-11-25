from Colors import Colors

class MemoryConfig:
    def __init__( self, numeroEntradaTLB=2,
    tamanhoEspacoVirtual=16,
    bitsMemoriaFisica=14,
    tamanhoPagina=10, 
    tamanhoSegText=12, 
    tamanhoSegData=11, 
    tamanhoSegStack=11, 
    niveisTabelaPagina=2
    ): 
        if bitsMemoriaFisica > tamanhoEspacoVirtual: 
            raise ValueError("Memória física não pode ser maior que o espaço virtual") 
        if niveisTabelaPagina not in [1, 2, 3]: 
            raise ValueError("A tabela de páginas deve ter 1, 2 ou 3 níveis.")
         
        self.numeroEntradaTLB = numeroEntradaTLB 
        self.tlb_entradas = 2 ** numeroEntradaTLB 
        self.tamanhoEspacoVirtual = tamanhoEspacoVirtual
        self.bitsMemoriaFisica = bitsMemoriaFisica 
        self.tamanhoPagina = tamanhoPagina 
        self.tamEspacoEnderecamentoVirtual = 2 ** tamanhoEspacoVirtual 
        self.tamanhoMemoriaFisica = 2 ** bitsMemoriaFisica 
        self.tamPagina = 2 ** tamanhoPagina 
        self.numPaginasVirtuais = self.tamEspacoEnderecamentoVirtual // self.tamPagina 
        self.numFrames = self.tamanhoMemoriaFisica // self.tamPagina 
        self.offsetBits = tamanhoPagina 
        self.vpnBits = tamanhoEspacoVirtual - tamanhoPagina 
        self.tamText = 2 ** tamanhoSegText 
        self.tamData = 2 ** tamanhoSegData 
        self.tamStack = 2 ** tamanhoSegStack 
        self.tamBss = self.tamText + self.tamData + self.tamStack
        self.niveisTabelaPagina = niveisTabelaPagina 
        self.calcularBitsPorNivel()

    def calcularBitsPorNivel(self):
        if self.niveisTabelaPagina == 1:
            self.bitsPorNivel = [self.vpnBits]
        elif self.niveisTabelaPagina == 2:
            metade = self.vpnBits // 2
            self.bitsPorNivel = [metade, self.vpnBits - metade]
        else:
            p1 = self.vpnBits // 3
            p2 = self.vpnBits // 3
            p3 = self.vpnBits - p1 - p2
            self.bitsPorNivel = [p1, p2, p3]

    def getLimitesSegmentos(self):
        inicioText = 0
        finalText = self.tamText - 1
        inicioData = finalText + 1
        finalData = inicioData + self.tamData - 1
        inicioBss = finalData + 1
        finalBss = inicioBss + self.tamBss - 1
        finalStack = self.tamEspacoEnderecamentoVirtual - 1
        inicioStack = finalStack - self.tamStack + 1

        return {
            "text": (inicioText, finalText),
            "data": (inicioData, finalData),
            "bss":  (inicioBss, finalBss),
            "stack": (inicioStack, finalStack)
        }

    def __str__(self):
        seg = self.getLimitesSegmentos()

        return f"""
    === Configuração de Memória ===

    TLB:
        Entradas: {self.tlb_entradas}

    Memória: 
    Espaço virtual: {self.tamEspacoEnderecamentoVirtual} bytes
    Memória física: {self.tamanhoMemoriaFisica} bytes
    Página: {self.tamPagina} bytes

    Segmentos:
    .text  = {self.tamText} bytes  ({seg['text'][0]} até {seg['text'][1]})
    .data  = {self.tamData} bytes  ({seg['data'][0]} até {seg['data'][1]})
    .bss   = {self.tamBss} bytes   ({seg['bss'][0]} até {seg['bss'][1]})
    .stack = {self.tamStack} bytes ({seg['stack'][0]} até {seg['stack'][1]})

    Tabela de páginas:
    Níveis: {self.niveisTabelaPagina}
    Bits por nível: {self.bitsPorNivel}
"""
