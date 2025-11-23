#!/bin/bash
# Script de teste rápido do simulador

echo "=========================================="
echo "TESTE DO SIMULADOR DE MEMÓRIA PAGINADA"
echo "=========================================="
echo ""

# Teste 1: Mostrar configuração
echo "1. Mostrando configuração padrão..."
python3 main.py --show-config
echo ""

# Teste 2: Gerar endereços
echo "2. Gerando 30 endereços aleatórios..."
python3 main.py -g 30 --generate-only --output-addresses test_addresses.txt
echo "   ✓ Endereços salvos em: test_addresses.txt"
echo ""

# Teste 3: Executar simulação
echo "3. Executando simulação..."
python3 main.py -i test_addresses.txt -o test_output.txt
echo ""

# Teste 4: Simulação com localidade
echo "4. Gerando e simulando com localidade..."
python3 main.py -g 50 --locality 0.8 -o test_locality.txt -q
echo "   ✓ Resultados em: test_locality.txt"
echo ""

# Teste 5: Configuração customizada
echo "5. Testando com configuração customizada..."
python3 main.py -g 40 -o test_custom.txt \
  --virtual-bits 18 \
  --physical-bits 16 \
  --page-bits 12 \
  --tlb-bits 3 \
  --page-table-levels 3 \
  -q
echo "   ✓ Resultados em: test_custom.txt"
echo ""

# Teste 6: Exportar JSON
echo "6. Exportando estado em JSON..."
python3 main.py -g 20 -o test_json_output.txt --json test_state.json -q
echo "   ✓ Estado exportado para: test_state.json"
echo ""

echo "=========================================="
echo "TODOS OS TESTES CONCLUÍDOS!"
echo "=========================================="
echo ""
echo "Arquivos gerados:"
echo "  - test_addresses.txt"
echo "  - test_output.txt"
echo "  - test_locality.txt"
echo "  - test_custom.txt"
echo "  - test_json_output.txt"
echo "  - test_state.json"
echo ""
echo "Examine os arquivos test_output.txt ou test_locality.txt"
echo "para ver os resultados detalhados da simulação!"
