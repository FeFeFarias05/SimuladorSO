import json
from datetime import datetime
from MemoryConfig import MemoryConfig
from mmu import MMU
from AddressGenerator import AddressGenerator

class MemorySimulator:
    """
    Simulador simples de gerenciamento de memória paginada.
    """

    def __init__(self, config):
        self.config = config
        self.mmu = MMU(config)
        self.generator = AddressGenerator(config)

    def run_simulation(self, input_file, output_file):
        """Executa a simulação e salva o resultado."""

        addresses = self.generator.load(input_file)
        results = self.mmu.translate_batch(addresses)
        self._write_output(output_file, results)

        print(f"Simulação concluída! Saída salva em: {output_file}")

    def _write_output(self, filename, translations):
        """Gera o arquivo de saída da simulação."""
        with open(filename, "w", encoding="utf-8") as f:

            f.write("SIMULADOR DE MEMÓRIA PAGINADA\n")
            f.write(f"Data: {datetime.now()}\n\n")

            # -----------------------
            # CONFIGURAÇÃO
            # -----------------------
            f.write("=== CONFIGURAÇÃO ===\n")
            f.write(str(self.config))
            f.write("\n")

            # -----------------------
            # TRADUÇÕES
            # -----------------------
            f.write("=== TRADUÇÕES ===\n")
            for i, t in enumerate(translations, start=1):
                f.write(f"{i}. {t}\n")
            f.write("\n")

            # -----------------------
            # TLB
            # -----------------------
            f.write("=== TLB ===\n")
            tlb_items = self.mmu.tlb.get_contents()

            if len(tlb_items) == 0:
                f.write("TLB vazia\n")
            else:
                for vpn, frame in tlb_items:
                    f.write(f"VPN {vpn} -> Frame {frame}\n")
            f.write("\n")

            # -----------------------
            # TABELA DE PÁGINAS
            # -----------------------
            f.write("=== TABELA DE PÁGINAS ===\n")
            mappings = self.mmu.page_table.get_all_mappings()

            if len(mappings) == 0:
                f.write("Tabela de páginas vazia\n")
            else:
                for vpn, frame in mappings:
                    f.write(f"VPN {vpn} -> Frame {frame}\n")
            f.write("\n")

            # -----------------------
            # MEMÓRIA FÍSICA
            # -----------------------
            f.write("=== MEMÓRIA FÍSICA ===\n")
            mem = self.mmu.physical_memory.get_contents()

            for frame_index, vpn, last_use in mem:
                if vpn == -1:
                    f.write(f"Frame {frame_index}: livre\n")
                else:
                    base_virtual = vpn * self.config.page_size
                    f.write(
                        f"Frame {frame_index}: VPN {vpn} "
                        f"(base virtual 0x{base_virtual:04x})\n"
                    )
            f.write("\n")

            # -----------------------
            # ESTATÍSTICAS
            # -----------------------
            stats = self.mmu.get_statistics()

            f.write("=== ESTATÍSTICAS ===\n")
            f.write(f"Total de traduções: {stats['total_translations']}\n")
            f.write(f"Page faults: {stats['page_faults']}\n")
            f.write(f"TLB hits: {stats['tlb']['hits']}\n")
            f.write(f"TLB misses: {stats['tlb']['misses']}\n")
            f.write(
                f"Molduras usadas: {stats['physical_memory']['used_frames']} "
                f"de {stats['physical_memory']['total_frames']}\n"
            )
            f.write("\n")

def create_default_simulation():
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
    return MemorySimulator(config)
