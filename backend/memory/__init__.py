"""
Memory Management Subsystem for Virtual OS Dashboard.

This package provides:
- Memory Allocation Algorithms: First Fit, Best Fit, Worst Fit
- Virtual Memory / Page Replacement Algorithms: FIFO, LRU, Optimal
- Memory & Page Replacement Statistics & Comparison Utilities
"""

from backend.memory.allocation import (
    MemoryBlock,
    MemoryManager,
    allocate_first_fit,
    allocate_best_fit,
    allocate_worst_fit,
    deallocate_process,
    reset_memory,
)

from backend.memory.page_replacement import (
    fifo,
    lru,
    optimal,
    parse_reference_string,
)

from backend.memory.statistics import (
    calculate_memory_stats,
    calculate_page_replacement_stats,
    compare_page_replacement,
)

__all__ = [
    "MemoryBlock",
    "MemoryManager",
    "allocate_first_fit",
    "allocate_best_fit",
    "allocate_worst_fit",
    "deallocate_process",
    "reset_memory",
    "fifo",
    "lru",
    "optimal",
    "parse_reference_string",
    "calculate_memory_stats",
    "calculate_page_replacement_stats",
    "compare_page_replacement",
]
