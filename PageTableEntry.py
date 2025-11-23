"""
Tabela de Páginas Multi-nível
Suporta 1, 2 ou 3 níveis de tabelas
"""

class PageTableEntry:
    """Entrada da tabela de páginas"""
    
    def __init__(self):
        self.valid = False
        self.frame = -1  # -1 indica entrada livre
        self.next_level = None  # Para tabelas multi-nível


class PageTable:
    """
    Tabela de Páginas com suporte a múltiplos níveis
    """
    
    def __init__(self, config):
        """
        Inicializa a tabela de páginas
        
        Args:
            config: Objeto MemoryConfig com a configuração do sistema
        """
        self.config = config
        self.levels = config.page_table_levels
        self.bits_per_level = config.bits_per_level
        
        # Cria a estrutura da tabela baseada no número de níveis
        if self.levels == 1:
            # Tabela de 1 nível: array simples
            self.table = self._create_table_level(0)
        else:
            # Tabela multi-nível: estrutura hierárquica
            self.table = {}
    
    def _create_table_level(self, level):
        """
        Cria um nível da tabela de páginas
        
        Args:
            level: Índice do nível (0 = primeiro nível)
            
        Returns:
            Dicionário representando o nível
        """
        return {}
    
    def _get_vpn_indices(self, vpn):
        """
        Extrai os índices de cada nível da tabela a partir do VPN
        
        Args:
            vpn: Número da página virtual
            
        Returns:
            Lista de índices, um por nível
        """
        indices = []
        remaining = vpn
        
        # Extrai bits de trás para frente (do último nível para o primeiro)
        for i in range(self.levels - 1, -1, -1):
            bits = self.bits_per_level[i]
            mask = (1 << bits) - 1
            index = remaining & mask
            indices.insert(0, index)
            remaining >>= bits
        
        return indices
    
    def lookup(self, vpn):
        """
        Procura um VPN na tabela de páginas
        
        Args:
            vpn: Número da página virtual
            
        Returns:
            Frame number se encontrado e válido, -1 caso contrário
        """
        if self.levels == 1:
            # Tabela de 1 nível
            if vpn in self.table and self.table[vpn]['valid']:
                return self.table[vpn]['frame']
            return -1
        else:
            # Tabela multi-nível
            indices = self._get_vpn_indices(vpn)
            current = self.table
            
            # Navega pelos níveis
            for i, index in enumerate(indices):
                if index not in current:
                    return -1
                
                if i == self.levels - 1:
                    # Último nível - deve conter o frame
                    if current[index]['valid']:
                        return current[index]['frame']
                    return -1
                else:
                    # Nível intermediário - deve apontar para próximo nível
                    if 'next_level' not in current[index]:
                        return -1
                    current = current[index]['next_level']
            
            return -1
    
    def insert(self, vpn, frame):
        """
        Insere ou atualiza uma entrada na tabela de páginas
        
        Args:
            vpn: Número da página virtual
            frame: Número da moldura física
        """
        if self.levels == 1:
            # Tabela de 1 nível
            self.table[vpn] = {
                'valid': True,
                'frame': frame
            }
        else:
            # Tabela multi-nível
            indices = self._get_vpn_indices(vpn)
            current = self.table
            
            # Navega/cria os níveis
            for i, index in enumerate(indices):
                if i == self.levels - 1:
                    # Último nível - insere o frame
                    current[index] = {
                        'valid': True,
                        'frame': frame
                    }
                else:
                    # Nível intermediário - cria próximo nível se necessário
                    if index not in current:
                        current[index] = {
                            'next_level': {}
                        }
                    current = current[index]['next_level']
    
    def invalidate(self, vpn):
        """
        Invalida uma entrada da tabela de páginas
        
        Args:
            vpn: Número da página virtual
        """
        if self.levels == 1:
            if vpn in self.table:
                self.table[vpn]['valid'] = False
                self.table[vpn]['frame'] = -1
        else:
            indices = self._get_vpn_indices(vpn)
            current = self.table
            
            for i, index in enumerate(indices):
                if index not in current:
                    return
                
                if i == self.levels - 1:
                    current[index]['valid'] = False
                    current[index]['frame'] = -1
                else:
                    if 'next_level' not in current[index]:
                        return
                    current = current[index]['next_level']
    
    def get_all_mappings(self):
        """
        Retorna todos os mapeamentos VPN -> Frame válidos
        
        Returns:
            Lista de tuplas (vpn, frame)
        """
        mappings = []
        
        if self.levels == 1:
            for vpn, entry in self.table.items():
                if entry['valid']:
                    mappings.append((vpn, entry['frame']))
        else:
            self._collect_mappings(self.table, [], mappings, 0)
        
        return sorted(mappings)
    
    def _collect_mappings(self, current_level, indices, mappings, level):
        """
        Coleta recursivamente todos os mapeamentos de uma tabela multi-nível
        
        Args:
            current_level: Nível atual da tabela
            indices: Índices acumulados até agora
            mappings: Lista para armazenar os mapeamentos
            level: Número do nível atual
        """
        for index, entry in current_level.items():
            new_indices = indices + [index]
            
            if level == self.levels - 1:
                # Último nível
                if entry.get('valid', False):
                    vpn = self._indices_to_vpn(new_indices)
                    mappings.append((vpn, entry['frame']))
            else:
                # Nível intermediário
                if 'next_level' in entry:
                    self._collect_mappings(entry['next_level'], new_indices, 
                                          mappings, level + 1)
    
    def _indices_to_vpn(self, indices):
        """
        Converte uma lista de índices de volta para VPN
        
        Args:
            indices: Lista de índices, um por nível
            
        Returns:
            VPN correspondente
        """
        vpn = 0
        for i, index in enumerate(indices):
            vpn <<= self.bits_per_level[i]
            vpn |= index
        return vpn
    
    def __str__(self):
        """Representação em string da tabela de páginas"""
        mappings = self.get_all_mappings()
        if not mappings:
            return f"Tabela de Páginas ({self.levels} níveis): [vazia]"
        
        result = [f"Tabela de Páginas ({self.levels} níveis):"]
        for vpn, frame in mappings:
            result.append(f"  VPN {vpn} -> Frame {frame}")
        
        return "\n".join(result)
    
    def to_dict(self):
        """
        Converte a tabela de páginas para dicionário
        
        Returns:
            Dicionário representando a tabela
        """
        return {
            'levels': self.levels,
            'bits_per_level': self.bits_per_level,
            'mappings': self.get_all_mappings()
        }
