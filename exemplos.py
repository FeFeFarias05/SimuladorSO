"""
Exemplo de uso do simulador
Demonstra como usar o simulador de diferentes formas
"""

from MemoryConfig import MemoryConfig
from MemorySimulator import MemorySimulator
from AddressGenerator import AddressGenerator


def exemplo_basico():
    """Exemplo básico de uso do simulador"""
    print("=== EXEMPLO 1: Uso Básico ===\n")
    
    # Cria configuração padrão
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
    
    print(config)
    
    # Cria simulador
    simulator = MemorySimulator(config)
    
    # Gera alguns endereços
    generator = AddressGenerator(config, seed=42)
    addresses = generator.generate_sequence(20)
    
    # Salva endereços em arquivo
    generator.save_to_file(addresses, 'exemplo_entrada.txt')
    
    # Executa simulação
    simulator.run_simulation('exemplo_entrada.txt', 'exemplo_saida.txt', verbose=True)
    
    print("\nArquivos gerados:")
    print("  - exemplo_entrada.txt (endereços de entrada)")
    print("  - exemplo_saida.txt (resultados da simulação)")


def exemplo_configuracao_personalizada():
    """Exemplo com configuração personalizada"""
    print("\n\n=== EXEMPLO 2: Configuração Personalizada ===\n")
    
    # Configuração maior com 3 níveis de tabela
    config = MemoryConfig(
        tlb_entries_bits=3,        # 8 entradas na TLB
        virtual_addr_bits=20,       # 1MB espaço virtual
        physical_addr_bits=18,      # 256KB memória física
        page_size_bits=12,          # 4KB páginas
        text_size_bits=14,          # 16KB .text
        data_size_bits=13,          # 8KB .data
        stack_size_bits=13,         # 8KB .stack
        page_table_levels=3         # 3 níveis
    )
    
    print("Configuração personalizada criada:")
    print(f"  - Espaço virtual: {config.virtual_addr_space // 1024}KB")
    print(f"  - Memória física: {config.physical_memory_size // 1024}KB")
    print(f"  - Páginas: {config.page_size // 1024}KB")
    print(f"  - TLB: {config.tlb_entries} entradas")
    print(f"  - Tabela: {config.page_table_levels} níveis")
    
    simulator = MemorySimulator(config)
    generator = AddressGenerator(config, seed=123)
    
    # Gera sequência com localidade
    addresses = generator.generate_locality_sequence(50, locality_factor=0.8)
    generator.save_to_file(addresses, 'exemplo_localidade_entrada.txt')
    
    simulator.run_simulation('exemplo_localidade_entrada.txt', 
                            'exemplo_localidade_saida.txt', 
                            verbose=False)
    
    print("\nSimulação concluída!")
    print("Arquivo de saída: exemplo_localidade_saida.txt")


def exemplo_traducao_individual():
    """Exemplo traduzindo endereços individualmente"""
    print("\n\n=== EXEMPLO 3: Traduções Individuais ===\n")
    
    config = MemoryConfig()
    simulator = MemorySimulator(config)
    
    # Endereços de exemplo em diferentes segmentos
    enderecos_teste = [
        0x0000,  # .text
        0x0400,  # .text
        0x1000,  # .data
        0x1800,  # .bss
        0xF800,  # .stack
    ]
    
    print("Traduzindo endereços individuais:\n")
    
    for addr in enderecos_teste:
        trans = simulator.mmu.translate(addr)
        print(trans)
    
    print("\nEstado da TLB:")
    print(simulator.mmu.tlb)


