"""
Gerador de Endereços Virtuais Aleatórios
Gera sequências de endereços para teste do simulador
"""

import random


class AddressGenerator:
    """
    Gera endereços virtuais aleatórios distribuídos pelos segmentos
    """
    
    def __init__(self, config, seed=None):
        """
        Inicializa o gerador de endereços
        
        Args:
            config: Objeto MemoryConfig com a configuração do sistema
            seed: Semente para o gerador aleatório (opcional)
        """
        self.config = config
        self.boundaries = config.get_segment_boundaries()
        
        if seed is not None:
            random.seed(seed)
    
    def generate_random_address(self, segment=None):
        """
        Gera um endereço virtual aleatório
        
        Args:
            segment: Segmento específico ou None para qualquer segmento
            
        Returns:
            Endereço virtual aleatório
        """
        if segment is None:
            # Escolhe um segmento aleatoriamente
            segment = random.choice(['text', 'data', 'bss', 'stack'])
        
        start, end = self.boundaries[segment]
        return random.randint(start, end)
    
    def generate_sequence(self, num_addresses, distribution=None):
        """
        Gera uma sequência de endereços virtuais
        
        Args:
            num_addresses: Número de endereços a gerar
            distribution: Dicionário com distribuição por segmento
                         Ex: {'text': 0.4, 'data': 0.3, 'bss': 0.2, 'stack': 0.1}
                         Se None, distribui igualmente
        
        Returns:
            Lista de endereços virtuais
        """
        addresses = []
        
        if distribution is None:
            # Distribuição uniforme entre os segmentos
            distribution = {
                'text': 0.25,
                'data': 0.25,
                'bss': 0.25,
                'stack': 0.25
            }
        
        # Calcula quantos endereços por segmento
        segments = list(distribution.keys())
        probabilities = list(distribution.values())
        
        for _ in range(num_addresses):
            segment = random.choices(segments, weights=probabilities)[0]
            addr = self.generate_random_address(segment)
            addresses.append(addr)
        
        return addresses
    
    def generate_locality_sequence(self, num_addresses, locality_factor=0.7):
        """
        Gera uma sequência com localidade temporal e espacial
        
        Args:
            num_addresses: Número de endereços a gerar
            locality_factor: Fator de localidade (0.0 a 1.0)
                           Maior = mais localidade
        
        Returns:
            Lista de endereços virtuais com localidade
        """
        addresses = []
        current_page = None
        page_size = self.config.page_size
        
        for _ in range(num_addresses):
            if current_page is None or random.random() > locality_factor:
                # Muda de página
                addr = self.generate_random_address()
                current_page = (addr // page_size) * page_size
            else:
                # Permanece na mesma página
                offset = random.randint(0, page_size - 1)
                addr = current_page + offset
            
            addresses.append(addr)
        
        return addresses
    
    def generate_sequential_pattern(self, start_segment, num_addresses, stride=1):
        """
        Gera uma sequência de endereços sequenciais
        
        Args:
            start_segment: Segmento de início
            num_addresses: Número de endereços a gerar
            stride: Incremento entre endereços
        
        Returns:
            Lista de endereços virtuais sequenciais
        """
        addresses = []
        start, end = self.boundaries[start_segment]
        current = start
        
        for _ in range(num_addresses):
            if current > end:
                current = start
            addresses.append(current)
            current += stride
        
        return addresses
    
    def save_to_file(self, addresses, filename):
        """
        Salva uma sequência de endereços em arquivo
        
        Args:
            addresses: Lista de endereços
            filename: Nome do arquivo de saída
        """
        with open(filename, 'w') as f:
            for addr in addresses:
                f.write(f"{addr}\n")
    
    def load_from_file(self, filename):
        """
        Carrega uma sequência de endereços de um arquivo
        
        Args:
            filename: Nome do arquivo de entrada
            
        Returns:
            Lista de endereços virtuais
        """
        addresses = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    # Aceita decimal ou hexadecimal
                    if line.startswith('0x') or line.startswith('0X'):
                        addr = int(line, 16)
                    else:
                        addr = int(line)
                    addresses.append(addr)
        return addresses


def main():
    """Função principal para testar o gerador"""
    from config import MemoryConfig
    
    # Configuração de exemplo
    config = MemoryConfig(
        tlb_entries_bits=2,
        virtual_addr_bits=16,
        physical_addr_bits=14,
        page_size_bits=10,
        text_size_bits=12,
        data_size_bits=11,
        stack_size_bits=11,
        page_table_levels=2
    )
    
    generator = AddressGenerator(config, seed=42)
    
    # Gera diferentes tipos de sequências
    print("=== Gerando Sequências de Endereços ===\n")
    
    # 1. Sequência aleatória
    random_addrs = generator.generate_sequence(10)
    print("Sequência aleatória (10 endereços):")
    generator.save_to_file(random_addrs, "addresses_random.txt")
    print(f"Salva em: addresses_random.txt\n")
    
    # 2. Sequência com localidade
    locality_addrs = generator.generate_locality_sequence(20, locality_factor=0.8)
    print("Sequência com localidade (20 endereços):")
    generator.save_to_file(locality_addrs, "addresses_locality.txt")
    print(f"Salva em: addresses_locality.txt\n")
    
    # 3. Sequência sequencial
    sequential_addrs = generator.generate_sequential_pattern('text', 15, stride=4)
    print("Sequência sequencial no .text (15 endereços):")
    generator.save_to_file(sequential_addrs, "addresses_sequential.txt")
    print(f"Salva em: addresses_sequential.txt\n")
    
    print("Arquivos de endereços gerados com sucesso!")


if __name__ == "__main__":
    main()
