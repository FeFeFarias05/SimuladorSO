import json
from datetime import datetime
from MemoryConfig import MemoryConfig
from MMU import MMU
from AddressLoader import AddressLoader

class MemorySimulator:
    def __init__(self, config):
        self.config = config
        self.MMU = MMU(config)
        self.generator = AddressLoader(config)

    def run_simulation(self, input_file, output_file):
        enderecos = self.generator.carregar(input_file)
        resultados = self.MMU.translate_batch(enderecos)
        self.write_output(output_file, resultados)

        print(f"Simulação concluída! Saída salva em: {output_file}")

    def write_output(self, nomeArquivo, traducoes):
        with open(nomeArquivo, "w", encoding="utf-8") as f:

            f.write("SIMULADOR DE MEMÓRIA PAGINADA\n")
            f.write(f"Data: {datetime.now()}\n\n")

            f.write("=== CONFIGURAÇÃO ===\n")
            f.write(str(self.config))
            f.write("\n")

            f.write("=== TRADUÇÕES ===\n")
            for i, t in enumerate(traducoes, start=1):
                f.write(f"{i}. {t}\n")
            f.write("\n")

            f.write("=== TLB ===\n")
            tlb_items = self.MMU.tlb.getEntradasTLB()

            if len(tlb_items) == 0:
                f.write("TLB vazia\n")
            else:
                for vpn, frame in tlb_items:
                    f.write(f"VPN {vpn} -> Frame {frame}\n")
            f.write("\n")

            f.write("=== TABELA DE PÁGINAS ===\n")
            mappings = self.MMU.page_table.get_all_mappings()

            if len(mappings) == 0:
                f.write("Tabela de páginas vazia\n")
            else:
                for vpn, frame in mappings:
                    f.write(f"VPN {vpn} -> Frame {frame}\n")
            f.write("\n")

            f.write("=== MEMÓRIA FÍSICA ===\n")
            mem = self.MMU.physical_memory.get_contents()

            for frame_index, vpn, last_use in mem:
                if vpn == -1:
                    f.write(f"Frame {frame_index}: livre\n")
                else:
                    base_virtual = vpn * self.config.tamPagina
                    f.write(
                        f"Frame {frame_index}: VPN {vpn} "
                        f"(base virtual 0x{base_virtual:04x})\n"
                    )
            f.write("\n")

            stats = self.MMU.getEstatisticas()

            f.write("=== ESTATÍSTICAS ===\n")
            f.write(f"Total de traduções: {stats['total_traducoes']}\n")
            f.write(f"Page faults: {stats['pageFaults']}\n")
            f.write(f"TLB hits: {stats['tlb']['hits']}\n")
            f.write(f"TLB misses: {stats['tlb']['misses']}\n")
            f.write(
                f"Molduras usadas: {stats['physical_memory']['used_frames']} "
                f"de {stats['physical_memory']['total_frames']}\n"
            )
            f.write("\n")

