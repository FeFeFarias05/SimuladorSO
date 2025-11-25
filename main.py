
from MemoryConfig import MemoryConfig
from MemorySimulator import MemorySimulator
from Colors import Colors

def main():
    print(f"{Colors.BOLD_BLUE}=== Simulador de um Sistema de Gerência de Memória Paginada do SO ==={Colors.RESET}")

    config = MemoryConfig(
        numeroEntradaTLB=2,
        tamanhoEspacoVirtual=16,
        bitsMemoriaFisica=14,
        tamanhoPagina=10,
        tamanhoSegText=12,
        tamanhoSegData=11,
        tamanhoSegStack=11,
        niveisTabelaPagina=2
    )

    print(f"{Colors.BOLD_GREEN}Configuração carregada.{Colors.RESET}\n")
    print(config)

    inputFile = input("Arquivo com os endereços virtuais: ").strip()
    outputFile = input("Arquivo de saída (saida.txt): ").strip()

    simulador = MemorySimulator(config)

    try:
        simulador.run_simulation(inputFile, outputFile)
        print(f"{Colors.BOLD_GREEN}\nSimulação concluída!{Colors.RESET}")
        print(f"Resultados salvos em: {outputFile}")
    except FileNotFoundError:
        print(f"{Colors.BOLD_RED}Erro: arquivo de entrada não encontrado.{Colors.RESET}")
    except ValueError as e:
        print(f"{Colors.BOLD_RED}Erro de configuração: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()
