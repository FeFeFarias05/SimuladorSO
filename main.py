#!/usr/bin/env python3
"""
Arquivo Principal do Simulador de Gerenciamento de Memória Paginada
Ponto de entrada do programa
"""

import argparse
import sys
from MemoryConfig import MemoryConfig
from MemorySimulator import MemorySimulator
from AddressGenerator import AddressGenerator


def parse_arguments():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='Simulador de Sistema de Gerenciamento de Memória Paginada',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  1. Executar simulação com arquivo de entrada:
     python main.py -i enderecos.txt -o resultado.txt

  2. Gerar endereços aleatórios e executar simulação:
     python main.py -g 100 -o resultado.txt

  3. Usar configuração personalizada:
     python main.py -i entrada.txt -o saida.txt --virtual-bits 18 --physical-bits 16

  4. Apenas gerar arquivo de endereços:
     python main.py --generate-only -g 50 --output-addresses enderecos.txt
        """
    )
    
    # Modo de operação
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('-i', '--input', 
                           help='Arquivo de entrada com endereços virtuais')
    mode_group.add_argument('-g', '--generate', type=int, metavar='N',
                           help='Gerar N endereços aleatórios')
    
    # Arquivo de saída
    parser.add_argument('-o', '--output', default='output.txt',
                       help='Arquivo de saída com resultados (padrão: output.txt)')
    
    # Geração de endereços
    parser.add_argument('--generate-only', action='store_true',
                       help='Apenas gerar endereços sem executar simulação')
    parser.add_argument('--output-addresses', default='addresses.txt',
                       help='Arquivo para salvar endereços gerados (padrão: addresses.txt)')
    parser.add_argument('--locality', type=float, default=0.0, metavar='F',
                       help='Fator de localidade (0.0-1.0) para geração de endereços')
    parser.add_argument('--seed', type=int,
                       help='Semente para geração aleatória')
    
    # Configuração da TLB
    parser.add_argument('--tlb-bits', type=int, default=2,
                       help='Bits para número de entradas na TLB (padrão: 2 -> 4 entradas)')
    
    # Configuração da memória
    parser.add_argument('--virtual-bits', type=int, default=16,
                       help='Bits para espaço de endereços virtuais (padrão: 16 -> 64KB)')
    parser.add_argument('--physical-bits', type=int, default=14,
                       help='Bits para memória física (padrão: 14 -> 16KB)')
    parser.add_argument('--page-bits', type=int, default=10,
                       help='Bits para tamanho da página (padrão: 10 -> 1KB)')
    
    # Configuração dos segmentos
    parser.add_argument('--text-bits', type=int, default=12,
                       help='Bits para segmento .text (padrão: 12 -> 4KB)')
    parser.add_argument('--data-bits', type=int, default=11,
                       help='Bits para segmento .data (padrão: 11 -> 2KB)')
    parser.add_argument('--stack-bits', type=int, default=11,
                       help='Bits para segmento .stack (padrão: 11 -> 2KB)')
    
    # Configuração da tabela de páginas
    parser.add_argument('--page-table-levels', type=int, default=2, choices=[1, 2, 3],
                       help='Número de níveis da tabela de páginas (padrão: 2)')
    
    # Outras opções
    parser.add_argument('--json', metavar='FILE',
                       help='Exportar estado final em JSON para FILE')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Modo silencioso (não imprime no console)')
    parser.add_argument('--show-config', action='store_true',
                       help='Mostrar configuração e sair')
    
    return parser.parse_args()


def main():
    """Função principal"""
    args = parse_arguments()
    
    try:
        # Cria configuração
        config = MemoryConfig(
            tlb_entries_bits=args.tlb_bits,
            virtual_addr_bits=args.virtual_bits,
            physical_addr_bits=args.physical_bits,
            page_size_bits=args.page_bits,
            text_size_bits=args.text_bits,
            data_size_bits=args.data_bits,
            stack_size_bits=args.stack_bits,
            page_table_levels=args.page_table_levels
        )
        
        # Apenas mostrar configuração
        if args.show_config:
            print(config)
            return 0
        
        # Cria simulador
        simulator = MemorySimulator(config)
        verbose = not args.quiet
        
        # Determina arquivo de entrada
        input_file = args.input
        
        # Gera endereços se necessário
        if args.generate:
            if verbose:
                print(f"Gerando {args.generate} endereços...")
            
            if args.locality > 0:
                addresses = simulator.address_generator.generate_locality_sequence(
                    args.generate, args.locality
                )
            else:
                addresses = simulator.address_generator.generate_sequence(args.generate)
            
            simulator.address_generator.save_to_file(addresses, args.output_addresses)
            
            if verbose:
                print(f"Endereços salvos em: {args.output_addresses}")
            
            # Se apenas gerar endereços, termina aqui
            if args.generate_only:
                return 0
            
            input_file = args.output_addresses
        
        # Executa simulação
        if verbose:
            print()
        
        simulator.run_simulation(input_file, args.output, verbose=verbose)
        
        # Exporta JSON se solicitado
        if args.json:
            simulator.export_state_json(args.json)
        
        return 0
        
    except ValueError as e:
        print(f"Erro de configuração: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Erro inesperado: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
