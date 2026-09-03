"""
Unit tests for Memory & Page Replacement Statistics:
- Memory utilization and fragmentation metrics
- Page replacement statistics calculation
- Comparative analysis across FIFO, LRU, and Optimal
"""

from backend.memory.allocation import MemoryManager
from backend.memory.statistics import (
    calculate_memory_stats,
    calculate_page_replacement_stats,
    compare_page_replacement,
)
from backend.memory.page_replacement import fifo


def test_calculate_memory_stats():
    mm = MemoryManager(total_memory=1000)
    mm.allocate("P1", 200, "first_fit")
    mm.allocate("P2", 300, "first_fit")

    stats = calculate_memory_stats(mm)

    assert stats["total_memory"] == 1000
    assert stats["used_memory"] == 500
    assert stats["free_memory"] == 500
    assert stats["utilization_percentage"] == 50.0
    assert stats["allocated_processes_count"] == 2
    assert stats["free_blocks_count"] == 1
    assert stats["allocated_processes"] == {"P1": 200, "P2": 300}


def test_calculate_page_replacement_stats():
    ref_str = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3]
    fifo_res = fifo(ref_str, 3)

    stats = calculate_page_replacement_stats(fifo_res)

    assert stats["algorithm"] == "FIFO"
    assert stats["total_references"] == 10
    assert stats["page_faults"] == 8
    assert stats["page_hits"] == 2
    assert stats["page_fault_rate"] == 80.0
    assert stats["page_hit_rate"] == 20.0


def test_compare_page_replacement():
    ref_str = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3]
    comparison = compare_page_replacement(ref_str, frame_count=3)

    assert comparison["frame_count"] == 3
    assert len(comparison["comparison"]) == 3
    assert comparison["best_algorithm"] == "Optimal"

    algos = [item["algorithm"] for item in comparison["comparison"]]
    assert "FIFO" in algos
    assert "LRU" in algos
    assert "Optimal" in algos

    # Detailed results key check
    assert "FIFO" in comparison["detailed_results"]
    assert "LRU" in comparison["detailed_results"]
    assert "Optimal" in comparison["detailed_results"]
