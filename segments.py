"""Segment layout utilities: compute bases and sizes for .text, .data, .stack, .bss."""
from typing import Tuple

def compute_segments(virtual_size: int, text_size: int, data_size: int, stack_size: int):
    # .bss = 3 * (text + data + stack), adjusted to fit remaining virtual space
    bss = 3 * (text_size + data_size + stack_size)
    used = text_size + data_size + stack_size
    remaining = max(0, virtual_size - used)
    if bss > remaining:
        bss = remaining
    # layout: text, data, bss, stack at top
    base = 0
    text_base = base; base += text_size
    data_base = base; base += data_size
    bss_base = base; base += bss
    stack_base = max(base, virtual_size - stack_size)
    return {
        "text": (text_base, text_size),
        "data": (data_base, data_size),
        "bss": (bss_base, bss),
        "stack": (stack_base, stack_size)
    }

def which_segment(segments, vaddr: int):
    for name, (base, size) in segments.items():
        if base <= vaddr < base + size:
            return name
    return "unknown"
