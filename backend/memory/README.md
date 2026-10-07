# Memory Management and Virtual Memory Subsystem

This module simulates physical memory allocation, virtual memory page replacement, and resource utilization statistics for the **Virtual OS Dashboard** project.

It provides clean, modular, JSON-ready Python interfaces designed to be easily imported and served by API endpoints (e.g. Flask/FastAPI) or integrated with the main application dashboard.

---

## Features & Algorithms Implemented

### 1. Memory Allocation (`backend.memory.allocation`)
- **First Fit**: Allocates memory to the first unallocated block large enough to satisfy the request.
- **Best Fit**: Allocates memory to the smallest unallocated block large enough to satisfy the request.
- **Worst Fit**: Allocates memory to the largest unallocated block large enough to satisfy the request.
- **Deallocation & Coalescing**: Deallocates memory by Process ID and automatically merges adjacent free blocks to minimize fragmentation.
- **External Fragmentation**: Identifies free space split into non-contiguous fragments that cannot satisfy allocation requests.

### 2. Page Replacement (`backend.memory.page_replacement`)
- **FIFO (First-In, First-Out)**: Replaces the page that entered physical memory earliest.
- **LRU (Least Recently Used)**: Replaces the page that has not been accessed for the longest duration.
- **Optimal (Belady's Optimal)**: Replaces the page whose next usage is farthest in the future (or never used again).

### 3. Statistics & Comparison (`backend.memory.statistics`)
- Memory Utilization %, Total, Used, Free memory calculations.
- Page Faults, Page Hits, Page Fault Rate %, and Hit Rate %.
- **Comparative Analysis**: Runs FIFO, LRU, and Optimal side-by-side on identical reference strings and frame counts to evaluate performance.

---

## Quick Start / Usage

### Memory Allocation Example

```python
from backend.memory import MemoryManager, allocate_first_fit, allocate_best_fit, deallocate_process

# 1. Initialize Memory Manager with total physical memory (e.g., 1024 MB)
mm = MemoryManager(total_memory=1024)

# 2. Allocate memory to processes
result1 = allocate_first_fit(mm, process_id="P1", size=200)
result2 = allocate_best_fit(mm, process_id="P2", size=300)

print(result2)
# Output:
# {
#   "success": True,
#   "message": "Process P2 (300 MB) successfully allocated using Best Fit.",
#   "total_memory": 1024,
#   "used_memory": 500,
#   "free_memory": 524,
#   "utilization_percentage": 48.83,
#   "external_fragmentation": 0,
#   "allocated_processes": {"P1": 200, "P2": 300},
#   "blocks": [...]
# }

# 3. Deallocate a process and coalesce free blocks
deallocate_result = deallocate_process(mm, process_id="P1")
```

---

### Page Replacement Example

```python
from backend.memory import fifo, lru, optimal, compare_page_replacement

ref_str = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3]
frames = 3

# Run individual algorithms
fifo_res = fifo(ref_str, frame_count=frames)
lru_res = lru(ref_str, frame_count=frames)
opt_res = optimal(ref_str, frame_count=frames)

# Compare all three algorithms side-by-side
comparison = compare_page_replacement(ref_str, frame_count=frames)
print(f"Best performing algorithm: {comparison['best_algorithm']}")
# Output: Best performing algorithm: Optimal
```

---

## Running Unit Tests

From the project root directory:

```bash
python3 -m pytest
```

All test suites (`test_scheduling.py`, `test_memory_allocation.py`, `test_page_replacement.py`, `test_memory_statistics.py`) should execute cleanly.
