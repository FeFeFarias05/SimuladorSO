"""
 - lê um arquivo de endereços virtuais
 - executa o simulador
 - salva os resultados em um arquivo de saída
"""

from MemoryConfig import MemoryConfig
from MemorySimulator import MemorySimulator
from Colors import Colors

def main():
    print(f"{Colors.BOLD_BLUE}=== Simulador de um Sistema de Gerência de Memória Paginada do SO ==={Colors.RESET}")

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

    print(f"{Colors.BOLD_GREEN}Configuração carregada.{Colors.RESET}\n")
    print(config)

    input_file = input("Arquivo com endereços virtuais: ").strip()
    output_file = input("Arquivo de saída: ").strip()

    sim = MemorySimulator(config)

    try:
        sim.run_simulation(input_file, output_file)
        print("\nSimulação concluída!")
        print(f"Resultados salvos em: {output_file}")
    except FileNotFoundError:
        print("Erro: arquivo de entrada não encontrado.")
    except ValueError as e:
        print(f"Erro de configuração: {e}")

if __name__ == "__main__":
    main()
