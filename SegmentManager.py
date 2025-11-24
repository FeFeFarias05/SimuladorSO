"""
Gerenciador simples de segmentos de memória.
Somente identifica em qual segmento um endereço virtual está.
"""

class SegmentManager:
    def __init__(self, config):
        self.boundaries = config.get_segment_boundaries()

    def identify_segment(self, addr):
        """
        Retorna o segmento (.text, .data, .bss, .stack)
        ou None se o endereço for inválido.
        """
        for seg, (start, end) in self.boundaries.items():
            if start <= addr <= end:
                return seg
        return None

    def is_valid_address(self, addr):
        return self.identify_segment(addr) is not None
