class SegmentManager:
    def __init__(self, config):
        self.limites = config.getLimitesSegmentos()

    def identificarSegmento(self, endereco):
        for seg, (inicio, fim) in self.limites.items():
            if inicio <= endereco <= fim:
                return seg
        return None

    def enderecoValido(self, endereco):
        return self.identificar_segmento(endereco) is not None
