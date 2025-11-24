
import json
from datetime import datetime
from MemoryConfig import MemoryConfig
from mmu import MMU
from AddressGenerator import AddressGenerator


class MemorySimulator:
    def __init__(self, config):

        self.config = config
        self.mmu = MMU(config)
        self.address_generator = AddressGenerator(config)
    
    def run_simulation(self, input_file, output_file, verbose=True):
        """
        Executa a simulação completa
        
        Args:
            input_file: Arquivo com endereços virtuais de entrada
            output_file: Arquivo para salvar os resultados
            verbose: Se True, imprime progresso no console
        """
        if verbose:
            print("=== Iniciando Simulação ===\n")
            print(self.config)
        
        # Carrega endereços de entrada
        addresses = self.address_generator.load_from_file(input_file)
        
        if verbose:
            print(f"\nEndereços carregados: {len(addresses)}")
            print(f"Arquivo de entrada: {input_file}")
            print(f"Arquivo de saída: {output_file}\n")
            print("Processando traduções...\n")
        
        # Executa traduções
        translations = self.mmu.translate_batch(addresses)
        
        # Gera saída
        self._generate_output(translations, output_file, verbose)
        
        if verbose:
            print(f"\n=== Simulação Concluída ===")
            print(f"Resultados salvos em: {output_file}")
            self._print_summary()
    
    def _generate_output(self, translations, output_file, verbose):
        """
        Gera o arquivo de saída com os resultados
        
        Args:
            translations: Lista de objetos AddressTranslation
            output_file: Nome do arquivo de saída
            verbose: Se True, imprime informações
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("="*80 + "\n")
            f.write("SIMULADOR DE GERENCIAMENTO DE MEMÓRIA PAGINADA\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Configuração
            f.write("CONFIGURAÇÃO DO SISTEMA\n")
            f.write("-"*80 + "\n")
            f.write(str(self.config))
            f.write("\n")
            
            # Traduções
            f.write("\n" + "="*80 + "\n")
            f.write("TRADUÇÕES DE ENDEREÇOS\n")
            f.write("="*80 + "\n\n")
            
            for i, trans in enumerate(translations, 1):
                f.write(f"[{i}] {trans}\n")
                if verbose and i % 10 == 0:
                    print(f"  Processado: {i}/{len(translations)} endereços")
            
            # Estado da TLB
            f.write("\n" + "="*80 + "\n")
            f.write("CONTEÚDO DA TLB\n")
            f.write("="*80 + "\n\n")
            tlb_contents = self.mmu.tlb.get_contents()
            if tlb_contents:
                for vpn, frame in tlb_contents:
                    f.write(f"VPN {vpn:>5} -> Frame {frame:>5}\n")
            else:
                f.write("[TLB vazia]\n")
            
            # Estado da Tabela de Páginas
            f.write("\n" + "="*80 + "\n")
            f.write("CONTEÚDO DA TABELA DE PÁGINAS\n")
            f.write("="*80 + "\n\n")
            f.write(f"Níveis: {self.config.page_table_levels}\n")
            f.write(f"Bits por nível: {self.config.bits_per_level}\n\n")
            
            page_mappings = self.mmu.page_table.get_all_mappings()
            if page_mappings:
                for vpn, frame in page_mappings:
                    f.write(f"VPN {vpn:>5} -> Frame {frame:>5}\n")
            else:
                f.write("[Tabela de páginas vazia]\n")
            
            # Estado da Memória Física
            f.write("\n" + "="*80 + "\n")
            f.write("CONTEÚDO DA MEMÓRIA FÍSICA\n")
            f.write("="*80 + "\n\n")
            
            memory_contents = self.mmu.physical_memory.get_contents()
            for frame_num, addr, last_access in memory_contents:
                if addr != -1:
                    f.write(f"Frame {frame_num:>5}: Endereço Virtual {addr:#08x} "
                           f"(Último acesso: {last_access})\n")
                else:
                    f.write(f"Frame {frame_num:>5}: [livre]\n")
            
            # Estatísticas
            f.write("\n" + "="*80 + "\n")
            f.write("ESTATÍSTICAS\n")
            f.write("="*80 + "\n\n")
            
            stats = self.mmu.get_statistics()
            f.write(f"Total de traduções:        {stats['total_translations']}\n")
            f.write(f"Page Faults:               {stats['page_faults']} "
                   f"({stats['page_fault_rate']:.2%})\n")
            f.write(f"\nTLB:\n")
            f.write(f"  Hits:                    {stats['tlb']['hits']} "
                   f"({stats['tlb']['hit_rate']:.2%})\n")
            f.write(f"  Misses:                  {stats['tlb']['misses']}\n")
            f.write(f"  Entradas atuais:         {stats['tlb']['current_entries']}"
                   f"/{stats['tlb']['max_entries']}\n")
            f.write(f"\nMemória Física:\n")
            f.write(f"  Molduras totais:         {stats['physical_memory']['total_frames']}\n")
            f.write(f"  Molduras em uso:         {stats['physical_memory']['used_frames']}\n")
            f.write(f"  Molduras livres:         {stats['physical_memory']['free_frames']}\n")
            f.write(f"  Utilização:              "
                   f"{stats['physical_memory']['utilization']:.2%}\n")
            f.write(f"  Substituições de página: "
                   f"{stats['physical_memory']['page_replacements']}\n")
            
            f.write("\n" + "="*80 + "\n")
    
    def _print_summary(self):
        """Imprime um resumo das estatísticas"""
        stats = self.mmu.get_statistics()
        
        print("\n" + "="*60)
        print("RESUMO DAS ESTATÍSTICAS")
        print("="*60)
        print(f"Total de traduções:         {stats['total_translations']}")
        print(f"Page Faults:                {stats['page_faults']} "
              f"({stats['page_fault_rate']:.2%})")
        print(f"TLB Hit Rate:               {stats['tlb']['hit_rate']:.2%}")
        print(f"Utilização da memória:      "
              f"{stats['physical_memory']['utilization']:.2%}")
        print(f"Substituições de página:    "
              f"{stats['physical_memory']['page_replacements']}")
        print("="*60)
    
    def export_state_json(self, filename):
        """
        Exporta o estado completo do sistema em JSON
        
        Args:
            filename: Nome do arquivo JSON de saída
        """
        state = {
            'config': {
                'tlb_entries': self.config.tlb_entries,
                'virtual_addr_space': self.config.virtual_addr_space,
                'physical_memory_size': self.config.physical_memory_size,
                'page_size': self.config.page_size,
                'page_table_levels': self.config.page_table_levels,
                'segments': self.config.get_segment_boundaries()
            },
            'mmu_state': self.mmu.get_state(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"Estado exportado para: {filename}")


def create_default_simulation():
    """
    Cria uma simulação com configuração padrão
    
    Returns:
        Objeto MemorySimulator configurado
    """
    config = MemoryConfig(
        tlb_entries_bits=2,        # 4 entradas na TLB
        virtual_addr_bits=16,       # 64KB espaço virtual
        physical_addr_bits=14,      # 16KB memória física
        page_size_bits=10,          # 1KB páginas
        text_size_bits=12,          # 4KB .text
        data_size_bits=11,          # 2KB .data
        stack_size_bits=11,         # 2KB .stack
        page_table_levels=2         # Tabela de 2 níveis
    )
    
    return MemorySimulator(config)
