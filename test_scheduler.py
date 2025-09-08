from process import Processo
from scheduler import Escalonador

def main():
    """Função principal para testes do escalonador"""
    
    # Criação dos processos usando parâmetros individuais
    A = Processo('A', 2, 5, 6, 1, 3)
    B = Processo('B', 3, 10, 6, 2, 3)
    C = Processo('C', 0, 0, 14, 3, 3)
    D = Processo('D', 0, 0, 10, 4, 3)

    # Inicialização dos atributos necessários para a simulação
    processos = [A, B, C, D]
    for p in processos:
        p.linha_tempo = []
        p.tempo_inicio = None
        p.tempo_fim = None

    # Cria o escalonador
    escalonador = Escalonador(processos)

    # Executa a simulação
    linha_tempo_cpu = escalonador.executar_simulacao()

    # Gera o relatório
    escalonador.gerar_relatorio(linha_tempo_cpu)

def teste_metodo_parametros():
    """Teste do método com parâmetros individuais"""
    print("\n=== Teste do método com parâmetros individuais ===")
    
    # Usando o construtor com parâmetros individuais
    processo1 = Processo('P1', 5, 3, 15, 1, 2)
    print(f"Processo criado: {processo1}")
    
    # Criando outro processo
    processo2 = Processo('P2', 8, 4, 20, 2, 1)
    print(f"Outro processo: {processo2}")

if __name__ == "__main__":
    # Executa o teste principal
    main()
    
    # Executa o teste do novo método
    teste_metodo_parametros()
