#!/usr/bin/env python3
"""
Script de demonstração do Simulador MLFQ

Este script demonstra diferentes cenários de uso do simulador
e pode ser executado para testar rapidamente o funcionamento.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> None:
    """Executa um comando e exibe o resultado."""
    print(f"\n{'='*60}")
    print(f"🎯 {description}")
    print(f"{'='*60}")
    print(f"Comando: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
    except FileNotFoundError:
        print("❌ Erro: Comando não encontrado. Verifique se está no diretório correto.")


def main():
    """Função principal do script de demonstração."""
    print("🚀 SIMULADOR MLFQ - DEMONSTRAÇÃO")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not Path("src/simulador_so").exists():
        print("❌ Erro: Execute este script no diretório raiz do projeto")
        print("   Diretório atual deve conter: src/simulador_so/")
        sys.exit(1)
    
    # Verificar se os exemplos existem
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("❌ Erro: Diretório 'examples' não encontrado")
        sys.exit(1)
    
    # Lista de demonstrações
    demos = [
        {
            "cmd": ["python", "-m", "src.simulador_so.cli", "--input", "examples/input_example.json"],
            "desc": "Exemplo Básico - 2 processos com E/S"
        },
        {
            "cmd": ["python", "-m", "src.simulador_so.cli", "--input", "examples/input_example.json", "--verbose"],
            "desc": "Exemplo Básico com Timeline Detalhada"
        },
        {
            "cmd": ["python", "-m", "src.simulador_so.cli", "--input", "examples/complex_example.json"],
            "desc": "Exemplo Complexo - 4 processos com diferentes características"
        },
        {
            "cmd": ["python", "-m", "src.simulador_so.cli", "--help"],
            "desc": "Ajuda do Simulador"
        }
    ]
    
    # Executar demonstrações
    for i, demo in enumerate(demos, 1):
        print(f"\n📋 Demonstração {i}/{len(demos)}")
        run_command(demo["cmd"], demo["desc"])
        
        if i < len(demos):
            input("\n⏸️  Pressione Enter para continuar...")
    
    # Executar testes
    print(f"\n{'='*60}")
    print("🧪 EXECUTANDO TESTES AUTOMATIZADOS")
    print(f"{'='*60}")
    run_command(["python", "-m", "pytest", "tests/", "-v"], "Testes Unitários")
    
    print(f"\n{'='*60}")
    print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
    print(f"{'='*60}")
    print("📚 Para mais informações, consulte:")
    print("   - README.md: Documentação completa")
    print("   - tests/: Testes automatizados")
    print("\n🎯 Comandos úteis:")
    print("   python -m src.simulador_so.cli --help")
    print("   python -m pytest tests/ -v")
    print("   python -m src.simulador_so.cli --input examples/input_example.json --verbose")


if __name__ == "__main__":
    main()
