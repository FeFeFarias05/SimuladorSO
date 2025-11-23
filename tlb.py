"""TLB module: FIFO TLB with configurable size (entries)."""
from collections import deque
from typing import Optional, List, Tuple

class TLBEntry:
    def __init__(self, vpn: int, pfn: int, time_added: int):
        self.vpn = vpn
        self.pfn = pfn
        self.time_added = time_added

class TLB:
    def __init__(self, entries_bits: int = 3):
        """
        entries_bits: number of bits n such that number of entries = 2^n.
        Valid n in [0..6] (0 -> 1 entry, 6 -> 64 entries). If 2^n > 64, capped to 64.
        """
        n = max(0, int(entries_bits))
        n = min(n, 6)
        self.size = 1 << n
        self.queue = deque()  # FIFO queue of TLBEntry
        self.map = {}  # vpn -> pfn

    def lookup(self, vpn: int) -> Optional[int]:
        return self.map.get(vpn, None)

    def add(self, vpn: int, pfn: int, timestamp: int):
        # remove existing entry if present
        if vpn in self.map:
            # update queue: remove old entry
            self.queue = deque(e for e in self.queue if e.vpn != vpn)
        # evict if full
        if self.size == 0:
            return
        if len(self.queue) >= self.size:
            ev = self.queue.popleft()
            if ev.vpn in self.map and self.map[ev.vpn] == ev.pfn:
                del self.map[ev.vpn]
        entry = TLBEntry(vpn, pfn, timestamp)
        self.queue.append(entry)
        self.map[vpn] = pfn

    def invalidate(self, vpn: int):
        if vpn in self.map:
            del self.map[vpn]
            self.queue = deque(e for e in self.queue if e.vpn != vpn)

    def dump(self) -> List[Tuple[int,int,int]]:
        return [(e.vpn, e.pfn, e.time_added) for e in self.queue]
