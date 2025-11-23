"""Multi-level page table (1..3 levels). Each mapped leaf stores PFN (int). Unmapped -> not present."""
from typing import Dict

class PageTable:
    def __init__(self, vpn_bits: int, levels: int = 1):
        assert 0 <= vpn_bits
        assert 1 <= levels <= 3
        self.vpn_bits = vpn_bits
        self.levels = levels
        base = vpn_bits // levels if levels>0 else 0
        rem = vpn_bits % levels if levels>0 else 0
        self.bits_per_level = [(base + (1 if i < rem else 0)) for i in range(levels)]
        # compute shifts
        acc = vpn_bits
        self.level_shifts = []
        for b in self.bits_per_level:
            acc -= b
            self.level_shifts.append(acc)
        self.root = {}

    def _indices(self, vpn: int):
        idxs = []
        for lvl,bits in enumerate(self.bits_per_level):
            shift = self.level_shifts[lvl]
            mask = (1 << bits)-1 if bits>0 else 0
            idx = (vpn >> shift) & mask if bits>0 else 0
            idxs.append(idx)
        return idxs

    def lookup(self, vpn: int) -> int:
        node = self.root
        idxs = self._indices(vpn)
        for i, idx in enumerate(idxs):
            if idx not in node:
                return -1
            node = node[idx]
        if isinstance(node, int):
            return node
        return -1

    def map(self, vpn: int, pfn: int):
        node = self.root
        idxs = self._indices(vpn)
        for i, idx in enumerate(idxs):
            if i == len(idxs)-1:
                node[idx] = pfn
            else:
                if idx not in node or not isinstance(node[idx], dict):
                    node[idx] = {}
                node = node[idx]

    def unmap(self, vpn: int):
        # simple unmap: walk and delete leaf if present, then cleanup empty dicts
        path = []
        node = self.root
        idxs = self._indices(vpn)
        for idx in idxs:
            if idx not in node:
                return
            path.append((node, idx))
            node = node[idx]
        parent, last_idx = path[-1]
        del parent[last_idx]
        # cleanup
        for parent, idx in reversed(path[:-1]):
            child = parent[idx]
            if isinstance(child, dict) and len(child)==0:
                del parent[idx]
            else:
                break

    def dump_mappings(self):
        result = {}
        def dfs(node, lvl, prefix):
            if lvl == len(self.bits_per_level):
                if isinstance(node, int):
                    result[prefix] = node
                return
            if not isinstance(node, dict):
                return
            bits = self.bits_per_level[lvl]
            for idx, child in node.items():
                new_prefix = (prefix << bits) | idx if bits>0 else prefix
                if lvl == len(self.bits_per_level)-1:
                    if isinstance(child, int):
                        result[new_prefix] = child
                else:
                    dfs(child, lvl+1, new_prefix)
        dfs(self.root, 0, 0)
        return result
