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
        resultados = self.MMU.traduzirLote(enderecos)
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
            tlbItems = self.MMU.tlb.getEntradasTLB()

            if len(tlbItems) == 0:
                f.write("TLB vazia\n")
            else:
                for vpn, frame in tlbItems:
                    f.write(f"VPN {vpn} -> Frame {frame}\n")
            f.write("\n")

            f.write("=== TABELA DE PÁGINAS ===\n")
            mapeamentos = self.MMU.tabelaPaginas.getMapeamentos()

            if len(mapeamentos) == 0:
                f.write("Tabela de páginas vazia\n")
            else:
                for vpn, frame in mapeamentos:
                    f.write(f"VPN {vpn} -> Frame {frame}\n")
            f.write("\n")

            f.write("=== MEMÓRIA FÍSICA ===\n")
            mem = self.MMU.memoriaFisica.getConteudo()

            for frameIndex, vpn, last_use in mem:
                if vpn == -1:
                    f.write(f"Frame {frameIndex}: livre\n")
                else:
                    base_virtual = vpn * self.config.tamPagina
                    f.write(
                        f"Frame {frameIndex}: VPN {vpn} "
                        f"(base virtual 0x{base_virtual:04x})\n"
                    )
            f.write("\n")

            estatisticas = self.MMU.getEstatisticas()

            f.write("=== ESTATÍSTICAS ===\n")
            f.write(f"Total de traduções: {estatisticas['totalTraducoes']}\n")
            f.write(f"Page faults: {estatisticas['pageFaults']}\n")
            f.write(f"TLB hits: {estatisticas['tlb']['hits']}\n")
            f.write(f"TLB misses: {estatisticas['tlb']['misses']}\n")
            f.write(
                f"Molduras usadas: {estatisticas['memoriaFisica']['used_frames']} "
                f"de {estatisticas['memoriaFisica']['total_frames']}\n"
            )
            f.write("\n")