def exemplo_diferentes_padroes():
    """Exemplo com diferentes padrões de acesso"""
    print("\n\n=== EXEMPLO 4: Diferentes Padrões de Acesso ===\n")
    
    config = MemoryConfig()
    generator = AddressGenerator(config, seed=999)
    
    # Padrão 1: Aleatório
    random_addrs = generator.generate_sequence(30)
    generator.save_to_file(random_addrs, 'padrao_aleatorio.txt')
    print(f"✓ Gerado: padrao_aleatorio.txt (30 endereços aleatórios)")
    
    # Padrão 2: Sequencial no .text
    sequential_addrs = generator.generate_sequential_pattern('text', 25, stride=4)
    generator.save_to_file(sequential_addrs, 'padrao_sequencial.txt')
    print(f"✓ Gerado: padrao_sequencial.txt (25 endereços sequenciais)")
    
    # Padrão 3: Com localidade alta
    locality_high = generator.generate_locality_sequence(40, locality_factor=0.9)
    generator.save_to_file(locality_high, 'padrao_localidade_alta.txt')
    print(f"✓ Gerado: padrao_localidade_alta.txt (40 endereços, localidade 90%)")
    
    # Padrão 4: Com localidade baixa
    locality_low = generator.generate_locality_sequence(40, locality_factor=0.3)
    generator.save_to_file(locality_low, 'padrao_localidade_baixa.txt')
    print(f"✓ Gerado: padrao_localidade_baixa.txt (40 endereços, localidade 30%)")
    
    print("\nSimulando cada padrão...\n")
    
    padroes = [
        ('padrao_aleatorio.txt', 'resultado_aleatorio.txt'),
        ('padrao_sequencial.txt', 'resultado_sequencial.txt'),
        ('padrao_localidade_alta.txt', 'resultado_localidade_alta.txt'),
        ('padrao_localidade_baixa.txt', 'resultado_localidade_baixa.txt'),
    ]
    
    for input_file, output_file in padroes:
        simulator = MemorySimulator(config)  # Novo simulador para cada padrão
        simulator.run_simulation(input_file, output_file, verbose=False)
        stats = simulator.mmu.get_statistics()
        print(f"{input_file:30} -> TLB Hit Rate: {stats['tlb']['hit_rate']:6.2%}, "
              f"Page Faults: {stats['page_faults']:3}")


def exemplo_exportar_json():
    """Exemplo exportando estado em JSON"""
    print("\n\n=== EXEMPLO 5: Exportar Estado em JSON ===\n")
    
    config = MemoryConfig()
    simulator = MemorySimulator(config)
    generator = AddressGenerator(config)
    
    # Gera e processa alguns endereços
    addresses = generator.generate_sequence(15)
    generator.save_to_file(addresses, 'exemplo_json_entrada.txt')
    
    simulator.run_simulation('exemplo_json_entrada.txt', 
                            'exemplo_json_saida.txt', 
                            verbose=False)
    
    # Exporta estado em JSON
    simulator.export_state_json('estado_sistema.json')
    
    print("✓ Estado do sistema exportado para: estado_sistema.json")
    print("  O arquivo JSON contém:")
    print("    - Configuração completa do sistema")
    print("    - Estado da TLB")
    print("    - Conteúdo da tabela de páginas")
    print("    - Estado da memória física")
    print("    - Estatísticas detalhadas")


if __name__ == "__main__":
    print("="*70)
    print("EXEMPLOS DE USO DO SIMULADOR DE GERENCIAMENTO DE MEMÓRIA")
    print("="*70)
    
    exemplo_basico()
    exemplo_configuracao_personalizada()
    exemplo_traducao_individual()
    exemplo_diferentes_padroes()
    exemplo_exportar_json()
    
    print("\n" + "="*70)
    print("TODOS OS EXEMPLOS FORAM EXECUTADOS COM SUCESSO!")
    print("="*70)
    print("\nArquivos gerados:")
    print("  - exemplo_entrada.txt / exemplo_saida.txt")
    print("  - exemplo_localidade_entrada.txt / exemplo_localidade_saida.txt")
    print("  - padrao_*.txt / resultado_*.txt")
    print("  - exemplo_json_entrada.txt / exemplo_json_saida.txt")
    print("  - estado_sistema.json")
    print("\nVocê pode examinar esses arquivos para entender melhor o funcionamento!")
