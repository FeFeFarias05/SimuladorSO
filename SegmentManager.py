
"""
Gerenciador de Segmentos de Memória
Identifica qual segmento (.text, .data, .bss, .stack) um endereço virtual pertence
"""

class SegmentManager:
    """
    Gerencia os segmentos de memória virtual
    """
    
    def __init__(self, config):
        """
        Inicializa o gerenciador de segmentos
        
        Args:
            config: Objeto MemoryConfig com a configuração do sistema
        """
        self.config = config
        self.boundaries = config.get_segment_boundaries()
    
    def identify_segment(self, virtual_address):
        """
        Identifica qual segmento um endereço virtual pertence
        
        Args:
            virtual_address: Endereço virtual a identificar
            
        Returns:
            Nome do segmento ('text', 'data', 'bss', 'stack') ou None se inválido
        """
        # Verifica cada segmento
        for segment_name, (start, end) in self.boundaries.items():
            if start <= virtual_address <= end:
                return segment_name
        
        return None
    
    def is_valid_address(self, virtual_address):
        """
        Verifica se um endereço virtual é válido (pertence a algum segmento)
        
        Args:
            virtual_address: Endereço virtual a verificar
            
        Returns:
            True se o endereço é válido
        """
        return self.identify_segment(virtual_address) is not None
    
    def get_segment_info(self, segment_name):
        """
        Retorna informações sobre um segmento
        
        Args:
            segment_name: Nome do segmento
            
        Returns:
            Tupla (start, end, size) ou None se segmento não existe
        """
        if segment_name not in self.boundaries:
            return None
        
        start, end = self.boundaries[segment_name]
        size = end - start + 1
        return (start, end, size)
    
    def get_all_segments_info(self):
        """
        Retorna informações sobre todos os segmentos
        
        Returns:
            Dicionário com informações de cada segmento
        """
        info = {}
        for segment_name in ['text', 'data', 'bss', 'stack']:
            start, end, size = self.get_segment_info(segment_name)
            info[segment_name] = {
                'start': start,
                'end': end,
                'size': size
            }
        return info
    
    def __str__(self):
        """Representação em string do gerenciador de segmentos"""
        result = ["Segmentos de Memória:"]
        
        for segment_name in ['text', 'data', 'bss', 'stack']:
            start, end, size = self.get_segment_info(segment_name)
            result.append(f"  .{segment_name}: [{start:#08x} - {end:#08x}] ({size} bytes)")
        
        return "\n".join(result)
    
    def format_address_info(self, virtual_address):
        """
        Formata informações sobre um endereço virtual
        
        Args:
            virtual_address: Endereço virtual
            
        Returns:
            String formatada com informações do endereço
        """
        segment = self.identify_segment(virtual_address)
        if segment is None:
            return f"Endereço {virtual_address:#08x}: INVÁLIDO"
        
        start, end, size = self.get_segment_info(segment)
        offset = virtual_address - start
        
        return f"Endereço {virtual_address:#08x}: .{segment} (offset {offset} dentro do segmento)"
