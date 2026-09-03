"""
Unit tests for Memory Management & Allocation Algorithms:
- First Fit
- Best Fit
- Worst Fit
- Deallocation & Free Block Coalescing
- Edge Cases & Input Validation
"""

import pytest
from backend.memory.allocation import (
    MemoryManager,
    allocate_first_fit,
    allocate_best_fit,
    allocate_worst_fit,
    deallocate_process,
    reset_memory,
)


def create_fragmented_memory() -> MemoryManager:
    """
    Helper function to construct a memory layout with free blocks of specific sizes:
    [Allocated P1 (100MB)] -> [Free (100MB)] -> [Allocated P2 (100MB)] ->
    [Free (300MB)] -> [Allocated P3 (100MB)] -> [Free (200MB)] -> [Allocated P4 (100MB)] -> [Free (500MB)]
    Total size = 1500 MB.
    Free blocks available: 100 MB (start 100), 300 MB (start 300), 200 MB (start 700), 500 MB (start 1000).
    """
    mm = MemoryManager(total_memory=1500)
    # 1. Allocate initial setup
    mm.allocate("P1", 100, "first_fit")  # [0..100]
    mm.allocate("P_FREE1", 100, "first_fit")  # [100..200]
    mm.allocate("P2", 100, "first_fit")  # [200..300]
    mm.allocate("P_FREE2", 300, "first_fit")  # [300..600]
    mm.allocate("P3", 100, "first_fit")  # [600..700]
    mm.allocate("P_FREE3", 200, "first_fit")  # [700..900]
    mm.allocate("P4", 100, "first_fit")  # [900..1000]
    mm.allocate("P_FREE4", 500, "first_fit")  # [1000..1500]

    # Free the placeholder blocks to create free holes of 100, 300, 200, 500
    mm.deallocate("P_FREE1")
    mm.deallocate("P_FREE2")
    mm.deallocate("P_FREE3")
    mm.deallocate("P_FREE4")
    return mm


def test_first_fit():
    mm = create_fragmented_memory()
    # Free blocks: 100MB (at 100), 300MB (at 300), 200MB (at 700), 500MB (at 1000)
    # Process P_NEW requests 250 MB. First Fit should select the 300 MB block at start 300.
    res = allocate_first_fit(mm, "P_NEW", 250)
    assert res["success"] is True

    p_new_block = [b for b in res["blocks"] if b["process_id"] == "P_NEW"][0]
    assert p_new_block["start"] == 300
    assert p_new_block["size"] == 250


def test_best_fit():
    # Scenario A: Free blocks 100MB, 300MB, 200MB, 500MB. Request 250MB -> Best fit picks 300MB block (at start 300).
    mm1 = create_fragmented_memory()
    res1 = allocate_best_fit(mm1, "P_NEW", 250)
    assert res1["success"] is True
    p_new1 = [b for b in res1["blocks"] if b["process_id"] == "P_NEW"][0]
    assert p_new1["start"] == 300
    assert p_new1["size"] == 250

    # Scenario B: Free blocks 100MB, 280MB, 300MB, 500MB. Request 250MB -> Best fit picks 280MB block.
    mm2 = MemoryManager(total_memory=1580)
    mm2.allocate("X1", 100, "first_fit")
    mm2.allocate("FREE1", 100, "first_fit")
    mm2.allocate("X2", 100, "first_fit")
    mm2.allocate("FREE2", 280, "first_fit")
    mm2.allocate("X3", 100, "first_fit")
    mm2.allocate("FREE3", 300, "first_fit")
    mm2.allocate("X4", 100, "first_fit")
    mm2.allocate("FREE4", 500, "first_fit")

    mm2.deallocate("FREE1")
    mm2.deallocate("FREE2")
    mm2.deallocate("FREE3")
    mm2.deallocate("FREE4")

    res2 = allocate_best_fit(mm2, "P_TARGET", 250)
    assert res2["success"] is True
    p_target = [b for b in res2["blocks"] if b["process_id"] == "P_TARGET"][0]
    assert p_target["start"] == 300  # FREE2 block starts at 300 (size 280)
    assert p_target["size"] == 250


def test_worst_fit():
    mm = create_fragmented_memory()
    # Free blocks: 100MB, 300MB, 200MB, 500MB.
    # Process P_NEW requests 250 MB. Worst Fit should select the largest (500 MB) block starting at 1000.
    res = allocate_worst_fit(mm, "P_NEW", 250)
    assert res["success"] is True
    p_new_block = [b for b in res["blocks"] if b["process_id"] == "P_NEW"][0]
    assert p_new_block["start"] == 1000
    assert p_new_block["size"] == 250


def test_deallocation_and_coalescing():
    mm = MemoryManager(total_memory=1024)
    mm.allocate("P1", 200, "first_fit")
    mm.allocate("P2", 300, "first_fit")
    mm.allocate("P3", 100, "first_fit")

    assert mm.get_used_memory() == 600
    assert mm.get_free_memory() == 424

    # Deallocate middle process P2
    res = deallocate_process(mm, "P2")
    assert res["success"] is True
    assert mm.get_used_memory() == 300

    # Deallocate P1 and P3 -> should coalesce everything back to a single 1024 MB free block
    deallocate_process(mm, "P1")
    res_final = deallocate_process(mm, "P3")
    assert res_final["success"] is True
    assert len(res_final["blocks"]) == 1
    assert res_final["blocks"][0]["size"] == 1024
    assert res_final["blocks"][0]["is_allocated"] is False


def test_validation_and_edge_cases():
    # Invalid total memory
    with pytest.raises(ValueError):
        MemoryManager(total_memory=0)

    with pytest.raises(ValueError):
        MemoryManager(total_memory=-100)

    mm = MemoryManager(total_memory=500)

    # Negative or zero allocation size
    res = mm.allocate("P1", 0)
    assert res["success"] is False
    assert "greater than 0" in res["message"]

    res = mm.allocate("P1", -50)
    assert res["success"] is False

    # Empty process ID
    res = mm.allocate("", 100)
    assert res["success"] is False

    # Allocation size exceeds total memory
    res = mm.allocate("P1", 600)
    assert res["success"] is False
    assert "exceeds total memory" in res["message"]

    # Duplicate process ID
    mm.allocate("P1", 200)
    res = mm.allocate("P1", 100)
    assert res["success"] is False
    assert "already present" in res["message"]

    # Deallocate non-existent process
    res = deallocate_process(mm, "P999")
    assert res["success"] is False
    assert "not found" in res["message"]

    # Reset memory
    res = reset_memory(mm, 1000)
    assert res["success"] is True
    assert mm.total_memory == 1000
    assert mm.get_free_memory() == 1000
