"""
Módulo para carregar processos de arquivos de entrada.
"""

import json
import csv
from typing import List, Dict, Any
from process import Process

class ProcessLoader:
    """Classe responsável por carregar processos de diferentes formatos de arquivo."""
    
    @staticmethod
    def load_from_json(file_path: str) -> List[Process]:
        """
        Carrega processos de um arquivo JSON.
        
        Formato esperado:
        {
            "quantum_q0": 5,
            "quantum_q1": 15,
            "processes": [
                {
                    "name": "P1",
                    "cpu_burst": 10,
                    "io_time": 5,
                    "total_cpu_time": 50,
                    "priority": 1
                },
                ...
            ]
        }
        
        Args:
            file_path: Caminho para o arquivo JSON
            
        Returns:
            Lista de processos carregados
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            processes = []
            process_data = data.get('processes', [])
            
            for proc_info in process_data:
                process = Process(
                    nome=proc_info['name'],
                    cpu_burst=proc_info['cpu_burst'],
                    io_time=proc_info['io_time'],
                    total_cpu_time=proc_info['total_cpu_time'],
                    priority=proc_info['priority']
                )
                processes.append(process)
                
            return processes
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON: {e}")
        except KeyError as e:
            raise ValueError(f"Campo obrigatório ausente: {e}")
    
    @staticmethod
    def load_from_csv(file_path: str) -> List[Process]:
        """
        Carrega processos de um arquivo CSV.
        
        Formato esperado (primeira linha deve ser o cabeçalho):
        name,cpu_burst,io_time,total_cpu_time,priority
        P1,10,5,50,1
        P2,15,3,40,2
        ...
        
        Args:
            file_path: Caminho para o arquivo CSV
            
        Returns:
            Lista de processos carregados
        """
        try:
            processes = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    process = Process(
                        nome=row['name'],
                        cpu_burst=int(row['cpu_burst']),
                        io_time=int(row['io_time']),
                        total_cpu_time=int(row['total_cpu_time']),
                        priority=int(row['priority'])
                    )
                    processes.append(process)
                    
            return processes
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        except ValueError as e:
            raise ValueError(f"Erro ao converter valores: {e}")
        except KeyError as e:
            raise ValueError(f"Coluna obrigatória ausente: {e}")
    
    @staticmethod
    def load_from_txt(file_path: str) -> List[Process]:
        """
        Carrega processos de um arquivo de texto simples.
        
        Formato esperado (uma linha por processo):
        nome cpu_burst io_time total_cpu_time priority
        P1 10 5 50 1
        P2 15 3 40 2
        ...
        
        Args:
            file_path: Caminho para o arquivo TXT
            
        Returns:
            Lista de processos carregados
        """
        try:
            processes = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):  # Ignora linhas vazias e comentários
                        continue
                        
                    parts = line.split()
                    if len(parts) != 5:
                        raise ValueError(f"Linha {line_num}: formato inválido. "
                                       f"Esperado: nome cpu_burst io_time total_cpu_time priority")
                    
                    try:
                        process = Process(
                            nome=parts[0],
                            cpu_burst=int(parts[1]),
                            io_time=int(parts[2]),
                            total_cpu_time=int(parts[3]),
                            priority=int(parts[4])
                        )
                        processes.append(process)
                    except ValueError as e:
                        raise ValueError(f"Linha {line_num}: erro ao converter valores - {e}")
                        
            return processes
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    @staticmethod
    def get_config_from_json(file_path: str) -> Dict[str, Any]:
        """
        Extrai configurações do escalonador de um arquivo JSON.
        
        Args:
            file_path: Caminho para o arquivo JSON
            
        Returns:
            Dicionário com configurações
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            config = {}
            if 'quantum_q0' in data:
                config['quantum_q0'] = data['quantum_q0']
            if 'quantum_q1' in data:
                config['quantum_q1'] = data['quantum_q1']
                
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON: {e}")
    
    @staticmethod
    def validate_process_data(processes: List[Process]) -> None:
        """
        Valida os dados dos processos carregados.
        
        Args:
            processes: Lista de processos para validar
            
        Raises:
            ValueError: Se algum processo tem dados inválidos
        """
        for i, process in enumerate(processes):
            if process.cpu_burst <= 0:
                raise ValueError(f"Processo {process.name}: cpu_burst deve ser > 0")
            if process.io_time < 0:
                raise ValueError(f"Processo {process.name}: io_time deve ser >= 0")
            if process.total_cpu_time <= 0:
                raise ValueError(f"Processo {process.name}: total_cpu_time deve ser > 0")
            if process.priority < 0:
                raise ValueError(f"Processo {process.name}: priority deve ser >= 0")
            if process.cpu_burst > process.total_cpu_time:
                raise ValueError(f"Processo {process.name}: cpu_burst não pode ser maior que total_cpu_time")
