"""
Translation Lookaside Buffer (TLB)
Cache para traduções de páginas virtuais para molduras físicas
"""

from collections import OrderedDict

class TLB:
    """
    Translation Lookaside Buffer
    Armazena traduções recentes de VPN -> Frame usando política FIFO
    """
    
    def __init__(self, num_entries):
        """
        Inicializa a TLB
        
        Args:
            num_entries: Número máximo de entradas na TLB
        """
        self.num_entries = num_entries
        # Usa OrderedDict para manter ordem de inserção (FIFO)
        self.entries = OrderedDict()
        
        # Estatísticas
        self.hits = 0
        self.misses = 0
    
    def lookup(self, vpn):
        """
        Procura um VPN na TLB
        
        Args:
            vpn: Número da página virtual
            
        Returns:
            Frame number se encontrado, None caso contrário
        """
        if vpn in self.entries:
            self.hits += 1
            return self.entries[vpn]
        else:
            self.misses += 1
            return None
    
    def insert(self, vpn, frame):
        """
        Insere ou atualiza uma tradução na TLB
        
        Args:
            vpn: Número da página virtual
            frame: Número da moldura física
        """
        # Se já existe, remove para reinserir no final (atualizar ordem)
        if vpn in self.entries:
            del self.entries[vpn]
        
        # Se está cheia, remove a entrada mais antiga (primeira)
        elif len(self.entries) >= self.num_entries:
            self.entries.popitem(last=False)  # Remove primeiro item (mais antigo)
        
        # Insere a nova entrada
        self.entries[vpn] = frame
    
    def invalidate(self, vpn):
        """
        Invalida uma entrada da TLB
        
        Args:
            vpn: Número da página virtual a invalidar
        """
        if vpn in self.entries:
            del self.entries[vpn]
    
    def clear(self):
        """Limpa todas as entradas da TLB"""
        self.entries.clear()
    
    def get_hit_rate(self):
        """
        Calcula a taxa de acertos da TLB
        
        Returns:
            Taxa de acertos (0.0 a 1.0)
        """
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total
    
    def get_statistics(self):
        """
        Retorna estatísticas da TLB
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_accesses': self.hits + self.misses,
            'hit_rate': self.get_hit_rate(),
            'current_entries': len(self.entries),
            'max_entries': self.num_entries
        }
    
    def get_contents(self):
        """
        Retorna o conteúdo atual da TLB
        
        Returns:
            Lista de tuplas (vpn, frame)
        """
        return list(self.entries.items())
    
    def __str__(self):
        """Representação em string da TLB"""
        contents = self.get_contents()
        if not contents:
            return "TLB: [vazia]"
        
        entries_str = ", ".join([f"VPN {vpn} -> Frame {frame}" 
                                 for vpn, frame in contents])
        return f"TLB ({len(contents)}/{self.num_entries}): [{entries_str}]"
    
    def to_dict(self):
        """
        Converte a TLB para dicionário (para serialização)
        
        Returns:
            Dicionário representando a TLB
        """
        return {
            'entries': self.get_contents(),
            'statistics': self.get_statistics()
        }
