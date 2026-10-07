"""
Memory & Page Replacement Statistics Module.

Calculates detailed statistics and algorithm performance comparisons:
- Memory Utilization & External Fragmentation Metrics
- Page Replacement Metrics (Page Faults, Hits, Rates)
- Side-by-side Algorithm Comparison (FIFO vs LRU vs Optimal)
"""

from typing import Dict, List, Union, Any
from backend.memory.allocation import MemoryManager
from backend.memory.page_replacement import (
    fifo,
    lru,
    optimal,
    parse_reference_string,
)


def calculate_memory_stats(memory_manager: MemoryManager) -> Dict[str, Any]:
    """
    Generates comprehensive statistics on memory allocation status, utilization, and fragmentation.
    """
    used = memory_manager.get_used_memory()
    free = memory_manager.get_free_memory()
    total = memory_manager.total_memory
    utilization = round((used / total) * 100, 2) if total > 0 else 0.0

    allocated_procs = memory_manager.get_allocated_processes()
    free_blocks = [b for b in memory_manager.blocks if not b.is_allocated]

    return {
        "total_memory": total,
        "used_memory": used,
        "free_memory": free,
        "utilization_percentage": utilization,
        "allocated_processes_count": len(allocated_procs),
        "free_blocks_count": len(free_blocks),
        "external_fragmentation": memory_manager.get_external_fragmentation(),
        "largest_free_block": max([b.size for b in free_blocks], default=0),
        "smallest_free_block": min([b.size for b in free_blocks], default=0),
        "allocated_processes": allocated_procs,
    }


def calculate_page_replacement_stats(result_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts summary statistics from a page replacement simulation result dictionary.
    """
    return {
        "algorithm": result_dict.get("algorithm", "Unknown"),
        "total_references": result_dict.get("total_references", 0),
        "page_faults": result_dict.get("page_faults", 0),
        "page_hits": result_dict.get("page_hits", 0),
        "page_fault_rate": result_dict.get("page_fault_rate", 0.0),
        "page_hit_rate": result_dict.get("page_hit_rate", 0.0),
    }


def compare_page_replacement(
    reference_string: Union[str, List[Union[int, str]]], frame_count: int
) -> Dict[str, Any]:
    """
    Runs FIFO, LRU, and Optimal algorithms on identical inputs and produces a comparative analysis.
    """
    parsed_ref = parse_reference_string(reference_string)

    fifo_res = fifo(parsed_ref, frame_count)
    lru_res = lru(parsed_ref, frame_count)
    optimal_res = optimal(parsed_ref, frame_count)

    comparison_list = [
        calculate_page_replacement_stats(fifo_res),
        calculate_page_replacement_stats(lru_res),
        calculate_page_replacement_stats(optimal_res),
    ]

    # Determine best performing algorithm (lowest page faults)
    best = min(comparison_list, key=lambda item: (item["page_faults"], item["algorithm"] != "Optimal"))

    return {
        "reference_string": parsed_ref,
        "frame_count": frame_count,
        "comparison": comparison_list,
        "best_algorithm": best["algorithm"],
        "detailed_results": {
            "FIFO": fifo_res,
            "LRU": lru_res,
            "Optimal": optimal_res,
        },
    }
