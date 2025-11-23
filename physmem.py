"""Physical memory: vector of frames initialized with -1 and LRU replacement."""
from typing import List, Tuple, Optional

class PhysicalMemory:
    def __init__(self, num_frames: int):
        assert num_frames >= 0
        self.num_frames = num_frames
        self.frames: List[int] = [-1]*num_frames  # stores vpn or -1
        self.last_used: List[int] = [0]*num_frames  # timestamps for LRU
        self.time = 0

    def allocate(self, vpn: int) -> Tuple[int, Optional[int]]:
        """
        Allocate a frame for vpn. Returns (frame_index, evicted_vpn_or_None).
        Uses free frame if available, otherwise LRU eviction.
        """
        self.time += 1
        if -1 in self.frames:
            idx = self.frames.index(-1)
            self.frames[idx] = vpn
            self.last_used[idx] = self.time
            return idx, None
        # LRU eviction (min last_used)
        lru_idx = min(range(self.num_frames), key=lambda i: self.last_used[i])
        evicted = self.frames[lru_idx]
        self.frames[lru_idx] = vpn
        self.last_used[lru_idx] = self.time
        return lru_idx, evicted

    def touch(self, frame_idx: int):
        self.time += 1
        self.last_used[frame_idx] = self.time

    def dump(self) -> List[int]:
        return list(self.frames)
